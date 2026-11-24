"""Filtrado de ECG para análisis exploratorio por ventanas."""
import numpy as np
from scipy.signal import butter, sosfiltfilt, filtfilt, iirnotch


def bandpass_filter(signal, fs, lowcut=0.5, highcut=40.0, order=4):
    if not 0 < lowcut < highcut < fs / 2:
        raise ValueError("La frecuencia de muestreo no permite el pasa-banda de 0.5–40 Hz.")
    sos = butter(order, [lowcut, highcut], btype="bandpass", fs=fs, output="sos")
    return sosfiltfilt(sos, signal)


def notch_filter(signal, fs, freq=60.0, quality=30.0):
    if freq >= fs / 2:
        return np.asarray(signal, dtype=float).copy()
    b, a = iirnotch(freq, quality, fs=fs)
    return filtfilt(b, a, signal)


def preprocess_ecg(signal, fs, mains=60):
    """Notch opcional (50/60 Hz), seguido de pasa-banda de 0.5–40 Hz.

    El filtrado de fase cero usa la ventana completa; no es un filtro en vivo.
    Un notch por encima de Nyquist se omite, sin corregir aliasing previo.
    """
    if mains not in (0, 50, 60):
        raise ValueError("La interferencia de red debe ser 0, 50 o 60 Hz.")
    x = np.asarray(signal, dtype=float)
    if mains:
        x = notch_filter(x, fs, freq=mains)
    return bandpass_filter(x, fs)
