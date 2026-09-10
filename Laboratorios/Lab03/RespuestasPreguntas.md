
# Respuestas a las preguntas:
Q1. Which are the significant frequencies for EMG acquisitions? Are they the same in all body areas such as facial
area?
- La banda que usan es de normalmente 20 a 450 Hz, porque esta es la que permite ver la información relevante de los movimientos musculares. Pero no son las mismas en todo el cuerpo por lo que diferentes músculos pueden tener diferentes frecuencias, ya que estas cambian también. 

Q2. Which kind of filter is essential when working with EMG signals? Why do we need to apply such a filter?
- Es importante utilizar un filtro pasa banda para conservar las frecuencias propias de la señal EMG y eliminar aquellas que corresponden principalmente a ruido.

Q3. How does the amplitude differ in each muscular contraction? Is there a difference for body locations?
- La amplitud de la señal EMG generalmente aumenta cuando aumenta la intensidad de la contracción muscular, debido a que se activan más unidades motoras. 
También puede variar dependiendo de la ubicación del músculo, su tamaño, la posición de los electrodos y la distancia entre ellos. 
Por ello, las amplitudes obtenidas en músculos faciales pueden ser diferentes de las obtenidas en músculos de brazos o piernas.

Q4. Show a screenshot of a relevant portion of Electromyography (EMG) data within the experiment proposed on Section D of a facial muscle of interest. Does this signal correspond to what you expected? Why? Which emotion and action did you perform to trigger the muscle? Which muscle did you trigger?
![Señal EMG bíceps braquial - movimiento con contrafuerza](./ADICIONALES/SUJETO1_BICEPS/Sujeto1_movimiento%20contrafuerza.png)
El músculo activado fue el bíceps braquial. La acción realizada fue una contracción voluntaria con contrafuerza (resistencia) al flexionar el antebrazo sobre el brazo, repitiendo el movimiento en tres intentos consecutivos. La señal obtenida sí corresponde a lo esperado: se observa una línea base estable alrededor de 500 (valor ADC en reposo), interrumpida por tres ráfagas claras de actividad EMG de alta amplitud (llegando hasta ~800 y bajando hasta ~150-200 en los picos), correspondientes a cada contracción con resistencia. Entre cada ráfaga la señal retorna a los niveles basales, indicando relajación muscular. Este comportamiento es consistente con lo esperado fisiológicamente, ya que al aplicar contrafuerza se reclutan más unidades motoras del bíceps braquial y aumenta su tasa de disparo, lo que se traduce en una mayor amplitud de la señal EMG en comparación con un movimiento sin resistencia.

Q5. To the best of your knowledge, does the EMG amplitude equal to the amount of force that you have generated
with your muscle?
- No exactamente. La amplitud de la señal EMG está relacionada con la fuerza muscular, porque una mayor fuerza generalmente requiere una mayor activación de unidades motoras. 
Sin embargo, la amplitud del EMG no es directamente igual a la fuerza generada, ya que también depende de factores como la posición de los electrodos, el músculo analizado, 
la cantidad de unidades motoras activadas y las características de la señal.
