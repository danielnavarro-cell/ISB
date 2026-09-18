# Procesamiento de señales ECG con BITalino y Python

Este código permite cargar, procesar y visualizar señales ECG registradas con BITalino y exportadas desde OpenSignals. El procedimiento se aplica de la misma forma a las derivaciones I, II y III.
---

## Librerías utilizadas

```python
from google.colab import files

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.signal import butter, filtfilt, find_peaks
```

En esta primera parte se importan las librerías necesarias para trabajar con los datos.

- `google.colab.files` permite cargar archivos directamente desde la computadora hacia Google Colab.
- `NumPy` se utiliza para realizar operaciones numéricas y trabajar con arreglos.
- `Pandas` permite leer y organizar los archivos `.txt` exportados desde OpenSignals.
- `Matplotlib` se utiliza para generar las gráficas de las señales ECG.
- `SciPy.signal` proporciona las funciones necesarias para filtrar la señal y detectar los picos R.

---

## Carga de los archivos

```python
uploaded = files.upload()

filenames = list(uploaded.keys())

print("Archivos cargados:")

for f in filenames:
    print("-", f)
```

Esta parte permite seleccionar los archivos desde la computadora.

La función:

```python
files.upload()
```

abre una ventana en Google Colab para subir los registros correspondientes a las tres derivaciones.

Posteriormente:

```python
filenames = list(uploaded.keys())
```

extrae los nombres de los archivos cargados y los guarda dentro de una lista.

Finalmente, el ciclo:

```python
for f in filenames:
    print("-", f)
```

muestra los archivos cargados para verificar que se hayan seleccionado correctamente.

---

## Identificación automática de las derivaciones

```python
file_D1 = [f for f in filenames if 'D1' in f.upper()][0]
file_D2 = [f for f in filenames if 'D2' in f.upper()][0]
file_D3 = [f for f in filenames if 'D3' in f.upper()][0]
```

Esta parte del codigo trata de identificar automaticamente el que archivo corresponde a cada derivación. 

El programa busca dentro del nombre del archivo las expresiones:

```text
D1
D2
D3
```

Por ejemplo:

```text
BASALD1.txt
BASALD2.txt
BASALD3.txt
```

serán relacionados automáticamente con las derivaciones I, II y III.

El uso de:

```python
f.upper()
```

convierte el nombre del archivo a mayúsculas, evitando problemas por diferencias entre mayúsculas y minúsculas.

Luego se comprueba la asignación mediante:

```python
print("\nArchivos identificados:")
print("Derivación I :", file_D1)
print("Derivación II:", file_D2)
print("Derivación III:", file_D3)
```

---

##  Parámetros de adquisición

```python
fs = 1000
n_bits = 10
VCC = 3.3
G = 1100
```

Estos parámetros corresponden al sistema utilizado para registrar la señal ECG.

### Frecuencia de muestreo

```python
fs = 1000
```

La frecuencia de muestreo fue de:

$$
f_s = 1000\ Hz
$$

Esto significa que se obtienen 1000 muestras de la señal por segundo.

El intervalo temporal entre dos muestras consecutivas es:

$$
T_s = \frac{1}{f_s}
$$

$$
T_s = \frac{1}{1000}
$$

$$
T_s = 0.001\ s
$$

Por lo tanto, cada muestra está separada aproximadamente 1 ms.

### Resolución del ADC

```python
n_bits = 10
```

El conversor analógico-digital trabaja con 10 bits, por lo que dispone de:

$$
2^{10}=1024
$$

niveles digitales posibles.

### Voltaje de referencia

```python
VCC = 3.3
```

Se utiliza un voltaje de referencia de 3.3 V.

### Ganancia

```python
G = 1100
```

La señal ECG es amplificada por el sistema de adquisición antes de ser digitalizada. La ganancia se utiliza posteriormente para recuperar aproximadamente la amplitud original de la señal.

---

## Función general de procesamiento

```python
def procesar_ecg(filename, titulo):
```

Se crea una función llamada:

```python
procesar_ecg()
```

Esta función contiene todo el procesamiento de una señal ECG.

Recibe dos parámetros:

```python
filename
titulo
```

`filename`   archivo que será procesado.

`titulo`  nombre que aparecerá en la gráfica.

La principal ventaja de utilizar una función es que el mismo procesamiento puede aplicarse a D1, D2 y D3 sin repetir todo el código.

---

##  Lectura del archivo de OpenSignals

