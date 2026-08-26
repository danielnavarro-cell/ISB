# 🧬 Laboratorio 01 — Git, GitHub, VS Code y Markdown

<p align="center">
  <strong>Ingeniería Biomédica | Herramientas para desarrollo y documentación colaborativa</strong>
</p>

<p align="center">
  Control de versiones • Documentación técnica • Repositorios • Trabajo colaborativo
</p>

---

## 🎯 1. Objetivo del laboratorio

El objetivo de este laboratorio fue familiarizarnos con herramientas utilizadas actualmente para el **desarrollo, documentación y gestión de proyectos de ingeniería**, particularmente **Git, GitHub, Visual Studio Code y Markdown**.

Durante la sesión se configuró un entorno de trabajo que permite registrar cambios realizados sobre archivos, almacenar diferentes versiones de un proyecto, documentar procedimientos mediante archivos `README.md` y sincronizar el trabajo desarrollado localmente con un repositorio remoto en GitHub.

Estas herramientas son especialmente útiles en proyectos de Ingeniería Biomédica, donde un mismo desarrollo puede involucrar simultáneamente **software, hardware, procesamiento de señales, documentación experimental y trabajo colaborativo**.

---

# 🔄 2. Ecosistema de trabajo

Aunque Git y GitHub suelen utilizarse juntos, cumplen funciones diferentes.

| Herramienta  | Función principal                                                                                     |
| ------------ | ----------------------------------------------------------------------------------------------------- |
| **Git**      | Sistema de control de versiones que registra localmente los cambios realizados en un proyecto.        |
| **GitHub**   | Plataforma remota que permite almacenar repositorios Git y colaborar con otros usuarios.              |
| **VS Code**  | Entorno de desarrollo utilizado para editar archivos, ejecutar comandos y administrar Git.            |
| **Markdown** | Lenguaje de marcado ligero utilizado para generar documentación estructurada mediante archivos `.md`. |

Una forma simplificada de representar el entorno utilizado es:

```text
        COMPUTADORA LOCAL                         NUBE

   ┌─────────────────────┐                ┌──────────────────┐
   │      VS Code        │                │      GitHub      │
   │                     │                │                  │
   │ Código + README.md  │ ─── git push →│   Repositorio    │
   │                     │←── git pull ── │     remoto       │
   └──────────┬──────────┘                └──────────────────┘
              │
              ▼
        ┌───────────┐
        │    Git    │
        │ historial │
        │ versiones │
        └───────────┘
```

> 💡 **Idea clave:** Git controla la historia del proyecto; GitHub permite almacenar y compartir esa historia de manera remota.

---

# 💻 3. Instalación y verificación de Git

Antes de trabajar con repositorios se verificó que Git estuviera correctamente instalado.

En macOS se utilizó la Terminal:

```bash
git --version
```

Una instalación correcta devuelve una versión de Git, por ejemplo:

```text
git version 2.x.x
```

### 📸 Evidencia

<p align="center">
  <img src="images/01_git_version.png" width="700">
</p>

<p align="center">
  <em>Figura 1. Verificación de la instalación de Git desde la Terminal.</em>
</p>

---

# 👤 4. Configuración inicial de Git

Git necesita asociar los cambios realizados con un usuario. Para ello se configuraron el nombre y el correo electrónico.

```bash
git config --global user.name "Nombre Apellido"

git config --global user.email "correo@universidad.edu.pe"
```

La configuración puede verificarse utilizando:

```bash
git config --global --list
```

Esta información queda asociada posteriormente a los **commits** realizados por el usuario.

---

# 🗂️ 5. ¿Cómo funciona Git?

Git organiza los cambios de un proyecto en diferentes etapas.

