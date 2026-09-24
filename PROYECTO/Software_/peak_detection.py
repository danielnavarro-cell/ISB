"""Detección de picos R (complejos QRS) sobre la señal filtrada."""
import numpy as np
from scipy.signal import find_peaks


def detect_r_peaks(filtered_signal, fs, min_bpm=40, max_bpm=200):
    """
    Detecta picos R usando una altura mínima adaptativa y una distancia
    mínima entre picos basada en el rango de frecuencia cardiaca esperado.
    """
    min_distance = int((60.0 / max_bpm) * fs)
    threshold = np.mean(filtered_signal) + 0.5 * np.std(filtered_signal)

    peaks, properties = find_peaks(
        filtered_signal,
        height=threshold,
        distance=min_distance,
    )
    return peaks, properties
