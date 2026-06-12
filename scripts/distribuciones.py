"""
Página 2 – Distribuciones y Dispersión
Requiere que cargar_datos() esté disponible (importada desde data_explorer.py
o definida en un módulo compartido utils.py).
"""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats

# ── Paleta ────────────────────────────────────────────────────────────────────
C_PRIMARY   = "#4C6EF5"   # azul índigo – histogramas / puntos
C_ACCENT    = "#F76707"   # naranja – línea de tendencia / KDE accent
C_NEUTRAL   = "#E9ECEF"   # gris claro – fondos de figura
C_TEXT      = "#212529"
C_GRID      = "#DEE2E6"
C_LOW       = "#F03E3E"   # promedio bajo  (<7)
C_MID       = "#4C6EF5"   # promedio medio
C_HIGH      = "#2F9E44"   # promedio alto  (≥9)

# ── Variables disponibles ──────────────────────────────────────────────────────
VARS_NUM = {
    "Promedio académico":        "promedio",
    "Calidad de sueño (1-10)":   "calidad_sueño",
    "Semestre":                  "semestre",
    "Horas de sueño (normal)":   "horas_sueño_normal_num",
    "Horas de sueño (examen)":   "horas_sueño_examen_num",
    "Horas de estudio semanal":  "horas_estudio_semanal_num",
    "Horas extra de estudio":    "horas_extra_estudio_num",
}

VARS_COLOR = {
    "Ninguna":           None,
    "Sexo":              "sexo",
    "¿Reprobó?":         "reprobó",
    "¿Es foráneo?":      "foráneo",
    "¿Ha recursado?":    "ha_recursado",
}

# Paleta para variables categóricas de color
CAT_COLORS = ["#4C6EF5", "#F76707", "#2F9E44", "#E64980", "#7950F2"]

# ── Helpers de estilo ──────────────────────────────────────────────────────────
def _base_fig(w=7, h=4):
    fig, ax = plt.subplots(figsize=(w, h), facecolor="none")
    ax.set_facecolor("none")
    ax.tick_params(colors=C_TEXT, labelsize=9)
    for spine in ax.spines.values():
        spine.set_color(C_GRID)
    ax.grid(axis="y", color=C_GRID, linewidth=0.7, linestyle="--")
    ax.grid(axis="x", visible=False)
    return fig, ax


def _label(col: str) -> str:
    return {v: k for k, v in VARS_NUM.items()}.get(col, col)


# ── Gráfico: Histograma + KDE ──────────────────────────────────────────────────
def plot_histograma(df: pd.DataFrame, col: str, bins: int,
                    color_col: str | None, mostrar_kde: bool) -> plt.Figure:
    serie = df[col].dropna()
    fig, ax = _base_fig(7, 4)

    if color_col is None or color_col not in df.columns:
        ax.hist(serie, bins=bins, color=C_PRIMARY, edgecolor="white",
                linewidth=0.5, alpha=0.85, label=_label(col))
        if mostrar_kde and len(serie) > 5:
            kde = stats.gaussian_kde(serie)
            xs  = np.linspace(serie.min(), serie.max(), 300)
            ax2 = ax.twinx()
            ax2.plot(xs, kde(xs), color=C_ACCENT, linewidth=2)
            ax2.set_ylabel("Densidad", fontsize=9, color=C_ACCENT)
            ax2.tick_params(axis="y", colors=C_ACCENT, labelsize=8)
            ax2.set_facecolor("none")
            for sp in ax2.spines.values():
                sp.set_color(C_GRID)
            ax2.grid(visible=False)
    else:
        cats = sorted(df[color_col].dropna().unique())
        for i, cat in enumerate(cats):
            sub = df.loc[df[color_col] == cat, col].dropna()
            color = CAT_COLORS[i % len(CAT_COLORS)]
            ax.hist(sub, bins=bins, color=color, edgecolor="white",
                    linewidth=0.5, alpha=0.7, label=str(cat))
            if mostrar_kde and len(sub) > 5:
                kde = stats.gaussian_kde(sub)
                xs  = np.linspace(sub.min(), sub.max(), 300)
                ax.plot(xs, kde(xs) * len(sub) * (serie.max() - serie.min()) / bins,
                        color=color, linewidth=1.5)
        ax.legend(fontsize=8, framealpha=0.3)

    ax.set_xlabel(_label(col), fontsize=10, color=C_TEXT)
    ax.set_ylabel("Frecuencia", fontsize=10, color=C_TEXT)
    fig.tight_layout()
    return fig


