"""IMPULSO P4-A. Run from project root with .venv's Streamlit module."""
import hashlib

import streamlit as st

from ecg_import import inspect_ecg_file
from p4_pipeline import AnalysisConfig, analyze_file
from p4_charts import ecg_figure, rr_figure
from workflow_ui import workflow
from workflow_runtime import synthetic_ecg, clear_evaluation_state

st.set_page_config(page_title="IMPULSO · ECG", page_icon=":material/cardiology:", layout="wide")


@st.cache_data(scope="session", max_entries=2, show_spinner=False)
def inspect_upload(content: bytes):
    return inspect_ecg_file(content)


@st.cache_data(scope="session", max_entries=2, show_spinner=False)
def process_upload(content: bytes, config: AnalysisConfig):
    return analyze_file(content, config)


# Clear all temporary evaluation data before recreating any widgets.
if st.session_state.get("cleanup_request"):
    inspect_upload.clear()
    process_upload.clear()
    clear_evaluation_state(st.session_state)

# Only working data lives in session state; encrypted history is separate.
for name, initial in {"analysis": None, "source_token": None, "result_revision": 0}.items():
    if name not in st.session_state:
        st.session_state[name] = initial

st.title(":material/cardiology: IMPULSO")
st.caption("Revisión experimental de ECG · BITalino / OpenSignals · Persona 4")

try:
    mode, store, transport, route, eid = workflow()
except PermissionError as exc:
    st.error(str(exc))
    st.stop()

if route == 'Análisis':
    with st.sidebar:
        st.subheader("Registro y análisis")
        choices=['Señal sintética'] if store.synthetic_only else (["Señal sintética", "Subir archivo"] if mode=="demo" else ["Subir archivo"])
        source = st.segmented_control("Origen",choices,
                                      default=choices[0], required=True, key="source")
        content = None
        if source=="Señal sintética":
            content = synthetic_ecg()
            st.caption("ECG ficticio de demostracion; unidades sinteticas, no mV.")
        else:
            uploaded = st.file_uploader("OpenSignals TXT o CSV de una columna", type=["txt", "csv"],
                                        max_upload_size=32, key=f"upload_{eid}",
                                        help="CSV: una amplitud por fila; indica su frecuencia y unidades originales.")
            if uploaded is not None:
                content = uploaded.getvalue()
        token = hashlib.sha256(content).hexdigest() if content is not None else None
        if token != st.session_state.source_token:
            st.session_state.analysis = None
            st.session_state.source_token = token
        info = None
        if content is not None:
            try:
                info = inspect_upload(content)
            except (ValueError, TypeError, OSError) as exc:
                st.error(f"Archivo incompatible: {exc}")
        if info is not None and content is not None and token is not None:
            st.caption(f"{info['format']} · {info['total_samples']:,} muestras · {info['unit']}")
            channels = ["auto", *info["channels"]]
            suggested = info["suggested_channel"]
            with st.form("analysis_form"):
                channel = st.selectbox("Canal", channels,
                                       index=channels.index(suggested) if suggested in channels else 0,
                                       key=f"channel_{token[:12]}",
                                       help="Auto usa el sensor ECG declarado en el encabezado. CSV: única columna.")
                fs = st.number_input("Frecuencia de muestreo (Hz)", min_value=100.0, max_value=10000.0,
                                     value=float(info["fs"] or 1000), step=100.0,
                                     disabled=info["fs"] is not None, key=f"fs_{token[:12]}",
                                     help="En TXT se respeta el encabezado; en CSV debes confirmar la frecuencia original.")
                if info["fs"] is not None:
                    st.caption(f"Duración del archivo: {info['total_samples']/info['fs']:.2f} s")
                notch = st.segmented_control("Notch de red", [0, 50, 60], default=60, required=True,
                                             format_func=lambda v: "Sin notch" if v == 0 else f"{v} Hz", key="notch")
                invert = st.checkbox("Invertir polaridad para detectar", key="invert",
                                      help="Solo se invierte la entrada al filtro. La curva original conserva su polaridad.")
                max_bpm = st.number_input("BPM máximo del detector", min_value=40, max_value=300,
                                          value=200, step=10, key="max_bpm",
                                          help="Define la separación mínima entre picos: 60 / BPMmáx segundos. No es un límite clínico.")
                rr_pct = st.slider("Umbral de desviación RR (%)", min_value=1, max_value=99,
                                   value=20, step=1, key="rr_pct",
                                       help="Desviación relativa respecto de la media global del registro completo.")
                submit = st.form_submit_button("Analizar registro completo", icon=":material/play_arrow:",
                                               type="primary", width="stretch")
            st.caption("Pasa-banda fijo: 0.5–40 Hz · fase cero. Se analizan todas las muestras; el zoom solo cambia el dibujo.")
            if submit:
                st.session_state.analysis = None
                try:
                    config = AnalysisConfig(fs_csv=fs, channel=channel,
                                            mains_hz=notch, invert=invert, max_bpm=max_bpm, rr_deviation=rr_pct/100,
                                            source_kind='synthetic' if source=='Señal sintética' else 'uploaded')
                    with st.spinner("Procesando el registro completo…"):
                        candidate = process_upload(content, config)
                        store.save_analysis(st.session_state.auth_token, eid, candidate, content)
                        st.session_state.analysis = candidate
                    st.session_state.result_revision += 1
                except (ValueError, TypeError, OSError, OverflowError, PermissionError) as exc:
                    st.error(f"No se pudo analizar el registro completo: {exc}")
        st.divider()
        st.caption("La configuración se aplica al pulsar Analizar. El zoom y la navegación conservan el análisis.")

