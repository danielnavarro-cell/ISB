"""
Carga de bases de ECG para clasificación de latidos (Persona 2).

Bases:
  - "mitbih"  : MIT-BIH Arrhythmia Database (PhysioNet `mitdb`), 360 Hz.
  - "icentia" : Icentia11k (PhysioNet `icentia11k-continuous-ecg`), 250 Hz -> se
                remuestrea a 360 Hz.

Todo se devuelve a TARGET_FS = 360 Hz y con UNA derivación:
  - MIT-BIH: MLII. Es la derivación que tienen 46 de los 48 registros (102 y 104
    no la tienen, pero se excluyen por marcapasos) y la que usa la literatura
    (de Chazal 2004). Se elige por nombre, no por posición: en el registro 114
    MLII está en el canal 1, no en el 0.
  - Icentia11k: la única que existe (parche CardioSTAT de una derivación,
    parecida a una derivación I modificada). Su morfología difiere de MLII, lo
    que es una fuente esperable de diferencias al evaluar entre bases.

Remuestreo (solo Icentia): scipy.signal.resample_poly(x, 36, 25), es decir
250 * 36 / 25 = 360 Hz, con filtro antialiasing incluido. Las anotaciones se
reescalan con round(muestra * 360 / 250).

Los archivos se descargan una sola vez a data/<carpeta>/ (rutas relativas al repo).

Uso:
    from data_loader import list_records, load_record, get_split
    rec = load_record("mitbih", "100")
    ds1, ds2 = get_split("mitbih")
"""
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import wfdb
from scipy.signal import resample_poly

TARGET_FS = 360
DATA_ROOT = Path(__file__).resolve().parent / "data"

# ------------------------------------------------------------------ AAMI
# Tabla símbolo -> clase AAMI (ANSI/AAMI EC57; de Chazal et al. 2004).
AAMI_MAP = {
    # N: latido normal y bloqueos de rama, escapes nodales/auriculares
    "N": "N", "L": "N", "R": "N", "e": "N", "j": "N",
    # S: ectópicos supraventriculares
    "A": "S", "a": "S", "J": "S", "S": "S",
    # V: ectópicos ventriculares
    "V": "V", "E": "V",
    # F: fusión ventricular + normal
    "F": "F",
    # Q: marcapasos, fusión de marcapasos, no clasificable
    "/": "Q", "f": "Q", "Q": "Q",
}
AAMI_CLASSES = ("N", "S", "V", "F", "Q")

# Anotaciones de MIT-BIH/Icentia que NO son latidos (se ignoran). Se listan
# para documentar; cualquier símbolo fuera de AAMI_MAP se ignora igual.
NON_BEAT_SYMBOLS = {
    "+": "cambio de ritmo", "~": "cambio de calidad de señal", "|": "artefacto aislado",
    "x": "onda P no conducida", "!": "onda de flutter ventricular",
    "[": "inicio de flutter/fibrilación ventricular", "]": "fin de flutter/fibrilación ventricular",
    '"': "comentario", "p": "pico de onda P", "t": "pico de onda T", "u": "pico de onda U",
    "`": "inicio de onda", "'": "fin de onda", "^": "espiga de marcapasos no capturada",
    "s": "cambio de ST", "T": "cambio de onda T", "*": "sístole", "D": "diástole",
    "=": "medida", "@": "enlace externo",
}


# Clases que se excluyen por base. En Icentia11k "Q" significa latido sin
# definir (tramos ruidosos o no revisados; hasta 89 % de un registro), no
# equivale a la Q de MIT-BIH, así que se saca del dataset.
EXCLUDED_CLASSES = {"mitbih": set(), "icentia": {"Q"}}


def symbol_to_aami(symbol):
    """Clase AAMI de un símbolo de anotación, o None si no es un latido."""
    return AAMI_MAP.get(symbol)


# ------------------------------------------------------------- MIT-BIH
MITBIH_PACED = ("102", "104", "107", "217")

# Split por paciente de de Chazal et al. (2004), sin registros con marcapasos.
MITBIH_DS1 = (
    "101", "106", "108", "109", "112", "114", "115", "116", "118", "119", "122",
    "124", "201", "203", "205", "207", "208", "209", "215", "220", "223", "230",
)
MITBIH_DS2 = (
    "100", "103", "105", "111", "113", "117", "121", "123", "200", "202", "210",
    "212", "213", "214", "219", "221", "222", "228", "231", "232", "233", "234",
)

