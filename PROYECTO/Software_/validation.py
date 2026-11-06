"""
Validación del detector contra las anotaciones de los cardiólogos (MIT-BIH).

Lo usan server.py (interfaz) y, si quieres, eda_mitbih.py.
"""
import numpy as np

# Símbolos de las anotaciones MIT-BIH que son latidos
BEAT_SYMBOLS = set("NLRBAaJSVrFejnE/fQ")
# Latidos que se consideran normales (clase N de AAMI)
NORMAL_SYMBOLS = {"N", "L", "R", "e", "j"}


def match_indices(detected, reference, tol):
    """
    Igual que match_beats, pero devuelve para cada pico detectado el índice
    del latido anotado con el que se emparejó, o -1 si es falso positivo.
    `detected` debe estar ordenado.
    """
    detected = np.asarray(detected)
    reference = np.asarray(reference)
    det_to_ref = np.full(len(detected), -1, dtype=np.int64)

    for k, r in enumerate(reference):
        i = np.searchsorted(detected, r)
        cands = [j for j in (i - 1, i)
                 if 0 <= j < len(detected) and det_to_ref[j] < 0 and abs(detected[j] - r) <= tol]
        if cands:
            j = min(cands, key=lambda c: abs(detected[c] - r))
            det_to_ref[j] = k
    return det_to_ref


def match_beats(detected, reference, tol):
    """
    Empareja cada latido anotado (reference) con el pico detectado más cercano
    dentro de ±tol muestras. Cada pico se usa una sola vez.

    Devuelve:
      used         -> bool por pico detectado (True = acierto, False = falso positivo)
      ref_matched  -> bool por latido anotado (True = encontrado, False = perdido)
    """
    det_to_ref = match_indices(detected, reference, tol)
    used = det_to_ref >= 0
    ref_matched = np.zeros(len(reference), dtype=bool)
    ref_matched[det_to_ref[used]] = True
    return used, ref_matched


def evaluate_detection(detected, reference, tol):
    """Devuelve (tp, fp, fn, sensibilidad, vpp). Misma salida que en eda_mitbih.py."""
    used, ref_matched = match_beats(detected, reference, tol)
    tp = int(ref_matched.sum())
    fp = int((~used).sum())
    fn = int((~ref_matched).sum())
    sens = tp / len(reference) if len(reference) else 0.0
    ppv = tp / (tp + fp) if (tp + fp) else 0.0
    return tp, fp, fn, sens, ppv
