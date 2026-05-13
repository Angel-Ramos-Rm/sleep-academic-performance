# Relación entre las horas de sueño y el desempeño académico en estudiantes universitarios

## Descripción

Este repositorio contiene el proyecto de investigación **"Relación entre las horas de sueño y el desempeño académico en estudiantes universitarios"**, desarrollado como parte de la asignatura de Estadística. El estudio se enfoca en estudiantes de la Universidad Michoacana de San Nicolás de Hidalgo (UMSNH).

El objetivo principal es cuantificar la correlación entre las horas de sueño y el rendimiento académico (promedio, materias reprobadas), utilizando encuestas y análisis estadístico, para determinar si reducir el sueño para estudiar afecta significativamente el desempeño.

## Herramientas y tecnologías

| Herramienta | Uso |
|-------------|-----|
| **Google Forms** | Recolección de datos |
| **Python** | Limpieza inicial y transformación de datos |
| **R** | Análisis estadístico, correlaciones y regresión lineal múltiple |
| **Quarto** | Generación del reporte final (HTML / sitio web) |
| **Streamlit** | Aplicación interactiva para explorar datos y resultados |
| **Git / GitHub** | Control de versiones y alojamiento del repositorio |

## Cómo reproducir el proyecto

### 1. Clonar el repositorio

```bash
git clone https://github.com/Angel-Ramos-Rm/sleep-academic-performance.git
cd sleep-academic-performance
```

### 2. Crear el ambiente virtual de Python e instalar dependencias

**Windows:**
```bash
cd app
python -m venv aplicacion.venv
aplicacion.venv\Scripts\activate
pip install -r requirements.txt
```

**Linux / macOS:**
```bash
cd app
python3 -m venv aplicacion.venv
source aplicacion.venv/bin/activate
pip install -r requirements.txt
```

### 3. Instalar dependencias de R

Abre R o RStudio y ejecuta:
```r
install.packages(c("tidyverse", "ggplot2", "corrplot", "knitr"))
```

### 4. Renderizar el sitio con Quarto

```bash
quarto render
```

El sitio se generará en la carpeta `docs/`.

### 5. Ejecutar la aplicación de Streamlit

Asegúrate de tener el ambiente virtual activado (paso 2), luego:

**Windows:**
```bash
aplicacion.venv\Scripts\activate
streamlit run app.py
```

**Linux / macOS:**
```bash
source aplicacion.venv/bin/activate
streamlit run app.py
```

## Resultados

El sitio web con los avances del proyecto se encuentra en:
🔗 [Angel-Ramos-Rm.github.io/sleep-academic-performance](https://Angel-Ramos-Rm.github.io/sleep-academic-performance)
