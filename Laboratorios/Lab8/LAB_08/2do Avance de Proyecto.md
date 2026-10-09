## Link de la presentación de CANVA:
https://www.canva.com/design/DAHXdajj-uA/IqHXFzPek07sOkcguUW_bA/edit

# Avance 2
Estado del arte: detección y clasificación automática de arritmias mediante ECG
1. Introducción
El análisis automatizado de señales electrocardiográficas permite detectar cambios en el ritmo y en la morfología de los latidos que pueden estar relacionados con alteraciones cardíacas. En este contexto, el proyecto propone desarrollar un detector y visualizador de posibles arritmias mediante ECG, procesando la señal para identificar los complejos QRS, calcular intervalos RR y analizar características morfológicas antes de mostrar los resultados mediante una interfaz.
Actualmente, el proyecto considera el uso de la MIT-BIH Arrhythmia Database, que contiene registros ECG anotados y permite comparar las detecciones realizadas por el algoritmo con anotaciones de referencia. Esta misma base de datos ha sido ampliamente utilizada en investigaciones previas sobre clasificación automática de latidos. En la propuesta actual del proyecto también se plantea obtener intervalos RR, frecuencia cardíaca, variabilidad y características morfológicas como información para identificar posibles alteraciones.
Para sustentar esta metodología se han seleccionado tres investigaciones que representan diferentes etapas en el desarrollo de sistemas automáticos de análisis de ECG.
---
2. Gradl et al. (2012): monitoreo ECG y detección de arritmias en tiempo real
El trabajo de Gradl, Kugler, Lohmüller y Eskofier constituye la principal referencia para la arquitectura general del proyecto. Los investigadores desarrollaron una aplicación para dispositivos Android capaz de visualizar ECG continuamente y detectar automáticamente latidos potencialmente anormales. La señal podía provenir de archivos previamente registrados o ser adquirida mediante un sensor Shimmer conectado por Bluetooth.
Metodología
El procesamiento se basó en el algoritmo Pan–Tompkins para detectar los complejos QRS. Después de la detección, el sistema incorporaba etapas adicionales para analizar los latidos y determinar si presentaban características anormales.
La arquitectura general puede resumirse como:
Adquisición ECG → detección QRS → análisis del latido → clasificación → visualización
Los autores evaluaron el algoritmo utilizando dos bases de datos: MIT-BIH Arrhythmia Database y MIT-BIH Supraventricular Arrhythmia Database
Una característica particularmente relevante es que el trabajo no se limitó a generar una clasificación. También desarrolló una interfaz capaz de presentar el ECG, información asociada con la frecuencia cardíaca y los latidos identificados por el sistema. Esto coincide con la orientación del proyecto actual hacia un detector y visualizador, y no únicamente hacia un clasificador.
Resultados
El algoritmo consiguió detectar correctamente más del 99 % de los complejos QRS. Para la detección general de latidos anormales obtuvo una sensibilidad de 89.5 % y una especificidad de 80.6 %. 
--- 
3. de Chazal et al. (2004): morfología ECG e intervalos RR
El trabajo de de Chazal, O'Dwyer y Reilly aborda específicamente la clasificación automática de latidos utilizando información morfológica y temporal del ECG. Este artículo es especialmente relevante para justificar qué características debería extraer nuestro sistema.
Los autores clasificaron los latidos en cinco categorías recomendadas por el estándar AAMI: latido normal, latido ventricular ectópico (VEB), latido supraventricular ectópico (SVEB), fusión y latidos no clasificables
Metodología
Se utilizaron 44 registros sin marcapasos de MIT-BIH Arrhythmia Database.
Los registros fueron separados en dos conjuntos de 22 registros, cada uno con aproximadamente 50 000 latidos. El primer conjunto se utilizó para seleccionar la configuración del clasificador y el segundo para efectuar una evaluación independiente. PubMed
Los autores compararon 12 configuraciones de características, obtenidas a partir de:
- morfología del ECG;
- intervalos entre latidos;
- intervalos RR.
Posteriormente, estas características fueron introducidas en un clasificador estadístico supervisado. 
En términos simplificados:
ECG → segmentación de latidos → RR + morfología → extracción de características → clasificación
Resultados
Para los latidos ventriculares ectópicos (VEB) se obtuvo:
- sensibilidad: 77.7 %;
- predictividad positiva: 81.9 %;
- tasa de falsos positivos: 1.2 %.
Para los latidos supraventriculares ectópicos (SVEB):
- sensibilidad: 75.9 %;
- predictividad positiva: 38.5 %;
- tasa de falsos positivos: 4.7 % 
Los autores reportaron una mejora respecto a resultados publicados previamente para sistemas automáticos de clasificación de latidos.
Aporte al proyecto
Este trabajo constituye una de las principales justificaciones para utilizar intervalos RR y características morfológicas del ECG.
En nuestro caso, después de localizar los picos R se pueden calcular los intervalos:
\[
RR_i=t_{R_{i+1}}-t_{R_i}
\]
y complementar esta información con características relacionadas con la forma del complejo QRS.
Por tanto, el estudio de de Chazal et al. respalda directamente la lógica:
picos R → intervalos RR + morfología → identificación de posibles alteraciones.
También sustenta la selección de MIT-BIH como base inicial de evaluación.
---

