"""
Página 3 – Matriz de Correlación (Spearman)
"""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats
from itertools import combinations

# ── Paleta (consistente con visualizaciones.py) ────────────────────────────────
C_POS     = "#4C6EF5"   # azul – correlación positiva
C_NEG     = "#F03E3E"   # rojo – correlación negativa
C_ZERO    = "#F8F9FA"   # casi blanco – sin correlación
C_TEXT    = "#212529"
C_GRID    = "#DEE2E6"
C_ACCENT  = "#F76707"

# ── Variables numéricas disponibles ───────────────────────────────────────────
VARS_NUM = {
    "Promedio":             "promedio",
    "Calidad sueño":        "calidad_sueño",
    "Semestre":             "semestre",
    "Sueño normal (h)":     "horas_sueño_normal_num",
    "Sueño examen (h)":     "horas_sueño_examen_num",
    "Estudio semanal (h)":  "horas_estudio_semanal_num",
    "Extra estudio (h)":    "horas_extra_estudio_num",
}

# ── Colormap divergente personalizado ─────────────────────────────────────────
CMAP = mcolors.LinearSegmentedColormap.from_list(
    "corr_cmap", [C_NEG, C_ZERO, C_POS]
)


def _sig(p: float) -> str:
    if p < 0.001: return "***"
    if p < 0.01:  return "**"
    if p < 0.05:  return "*"
    return ""


def calcular_matriz(df: pd.DataFrame, cols: list[str]):
    """Devuelve (rho_df, pval_df) con correlaciones Spearman por pares."""
    n = len(cols)
    rho_arr  = np.ones((n, n))
    pval_arr = np.zeros((n, n))

    for i, j in combinations(range(n), 2):
        sub = df[[cols[i], cols[j]]].dropna()
        if len(sub) < 4:
            rho_arr[i, j] = rho_arr[j, i] = np.nan
            pval_arr[i, j] = pval_arr[j, i] = np.nan
        else:
            r, p = stats.spearmanr(sub[cols[i]], sub[cols[j]])
            rho_arr[i, j]  = rho_arr[j, i]  = r
            pval_arr[i, j] = pval_arr[j, i] = p

    labels = [k for k, v in VARS_NUM.items() if v in cols]
    rho_df  = pd.DataFrame(rho_arr,  index=labels, columns=labels)
    pval_df = pd.DataFrame(pval_arr, index=labels, columns=labels)
    return rho_df, pval_df


def plot_heatmap(rho_df: pd.DataFrame, pval_df: pd.DataFrame,
                 mostrar_sig: bool, triangulo: bool) -> plt.Figure:
    n = len(rho_df)
    fig, ax = plt.subplots(figsize=(n * 1.05 + 1.2, n * 1.05 + 0.6),
                           facecolor="none")
    ax.set_facecolor("none")

    data = rho_df.values.copy()
    mask = np.zeros_like(data, dtype=bool)
    if triangulo:
        mask[np.triu_indices_from(mask, k=1)] = True
        data[mask] = np.nan

    im = ax.imshow(data, cmap=CMAP, vmin=-1, vmax=1, aspect="auto")

    # Etiquetas de ejes
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(rho_df.columns, rotation=40, ha="right",
                       fontsize=9, color=C_TEXT)
    ax.set_yticklabels(rho_df.index, fontsize=9, color=C_TEXT)

    # Valores en celdas
    for i in range(n):
        for j in range(n):
            if triangulo and j > i:
                continue
            val = rho_df.values[i, j]
            if np.isnan(val):
                continue
            p   = pval_df.values[i, j]
            sig = _sig(p) if mostrar_sig else ""
            txt = f"{val:.2f}{sig}" if i != j else "1"
            color_txt = "white" if abs(val) > 0.55 else C_TEXT
            ax.text(j, i, txt, ha="center", va="center",
                    fontsize=8.5, color=color_txt, fontweight="bold" if i == j else "normal")

    # Colorbar
    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.03)
    cbar.ax.tick_params(labelsize=8, colors=C_TEXT)
    cbar.set_label("ρ Spearman", fontsize=9, color=C_TEXT)

    # Bordes de celda
    for i in range(n):
        for j in range(n):
            if triangulo and j > i:
                continue
            ax.add_patch(plt.Rectangle(
                (j - 0.5, i - 0.5), 1, 1,
                fill=False, edgecolor=C_GRID, linewidth=0.5
            ))

    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.tight_layout()
    return fig


def plot_burbujas(rho_df: pd.DataFrame, pval_df: pd.DataFrame,
                  mostrar_sig: bool) -> plt.Figure:
    """Vista alternativa: círculos proporcionales al |ρ|."""
    n = len(rho_df)
    fig, ax = plt.subplots(figsize=(n * 1.1 + 1, n * 1.0 + 0.5),
                           facecolor="none")
    ax.set_facecolor("none")
    ax.set_xlim(-0.5, n - 0.5)
    ax.set_ylim(-0.5, n - 0.5)
    ax.invert_yaxis()

    norm = mcolors.Normalize(vmin=-1, vmax=1)
    sm   = plt.cm.ScalarMappable(cmap=CMAP, norm=norm)
    sm.set_array([])

    for i in range(n):
        for j in range(i + 1):         # triángulo inferior + diagonal
            val = rho_df.values[i, j]
            if np.isnan(val):
                continue
            p      = pval_df.values[i, j]
            color  = CMAP(norm(val))
            radius = abs(val) * 0.45 if i != j else 0.45
            circle = plt.Circle((j, i), radius, color=color, alpha=0.85)
            ax.add_patch(circle)
            if mostrar_sig and i != j:
                sig = _sig(p)
                if sig:
                    txt_c = "white" if abs(val) > 0.5 else C_TEXT
                    ax.text(j, i, sig, ha="center", va="center",
                            fontsize=7, color=txt_c)

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(rho_df.columns, rotation=40, ha="right",
                       fontsize=9, color=C_TEXT)
    ax.set_yticklabels(rho_df.index, fontsize=9, color=C_TEXT)
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.grid(color=C_GRID, linewidth=0.4)

    fig.colorbar(sm, ax=ax, fraction=0.035, pad=0.03,
                 label="ρ Spearman").ax.tick_params(labelsize=8, colors=C_TEXT)
    fig.tight_layout()
    return fig


