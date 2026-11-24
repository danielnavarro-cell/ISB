"""Local persistence boundary. Every record operation re-authenticates a token.

Private payloads, source files, PDF and email addresses are encrypted at rest.
SQL owner predicates are mandatory, including for indirect mail operations.
"""
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import hmac
import json
from pathlib import Path
import secrets
import sqlite3
import time
import uuid

from cryptography.fernet import Fernet

CONSENT_TEXT = "IMPULSO-v1: autorización para procesar el ECG y conservar esta evaluación en el historial del operador."


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def validate_person(first, last, age, email=""):
    first, last = first.strip(), last.strip()
    if not first or not last or len(first)>80 or len(last)>80 or any(ord(c)<32 for c in first+last):
        raise ValueError("Introduce nombre y apellido válidos (hasta 80 caracteres cada uno).")
    if isinstance(age, bool) or int(age) != age or not 0 <= age <= 120:
        raise ValueError("Edad válida: de 0 a 120 años enteros.")
    if email.strip():
        from mail_service import normalize_email
        email = normalize_email(email)
    return dict(first_name=first, last_name=last, age=int(age), email=email.strip())


class EvaluationStore:
    def __init__(self, path: Path, key: bytes, *, synthetic_only=False):
        self.path = Path(path)
        self.key = key
        self.synthetic_only=synthetic_only
        self.cipher = Fernet(key)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.db() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS users(
              id TEXT PRIMARY KEY, login TEXT UNIQUE, display TEXT, role TEXT,
              salt BLOB, verifier BLOB, failures INTEGER DEFAULT 0, locked REAL DEFAULT 0);
            CREATE TABLE IF NOT EXISTS sessions(hash TEXT PRIMARY KEY, owner TEXT, expires REAL);
            CREATE TABLE IF NOT EXISTS evaluations(
              id TEXT PRIMARY KEY, owner TEXT NOT NULL, created TEXT NOT NULL, status TEXT NOT NULL,
              synthetic INTEGER NOT NULL, payload BLOB NOT NULL, source BLOB, pdf BLOB,
              revision INTEGER DEFAULT 0, mail_status TEXT DEFAULT 'no_solicitado');
            CREATE TABLE IF NOT EXISTS verification(
              evaluation TEXT PRIMARY KEY, recipient BLOB, nonce TEXT, digest TEXT,
              expires REAL, tries INTEGER, verified INTEGER, requested REAL);
            CREATE TABLE IF NOT EXISTS events(
              id INTEGER PRIMARY KEY, owner TEXT, evaluation TEXT, created TEXT, kind TEXT, detail BLOB);
            """)

    @contextmanager
    def db(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def pack(self, value):
        return self.cipher.encrypt(json.dumps(value, ensure_ascii=False, allow_nan=False).encode())

    def unpack(self, value):
        return json.loads(self.cipher.decrypt(value))

    def _audit(self, db, owner, eid, kind, detail=None):
        db.execute("INSERT INTO events(owner,evaluation,created,kind,detail) VALUES(?,?,?,?,?)",
                   (owner,eid,timestamp(),kind,self.pack(detail or {})))

    def create_demo_account(self, login, password, display, role="particular"):
        if len(password)<12 or not login.strip() or role not in ("particular", "profesional"):
            raise ValueError("Cuenta local: usuario y contraseña de al menos 12 caracteres; perfil válido.")
        salt = secrets.token_bytes(16)
        verifier = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600000)
        with self.db() as db:
            db.execute("INSERT INTO users(id,login,display,role,salt,verifier) VALUES(?,?,?,?,?,?)",
                       (str(uuid.uuid4()),login.strip().lower(),display,role,salt,verifier))

    def login(self, login, password):
        # Development accounts only. The OIDC mode does not call this method.
        with self.db() as db:
            db.execute("BEGIN IMMEDIATE")
            user = db.execute("SELECT * FROM users WHERE login=?",(login.strip().lower(),)).fetchone()
            salt = bytes(user["salt"]) if user and user["salt"] else bytes(16)
            digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600000)
            valid = user and user["verifier"] and hmac.compare_digest(digest,user["verifier"]) and user["locked"]<time.time()
            if not valid:
                if user:
                    failures = user["failures"]+1
                    db.execute("UPDATE users SET failures=?,locked=? WHERE id=?",
                               (failures,time.time()+300 if failures>=5 else 0,user["id"]))
                token = None
            else:
                db.execute("UPDATE users SET failures=0,locked=0 WHERE id=?",(user["id"],))
                token = self._session(db,user["id"])
        if token is None:
            raise PermissionError("Credenciales no válidas o cuenta temporalmente bloqueada.")
        return token

    def _session(self, db, owner):
        token = secrets.token_urlsafe(32)
        db.execute("INSERT INTO sessions VALUES(?,?,?)",
                   (hashlib.sha256(token.encode()).hexdigest(),owner,time.time()+8*3600))
        return token

    def oidc_session(self, issuer, subject, display):
        """SERVER ONLY: issuer/sub must come from st.user, never form/query input."""
        if not issuer or not subject:
            raise PermissionError("El proveedor no entregó issuer/sub verificables.")
        login = "oidc:"+hashlib.sha256((issuer+"\0"+subject).encode()).hexdigest()
        with self.db() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("INSERT OR IGNORE INTO users(id,login,display,role) VALUES(?,?,?,?)",
                       (str(uuid.uuid4()),login,display,"operador"))
            owner = db.execute("SELECT id FROM users WHERE login=?",(login,)).fetchone()[0]
            return self._session(db,owner)

    def _identity(self, db, token):
        row = db.execute("SELECT users.id,display,role FROM sessions JOIN users ON users.id=sessions.owner "
                         "WHERE sessions.hash=? AND expires>?",
                         (hashlib.sha256(token.encode()).hexdigest(),time.time())).fetchone()
        if row is None:
            raise PermissionError("Sesión no válida o caducada. Vuelve a identificarte.")
        return dict(row)

    def identity(self, token):
        with self.db() as db:
            return self._identity(db,token)

    def logout(self, token):
        with self.db() as db:
            db.execute("DELETE FROM sessions WHERE hash=?",(hashlib.sha256(token.encode()).hexdigest(),))

    def _owned(self, db, token, eid):
        owner = self._identity(db,token)["id"]
        # Do not materialize the original ECG blob during UI/permission checks.
        row = db.execute("SELECT id,owner,created,status,synthetic,payload,pdf,revision,mail_status "
                         "FROM evaluations WHERE id=? AND owner=?",(eid,owner)).fetchone()
        if row is None:
            raise PermissionError("Evaluación no disponible para esta identidad.")
        return row

    def create(self, token, person, consent, synthetic=False):
        if self.synthetic_only:
            person=dict(first_name='Persona',last_name='Ficticia',age=30,email='')
            synthetic=True
        person = validate_person(person["first_name"],person["last_name"],person["age"],person.get("email", ""))
        if consent is not True:
            raise ValueError("Se requiere autorización documentada antes de guardar la evaluación.")
        eid = str(uuid.uuid4())
        created = timestamp()
        with self.db() as db:
            identity = self._identity(db,token)
            payload = dict(person=person,operator=identity,created=created,evaluation_id=eid,
                           consent=dict(basis="consentimiento registrado por el operador",text=CONSENT_TEXT,
                                        accepted_at=created,operator_id=identity["id"]), synthetic=bool(synthetic))
            db.execute("INSERT INTO evaluations(id,owner,created,status,synthetic,payload) VALUES(?,?,?,?,?,?)",
                       (eid,identity["id"],created,"registrada",int(synthetic),self.pack(payload)))
            self._audit(db,identity["id"],eid,"registro_autorizado")
        return eid

    def get(self, token, eid):
        with self.db() as db:
            row = self._owned(db,token,eid)
            return dict(self.unpack(row["payload"]), status=row["status"], revision=row["revision"],
                        mail_status=row["mail_status"], has_pdf=row["pdf"] is not None)

    def history(self, token):
        with self.db() as db:
            owner = self._identity(db,token)["id"]
            rows = db.execute("SELECT payload,status,mail_status,(pdf IS NOT NULL) AS has_pdf "
                              "FROM evaluations WHERE owner=? ORDER BY created DESC",(owner,)).fetchall()
            return [dict(self.unpack(r["payload"]),status=r["status"],mail_status=r["mail_status"],has_pdf=bool(r["has_pdf"])) for r in rows]

    def save_analysis(self, token, eid, result, content):
        from p4_pipeline import report_dict
        from p4_charts import plot_snapshot
        if self.synthetic_only:
            from workflow_runtime import synthetic_ecg
            if result.config.source_kind!='synthetic' or content!=synthetic_ecg():
                raise ValueError('La versión pública solo acepta su señal sintética integrada; no se guarda este archivo.')
        if hashlib.sha256(content).hexdigest()!=result.source_sha256:
            raise ValueError("El archivo no corresponde a los resultados de este análisis.")
        origin = result.acquisition["start_s"]
        end = min(origin+10,origin+result.acquisition["duration_s"])
        plot = plot_snapshot(result,origin,end)
        overview = plot_snapshot(result,origin,origin+result.acquisition['duration_s'])
        with self.db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = self._owned(db,token,eid)
            if row["status"]=="finalizada" or row["mail_status"] in ("pendiente","aceptado"):
                raise ValueError("La evaluación está cerrada o tiene un envío en curso/aceptado.")
            payload = self.unpack(row["payload"])
            payload.setdefault('identity_fictitious',payload.get('synthetic',False))
            payload.update(report=report_dict(result),plot=plot,overview=overview,
                           synthetic=result.config.source_kind=='synthetic')
            db.execute("UPDATE evaluations SET payload=?,source=?,synthetic=?,pdf=NULL,revision=revision+1,status='analizada',mail_status='no_solicitado' WHERE id=? AND owner=?",
                       (self.pack(payload),self.cipher.encrypt(content),int(payload['synthetic']),eid,row["owner"]))
            db.execute("DELETE FROM verification WHERE evaluation=?",(eid,))
            self._audit(db,row["owner"],eid,"analisis_guardado",dict(sha256=result.source_sha256))

    def ensure_pdf(self, token, eid):
        from pdf_report import build_pdf
        with self.db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = self._owned(db,token,eid)
            if row["pdf"] is not None:
                return self.cipher.decrypt(row["pdf"])
            payload = self.unpack(row["payload"])
            if "report" not in payload:
                raise ValueError("Primero analiza un segmento.")
            pdf = build_pdf(payload)
            db.execute("UPDATE evaluations SET pdf=? WHERE id=? AND owner=?",
                       (self.cipher.encrypt(pdf),eid,row["owner"]))
            self._audit(db,row["owner"],eid,"pdf_generado")
            return pdf

    def source_bytes(self, token, eid):
        with self.db() as db:
            row = self._owned(db,token,eid)
            source = db.execute("SELECT source FROM evaluations WHERE id=? AND owner=?",(eid,row['owner'])).fetchone()[0]
            if source is None:
                raise ValueError("No existe archivo asociado.")
            return self.cipher.decrypt(source)

    def finalize(self, token, eid):
        with self.db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = self._owned(db,token,eid)
            if row["pdf"] is None:
                raise ValueError("Se requiere PDF antes de finalizar.")
            if row["mail_status"]=="pendiente":
                raise ValueError("Hay un envío pendiente. Conserva los resultados y revisa su estado.")
            db.execute("UPDATE evaluations SET status='finalizada' WHERE id=? AND owner=?",(eid,row["owner"]))
            db.execute("DELETE FROM verification WHERE evaluation=?",(eid,))
            self._audit(db,row["owner"],eid,"evaluacion_finalizada",dict(mail_status=row['mail_status']))
