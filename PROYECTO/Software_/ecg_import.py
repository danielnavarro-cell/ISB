"""Importación de ECG: OpenSignals TXT y CSV de una columna."""
import io
import json
import numpy as np
import pandas as pd


MAX_RECORD_SAMPLES = 2_000_000


def validate_signal(signal, fs, *, max_samples=600000):
    if not np.isfinite(fs) or not 100 <= fs <= 10000:
        raise ValueError("La frecuencia debe estar entre 100 y 10000 Hz para este análisis.")
    x = np.asarray(signal, dtype=float)
    if x.ndim != 1 or len(x) < max(32, int(5 * fs)):
        raise ValueError("Se necesitan al menos 5 segundos de señal.")
    if len(x) > max_samples:
        raise ValueError(f"La señal supera el límite de {max_samples} muestras; no se recorta automáticamente.")
    if not np.isfinite(x).all():
        raise ValueError("La señal contiene valores vacíos, NaN o infinitos.")
    if np.ptp(x) == 0:
        raise ValueError("La señal es constante. Revisa el canal ECG seleccionado.")
    return x


def load_ecg_file(content, fs=1000, channel="auto", start=0, seconds=15, *, windowed=False, full_record=False):
    """Legacy window by default; full_record explicitly imports every sample.

    Complete records use the same parser and validations, with a declared
    memory limit. Neither mode silently truncates to fit a sample limit.
    """
    if full_record:
        if windowed or start != 0:
            raise ValueError("La lectura completa no admite recorte ni inicio distinto de cero.")
        info = inspect_ecg_file(content)
        if info['total_samples'] > MAX_RECORD_SAMPLES:
            raise ValueError(f"Registro demasiado grande: máximo {MAX_RECORD_SAMPLES} muestras, sin truncamiento.")
    if windowed:
        return _load_selected_rows(content, fs, channel, start, seconds)
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("El archivo debe ser TXT o CSV en UTF-8.") from exc
    if not full_record and (not np.isfinite(start) or start < 0 or not 5 <= seconds <= 60):
        raise ValueError("El inicio debe ser positivo y el tramo debe durar entre 5 y 60 s.")
    metadata = None
    for line in text.splitlines():
        if not line.startswith("#"):
            break
        if line[1:].strip().startswith("{"):
            try:
                metadata = json.loads(line[1:].strip())
            except json.JSONDecodeError as exc:
                raise ValueError("Encabezado JSON de OpenSignals inválido.") from exc
    is_opensignals = text.lstrip().startswith("# OpenSignals") or metadata is not None
    if is_opensignals:
        if not isinstance(metadata, dict) or len(metadata) != 1:
            raise ValueError("Se requiere un TXT de OpenSignals con un único dispositivo y su encabezado.")
        device = next(iter(metadata.values()))
        if not isinstance(device, dict):
            raise ValueError("Metadatos del dispositivo inválidos.")
        fs = float(device.get("sampling rate", 0))
        if not np.isfinite(fs) or not 100 <= fs <= 10000:
            raise ValueError("Frecuencia de OpenSignals no compatible: usa al menos 100 Hz.")
        columns = device.get("column", [])
        channels = device.get("channels", [])
        sensors = device.get("sensor", [])
        if channel == "auto":
            matches = [i for i, sensor in enumerate(sensors) if "ECG" in str(sensor).upper()]
            if len(matches) != 1 or matches[0] >= len(channels):
                raise ValueError("No se identifica un único sensor ECG. Selecciona su canal A1–A6.")
            channel = "A" + str(channels[matches[0]])
        if channel not in {"A1", "A2", "A3", "A4", "A5", "A6"} or channel not in columns:
            raise ValueError(f"El canal {channel} no está en el archivo. Disponibles: {', '.join(map(str, columns))}.")
        frame = pd.read_csv(io.StringIO(text), sep=r"\s+", comment="#", header=None, skip_blank_lines=False)
        if len(frame.columns) != len(columns):
            raise ValueError("Las columnas del TXT no coinciden con su encabezado.")
        raw = pd.to_numeric(frame.iloc[:, columns.index(channel)], errors="raise").to_numpy(dtype=float)
        converted = device.get("convertedValues", 0)
        if converted not in (0, False):
            raise ValueError("Exporta OpenSignals en valores digitales sin convertir; la unidad física no se puede verificar.")
        unit = "ADC"
        source = "OpenSignals · " + channel
    else:
        frame = pd.read_csv(io.StringIO(text), sep=",", header=None, skip_blank_lines=False, low_memory=False)
        if len(frame.columns) != 1:
            raise ValueError("El CSV debe tener una columna de amplitud. Para OpenSignals usa el TXT original.")
        col = frame.iloc[:, 0]
        try:
            float(col.iloc[0])
        except (ValueError, TypeError):
            col = col.iloc[1:]  # encabezado opcional; no descartar la primera muestra numérica
        raw = pd.to_numeric(col, errors="raise").to_numpy(dtype=float)
        unit, source, channel = "u. originales", "CSV", None
    if not np.isfinite(fs) or not 100 <= fs <= 10000:
        raise ValueError("La frecuencia debe estar entre 100 y 10000 Hz.")
    first = int(start * fs)
    last = len(raw) if full_record else first + int(seconds * fs)
    signal = validate_signal(raw[first:last], fs, max_samples=MAX_RECORD_SAMPLES if full_record else 600000)
    meta = {
        "source": source, "unit": unit, "channel": channel,
        "start_s": first / fs, "duration_s": len(signal) / fs,
        "samples": len(signal), "file_duration_s": len(raw) / fs,
    }
    if full_record:
        meta['analysis_scope'] = 'full_record'
    return signal, fs, meta


