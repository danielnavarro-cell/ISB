# Ploteos para las señales de hiperventilación

from google.colab import files

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.signal import butter, filtfilt, find_peaks


# Subimos los tres archivos correspondientes
# a las derivaciones I, II y III en condición de hiperventilación.

uploaded = files.upload()

filenames = list(uploaded.keys())

print("Archivos cargados:")

for f in filenames:
    print("-", f)


# Identificamos automáticamente qué archivo corresponde
# a cada derivación buscando D1, D2 y D3 en el nombre.

file_hiper_D1 = [f for f in filenames if 'D1' in f.upper()][0]
file_hiper_D2 = [f for f in filenames if 'D2' in f.upper()][0]
file_hiper_D3 = [f for f in filenames if 'D3' in f.upper()][0]

print("\nArchivos identificados:")
print("Derivación I :", file_hiper_D1)
print("Derivación II:", file_hiper_D2)
print("Derivación III:", file_hiper_D3)


# Parámetros del sistema BITalino utilizado para adquirir el ECG.

fs = 1000
n_bits = 10
VCC = 3.3
G = 1100


# Esta función realiza el procesamiento completo de cada archivo:
# lectura, conversión a mV, filtrado, detección de picos R,
# selección de un segmento y generación de la gráfica.

def procesar_ecg(filename, titulo):

    # Leemos el archivo exportado desde OpenSignals.
    # Las líneas que empiezan con "#" corresponden al encabezado
    # y se ignoran.

    data = pd.read_csv(
        filename,
        comment='#',
        sep='\t',
        header=None
    )

    # Eliminamos posibles columnas vacías.

    data = data.dropna(axis=1, how='all')


    # La señal ECG se encuentra en la sexta columna,
    # correspondiente al canal A2.

    adc = data.iloc[:, 5].to_numpy(dtype=float)


    # Convertimos los valores digitales del ADC a voltaje.

    voltage = adc * VCC / (2**n_bits)


    # Convertimos el voltaje a amplitud ECG en mV.
    # Primero se elimina el nivel de referencia VCC/2
    # y luego se divide entre la ganancia del sensor.

    ecg_mv = (
        (voltage - VCC / 2)
        / G
        * 1000
    )


    # Eliminamos un posible pequeño offset residual.

    ecg_mv = ecg_mv - np.median(ecg_mv)


    # Creamos el vector de tiempo.
    # Con fs = 1000 Hz, cada muestra equivale a 0.001 s.

    N = len(ecg_mv)
    t = np.arange(N) / fs


    # Aplicamos un filtro pasa banda entre 0.5 y 40 Hz
    # para reducir deriva de línea base y ruido de alta frecuencia.

    nyquist = fs / 2

    low = 0.5 / nyquist
    high = 40 / nyquist

    b, a = butter(
        4,
        [low, high],
        btype='band'
    )

    ecg_filtered = filtfilt(
        b,
        a,
        ecg_mv
    )


    # Detectamos posibles picos R.

    min_distance = int(0.5 * fs)

    prominence = 0.5 * np.std(ecg_filtered)

    peaks, _ = find_peaks(
        ecg_filtered,
        distance=min_distance,
        prominence=prominence
    )


    # Seleccionamos aproximadamente 5 ciclos cardíacos
    # de una zona intermedia del registro.

    num_cycles = 5

    if len(peaks) >= num_cycles + 1:

        center_peak = len(peaks) // 2

        start_peak_index = max(
            0,
            center_peak - num_cycles // 2
        )

        end_peak_index = min(
            len(peaks) - 1,
            start_peak_index + num_cycles
        )


        # Agregamos un pequeño margen antes y después
        # para visualizar mejor las ondas alrededor del QRS.

        start_sample = max(
            0,
            peaks[start_peak_index] - int(0.3 * fs)
        )

        end_sample = min(
            N,
            peaks[end_peak_index] + int(0.5 * fs)
        )

    else:

        # Si no se detectan suficientes picos R,
        # mostramos los primeros 5 segundos.

        start_sample = 0
        end_sample = min(N, int(5 * fs))


    # Recortamos el segmento seleccionado.

    t_segment = t[start_sample:end_sample]
    ecg_segment = ecg_filtered[start_sample:end_sample]


    # Hacemos que el tiempo empiece en 0 s.

    t_segment = t_segment - t_segment[0]


    # Graficamos la señal.

    plt.figure(figsize=(14, 5))

    plt.plot(
        t_segment,
        ecg_segment,
        linewidth=1.2
    )

    plt.title(
        titulo,
        fontsize=15,
        fontweight='bold'
    )

    plt.xlabel(
        'Tiempo (s)',
        fontsize=12
    )

    plt.ylabel(
        'Amplitud (mV)',
        fontsize=12
    )

    plt.grid(
        True,
        alpha=0.3
    )

    plt.axhline(
        0,
        linewidth=0.8,
        alpha=0.5
    )

    plt.tight_layout()
    plt.show()


# Procesamos las tres derivaciones de hiperventilación.

procesar_ecg(
    file_hiper_D1,
    'ECG en hiperventilación - Derivación I'
)

procesar_ecg(
    file_hiper_D2,
    'ECG en hiperventilación - Derivación II'
)

procesar_ecg(
    file_hiper_D3,
    'ECG en hiperventilación - Derivación III'
)
