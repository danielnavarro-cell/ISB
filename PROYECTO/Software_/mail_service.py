"""Decoupled transport and verified-recipient workflow. Defaults never send mail."""
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import make_msgid
import hashlib
import hmac
import re
import secrets
import smtplib
import ssl
import time

SUBJECT = "IMPULSO | Resultados de tu análisis electrocardiográfico"
MAIL_ERROR_MESSAGES = {
    'authentication_failed':'El proveedor rechazó la autenticación SMTP. Revisa las credenciales privadas del servidor.',
    'recipient_refused':'El proveedor rechazó la dirección destinataria.',
    'sender_refused':'El proveedor rechazó el remitente. Comprueba que está autorizado.',
    'connection_failed':'No se pudo conectar al servidor SMTP. Revisa host, puerto y conectividad.',
    'acceptance_uncertain':'La conexión se interrumpió o agotó el tiempo. La aceptación puede ser incierta; no reintentes automáticamente.',
    'provider_failed':'El proveedor no confirmó la aceptación. El PDF permanece disponible.',
    'recipient_not_allowed':'Esta dirección no pertenece a la lista privada de destinatarios de prueba.',
}


def mail_error_code(exc):
    """Controlled categories only; never expose provider text, keys or recipients."""
    if isinstance(exc,RecipientNotAllowed):return 'recipient_not_allowed'
    if isinstance(exc,smtplib.SMTPAuthenticationError):return 'authentication_failed'
    if isinstance(exc,smtplib.SMTPRecipientsRefused):return 'recipient_refused'
    if isinstance(exc,smtplib.SMTPSenderRefused):return 'sender_refused'
    if isinstance(exc,(TimeoutError,smtplib.SMTPServerDisconnected)):return 'acceptance_uncertain'
    if isinstance(exc,smtplib.SMTPConnectError):return 'connection_failed'
    if isinstance(exc,smtplib.SMTPException):return 'provider_failed'
    if isinstance(exc,OSError):return 'connection_failed'
    return 'provider_failed'


def normalize_email(value):
    value = value.strip()
    if len(value)>254 or not re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,63}",value):
        raise ValueError("Introduce un correo válido, sin saltos de línea ni varios destinatarios.")
    local,domain = value.rsplit("@",1)
    if len(local)>64 or local.startswith(".") or local.endswith(".") or ".." in value:
        raise ValueError("La dirección de correo no es válida.")
    return local+"@"+domain.lower()


@dataclass(frozen=True)
class Receipt:
    accepted: bool
    simulated: bool
    message_id: str


class RecipientNotAllowed(ValueError):
    pass


class MockTransport:
    simulated = True
    def __init__(self, fail=False):
        self.fail = fail

    def send(self, recipient, subject, body, pdf=None, request_id=""):
        if self.fail:
            raise OSError("Simulación de proveedor no disponible")
        # Never persist an unencrypted attachment or transmit anything.
        return Receipt(True,True,"mock-"+request_id)


class SMTPTransport:
    simulated = False
    def __init__(self, host, port, username, password, sender, tls_mode="starttls",allowed_recipients=None):
        if not all((host,username,password,sender)) or tls_mode not in ("starttls","ssl"):
            raise ValueError("SMTP requiere configuración completa y TLS.")
        try:
            port=int(port)
        except (TypeError,ValueError):
            raise ValueError("Puerto SMTP no válido.") from None
        if any(c.isspace() for c in host) or not 1<=port<=65535:
            raise ValueError("Host o puerto SMTP no válidos.")
        self.host,self.port,self.username,self.password = host,int(port),username,password
        self.sender,self.tls_mode = normalize_email(sender),tls_mode
        self.allowed_recipients=None if allowed_recipients is None else {normalize_email(v) for v in allowed_recipients}

    def send(self, recipient, subject, body, pdf=None, request_id=""):
        recipient = normalize_email(recipient)
        if self.allowed_recipients is not None and recipient not in self.allowed_recipients:
            raise RecipientNotAllowed('Destinatario fuera de la lista de pruebas.')
        message = EmailMessage()
        message['Subject'],message['From'],message['To'] = subject,self.sender,recipient
        message['Message-ID'] = make_msgid(idstring=request_id)
        message.set_content(body)
        if pdf:
            message.add_attachment(pdf,maintype="application",subtype="pdf",filename="IMPULSO_resultados.pdf")
        context = ssl.create_default_context()
        client = smtplib.SMTP_SSL(self.host,self.port,timeout=20,context=context) if self.tls_mode=="ssl" else smtplib.SMTP(self.host,self.port,timeout=20)
        with client:
            if self.tls_mode=="starttls":
                client.starttls(context=context)
            client.login(self.username,self.password)
            refused = client.send_message(message)
            if refused:
                raise OSError("El proveedor no aceptó al destinatario.")
        return Receipt(True,False,message['Message-ID'])


