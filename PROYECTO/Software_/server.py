"""
Backend Flask para el detector y visualizador de arritmias ECG.

Ejecutar con: python server.py
Luego abrir: http://localhost:5000
"""
import io
import numpy as np
import pandas as pd
import wfdb
from flask import Flask, jsonify, request, send_from_directory

from filters import preprocess_ecg
from peak_detection import detect_r_peaks
from features import compute_all_features
from classification import classify_beats, summarize_classification

app = Flask(__name__, static_folder="interfaz_arrit", static_url_path="")

MAX_POINTS = 2000  # límite de puntos enviados al navegador para no saturar el gráfico


def downsample(arr, max_points=MAX_POINTS):
    if len(arr) <= max_points:
        return arr
    step = len(arr) // max_points
    return arr[::step]


def run_pipeline(raw_signal, fs):
    filtered = preprocess_ecg(raw_signal, fs)
    r_peaks, _ = detect_r_peaks(filtered, fs)
    feats = compute_all_features(r_peaks, fs)
    labels = classify_beats(feats["rr_intervals_ms"])
    summary = summarize_classification(labels)

    raw_ds = downsample(raw_signal)
    filtered_ds = downsample(filtered)
    factor = max(1, len(raw_signal) // len(raw_ds)) if len(raw_ds) else 1
    peaks_ds = sorted(set(int(p // factor) for p in r_peaks if int(p // factor) < len(raw_ds)))

    return {
        "raw": [round(float(v), 4) for v in raw_ds],
        "filtered": [round(float(v), 4) for v in filtered_ds],
        "peaks": peaks_ds,
        "fs": fs,
        "bpm": feats["bpm"],
        "hrv_sdnn_ms": feats["hrv_sdnn_ms"],
        "n_latidos": feats["n_latidos"],
        "labels": labels,
        "summary": summary,
    }


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/mitbih")
def api_mitbih():
    record_id = request.args.get("record", "100")
    seconds = int(request.args.get("seconds", 15))
    fs_default = 360
    try:
        record = wfdb.rdrecord(record_id, pn_dir="mitdb", sampto=seconds * fs_default)
    except Exception as e:
        return jsonify({"error": f"No se pudo descargar el registro '{record_id}': {e}"}), 400

    raw_signal = record.p_signal[:, 0]
    result = run_pipeline(raw_signal, record.fs)
    return jsonify(result)


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

    result = run_pipeline(raw_signal, fs)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5000)