4. Kiranyaz et al. (2016): clasificación mediante CNN 1D
El tercer trabajo representa una evolución respecto de los métodos basados en características definidas manualmente.
Kiranyaz, Ince y Gabbouj propusieron un sistema de clasificación de ECG específico para cada paciente basado en redes neuronales convolucionales unidimensionales o 1-D CNN. Su objetivo fue desarrollar un método rápido y preciso que pudiera emplearse para clasificación y monitoreo en tiempo real.
Metodología
En métodos como el de de Chazal existen dos procesos diferenciados:
ECG -> extraer características -> clasificacion
Kiranyaz et al. propusieron integrar ambos procesos dentro de una CNN:
ECG -> 1-D CNN -> Clasificacion
La red aprende automáticamente características relevantes de la señal, evitando que todas tengan que ser definidas manualmente por el investigador.
Además, el método combina una cantidad limitada de datos comunes con información específica del paciente para entrenar un modelo individual. La evaluación fue realizada utilizando nuevamente la MIT-BIH Arrhythmia Database.
Resultados
Los autores informaron que su método presentó un rendimiento superior a gran parte de los métodos comparados en la literatura para la detección de VEB y SVEB sobre MIT-BIH. También destacaron la eficiencia computacional del sistema y la posibilidad de utilizar una CNN previamente entrenada para analizar secuencias ECG prolongadas, como registros Holter, o para aplicaciones de monitoreo en tiempo real.
Aporte al proyecto
No implica que nuestro proyecto deba implementar inmediatamente una CNN.

Para la primera versión del proyecto resulta razonable conservar variables fisiológicamente interpretables como RR, frecuencia cardíaca y características morfológicas. Posteriormente, si se dispone de suficientes datos, podría compararse este enfoque con un modelo basado en CNN.

--- 

Relación entre los tres trabajos y nuestro proyecto 

| Investigación | Principal aporte | Aplicación en nuestro proyecto |
|---|---|---|
| **Gradl et al., 2012** | Detección QRS + detección de anomalías + interfaz | Arquitectura general del detector y visualizador |
| **de Chazal et al., 2004** | Morfología ECG + intervalos RR | Características principales que analizaremos |
| **Kiranyaz et al., 2016** | Clasificación mediante CNN 1D | Posible evolución futura del clasificador |
| **Base compartida** | MIT-BIH Arrhythmia Database | Base inicial para desarrollo y evaluación | 
## Plan de acción (Cronograma de Avances)
--- 
Conclusión: 
Para el alcance actual del proyecto, los trabajos de Gradl et al. y de Chazal et al. son los más directamente relacionados con la implementación: el primero sustenta la arquitectura de detección, monitoreo y visualización, mientras que el segundo justifica utilizar RR y morfología como información para analizar cada latido. El trabajo de Kiranyaz et al. complementa el estado del arte mostrando cómo estas tareas pueden evolucionar hacia técnicas de aprendizaje automático.
Por ello, la propuesta no busca inicialmente realizar un diagnóstico clínico, sino desarrollar una herramienta capaz de procesar el ECG, detectar latidos que se aparten del patrón esperado y presentarlos claramente para su posterior revisión. 