def tabla_pares(rho_df: pd.DataFrame, pval_df: pd.DataFrame) -> pd.DataFrame:
    """Tabla larga con todos los pares ordenados por |ρ| descendente."""
    rows = []
    cols = rho_df.columns.tolist()
    for i, j in combinations(range(len(cols)), 2):
        r = rho_df.values[i, j]
        p = pval_df.values[i, j]
        rows.append({
            "Variable A":     cols[i],
            "Variable B":     cols[j],
            "ρ Spearman":     round(r, 4),
            "p-valor":        round(p, 4),
            "Significancia":  _sig(p) or "ns",
            "|ρ|":            round(abs(r), 4),
        })
    return (pd.DataFrame(rows)
              .sort_values("|ρ|", ascending=False)
              .drop(columns=["|ρ|"])
              .reset_index(drop=True))


# ── Página principal ───────────────────────────────────────────────────────────
def run():
    from data import cargar_datos
    df, _, _ = cargar_datos()

    st.title("Matriz de Correlación")
    st.markdown(
        "Se usa el coeficiente de **Spearman ρ** — robusto ante no normalidad "
        "y apropiado para variables ordinales como calidad de sueño."
    )

    # ── Controles ─────────────────────────────────────────────────────────────
    cc1, cc2, cc3, cc4 = st.columns([3, 1, 1, 1])

    with cc1:
        vars_sel = st.multiselect(
            "Variables a incluir",
            options=list(VARS_NUM.keys()),
            default=list(VARS_NUM.keys()),
        )
    with cc2:
        vista = st.radio("Vista", ["Heatmap", "Burbujas"], horizontal=False)
    with cc3:
        mostrar_sig = st.toggle("Significancia", value=True)
    with cc4:
        triangulo = st.toggle("Solo triángulo", value=False,
                              disabled=(vista == "Burbujas"))

    if len(vars_sel) < 2:
        st.warning("Selecciona al menos dos variables.")
        return

    cols_sel = [VARS_NUM[v] for v in vars_sel]
    rho_df, pval_df = calcular_matriz(df, cols_sel)

    # ── Figura principal ───────────────────────────────────────────────────────
    if vista == "Heatmap":
        fig = plot_heatmap(rho_df, pval_df, mostrar_sig, triangulo)
    else:
        fig = plot_burbujas(rho_df, pval_df, mostrar_sig)

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    # ── Leyenda de significancia ───────────────────────────────────────────────
    if mostrar_sig:
        st.caption("\\*** p<0.001  \\*\\* p<0.01  \\* p<0.05  (sin asterisco = ns)")

    st.divider()

    # ── Tabla de pares ─────────────────────────────────────────────────────────
    with st.expander("Tabla de correlaciones por par (ordenada por |ρ|)"):
        tbl = tabla_pares(rho_df, pval_df)

        def color_rho(val):
            if abs(val) >= 0.7: return "background-color:#d0ebff; color:#1864ab"
            if abs(val) >= 0.4: return "background-color:#fff3bf; color:#5c4000"
            return ""

        def color_sig(val):
            if val in ("***", "**"): return "color:#2f9e44; font-weight:bold"
            if val == "*":           return "color:#f76707"
            return "color:#adb5bd"

        styled = (
            tbl.style
            .applymap(color_rho,  subset=["ρ Spearman"])
            .applymap(color_sig,  subset=["Significancia"])
            .format({"ρ Spearman": "{:.4f}", "p-valor": "{:.4f}"})
        )
        st.dataframe(styled, use_container_width=True, hide_index=True)
        st.caption("🔵 |ρ| ≥ 0.7 correlación fuerte · 🟡 |ρ| ≥ 0.4 moderada")

    # ── Alerta de multicolinealidad ────────────────────────────────────────────
    cols_labels = list(rho_df.columns)
    fuertes = []
    for i, j in combinations(range(len(cols_labels)), 2):
        r = rho_df.values[i, j]
        if abs(r) >= 0.7:
            fuertes.append(
                f"**{cols_labels[i]}** ↔ **{cols_labels[j]}** (ρ = {r:.2f})"
            )

    if fuertes:
        with st.expander("Posible multicolinealidad (|ρ| ≥ 0.7)"):
            st.markdown(
                "Los siguientes pares tienen correlación alta. "
                "Considera incluir solo uno de cada par en el modelo de regresión:"
            )
            for par in fuertes:
                st.markdown(f"- {par}")


if __name__ == "__main__":
    run()