result = st.session_state.analysis
if result is None:
    with st.container(border=True):
        st.subheader("Del registro al intervalo RR")
        st.write("Carga un TXT de OpenSignals o un CSV de amplitud y pulsa **Analizar registro completo**.")
        st.write("Explora el ECG, revisa los candidatos R y exporta las mediciones globales. "
                 "También puedes usar la señal sintética de demostración.")
        st.caption("Importación → filtrado → detección R → métricas → regla preliminar RR")
else:
    meta = result.acquisition
    full = meta.get('analysis_scope')=='full_record'
    st.subheader("Resumen del registro completo" if full else "Resumen histórico del segmento guardado")
    st.caption(f"{meta['source']} · canal {meta['channel'] or 'único'} · {result.fs:g} Hz · "
               f"{meta['unit']} · archivo {meta['file_duration_s']:.2f} s · "
               f"analizado {meta['start_s']:.2f}–{meta['start_s']+meta['duration_s']:.2f} s "
               f"({meta['samples']:,} muestras)")
    with st.container(horizontal=True, gap="medium"):
        st.metric("FC estimada · BPM", f"{result.metrics['bpm']:.1f}" if result.metrics['bpm'] is not None else "—",
                  border=True, width="stretch", help="60 000 / media RR en ms, usando picos automáticos no verificados.")
        st.metric("Picos detectados", result.metrics["n_peaks"], border=True, width="stretch")
        st.metric("RR medio · ms", f"{result.metrics['mean_rr_ms']:.1f}" if result.metrics['mean_rr_ms'] is not None else "—",
                  border=True, width="stretch")
        st.metric("SD de RR · ms", f"{result.metrics['sdnn_rr_ms']:.1f}" if result.metrics['sdnn_rr_ms'] is not None else "—",
                  border=True, width="stretch", help="SDNN del pipeline (ddof=0), sin depurar artefactos ni confirmar latidos sinusales.")
    for warning in result.warnings:
        st.caption(warning)
    page = st.segmented_control("Explorar resultados", ["Señal ECG", "Intervalos RR", "Clasificación y ritmo"],
                                default="Señal ECG", required=True, key="section")
    if page == "Señal ECG":
        origin, end = meta["start_s"], meta["start_s"]+meta["duration_s"]
        st.subheader('Vista global · registro completo' if full else 'Vista del segmento histórico analizado')
        st.plotly_chart(ecg_figure(result,origin,end),width='stretch',key='ecg_global',
                        config={'scrollZoom':True,'displaylogo':False},
                        alt='Todo el registro ECG analizado y sus picos R detectados.')
        with st.container(border=True):
            st.subheader("Detalle y candidatos R · solo visualización")
            window = st.slider("Ventana visible (s) · no recorta el análisis", min_value=float(origin), max_value=float(end),
                               value=(float(origin), float(min(end, origin+10))), step=.1,
                               key=f"viewport_{st.session_state.result_revision}")
            if window[1] > window[0]:
                st.plotly_chart(ecg_figure(result, *window), width="stretch", key="ecg_chart",
                                config={"scrollZoom": True, "displaylogo": False},
                                alt="ECG original, filtrado y picos R automáticos en el tramo visible.")
            else:
                st.info("Amplía la ventana visible para mostrar una porción de la señal.")
            st.caption("Arrastra para desplazarte, usa la rueda o la lupa para ampliar y doble clic para restablecer. "
                       "Pulsa una leyenda para ocultar una curva. Para ver más detalle, estrecha la ventana visible: "
                       "se reconstruye con las muestras del análisis. La reducción min/máx solo afecta al dibujo.")
            st.caption("El filtro retira la componente continua: las curvas original y filtrada pueden tener distintas líneas de base. "
                       "Los marcadores indican candidatos R, no complejos QRS confirmados.")
            st.caption('Mover esta ventana no cambia las métricas, los RR ni el alcance del PDF. Las evaluaciones históricas por segmento mantienen su alcance original.')
    elif page == "Intervalos RR":
        st.subheader("Intervalos entre detecciones consecutivas")
        if result.metrics["n_rr"]:
            st.plotly_chart(rr_figure(result), width="stretch", key="rr_chart",
                            config={"displaylogo": False}, alt="Intervalos RR y límites de desviación respecto de su media global.")
            st.dataframe(result.rr_table, hide_index=True, width="stretch")
        else:
            st.info("Se necesitan al menos dos picos para calcular un intervalo RR.")
        st.caption("RRᵢ = 1000 (Rᵢ₊₁ − Rᵢ) / fs. La dispersión usa RR sin depurar; no equivale a una evaluación clínica de HRV.")
    elif page == "Clasificación y ritmo":
        st.subheader("Regla RR · resultado preliminar")
        st.write(f"Cada intervalo se compara con la media global: |RR − media| / media > "
                 f"{result.config.rr_deviation:.0%}. Hay {result.metrics['n_rr']} intervalos evaluables.")
        if result.metrics["n_rr"]:
            outside = int((result.rr_table.regla_rr == "Fuera del umbral RR").sum())
            with st.container(horizontal=True):
                st.metric("Dentro del umbral RR", f"{result.summary['normal_pct']:.1f}%", border=True)
                st.metric("Fuera del umbral RR", f"{result.summary['anomalo_pct']:.1f}%", border=True)
                st.metric("Intervalos fuera del umbral", outside, border=True)
        st.info("Esta regla etiqueta intervalos; no clasifica latidos N/S/V/F ni confirma arritmias.")
        st.subheader("Clasificación AAMI y patrones · pendiente del equipo")
        st.write("N: grupo normal; S: ectópico supraventricular; V: ectópico ventricular; "
                 "F: fusión normal–ventricular. La app todavía no ejecuta predict_beats ni carga el modelo.")
        st.table({"Patrón": ["Bigeminismo", "Trigeminismo", "Parejas ventriculares", "Rachas ventriculares"],
                  "Estado": ["No evaluado · requiere etiquetas por latido verificadas"]*4})
        st.caption("La conexión futura deberá conservar una etiqueta por pico, índices de muestra, calidad y procedencia. "
                   "No se deducen patrones ventriculares a partir de la regla RR.")

st.divider()
st.caption("IMPULSO · Funciones experimentales para apoyar la revisión de registros tras la evaluación clínica inicial. "
           "No sustituye el triaje ni el ECG diagnóstico de 12 derivaciones. Sin alertas médicas automáticas.")