Para este trabajo nos organizaremos para desarrollarlo en las semanas 10 y 15 que son las que aún nos quedan hasta antes de la exposición final. Tomamos en cuenta también que la semana 9 tenemos exámenes parciales y para la semana 16 tenemos finales y la presentación final por lo que no las estamos considerando para el desarrollo. También para equilibrar la carga que tenemos cada uno con otros cursos en la universidad estamos ideando dedicarle unas **2 horas semanales** al proyecto.

| Semana | Fechas | Actividades | Hito |
|---|---|---|---|
| 8 | 5 – 9 oct | Descarga y estructuración de MIT-BIH, EDA inicial, validación del detector de picos R del Avance 1 | ✅ **Avance 2** |
| 9 | 12 – 16 oct | Semana de parciales (sin avance) | — |
| 10 | 19 – 23 oct | Corregir los puntos débiles del detector (registros ruidosos) | **H1:** detector de picos R validado en los 44 registros |
| 11 | 26 – 30 oct | Extracción de características por latido: RR previo, RR siguiente, relación de prematuridad, ancho del QRS | — |
| 12 | 2 – 6 nov | Características morfológicas (correlación con plantilla QRS) + índice simple de calidad de señal | **H2:** tabla de características por latido |
| 13 | 9 – 13 nov | Clasificador normal / posible alteración (umbrales o árbol de decisión). Evaluación con sensibilidad y especificidad | **H3:** clasificador evaluado |
| 14 | 16 – 20 nov | Integración en la interfaz: latidos en verde (normal) y rojo (posible alteración), panel con BPM, RR, SDNN y n.º de latidos sospechosos | **H4:** aplicación integrada |
| 15 | 23 – 27 nov | Pruebas finales, tabla de resultados, README final en GitHub, ensayo de la presentación | **H5:** entrega final lista |
| 16 | 30 nov – 4 dic | Presentación final | 🎯 **Presentación final** |

---

## Avance: estructuración de la base de datos y análisis exploratorio (EDA)

### 1. Descarga y estructuración de la base de datos

Descargamos la **MIT-BIH Arrhythmia Database** de PhysioNet usando la librería `wfdb` de Python (`eda_mitdb.py`), trabajando en Visual Studio Code. Para este avance se usaron **4 registros** de ~30 min a 360 Hz, elegidos por tener ritmos distintos: **100** (ritmo casi normal), **106** y **119** (muchas extrasístoles) y **200** (mixto). La validación con los 44 registros sin marcapasos queda para la semana 10 (hito H1).

Cada registro consta de tres archivos, organizados en la carpeta `data/mitdb/`:

| Archivo | Contenido |
|---|---|
| `.dat` | Señal ECG (2 canales) |
| `.hea` | Encabezado: frecuencia de muestreo, canales y ganancia |
| `.atr` | Anotaciones: tipo de cada latido, marcado por cardiólogos |

Con esto generamos dos tablas:

- **`tabla_registros.csv`**: una fila por registro (derivación, frecuencia de muestreo, duración, número de latidos por clase, si tiene marcapasos).
- **`latidos.csv`**: una fila por latido (registro, posición, símbolo de anotación, clase AAMI, RR previo y RR siguiente en ms).

Los símbolos de anotación se agruparon en las **5 clases del estándar AAMI EC57**, que es la forma habitual de evaluar clasificadores de latidos:

| Clase AAMI | Símbolos MIT-BIH | Significado |
|---|---|---|
| N | N, L, R, e, j | Normal y bloqueos de rama |
| S | A, a, J, S | Ectópico supraventricular |
| V | V, E | Ectópico ventricular |
| F | F | Fusión |
| Q | /, f, Q | Marcapasos / no clasificable |

### 2. EDA: resultados por registro

Se aplicó el detector de picos R del Avance 1 y se comparó con las anotaciones de los especialistas (tolerancia de ±150 ms).

