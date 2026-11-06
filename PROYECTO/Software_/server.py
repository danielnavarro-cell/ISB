"""
Backend Flask para el detector y visualizador de arritmias ECG.

Ejecutar con: python server.py
Luego abrir: http://localhost:5000
"""
import io
import os

import numpy as np
import pandas as pd
import wfdb
from flask import Flask, jsonify, request, send_from_directory

from classification import classify_beats, summarize_classification
from features import compute_all_features
from filters import preprocess_ecg
from peak_detection import detect_r_peaks
from validation import BEAT_SYMBOLS, NORMAL_SYMBOLS, match_beats

app = Flask(__name__, static_folder="interfaz_arrit", static_url_path="")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "mitdb")  # registros descargados con eda_mitbih.py

# Máximo de puntos enviados al navegador. Con 25000 no se submuestrea nada
# hasta 60 s de MIT-BIH (21600 muestras), así los picos caen justo en la señal.
MAX_POINTS = 25000


def build_validation(r_peaks, fs, ann_samples, ann_symbols, step):
    """Compara los picos R detectados con los latidos anotados por los especialistas."""
    if ann_samples is None or len(ann_samples) == 0:
        return None

    symbols = np.array(ann_symbols)
    is_beat = np.array([s in BEAT_SYMBOLS for s in symbols])
    ref = np.asarray(ann_samples)[is_beat]
    syms = symbols[is_beat]
    if len(ref) == 0:
        return None

    tol = int(0.15 * fs)  # ±150 ms
    used, ref_matched = match_beats(r_peaks, ref, tol)
    tp = int(ref_matched.sum())
    fp = int((~used).sum())
    fn = int((~ref_matched).sum())
    sens = tp / len(ref)
    ppv = tp / (tp + fp) if (tp + fp) else 0.0

    normal_mask = np.array([s in NORMAL_SYMBOLS for s in syms])
    anomalo_pct = 100 * (1 - normal_mask.mean())

    def ds(idx):  # índices de muestra -> índices de la señal enviada al navegador
        return [int(i // step) for i in idx]

    return {
        "n_anotados": int(len(ref)),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "sens": round(100 * sens, 1),
        "ppv": round(100 * ppv, 1),
        "anotado_anomalo_pct": round(float(anomalo_pct), 1),
        "ann_normal": ds(ref[normal_mask]),
        "ann_anomalo": ds(ref[~normal_mask]),
        "fp_peaks": ds(np.asarray(r_peaks)[~used]),
        "fn_beats": ds(ref[~ref_matched]),
    }


def run_pipeline(raw_signal, fs, ann_samples=None, ann_symbols=None):
    filtered = preprocess_ecg(raw_signal, fs)
    r_peaks, _ = detect_r_peaks(filtered, fs)
    feats = compute_all_features(r_peaks, fs)
    labels = classify_beats(feats["rr_intervals_ms"])
    summary = summarize_classification(labels)

    n = len(raw_signal)
    step = 1 if n <= MAX_POINTS else n // MAX_POINTS
    raw_ds = raw_signal[::step]
    filtered_ds = filtered[::step]
    peaks_ds = sorted(set(int(p // step) for p in r_peaks))

    return {
        "raw": [round(float(v), 4) for v in raw_ds],
        "filtered": [round(float(v), 4) for v in filtered_ds],
        "peaks": peaks_ds,
        "fs": fs,
        "fs_ds": fs / step,  # muestras por segundo de la señal enviada (para el eje de tiempo)
        "bpm": feats["bpm"],
        "hrv_sdnn_ms": feats["hrv_sdnn_ms"],
        "n_latidos": feats["n_latidos"],
        "labels": labels,
        "summary": summary,
        "validation": build_validation(r_peaks, fs, ann_samples, ann_symbols, step),
    }


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/mitbih")
def api_mitbih():
    record_id = request.args.get("record", "100").strip()
    if not record_id.isalnum():
        return jsonify({"error": "Registro inválido."}), 400
    try:
        seconds = int(request.args.get("seconds", 15))
    except ValueError:
        seconds = 15
    seconds = max(5, min(seconds, 60))
    sampto = seconds * 360

    # Usa el registro local (data/mitdb/) si existe; si no, lo descarga de PhysioNet
    local = os.path.join(DATA_DIR, record_id)
    use_local = os.path.exists(local + ".dat") and os.path.exists(local + ".hea")

    try:
        if use_local:
            record = wfdb.rdrecord(local, sampto=sampto)
        else:
            record = wfdb.rdrecord(record_id, pn_dir="mitdb", sampto=sampto)
    except Exception as e:
        return jsonify({"error": f"No se pudo leer el registro '{record_id}': {e}"}), 400

    raw_signal = record.p_signal[:, 0]

    # Anotaciones de los especialistas (.atr) para la misma ventana de tiempo
    ann_samples, ann_symbols = None, None
    try:
        if use_local:
            ann = wfdb.rdann(local, "atr", sampto=len(raw_signal))
        else:
            ann = wfdb.rdann(record_id, "atr", pn_dir="mitdb", sampto=len(raw_signal))
        ann_samples, ann_symbols = ann.sample, ann.symbol
    except Exception:
        pass  # sin anotaciones: la interfaz funciona igual, solo sin comparación

    return jsonify(run_pipeline(raw_signal, record.fs, ann_samples, ann_symbols))


@app.route("/api/upload", methods=["POST"])
def api_upload():
    if "file" not in request.files:
        return jsonify({"error": "No se recibió ningún archivo"}), 400
    fs = int(request.form.get("fs", 360))
    file = request.files["file"]
    try:
        raw_signal = pd.read_csv(io.BytesIO(file.read())).iloc[:, 0].values.astype(float)
    except Exception as e:
        return jsonify({"error": f"No se pudo leer el CSV: {e}"}), 400

    # Un CSV propio no tiene anotaciones, así que no hay comparación
    return jsonify(run_pipeline(raw_signal, fs))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