```text
┌──────────────────┐
│ Working Directory│
│                  │
│ Archivos editados│
└────────┬─────────┘
         │ git add
         ▼
┌──────────────────┐
│   Staging Area   │
│                  │
│ Cambios preparados│
└────────┬─────────┘
         │ git commit
         ▼
┌──────────────────┐
│ Local Repository │
│                  │
│ Historial Git    │
└────────┬─────────┘
         │ git push
         ▼
┌──────────────────┐
│Remote Repository │
│                  │
│      GitHub      │
└──────────────────┘
```

### 🧠 Interpretación

### 1. Working Directory

Es la carpeta donde se trabaja normalmente y se modifican los archivos.

### 2. Staging Area

Permite seleccionar qué modificaciones serán incluidas en el próximo commit.

```bash
git add nombre_archivo
```

Para agregar todos los cambios:

```bash
git add .
```

### 3. Local Repository

Al realizar un commit se almacena un **snapshot o estado del proyecto** dentro del historial local de Git.

```bash
git commit -m "Descripción del cambio"
```

### 4. Remote Repository

Finalmente, los commits locales pueden enviarse al repositorio remoto almacenado en GitHub.

```bash
git push
```

---

# 🚦 6. Flujo de trabajo utilizado

Durante el laboratorio se aplicó el siguiente flujo:

```text
Modificar
   ↓
git status
   ↓
git add .
   ↓
git commit
   ↓
git push
   ↓
GitHub actualizado ✅
```

Antes de registrar un cambio es recomendable verificar el estado del repositorio:

```bash
git status
```

Este comando permite identificar:

* archivos modificados;
* archivos nuevos;
* archivos todavía no rastreados;
* archivos preparados para commit.

Después se agregan los cambios:

```bash
git add .
```

Se crea un commit:

```bash
git commit -m "Actualización del informe Lab01"
```

Y finalmente:

```bash
git push
```

---

# 🕒 7. Los commits como historial del proyecto

Un **commit** representa un punto específico dentro de la evolución del proyecto.

Por ejemplo:

```text
● Configuración inicial
│
● Creación del README
│
● Incorporación de imágenes
│
● Corrección de documentación
│
● Versión final del laboratorio
```

Para consultar este historial se utiliza:

```bash
git log
```

Una visualización más resumida se obtiene mediante:

```bash
git log --oneline
```

Y una representación útil cuando existen ramas es:

```bash
git log --oneline --graph --decorate --all
```

Esto permite identificar quién realizó cada modificación y regresar a estados anteriores del proyecto si fuera necesario.

---

# 🌿 8. Trabajo mediante ramas

Las **branches o ramas** permiten desarrollar modificaciones sin afectar directamente la versión principal del proyecto.

Una estructura típica sería:

```text
                  ●──●──● feature/documentacion
                 /
●────●────●─────●────────● main
```

Se puede crear una nueva rama mediante:

```bash
git checkout -b nombre_rama
```

Por ejemplo:

```bash
git checkout -b lab01-documentacion
```

Para regresar a `main`:

```bash
git checkout main
```

Este mecanismo resulta especialmente útil cuando diferentes integrantes trabajan simultáneamente en software, documentación o análisis de datos.

---

# ☁️ 9. GitHub como repositorio remoto

GitHub permite almacenar el proyecto de forma remota y mantener una estructura organizada de archivos y directorios.

La organización propuesta para el curso sigue aproximadamente la siguiente estructura:

```text
Repositorio/
│
├── Software/
│   └── README.md
│
├── Hardware/
│   └── README.md
│
├── ISB/
│   │
│   └── Laboratorios/
│       │
│       └── Lab01/
│           ├── README.md
│           └── images/
│
└── README.md
```

Cada `README.md` puede contener documentación correspondiente al nivel donde se encuentra.

Por ejemplo:

* `Software/README.md` → librerías, dependencias y funcionamiento del software.
* `Hardware/README.md` → componentes y características técnicas.
* `Laboratorios/Lab01/README.md` → documentación del laboratorio.
* `README.md` principal → descripción general del proyecto o curso.

Esta organización facilita la **trazabilidad, reproducibilidad y mantenimiento** del proyecto.

---

# 📝 10. Markdown para documentación técnica