| Registro | Latidos anotados | Latidos detectados | BPM | SDNN (ms) | Sensibilidad picos R | VPP picos R |
|---|---|---|---|---|---|---|
| 100 | 2273 | 2277 | 75.6 | 53.9 | 99.96 % | 99.78 % |
| 106 | 2027 | 2221 | 73.8 | 281.9 | 95.91 % | 87.53 % |
| 119 | 1987 | 2803 | 93.1 | 330.8 | 100.00 % | 70.89 % |
| 200 | 2601 | 2689 | 89.4 | 143 | 73.97 % | 71.55 % |

- **Sensibilidad:** porcentaje de latidos reales que el detector encontró.
- **VPP (valor predictivo positivo):** porcentaje de picos detectados que son latidos reales.

### 3. Detector y clasificador vs. especialistas

**Detección de picos R.** El detector funciona casi perfecto en el registro 100. En el 119 encuentra todos los latidos, pero marca unos 800 de más (2803 detectados para 1987 reales). En el 200 pierde cerca de un 26 % de los latidos.

**Latidos anómalos.** Se comparó el porcentaje de latidos anómalos según los cardiólogos con el que marca nuestra regla de intervalos RR:

| Registro | Anómalos según especialistas | Anómalos según regla RR |
|---|---|---|
| 100 | 1.5 % | 2.4 % |
| 106 | 25.7 % | 60.8 % |
| 119 | 22.3 % | 56.0 % |
| 200 | 33.0 % | 24.6 % |

La regla RR sobreestima los anómalos en los registros 106 y 119, y los subestima en el 200. La comparación es aproximada: los especialistas anotan **latidos** y nuestra regla compara **intervalos RR**.

### 4. Hallazgos

1. **Ritmo regular.** En el registro 100 la sensibilidad es 99.96 % y el VPP 99.78 %, por lo que el pipeline funciona.
2. **Extrasístoles.** En el registro 119 se detectan 2803 picos para 1987 latidos reales (VPP 70.9 %) y en el 200 la sensibilidad baja a 74.0 %.
3. **Regla RR.** En el registro 106 la regla marca 60.8 % de latidos como anómalos frente a 25.7 % anotado. Un umbral global no basta.

**Limitación:** con 4 registros el análisis es exploratorio y está sesgado hacia casos difíciles (3 de 4 tienen muchas arritmias).

### 5. Siguientes pasos

- Umbral adaptativo o algoritmo Pan–Tompkins para el detector de picos R.
- Promedio móvil local en la regla RR, en lugar de un umbral global.
- Características morfológicas del latido.
- Validar con más registros de MIT-BIH (los 44 registros sin marcapasos).

---
---

## Referencias

[1] P. de Chazal, M. O'Dwyer, and R. B. Reilly, "Automatic classification of heartbeats using ECG morphology and heartbeat interval features," IEEE Trans. Biomed. Eng., vol. 51, no. 7, pp. 1196–1206, Jul. 2004, doi: 10.1109/TBME.2004.827359

[2] S. Gradl, P. Kugler, C. Lohmüller, and B. M. Eskofier, "Real-time ECG monitoring and arrhythmia detection using Android-based mobile devices," in Proc. 34th Annu. Int. Conf. IEEE Eng. Med. Biol. Soc. (EMBC), 2012, pp. 2452–2455, doi: 10.1109/EMBC.2012.6346460

[3] S. Kiranyaz, T. Ince, and M. Gabbouj, "Real-time patient-specific ECG classification by 1-D convolutional neural networks," IEEE Trans. Biomed. Eng., vol. 63, no. 3, pp. 664–675, Mar. 2016, doi: 10.1109/TBME.2015.2468589

[4] G. B. Moody and R. G. Mark, "The impact of the MIT-BIH Arrhythmia Database," IEEE Eng. Med. Biol. Mag., vol. 20, no. 3, pp. 45–50, May–Jun. 2001, doi: 10.1109/51.932724

[5] A. L. Goldberger et al., "PhysioBank, PhysioToolkit, and PhysioNet: Components of a new research resource for complex physiologic signals," Circulation, vol. 101, no. 23, p. e215, Jun. 2000, doi: 10.1161/01.CIR.101.23.e215
