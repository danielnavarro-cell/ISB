"""Extracción de características a partir de los picos R detectados."""
import numpy as np
import pandas as pd


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


# =====================================================================
# Features por latido para el clasificador (Persona 2)
# =====================================================================
PRE_S = 0.25          # ventana: 0.25 s antes de R
POST_S = 0.40         # ... y 0.40 s después
N_WINDOW = 100        # remuestreada a 100 puntos
LOCAL_RR_BEATS = 10   # media local de RR: ~10 intervalos centrados en el latido
SHORT_RR_S = 0.20     # RR < 200 ms -> pico sospechoso (rr_corto = 1)
QRS_SEARCH_S = 0.15   # búsqueda de QRS: ±150 ms alrededor de R
QRS_SMOOTH_S = 0.010  # suavizado de |derivada|: 10 ms
QRS_THRESH = 0.15     # umbral: 15 % de la pendiente máxima
QRS_GAP_S = 0.010     # el QRS termina tras 10 ms seguidos bajo el umbral
QRS_MIN_S, QRS_MAX_S = 0.04, 0.20

RR_COLUMNS = ["rr_prev", "rr_next", "rr_local", "rr_prev_ratio", "rr_next_ratio"]
MORPH_COLUMNS = ["r_amp", "qrs_width"]
FLAG_COLUMNS = ["borde", "rr_corto"]
WINDOW_COLUMNS = [f"w_{i:03d}" for i in range(N_WINDOW)]
FEATURE_COLUMNS = RR_COLUMNS + MORPH_COLUMNS + FLAG_COLUMNS + WINDOW_COLUMNS


def extract_beat_features(signal, r_peaks, fs):
    """
    Features de cada latido. `signal` debe estar ya filtrada (filters.preprocess_ecg)
    y `r_peaks` ordenados (índices de muestra). Devuelve un DataFrame con una fila
    por pico, en el mismo orden, y columnas FEATURE_COLUMNS (orden estable).

    RR (segundos):
      rr_prev, rr_next   intervalo con el latido anterior / siguiente.
      rr_local           media de ~10 intervalos RR centrados en el latido.
      rr_*_ratio         rr_prev / rr_local y rr_next / rr_local.
    Morfología:
      r_amp              valor de la señal filtrada en R (mV; el pasa-altos
                         de 0.5 Hz ya quita la línea base).
      qrs_width          ancho de QRS (s), ver _qrs_width.
      w_000..w_099       señal de R-0.25 s a R+0.40 s remuestreada a 100 puntos
                         (interpolación lineal; la señal ya está limitada a 40 Hz).
    Bordes y casos raros:
      borde = 1          primer o último latido: el RR que falta se copia del
                         otro (rr_prev <- rr_next y al revés).
      rr_corto = 1       algún RR < 200 ms (posible pico duplicado o falso).
      Ventana fuera de la señal: se rellena repitiendo el valor del extremo.
      NaN en la señal: se interpolan linealmente antes de calcular nada.
      Un solo latido: los RR quedan NaN (no hay forma de estimarlos).
    """
    x = np.asarray(signal, dtype=np.float64)
    r = np.asarray(r_peaks, dtype=np.int64).ravel()
    n = len(r)
    if n == 0:
        return pd.DataFrame(columns=FEATURE_COLUMNS, dtype=np.float64)
    if np.any(np.diff(r) < 0):
        raise ValueError("r_peaks debe estar ordenado.")
    if r[0] < 0 or r[-1] >= len(x):
        raise ValueError("Hay picos fuera de la señal.")
    if np.isnan(x).any():
        x = _interp_nan(x)

    rr_prev, rr_next, rr_local, borde, rr_corto = _rr_features(r, fs)
    with np.errstate(divide="ignore", invalid="ignore"):
        prev_ratio = rr_prev / rr_local
        next_ratio = rr_next / rr_local

    qrs = np.array([_qrs_width(x, p, fs) for p in r])
    windows = _beat_windows(x, r, fs)

    cols = {
        "rr_prev": rr_prev, "rr_next": rr_next, "rr_local": rr_local,
        "rr_prev_ratio": prev_ratio, "rr_next_ratio": next_ratio,
        "r_amp": x[r], "qrs_width": qrs,
        "borde": borde, "rr_corto": rr_corto,
    }
    df = pd.concat([pd.DataFrame(cols), pd.DataFrame(windows, columns=WINDOW_COLUMNS)], axis=1)
    return df[FEATURE_COLUMNS]


