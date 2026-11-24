"""P4 orchestration and reports. No Flask, model loading or AAMI inference."""
from dataclasses import dataclass, asdict
import hashlib
import json
import numpy as np
import pandas as pd

from ecg_import import load_ecg_file
from filters import preprocess_ecg
from peak_detection import detect_r_peaks
from features import compute_all_features
from classification import classify_beats, summarize_classification


@dataclass(frozen=True)
class AnalysisConfig:
    fs_csv: float = 1000
    channel: str = "auto"
    start_s: float = 0
    duration_s: float | None = None
    mains_hz: int = 60
    invert: bool = False
    max_bpm: int = 200
    rr_deviation: float = .20
    scope: str = "full_record"
    source_kind: str = "uploaded"


@dataclass
class AnalysisResult:
    raw: np.ndarray
    filtered: np.ndarray
    peaks: np.ndarray
    fs: float
    acquisition: dict
    config: AnalysisConfig
    metrics: dict
    rr_table: pd.DataFrame
    summary: dict
    warnings: list[str]
    source_sha256: str
    # Future P2/P3 boundary: one VERIFIED label per detected/reviewed beat,
    # same sample axis, model provenance and explicit quality mask required.
    # No producer is wired in P4-A; interval labels must never populate this.
    aami_labels: tuple[str, ...] | None = None
    aami_provenance: dict | None = None


def analyze_file(content: bytes, config: AnalysisConfig) -> AnalysisResult:
    if not 40 <= config.max_bpm <= 300 or not np.isfinite(config.rr_deviation) or not 0 < config.rr_deviation < 1:
        raise ValueError("Parametros del detector o de la regla RR invalidos.")
    if config.scope not in ('full_record','segment') or config.source_kind not in ('uploaded','synthetic'):
        raise ValueError("Alcance o procedencia del análisis no válidos.")
    if config.scope == 'full_record':
        if config.start_s != 0 or config.duration_s is not None:
            raise ValueError("El análisis completo no admite inicio/duración de recorte. Usa la ventana de visualización.")
        raw, fs, meta = load_ecg_file(content, config.fs_csv, config.channel, full_record=True)
    else:
        raw, fs, meta = load_ecg_file(content, config.fs_csv, config.channel, config.start_s,
                                     config.duration_s or 30, windowed=True)
        meta['analysis_scope'] = 'segment'
    filtered = preprocess_ecg(raw * (-1 if config.invert else 1), fs, mains=config.mains_hz)
    peaks, _ = detect_r_peaks(filtered, fs, max_bpm=config.max_bpm)
    features = compute_all_features(peaks, fs)
    rr = features["rr_intervals_ms"]
    labels = classify_beats(rr, deviation_threshold=config.rr_deviation)
    summary = summarize_classification(labels)
    neutral = ["Dentro del umbral RR" if label == "Normal" else "Fuera del umbral RR" for label in labels]
    table = pd.DataFrame(dict(intervalo=np.arange(1, len(rr)+1),
                              inicio_s=meta["start_s"]+peaks[:-1]/fs,
                              fin_s=meta["start_s"]+peaks[1:]/fs, rr_ms=rr,
                              desviacion_relativa=np.abs(rr-np.mean(rr))/np.mean(rr) if len(rr) else [],
                              regla_rr=neutral))
    metrics = dict(bpm=float(features["bpm"]) if len(rr) else None,
                   sdnn_rr_ms=float(features["hrv_sdnn_ms"]) if len(rr)>1 else None,
                   n_peaks=int(features["n_latidos"]), n_rr=len(rr),
                   mean_rr_ms=float(np.mean(rr)) if len(rr) else None)
    warnings = ["Los picos son detecciones automaticas sin verificacion manual; la regla RR no confirma arritmias."]
    if len(rr)<2: warnings.append("Intervalos RR insuficientes para estimar su dispersion.")
    if config.duration_s is not None and meta["duration_s"] + 1/fs < config.duration_s:
        warnings.append("El tramo llega al final del archivo; se informa la duracion disponible.")
    if config.mains_hz and config.mains_hz >= fs/2:
        warnings.append("El notch se omite por estar en o sobre Nyquist; no corrige aliasing previo.")
    return AnalysisResult(raw, filtered, peaks, fs, meta, config, metrics, table, summary,
                          warnings, hashlib.sha256(content).hexdigest())


