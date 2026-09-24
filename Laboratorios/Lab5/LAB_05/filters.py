"""Filtrado de la señal ECG cruda."""
import numpy as np
from scipy.signal import butter, filtfilt, iirnotch


def bandpass_filter(signal, fs, lowcut=0.5, highcut=40.0, order=4):
    """Filtro pasa-banda para eliminar deriva de línea base y ruido de alta frecuencia."""
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype="band")
    return filtfilt(b, a, signal)


def notch_filter(signal, fs, freq=60.0, quality=30.0):
    """Filtro notch para eliminar interferencia de la línea eléctrica (60 Hz)."""
    nyq = 0.5 * fs
    w0 = freq / nyq
    b, a = iirnotch(w0, quality)
    return filtfilt(b, a, signal)


def preprocess_ecg(signal, fs):
    """Pipeline completo: notch + pasa-banda."""
    signal = notch_filter(signal, fs)
    signal = bandpass_filter(signal, fs)
    return signal
