# Informe de adquisición y análisis de señales EEG con BITalino

## 1. Introducción

En este informe se recopila el procedimiento de adquisición y el análisis de las señales electroencefalográficas (EEG) registradas mediante **BITalino** y **OpenSignals**. Se estudiaron dos participantes, **Antonella** y **Kimberly**, bajo cuatro condiciones experimentales: condición basal, apertura de ojos/pestañeo, actividad cognitiva mediante preguntas y escucha de música.

El análisis incluye representaciones en el **dominio del tiempo** y el **dominio de la frecuencia**, además de la señal filtrada, el espectro obtenido mediante FFT, la densidad espectral de potencia (PSD) y la distribución de potencia por bandas EEG.

---

## 2. Adquisición de las señales EEG

Para la adquisición de las señales electroencefalográficas (EEG) se utilizó el sistema **BITalino**, conectado mediante Bluetooth a una computadora y empleando el software **OpenSignals** para visualizar y almacenar las señales.

### 2.1 Procedimiento

1. **Preparación del sistema:**  
Se conectaron los sensores de EEG al BITalino y posteriormente el dispositivo se vinculó mediante Bluetooth con la computadora. 
En OpenSignals se verificó la correcta detección del dispositivo y de los canales utilizados para la adquisición.

2. **Preparación del participante:**  
   El participante se colocó en una posición cómoda con una máscara que le tapara los ojos junto con unos audífonos para evitar el ruido externo y se procuró mantenerlo con el menor movimiento posible durante el registro, con el objetivo de disminuir artefactos producidos por movimientos musculares o desplazamiento de los electrodos.

3. **Preparación de la piel:**  
   Antes de colocar los electrodos, se limpió la superficie de la piel en las zonas seleccionadas para mejorar el contacto electrodo-piel y reducir posibles interferencias en la señal.

4. **Colocación de los electrodos:**  
   Los electrodos fueron colocados de acuerdo con las posiciones establecidas para la práctica. También se colocaron los electrodos de referencia correspondientes para permitir la adquisición diferencial de la actividad eléctrica cerebral.

5. **Configuración de OpenSignals:**  
   Una vez colocados los electrodos, se seleccionaron los canales correspondientes al EEG en OpenSignals. Para los registros realizados se utilizaron los canales **A1 y A2**, configurados con una frecuencia de muestreo de **1000 Hz**.

6. **Verificación de la señal:**  
   Antes de iniciar cada registro se observó la señal en tiempo real para comprobar que los electrodos tuvieran un contacto adecuado y que no existieran artefactos excesivos.

7. **Registro de las señales:**  
   Se inició la adquisición mientras el participante realizaba la condición indicada para cada prueba. Durante cada registro se procuró mantener las mismas condiciones experimentales y evitar movimientos innecesarios.

8. **Almacenamiento de los datos:**  
   Finalmente, las señales adquiridas fueron guardadas desde OpenSignals en archivos `.txt`. Estos archivos contienen las muestras correspondientes a los canales A1 y A2 y posteriormente fueron utilizados para el procesamiento, filtrado, graficación y análisis de las señales EEG.


---

## 3. Fundamento para el análisis temporal y frecuencial

### 3.1 Bandas EEG consideradas

| Banda | Rango aproximado | Asociación fisiológica general |
|---|---:|---|
| Delta (δ) | 0.5–4 Hz | Actividad lenta y sueño profundo |
| Theta (θ) | 4–8 Hz | Somnolencia, memoria y procesamiento interno |
| Alpha (α) | 8–13 Hz | Relajación y reposo, especialmente con ojos cerrados |
| Beta (β) | 13–30 Hz | Atención y procesamiento cognitivo |
| Gamma (γ) | >30 Hz | Procesamiento de mayor frecuencia |

### 3.2 Dominio del tiempo

La representación temporal permite observar cómo cambia la amplitud de la señal EEG durante el registro. A partir de ella se pueden reconocer variaciones de amplitud, eventos transitorios y posibles artefactos asociados a parpadeos, movimientos o actividad muscular.

### 3.3 FFT y dominio de la frecuencia

La **Transformada Rápida de Fourier (FFT)** se utiliza para obtener una representación frecuencial de la señal registrada en el tiempo. Esto permite observar en qué regiones de frecuencia existe una mayor contribución y relacionarlas con las bandas Delta, Theta, Alpha, Beta y Gamma. En una señal EEG, estas componentes aparecen superpuestas en el dominio temporal, por lo que el análisis frecuencial complementa la inspección visual de la señal cruda.

### 3.4 PSD y potencia por bandas

La densidad espectral de potencia (PSD) permite observar cómo se distribuye la potencia de la señal a lo largo de la frecuencia. A partir de esta distribución se puede estimar la contribución relativa de cada banda EEG y comparar las distintas condiciones experimentales.

---

## 4. Inspección inicial de las señales en OpenSignals

### 4.1 Condición basal

<img width="2940" height="1842" alt="basal" src="https://github.com/user-attachments/assets/676c7fb5-2bba-458d-866d-c84cbf53b309" />

##### Observaciones

Durante el registro basal, la señal presenta una actividad relativamente estable durante la mayor parte del intervalo analizado.

En el **canal A1** se observa una señal centrada aproximadamente alrededor de cero, con oscilaciones de pequeña amplitud durante la mayor parte de la adquisición. Sin embargo, aparecen algunos picos aislados de mayor amplitud. Estos eventos son considerablemente más grandes que la actividad observada alrededor de ellos y podrían corresponder a **artefactos producidos por movimiento, parpadeo, cambios en el contacto de los electrodos o interferencias externas**.

El **canal A2** muestra un comportamiento todavía más estable, con menor variabilidad de la señal central y sin cambios abruptos tan marcados como los encontrados en A1.

En términos generales, el registro basal presenta:

- Relativa estabilidad de la señal.
- Baja variabilidad alrededor de la línea de referencia.
- Pocos eventos transitorios de gran amplitud.
- Diferencias de amplitud entre los canales A1 y A2.
- Presencia de algunos posibles artefactos principalmente en A1.

