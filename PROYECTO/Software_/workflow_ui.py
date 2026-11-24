"""Authenticated evaluation screens and finalization dialog (presentation only)."""
import hashlib
import streamlit as st
from uuid import UUID
from mail_service import MailService, MAIL_ERROR_MESSAGES
from workflow_runtime import runtime, clear_evaluation_state, public_demo_only
from evaluation_store import validate_person, CONSENT_TEXT
from private_pdf_download import private_pdf_download
from access_entry import entry_gate, show_app_qr, choose_particular
from p4_charts import snapshot_figure


def move(route):
    st.session_state.route = route


def request_cleanup():
    st.session_state.cleanup_request = True
    st.rerun()


@st.dialog("Finalizar evaluación", width="medium", dismissible=False)
def finish_dialog(store, transport, eid):
    token = st.session_state.auth_token
    try:
        record = store.get(token,eid)
        pdf = store.ensure_pdf(token,eid)
    except (PermissionError,ValueError) as exc:
        st.error(str(exc))
        if st.button("Volver a resultados",key="finish_back_error"):
            st.session_state.pop("finish_open",None)
            st.rerun()
        return
    st.write("Tu reporte está listo. Puedes descargarlo o solicitar una copia por correo. El QR sirve para abrir la aplicación IMPULSO.")
    st.caption(f"Evaluación {eid} · {record['person']['first_name']} {record['person']['last_name']}")
    private_pdf_download("Descargar PDF",pdf,f"IMPULSO_{eid}.pdf",key="finish_download")
    with st.container(horizontal=True):
        if st.button("QR para abrir IMPULSO",key="finish_qr"):
            st.session_state.qr_requested = eid
        if st.button("Enviar al correo",key="finish_yes"):
            st.session_state.mail_phase = True
        if st.button("Finalizar sin exportar",key="finish_no"):
            try:
                store.finalize(token,eid)
                request_cleanup()
            except (ValueError,PermissionError) as exc:
                st.error(str(exc))
        if st.button("Volver a resultados",key="finish_back"):
            st.session_state.pop("mail_phase",None)
            st.session_state.pop("finish_open",None)
            st.rerun()
    if st.session_state.get('qr_requested')==eid:
        show_app_qr()
    if not st.session_state.get("mail_phase"):
        return
    service = MailService(store,transport)
    if transport.simulated:
        st.info("Correo SIMULADO: no se enviarán mensajes ni adjuntos a ninguna dirección.")
    recipient = st.text_input("Destinatario del PDF",value=record['person'].get('email',''),key="mail_recipient")
    if st.button("Solicitar código de verificación",key="mail_request_code"):
        try:
            code = service.request_verification(token,eid,recipient)
            st.session_state.demo_mailbox = (recipient.strip(),code)
            st.success("Solicitud de verificación aceptada. El mensaje no contiene el reporte ECG.")
        except (ValueError,PermissionError) as exc:
            st.error(str(exc))
    simulated = st.session_state.get("demo_mailbox")
    if transport.simulated and simulated and simulated[0]==recipient.strip() and simulated[1]:
        st.code(f"Buzón simulado · código: {simulated[1]}")
    code = st.text_input("Código de verificación",key="mail_code",max_chars=6)
    if st.button("Validar código",key="mail_verify"):
        try:
            service.verify(token,eid,recipient,code)
            st.success("Destinatario verificado para esta evaluación durante 10 minutos.")
        except (ValueError,PermissionError) as exc:
            st.error(str(exc))
    st.write(f"Destinatario que recibiría el PDF: **{recipient}**")
    confirm_key = "mail_confirm_"+hashlib.sha256((eid+recipient).encode()).hexdigest()[:16]
    confirmed = st.checkbox("Confirmo este destinatario y autorizo enviarle el PDF de esta evaluación.",key=confirm_key)
    status = store.get(token,eid)['mail_status']
    if status=='fallido':
        st.warning("Envío fallido. Tus resultados se conservan. Si hubo un corte de conexión, la aceptación puede ser incierta; reintentar podría duplicar el correo.")
        code=store.get(token,eid).get('delivery',{}).get('error_code','provider_failed')
        st.caption(MAIL_ERROR_MESSAGES.get(code,MAIL_ERROR_MESSAGES['provider_failed']))
    if st.button("Reintentar envío confirmado" if status=='fallido' else "Confirmar y enviar PDF",
                 key="mail_send",disabled=status in ('aceptado','pendiente'),type="primary"):
        try:
            with st.status("Envío pendiente de aceptación…",expanded=True) as progress:
                status = service.send_pdf(token,eid,recipient,confirmed)
                progress.update(label=f"Estado: {status}",state="complete" if status=='aceptado' else "error")
                if status=='fallido':
                    code=store.get(token,eid).get('delivery',{}).get('error_code','provider_failed')
                    st.error(MAIL_ERROR_MESSAGES.get(code,MAIL_ERROR_MESSAGES['provider_failed']))
        except (ValueError,PermissionError) as exc:
            st.error(str(exc))
    if status=='aceptado':
        delivery = store.get(token,eid).get('delivery',{})
        st.caption(f"Destinatario del envío aceptado: {delivery.get('recipient','')}")
        st.success("Aceptado por el proveedor simulado. No hubo envío real." if transport.simulated else
                   "Aceptado por el proveedor. No se ha confirmado su entrega en la bandeja de entrada.")
        if st.button("Finalizar y volver al inicio",key="finish_accepted"):
            store.finalize(token,eid)
            request_cleanup()
    elif status=='pendiente':
        st.info("Envío pendiente. No se repetirá automáticamente. Si el proceso se interrumpió, revisa el estado con el administrador.")
    elif status=='fallido':
        st.caption("Puedes reintentar explícitamente, descargar el PDF o finalizar sin enviar.")


