"""
Clasificación básica de latidos como 'Normal' o 'Anómalo'.

Esta es una versión simple basada en reglas (umbral sobre el intervalo RR
respecto al promedio local). Se puede reemplazar más adelante por un
clasificador entrenado (ej. comparando contra las anotaciones del MIT-BIH).
"""
import numpy as np


def classify_beats(rr_intervals_ms, deviation_threshold=0.20):
    """
    Devuelve una lista de etiquetas ('Normal' / 'Anómalo'), una por cada
    intervalo RR, comparando cada intervalo contra el promedio móvil local.
    """
    if len(rr_intervals_ms) == 0:
        return []

    mean_rr = np.mean(rr_intervals_ms)
    labels = []
    for rr in rr_intervals_ms:
        deviation = abs(rr - mean_rr) / mean_rr
        labels.append("Anómalo" if deviation > deviation_threshold else "Normal")
    return labels


def summarize_classification(labels):
    total = len(labels)
    if total == 0:
        return {"normal_pct": 0.0, "anomalo_pct": 0.0}
    normales = labels.count("Normal")
    return {
        "normal_pct": round(100 * normales / total, 1),
        "anomalo_pct": round(100 * (total - normales) / total, 1),
    }