```python
data = pd.read_csv(
    filename,
    comment='#',
    sep='\t',
    header=None
)
```
El archivo `.txt` se lee utilizando Pandas. 
```

indica que los datos se encuentran separados mediante tabulaciones.

Finalmente:

```python
header=None
```

indica que no existe una fila convencional con los nombres de las columnas.

---

##  Limpieza inicial de los datos

```python
data = data.dropna(axis=1, how='all')
```

Esta instrucción elimina columnas que se encuentren completamente vacías.
Esto evita posibles problemas si el archivo exportado contiene columnas adicionales sin información.

---

##  Extracción del canal ECG

```python
adc = data.iloc[:, 5].to_numpy(dtype=float)
```

La señal ECG se encuentra en la sexta columna del archivo, correspondiente al canal A2.

La instrucción:

```python
data.iloc[:, 5]
```

selecciona:

```text
Todas las filas
Columna número 5
```

Como Python empieza a contar desde cero, la columna número 5 corresponde realmente a la sexta columna.

Luego:

```python
.to_numpy()
```

convierte los datos en un arreglo NumPy para facilitar las operaciones matemáticas.

---

##  Conversión de ADC a voltaje

```python
voltage = adc * VCC / (2**n_bits)
```

Los valores almacenados inicialmente corresponden a valores digitales del ADC.
Para convertirlos a voltaje se utiliza:

$$
V =
\frac{ADC}{2^{n}}
V_{CC}
$$

Con:

$$
n=10
$$

y:

$$
V_{CC}=3.3\ V
$$

se obtiene:

$$
V =
\frac{ADC}{1024}
(3.3)
$$

De esta forma se obtiene una señal expresada en voltios.

---

## Conversión de voltaje a ECG en milivoltios

```python
ecg_mv = (
    (voltage - VCC / 2)
    / G
    * 1000
)
```

La señal adquirida se encuentra desplazada alrededor de un nivel de referencia cercano a:

$$
\frac{VCC}{2}
$$

Por esta razón, primero se resta:

$$
\frac{3.3}{2}
=
1.65\ V
$$

Luego se divide entre la ganancia del sistema:

$$
G=1100
$$

para recuperar aproximadamente la amplitud original del ECG.

Finalmente se multiplica por 1000 para expresar la señal en milivoltios:

$$
1\ V = 1000\ mV
$$

---

##  Corrección del offset

```python
ecg_mv = ecg_mv - np.median(ecg_mv)
```

Aunque previamente se elimina el nivel de referencia, todavía puede existir un pequeño desplazamiento de la línea base.

Por esta razón se calcula la mediana de la señal y se resta a todas las muestras.

El objetivo es centrar la señal aproximadamente alrededor de:

$$
0\ mV
$$

---

##  Construcción del vector de tiempo

```python
N = len(ecg_mv)

t = np.arange(N) / fs
```

Primero se obtiene el número total de muestras mediante:

```python
N = len(ecg_mv)
```

Luego se genera un vector:
y se divide entre la frecuencia de muestreo.

Como:

$$
f_s = 1000\ Hz
$$

el vector de tiempo tendrá valores como:

```text
0
0.001
0.002
0.003
...
```

Esto permite representar la señal en función del tiempo en segundos.

---

## Diseño del filtro pasa banda
Usamos un pasa banda porque queremos eliminar tanto las variaciones muy lentas de la línea base como el ruido de alta frecuencia, conservando el rango principal donde se encuentra la información del ECG

```python
nyquist = fs / 2
```

Como:

$$
f_s=1000\ Hz
$$

entonces:

$$
f_N = \frac{1000}{2}
$$

$$
f_N=500\ Hz
$$

Después se normalizan las frecuencias de corte:

```python
low = 0.5 / nyquist
high = 40 / nyquist
```

Las frecuencias seleccionadas son:

$$
0.5\ Hz
$$

y:

$$
40\ Hz
$$

Luego se diseña el filtro:

```python
b, a = butter(
    4,
    [low, high],
    btype='band'
)
```

Se utiliza un filtro Butterworth pasa banda de orden 4.

El objetivo es conservar principalmente las componentes de la señal comprendidas entre:

$$
0.5-40\ Hz
$$

reduciendo componentes de muy baja frecuencia asociadas con la deriva de línea base y componentes de alta frecuencia relacionadas con ruido.

---

## Aplicación del filtro
Usamos un filtro pasa banda porque queremos conservar el rango de frecuencias donde está la mayor parte de la información útil del ECG y atenuar componentes no deseadas por debajo y por encima de ese rango.


```python
ecg_filtered = filtfilt(
    b,
    a,
    ecg_mv
)
```

La función:

```python
filtfilt()
```

aplica el filtro hacia adelante y hacia atrás.

Esto permite reducir el desfase producido por el filtrado.

En una señal ECG esto es importante porque interesa conservar lo mejor posible la posición temporal de los complejos QRS.

La señal resultante se almacena en:

```python
ecg_filtered
```

---

##  Detección de picos R

Primero se establece una distancia mínima entre picos:

```python
min_distance = int(0.5 * fs)
```

Como:

$$
f_s=1000
$$

se obtiene:

$$
0.5(1000)=500
$$

muestras.

Esto equivale a:

$$
0.5\ s
$$

El objetivo es evitar que diferentes partes de un mismo complejo QRS sean interpretadas como latidos distintos.

Luego se calcula un criterio de prominencia:

```python
prominence = 0.5 * np.std(ecg_filtered)
```

La desviación estándar representa la variabilidad de la amplitud de la señal.

Por tanto, este criterio permite utilizar un umbral que depende de la señal y no un valor completamente fijo.

Finalmente se detectan los picos:

```python
peaks, _ = find_peaks(
    ecg_filtered,
    distance=min_distance,
    prominence=prominence
)
```

La variable:

```python
peaks
```

contiene las posiciones donde fueron detectados los posibles picos R.

---

##  Selección de ciclos cardíacos

```python
num_cycles = 5
```

Se decide mostrar aproximadamente cinco ciclos cardíacos.

Esto permite visualizar mejor la morfología del ECG sin mostrar todo el registro completo.

Primero se comprueba si existen suficientes picos:

```python
if len(peaks) >= num_cycles + 1:
```

Si existen suficientes picos, se selecciona una región aproximadamente central de la señal:

```python
center_peak = len(peaks) // 2
```

Luego se calculan el pico inicial y el pico final:

```python
start_peak_index = max(
    0,
    center_peak - num_cycles // 2
)

