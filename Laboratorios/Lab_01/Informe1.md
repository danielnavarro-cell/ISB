# <p align="center"> Resumen del laboratorio 01 
</p> 

# Objetivo del laboratorio : 
En este laboratorio, nuestro objetivo fue familiarizarnos con las herramientas usadas para para el desarrollo, documentación y gestión de proyectos de ingeniería
# Herramientas empleadas: 
En la sesión iniciamos descargando Git y creándonos una cuenta de GitHub, a pesar de que suelen utilizarse juntos,  cumplen funciones diferentes.
Podemos definir Git como un sistema de control de versiones que registra localmente los cambios que hacemos en el proyecto. Mientras que GitHub es una plataforma donde alojamos nuestro repositorio de Git y que nos permite colaborar entre compañeros. 
Por otro lado, también nos enseñaron el uso de VS CODE para las modificaciones sobre nuestro repositorio, esta herramienta es el entorno de desarrollo (IDE) desde donde editamos el código, ejecutamos comandos y administramos GIT. 
Por útlimo, tambien nos mencionaron hacer del Markdown que es el lenguaje con el que estructuramos y redactamos la documentación en los archivos .md . 
En conclusión, mediante Git podemos controlar la historia del proyecto en nuestras computadoras de forma local y GitHub nos permite guardar y compartir esas modificaciones en la nube para la contribución de todos los miembros de un equipo. 
# Instalación y verificación de Git
En la sesión, se nos recomendó que antes de trabajar con repositorios verificar que Git estuviera correctamente instalado.
Para ello abrimos el CMD (Símbolo del sistema) y ejecutamos el siguiente comando: 

```Símbolo del sistema
git --version
```
Esto fue lo que se mostro en la terminal: 
```Símbolo del sistema
git --version 2.55.0.windows.5
``` 
--- 

# Configuración inicial de Git

Git necesita asociar los cambios realizados con un usuario. Para ello se configuraron el nombre y el correo electrónico.
Acá se muestra la configuración en la terminal para enlazar el Git: 

```Símbolo del sistema
C:\Users\User>git config --global user.name "Daniel Navarro"

C:\Users\User>git config --global user.email "daniel.navarro@pucp.edu.pe"
```

La configuración puede verificarse utilizando:

```Símbolo del sistema
git config --global --list
```
Luego de escribir dicho comando, podemos verificar que se guardo correctamente: 

```Símbolo del sistema 
C:\Users\User>git config --global --list
user.email=daniel.navarro@pucp.edu.pe
user.name=Daniel Navarro
``` 

Esta información queda asociada posteriormente a los **commits** realizados. 

---

# Funcionamiento del Git 
Todo comienza en el directorio de trabajo. Esta es  la carpeta local en nuestras computadoras donde abrimos, editamos y guardamos los archivos de manera normal. 

Una vez que realizamos cambios en este directorio, no se guardan automáticamente en el historial. Primero debemos pasarlos al área de preparación. En esta etapa seleccionamos específicamente qué modificaciones queremos incluir en nuestro próximo guardado 
Para enviar un archivo a esta zona usamos el comando ``` git add nombre_archivo ``` , o si queremos agregar todos los cambios modificados de una sola vez, utilizamos  ``` git add ```  ..

Cuando ya tenemos los archivos listados en el área de preparación, el siguiente paso es registrarlos en el repositorio local. Al ejecutar el comando  ```  git commit -m  "Descripción del cambio" ```  , lo que se hacemos es como tener un historial de cambios interno del Git dentro de nuestra computadora, esto nos ayuda porque funciona como un punto de restauración de nuestro trabajo.

Finalmente, para que el resto del equipo pueda ver los avances o para tener un respaldo en la nube, enviamos este historial local al repositorio remoto. Utilizando el comando ```  git push  ```  , todos los commits que guardamos en la computadora se sincronizan y se suben a la plataforma de GitHub.

# Flujo de trabajo utilizado
Durante el desarrollo de la sesión, aplicamos estas etapas teóricas de forma constante. Antes de registrar cualquier modificación, comprobamos el estado del proyecto con el  comando  ``` git status ``` . Esto nos resultó bastante útil porque nos permite identificar de manera clara qué archivos hemos modificado, cuáles son totalmente nuevos (y Git todavía no los rastrea) y cuáles ya están preparados para el commit.