def display_indices(result, start_s, end_s, max_points=6000):
    """Min/max envelopes for display only; markers use exact peaks separately.

    Recomputed for the selected viewport; no reduced arrays enter analysis.
    Not a resampling filter and not a replacement for detailed original data.
    """
    if max_points < 16 or end_s <= start_s:
        raise ValueError("Ventana visible o limite de puntos invalido.")
    origin = result.acquisition["start_s"]
    a = max(0, int(np.floor((start_s-origin)*result.fs)))
    b = min(len(result.raw), int(np.ceil((end_s-origin)*result.fs))+1)
    if b <= a: return np.array([], dtype=int)
    if b-a <= max_points: return np.arange(a,b)
    peaks = result.peaks[(result.peaks>=a)&(result.peaks<b)]
    # Markers are drawn independently at exact indices. A long overview must
    # not expand its line envelope indefinitely to include every marker.
    if len(peaks) > max_points//3:
        peaks = np.array([],dtype=int)
    buckets = max(1,(max_points-len(peaks)-2)//4)
    bounds = np.linspace(a,b,buckets+1,dtype=int)
    chosen = [a,b-1,*peaks.tolist()]
    for lo,hi in zip(bounds[:-1],bounds[1:]):
        if hi>lo:
            for signal in (result.raw,result.filtered):
                chosen.extend([lo+int(np.argmin(signal[lo:hi])),lo+int(np.argmax(signal[lo:hi]))])
    return np.unique(np.asarray(chosen,dtype=int))


def report_dict(result, alias="Registro ECG"):
    return dict(application="IMPULSO P4-A",record_alias=alias,source_sha256=result.source_sha256,
                acquisition={**result.acquisition, "sampling_rate_hz": result.fs},
                parameters=asdict(result.config),metrics=result.metrics,
                analysis_scope=result.acquisition.get('analysis_scope','segment'),
                source_kind=result.config.source_kind,
                filtering=dict(bandpass_hz=[0.5, 40], butterworth_order=4,
                               notch_hz=result.config.mains_hz, notch_quality=30,
                               zero_phase=True, scope=result.acquisition.get('analysis_scope','segment')),
                detector="find_peaks actual; umbral global media + 0.5 SD",
                rr_rule=dict(kind="preliminar por intervalo, no AAMI",reference="media global del registro" if result.acquisition.get('analysis_scope')=='full_record' else "media global del tramo",
                             deviation_threshold=result.config.rr_deviation,
                             outside_threshold_count=int((result.rr_table.regla_rr=="Fuera del umbral RR").sum())),
                aami_status="no_disponible",rhythm_patterns_status="no_evaluados_sin_etiquetas_AAMI_verificadas",
                cautions=result.warnings+[
                    "SDNN calculada sobre RR sin depuracion de artefactos; no equivale a HRV clinica.",
                    "Filtrado de fase cero fuera de línea; no es monitorizacion continua.",
                    "Apoyo experimental a revision; no sustituye triaje ni ECG diagnostico de 12 derivaciones."],
                rr_intervals=result.rr_table.to_dict(orient="records"))


def report_json(result, alias="Registro ECG"):
    return json.dumps(report_dict(result,alias),ensure_ascii=False,indent=2,allow_nan=False).encode("utf-8")


def report_text(result, alias="Registro ECG"):
    report = report_dict(result,alias)
    lines = ["IMPULSO / Resumen experimental",alias,
             f"Fuente: {result.acquisition['source']} | canal: {result.acquisition['channel'] or 'columna unica'}",
             f"Muestreo: {result.fs:g} Hz | unidades: {result.acquisition['unit']}",
             f"Inicio: {result.acquisition['start_s']:g} s | duracion: {result.acquisition['duration_s']:g} s",
             "Configuracion: "+json.dumps(report['parameters'],ensure_ascii=False),
             "Metricas: "+json.dumps(result.metrics,ensure_ascii=False),
             "Regla RR preliminar: "+json.dumps(report['rr_rule'],ensure_ascii=False),
             "AAMI: no disponible. Patrones: no evaluados.",*report['cautions'],
             "SHA-256 del archivo: "+result.source_sha256]
    return "\n".join(lines).encode("utf-8")
