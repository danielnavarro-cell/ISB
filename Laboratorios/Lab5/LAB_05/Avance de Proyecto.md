
# Planteamiento del problema

## Arritmias cardíacas

Las arritmias cardíacas son alteraciones en el ritmo normal del corazón que se producen debido a cambios en la generación o conducción de los impulsos eléctricos cardíacos. Estas alteraciones pueden ocasionar que el corazón lata demasiado rápido, demasiado lento o de manera irregular.

Dentro de las arritmias, una de las más frecuentes es la fibrilación auricular (FA). Se estima que aproximadamente 50 millones de personas vivían con fibrilación auricular a nivel mundial en el año 2020 [1]. Además, algunas arritmias pueden presentarse sin síntomas evidentes. En el caso de la fibrilación auricular, se ha reportado que entre el 10 % y 40 % de los pacientes pueden ser asintomáticos, dependiendo de la población estudiada [1].

Esto representa un problema debido a que una persona puede presentar una alteración en su ritmo cardíaco sin identificarla oportunamente.

## Importancia del problema

Las arritmias pueden estar relacionadas con diferentes complicaciones cardiovasculares. En particular, la fibrilación auricular se encuentra asociada con un mayor riesgo de accidente cerebrovascular (ACV) y otras complicaciones cardiovasculares [1].

Según la guía ACC/AHA/ACCP/HRS, la fibrilación auricular se asocia con aproximadamente 2.4 veces mayor riesgo de accidente cerebrovascular [1]. Por este motivo, el análisis de la actividad eléctrica del corazón resulta importante para identificar posibles alteraciones en el ritmo cardíaco y orientar una posterior evaluación clínica.

Algunos datos relevantes sobre esta problemática son:

| Indicador | Dato |
|---|---|
| Personas con fibrilación auricular | Aproximadamente 50 millones a nivel mundial en 2020 [1] |
| Pacientes asintomáticos | Entre 10 % y 40 %, dependiendo de la población estudiada [1] |
| Riesgo asociado de ACV | Aproximadamente 2.4 veces mayor en personas con fibrilación auricular [1] |

## Consecuencias y necesidad de una solución

Las alteraciones del ritmo cardíaco pueden afectar tanto al paciente como a su entorno. A nivel individual, pueden presentarse síntomas como palpitaciones, fatiga, mareos o dificultad para respirar. Sin embargo, algunas personas pueden no presentar síntomas, lo que puede dificultar la identificación de estas alteraciones.

A nivel familiar, la aparición de síntomas o complicaciones puede generar preocupación y requerir tiempo y recursos para consultas, evaluaciones y seguimiento médico. Asimismo, las enfermedades cardiovasculares representan una carga importante para los sistemas de salud [2].

Por esta razón, resulta de interés contar con herramientas que permitan analizar la actividad eléctrica cardíaca e identificar posibles alteraciones en el ritmo. El electrocardiograma (ECG) permite registrar la actividad eléctrica del corazón y obtener información sobre su comportamiento.

A partir de esta problemática, se plantea el uso del procesamiento digital de señales ECG como una alternativa para analizar la señal, extraer características relevantes e identificar posibles alteraciones del ritmo cardíaco que puedan requerir una evaluación posterior.

# Propuesta de solución

## Detector y visualizador de posibles alteraciones del ritmo cardíaco mediante ECG

A partir de la problemática identificada, proponemos desarrollar una herramienta capaz de analizar señales de electrocardiograma (ECG) con el objetivo de identificar latidos o segmentos que presenten características diferentes al comportamiento esperado.

La propuesta integra dos funciones principales:

1. **Detección de posibles alteraciones:** el sistema analizará información relevante presente en el ECG para reconocer cambios en el ritmo y en la morfología de los latidos.

2. **Visualización de resultados:** los resultados obtenidos serán presentados mediante una interfaz que permita observar la señal ECG y localizar los latidos o segmentos identificados como potencialmente anormales.

La herramienta se plantea como un sistema de apoyo para el análisis de señales ECG y no como un reemplazo del diagnóstico médico.

---

## Funcionamiento general de la propuesta

El funcionamiento del sistema puede resumirse en cuatro etapas principales:

**ECG de entrada → Análisis del latido → Identificación de posibles alteraciones → Visualización de resultados**

### 1. Entrada de la señal ECG

El sistema recibirá una señal electrocardiográfica que podrá provenir inicialmente de registros almacenados, como los disponibles en bases de datos de PhysioNet.

Esta señal contiene información sobre la actividad eléctrica del corazón a lo largo del tiempo.