# Los registros 201 y 202 son del MISMO paciente (documentación de MIT-BIH).
# En el split de de Chazal quedan en DS1 y DS2 respectivamente: eso es fuga de
# datos a nivel de paciente. Con strict=True (por defecto) se saca 202 de DS2.
MITBIH_SAME_PATIENT = {"202": "201"}


def _mitbih_patient(record_id):
    return MITBIH_SAME_PATIENT.get(record_id, record_id)


# ------------------------------------------------------------ Icentia11k
ICENTIA_PN_DIR = "icentia11k-continuous-ecg"
ICENTIA_FS = 250
# 30 pacientes elegidos al azar con np.random.default_rng(42).choice(11000, 30,
# replace=False). Se fija la lista aquí para no depender de la versión de numpy.
ICENTIA_SUBSET = (
    "p00943", "p00979", "p01034", "p01407", "p02006", "p02211", "p04075", "p04425",
    "p04752", "p04816", "p04877", "p04949", "p05499", "p05638", "p05781", "p05999",
    "p07079", "p07182", "p07655", "p07881", "p08080", "p08360", "p08491", "p08593",
    "p08635", "p09048", "p09227", "p09423", "p10188", "p10714",
)
ICENTIA_SEGMENT = "s00"  # un segmento (~70 min) por paciente


def _icentia_parts(record_id):
    """'p00943' o 'p00943_s03' -> (paciente, nombre del segmento, subcarpeta)."""
    if "_" in record_id:
        patient, seg = record_id.split("_", 1)
    else:
        patient, seg = record_id, ICENTIA_SEGMENT
    name = f"{patient}_{seg}"
    subdir = f"{patient[:3]}/{patient}"  # p00/p00943
    return patient, name, subdir


# ------------------------------------------------------------- registros
@dataclass
class Record:
    db: str
    record_id: str
    patient_id: str
    signal: np.ndarray          # 1-D, mV, a `fs` Hz
    fs: int                     # siempre TARGET_FS
    fs_orig: int
    lead: str
    ann_samples: np.ndarray     # solo latidos, en muestras a `fs`
    ann_symbols: np.ndarray     # símbolo original
    ann_aami: np.ndarray        # clase AAMI (N, S, V, F, Q)
    extra: dict = field(default_factory=dict)

    @property
    def duration_s(self):
        return len(self.signal) / self.fs


_DB_DIRS = {"mitbih": "mitdb", "icentia": "icentia11k"}


def _check_db(db):
    if db not in _DB_DIRS:
        raise ValueError(f"Base desconocida '{db}'. Opciones: {sorted(_DB_DIRS)}")


def list_records(db, include_paced=False):
    """Lista de identificadores de registro de la base."""
    _check_db(db)
    if db == "mitbih":
        recs = sorted(MITBIH_DS1 + MITBIH_DS2)
        if include_paced:
            recs = sorted(recs + list(MITBIH_PACED))
        return recs
    return list(ICENTIA_SUBSET)


def get_split(db, strict=True):
    """
    Split por paciente -> (DS1 entrenamiento, DS2 prueba), listas de record_id.

    mitbih : de Chazal. Con strict=True se quita 202 de DS2 (mismo paciente que
             201, que está en DS1). strict=False devuelve el split original para
             comparar con la literatura.
    icentia: se usa entera como prueba externa entre bases: DS1 vacío.
    """
    _check_db(db)
    if db == "mitbih":
        ds2 = [r for r in MITBIH_DS2 if not (strict and r in MITBIH_SAME_PATIENT)]
        return list(MITBIH_DS1), ds2
    return [], list(ICENTIA_SUBSET)


def get_patient_id(db, record_id):
    _check_db(db)
    if db == "mitbih":
        return _mitbih_patient(record_id)
    return _icentia_parts(record_id)[0]


def split_of(db, record_id, strict=True):
    """'DS1', 'DS2' o None si el registro no está en el split."""
    ds1, ds2 = get_split(db, strict=strict)
    if record_id in ds1:
        return "DS1"
    if record_id in ds2:
        return "DS2"
    return None