Esta condición puede utilizarse como **referencia para comparar los cambios producidos durante la apertura de los ojos y durante la actividad cognitiva**.

---

### 4.2 Condición de ojos abiertos

<img width="2940" height="1842" alt="eeg_ojos_abiertos" src="https://github.com/user-attachments/assets/9cd03c3d-6627-4d65-96c7-e29217a2e3d6" />

##### Observaciones

Al solicitar a la participante que mantuviera los **ojos abiertos**, la señal presenta una mayor variabilidad temporal respecto al registro basal.

En ambos canales se observa un aumento importante de las fluctuaciones de amplitud. En **A1** aparecen múltiples variaciones rápidas y algunos eventos abruptos que alcanzan amplitudes considerablemente mayores que las oscilaciones habituales de la señal.

El canal **A2** presenta un comportamiento similar, con mayor dispersión de los valores alrededor de cero y algunos eventos transitorios pronunciados.

La apertura de los ojos introduce además nuevas posibles fuentes de artefacto. Los movimientos oculares y los parpadeos generan potenciales eléctricos relativamente grandes debido a la actividad electrooculográfica (EOG), los cuales pueden propagarse hacia los electrodos utilizados para registrar EEG.

Por esta razón, parte de los picos de gran amplitud encontrados durante esta etapa podrían estar asociados a:

- Parpadeos.
- Movimiento de los ojos.
- Movimiento de la cabeza.
- Actividad muscular facial.
- Variaciones en el contacto entre electrodo y piel.

Comparando visualmente con la condición basal, el registro de ojos abiertos muestra una señal **menos estable y con una mayor cantidad de fluctuaciones y eventos transitorios**.

Sin embargo, esta observación no permite afirmar directamente que una banda específica del EEG aumentó o disminuyó. Para comprobar, por ejemplo, la reducción de actividad alfa asociada a la apertura de los ojos, sería necesario analizar el contenido espectral de la señal.

---

### 4.3 Actividad cognitiva: preguntas sin respuesta verbal

<img width="2940" height="1836" alt="eeg_preguntas" src="https://github.com/user-attachments/assets/e839686e-0d5c-4fc9-98ec-d54bf3a91fb6" />

##### Procedimiento

Durante esta etapa se realizaron diferentes preguntas a la participante. Se le indicó que debía **pensar mentalmente en la respuesta sin decirla en voz alta**.

El objetivo fue generar una condición de actividad cognitiva evitando, en la medida de lo posible, los artefactos musculares asociados al habla.

##### Observaciones

Durante esta condición se observa una actividad continua y variable en ambos canales.

En el **canal A1** existen oscilaciones frecuentes alrededor de la línea basal, con variaciones positivas y negativas a lo largo de todo el registro. A diferencia de la condición de ojos abiertos, en el segmento mostrado no predominan eventos extremos tan notorios, sino una actividad distribuida de manera relativamente continua.

El **canal A2** presenta igualmente fluctuaciones constantes alrededor de su valor de referencia. La señal conserva una variabilidad temporal considerable durante prácticamente toda la adquisición.

Esta actividad coincide temporalmente con el periodo durante el cual la participante estaba escuchando las preguntas y elaborando mentalmente sus respuestas.

No obstante, únicamente a partir de la señal temporal **no es posible atribuir estas variaciones directamente al procesamiento cognitivo**. Para evaluar posibles cambios asociados a concentración, atención o procesamiento mental sería necesario comparar cuantitativamente la potencia de diferentes bandas de frecuencia entre las condiciones experimentales.

---

### 4.4 Comparación entre las tres condiciones

| Característica | Basal | Ojos abiertos | Preguntas |
|---|---|---|---|
| Estabilidad temporal | Mayor | Menor | Intermedia |
| Fluctuaciones rápidas | Bajas en gran parte del registro | Elevadas | Frecuentes |
| Eventos de gran amplitud | Algunos eventos aislados | Varios eventos pronunciados | Menos pronunciados en el segmento mostrado |
| Posibles artefactos oculares | Menores | Mayores | Posibles |
| Posibles artefactos de movimiento | Algunos | Más notorios | Posibles |
| Actividad cognitiva dirigida | No | No necesariamente | Sí |
| Interpretación espectral | No realizada | No realizada | No realizada |

La diferencia más evidente en los registros temporales se encuentra entre la **condición basal y la condición de ojos abiertos**.

Durante el basal se observa una señal comparativamente más estable, mientras que con los ojos abiertos aumenta considerablemente la variabilidad y aparecen eventos de mayor amplitud.

Durante la condición de preguntas, la señal mantiene fluctuaciones continuas mientras la participante procesa mentalmente las respuestas, aunque el registro mostrado no presenta tantos eventos extremos como la condición de ojos abiertos.

---

### 4.5 Consideraciones sobre los artefactos

Es importante considerar que una señal EEG posee amplitudes relativamente pequeñas y puede ser fácilmente contaminada por otras fuentes eléctricas.

Entre los principales artefactos que podrían encontrarse en los registros realizados se encuentran:

- **EOG:** movimiento de los ojos y parpadeos.
- **EMG:** contracciones de músculos faciales, mandibulares o del cuello.
- Movimiento del participante.
- Modificaciones del contacto electrodo-piel.
- Ruido eléctrico ambiental.
- Interferencia de la red eléctrica.

Los picos abruptos que aparecen en determinados instantes, particularmente durante la condición de ojos abiertos, deben analizarse cuidadosamente antes de considerarlos actividad cerebral.

---

### 4.6 Interpretación fisiológica esperada

La comparación realizada es consistente con algunos fenómenos esperados durante el registro EEG.

Durante condiciones de reposo, especialmente cuando existe relajación y reducción de estímulos visuales, la actividad cerebral puede presentar un comportamiento más regular.

Al abrir los ojos aumenta el procesamiento de información visual y también se introducen artefactos relacionados con los movimientos oculares y los parpadeos. Por ello, el registro temporal puede mostrar una mayor variabilidad.

Por otro lado, durante la condición de preguntas existe un aumento de la demanda cognitiva debido a procesos como:

- Atención.
- Comprensión de la pregunta.
- Recuperación de información.
- Memoria de trabajo.
- Elaboración mental de una respuesta.