def _rr_features(r, fs):
    n = len(r)
    rr = np.diff(r) / fs                       # rr[k]: entre latido k y k+1
    rr_prev = np.full(n, np.nan)
    rr_next = np.full(n, np.nan)
    rr_prev[1:] = rr
    rr_next[:-1] = rr

    rr_corto = ((rr_prev < SHORT_RR_S) | (rr_next < SHORT_RR_S)).astype(np.int8)
    borde = np.zeros(n, dtype=np.int8)
    borde[[0, -1]] = 1
    rr_prev[0] = rr_next[0]                    # bordes: copiar el RR que sí existe
    rr_next[-1] = rr_prev[-1]

    rr_local = np.full(n, np.nan)
    if len(rr):
        half = LOCAL_RR_BEATS // 2
        csum = np.concatenate([[0.0], np.cumsum(rr)])
        lo = np.clip(np.arange(n) - half, 0, len(rr))
        hi = np.clip(np.arange(n) + half, 0, len(rr))
        hi = np.maximum(hi, lo + 1)            # al menos un intervalo
        lo = np.minimum(lo, len(rr) - 1)
        hi = np.minimum(hi, len(rr))
        rr_local = (csum[hi] - csum[lo]) / (hi - lo)
    return rr_prev, rr_next, rr_local, borde, rr_corto


def _qrs_width(x, r, fs):
    """
    Ancho de QRS por pendiente (método simple):
      1. Tramo de ±150 ms alrededor de R.
      2. |derivada| suavizada con media móvil de 10 ms.
      3. Umbral = 15 % del máximo de esa pendiente dentro de ±60 ms de R.
      4. Desde R se camina hacia la izquierda y hacia la derecha; el QRS
         termina cuando la pendiente pasa 10 ms seguidos bajo el umbral (así no
         se corta en el propio pico R, donde la derivada es ~0).
      5. Se recorta a [40, 200] ms.
    """
    half = int(round(QRS_SEARCH_S * fs))
    a, b = max(r - half, 0), min(r + half + 1, len(x))
    seg = x[a:b]
    if len(seg) < 3:
        return np.nan
    d = np.abs(np.diff(seg))
    k = max(int(round(QRS_SMOOTH_S * fs)), 1)
    d = np.convolve(d, np.ones(k) / k, mode="same")
    c = r - a                                   # posición de R en el tramo
    near = int(round(0.06 * fs))
    lo, hi = max(c - near, 0), min(c + near, len(d))
    peak = d[lo:hi].max() if hi > lo else d.max()
    if peak <= 0:
        return np.nan
    thr = QRS_THRESH * peak
    gap = max(int(round(QRS_GAP_S * fs)), 1)

    def walk(start, step):
        i, run, edge = start, 0, start
        while 0 <= i < len(d):
            if d[i] < thr:
                run += 1
                if run >= gap:
                    return edge
            else:
                run, edge = 0, i
            i += step
        return edge

    c = min(c, len(d) - 1)
    onset, offset = walk(c, -1), walk(c, +1)
    width = (offset - onset + 1) / fs
    return float(np.clip(width, QRS_MIN_S, QRS_MAX_S))


def _beat_windows(x, r, fs):
    pre = int(round(PRE_S * fs))
    post = int(round(POST_S * fs))
    padded = np.pad(x, (pre, post), mode="edge")   # bordes: repetir el extremo
    idx = r[:, None] + np.arange(pre + post + 1)[None, :]  # índices en `padded`
    raw = padded[idx]                                       # (n, pre+post+1)
    src = np.linspace(0.0, 1.0, raw.shape[1])
    dst = np.linspace(0.0, 1.0, N_WINDOW)
    return np.vstack([np.interp(dst, src, row) for row in raw])


def _interp_nan(x):
    x = x.copy()
    bad = np.isnan(x)
    if bad.all():
        return np.zeros_like(x)
    i = np.arange(len(x))
    x[bad] = np.interp(i[bad], i[~bad], x[~bad])
    return x