### 2. Análisis de los latidos

A partir de la señal ECG se analizarán características que permitan describir el comportamiento de cada latido.

Estas características pueden dividirse principalmente en dos grupos:

| Tipo de información | Características de interés |
|---|---|
| **Ritmo cardíaco** | Intervalos R-R, frecuencia cardíaca y regularidad o variabilidad entre latidos |
| **Morfología** | Forma y duración del complejo QRS, información de las ondas P y T y cambios en la forma del latido |

La combinación de información temporal y morfológica permite representar de manera cuantitativa el comportamiento de la señal ECG.

### 3. Identificación de posibles alteraciones

Una vez obtenidas las características de cada latido, estas podrán compararse con patrones esperados o con criterios definidos por el método de clasificación utilizado.

Si un latido presenta diferencias relevantes en su ritmo o morfología, el sistema podrá señalarlo como una **posible alteración** para su posterior revisión.

Por ejemplo, cambios importantes en los intervalos R-R pueden indicar irregularidad en el ritmo, mientras que modificaciones en la duración o forma del complejo QRS pueden indicar diferencias en la morfología del latido.

### 4. Visualización

Finalmente, la herramienta mostrará los resultados obtenidos de forma gráfica.

El objetivo es que el usuario pueda visualizar:

- La señal ECG analizada.
- Los latidos detectados.
- Información relacionada con el ritmo cardíaco.
- Las características obtenidas durante el análisis.
- Los latidos o segmentos identificados como potencialmente anormales.

De esta manera, el sistema integrará en una sola herramienta el análisis de la señal y la presentación de los resultados.

---

## ¿Cómo ayuda el ECG a identificar alteraciones?

El ECG registra la actividad eléctrica del corazón y permite observar diferentes componentes asociados a cada ciclo cardíaco, entre ellos las ondas P, el complejo QRS y la onda T.

Además, la identificación de los picos R permite calcular el **intervalo R-R**, correspondiente al tiempo transcurrido entre dos picos R consecutivos.

A partir de estos elementos es posible obtener información relacionada con:

- La frecuencia cardíaca.
- La regularidad del ritmo.
- La variabilidad entre latidos.
- La duración del complejo QRS.
- La forma de los distintos componentes del ECG.

Por lo tanto, el análisis conjunto del **ritmo** y la **morfología** permite caracterizar cada latido y detectar aquellos que presentan un comportamiento diferente al esperado.

> **Importante:** la identificación realizada por el sistema corresponde a posibles alteraciones de la señal ECG. La interpretación clínica y el diagnóstico definitivo deben ser realizados por un profesional de la salud.

---

## Objetivo de la solución

Desarrollar un sistema que integre el análisis y la visualización de señales ECG para facilitar la identificación de latidos o segmentos con posibles alteraciones del ritmo cardíaco.

La propuesta busca facilitar una revisión más rápida y objetiva de la señal, permitiendo resaltar regiones que podrían requerir una evaluación posterior.


# Procesamiento de la señal ECG

Para el procesamiento lo que hacemos primero es una etapa previa a la identificación de las posibles alteraciones, esto más que nada porque la señal adquirida puede contener componentes no deseados los cuales interfieren en la correcta detección de latidos. Seguimos un flujo de: Preprocesamiento - Detección de picos R - Extracción de características temporales. 

Durante el preprocesamiento implementamos 2 filtros: primero un filtro notch en 60Hz para poder atenuar la interferencia a la red eléctrica y luego utilizamos un filtro pasabanda Butterworth con frecuencias de corte entre 0.5 y 40 Hz para reducir los componentes de baja frecuencia que estén asociados a la deriva de línea base y los componentes de alta frecuencia no deseados también. Ambos filtros los aplicamos mediante filtrado de fase cero, para evitar el tener que introducir un desplazamiento temporal de los componentes de la señal [4][5].

Ya una vez que hayamos terminado lo del prefiltrado recién realizamos la detección de los picos R, que los vamos a utilizar como puntos de referencia para determinar la ocurrencia de cada latido. La implementación inicial utiliza un detector de picos con un umbral dependiente de las características estadísticas de la señal, definido a partir de su media y desviación estándar. También se establece una distancia mínima entre picos considerando un rango esperado de frecuencia cardiaca con la finalidad de disminuir detecciones múltiples asociadas a un mismo complejo. Y es a partir de las posiciones de los picos R que realizamos el cálculo de los intervalos RR que serán definidos como diferencia temporal entre picos R consecutivos, consideramos también una frecuencia de muestreo como fs y para convertirlo a milisegundos usamos:

