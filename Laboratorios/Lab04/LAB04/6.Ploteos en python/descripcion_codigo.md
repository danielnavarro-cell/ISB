
https://colab.research.google.com/drive/17pdUPH7VJ1PXXCR-wMN52AsBbCX_hIyR?usp=sharing 

En este link se encuentra nuestro Colab en el cual realizamos las pruebas 
para generar los ploteos correspondientes para cada grafica. 
Primero se identificó el canal donde se encontraba registrada la señal ECG y se extrajeron sus valores digitales. Como estos datos provenían directamente del conversor analógico-digital del BITalino, fue necesario convertirlos a voltaje y posteriormente a milivoltios, considerando la resolución del ADC, el voltaje de alimentación y la ganancia del sensor.

Luego se generó un vector de tiempo usando la frecuencia de muestreo de 1000 Hz, de modo que cada muestra pudiera ubicarse correctamente en segundos. Después, la señal fue filtrada con un filtro pasa banda entre 0.5 y 40 Hz para reducir la deriva de la línea base y parte del ruido de alta frecuencia, conservando principalmente la información útil del ECG.

A continuación, se detectaron los picos R para identificar los latidos cardíacos y seleccionar automáticamente un segmento de aproximadamente cinco ciclos. Esto permitió visualizar mejor la morfología de la señal sin mostrar todo el registro completo, que resultaría demasiado comprimido. Finalmente, se graficó la señal procesada como amplitud en milivoltios en función del tiempo.

El mismo procedimiento se aplicó a las derivaciones I, II y III y también a las diferentes condiciones experimentales, como reposo, hipoventilación e hiperventilación. De esta manera, las señales pudieron compararse utilizando el mismo método de procesamiento.
