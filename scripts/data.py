from pathlib import Path
import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).parent / "data" / "data.csv"

HORAS_SUEÑO_MAP = {
    "Menos de 4.5 h": 3.5,
    "Entre 4.5 h y 6 h": 5.25,
    "Entre 6 h y 7.5 h": 6.75,
    "Entre 7.5 h y 9 h": 8.25,
    "Más de 9 h": 10.0,
}

HORAS_ESTUDIO_MAP = {
    "Entre 1 y 2": 1.5,
    "Entre 2 y 3": 2.5,
    "Entre 3 y 4": 3.5,
    "Entre 4 y 5": 4.5,
    "Entre 5 y 6": 5.5,
    "Entre 6 y 7": 6.5,
    "Más de 7": 8.0,
}

HORAS_EXTRA_ESTUDIO_MAP = {
    "Entre 1 y 2": 1.5,
    "Entre 2 y 3": 2.5,
    "Entre 4 y 5": 4.5,
    "Más de 5": 6.0,
}

EDAD_ORDEN = ["17 - 18 años", "19 - 20 años", "20 - 22 años", "Más de 22 años"]


# Carga y limpieza de datos 
@st.cache_data
def cargar_datos() -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    df = pd.read_csv(DATA_PATH)
    advertencias: list[str] = []

    df.columns = [
        "timestamp", "sexo", "edad", "horas_sueño_normal", "horas_sueño_examen",
        "promedio", "dedica_a_estudio", "horas_extra_estudio",
        "semestre", "horas_estudio_semanal", "facultad",
        "reprobó", "motivo_reprobó", "foráneo",
        "se_despierta", "recuerda_sueños", "calidad_sueño",
        "ha_recursado",
        "col_extra1", "col_extra2", "col_extra3", "col_extra4",
    ]

    df_original = df.copy()

    df.drop(columns=["col_extra1", "col_extra2", "col_extra3", "col_extra4"],
            inplace=True)

    df["timestamp"] = pd.to_datetime(df["timestamp"], dayfirst=True, errors="coerce")

    df["promedio_raw"] = df["promedio"].astype(str).str.strip()
    df["promedio_raw"] = df["promedio_raw"].str.replace("≈", "", regex=False)
    df["promedio"] = pd.to_numeric(df["promedio_raw"], errors="coerce")
    df.drop(columns=["promedio_raw"], inplace=True)

    # Detectar outliers 
    mask_outlier = df["promedio"] > 10
    if mask_outlier.any():
        n = mask_outlier.sum()
        advertencias.append(
            f"⚠️ Se encontraron **{n} valor(es) atípico(s)** en *promedio académico* "
            f"(>10, p. ej. 1198). Se marcan como datos faltantes."
        )
        df.loc[mask_outlier, "promedio"] = pd.NA

    semestre_limpio = df["semestre"].astype(str).str.strip()
    semestre_limpio = semestre_limpio.str.extract(r"^(\d+)")[0]
    df["semestre"] = pd.to_numeric(semestre_limpio, errors="coerce")
    mask_sem = df["semestre"].isna()
    if mask_sem.any():
        n = mask_sem.sum()
        advertencias.append(
            f"⚠️ Se encontraron **{n} valor(es) no numérico(s)** en *semestre* "
            f"(p. ej. 'Terminé la carrera', '3er año'). Se marcan como datos faltantes."
        )

    df["horas_sueño_normal_num"] = df["horas_sueño_normal"].map(HORAS_SUEÑO_MAP)
    df["horas_sueño_examen_num"] = df["horas_sueño_examen"].map(HORAS_SUEÑO_MAP)
    df["horas_estudio_semanal_num"] = df["horas_estudio_semanal"].map(HORAS_ESTUDIO_MAP)
    df["horas_extra_estudio_num"] = df["horas_extra_estudio"].map(HORAS_EXTRA_ESTUDIO_MAP)

    # 7. Normalizar texto en columnas categóricas
    for col in ["sexo", "reprobó", "foráneo", "ha_recursado",
                "dedica_a_estudio", "se_despierta", "recuerda_sueños"]:
        df[col] = df[col].astype(str).str.strip().str.capitalize()
        df[col] = df[col].replace({"Nan": pd.NA})

    df["facultad"] = df["facultad"].astype(str).str.strip()

    return df, df_original, advertencias


