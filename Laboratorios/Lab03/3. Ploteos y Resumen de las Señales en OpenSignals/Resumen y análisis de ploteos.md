# Resumen del registro electromiográfico: 
En este documento presentamos el análisis de las señales EMG adquiridas en OpenSignals para dos sujetos de prueba. 
Para cada compañera, evaluamos la actividad neuromuscular en dos condiciones: movimiento leve y movimiento central, documentando tres intentos consecutivos por cada condición. 
El objetivo es caracterizar la progresión del reclutamiento de unidades motoras y validar la técnica de las capturas antes de proceder al filtrado digital y extracción de caracteristicas como amplitud y frecuencia  en el analisis en Python. 
## Análisis e interpretación por sujeto y condición 
### 1.- Sujeto 1 (Adriana): 
 - Movimiento leve: 
En los tres ploteos correspondientes a esta condición, la señal aumenta con respecto al nivel o piso basal de ruido instrumental para mostrar ráfagas eléctricas aisladas y de corta duración. La amplitud pico a pico se mantiene en un rango bajo. A nivel fisiológico, las graficas reflejan que el sistema nervioso central esta activando un número reducido de motoneuronas para generar un nivel de fuerza controlado y submáximo.
 - Movimiento Contrafuerza:
Durante los tres intentos de movimiento contrafuerza, la morfología cambia ya que las ráfagas discretas son reemplazadas por un patrón interferencial denso y continuo, cuya amplitud pico a pico tiene un ensanchamiento significativo en comparación con la prueba anterior, estando mas visible entre los limites de 1mV a -1mV en el eje Y. Esto se puede interpretar como un reclutamiento espacial y temporal explosivo, ya que tiene un ascenso rápido y luego alcanza un pico máximo de tensión para superar la resistencia y por ultimo una fase de relajación gradual.

### 2.- Sujeta 2 (Kim): 
Movimiento leve:
En los tres ploteos evaluados para esta condición, la señal se eleva por encima del ruido basal mostrando ráfagas eléctricas contenidas y de corta duración, acompañadas de ligeras fluctuaciones en la línea base que corresponden a artefactos de movimiento. La amplitud pico a pico sigue manteniéndose en un rango bajo en comparación del sujeto 1. Sin embargo, para este sujete se puede evidenciar que la duración sus movimientos leves son mayores. Del mismo modo, tambien refleja la activicación de un grupo reducido de motoneuronas que generan los niveles de fuerza controlado. 

Movimiento Contrafuerza:
Durante los tres intentos finales bajo esta condición, la señal adopta un patrón interferencial prolongado, pero con un amplitud menor, manteniéndose contenida en el rango de aproximadamente -0.5mV a 0.5mV. Por lo que la gráfica muestra una contracción isométrica sostenida, en lugar de un pico explosivo. 
