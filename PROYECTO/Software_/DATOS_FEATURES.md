# Datos y features (P2)

Todo se reproduce con un solo comando desde esta carpeta:

```
pip install -r requirements.txt
python reproduce.py
```

Descarga los datos a `data/` (unos 145 MB, solo la primera vez), corre los tests,
genera el EDA en `eda_output/` y los CSV en `features_out/`. No hay rutas
absolutas y la semilla es 42.

## Bases

| | MIT-BIH Arrhythmia | Icentia11k |
|---|---|---|
| Registros | 44 (sin marcapasos: 102, 104, 107, 217) | 30 pacientes, segmento `s00` (~70 min c/u), elegidos con semilla 42 |
| Derivación | MLII (elegida por nombre; en el 114 es el canal 1) | la única del parche |
| Frecuencia | 360 Hz | 250 Hz → 360 Hz con `resample_poly(x, 36, 25)` |
| Split | de Chazal: DS1 entrenamiento (22) / DS2 prueba (21) | todo DS2 (prueba externa entre bases) |

**Ojo con el split de de Chazal:** los registros 201 (DS1) y 202 (DS2) son del mismo
paciente. `get_split("mitbih")` saca 202 de DS2 para que no haya fuga.
`get_split("mitbih", strict=False)` da el split original, para comparar con artículos.

## Clases AAMI

| Clase | Símbolos |
|---|---|
| N | N, L, R, e, j |
| S | A, a, J, S |
| V | V, E |
| F | F |
| Q | /, f, Q |

Las anotaciones que no son latidos (`+ ~ | x ! [ ] " p t u ...`) se ignoran.

Icentia11k solo tiene N, S, V y Q. Su `Q` significa "latido sin definir" (ruido o
tramos sin revisar) y **se excluye**. No tiene F, y S y V son escasas (0.4 % y
0.7 %) y están concentradas en pocos pacientes. MIT-BIH Q tiene solo 15 latidos.
Detalle en `eda_output/eda_clases.md`.

## CSV de features

`features_out/features_mitbih.csv` y `features_out/features_icentia.csv` (picos de
referencia, v1). Con un detector: `features_<db>_<detector>.csv` y
`matching_<db>_<detector>.csv`.

```
python build_features.py --db {mitbih,icentia} --detector {gt,pantompkins,xqrs}
```

| Columna | Qué es |
|---|---|
| `record`, `split`, `beat_idx`, `r_sample`, `clase_aami` | identificación; `r_sample` a 360 Hz |
| `rr_prev`, `rr_next` | RR con el latido anterior / siguiente (s) |
| `rr_local` | media de 10 RR centrados en el latido (s) |
| `rr_prev_ratio`, `rr_next_ratio` | RR / `rr_local` |
| `r_amp` | señal filtrada en R (mV) |
| `qrs_width` | ancho de QRS (s): pendiente suavizada 10 ms, umbral 15 % del máximo, se recorta a 40–200 ms. Sirve para comparar latidos, no como medida clínica (sale algo más corto) |
| `borde` | 1 = primer o último latido del registro (el RR que falta se copia del otro) |
| `rr_corto` | 1 = algún RR < 200 ms (posible pico duplicado) |
| `w_000`…`w_099` | señal filtrada de R−0.25 s a R+0.40 s, remuestreada a 100 puntos |

Para entrenar, agrupen por `record` (equivale a paciente) y usen la columna
`split`; nunca dividan por latido.

## Con los picos del detector (P1)

`peak_detection.py` debe exponer `detect_r_peaks_pantompkins(signal, fs)` y
`detect_r_peaks_xqrs(signal, fs)`. Reciben la señal sin filtrar a 360 Hz y
devuelven los índices de los picos (o una tupla cuyo primer elemento son los picos).

- Las features se calculan con **todos** los picos detectados, como en uso real.
- Cada pico se empareja con la anotación más cercana a **±50 ms**, uno a uno.
- **Falsos positivos:** se descartan del CSV y se cuentan en `matching_*.csv`
  (por eso puede haber huecos en `beat_idx`).
- **Latidos no detectados:** no tienen fila; se cuentan en `matching_*.csv`.
- Picos sobre latidos excluidos (Q de Icentia) se descartan sin contar como FP.

## Archivos

- `data_loader.py`: `list_records`, `load_record`, `get_split`, tabla AAMI.
- `features.py`: `extract_beat_features(signal, r_peaks, fs)`.
- `validation.py`: `match_indices` (nuevo) y `match_beats`.
- `eda_dataset.py`, `build_features.py`, `reproduce.py`.
- `tests/`: `python -m pytest -q tests`.