def stored_results(record):
    report = record.get('report')
    if not report:
        st.info("Evaluación registrada; todavía no contiene un análisis.")
        return
    st.write(f"{record['person']['first_name']} {record['person']['last_name']} · {record['person']['age']} años")
    st.json(report['metrics'])
    unit = report['acquisition']['unit']
    scope = report.get('analysis_scope','segment')
    st.caption('Métricas del registro completo' if scope=='full_record' else 'Evaluación histórica de un segmento; no se recalculó ni convirtió a registro completo.')
    if record.get('overview'):
        st.plotly_chart(snapshot_figure(record['overview'],unit),width='stretch',key='stored_overview',
                        alt='Vista global del registro analizado, con candidatos R.')
    st.plotly_chart(snapshot_figure(record['plot'],unit),width='stretch',key='stored_detail',
                    alt='Detalle ECG conservado con candidatos R sin verificación manual.')
    st.caption("Regla RR preliminar; AAMI y patrones ventriculares no evaluados. Prototipo experimental.")


def workflow():
    """Returns the analysis route context, or stops after rendering other screens."""
    try:
        config = dict(st.secrets.get('impulso',{}))
    except FileNotFoundError:
        config = {}
    entry_gate(config)
    demo_only=public_demo_only(config)
    if demo_only and not config.get('professional_emails'):
        st.info('Demostración particular disponible. El acceso profesional requiere configurar OIDC y professional_emails en Secrets.')
        st.button('Volver a demostración particular',key='unconfigured_to_demo',on_click=choose_particular)
        st.stop()
    try:
        mode,store,transport = runtime(config)
    except (ValueError,OSError) as exc:
        st.error(f"Configuración del servidor no disponible: {exc}")
        st.stop()
    if demo_only and mode!='oidc':
        st.info('El acceso profesional de la publicación requiere mode="oidc" y un proveedor de identidad configurado.')
        st.button('Volver a demostración particular',key='mode_to_demo',on_click=choose_particular)
        st.stop()
    if demo_only:
        st.info('PUBLICACIÓN DE DEMOSTRACIÓN · Solo identidad y señal ficticias integradas. Carga y almacenamiento de ECG reales deshabilitados. Historial ficticio temporal.')
    if mode=='demo':
        st.info("LOCAL / DEMO · Señal sintética o archivo preexistente · Correo simulado · Historial protegido por cuenta. Un archivo subido no se considera sintético.")
    else:
        if not st.user.get('is_logged_in',False):
            if st.session_state.get('auth_token'):
                store.logout(st.session_state.auth_token)
                clear_evaluation_state(st.session_state)
                st.session_state.pop('auth_token',None)
            try:
                auth_configured=bool(st.secrets.get('auth',{}).get('client_id'))
            except FileNotFoundError:
                auth_configured=False
            if not auth_configured:
                st.info('Acceso profesional pendiente: configura [auth] con tu proveedor OIDC en Secrets.')
                st.button('Volver a demostración particular',key='auth_to_demo',on_click=choose_particular)
                st.stop()
            st.write("Identifica al operador con el proveedor autorizado. La persona evaluada se registra después.")
            if st.button("Identificarse",key="oidc_login"):
                st.login()
            st.stop()
        issuer = st.user.get('iss',config.get('issuer',''))
        subject = st.user.get('sub','')
        if demo_only:
            allowed={str(x).strip().lower() for x in config.get('professional_emails',[])}
            if st.user.get('email_verified') is not True or str(st.user.get('email','')).lower() not in allowed:
                st.error('Esta identidad no está autorizada para el acceso profesional de demostración.')
                if st.button('Salir de la cuenta',key='oidc_denied_logout'):
                    st.logout()
                st.button('Usar demostración particular',key='denied_to_demo',on_click=choose_particular)
                st.stop()
        fingerprint = hashlib.sha256((str(issuer)+'\0'+str(subject)).encode()).hexdigest()
        if st.session_state.get('oidc_identity')!=fingerprint:
            if st.session_state.get('auth_token'):
                store.logout(st.session_state.auth_token)
            clear_evaluation_state(st.session_state)
            st.session_state.auth_token = store.oidc_session(issuer,subject,'Operador de demostración' if demo_only else st.user.get('name','Operador'))
            st.session_state.oidc_identity = fingerprint
    if not st.session_state.get('auth_token'):
        st.subheader("Acceso del operador")
        with st.form('operator_login'):
            login = st.text_input("Usuario local",key="login_name")
            password = st.text_input("Contraseña",type="password",key="login_password")
            submitted = st.form_submit_button("Acceder",key="login_submit")
        if submitted:
            try:
                st.session_state.auth_token = store.login(login,password)
                request_cleanup()
            except PermissionError as exc:
                st.error(str(exc))
        st.caption("No existen cuentas ni contraseñas por defecto. Crear una cuenta demo desde la terminal:")
        st.code('.\\.venv\\Scripts\\python.exe Software_\\workflow_runtime.py --create-demo-user operador --display "Operador ficticio"')
        st.stop()
    token = st.session_state.auth_token
    try:
        identity = store.identity(token)
    except PermissionError as exc:
        st.error(str(exc))
        if st.button("Volver al acceso",key="reauth"):
            clear_evaluation_state(st.session_state)
            st.session_state.pop('auth_token',None)
            st.rerun()
        st.stop()
    if 'route' not in st.session_state:
        st.session_state.route = 'Inicio'
    if st.session_state.get('next_route'):
        st.session_state.route = st.session_state.pop('next_route')
    with st.sidebar:
        st.subheader("IMPULSO")
        st.caption(f"Operador: {identity['display']} · {identity['role']}")
        if st.button("Cerrar sesión",key="logout"):
            store.logout(token)
            clear_evaluation_state(st.session_state)
            st.session_state.pop('auth_token',None)
            if mode=='oidc':
                st.logout()
            st.rerun()
    requested = st.query_params.get('report')
    if requested:
        st.subheader('Reporte protegido de IMPULSO')
        try:
            linked_id = str(UUID(str(requested)))
            linked = store.get(token,linked_id)
            if not linked['has_pdf']:
                st.info('El PDF todavía no está disponible. Se prepara al pulsar Finalizar evaluación.')
            else:
                st.caption(f"Evaluación {linked_id}")
                private_pdf_download('Descargar PDF',store.ensure_pdf(token,linked_id),f'IMPULSO_{linked_id}.pdf',key='linked_pdf')
        except (PermissionError,ValueError):
            st.error('Reporte no disponible para esta identidad.')
        if st.button('Volver a la aplicación',key='close_linked_report'):
            del st.query_params['report']
            st.rerun()
        st.stop()
    route = st.segmented_control("Navegación",['Inicio','Registro','Análisis','Resultados','Historial'],
                                 key='route',required=True)
    if route not in ('Resultados','Historial'):
        st.session_state.pop('finish_open',None)
    eid = st.session_state.get('evaluation_id')
    if route=='Inicio':
        st.subheader("Una evaluación, una persona, un registro")
        st.write("Registra a la persona evaluada, analiza un registro completo y revisa sus resultados. "
                 "La exportación y el correo se abren únicamente al finalizar.")
        if eid:
            st.caption(f"Evaluación activa: {eid}. Finalízala antes de registrar otra persona.")
            st.button("Continuar evaluación",on_click=move,args=('Resultados' if st.session_state.get('analysis') else 'Análisis',),key='continue')
        else:
            st.button("Nueva evaluación",type='primary',on_click=move,args=('Registro',),key='new')
        st.stop()
    if route=='Registro':
        if eid:
            st.info("Ya existe una evaluación activa. Vuelve a sus resultados para finalizarla.")
            st.stop()
        st.subheader("Registro de la persona evaluada")
        st.caption("Estos datos pertenecen a la persona evaluada; no cambian la identidad del operador.")
        with st.form('person_registration'):
            first = st.text_input("Nombre",value='Persona' if demo_only else '',key='person_first',max_chars=80,disabled=demo_only)
            last = st.text_input("Apellido",value='Ficticia' if demo_only else '',key='person_last',max_chars=80,disabled=demo_only)
            age = st.number_input("Edad (años)",min_value=0,max_value=120,value=30,key='person_age',disabled=demo_only)
            email = st.text_input("Correo electrónico (opcional)",key='person_email',disabled=demo_only,
                                  help='En la versión pública se solicita únicamente al confirmar el envío del PDF ficticio.' if demo_only else None)
            consent = st.checkbox("Confirmo que la persona autorizó procesar su ECG y conservar esta evaluación en mi historial.",key='person_consent')
            st.caption(CONSENT_TEXT)
            fictitious = st.checkbox("Confirmo que la identidad usada en esta demostración es ficticia.",key='person_demo') if mode=='demo' else False
            submitted = st.form_submit_button("Guardar registro y continuar",key='register_submit',type='primary')
        if submitted:
            try:
                if mode=='demo' and not fictitious:
                    raise ValueError("La demostración requiere una identidad ficticia; la procedencia del ECG se registra por separado.")
                person = validate_person(first,last,age,email)
                st.session_state.evaluation_id = store.create(token,person,consent,synthetic=mode=='demo')
                st.session_state.next_route = 'Análisis'
                st.rerun()
            except (ValueError,PermissionError) as exc:
                st.error(str(exc))
        st.stop()
    if route=='Historial':
        st.subheader("Historial de la identidad autorizada")
        records = store.history(token)
        if not records:
            st.info("Tu cuenta todavía no tiene evaluaciones.")
            st.stop()
        options = {r['evaluation_id']:r for r in records}
        selected = st.selectbox("Evaluación guardada",list(options),key='history_selected',
                                format_func=lambda k:f"{options[k]['created'][:10]} · {options[k]['person']['first_name']} {options[k]['person']['last_name']} · {options[k]['status']} · {k[:8]}")
        record = store.get(token,selected)  # Never trust a selected/query id without authorization.
        simulation = 'SIMULADO · ' if record.get('delivery',{}).get('simulated') else ''
        st.caption(f"ID {selected} · envío: {simulation}{record['mail_status']}")
        if record.get('delivery'):
            st.caption(f"Destinatario confirmado: {record['delivery']['recipient']}")
        stored_results(record)
        if record['status']=='finalizada' and record['has_pdf']:
            private_pdf_download('Descargar PDF del historial',store.ensure_pdf(token,selected),
                                 f'IMPULSO_{selected}.pdf',key='history_pdf')
        elif record.get('report') and (not eid or selected==eid):
            if st.button('Finalizar evaluación',key='history_finish'):
                st.session_state.evaluation_id = selected
                st.session_state.finish_open = selected
            if st.session_state.get('finish_open')==selected:
                finish_dialog(store,transport,selected)
        st.stop()
    if not eid:
        st.info("Registra primero una evaluación autorizada.")
        st.stop()
    record = store.get(token,eid)
    st.caption(f"Persona evaluada: {record['person']['first_name']} {record['person']['last_name']} · ID {eid}")
    if route=='Resultados':
        if record.get('report'):
            if st.button('Finalizar evaluación',key='finish_evaluation',type='primary'):
                st.session_state.finish_open = eid
            if st.session_state.get('finish_open')==eid:
                finish_dialog(store,transport,eid)
        else:
            st.info("Primero analiza un registro completo en la pantalla Análisis.")
        if st.session_state.get('analysis') is None:
            stored_results(record)
            st.stop()
    return mode,store,transport,route,eid