<img width="494" height="116" alt="image" src="https://github.com/user-attachments/assets/5d539efc-45f4-4957-be14-b8a7636dbc2a" />

A partir de estos intervalos RR, la implementación calcula la frecuencia cardiaca promedio (BPM) y una medida de variabilidad basada en la desviación estándar de los intervalos RR (SDNN), además del número de latidos detectados, constituyen nuestra información que va a ser utilizada en la versión inicial del sistema para evaluar la regularidad de los latidos.





## Analísis de articulo referencial 
### Resumen 
Se desarrollo una aplicación para Android que visualizaba continuamente el ECG, detectaba complejos QRS e identificaba latidos que podían considerarse anormales. La aplicación recibía datos de un sensor Shimmer por Bluetooth o reproducía registros almacenados.[6] 

#### Arquitectura y metodología del sistema
1. Adquisición de la señal ECG
Los investigadores utilizaron un sensor Shimmer para adquirir el ECG en derivación II y transmitirlo mediante Bluetooth a una aplicación Android. El sistema también podía procesar registros previamente almacenados, simulando su adquisición en tiempo real. 

2. Filtrado digital y detección QRS

Se implementó una adaptación del algoritmo de Pan-Tompkins. Primero, la señal pasa por un filtro pasa banda formado por filtros pasa bajas y pasa altas en cascada, cuyo objetivo es reducir el ruido antes de detectar los complejos QRS.
Posteriormente, se aplican una derivada de cinco puntos, una elevación al cuadrado y una integración mediante una ventana móvil. La derivada resalta los cambios rápidos del QRS; la elevación al cuadrado acentúa las pendientes pronunciadas, y la integración junta esa información para localizar cada complejo.
Para detectar los picos R, se calcula un umbral utilizando una media móvil de 150 ms, seguido de un detector de máximos de tres puntos y una verificación de los picos candidatos.[6]

3. Creación de plantillas y extracción de características

Una vez detectados los picos R, el sistema construye automáticamente dos plantillas QRS a partir de los primeros seis latidos válidos. Para ello, analiza ventanas de 400 ms centradas en cada pico R y busca latidos con áreas similares y una correlación de Pearson superior a 0.95. Las plantillas se actualizan posteriormente con los latidos clasificados como normales.
Para analizar cada nuevo latido, extrae cuatro características: diferencia de área respecto a la plantilla, correlación máxima, duración del QRS e intervalo RR. [6]

4. Detección de anomalías y visualización

Finalmente, las cuatro características se introducen en un árbol de decisiones que utiliza umbrales para identificar latidos normales o anormales y alteraciones del ritmo.[6]

#### Interfaz 
La interfaz desarrollada en el artículo presenta la señal ECG original, los complejos QRS extraídos y las variaciones de la frecuencia cardíaca. Además, muestra la frecuencia actual, el intervalo RR en milisegundos y la cantidad de QRS reconocidos. 
                                            ![Interfaz del sistema](Interfaz_paper.png)


Tambien los  autores incorporaron indicadores de color
Verde : Latido identificado como normal.
Rojo : Latido identificado como anormal.

### Resultados 
La aplicación muestra continuamente el ECG, los complejos QRS y las variaciones de la frecuencia cardíaca. También presenta los intervalos RR y marca los latidos normales en verde y los anormales en rojo
evaluaron su aplicación utilizando las bases de datos MIT-BIH Arrhythmia y MIT-BIH Supraventricular Arrhythmia. En total, procesaron 256 014 anotaciones de latidos, correspondientes a 111 registros seleccionados. Las pruebas se realizaron en tres modelos de teléfonos Android y produjeron los mismos resultados en todos ellos. 
El algoritmo logró detectar correctamente el 99.59 % de los complejos QRS en MIT-BIH Arrhythmia y el 99.58 % en MIT-BIH Supraventricular Arrhythmia. En conjunto, solo el 0.42 % de las anotaciones no fueron reconocidas. Estos resultados muestran que el sistema consiguió localizar los latidos con una alta tasa de detección. 
Respecto a la identificación de latidos anormales, se obtuvo una sensibilidad global del 89.5 % y una especificidad del 80.6 %. Esto significa que el sistema identificó aproximadamente nueve de cada diez latidos anormales, aunque también presentó falsas alarmas al clasificar algunos latidos normales como anormales. 
Finalmente, se comprobó que la aplicación podía procesar y visualizar el ECG en tiempo real utilizando un sensor Shimmer conectado mediante Bluetooth. Sin embargo, esta prueba en vivo se realizó únicamente con una persona sana, por lo que no permitió comprobar su rendimiento clínico en pacientes con arritmias.

