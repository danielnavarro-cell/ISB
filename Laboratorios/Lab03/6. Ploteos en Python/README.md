# Ploteos en Python

Aquí colocamos las gráficas de las señales EMG de Adriana y de Kimberly, también se hizo un ploteo de la FFT.

## Gráficas de Adriana

<img width="1590" height="495" alt="image" src="https://github.com/user-attachments/assets/dae2f268-7726-40bb-ba63-68195a7c3d6d" /> 

En el dominio del tiempo, esta señal se mantiene en un estado de silencio eléctrico basal. Las variaciones oscilan  alrededor del valor central de 512. La amplitud pico a pico es mínima, representando el ruido térmico y electrónico inherente de los electrodos superficiales sin actividad muscular subyacente.
Por otro lado, en el dominio de la frecuencia, notamos como el espectro es plano y de magnitud baja, rondando los -50 dB de techo y sin picos notables, lo que confirma que aún no se ha realizado ningún movimiento por la ausencia de potenciales de acción.

<img width="1590" height="495" alt="image" src="https://github.com/user-attachments/assets/3eff47cb-2c9e-4af5-94cb-26d7099ac50a" />

Para el movimiento leve, en el dominio del tiempo se observan tres ráfagas que representan contracciones voluntarias de baja intensidad. La amplitud aumenta llegando a picos que varían entre 430 y 550. Y a partir de lo visto en la sesión teórica, esto refleja un reclutamiento espacial inicial, donde el el sistema nervioso activa selectivamente un número reducido de fibras musculares para generar una fuerza controlada. 
Y por el lado del dominio de la frecuencia, se observa que la energía espectral deja el patrón plano y comienza a concentrarse en 20 Hz y 150 Hz, banda fisiológica típica del EMG.

<img width="1590" height="495" alt="image" src="https://github.com/user-attachments/assets/38d2357d-95d9-42c3-aad2-ae795021dfba" />
En el dominio del tiempo, la amplitud pico a pico es mayor y oscila entre 150 a 800, esta ensanchamiento indica que el músculo ha reclutado una cantidad masiva de unidades motoras disparando a alta frecuencia para sostener un esfuerzo físico considerable. 
Respecto a la señal transformada al dominio de la frecuencia por la FFT, vemos que esta definida y existe un pico pronunciado alrededor de los 50-100 Hz y la magnitud total en decibelios es superior en todo el espectro fisiológico en comparación con las pruebas anteriores. 

## Gráficas de Kimberly

<img width="1590" height="495" alt="image" src="https://github.com/user-attachments/assets/41071a89-b29f-4091-a4a1-4f3c1cc60087" />
En el dominio del tiempo la señal muestra una línea base estable aproximadamente en el valor de 506, tambien presenta fluctuaciones minimas entre 504 y 510, re


<img width="1590" height="495" alt="image" src="https://github.com/user-attachments/assets/a281a1cf-47da-4042-8617-27e42113191a" />

<img width="1590" height="495" alt="image" src="https://github.com/user-attachments/assets/1b2bbe64-7c85-4616-b026-6ebb46dc0438" />
