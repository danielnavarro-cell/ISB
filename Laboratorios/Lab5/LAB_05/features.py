"""Extracción de características a partir de los picos R detectados."""
import numpy as np


def compute_rr_intervals(r_peaks, fs):
    """Intervalos RR en milisegundos."""
    rr_samples = np.diff(r_peaks)
    return (rr_samples / fs) * 1000.0


def compute_heart_rate(rr_intervals_ms):
    """Frecuencia cardiaca promedio en BPM a partir de los intervalos RR."""
    if len(rr_intervals_ms) == 0:
        return 0.0
    mean_rr_s = np.mean(rr_intervals_ms) / 1000.0
    return 60.0 / mean_rr_s


def compute_hrv_sdnn(rr_intervals_ms):
    """SDNN: desviación estándar de los intervalos RR (variabilidad cardiaca)."""
    if len(rr_intervals_ms) < 2:
        return 0.0
    return float(np.std(rr_intervals_ms))


def compute_all_features(r_peaks, fs):
    rr = compute_rr_intervals(r_peaks, fs)
    return {
        "bpm": round(compute_heart_rate(rr), 1),
        "hrv_sdnn_ms": round(compute_hrv_sdnn(rr), 1),
        "n_latidos": len(r_peaks),
        "rr_intervals_ms": rr,
    }