# -------------------------------------------------------------- descarga
def _local_base(db, record_id):
    folder = DATA_ROOT / _DB_DIRS[db]
    if db == "mitbih":
        return folder / record_id, None, record_id
    _, name, subdir = _icentia_parts(record_id)
    return folder / subdir / name, subdir, name


def ensure_downloaded(db, record_id):
    """Descarga .hea/.dat/.atr si faltan. Devuelve la ruta base local (sin extensión)."""
    _check_db(db)
    base, subdir, name = _local_base(db, record_id)
    exts = (".hea", ".dat", ".atr")
    missing = [e for e in exts if not base.with_suffix(e).exists()]
    if missing:
        base.parent.mkdir(parents=True, exist_ok=True)
        if db == "mitbih":
            wfdb.dl_files("mitdb", str(base.parent), [name + e for e in missing])
        else:
            wfdb.dl_files(ICENTIA_PN_DIR, str(DATA_ROOT / _DB_DIRS[db]),
                          [f"{subdir}/{name}{e}" for e in missing])
    return base


def download_all(db):
    for rec in list_records(db):
        ensure_downloaded(db, rec)


# ------------------------------------------------------------------ carga
def _beats_only(samples, symbols):
    symbols = np.asarray(symbols, dtype=object)
    aami = np.array([symbol_to_aami(s) for s in symbols], dtype=object)
    keep = aami != None  # noqa: E711  (comparación elemento a elemento)
    return (np.asarray(samples)[keep].astype(np.int64),
            symbols[keep].astype(str), aami[keep].astype(str))


def load_record(db, record_id, drop_excluded=True):
    """
    Carga un registro completo: señal de una derivación a 360 Hz (mV) y sus
    anotaciones de latido con la clase AAMI. Descarga si hace falta.

    Con drop_excluded=True se quitan las clases de EXCLUDED_CLASSES[db] de
    ann_*; sus posiciones quedan en extra["excluded_samples"] (sirven para no
    contar como falso positivo un pico detectado sobre un latido excluido).
    """
    _check_db(db)
    record_id = str(record_id)
    base = ensure_downloaded(db, record_id)
    rec = wfdb.rdrecord(str(base))
    ann = wfdb.rdann(str(base), "atr")
    fs_orig = int(rec.fs)

    if db == "mitbih":
        if "MLII" not in rec.sig_name:
            raise ValueError(f"El registro {record_id} no tiene MLII ({rec.sig_name}).")
        ch = rec.sig_name.index("MLII")
        lead = "MLII"
    else:
        ch, lead = 0, rec.sig_name[0]

    signal = rec.p_signal[:, ch].astype(np.float64)
    samples = np.asarray(ann.sample)

    # NaN en la señal (raro, pero existe en algunas bases): se rellenan por
    # interpolación lineal antes de remuestrear/filtrar.
    n_nan = int(np.isnan(signal).sum())
    if n_nan:
        signal = _fill_nan(signal)

    if fs_orig != TARGET_FS:
        signal = _resample(signal, fs_orig, TARGET_FS)
        samples = np.round(samples * TARGET_FS / fs_orig).astype(np.int64)

    samples, symbols, aami = _beats_only(samples, ann.symbol)
    inside = (samples >= 0) & (samples < len(signal))
    samples, symbols, aami = samples[inside], symbols[inside], aami[inside]

    excl = np.isin(aami, list(EXCLUDED_CLASSES[db])) if drop_excluded else np.zeros(len(aami), bool)

    return Record(
        db=db, record_id=record_id, patient_id=get_patient_id(db, record_id),
        signal=signal, fs=TARGET_FS, fs_orig=fs_orig, lead=lead,
        ann_samples=samples[~excl], ann_symbols=symbols[~excl], ann_aami=aami[~excl],
        extra={"n_nan_rellenados": n_nan, "excluded_samples": samples[excl],
               "n_excluidos": int(excl.sum())},
    )


def _resample(x, fs_in, fs_out):
    from math import gcd
    g = gcd(int(fs_out), int(fs_in))
    return resample_poly(x, int(fs_out) // g, int(fs_in) // g)


def _fill_nan(x):
    x = x.copy()
    bad = np.isnan(x)
    if bad.all():
        return np.zeros_like(x)
    idx = np.arange(len(x))
    x[bad] = np.interp(idx[bad], idx[~bad], x[~bad])
    return x
