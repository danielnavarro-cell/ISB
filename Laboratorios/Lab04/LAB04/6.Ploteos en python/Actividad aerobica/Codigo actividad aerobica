from google.colab import files

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.signal import butter, filtfilt, find_peaks


# 1. SUBIR LOS ARCHIVOS


# Primero subimos los tres archivos correspondientes
# a las derivaciones D1, D2 y D3 durante ACTIVIDAD AERÓBICA.
#
# Archivos esperados:
# ACTIV.AEROBICA D1.txt
# ACTIV.AEROBICA D2.txt
# ACTIV.AEROBICA D3.txt

uploaded = files.upload()

# Guardamos los nombres de los archivos que se subieron.

filenames = list(uploaded.keys())

print("Archivos cargados:")

for f in filenames:
    print("-", f)


# 2. IDENTIFICAR D1, D2 Y D3


# Identificamos automáticamente qué archivo corresponde
# a cada derivación utilizando el nombre del archivo.

file_D1 = [f for f in filenames if 'D1' in f.upper()][0]
file_D2 = [f for f in filenames if 'D2' in f.upper()][0]
file_D3 = [f for f in filenames if 'D3' in f.upper()][0]

print("\nArchivos identificados:")

print("Derivación I  :", file_D1)
print("Derivación II :", file_D2)
print("Derivación III:", file_D3)



# 3. PARÁMETROS DEL BITALINO


# Parámetros del sistema BITalino utilizado
# para adquirir las señales ECG.

fs = 1000       # Frecuencia de muestreo (Hz)
n_bits = 10     # Resolución del ADC
VCC = 3.3       # Voltaje de alimentación (V)
G = 1100        # Ganancia del sensor ECG



# 4. FUNCIÓN PARA PROCESAR EL ECG

# Esta función realiza:
#
# 1. Lectura del archivo OpenSignals
# 2. Extracción del canal ECG A2
# 3. Conversión ADC -> mV
# 4. Corrección de línea base
# 5. Filtrado pasa banda
# 6. Detección de picos R
# 7. Selección de aproximadamente 5 ciclos cardíacos
# 8. Gráfica Tiempo (s) vs ECG (mV)


def procesar_ecg(filename, titulo):

    # Lectura del archivo
  

    # Las líneas que comienzan con "#"
    # corresponden al encabezado generado por OpenSignals
    # y no contienen muestras de ECG.

    data = pd.read_csv(
        filename,
        comment='#',
        sep='\t',
        header=None
    )

    # Eliminamos posibles columnas completamente vacías.

    data = data.dropna(axis=1, how='all')


    
    # Extracción del ECG

    # El ECG se encuentra en la sexta columna
    # correspondiente al canal analógico A2.

    adc = data.iloc[:, 5].to_numpy(dtype=float)


    # Conversión ADC -> mV


    # Primero convertimos los valores digitales del ADC
    # a voltaje.

    voltage = adc * VCC / (2**n_bits)


    # La señal se encuentra centrada aproximadamente
    # alrededor de VCC/2.
    #
    # Restamos este nivel y dividimos entre la ganancia
    # del sensor para obtener la señal ECG.
    #
    # Multiplicamos por 1000 para expresarla en mV.

    ecg_mv = (
        (voltage - VCC / 2)
        / G
        * 1000
    )


    # Corrección de línea base


    # Eliminamos el desplazamiento residual de la señal
    # utilizando la mediana.

    ecg_mv = ecg_mv - np.median(ecg_mv)


    # Vector de tiempo
  

    N = len(ecg_mv)

    t = np.arange(N) / fs

    # Filtro pasa banda


    # Se utiliza un filtro Butterworth de 0.5 a 40 Hz.
    #
    # El límite inferior ayuda a reducir la deriva
    # de la línea base.
    #
    # El límite superior ayuda a disminuir
    # el ruido de alta frecuencia.

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


    # Detección de picos R


    # Establecemos una separación mínima de 0.5 segundos
    # entre los picos detectados.

    min_distance = int(0.5 * fs)


    # La prominencia se calcula automáticamente
    # en función de la desviación estándar de la señal.

    prominence = 0.5 * np.std(ecg_filtered)

    peaks, _ = find_peaks(
        ecg_filtered,
        distance=min_distance,
        prominence=prominence
    )


    # Selección de aproximadamente 5 ciclos cardíacos

    # Para visualizar mejor la morfología del ECG,
    # seleccionamos aproximadamente cinco ciclos
    # ubicados en la región central del registro.
    #
    # Esto permite evitar posibles artefactos
    # presentes al inicio o al final.

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


        # Agregamos un pequeño margen antes
        # y después de los picos seleccionados.

        start_sample = max(
            0,
            peaks[start_peak_index] - int(0.3 * fs)
        )

        end_sample = min(
            N,
            peaks[end_peak_index] + int(0.5 * fs)
        )

    else:

        # Si no se detectan suficientes picos,
        # mostramos los primeros 5 segundos.

        start_sample = 0

        end_sample = min(
            N,
            int(5 * fs)
        )


    # Recorte del segmento


    t_segment = t[start_sample:end_sample]

    ecg_segment = ecg_filtered[start_sample:end_sample]


    # Hacemos que el segmento seleccionado
    # empiece exactamente en t = 0 segundos.

    t_segment = t_segment - t_segment[0]

    # Gráfica

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
        'ECG (mV)',
        fontsize=12
    )


    # Cuadrícula para facilitar la lectura.

    plt.grid(
        True,
        alpha=0.3
    )


    # Línea horizontal correspondiente a 0 mV.

    plt.axhline(
        0,
        linewidth=0.8,
        alpha=0.5
    )

    plt.tight_layout()

    plt.show()

# 5. PROCESAMIENTO DE LAS TRES DERIVACIONES

# ACTIVIDAD AERÓBICA - DERIVACIÓN D1

procesar_ecg(
    file_D1,
    'ECG durante actividad aeróbica - Derivación I'
)


# ACTIVIDAD AERÓBICA - DERIVACIÓN D2

procesar_ecg(
    file_D2,
    'ECG durante actividad aeróbica - Derivación II'
)


# ACTIVIDAD AERÓBICA - DERIVACIÓN D3

procesar_ecg(
    file_D3,
    'ECG durante actividad aeróbica - Derivación III'
)