Sin embargo, para relacionar estos procesos con cambios específicos del EEG se requiere complementar la inspección temporal con un **análisis en frecuencia**.

---

---

### 4.7 Síntesis de la inspección en OpenSignals

Los registros obtenidos mediante OpenSignals permiten observar diferencias cualitativas entre las tres condiciones experimentales.

La **condición basal** presenta el comportamiento temporal más estable, aunque existen algunos eventos aislados posiblemente asociados a artefactos.

La condición de **ojos abiertos** muestra un incremento evidente de la variabilidad y una mayor presencia de eventos de amplitud elevada, probablemente como resultado de la combinación entre actividad EEG y artefactos oculares o musculares.

Finalmente, durante la condición de **preguntas sin respuesta verbal** se observa una actividad continua mientras la participante realiza el procesamiento mental de las preguntas. El hecho de no responder verbalmente permite reducir parte de la contaminación electromiográfica producida por los músculos involucrados en el habla.

A pesar de estas diferencias visuales, no es posible determinar únicamente a partir de estos gráficos qué bandas cerebrales aumentaron o disminuyeron. Por ello, la interpretación se complementó con el procesamiento digital de las señales y la comparación de su contenido espectral.

---

## 5. Resultados — Participante Antonella

### 5.1 Condición basal

#### Señal EEG original

<p align="center"><img src="6. Ploteos en python/Análisis de Primera Persona/Basal_Anto/Señal_EEG_basal.png" width="900" alt="Señal EEG basal"></p>

La señal basal representa el estado de referencia de la participante, antes de introducir estímulos o tareas cognitivas específicas.

En el dominio temporal se observa la actividad espontánea del EEG, compuesta por oscilaciones de amplitud variable. Este registro sirve como punto de comparación para las demás condiciones experimentales.

En una condición basal se espera una señal relativamente estable, aunque pueden aparecer fluctuaciones asociadas a movimientos involuntarios, actividad ocular, contracciones musculares o variaciones en el contacto de los electrodos.

---

#### Señal EEG filtrada

<p align="center"><img src="6. Ploteos en python/Análisis de Primera Persona/Basal_Anto/EEG_filtrado_basal.png" width="900" alt="EEG filtrado basal"></p>

Luego del filtrado se observa una señal más limpia, donde se reducen componentes de muy baja frecuencia, ruido eléctrico y componentes fuera del rango de interés del EEG.

La señal filtrada permite distinguir con mayor claridad las oscilaciones cerebrales que se encuentran dentro del rango fisiológico esperado.

La diferencia entre la señal original y la señal filtrada muestra la importancia del preprocesamiento antes de realizar cualquier análisis espectral.

---

#### Espectro de frecuencia

<p align="center"><img src="6. Ploteos en python/Análisis de Primera Persona/Basal_Anto/espectro_EEG_basal.png" width="900" alt="Espectro EEG basal"></p>

El espectro permite observar qué frecuencias poseen mayor amplitud dentro de la señal.

En el EEG basal, gran parte de la energía suele concentrarse en frecuencias relativamente bajas. Dependiendo del estado de relajación de la participante, pueden observarse componentes relacionadas con las bandas theta y alpha.

No obstante, la presencia de un pico espectral no debe interpretarse de manera aislada, ya que algunos componentes pueden corresponder a interferencias o artefactos.

---

#### Densidad espectral de potencia

<p align="center"><img src="6. Ploteos en python/Análisis de Primera Persona/Basal_Anto/Densidad_EEG_basal.png" width="900" alt="Densidad EEG basal"></p>

La densidad espectral de potencia, o PSD, muestra cómo se distribuye la potencia de la señal en función de la frecuencia.

Esta representación es especialmente útil en EEG porque permite evaluar qué bandas presentan mayor contribución energética.

En la condición basal se utiliza esta gráfica como referencia para comparar posteriormente los cambios producidos por los estímulos visuales, cognitivos y auditivos.

---

#### Distribución de potencia por bandas

<p align="center"><img src="6. Ploteos en python/Análisis de Primera Persona/Basal_Anto/distribucion_potencia_EEG_basal.png" width="900" alt="Distribución de potencia EEG basal"></p>

La distribución por bandas resume el contenido espectral del EEG y permite comparar directamente la contribución relativa de delta, theta, alpha, beta y gamma.

Este gráfico funciona como una referencia cuantitativa para analizar si alguna banda aumenta o disminuye durante las otras condiciones experimentales.

---

### 5.2 Ojos abiertos y pestañeo

#### Señal EEG

<p align="center"><img src="6. Ploteos en python/Análisis de Primera Persona/Pestañeo_Anto/ojos_abiertos_señal.png" width="900" alt="EEG ojos abiertos"></p>

Durante esta condición se observa el EEG mientras la participante mantiene los ojos abiertos y realiza movimientos oculares o pestañeos.

A diferencia de la condición basal, los movimientos de los ojos pueden introducir artefactos importantes en la señal debido a la actividad electrooculográfica.

Los pestañeos pueden generar deflexiones de gran amplitud en el registro temporal debido al movimiento del dipolo eléctrico generado por el ojo.

Por esta razón, los cambios bruscos de amplitud encontrados en esta condición no deben interpretarse necesariamente como actividad cortical.

---

#### Señal EEG filtrada

<p align="center"><img src="6. Ploteos en python/Análisis de Primera Persona/Pestañeo_Anto/señal_EEG_filtrado.png" width="900" alt="EEG ojos filtrado"></p>

Luego del filtrado, la señal presenta una reducción de componentes indeseadas, aunque algunos artefactos oculares pueden permanecer debido a que su contenido frecuencial puede superponerse con las bandas EEG.

Esta condición demuestra una de las principales dificultades del registro electroencefalográfico: separar la actividad cerebral real de señales fisiológicas externas.

---

#### Espectro de frecuencia

<p align="center"><img src="6. Ploteos en python/Análisis de Primera Persona/Pestañeo_Anto/Espectro_EEG_ojos.png" width="900" alt="Espectro EEG ojos"></p>

