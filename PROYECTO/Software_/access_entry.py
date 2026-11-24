"""Public entry and session-only fictitious demonstration. No patient store."""
import streamlit as st
from p4_pipeline import AnalysisConfig, analyze_file
from p4_charts import ecg_figure
from workflow_runtime import synthetic_ecg
from report_qr import app_link, qr_png, is_lan_link


def show_app_qr(config=None):
    if config is None:
        try:
            config=dict(st.secrets.get('impulso',{}))
        except FileNotFoundError:
            config={}
    try:
        url=app_link(config.get('public_url'))
    except ValueError as exc:
        st.info(str(exc))
        return
    st.image(qr_png(url),width=240,caption='Escanea para abrir IMPULSO en tu celular')
    st.text(url)
    st.link_button('Abrir IMPULSO',url)
    if is_lan_link(url):
        st.caption('Acceso de prueba en red local: celular y PC deben tener conexión entre sí. No es una publicación en Internet.')
    else:
        st.caption('URL configurada de la aplicación. Debe estar publicada y accesible; generar el QR no crea ni verifica el alojamiento.')
    st.caption('El QR abre la entrada de IMPULSO. No contiene un reporte, UUID, datos ECG ni permisos de historial.')


def _choose_professional():
    st.session_state.pop('public_demo_result',None)
    st.session_state.access_journey='professional'


def choose_particular():
    st.session_state.access_journey='particular'


def entry_gate(config):
    """The public branch stops BEFORE EvaluationStore/runtime is instantiated."""
    if st.session_state.get('access_journey')=='particular':
        st.subheader('Acceso particular · evaluación de demostración')
        st.info('Se utiliza únicamente una señal ficticia. No solicita datos personales, no guarda historial y no envía correo.')
        if st.button('Ejecutar demostración',key='public_demo_run',type='primary'):
            st.session_state.public_demo_result=analyze_file(synthetic_ecg(),AnalysisConfig(source_kind='synthetic'))
        result=st.session_state.get('public_demo_result')
        if result is not None:
            with st.container(horizontal=True):
                st.metric('FC ficticia estimada (BPM)',result.metrics['bpm'],border=True)
                st.metric('Picos automáticos',result.metrics['n_peaks'],border=True)
                st.metric('Intervalos RR',result.metrics['n_rr'],border=True)
            st.plotly_chart(ecg_figure(result,0,result.acquisition['duration_s']),width='stretch',
                            alt='ECG sintético de demostración, sin datos de pacientes.')
            st.caption('Regla RR preliminar; no es diagnóstico ni clasificación AAMI. Los datos de esta demostración solo viven en la sesión.')
        st.button('Acceso profesional',key='public_to_professional',on_click=_choose_professional)
        st.stop()
    if (st.session_state.get('auth_token') or st.user.get('is_logged_in',False) or st.query_params.get('report')
            or st.session_state.get('access_journey')=='professional'):
        return
    st.subheader('Abre IMPULSO y elige tu recorrido')
    st.write('Particular: evaluación ficticia sin historial privado. Profesional: autenticación y evaluaciones autorizadas.')
    with st.container(horizontal=True):
        if st.button('Acceso particular · demostración',key='enter_particular',type='primary'):
            choose_particular()
            st.rerun()
        st.button('Acceso profesional',key='enter_professional',on_click=_choose_professional)
    with st.expander('QR para abrir IMPULSO desde otro dispositivo'):
        show_app_qr(config)
    st.stop()