Markdown utiliza símbolos sencillos para generar documentos estructurados.

## Encabezados

```markdown
# Título principal
## Subtítulo
### Sección
#### Subsección
```

## Texto

```markdown
**Texto en negrita**

*Texto en cursiva*

`código en línea`
```

Resultado:

**Texto en negrita**

*Texto en cursiva*

`código en línea`

---

## Listas

```markdown
- Git
- GitHub
- VS Code
- Markdown
```

También es posible crear listas numeradas:

```markdown
1. Editar archivo
2. Guardar cambios
3. Crear commit
4. Subir a GitHub
```

---

## Tablas

```markdown
| Herramienta | Uso |
|---|---|
| Git | Control de versiones |
| GitHub | Repositorio remoto |
| VS Code | Editor |
| Markdown | Documentación |
```

---

## Enlaces

```markdown
[Visual Studio Code](https://code.visualstudio.com/)
```

---

## Imágenes

Las imágenes pueden almacenarse dentro del propio repositorio.

Por ejemplo:

```text
Lab01/
├── README.md
└── images/
    ├── git_terminal.png
    ├── vscode.png
    └── github.png
```

Luego pueden insertarse mediante:

```markdown
![Git desde Terminal](images/git_terminal.png)
```

También se puede modificar su tamaño utilizando HTML:

```html
<p align="center">
  <img src="images/git_terminal.png" width="700">
</p>
```

---

# 🖥️ 11. Visual Studio Code + Markdown

VS Code fue utilizado como entorno principal para editar la documentación.

Para mejorar la visualización de archivos Markdown se puede instalar la extensión:

> **Markdown Preview Enhanced**

Desde:

```text
Extensions → Markdown Preview Enhanced → Install
```

### 📸 Evidencia

<p align="center">
  <img src="images/02_markdown_extension.png" width="700">
</p>

<p align="center">
  <em>Figura 2. Instalación de una extensión para visualización de Markdown.</em>
</p>

---

# 👀 12. Visualización previa del README

Una ventaja de Markdown es que el documento puede visualizarse mientras se escribe.

En VS Code:

```text
README.md → Open Preview
```

También puede utilizarse:

```text
Ctrl + Shift + V
```

En macOS:

```text
⌘ + Shift + V
```

La visualización lado a lado permite observar simultáneamente el código Markdown y el resultado final.

### 🎬 Evidencia del procedimiento

<p align="center">
  <img src="images/03_markdown_preview.gif" width="800">
</p>

<p align="center">
  <em>Figura 3. Edición y previsualización dinámica de un archivo Markdown en VS Code.</em>
</p>

---

# 🔗 13. Integración de VS Code con GitHub

VS Code incluye herramientas gráficas para administrar Git.

Desde la pestaña:

```text
Source Control
```

es posible visualizar directamente los archivos modificados.

El procedimiento utilizado puede resumirse como:

```text
Modificar archivo
      ↓
Source Control
      ↓
Stage Changes (+)
      ↓
Escribir mensaje
      ↓
Commit
      ↓
Sync Changes / Push
      ↓
GitHub
```

### 📸 Evidencia

<p align="center">
  <img src="images/04_source_control.png" width="700">
</p>

<p align="center">
  <em>Figura 4. Panel Source Control de VS Code utilizado para administrar cambios del repositorio.</em>
</p>

---

# 🌐 14. Sincronización con GitHub

Después de realizar el commit local, los cambios pueden publicarse utilizando:

```bash
git push
```

También puede hacerse directamente desde VS Code mediante:

```text
Sync Changes
```

Al ingresar posteriormente al repositorio de GitHub se puede comprobar que los archivos fueron actualizados.

### 🎬 Evidencia

<p align="center">
  <img src="images/05_push_github.gif" width="800">
</p>

<p align="center">
  <em>Figura 5. Sincronización de los cambios locales con el repositorio remoto de GitHub.</em>
</p>

---

# 🧪 15. Aplicación en Ingeniería Biomédica