El espectro durante la apertura de los ojos puede presentar diferencias respecto al basal.

Fisiológicamente, la apertura de los ojos suele producir una reducción de la actividad alpha asociada al denominado **bloqueo alpha**, especialmente cuando el sujeto pasa de una condición relajada con ojos cerrados a una condición con mayor estimulación visual.

Además, los movimientos oculares introducen componentes de baja frecuencia que pueden incrementar artificialmente la energía en las regiones bajas del espectro.

---

#### Densidad espectral de potencia

<p align="center"><img src="6. Ploteos en python/Análisis de Primera Persona/Pestañeo_Anto/Densidad_espectral.png" width="900" alt="PSD ojos"></p>

La PSD permite visualizar cómo cambia la distribución energética durante esta condición.

En comparación con el basal, la actividad puede volverse más distribuida debido al procesamiento visual y a la presencia de artefactos oculares.

Debe tenerse especial cuidado al interpretar incrementos en frecuencias bajas, ya que podrían estar relacionados con parpadeos o movimientos oculares.

---

#### Distribución de potencia

<p align="center"><img src="6. Ploteos en python/Análisis de Primera Persona/Pestañeo_Anto/distribucion_potencia_EEG_ojos.png" width="900" alt="Distribución EEG ojos"></p>

Esta gráfica permite comparar la contribución de cada banda EEG durante la apertura de los ojos.

La comparación con el basal permite identificar posibles cambios en la potencia relativa de alpha, beta y otras bandas.

En particular, una reducción relativa de alpha sería compatible con el aumento del procesamiento visual asociado a la apertura de los ojos.

---

### 5.3 Actividad cognitiva: preguntas

#### Señal EEG

<p align="center"><img src="6. Ploteos en python/Análisis de Primera Persona/Preguntas_Anto/SEÑAL_eeg_preguntas.png" width="900" alt="EEG preguntas"></p>

Durante esta condición se realizaron preguntas a la participante y se le indicó que debía pensar en la respuesta sin verbalizarla.

Este procedimiento busca inducir actividad cognitiva relacionada con atención, memoria, comprensión y elaboración mental, evitando al mismo tiempo artefactos musculares asociados al habla.

La señal presenta una actividad EEG continua durante el periodo en que la participante procesa las preguntas.

---

#### Señal filtrada

<p align="center"><img src="6. Ploteos en python/Análisis de Primera Persona/Preguntas_Anto/señal_Filtrado_eeg.png" width="900" alt="EEG preguntas filtrado"></p>

Después del filtrado, se conserva principalmente la actividad dentro del rango fisiológico del EEG.

La señal filtrada facilita la identificación de oscilaciones cerebrales y reduce interferencias externas.

Durante una tarea cognitiva pueden aparecer cambios en las bandas theta y beta relacionados con procesos de memoria de trabajo, atención y procesamiento mental.

---

#### Espectro de frecuencia

<p align="center"><img src="6. Ploteos en python/Análisis de Primera Persona/Preguntas_Anto/espectro_egg_preguntas.png" width="900" alt="Espectro EEG preguntas"></p>

El espectro permite observar qué frecuencias dominan durante el procesamiento de las preguntas.

En comparación con la condición basal, puede existir una redistribución de la energía hacia bandas relacionadas con actividad cognitiva.

La banda beta suele asociarse con atención y procesamiento activo, mientras que cambios en theta también pueden aparecer durante tareas que involucran memoria de trabajo.

Sin embargo, estas relaciones deben interpretarse como tendencias fisiológicas generales y no como una medición directa de pensamientos específicos.

---

#### Densidad espectral de potencia

<p align="center"><img src="6. Ploteos en python/Análisis de Primera Persona/Preguntas_Anto/densidad_espectral_egg_preguntas.png" width="900" alt="PSD EEG preguntas"></p>

La PSD permite evaluar con mayor claridad la distribución energética durante la tarea cognitiva.

Comparar esta gráfica con la PSD basal permite identificar qué regiones de frecuencia aumentaron o disminuyeron durante el procesamiento mental de las preguntas.

---

#### Distribución de potencia

<p align="center"><img src="6. Ploteos en python/Análisis de Primera Persona/Preguntas_Anto/distrubucion_preguntas_Eeg.png" width="900" alt="Distribución EEG preguntas"></p>

La distribución por bandas facilita la comparación entre la condición cognitiva y la condición basal.

Un incremento relativo de componentes theta o beta podría ser coherente con una mayor demanda de memoria, atención y procesamiento cognitivo.

Sin embargo, la interpretación debe realizarse considerando también la señal temporal y la posible presencia de artefactos.

---

### 5.4 Actividad con música

#### Señal EEG

<p align="center"><img src="6. Ploteos en python/Análisis de Primera Persona/Actividad_musica_Anto/señal_EEG_anto_musica.png" width="900" alt="EEG música"></p>

Durante esta etapa la participante estuvo expuesta a un estímulo musical.

La música constituye un estímulo auditivo complejo capaz de involucrar simultáneamente procesos de atención, percepción auditiva, memoria y respuesta emocional.

La señal temporal muestra la actividad EEG registrada durante toda la estimulación musical.

---

#### Señal filtrada

<p align="center"><img src="6. Ploteos en python/Análisis de Primera Persona/Actividad_musica_Anto/eeg_filtrado_musica_Anto.png" width="900" alt="EEG música filtrada"></p>

La señal filtrada permite observar con mayor claridad las componentes cerebrales relevantes eliminando parte del ruido y de las frecuencias fuera del rango de interés.

Durante la escucha de música pueden presentarse cambios en diferentes bandas EEG dependiendo del nivel de atención, familiaridad, relajación o respuesta emocional generada por el estímulo.

---

#### Espectro de frecuencia

<p align="center"><img src="6. Ploteos en python/Análisis de Primera Persona/Actividad_musica_Anto/espectro_eeg_musica_anto.png" width="900" alt="Espectro EEG música"></p>

El espectro permite identificar las frecuencias predominantes durante la estimulación musical.

Al comparar este registro con el basal puede observarse si la música produce una redistribución de la energía entre las distintas bandas.