def inspect_ecg_file(content):
    """Scan bytes without materializing the complete numeric recording.

    Acquisition fields plus internal headers for reusing the existing parser.
    Internal headers must not be displayed or exported by presentation code.
    Duration is based on data-row count; amplitudes are validated on import of
    the selected segment. The original load_ecg_file contract remains default.
    """
    if not content or len(content) > 32 * 1024 * 1024:
        raise ValueError("Selecciona un TXT/CSV no vacio de hasta 32 MB.")
    stream = io.BytesIO(content)
    headers = []
    metadata = None
    first = None
    for offset, line in enumerate(stream):
        try:
            text = line.decode("utf-8-sig" if offset == 0 else "utf-8").rstrip("\r\n")
        except UnicodeDecodeError as exc:
            raise ValueError("El archivo debe ser TXT o CSV UTF-8; no se admite HDF5.") from exc
        if first is None and text.startswith("#"):
            headers.append(text)
            if text[1:].strip().startswith("{"):
                try:
                    metadata = json.loads(text[1:].strip())
                except json.JSONDecodeError as exc:
                    raise ValueError("Encabezado OpenSignals invalido.") from exc
            continue
        first = offset
        first_text = text
        break
    if first is None:
        raise ValueError("El archivo no contiene muestras.")
    opensignals = any(h.startswith("# OpenSignals") for h in headers) or metadata is not None
    csv_header = False
    if not opensignals:
        if "," in first_text or "\t" in first_text or ";" in first_text:
            raise ValueError("El CSV debe tener una unica columna de amplitud.")
        try:
            float(first_text)
        except ValueError:
            csv_header = True
    total_rows = 1 + sum(1 for _ in stream) - int(csv_header)
    if total_rows <= 0:
        raise ValueError("El archivo no contiene muestras.")
    info: dict = dict(format="CSV", fs=None, channels=[], suggested_channel="auto", unit="u. originales",
                total_samples=total_rows, data_line=first + int(csv_header), headers=headers)
    if opensignals:
        if not isinstance(metadata, dict) or len(metadata) != 1:
            raise ValueError("Se requiere OpenSignals con un solo dispositivo y encabezado JSON.")
        device = next(iter(metadata.values()))
        if not isinstance(device, dict):
            raise ValueError("Metadatos del dispositivo invalidos.")
        fs = float(device.get("sampling rate", 0))
        if not np.isfinite(fs) or not 100 <= fs <= 10000:
            raise ValueError("La frecuencia del archivo debe estar entre 100 y 10000 Hz.")
        if device.get("convertedValues", 0) not in (0, False):
            raise ValueError("Exporta valores digitales de OpenSignals sin convertir.")
        channels = [str(c) for c in device.get("column", []) if str(c) in {f"A{i}" for i in range(1, 7)}]
        sensors = device.get("sensor", [])
        matches = [i for i,s in enumerate(sensors) if "ECG" in str(s).upper()]
        connected = device.get("channels", [])
        suggested = "A" + str(connected[matches[0]]) if len(matches)==1 and matches[0]<len(connected) else "auto"
        info.update(format="OpenSignals", fs=fs, channels=channels, suggested_channel=suggested, unit="ADC")
    return info


def _load_selected_rows(content, fs, channel, start, seconds):
    """Materialize only the selected window, reusing the established parser."""
    if not np.isfinite(start) or start < 0 or not np.isfinite(seconds) or not 5 <= seconds <= 60:
        raise ValueError("Selecciona inicio no negativo y duracion entre 5 y 60 s.")
    info = inspect_ecg_file(content)
    fs = info["fs"] or float(fs)
    if not np.isfinite(fs) or not 100 <= fs <= 10000:
        raise ValueError("La frecuencia debe estar entre 100 y 10000 Hz.")
    first, count = int(start*fs), int(seconds*fs)
    if info["total_samples"] - first < 5*fs:
        raise ValueError("El inicio seleccionado debe dejar al menos 5 s de datos disponibles.")
    selected = []
    for index,line in enumerate(io.BytesIO(content)):
        sample_index = index - info["data_line"]
        if sample_index < first:
            continue
        if sample_index >= first + count:
            break
        selected.append(line)
    prefix = ("\n".join(info["headers"]) + "\n").encode() if info["format"]=="OpenSignals" else b""
    signal, fs, meta = load_ecg_file(prefix+b"".join(selected), fs, channel, 0, seconds)
    meta.update(start_s=first/fs, file_duration_s=info["total_samples"]/fs)
    return signal, fs, meta
