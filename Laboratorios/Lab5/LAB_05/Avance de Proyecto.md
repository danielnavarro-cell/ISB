Canva del primer avance de proyecto:



## Analísis de articulo referencial 
### Resumen 
Se desarrollo una aplicación para Android que visualizaba continuamente el ECG, detectaba complejos QRS e identificaba latidos que podían considerarse anormales. La aplicación recibía datos de un sensor Shimmer por Bluetooth o reproducía registros almacenados. 

#### Arquitectura y metodología del sistema
1. Adquisición de la señal ECG

Los investigadores utilizaron un sensor Shimmer para adquirir el ECG en derivación II y transmitirlo mediante Bluetooth a una aplicación Android. El sistema también podía procesar registros previamente almacenados, simulando su adquisición en tiempo real. 

2.Filtrado digital y detección QRS

Se implementó una adaptación del algoritmo de Pan-Tompkins. Primero, la señal pasa por un filtro pasa banda formado por filtros pasa bajas y pasa altas en cascada, cuyo objetivo es reducir el ruido antes de detectar los complejos QRS.

Posteriormente, se aplican una derivada de cinco puntos, una elevación al cuadrado y una integración mediante una ventana móvil. La derivada resalta los cambios rápidos del QRS; la elevación al cuadrado acentúa las pendientes pronunciadas, y la integración junta esa información para localizar cada complejo.

Para detectar los picos R, se calcula un umbral utilizando una media móvil de 150 ms, seguido de un detector de máximos de tres puntos y una verificación de los picos candidatos. 

3. Creación de plantillas y extracción de características

Una vez detectados los picos R, el sistema construye automáticamente dos plantillas QRS a partir de los primeros seis latidos válidos. Para ello, analiza ventanas de 400 ms centradas en cada pico R y busca latidos con áreas similares y una correlación de Pearson superior a 0.95. Las plantillas se actualizan posteriormente con los latidos clasificados como normales.

Para analizar cada nuevo latido, extrae cuatro características: diferencia de área respecto a la plantilla, correlación máxima, duración del QRS e intervalo RR. 

#### Interfaz 
La interfaz desarrollada en el artículo presenta la señal ECG original, los complejos QRS extraídos y las variaciones de la frecuencia cardíaca. Además, muestra la frecuencia actual, el intervalo RR en milisegundos y la cantidad de QRS reconocidos. 


Tambien los  autores incorporaron indicadores de color:

Verde : Latido identificado como normal.

Rojo : Latido identificado como anormal.

### Oportunidades de mejora 
Finalmente, identificamos oportunidades de mejora en el artículo a partir de las limitaciones encontradas
El algoritmo depende de la calidad de los primeros latidos, porque los utiliza para construir sus plantillas. Por eso proponemos evaluar la calidad de la señal antes de generarlas.

El sistema todavía presenta falsas alarmas. Nuestra idea es que la interfaz permita visualizar los latidos sospechosos para facilitar su revisión.

El algoritmo tiene una carga computacional elevada debido al cálculo de correlaciones. Por ello, podríamos comparar un método sencillo basado en intervalos RR con otro que también considere la morfología del QRS.

Finalmente, como las pruebas en vivo fueron limitadas y utilizaron el sensor Shimmer, proponemos comenzar con registros anotados de PhysioNet

4. Detección de anomalías y visualización

Finalmente, las cuatro características se introducen en un árbol de decisiones que utiliza umbrales para identificar latidos normales o anormales y alteraciones del ritmo.

La aplicación muestra continuamente el ECG, los complejos QRS y las variaciones de la frecuencia cardíaca. También presenta los intervalos RR y marca los latidos normales en verde y los anormales en rojo


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