Dependiendo del estado de la participante, puede existir una combinación de actividad relacionada con relajación, atención y procesamiento auditivo.

---

#### Densidad espectral de potencia

<p align="center"><img src="6. Ploteos en python/Análisis de Primera Persona/Actividad_musica_Anto/densidad_eeg_music_anto.png" width="900" alt="PSD EEG música"></p>

La densidad espectral permite analizar con mayor precisión cómo se distribuye la potencia de la señal durante la escucha musical.

Esta representación puede mostrar cambios con respecto a la condición basal que no son evidentes únicamente observando la señal en el dominio temporal.

---

#### Distribución de potencia por bandas

<p align="center"><img src="6. Ploteos en python/Análisis de Primera Persona/Actividad_musica_Anto/distribucion_musica_eeg_anto.png" width="900" alt="Distribución EEG música"></p>

La distribución de potencia permite comparar directamente la participación de las bandas delta, theta, alpha, beta y gamma.

Esta gráfica resulta particularmente útil para evaluar si el estímulo musical produjo un patrón diferente respecto a la condición basal o a la actividad cognitiva.

---

### 5.5 Comparación general entre condiciones

Las cuatro condiciones muestran diferentes características tanto en el dominio temporal como frecuencial.

| Condición | Característica principal | Interpretación esperada |
|---|---|---|
| Basal | Actividad espontánea y relativamente estable | Referencia fisiológica |
| Ojos abiertos / pestañeo | Mayor presencia de transitorios y artefactos oculares | Procesamiento visual + EOG |
| Preguntas | Actividad asociada a procesamiento mental | Atención, memoria de trabajo y cognición |
| Música | Respuesta a estimulación auditiva | Procesamiento auditivo, atención y respuesta emocional |

La condición basal se utiliza como referencia para interpretar las demás etapas.

Durante la apertura de los ojos, una parte importante de los cambios puede estar relacionada tanto con la actividad visual como con artefactos electrooculográficos.

En la condición de preguntas, las modificaciones espectrales pueden relacionarse con una mayor demanda cognitiva, especialmente en bandas theta y beta.

Finalmente, durante la escucha de música se produce una estimulación auditiva compleja que puede modificar la distribución de potencia en diferentes bandas EEG.

---

### 5.6 Importancia del análisis temporal y frecuencial

El análisis del EEG no debe realizarse únicamente observando la señal en función del tiempo.

Una señal aparentemente similar entre dos condiciones puede presentar diferencias importantes en el dominio de la frecuencia.

Por esta razón se utilizaron cinco representaciones complementarias:

- Señal EEG original.
- Señal EEG filtrada.
- Espectro de frecuencia.
- Densidad espectral de potencia.
- Distribución de potencia por bandas.

La combinación de estos análisis permite obtener una interpretación más completa de la actividad cerebral registrada.

---

### 5.7 Consideraciones sobre artefactos

Las señales EEG tienen amplitudes muy pequeñas y son susceptibles a distintas fuentes de interferencia.

Entre los principales artefactos presentes en este experimento se encuentran:

- Parpadeos y movimientos oculares.
- Movimiento de la cabeza.
- Actividad muscular facial.
- Movimiento de los electrodos.
- Variaciones de impedancia electrodo-piel.
- Interferencia eléctrica.
- Ruido de alta frecuencia.

En particular, la condición de ojos abiertos y pestañeo es útil para visualizar cómo la actividad ocular puede modificar considerablemente un registro EEG.

---

### 5.8 Síntesis de resultados

El análisis realizado permite observar que la actividad EEG de la participante cambia en función de la condición experimental.

La condición basal proporciona un punto de referencia sobre la actividad espontánea.

Los registros de ojos abiertos presentan una mayor influencia de artefactos oculares y cambios asociados al procesamiento visual.

La condición de preguntas permite estudiar modificaciones asociadas a atención y procesamiento cognitivo, mientras que la estimulación musical permite evaluar la respuesta cerebral frente a un estímulo auditivo complejo.

El uso conjunto de señales temporales, espectros, densidades espectrales y distribución de potencia permite realizar una interpretación más completa que la simple inspección de la señal cruda.

No obstante, cualquier asociación entre una banda EEG específica y un proceso cognitivo debe interpretarse con cautela, ya que las señales pueden contener artefactos y la actividad cerebral depende de múltiples procesos simultáneos.

---

## 6. Resultados — Participante Kimberly

### 6.1 Condición basal

#### Señal EEG original

<p align="center"><img src="6. Ploteos en python/Análisis de Segunda Persona/Basal_Kim/Señal_EEG_basal.png" width="900" alt="Señal EEG basal"></p>

La condición basal constituye el registro de referencia de la participante antes de realizar tareas cognitivas o recibir estímulos externos específicos.

La señal temporal muestra las variaciones espontáneas de la actividad eléctrica cerebral. Este registro permite establecer un punto de comparación para evaluar posteriormente los cambios observados durante el pestañeo, las preguntas complejas y la estimulación auditiva.

Durante una condición basal pueden observarse oscilaciones de amplitud relativamente estable, aunque también pueden aparecer variaciones asociadas a movimiento, parpadeo, actividad muscular o cambios en el contacto de los electrodos.

---

#### Señal EEG filtrada

<p align="center"><img src="6. Ploteos en python/Análisis de Segunda Persona/Basal_Kim/EEG_filtrado.png" width="900" alt="EEG filtrado basal"></p>

Luego del procesamiento, la señal filtrada presenta una reducción de componentes no deseadas y permite observar con mayor claridad las oscilaciones correspondientes al EEG.

El filtrado es importante debido a que las señales electroencefalográficas presentan amplitudes pequeñas y pueden ser fácilmente contaminadas por ruido eléctrico, movimiento o actividad muscular.

La comparación entre la señal original y la señal filtrada permite evaluar el efecto del preprocesamiento sobre el registro.

---

#### Espectro de frecuencia

<p align="center"><img src="6. Ploteos en python/Análisis de Segunda Persona/Basal_Kim/Espectro_EEG_basal.png" width="900" alt="Espectro EEG basal"></p>

