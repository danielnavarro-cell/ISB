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


def _raw_input(signal, fs):
    """Validate the RAW single-channel adapter contract, without mutating data."""
    x = np.asarray(signal, dtype=float)
    if not np.isfinite(fs) or not 100 <= fs <= 10000:
        raise ValueError("Los adaptadores QRS requieren 100-10000 Hz.")
    if x.ndim != 1 or len(x) < int(2 * fs) or not np.isfinite(x).all():
        raise ValueError("Se requieren al menos 2 s de senal 1D finita.")
    return x


def _standardize(x):
    # Dimensionless numerical normalization, NOT an ADC-to-mV calibration.
    return (x - np.median(x)) / np.std(x)


def detect_r_peaks_find_peaks(signal, fs):
    """RAW adapter: exactly one original notch/bandpass + unchanged baseline."""
    from filters import preprocess_ecg
    x = _raw_input(signal, fs)
    if np.ptp(x) == 0:
        return np.array([], dtype=np.int64)
    return detect_r_peaks(preprocess_ecg(x, fs), fs)[0].astype(np.int64)


def pan_tompkins_details(signal, fs):
    """Return (native energy candidates, localized QRS extrema).

    py-ecg-detectors 1.3.5 is an identified VARIANT, not an exact 1985 replica:
    causal first-order Butterworth 5-15 Hz, first difference, square, 150 ms
    moving average, adaptive thresholds/searchback; no explicit T-slope test.
    Native outputs are delayed energy peaks. Fixed localization uses the
    largest absolute deviation from the local median in [-200,+50] ms of RAW
    data. No annotations, score-based offset fitting, or extra bandpass.
    Duplicate localized indices are removed per the existing builder contract;
    native candidates remain available to audit this effect. Offline adapter.
    """
    from ecgdetectors import Detectors
    x = _raw_input(signal, fs)
    if np.ptp(x) == 0:
        empty = np.array([], dtype=np.int64)
        return empty, empty.copy()
    native = np.asarray(Detectors(fs).pan_tompkins_detector(_standardize(x)), dtype=np.int64)
    localized = []
    for p in native:
        a, b = max(0, p-round(.2*fs)), min(len(x), p+round(.05*fs)+1)
        segment = x[a:b]
        localized.append(a + int(np.argmax(np.abs(segment-np.median(segment)))))
    return native, np.unique(np.asarray(localized, dtype=np.int64))


def detect_r_peaks_pantompkins(signal, fs):
    """RAW adapter returning indices at the ORIGINAL sampling frequency."""
    return pan_tompkins_details(signal, fs)[1]


def detect_r_peaks_xqrs(signal, fs):
    """RAW WFDB XQRS, defaults (T-wave inspection disabled), own 5-20 Hz filter.

    Center/scale only for numerical amplitude consistency. No external notch,
    no external bandpass and no annotation-derived temporal correction.
    """
    from wfdb.processing import xqrs_detect
    x = _raw_input(signal, fs)
    if np.ptp(x) == 0:
        return np.array([], dtype=np.int64)
    return np.asarray(xqrs_detect(_standardize(x), fs, verbose=False), dtype=np.int64)