### Oportunidades de mejora 
Finalmente, identificamos oportunidades de mejora en el artículo a partir de las limitaciones encontradas
El algoritmo depende de la calidad de los primeros latidos, porque los utiliza para construir sus plantillas. Por eso proponemos evaluar la calidad de la señal antes de generarlas.

El sistema todavía presenta falsas alarmas. Nuestra idea es que la interfaz permita visualizar los latidos sospechosos para facilitar su revisión.
El algoritmo tiene una carga computacional elevada debido al cálculo de correlaciones. Por ello, podríamos comparar un método sencillo basado en intervalos RR con otro que también considere la morfología del QRS.
Finalmente, como las pruebas en vivo fueron limitadas y utilizaron el sensor Shimmer, proponemos comenzar con registros anotados de PhysioNet 

### Conclusiones 
Gracias al algoritmo de Pan-Tompkins, la comparación con plantillas QRS y la extracción de características temporales y morfológicas, los investigadores consiguieron integrar la adquisición, el procesamiento y la visualización de las señales en una sola aplicación.
Una de las principales limitaciones fue la dependencia de las plantillas iniciales: cuando los primeros latidos contenían ruido o alteraciones, podían generarse plantillas inadecuadas y aumentar los errores de clasificación. Asimismo, el cálculo de correlación generó una carga computacional considerable.
A partir de sus limitaciones, planteamos incorporar una evaluación inicial de la calidad de la señal y permitir que el usuario visualice los latidos señalados como sospechosos. Además, proponemos comenzar la validación con registros anotados de PhysioNet antes de considerar la adquisición en tiempo real

## Dataset: MIT-BIH Arrhythmia Database

### PhysioNet – MIT-BIH Arrhythmia Database

- 48 registros de ECG de pacientes.
- Cada registro contiene aproximadamente 30 minutos de señal ECG.
- Frecuencia de muestreo: 360 Hz.
- Los latidos están anotados por especialistas.
- Permite comparar las detecciones del sistema con anotaciones de referencia.

> **Ejemplo utilizado:** Record 100, 200, 250 y 102
>
> **Entrada → ECG → Procesamiento → Clasificación**

🔗 [MIT-BIH Arrhythmia Database – PhysioNet](https://physionet.org/content/mitdb/1.0.0/)

## Interfaz de la aplicación

![Interfaz del sistema](image.png)
--- 
## Referencia IEEE
## Referencias

[1] J. A. Joglar et al., “2023 ACC/AHA/ACCP/HRS Guideline for the Diagnosis and Management of Atrial Fibrillation,” *Circulation*, vol. 149, no. 1, pp. e1–e156, Jan. 2024, doi: 10.1161/CIR.0000000000001193.  
Available: https://www.ahajournals.org/doi/10.1161/CIR.0000000000001193

[2] C. W. Tsao et al., “Heart Disease and Stroke Statistics—2023 Update: A Report From the American Heart Association,” *Circulation*, vol. 147, no. 8, pp. e93–e621, Feb. 2023, doi: 10.1161/CIR.0000000000001123.  
Available: https://www.ahajournals.org/doi/10.1161/CIR.0000000000001123

[3] World Health Organization Regional Office for Europe, *What Is the Effectiveness of Systematic Population-Level Screening Programmes for Reducing the Burden of Cardiovascular Diseases?*, 2nd ed. Copenhagen, Denmark: WHO Regional Office for Europe, 2024.  
Available: https://www.who.int/europe/publications/i/item/978-92-890-6088-2

[4] “iirnotch — SciPy v1.18.0 Manual.” Accessed: Sep. 24, 2026. [Online]. Available: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.iirnotch.html

[5] G. Lenis, N. Pilia, A. Loewe, W. H. W. Schulze, and O. Dössel, “Comparison of Baseline Wander Removal Techniques considering the Preservation of ST Changes in the Ischemic ECG: A Simulation Study,” Comput Math Methods Med, vol. 2017, p. 9295029, 2017, doi: 10.1155/2017/9295029.

[6] S. Gradl, P. Kugler, C. Lohmüller y B. M. Eskofier, “Real-time ECG monitoring and arrhythmia detection using Android-based mobile devices,” Proc. 34th Annual International Conference of the IEEE Engineering in Medicine and Biology Society, pp. 2452–2455, 2012, doi: 10.1109/EMBC.2012.6346460.