El espectro muestra la contribución de las distintas frecuencias presentes en la señal EEG basal.

Esta representación permite identificar las regiones frecuenciales con mayor contenido energético y posteriormente relacionarlas con las bandas delta, theta, alpha, beta y gamma.

En una condición de reposo pueden encontrarse componentes importantes en las regiones de baja y media frecuencia, aunque la interpretación depende de las condiciones específicas de adquisición.

---

#### Densidad espectral de potencia

<p align="center"><img src="6. Ploteos en python/Análisis de Segunda Persona/Basal_Kim/Densidad_EEG_basal.png" width="900" alt="Densidad EEG basal"></p>

La densidad espectral de potencia permite observar cómo se distribuye la energía de la señal a lo largo de la frecuencia.

A diferencia del espectro de amplitud, esta representación facilita la comparación de la contribución energética de las diferentes bandas EEG.

El registro basal sirve como referencia para determinar posteriormente si existe una redistribución de potencia al introducir tareas cognitivas o estímulos externos.

---

#### Distribución de potencia

<p align="center"><img src="6. Ploteos en python/Análisis de Segunda Persona/Basal_Kim/Distribucion_potencia_EEG.png" width="900" alt="Distribución de potencia basal"></p>

La distribución de potencia permite visualizar de manera resumida la contribución relativa de cada banda de frecuencia.

Este gráfico es especialmente útil para comparar la condición basal con las condiciones de mayor demanda cognitiva o sensorial.

---

### 6.2 Ojos abiertos y pestañeo

#### Registro EEG durante pestañeo

<p align="center"><img src="6. Ploteos en python/Análisis de Segunda Persona/Pestañeo_Kim/image.png" width="900" alt="EEG pestañeo"></p>

Durante esta etapa se registró la actividad EEG mientras la participante realizaba apertura de ojos y pestañeos.

Los movimientos oculares producen potenciales eléctricos que pueden ser detectados por los electrodos de EEG. Por esta razón, los pestañeos suelen generar deflexiones de amplitud considerablemente mayor que la actividad cerebral espontánea.

Los cambios bruscos observados durante esta condición pueden estar relacionados con:

- Pestañeos.
- Movimiento del globo ocular.
- Movimiento facial.
- Actividad muscular periocular.
- Cambios momentáneos en el contacto electrodo-piel.

Por ello, estas deflexiones deben interpretarse principalmente como **posibles artefactos electrooculográficos**, y no necesariamente como cambios corticales.

Esta condición resulta útil para evidenciar la sensibilidad del EEG frente a señales fisiológicas externas.

---

### 6.3 Preguntas complejas

Durante esta etapa se realizaron preguntas que requerían mayor procesamiento mental por parte de la participante. Se buscó generar una condición de mayor demanda cognitiva asociada con procesos como atención, memoria de trabajo, recuperación de información y elaboración de respuestas.

#### Señal EEG original

<p align="center"><img src="6. Ploteos en python/Análisis de Segunda Persona/Preguntas_complejas_Kim/Señal_EEG.png" width="900" alt="Señal EEG preguntas"></p>

La señal temporal presenta la actividad registrada mientras la participante procesaba las preguntas.

A diferencia de una condición basal, durante una tarea cognitiva pueden producirse modificaciones en la actividad cerebral relacionadas con la atención sostenida y la elaboración mental.

No obstante, las variaciones temporales por sí solas no permiten determinar qué bandas EEG están involucradas, por lo que es necesario complementar el análisis con información espectral.

---

#### Señal EEG filtrada

<p align="center"><img src="6. Ploteos en python/Análisis de Segunda Persona/Preguntas_complejas_Kim/Señal_EEG_filtrada.png" width="900" alt="Señal EEG filtrada"></p>

Luego del filtrado se conservan principalmente las componentes de interés del EEG, reduciendo parte del ruido presente en la señal original.

Esto facilita la identificación de patrones oscilatorios y mejora la calidad del análisis en frecuencia.

La señal filtrada permite observar de manera más clara los cambios producidos durante el procesamiento mental de las preguntas.

---

#### Espectro de frecuencia

<p align="center"><img src="6. Ploteos en python/Análisis de Segunda Persona/Preguntas_complejas_Kim/Espectro_EEG_preguntas.png" width="900" alt="Espectro EEG preguntas"></p>

El espectro permite identificar las frecuencias predominantes durante la tarea cognitiva.

Durante actividades de atención y procesamiento mental pueden producirse modificaciones en bandas como theta y beta.

La banda theta puede relacionarse con procesos de memoria de trabajo, mientras que la actividad beta suele asociarse con atención y procesamiento activo.

Sin embargo, estas asociaciones representan tendencias fisiológicas generales y no deben interpretarse como una medición directa del contenido de los pensamientos.

---

#### Densidad espectral de potencia

<p align="center"><img src="6. Ploteos en python/Análisis de Segunda Persona/Preguntas_complejas_Kim/Densidad_EEG.png" width="900" alt="Densidad EEG preguntas"></p>

La densidad espectral permite observar la distribución energética de la señal durante la resolución de las preguntas.

Comparando esta gráfica con la condición basal se puede evaluar si determinadas regiones frecuenciales presentan una mayor o menor contribución durante la tarea cognitiva.

---

#### Distribución de potencia por bandas

<p align="center"><img src="6. Ploteos en python/Análisis de Segunda Persona/Preguntas_complejas_Kim/Distribución_de_potencias.png" width="900" alt="Distribución de potencia preguntas"></p>

La distribución de potencia resume la participación relativa de las principales bandas EEG.

Esta representación permite comparar de manera más directa la condición cognitiva con el registro basal.

Un cambio en la contribución relativa de theta o beta podría ser compatible con un aumento de la demanda cognitiva, aunque siempre debe interpretarse junto con el resto de las representaciones.

---

### 6.4 Actividad asociada al estímulo musical


#### Señal EEG

<p align="center"><img src="6. Ploteos en python/Análisis de Segunda Persona/Actividad_musica_Kim/preguntas_EEG_señal_kim.png" width="900" alt="Señal EEG música"></p>

Durante esta etapa la participante estuvo expuesta a un estímulo auditivo musical.