# ── Gráfico: Boxplot por categoría ────────────────────────────────────────────
def plot_boxplot(df: pd.DataFrame, col: str, color_col: str | None) -> plt.Figure:
    fig, ax = _base_fig(7, 4)

    if color_col is None or color_col not in df.columns:
        data = [df[col].dropna().values]
        bp = ax.boxplot(data, patch_artist=True, widths=0.4,
                        medianprops=dict(color=C_ACCENT, linewidth=2))
        bp["boxes"][0].set_facecolor(C_PRIMARY)
        bp["boxes"][0].set_alpha(0.7)
        ax.set_xticks([1])
        ax.set_xticklabels([_label(col)])
    else:
        cats  = sorted(df[color_col].dropna().unique())
        data  = [df.loc[df[color_col] == c, col].dropna().values for c in cats]
        bp    = ax.boxplot(data, patch_artist=True, widths=0.5,
                           medianprops=dict(color=C_ACCENT, linewidth=2))
        for patch, color in zip(bp["boxes"], CAT_COLORS):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        ax.set_xticks(range(1, len(cats) + 1))
        ax.set_xticklabels([str(c) for c in cats], fontsize=9)
        ax.set_xlabel(VARS_COLOR.get(color_col, color_col) or "", fontsize=10,
                      color=C_TEXT)

    ax.set_ylabel(_label(col), fontsize=10, color=C_TEXT)
    fig.tight_layout()
    return fig


# ── Gráfico: Dispersión ───────────────────────────────────────────────────────
def plot_dispersion(df: pd.DataFrame, x_col: str, y_col: str,
                    color_col: str | None, mostrar_tendencia: bool) -> plt.Figure:
    fig, ax = _base_fig(7, 4.5)
    sub = df[[x_col, y_col]].copy()
    if color_col and color_col in df.columns:
        sub[color_col] = df[color_col]

    sub = sub.dropna(subset=[x_col, y_col])

    if color_col is None or color_col not in df.columns:
        ax.scatter(sub[x_col], sub[y_col], color=C_PRIMARY,
                   alpha=0.55, edgecolors="white", linewidth=0.4, s=45)
        if mostrar_tendencia and len(sub) > 3:
            m, b, r, p, _ = stats.linregress(sub[x_col], sub[y_col])
            xs = np.linspace(sub[x_col].min(), sub[x_col].max(), 200)
            ax.plot(xs, m * xs + b, color=C_ACCENT, linewidth=2,
                    label=f"y = {m:.2f}x + {b:.2f}   r = {r:.2f}")
            ax.legend(fontsize=8, framealpha=0.3)
    else:
        cats = sorted(sub[color_col].dropna().unique())
        for i, cat in enumerate(cats):
            ss = sub[sub[color_col] == cat]
            color = CAT_COLORS[i % len(CAT_COLORS)]
            ax.scatter(ss[x_col], ss[y_col], color=color,
                       alpha=0.6, edgecolors="white", linewidth=0.4,
                       s=45, label=str(cat))
            if mostrar_tendencia and len(ss) > 3:
                m, b, r, *_ = stats.linregress(ss[x_col], ss[y_col])
                xs = np.linspace(ss[x_col].min(), ss[x_col].max(), 200)
                ax.plot(xs, m * xs + b, color=color, linewidth=1.5,
                        linestyle="--")
        ax.legend(fontsize=8, framealpha=0.3)

    # Correlación global (Spearman)
    rho, pval = stats.spearmanr(sub[x_col], sub[y_col])
    sig = "***" if pval < 0.001 else ("**" if pval < 0.01 else ("*" if pval < 0.05 else "ns"))
    ax.set_title(f"ρ Spearman = {rho:.3f}  {sig}",
                 fontsize=9, color=C_TEXT, pad=6)

    ax.set_xlabel(_label(x_col), fontsize=10, color=C_TEXT)
    ax.set_ylabel(_label(y_col), fontsize=10, color=C_TEXT)
    fig.tight_layout()
    return fig


# ── Estadísticas descriptivas rápidas ─────────────────────────────────────────
def tabla_desc(df: pd.DataFrame, col: str) -> pd.DataFrame:
    s = df[col].dropna()
    return pd.DataFrame({
        "n":       [len(s)],
        "Media":   [round(s.mean(), 3)],
        "Mediana": [round(s.median(), 3)],
        "DE":      [round(s.std(), 3)],
        "Min":     [round(s.min(), 3)],
        "P25":     [round(s.quantile(0.25), 3)],
        "P75":     [round(s.quantile(0.75), 3)],
        "Max":     [round(s.max(), 3)],
        "CV (%)":  [round(s.std() / s.mean() * 100, 1) if s.mean() != 0 else None],
    })


