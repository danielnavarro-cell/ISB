Durante la clase práctica del curso **Introducción a Señales Biomédicas (ISB)** se desarrolló el flujo completo para estructurar, registrar y sincronizar el repositorio del proyecto:

**1. Configuración de Identidad y Repositorio en GitHub**

* **Configuración Local:** Se registraron el nombre de usuario y correo de GitHub en la terminal mediante `git config --global` para validar la autoría de los cambios.
* **Creación Remota:** Se creó el repositorio grupal en la plataforma de GitHub asignando el nombre oficial del grupo (`GRUPO 6-ISB-2026-11`) y marcándolo como público.



**2. Organización de la Estructura de Carpetas**

* **Jerarquía Local:** Se creó la carpeta raíz del proyecto y se armó la estructura de subcarpetas solicitada por la guía del laboratorio:


* `CITI program - certificados/`

* `Laboratorios/Lab_01/`

* `Proyecto/Hardware/` y `Proyecto/Software/`



* **Regla de Archivos:** Como Git no rastrea directorios vacíos, se crearon los archivos `.md` correspondientes (`README.md` en la raíz y `git-Github.md` en `Lab_01`) para que Git reconozca la existencia de cada carpeta.



**3. Inicialización y Vinculación Local-Remota**

* **Inicializar Repositorio:** Se ejecutó `git init` dentro de la carpeta raíz para activar el seguimiento de versiones local.
* **Asignar Rama y Remoto:** Se renombró la rama principal a `main` (`git branch -M main`) y se vinculó la carpeta local con el repositorio de GitHub mediante `git remote add origin <URL>`.



**4. Flujo de Control de Versiones y Publicación**

* **Staging y Commit:** Se verificó el estado de los archivos con `git status`, se pasaron al área de preparación con `git add .` y se registró la primera captura formal mediante `git commit -m "Estructura inicial del repositorio"`.
* **Sincronización:** Se publicaron los archivos en la nube ejecutando `git push -u origin main`.


* **Documentación Final:** Se completó la redacción del resumen técnico dentro de `Laboratorios/Lab_01/git-Github.md` y la descripción del grupo en el `README.md` principal, subiendo los cambios definitivos a GitHub. 