La música constituye un estímulo complejo que puede involucrar simultáneamente percepción auditiva, atención, memoria, respuesta emocional y procesamiento temporal.

La señal EEG temporal permite observar las variaciones de actividad registradas durante el periodo de estimulación.

---

#### Señal procesada

<p align="center"><img src="6. Ploteos en python/Análisis de Segunda Persona/Actividad_musica_Kim/preguntas_EEG_kim.png" width="900" alt="EEG música procesada"></p>

El procesamiento de la señal permite reducir componentes no deseadas y facilita la visualización de las oscilaciones presentes durante la estimulación musical.

La respuesta EEG frente a música puede variar dependiendo del nivel de atención, familiaridad con el estímulo, estado emocional y nivel de relajación de la participante.

---

#### Espectro de frecuencia

<p align="center"><img src="6. Ploteos en python/Análisis de Segunda Persona/Actividad_musica_Kim/espectro_eeg_preguntas.png" width="900" alt="Espectro EEG música"></p>

El espectro permite identificar qué regiones frecuenciales presentan una mayor contribución durante la estimulación auditiva.

Comparando este registro con la condición basal puede evaluarse si existe una redistribución del contenido frecuencial asociada al estímulo musical.

No obstante, para establecer diferencias cuantitativas sería necesario comparar directamente los valores de potencia obtenidos en cada banda.

---

#### Densidad espectral

<p align="center"><img src="6. Ploteos en python/Análisis de Segunda Persona/Actividad_musica_Kim/pregunta_EEG_densidad.png" width="900" alt="Densidad EEG música"></p>

La densidad espectral permite analizar la distribución energética de la señal durante la exposición musical.

Esta representación complementa el análisis temporal, ya que permite identificar cambios que no necesariamente son evidentes al observar únicamente la amplitud de la señal.

---

#### Distribución de potencia

<p align="center"><img src="6. Ploteos en python/Análisis de Segunda Persona/Actividad_musica_Kim/preguntas_kim_eeg.png" width="900" alt="Distribución EEG música"></p>

La distribución por bandas permite visualizar la contribución relativa de delta, theta, alpha, beta y gamma durante la actividad musical.

La comparación con la condición basal y la condición cognitiva permite evaluar si el estímulo musical produjo una distribución de potencia distinta.

---

### 6.5 Comparación general de las condiciones

| Condición | Característica principal | Interpretación general |
|---|---|---|
| Basal | Actividad espontánea | Referencia fisiológica |
| Ojos abiertos / pestañeo | Deflexiones asociadas a actividad ocular | Artefactos EOG y procesamiento visual |
| Preguntas complejas | Mayor demanda cognitiva | Atención, memoria y procesamiento mental |
| Música | Estimulación auditiva | Procesamiento auditivo y respuesta emocional |

La condición basal constituye el punto de comparación principal.

Durante la condición de pestañeo se observa una mayor influencia de la actividad ocular, lo que demuestra cómo los artefactos fisiológicos pueden alterar significativamente un registro EEG.

Durante las preguntas complejas se busca evaluar cambios asociados con una mayor demanda cognitiva.

Por otro lado, la condición musical permite estudiar cómo un estímulo auditivo complejo puede modificar la dinámica temporal y espectral del EEG.

---

### 6.6 Análisis temporal y espectral

La interpretación del EEG debe combinar diferentes representaciones.

La señal temporal permite identificar:

- Cambios de amplitud.
- Eventos transitorios.
- Artefactos.
- Variaciones en el tiempo.

El análisis espectral permite identificar:

- Frecuencias dominantes.
- Distribución de energía.
- Potencia de las bandas EEG.
- Diferencias entre condiciones experimentales.

Por esta razón, la combinación de ambos dominios proporciona una interpretación más completa del registro.

---

### 7. Consideraciones sobre artefactos

Las señales EEG pueden estar contaminadas por diferentes fuentes externas a la actividad cortical.

Entre los principales artefactos que pueden aparecer durante este experimento se encuentran:

- Parpadeos.
- Movimientos oculares.
- Actividad muscular facial.
- Movimiento de la cabeza.
- Cambios en la impedancia electrodo-piel.
- Interferencia eléctrica.
- Ruido de alta frecuencia.

La identificación de estos artefactos es fundamental para evitar interpretar actividad no cerebral como cambios en el EEG.

---

### 8. Conclusión

Los registros obtenidos permiten observar diferencias entre las condiciones experimentales evaluadas en Kimberly.

La condición basal proporciona una referencia de la actividad EEG espontánea.

La apertura de ojos y los pestañeos generan variaciones importantes relacionadas principalmente con actividad electrooculográfica y artefactos fisiológicos.

Durante la resolución de preguntas complejas se registra una condición de mayor demanda cognitiva, en la que pueden producirse cambios en la distribución de potencia de bandas relacionadas con atención y memoria de trabajo.

Finalmente, la estimulación musical permite evaluar la respuesta cerebral frente a un estímulo auditivo complejo y comparar su comportamiento temporal y espectral con las demás condiciones.

El análisis conjunto de la señal temporal, la señal filtrada, el espectro y la densidad de potencia permite realizar una interpretación más completa del EEG que la simple inspección visual de la señal cruda.

---

## 7. Síntesis del análisis temporal y frecuencial

En ambas participantes se utilizaron de manera complementaria la señal temporal original, la señal filtrada, el espectro de frecuencia, la PSD y la distribución de potencia por bandas. La señal temporal permite observar la evolución del registro y reconocer artefactos, mientras que el análisis frecuencial permite estudiar la contribución de las distintas bandas EEG.

La condición basal funciona como referencia para las demás actividades. Durante la apertura de ojos y el pestañeo pueden aparecer deflexiones relacionadas con actividad ocular. Durante las preguntas se busca una mayor demanda cognitiva y, durante la música, una respuesta asociada a la estimulación auditiva. Estas interpretaciones deben realizarse junto con el análisis espectral y considerando la presencia de artefactos.

---

## 8. Preguntas de la guía BITalino EEG

<img width="1292" height="966" alt="image" src="https://github.com/user-attachments/assets/cd6a31c8-eb82-4375-838b-753c7c63e4b7" />