end_peak_index = min(
    len(peaks) - 1,
    start_peak_index + num_cycles
)
```

Esto permite seleccionar varios latidos alrededor de la parte central del registro.

---

##  Margen antes y después de los ciclos

Para visualizar mejor la morfología del ECG se agrega un pequeño margen alrededor de los picos seleccionados.

Antes del primer pico:

```python
start_sample = max(
    0,
    peaks[start_peak_index] - int(0.3 * fs)
)
```

se agregan aproximadamente:

$$
0.3\ s
$$

Esto permite visualizar la región anterior al QRS, donde puede aparecer la onda P.

Después del último pico:

```python
end_sample = min(
    N,
    peaks[end_peak_index] + int(0.5 * fs)
)
```

se agregan aproximadamente:

$$
0.5\ s
$$

Esto permite visualizar la zona posterior al QRS, incluyendo la onda T.

---


## Recorte del segmento

```python
t_segment = t[start_sample:end_sample]

ecg_segment = ecg_filtered[start_sample:end_sample]
```

Una vez definidos los límites, se extrae únicamente el fragmento que será mostrado.

`t_segment` contiene el tiempo.

`ecg_segment` contiene la señal ECG correspondiente exactamente al mismo intervalo.

---

## Reinicio del tiempo

```python
t_segment = t_segment - t_segment[0]
```

Aunque el segmento seleccionado puede encontrarse, por ejemplo, alrededor del segundo 30 del registro original, para la gráfica se hace que empiece nuevamente en:

$$
t=0
$$

---

## Generación de la gráfica

Primero se crea la figura:

```python
plt.figure(figsize=(14, 5))
```

Después se grafica:

```python
plt.plot(
    t_segment,
    ecg_segment,
    linewidth=1.2
)
```

El eje horizontal representa:

$$
\text{Tiempo (s)}
$$

mientras que el eje vertical representa:

$$
\text{Amplitud (mV)}
$$

---

##  Título y etiquetas

```python
plt.title(
    titulo,
    fontsize=15,
    fontweight='bold'
)
```

coloca el título correspondiente a cada derivación.

Luego:

```python
plt.xlabel(
    'Tiempo (s)',
    fontsize=12
)

plt.ylabel(
    'Amplitud (mV)',
    fontsize=12
)
```

se etiquetan los ejes.

---

## Elementos visuales de la gráfica
Esta parte es útil para facilitar la lectura de tiempo y amplitud, ya que se agregan como cuadriculas. 

```python
plt.grid(
    True,
    alpha=0.3
)
```

Luego:

```python
plt.axhline(
    0,
    linewidth=0.8,
    alpha=0.5
)
```

dibuja una línea horizontal en:

$$
0\ mV
$$

Esto permite distinguir mejor las deflexiones positivas y negativas del ECG.

---

## Visualización final

```python
plt.tight_layout()
plt.show()
```

`plt.tight_layout()` ajusta automáticamente los márgenes de la figura.

`plt.show()` muestra finalmente la gráfica.

---

## Procesamiento de las tres derivaciones

Una vez definida la función, se utiliza para procesar cada derivación:
Esta parte es la que se cambia para analizar las gráficas tanto reposo, hipoventilación e hiperventilación, ya que la lógica y el filtrado será el mismo para poder obtener las gráficas presentadas. 

```python
procesar_ecg(
    file_D1,
    'ECG en reposo - Derivación I'
)

procesar_ecg(
    file_D2,
    'ECG en reposo - Derivación II'
)

procesar_ecg(
    file_D3,
    'ECG en reposo - Derivación III'
)
```

De esta forma, las tres derivaciones utilizan exactamente el mismo procedimiento de procesamiento.

Esto permite realizar una comparación más consistente entre D1, D2 y D3.

---
En resumen, el código toma los datos originales registrados por BITalino, los convierte a una señal ECG interpretable, reduce componentes de ruido mediante filtrado, identifica los complejos cardíacos principales y selecciona un segmento representativo para su visualización.