def run():
    st.title("📋 Exploración del conjunto de datos")
    st.markdown(
        "Aquí puedes explorar la tabla de respuestas ya limpia, aplicar filtros "
        "y descargar el subconjunto que te interese."
    )

    df, df_original, advertencias = cargar_datos()

    if advertencias:
        with st.expander("🔧 Notas del proceso de limpieza", expanded=True):
            for msg in advertencias:
                st.markdown(msg)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de respuestas", len(df))
    col2.metric("Promedio válido", f"{df['promedio'].notna().sum()} / {len(df)}")
    col3.metric("Semestre válido", f"{df['semestre'].notna().sum()} / {len(df)}")
    col4.metric("Facultades distintas", df["facultad"].nunique())

    st.divider()

    st.subheader("🔍 Filtros")
    f1, f2, f3 = st.columns(3)

    with f1:
        sexos = ["Todos"] + sorted(df["sexo"].dropna().unique().tolist())
        sexo_sel = st.selectbox("Sexo", sexos)

    with f2:
        edades = ["Todos"] + [e for e in EDAD_ORDEN if e in df["edad"].values]
        edad_sel = st.selectbox("Rango de edad", edades)

    with f3:
        facultades = ["Todas"] + sorted(df["facultad"].dropna().unique().tolist())
        fac_sel = st.selectbox("Facultad", facultades)

    f4, f5 = st.columns(2)
    with f4:
        reprobó_sel = st.selectbox("¿Ha reprobado?", ["Todos", "Sí", "No"])
    with f5:
        foráneo_sel = st.selectbox("¿Es foráneo?", ["Todos", "Sí", "No"])

    # Aplicar filtros
    mask = pd.Series([True] * len(df), index=df.index)
    if sexo_sel != "Todos":
        mask &= df["sexo"] == sexo_sel
    if edad_sel != "Todos":
        mask &= df["edad"] == edad_sel
    if fac_sel != "Todas":
        mask &= df["facultad"] == fac_sel
    if reprobó_sel != "Todos":
        mask &= df["reprobó"] == reprobó_sel
    if foráneo_sel != "Todos":
        mask &= df["foráneo"] == foráneo_sel

    df_filtrado = df[mask].copy()
    st.caption(f"Mostrando **{len(df_filtrado)}** de {len(df)} registros")

    st.divider()

    # Columnas a mostrar 
    COLS_DISPLAY = {
        "sexo": "Sexo",
        "edad": "Edad",
        "semestre": "Semestre",
        "facultad": "Facultad",
        "horas_sueño_normal": "Sueño normal",
        "horas_sueño_examen": "Sueño en examen",
        "promedio": "Promedio",
        "reprobó": "¿Reprobó?",
        "ha_recursado": "¿Recursado?",
        "foráneo": "Foráneo",
        "calidad_sueño": "Calidad sueño (1-10)",
    }

    df_tabla = df_filtrado[list(COLS_DISPLAY.keys())].rename(columns=COLS_DISPLAY)

    # Resaltar celdas de promedio
    def resaltar_promedio(val):
        if pd.isna(val):
            return "background-color: #fff3cd; color: #856404"
        if val < 7:
            return "background-color: #f8d7da; color: #721c24"
        if val >= 9:
            return "background-color: #d4edda; color: #155724"
        return ""

    styled = (
        df_tabla.style
        .applymap(resaltar_promedio, subset=["Promedio"])
        .format({"Promedio": lambda x: f"{x:.2f}" if pd.notna(x) else "N/D",
                 "Semestre": lambda x: str(int(x)) if pd.notna(x) else "N/D"})
    )

    st.dataframe(styled, use_container_width=True, height=420)

    # Leyenda de colores
    st.markdown(
        """
        <div style="display:flex; gap:1.5rem; font-size:0.82rem; margin-top:4px;">
            <span>🟩 Promedio ≥ 9</span>
            <span>🟥 Promedio &lt; 7</span>
            <span>🟨 Sin dato válido</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # Estadísticas rápidas del subconjunto filtrado 
    with st.expander("📊 Estadísticas del subconjunto seleccionado"):
        ec1, ec2, ec3 = st.columns(3)
        promedio_medio = df_filtrado["promedio"].mean()
        calidad_media = df_filtrado["calidad_sueño"].mean()
        sueño_media = df_filtrado["horas_sueño_normal_num"].mean()

        ec1.metric(
            "Promedio académico medio",
            f"{promedio_medio:.2f}" if pd.notna(promedio_medio) else "N/D",
        )
        ec2.metric(
            "Calidad de sueño media",
            f"{calidad_media:.1f} / 10" if pd.notna(calidad_media) else "N/D",
        )
        ec3.metric(
            "Horas de sueño normales (media)",
            f"{sueño_media:.1f} h" if pd.notna(sueño_media) else "N/D",
        )

        st.dataframe(
            df_filtrado[["promedio", "calidad_sueño",
                         "horas_sueño_normal_num", "semestre"]]
            .describe()
            .rename(columns={
                "promedio": "Promedio",
                "calidad_sueño": "Calidad sueño",
                "horas_sueño_normal_num": "Horas sueño (num)",
                "semestre": "Semestre",
            })
            .round(2),
            use_container_width=True,
        )

    st.subheader("⬇️ Descargar datos")
    csv_bytes = df_filtrado[list(COLS_DISPLAY.keys())].rename(
        columns=COLS_DISPLAY
    ).to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Descargar subconjunto como CSV",
        data=csv_bytes,
        file_name="datos_filtrados.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    run()