### 8.1 Pregunta 1
Las frecuencias significativas según la teoría se nos enseña que va desde 0.5 hasta 40-50 Hz, y está diferenciado en bandas porque cada uno se asocia a cierto estado, entonces no, no son iguales en todas las áreas.

<img width="594" height="318" alt="image" src="https://github.com/user-attachments/assets/3b59c17a-b894-4fd5-b804-10397bc6674c" />

<img width="480" height="176" alt="image" src="https://github.com/user-attachments/assets/f403c627-0a05-4737-b8b8-b59c06470a5b" />

| Banda | Frecuencia | Estado asociado |
|-------|------------|-----------------|
| Delta (δ) | 0,5–4 Hz | Sueño profundo |
| Theta (θ) | 4–8 Hz | Somnolencia, meditación, memoria |
| Alpha (α) | 8–13 Hz | Relajación con ojos cerrados |
| Beta (β) | 13–30 Hz | Atención activa, concentración, cálculo mental |
| Gamma (γ) | >30 Hz | Procesamiento cognitivo complejo |

### 8.2 Pregunta 2
Son 2 filtros esenciales, el primero es uno pasa-banda que va normalmente de 0.5 Hz a 40 Hz y se combina con un segundo que es un filtro Notch: 
- El pasa-altos (~0,5 Hz) elimina el offset DC y las derivas lentas por sudor, respiración o movimiento de electrodos.
- El pasa-bajos (~40 Hz) elimina ruido de alta frecuencia, sobre todo la actividad muscular (EMG) de la cara y la mandíbula.
- El notch elimina la interferencia de la red eléctrica, que suele ser mucho mayor que el propio EEG.
  
Se usan porque las señales son de muy baja en amplitud, en microvoltios, entonces el ruido se mostraría más que lo que debería de ser y sería imposible identificar las bandas. 

### 8.3 Pregunta 3
No nos muestra lo que realmente piensa la persona, pero se puede notar un cambio en el estado mental ya que la potencia de las bandas de frecuencia cambian, se nota la banda Alpha (α) cuando hace la acción de cerrar los ojos para relajarse, la banda Beta (β) para cuando se realiza las preguntas difíciles y Theta en estado de meditación.

### 8.4 Pregunta 4
<img width="1120" height="696" alt="image" src="https://github.com/user-attachments/assets/edd516a3-eda1-4cbd-a83e-96695dd64828" />

En esta señal que es la de ojos abiertos/cerrados se muestran un aprox de 27s de los canales A1 y A2. Cerca de los segundos 21 y 35 podemos ver deflexiones de amplitud que aparecen en ambas señales, lo cual nos permite afirmar que corresponden al momento de abrir los ojos. 
Corresponde parcialmente a lo que esperamos, porque en sí se esperaría ver un aumento del rango Alpha (α) (8-13Hz) con los ojos cerrados y que se atenúe al abrirlos, pero no lo podemos ver tan claramente en la señal que sacamos, puede ser también porque los electrodos que usamos los tenemos en la zona prefrontal en vez de occipital lo cual hace que la distancia cambie un poco lo que esperábamos ver.

### 8.5 Pregunta 5
Como los electrodos fueron colocados bastante cerca uno del otro no podemos notar diferencias abismales en cuanto a lo de movimiento de ojos y parpadeos. La diferencia que sí podemos ver es sobre la amplitud porque en A1 los artefactos superan los 20µV mientras que en A2 apenas los alcanzan, esto se puede deber a que no sea de origen cerebral, sino que probablemente se refiera al contacto o impedancia distinta de cada electrodo con la piel, o una posición un tanto diferente respecto al ojo. 

### 8.6 Pregunta 6
<img width="1240" height="408" alt="image" src="https://github.com/user-attachments/assets/b901f056-d19c-4473-bc87-5e9fc91b54fd" />

Según la teoría en el experimento de ojos abiertos/cerrados, la banda que debería cambiar es Alpha(α) (8–13 Hz): aumenta al cerrar los ojos y relajarse, y disminuye al abrirlos (bloqueo alpha). En tareas de concentración, en cambio, debería aumentar beta (13–30 Hz) y disminuir alpha.
En la señal que tenemos el cambio alpha no se distingue muy claramente, lo que más se puede notar son los parpadeos en sí, por sus deflexiones de (~30 µV) que están entre los segundos 3, 5,5 y 6 que triplican la amplitud de lo que estaba antes y de ahí entre los segundos 6 y 10 la señal se vuelve más rápida e irregular y aparecen picos negativos de hasta −28 µV que podrían deberse también a movimientos oculares o actividad muscular.


### 8.7 Pregunta 7
No, porque no se mide de forma directa la concentración. Cuando analizamos los EEG podemos encontrar diversos comportamientos, porque por ejemplo cuando la persona se concentra su actividad neuronal se desincroniza, entonces aparece frecuencia como las beta más rápidas pero tienen menor amplitud, en cambio las amplitudes altas se manifiestan más cuando se está en reposo o incluso en el sueño. Aparte de eso también debemos de contar que el contacto con el electrodo, o los artefactos pueden producir más amplitud que alguna actividad cerebral normal. Si quisiéramos estimar lo de la concentración deberíamos enfocarnos mejor en la potencia relativa de las bandas para poder detectar en cuál es la que predomina.

---

## 9. Conclusiones generales

El laboratorio permitió adquirir señales EEG mediante BITalino y OpenSignals y analizarlas tanto en el dominio temporal como en el dominio de la frecuencia. La inspección temporal resultó útil para reconocer cambios de amplitud y posibles artefactos, mientras que la FFT y la PSD permitieron estudiar el contenido frecuencial de los registros y relacionarlo con las bandas EEG consideradas.

La comparación entre las condiciones basal, ojos abiertos/pestañeo, preguntas y música mostró que la interpretación del EEG no debe basarse únicamente en la amplitud de la señal. El análisis conjunto de la señal cruda, la señal filtrada, el espectro, la PSD y la potencia relativa por bandas proporciona una descripción más completa de los registros obtenidos.