# ── Página principal ───────────────────────────────────────────────────────────
def run():
    from data import cargar_datos
    df, _, _ = cargar_datos()
    st.title("Distribuciones y Dispersión")
    st.markdown(
        "Explora la forma de cada variable y las relaciones entre pares. "
        "Los controles de cada sección son independientes."
    )
    # ── Sección 1: Histograma ──────────────────────────────────────────────────
    st.header("Distribución de una variable")

    hc1, hc2, hc3, hc4 = st.columns([2, 1, 1, 1])
    with hc1:
        var_hist = st.selectbox(
            "Variable", list(VARS_NUM.keys()), key="hist_var"
        )
    with hc2:
        bins = st.slider("Bins", min_value=5, max_value=60, value=15, key="hist_bins")
    with hc3:
        color_hist_lbl = st.selectbox(
            "Color por", list(VARS_COLOR.keys()), key="hist_color"
        )
    with hc4:
        mostrar_kde = st.toggle("Curva KDE", value=True, key="hist_kde")

    col_hist     = VARS_NUM[var_hist]
    color_hist   = VARS_COLOR[color_hist_lbl]

    fig_hist = plot_histograma(df, col_hist, bins, color_hist, mostrar_kde)
    st.pyplot(fig_hist, use_container_width=True)
    plt.close(fig_hist)

    # Stats descriptivas
    with st.expander("Estadísticas descriptivas"):
        st.dataframe(tabla_desc(df, col_hist), use_container_width=True, hide_index=True)

    st.divider()

    # ── Sección 1b: Boxplot ────────────────────────────────────────────────────
    st.subheader("Distribución por grupo (boxplot)")

    bc1, bc2 = st.columns([2, 2])
    with bc1:
        var_box = st.selectbox(
            "Variable", list(VARS_NUM.keys()), key="box_var",
            index=list(VARS_NUM.keys()).index("Promedio académico")
        )
    with bc2:
        color_box_lbl = st.selectbox(
            "Agrupar por", list(VARS_COLOR.keys()), key="box_color",
            index=list(VARS_COLOR.keys()).index("¿Reprobó?")
        )

    col_box   = VARS_NUM[var_box]
    color_box = VARS_COLOR[color_box_lbl]

    fig_box = plot_boxplot(df, col_box, color_box)
    st.pyplot(fig_box, use_container_width=True)
    plt.close(fig_box)

    st.divider()

    # ── Sección 2: Dispersión ──────────────────────────────────────────────────
    st.header("Relación entre dos variables")

    dc1, dc2, dc3, dc4 = st.columns([2, 2, 2, 1])
    with dc1:
        var_x_lbl = st.selectbox(
            "Eje X", list(VARS_NUM.keys()), key="disp_x",
            index=list(VARS_NUM.keys()).index("Horas de sueño (normal)")
        )
    with dc2:
        var_y_lbl = st.selectbox(
            "Eje Y", list(VARS_NUM.keys()), key="disp_y",
            index=list(VARS_NUM.keys()).index("Promedio académico")
        )
    with dc3:
        color_disp_lbl = st.selectbox(
            "Color por", list(VARS_COLOR.keys()), key="disp_color"
        )
    with dc4:
        mostrar_tend = st.toggle("Tendencia", value=True, key="disp_tend")

    x_col      = VARS_NUM[var_x_lbl]
    y_col      = VARS_NUM[var_y_lbl]
    color_disp = VARS_COLOR[color_disp_lbl]

    if x_col == y_col:
        st.warning("Selecciona variables distintas para los ejes X e Y.")
    else:
        fig_disp = plot_dispersion(df, x_col, y_col, color_disp, mostrar_tend)
        st.pyplot(fig_disp, use_container_width=True)
        plt.close(fig_disp)

        # Tabla de correlación rápida
        with st.expander("Correlación Spearman — detalle"):
            sub = df[[x_col, y_col]].dropna()
            rho, pval = stats.spearmanr(sub[x_col], sub[y_col])
            r_lin, p_lin = stats.pearsonr(sub[x_col], sub[y_col])
            tbl = pd.DataFrame({
                "Coeficiente":  ["Spearman ρ", "Pearson r"],
                "Valor":        [round(rho, 4),   round(r_lin, 4)],
                "p-valor":      [round(pval, 4),  round(p_lin, 4)],
                "Significancia": [
                    "***" if pval  < 0.001 else ("**" if pval  < 0.01 else ("*" if pval  < 0.05 else "ns")),
                    "***" if p_lin < 0.001 else ("**" if p_lin < 0.01 else ("*" if p_lin < 0.05 else "ns")),
                ],
            })
            st.dataframe(tbl, use_container_width=True, hide_index=True)
            st.caption("*** p<0.001  ** p<0.01  * p<0.05  ns: no significativo")



if __name__ == "__main__":
    run()
    