Después de modificar nuestros archivos y verificar su estado, el flujo estándar que seguimos consistió en agregar los cambios con  ``` git add . ``` .Luego, procedimos a empaquetarlos en una nueva versión ejecutando  ``` git commit -m "Actualización del informe Lab01"  ```  , asegurándonos siempre de dejar un mensaje claro. Como último paso de esta rutina, utilizamos ```  git push  ```   para sincronizar nuestro repositorio local con GitHub, logrando que nuestro trabajo en la nube quedara completamente actualizado.
Por otro lado, también aprendimos que se puede realizar exactamente este mismo flujo de trabajo utilizando  la interfaz gráfica de Visual Studio Code. En lugar de ejecutar git status,  nos dirigimos al panel lateral izquierdo y hacemos clic en el ícono de Source Control (Control de código fuente). En este panel, el editor nos muestra de forma automática y visual una lista con todos los archivos que han sido modificados, agregados o eliminados, cumpliendo con la misma función de diagnóstico inicial.

Luego respecto al área de preparación, en lugar de usar el comando git add ., solo pasamos el cursor sobre la lista de cambios y hacemos clic en el ícono del símbolo + (Stage All Changes). Esto mueve nuestros archivos a la sección de cambios preparados. A continuación, reemplazamos el comando del commit escribiendo nuestro mensaje descriptivo (como "Actualización del informe Lab01") directamente en la caja de texto superior y presionando el botón Commit. Como último paso, para sustituir el git push, simplemente hacemos clic en el botón azul Sync Changes (Sincronizar cambios) que aparece en el mismo panel. 


--- 


# Uso de GitHub como repositorio remoto

GitHub permite almacenar el proyecto de forma remota y mantener una estructura organizada de archivos y directorios en el cual se puede añadir a más personas para un trabajo colaborativo. 
En la sesión se comentó que es muy importante tener un archivo  `README.md` que sirva de documentación de nuestro repositorio. 
Por ejemplo:

* `Software/README.md` : librerías, dependencias y funcionamiento del software.
* `Hardware/README.md` : componentes y características técnicas.
* `Laboratorios/Lab01/README.md` : documentación del laboratorio.
* `README.md` principal :  descripción general del proyecto o curso.

---

# Markdown para documentación técnica

Respecto al lenguaje Markdown utiliza símbolos sencillos para generar documentos estructurados. Por ejemplo, si queremos escribir con algún detalle que resalte lo que mencionamos en el texto podemos usar: 
` **texto en negrita** `
` *texto en cursiva :)* `
Y se vería de esta forma: 
 **hola mundo**
 *Mejoras del lab1* 
 --- 
 Por otro lado, si queremos organizar la cabecera del documento podemos usar: 
 `código en línea`
` # Título principal`
` ## Encabezado`
` ### Sección`
` #### Subsección ` 
Y nos daría como resultado esta organización: 
# Título principal
## Encabezado
### Sección
#### Subsección
---
# Buenas prácticas aprendidas

Durante el laboratorio se identificaron algunas prácticas importantes:

* Realizar `git status` antes de crear un commit.
* Escribir mensajes de commit cortos pero descriptivos.
* Evitar subir archivos innecesarios al repositorio.
* Mantener una estructura clara de carpetas.
* Utilizar rutas relativas para imágenes almacenadas en GitHub.
* Incorporar imágenes o GIF cuando se documenta un procedimiento.
* Realizar sincronizaciones frecuentes con el repositorio remoto.

# Conclusiones

Git, GitHub, Visual Studio Code y Markdown constituyen un conjunto de herramientas complementarias para el desarrollo organizado de proyectos tecnológicos.

**Git** permite mantener un historial controlado de cambios, mientras que **GitHub** facilita el almacenamiento remoto y el trabajo colaborativo. Por otro lado, **VS Code** se encarga de la edición y gestión del proyecto, y **Markdown** permite mantener documentación técnica ligera, estructurada y directamente integrada al repositorio.

En Ingeniería Biomédica, esta metodología resulta importante debido a que los proyectos suelen integrar diferentes componentes como hardware, software, procesamiento de datos y documentación experimental que deben mantenerse organizados y ser reproducibles.

El laboratorio permitió establecer un flujo de trabajo que podrá utilizarse durante el curso para documentar progresivamente los futuros desarrollos y mantener un historial claro de su evolución.

---

#  Referencias y recursos

* Meza, M. *Getting Started with Git and GitHub: From Zero to Teamwork*.
* Meza, M. *VS Code and Markdown: A Perfect Combination*.
* [Git](https://git-scm.com/)
* [GitHub](https://github.com/)
* [Visual Studio Code](https://code.visualstudio.com/)

---

<p align="center">
  🧬 <strong>Ingeniería Biomédica</strong><br>
  Laboratorio 01 — Control de versiones y documentación
</p>
