"""Server configuration, fictitious source, and temporary-state isolation."""
import os
from pathlib import Path
import numpy as np
from cryptography.fernet import Fernet
from evaluation_store import EvaluationStore
from mail_service import MockTransport, SMTPTransport

ROOT = Path(__file__).resolve().parent.parent


def public_demo_only(config=None):
    """Cloud bundle marker cannot be disabled by browser state or a secret."""
    if (Path(__file__).resolve().parent/'cloud_demo.flag').exists():
        return True
    value=os.getenv('IMPULSO_PUBLIC_DEMO_ONLY',(config or {}).get('public_demo_only',False))
    return value is True or str(value).lower() in ('true','1','yes')


def runtime(secrets_config=None):
    config = secrets_config or {}
    mode = os.getenv("IMPULSO_MODE",config.get("mode","demo"))
    if mode not in ("demo","oidc"):
        raise ValueError("IMPULSO_MODE debe ser demo u oidc.")
    default = ROOT/".impulso_private"/("demo" if mode=="demo" else "oidc")
    directory = Path(os.getenv("IMPULSO_PRIVATE_DIR",str(config.get("private_dir",default))))
    directory.mkdir(parents=True,exist_ok=True)
    key = os.getenv("IMPULSO_DATA_KEY",config.get("data_key", ""))
    if not key:
        if mode != "demo":
            raise ValueError("Configura IMPULSO_DATA_KEY en el servidor antes de habilitar OIDC.")
        key_file = directory/"development.key"
        try:
            fd = os.open(key_file,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        except FileExistsError:
            pass
        else:
            with os.fdopen(fd,"wb") as stream:
                stream.write(Fernet.generate_key())
        key = key_file.read_bytes().decode()
    demo_only=public_demo_only(config)
    store = EvaluationStore(directory/"history.sqlite3",key.encode(),synthetic_only=demo_only)
    mail = config.get("mail",{})
    mail_mode = os.getenv("IMPULSO_MAIL_MODE",mail.get("mode","mock"))
    if mail_mode not in ("mock","smtp") or mode=="demo" and mail_mode!="mock":
        raise ValueError("El modo demo solo admite correo simulado.")
    if mail_mode=="mock":
        transport = MockTransport()
    else:
        options={name:os.getenv("IMPULSO_SMTP_"+name.upper(),mail.get(name,""))
                 for name in ("host","username","password","sender")}
        options['tls_mode']=os.getenv('IMPULSO_SMTP_TLS_MODE',mail.get('tls_mode','starttls'))
        options['port']=os.getenv('IMPULSO_SMTP_PORT',mail.get('port',465 if options['tls_mode']=='ssl' else 587))
        if demo_only:
            allowed=mail.get('allowed_recipients',[])
            if not allowed or not isinstance(allowed,list):
                raise ValueError('El envío real de la demo requiere allowed_recipients con tus direcciones de prueba.')
            options['allowed_recipients']=allowed
        transport = SMTPTransport(**options)
    return mode,store,transport


def synthetic_ecg():
    """Deterministic teaching signal, not a simulated clinical diagnosis."""
    fs = 1000
    t = np.arange(30000)/fs
    signal = .02*np.sin(2*np.pi*.3*t)
    for beat in np.arange(.6,29.8,.8):
        signal += np.exp(-.5*((t-beat)/.015)**2)+.18*np.exp(-.5*((t-beat-.25)/.06)**2)
    return ("amplitud_sintetica\n"+"\n".join(f"{v:.6f}" for v in signal)).encode()


def clear_evaluation_state(state):
    """Call BEFORE widgets render. Preserve only the authenticated session token."""
    token = state.get("auth_token")
    for key in list(state):
        del state[key]
    if token:
        state["auth_token"] = token
    state["route"] = "Inicio"


if __name__=="__main__":
    import argparse
    import getpass
    parser = argparse.ArgumentParser(description="Crear una cuenta local de demostración (sin datos reales).")
    parser.add_argument("--create-demo-user",required=True)
    parser.add_argument("--display",default="Operador de demostración")
    parser.add_argument("--role",choices=["particular","profesional"],default="particular")
    args = parser.parse_args()
    mode,store,_transport = runtime()
    if mode!="demo":
        parser.error("Las cuentas locales solo están disponibles en modo demo.")
    password = getpass.getpass("Contraseña nueva (mínimo 12 caracteres): ")
    if password!=getpass.getpass("Repetir contraseña: "):
        parser.error("Las contraseñas no coinciden.")
    store.create_demo_account(args.create_demo_user,password,args.display,args.role)
    print("Cuenta creada. Inicia Streamlit y accede con ella. No hay contraseñas por defecto.")
