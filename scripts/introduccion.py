import streamlit as st

st.title("Horas de sueño y rendimiento académico")
st.markdown("""
## Introducción

Esta aplicación interactiva forma parte del proyecto de Estadística de la **Universidad Michoacana de San Nicolás de Hidalgo (UMSNH)**.  
El objetivo es analizar la **relación entre las horas de sueño y el desempeño académico** en estudiantes de nivel licenciatura.

**Hipótesis de partida:**  
Una menor cantidad de sueño nocturno se asocia con promedios académicos más bajos y un mayor número de materias reprobadas, controlando por factores como edad, semestre y calidad de sueño autopercibida.

**Objetivo principal:**  
Determinar la fuerza de correlación entre las horas de sueño y el rendimiento académico a partir de datos recolectados mediante encuestas.  
Se utilizan tablas de frecuencias, medidas de tendencia central, diagramas de dispersión y modelos de regresión para identificar patrones y evaluar si sacrificar horas de sueño para estudiar repercute significativamente en el rendimiento.

---

## ¿Qué puedes hacer en esta aplicación?

- **Cargar y explorar** el dataframe limpio (tabla dinámica con búsqueda y filtros).
- **Visualizar la matriz de correlación** con mapa de calor interactivo (tooltips con el coeficiente exacto).
- **Resultados del modelo de regresión**: ecuación estimada, tabla de coeficientes, gráficos de residuos y métricas de ajuste.
- **Comparar escenarios**: simular cambios en horas de sueño y ver su efecto en el promedio predicho.
- **Estadísticas descriptivas**: media, mediana, distribución de variables.
- **Gráficos interactivos**: histogramas, diagramas de caja, dispersión.

---

## Metodología de la encuesta

| Concepto | Descripción |
|----------|-------------|
| **Población objetivo** | Estudiantes de licenciatura de la UMSNH (≈40,000) |
| **Tamaño de muestra** | Entre 121 respuestas (mínimo aceptable) y 381 (óptimo) |
| **Técnica de muestreo** | Muestreo por conveniencia (no probabilístico) |
| **Instrumento** | Cuestionario autoaplicado |

---

## Importancia del estudio

El sueño es un estado fisiológico esencial para la reparación del cuerpo, la consolidación de la memoria y la eliminación de toxinas cerebrales.  
La falta de sueño afecta negativamente el estado de ánimo, la memoria, la toma de decisiones y la salud cardiovascular.  
Se recomienda dormir entre **7.5 y 9 horas diarias**; menos de 4.5 horas es perjudicial. Además, completar los ciclos de sueño (≈90 minutos) evita despertar con fatiga.

En el entorno universitario, es frecuente que los estudiantes reduzcan sus horas de descanso, sobre todo en épocas de exámenes o entregas, lo que puede afectar su concentración y rendimiento académico.  
Por ello, surge el interés de analizar si existe una relación entre la cantidad y calidad del sueño y el desempeño académico de los estudiantes de nuestra universidad.

---

📌 **Para más información sobre el proyecto, consulta el repositorio de GitHub:**  
[Ver repositorio →](https://github.com/Angel-Ramos-Rm/sleep-academic-performance)
""")


