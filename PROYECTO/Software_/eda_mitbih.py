"""
EDA mínimo sobre MIT-BIH Arrhythmia Database.

Qué hace:
  1. Descarga (una sola vez) los registros elegidos a data/mitdb/
  2. Aplica TU pipeline (filters, peak_detection, features, classification)
  3. Compara con las anotaciones de los especialistas (.atr)
  4. Guarda gráficas y una tabla resumen en eda_output/

Uso (desde la carpeta donde están filters.py, features.py, etc.):
    pip install wfdb numpy pandas scipy matplotlib
    python eda_mitbih.py
    python eda_mitbih.py --records 100 101 200 207 --seconds 10
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import wfdb

from classification import classify_beats, summarize_classification
from features import compute_all_features
from filters import preprocess_ecg
from peak_detection import detect_r_peaks

DATA_DIR = os.path.join("data", "mitdb")
OUT_DIR = "eda_output"

# Registros válidos de MIT-BIH con variedad de ritmos:
# 100 (casi todo normal), 106 y 119 (muchas extrasístoles ventriculares), 200 (mixto)
DEFAULT_RECORDS = ["100", "106", "119", "200"]

# Símbolos de latido de las anotaciones MIT-BIH
NORMAL_SYMBOLS = {"N", "L", "R", "e", "j"}                     # clase N (AAMI)
BEAT_SYMBOLS = set("NLRBAaJSVrFejnE/fQ")                       # todo lo que es un latido

PINK = "#E38AA0"
DARK = "#A50B2A"
GREY = "#C9A9A6"


# ---------------------------------------------------------------- descarga
def download_records(records):
    os.makedirs(DATA_DIR, exist_ok=True)
    for rec in records:
        files = [f"{rec}.dat", f"{rec}.hea", f"{rec}.atr"]
        missing = [f for f in files if not os.path.exists(os.path.join(DATA_DIR, f))]
        if missing:
            print(f"Descargando registro {rec} ...")
            wfdb.dl_files("mitdb", DATA_DIR, missing)
        else:
            print(f"Registro {rec} ya está en {DATA_DIR}/")


# ------------------------------------------------------------- validación
def evaluate_detection(detected, reference, tol):
    """Sensibilidad y valor predictivo positivo de los picos R detectados."""
    detected = np.sort(np.asarray(detected))
    used = np.zeros(len(detected), dtype=bool)
    tp = 0
    for r in reference:
        i = np.searchsorted(detected, r)
        cands = [j for j in (i - 1, i)
                 if 0 <= j < len(detected) and not used[j] and abs(detected[j] - r) <= tol]
        if cands:
            j = min(cands, key=lambda k: abs(detected[k] - r))
            used[j] = True
            tp += 1
    fp = len(detected) - tp
    fn = len(reference) - tp
    sens = tp / len(reference) if len(reference) else 0.0
    ppv = tp / (tp + fp) if (tp + fp) else 0.0
    return tp, fp, fn, sens, ppv


# ---------------------------------------------------------------- análisis
def analyze_record(rec, seconds):
    path = os.path.join(DATA_DIR, rec)
    record = wfdb.rdrecord(path)
    ann = wfdb.rdann(path, "atr")
    fs = record.fs
    raw = record.p_signal[:, 0]

    filtered = preprocess_ecg(raw, fs)
    r_peaks, _ = detect_r_peaks(filtered, fs)
    feats = compute_all_features(r_peaks, fs)
    rr = feats["rr_intervals_ms"]
    labels = classify_beats(rr)
    summary = summarize_classification(labels)

    # Anotaciones: solo latidos
    mask = np.array([s in BEAT_SYMBOLS for s in ann.symbol])
    beat_samples = ann.sample[mask]
    beat_symbols = np.array(ann.symbol)[mask]
    n_total = len(beat_symbols)
    n_normal = int(np.sum([s in NORMAL_SYMBOLS for s in beat_symbols]))
    ann_normal_pct = 100 * n_normal / n_total if n_total else 0.0

    tol = int(0.15 * fs)  # ±150 ms
    tp, fp, fn, sens, ppv = evaluate_detection(r_peaks, beat_samples, tol)

    row = {
        "registro": rec,
        "fs_hz": fs,
        "duracion_min": round(len(raw) / fs / 60, 1),
        "latidos_anotados": n_total,
        "latidos_detectados": feats["n_latidos"],
        "bpm": feats["bpm"],
        "sdnn_ms": feats["hrv_sdnn_ms"],
        "anotado_normal_%": round(ann_normal_pct, 1),
        "anotado_anomalo_%": round(100 - ann_normal_pct, 1),
        "regla_RR_normal_%": summary["normal_pct"],
        "regla_RR_anomalo_%": summary["anomalo_pct"],
        "sens_picos_R_%": round(100 * sens, 2),
        "ppv_picos_R_%": round(100 * ppv, 2),
    }

    plot_record(rec, raw, filtered, r_peaks, beat_samples, beat_symbols,
                rr, row, fs, seconds)
    return row, rr


# ----------------------------------------------------------------- gráficas
def safe_savefig(fig, path):
    """Guarda la figura; si Windows la tiene bloqueada, la guarda con otro nombre."""
    try:
        fig.savefig(path, dpi=150)
    except OSError:
        alt = path.replace(".png", "_nuevo.png")
        print(f"No pude escribir {path} (¿está abierto?). Guardé {alt}")
        fig.savefig(alt, dpi=150)


def safe_to_csv(df, path):
    """Guarda el CSV; si está abierto en Excel, lo guarda con otro nombre."""
    try:
        df.to_csv(path, index=False)
    except PermissionError:
        alt = path.replace(".csv", "_nuevo.csv")
        print(f"No pude escribir {path} (¿está abierto en Excel?). Guardé {alt}")
        df.to_csv(alt, index=False)


def plot_record(rec, raw, filtered, r_peaks, beat_samples, beat_symbols, rr, row, fs, seconds):
    n = int(seconds * fs)
    t = np.arange(n) / fs

    fig = plt.figure(figsize=(12, 7))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.4, 1])

    # 1) cruda vs filtrada con picos y anotaciones
    ax = fig.add_subplot(gs[0, :])
    ax.plot(t, raw[:n], color=GREY, lw=0.8, label="cruda")
    ax.plot(t, filtered[:n], color=PINK, lw=1.2, label="filtrada")
    pk = r_peaks[r_peaks < n]
    ax.plot(pk / fs, filtered[pk], "o", color=DARK, ms=4, label="picos R detectados")
    for s, sym in zip(beat_samples, beat_symbols):
        if s < n:
            ax.axvline(s / fs, color="green" if sym in NORMAL_SYMBOLS else "red",
                       alpha=0.25, lw=2)
    ax.set_title(f"Registro {rec} - primeros {seconds} s "
                 "(líneas verdes = latido normal anotado, rojas = anómalo anotado)")
    ax.set_xlabel("tiempo (s)")
    ax.set_ylabel("mV")
    ax.legend(loc="upper right", fontsize=8)

    # 2) histograma RR
    ax = fig.add_subplot(gs[1, 0])
    ax.hist(rr, bins=40, color=PINK, edgecolor="white")
    ax.axvline(np.mean(rr), color=DARK, ls="--", label=f"media = {np.mean(rr):.0f} ms")
    ax.set_title("Histograma de intervalos RR")
    ax.set_xlabel("RR (ms)")
    ax.set_ylabel("frecuencia")
    ax.legend(fontsize=8)

    # 3) proporción normal / anómalo
    ax = fig.add_subplot(gs[1, 1])
    x = np.arange(2)
    w = 0.35
    ax.bar(x - w / 2, [row["anotado_normal_%"], row["anotado_anomalo_%"]], w,
           color=DARK, label="anotaciones (especialistas)")
    ax.bar(x + w / 2, [row["regla_RR_normal_%"], row["regla_RR_anomalo_%"]], w,
           color=PINK, label="regla RR (nuestro código)")
    ax.set_xticks(x)
    ax.set_xticklabels(["normal", "anómalo"])
    ax.set_ylabel("% de latidos")
    ax.set_title("Normal vs anómalo")
    ax.legend(fontsize=8)

    fig.suptitle(f"EDA MIT-BIH - registro {rec}   |   "
                 f"BPM {row['bpm']}  SDNN {row['sdnn_ms']} ms  |  "
                 f"Sens. picos R {row['sens_picos_R_%']}%  VPP {row['ppv_picos_R_%']}%",
                 fontsize=11)
    fig.tight_layout()
    safe_savefig(fig, os.path.join(OUT_DIR, f"eda_{rec}.png"))
    plt.close(fig)


def plot_summary(df):
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    recs = df["registro"].astype(str)

    axes[0].bar(recs, df["bpm"], color=PINK)
    axes[0].set_title("Frecuencia cardiaca promedio")
    axes[0].set_ylabel("BPM")

    axes[1].bar(recs, df["sdnn_ms"], color=DARK)
    axes[1].set_title("Variabilidad (SDNN)")
    axes[1].set_ylabel("ms")

    axes[2].bar(recs, df["anotado_normal_%"], color=PINK, label="normal")
    axes[2].bar(recs, df["anotado_anomalo_%"], bottom=df["anotado_normal_%"],
                color=DARK, label="anómalo")
    axes[2].set_title("Latidos según anotaciones")
    axes[2].set_ylabel("%")
    axes[2].legend(fontsize=8)

    for ax in axes:
        ax.set_xlabel("registro MIT-BIH")
    fig.tight_layout()
    safe_savefig(fig, os.path.join(OUT_DIR, "eda_resumen.png"))
    plt.close(fig)


# -------------------------------------------------------------------- main
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", nargs="+", default=DEFAULT_RECORDS)
    parser.add_argument("--seconds", type=int, default=10,
                        help="segundos a graficar de la señal")
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    download_records(args.records)

    rows = []
    for rec in args.records:
        print(f"Analizando registro {rec} ...")
        row, _ = analyze_record(rec, args.seconds)
        rows.append(row)

    df = pd.DataFrame(rows)
    safe_to_csv(df, os.path.join(OUT_DIR, "resumen_eda.csv"))
    plot_summary(df)

    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", None)
    print("\n=== RESUMEN ===")
    print(df.to_string(index=False))
    print(f"\nGráficas y CSV guardados en {OUT_DIR}/")


if __name__ == "__main__":
    main()