Aunque estas herramientas provienen principalmente del desarrollo de software, su utilidad se extiende directamente a proyectos de Ingeniería Biomédica.

Por ejemplo, un mismo repositorio podría organizar:

```text
Proyecto_Biomedico/
│
├── Hardware/
│   ├── esquematicos/
│   └── README.md
│
├── Software/
│   ├── adquisicion.py
│   ├── procesamiento.py
│   └── README.md
│
├── Data/
│   └── experimentos/
│
├── Docs/
│   └── protocolo.md
│
└── README.md
```

Esto permitiría controlar simultáneamente:

* código de adquisición de señales biomédicas;
* algoritmos de procesamiento;
* configuraciones de sensores;
* características del hardware;
* documentación experimental;
* resultados;
* versiones del proyecto.

De esta manera, Git y GitHub contribuyen no solo a almacenar archivos, sino también a mejorar la **reproducibilidad y trazabilidad de un desarrollo tecnológico**.

---

# ✅ 16. Buenas prácticas aprendidas

Durante el laboratorio se identificaron algunas prácticas importantes:

* Realizar `git status` antes de crear un commit.
* Escribir mensajes de commit cortos pero descriptivos.
* Evitar subir archivos innecesarios al repositorio.
* Mantener una estructura clara de carpetas.
* Documentar cada módulo mediante archivos `README.md`.
* Utilizar rutas relativas para imágenes almacenadas en GitHub.
* Mantener actualizada la rama principal.
* Utilizar ramas para cambios experimentales o colaborativos.
* Incorporar imágenes o GIF cuando se documenta un procedimiento.
* Realizar sincronizaciones frecuentes con el repositorio remoto.

### Ejemplo de buenos commits

✅ Recomendado:

```text
Add Git installation evidence
Update Lab01 Markdown documentation
Fix repository structure diagram
Add VS Code preview GIF
```

❌ Poco descriptivo:

```text
cambio
prueba
final
final2
ahora_si_final
```

---

# 🧠 17. Principales aprendizajes

Al finalizar el laboratorio se logró comprender que estas herramientas forman parte de un mismo flujo:

```text
             DESARROLLO
                 │
                 ▼
             VS Code
                 │
       ┌─────────┴─────────┐
       ▼                   ▼
    Markdown              Git
 Documentación       Control de versiones
       │                   │
       └─────────┬─────────┘
                 ▼
               GitHub
                 │
                 ▼
        Proyecto organizado,
       trazable y colaborativo
```

Los principales aprendizajes fueron:

1. Diferenciar las funciones de **Git y GitHub**.
2. Comprender el flujo `Working Directory → Staging → Commit → Push`.
3. Crear y documentar archivos `README.md`.
4. Utilizar Markdown para generar documentación técnica.
5. Administrar cambios desde VS Code.
6. Sincronizar un repositorio local con GitHub.
7. Comprender la utilidad de commits y ramas.
8. Organizar un repositorio de forma reproducible.

---

# 🏁 18. Conclusiones

Git, GitHub, Visual Studio Code y Markdown constituyen un conjunto de herramientas complementarias para el desarrollo organizado de proyectos tecnológicos.

**Git** permite mantener un historial controlado de cambios, mientras que **GitHub** facilita el almacenamiento remoto y el trabajo colaborativo. Por otro lado, **VS Code** centraliza la edición y gestión del proyecto, y **Markdown** permite mantener documentación técnica ligera, estructurada y directamente integrada al repositorio.

En Ingeniería Biomédica, esta metodología resulta particularmente relevante debido a que los proyectos suelen integrar diferentes componentes —hardware, software, procesamiento de datos y documentación experimental— que deben mantenerse organizados y ser reproducibles.

El laboratorio permitió establecer un flujo de trabajo que podrá utilizarse durante el curso para documentar progresivamente los futuros desarrollos y mantener un historial claro de su evolución.

---

# 📚 19. Referencias y recursos

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