class MailService:
    def __init__(self, store, transport):
        self.store,self.transport = store,transport

    def _digest(self, eid, recipient, nonce, code):
        return hmac.new(self.store.key,f"{eid}\0{recipient}\0{nonce}\0{code}".encode(),hashlib.sha256).hexdigest()

    def request_verification(self, token, eid, recipient):
        recipient = normalize_email(recipient)
        code = f"{secrets.randbelow(1000000):06d}"
        nonce = secrets.token_hex(16)
        with self.store.db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = self.store._owned(db,token,eid)
            if row['status']=='finalizada' or row['mail_status'] in ('aceptado','pendiente') or row['pdf'] is None:
                raise ValueError("No se puede verificar destinatario en este estado.")
            old = db.execute("SELECT requested FROM verification WHERE evaluation=?",(eid,)).fetchone()
            if old and time.time()-old['requested']<60:
                raise ValueError("Espera 60 s antes de solicitar otro código.")
            db.execute("INSERT OR REPLACE INTO verification VALUES(?,?,?,?,?,?,?,?)",
                       (eid,self.store.cipher.encrypt(recipient.encode()),nonce,
                        self._digest(eid,recipient,nonce,code),time.time()+600,0,0,time.time()))
            self.store._audit(db,row['owner'],eid,'verificacion_solicitada')
        try:
            receipt = self.transport.send(recipient,"IMPULSO | Verifica tu correo",
                                          f"Código para verificar el destinatario: {code}. Caduca en 10 minutos. No incluye resultados ECG.",request_id=nonce)
            if not receipt.accepted:
                raise OSError("Solicitud no aceptada")
        except Exception as exc:
            error=mail_error_code(exc)
            with self.store.db() as db:
                db.execute("DELETE FROM verification WHERE evaluation=? AND nonce=?",(eid,nonce))
                self.store._audit(db,row['owner'],eid,'verificacion_fallida',dict(error_code=error,simulated=self.transport.simulated))
            raise ValueError("No se pudo solicitar la verificación. No se ha enviado ningún PDF. "+MAIL_ERROR_MESSAGES[error]) from None
        return code if receipt.simulated else None

    def verify(self, token, eid, recipient, code):
        recipient = normalize_email(recipient)
        with self.store.db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = self.store._owned(db,token,eid)
            challenge = db.execute("SELECT * FROM verification WHERE evaluation=?",(eid,)).fetchone()
            valid = (challenge is not None and challenge['expires']>time.time() and challenge['tries']<5
                     and self.store.cipher.decrypt(challenge['recipient']).decode()==recipient
                     and hmac.compare_digest(challenge['digest'],self._digest(eid,recipient,challenge['nonce'],code.strip())))
            if challenge:
                db.execute("UPDATE verification SET tries=tries+1,verified=? WHERE evaluation=?",(int(bool(valid)),eid))
            if valid:
                self.store._audit(db,row['owner'],eid,'destinatario_verificado')
        if not valid:
            raise ValueError("Código incorrecto, caducado o destinatario diferente (máximo 5 intentos).")

    def send_pdf(self, token, eid, recipient, confirmed):
        if confirmed is not True:
            raise ValueError("Confirma explícitamente el destinatario y el envío del PDF.")
        recipient = normalize_email(recipient)
        request_id = secrets.token_hex(16)
        with self.store.db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = self.store._owned(db,token,eid)
            if row['mail_status'] in ('aceptado','pendiente'):
                delivery = self.store.unpack(row['payload']).get('delivery',{})
                if delivery.get('recipient') != recipient:
                    raise ValueError("El envío existente corresponde a otro destinatario.")
                return row['mail_status']
            challenge = db.execute("SELECT * FROM verification WHERE evaluation=?",(eid,)).fetchone()
            if (row['status']=='finalizada' or row['pdf'] is None or challenge is None
                    or not challenge['verified'] or challenge['expires']<=time.time()
                    or self.store.cipher.decrypt(challenge['recipient']).decode()!=recipient):
                raise ValueError("Primero verifica este destinatario para esta evaluación.")
            pdf = self.store.cipher.decrypt(row['pdf'])
            payload = self.store.unpack(row['payload'])
            from evaluation_store import timestamp
            payload['delivery'] = dict(recipient=recipient,confirmed_at=timestamp(),
                                       verified=True,simulated=self.transport.simulated,request_id=request_id)
            db.execute("UPDATE evaluations SET mail_status='pendiente',payload=? WHERE id=? AND owner=?",
                       (self.store.pack(payload),eid,row['owner']))
            self.store._audit(db,row['owner'],eid,'consentimiento_envio',dict(recipient=recipient,request_id=request_id,explicit=True,simulated=self.transport.simulated))
        # Reservation committed BEFORE the external operation; reruns cannot resend.
        error=None
        message_id=None
        try:
            receipt = self.transport.send(recipient,SUBJECT,
                                          "Adjuntamos un reporte de demostración con señal ficticia; no corresponde a una evaluación clínica." if payload.get('synthetic') else
                                          "Adjuntamos tu reporte experimental IMPULSO. No constituye un diagnóstico.",
                                          pdf=pdf,request_id=request_id)
            status = 'aceptado' if receipt.accepted else 'fallido'
            message_id=receipt.message_id if receipt.accepted else None
            if not receipt.accepted:error='provider_failed'
        except Exception as exc:
            status = 'fallido'
            error=mail_error_code(exc)
        with self.store.db() as db:
            # Complete the already-authorized reservation even if the browser
            # session expires during the provider call. Never lose acceptance.
            db.execute('BEGIN IMMEDIATE')
            current=db.execute('SELECT payload FROM evaluations WHERE id=? AND owner=?',(eid,row['owner'])).fetchone()
            payload=self.store.unpack(current['payload'])
            payload['delivery'].update(error_code=error,message_id=message_id)
            db.execute("UPDATE evaluations SET mail_status=?,payload=? WHERE id=? AND owner=?",
                       (status,self.store.pack(payload),eid,row['owner']))
            self.store._audit(db,row['owner'],eid,'estado_envio',dict(status=status,request_id=request_id,
                                                                    simulated=self.transport.simulated,error_code=error,
                                                                    meaning="aceptación del proveedor; entrega en bandeja no verificada"))
        return status
