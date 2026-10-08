## Link de la presentación de CANVA:
https://www.canva.com/design/DAHXdajj-uA/IqHXFzPek07sOkcguUW_bA/edit

# Avance 2

## Plan de acción (Cronograma de Avances)

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

Descargamos la **MIT-BIH Arrhythmia Database** de PhysioNet usando la librería `wfdb` de Python (`eda_mitdb.py`). Usamos Visual Studio Code para hacer el proceso de codificado y para cada registro se leen la señal (`.dat`, `.hea`) y las anotaciones de los especialistas (`.atr`).

Con esto logramos generar dos tablas:

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



### 4. Conclusiones del avance

- La base ya la tenemos descargada, organizada por latido y agrupada en clases AAMI.
- El desbalance de clases define cómo evaluaremos el sistema: sensibilidad y especificidad.
- El EDA confirma que el RR (ritmo) separa bien los latidos prematuros y que la morfología del QRS es necesaria para los ventriculares.
- El detector del Avance 1 funciona bien en señales limpias, pero hay que mejorarlo cuando tenemos registros ruidosos.

### Referencia adicional

[1] ANSI/AAMI EC57:2012, *Testing and Reporting Performance Results of Cardiac Rhythm and ST Segment Measurement Algorithms*. Arlington, VA, USA: AAMI, 2012.
