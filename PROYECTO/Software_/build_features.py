"""
Genera el CSV de features por latido (Persona 2, etapa e).

Uso:
    python build_features.py --db mitbih --detector gt          # v1: picos de referencia
    python build_features.py --db mitbih --detector pantompkins # picos del detector de P1
    python build_features.py --db icentia --detector xqrs

Salida en features_out/:
    features_<db>.csv              con --detector gt
    features_<db>_<detector>.csv   con un detector
    matching_<db>_<detector>.csv   resumen por registro de la alineación (solo detector)

Columnas (orden estable): record, split, beat_idx, r_sample, clase_aami,
    y luego features.FEATURE_COLUMNS.
  beat_idx  posición del pico dentro de la secuencia de picos del registro
            (con detector, los huecos en beat_idx son picos descartados).
  r_sample  muestra del pico a 360 Hz (anotación con gt, pico detectado si no).

Cómo se usan los picos de un detector:
  1. Se filtra la señal (filters.preprocess_ecg) y el detector recibe la señal
     SIN filtrar a 360 Hz: detect_xxx(signal, fs) -> índices de muestra
     (también se acepta una tupla (picos, ...)). Cada detector filtra a su manera.
  2. Las features (incluidos los RR) se calculan con TODOS los picos detectados,
     como pasaría en uso real.
  3. Cada pico se empareja con la anotación más cercana a ±50 ms
     (validation.match_indices, uno a uno) y hereda su clase AAMI.
  4. Falsos positivos (pico sin anotación): se descartan del CSV y se cuentan.
     Latidos no detectados: no tienen fila (no hay pico) y se cuentan.
     Picos sobre latidos excluidos (Q de Icentia): se descartan, no son FP.
"""
import argparse
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import data_loader as dl
import peak_detection
from features import FEATURE_COLUMNS, extract_beat_features
from filters import preprocess_ecg
from validation import match_indices

SEED = 42
TOL_S = 0.050
OUT_DIR = Path(__file__).resolve().parent / "features_out"
ID_COLUMNS = ["record", "split", "beat_idx", "r_sample", "clase_aami"]
COLUMNS = ID_COLUMNS + FEATURE_COLUMNS

# Nombre de la función que P1 debe exponer en peak_detection.py
DETECTORS = {
    "pantompkins": "detect_r_peaks_pantompkins",
    "xqrs": "detect_r_peaks_xqrs",
}


def get_detector(name):
    fn = getattr(peak_detection, DETECTORS[name], None)
    if fn is None:
        sys.exit(f"peak_detection.py todavía no tiene {DETECTORS[name]}(signal, fs). "
                 "Es la parte del detector (P1). Usa --detector gt mientras tanto.")
    return fn


def detect(fn, signal, fs):
    out = fn(signal, fs)
    if isinstance(out, tuple):
        out = out[0]
    peaks = np.unique(np.asarray(out, dtype=np.int64))  # ordena y quita duplicados
    return peaks[(peaks >= 0) & (peaks < len(signal))]


def process_record(db, rec_id, split, detector_fn, tol):
    rec = dl.load_record(db, rec_id)
    filtered = preprocess_ecg(rec.signal, rec.fs)
    excluded = rec.extra["excluded_samples"]

    if detector_fn is None:
        peaks = rec.ann_samples
        labels = rec.ann_aami
        keep = np.ones(len(peaks), dtype=bool)
        log = None
    else:
        peaks = detect(detector_fn, rec.signal, rec.fs)
        # Se empareja contra latidos válidos + excluidos para no contar como
        # falso positivo un pico que cae sobre un latido excluido.
        ref = np.concatenate([rec.ann_samples, excluded])
        ref_cls = np.concatenate([rec.ann_aami, np.full(len(excluded), "excluido")])
        order = np.argsort(ref, kind="stable")
        ref, ref_cls = ref[order], ref_cls[order]
        det_to_ref = match_indices(peaks, ref, tol)
        matched = det_to_ref >= 0
        labels = np.where(matched, ref_cls[np.maximum(det_to_ref, 0)], "")
        keep = matched & (labels != "excluido")

        n_valid = len(rec.ann_samples)
        tp = int(keep.sum())
        log = {
            "record": rec_id, "split": split,
            "anotados": n_valid, "detectados": len(peaks),
            "emparejados": tp,
            "falsos_positivos": int((~matched).sum()),
            "no_detectados": n_valid - tp,
            "sobre_excluidos": int((matched & (labels == "excluido")).sum()),
            "sens_%": round(100 * tp / n_valid, 2) if n_valid else np.nan,
            "vpp_%": round(100 * tp / (tp + (~matched).sum()), 2) if len(peaks) else np.nan,
        }

    feats = extract_beat_features(filtered, peaks, rec.fs)
    ids = pd.DataFrame({
        "record": rec_id, "split": split, "beat_idx": np.arange(len(peaks)),
        "r_sample": peaks, "clase_aami": labels,
    })
    df = pd.concat([ids, feats], axis=1)[COLUMNS]
    return df[keep].reset_index(drop=True), log


def build(db, detector, tol_s=TOL_S, out_dir=OUT_DIR):
    random.seed(SEED)
    np.random.seed(SEED)
    detector_fn = None if detector == "gt" else get_detector(detector)
    tol = int(round(tol_s * dl.TARGET_FS))

    ds1, ds2 = dl.get_split(db)
    parts, logs = [], []
    for split, recs in (("DS1", ds1), ("DS2", ds2)):
        for rec_id in recs:
            df, log = process_record(db, rec_id, split, detector_fn, tol)
            parts.append(df)
            if log:
                logs.append(log)
            print(f"  {db} {split} {rec_id}: {len(df)} latidos")

    out = pd.concat(parts, ignore_index=True)
    out["beat_idx"] = out["beat_idx"].astype(np.int64)
    out["r_sample"] = out["r_sample"].astype(np.int64)
    for c in ("borde", "rr_corto"):
        out[c] = out[c].astype(np.int8)

    out_dir.mkdir(exist_ok=True)
    name = f"features_{db}.csv" if detector == "gt" else f"features_{db}_{detector}.csv"
    path = out_dir / name
    out.to_csv(path, index=False, float_format="%.6g", lineterminator="\n")
    print(f"{path.name}: {len(out)} filas x {out.shape[1]} columnas")
    print(out.groupby(["split", "clase_aami"]).size().unstack(fill_value=0).to_string())

    if logs:
        lg = pd.DataFrame(logs)
        lg.to_csv(out_dir / f"matching_{db}_{detector}.csv", index=False, lineterminator="\n")
        tot = lg[["anotados", "detectados", "emparejados", "falsos_positivos",
                  "no_detectados", "sobre_excluidos"]].sum()
        print(tot.to_string())
    return path


def main(argv=None):
    p = argparse.ArgumentParser(description="CSV de features por latido.")
    p.add_argument("--db", required=True, choices=["mitbih", "icentia"])
    p.add_argument("--detector", default="gt", choices=["gt", *DETECTORS])
    p.add_argument("--tol-ms", type=float, default=TOL_S * 1000,
                   help="tolerancia de emparejamiento pico-anotación (ms)")
    a = p.parse_args(argv)
    build(a.db, a.detector, a.tol_ms / 1000)


if __name__ == "__main__":
    main()
