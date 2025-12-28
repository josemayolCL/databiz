"""
viz.py
Funciones de visualización con matplotlib.
Cada función devuelve un objeto Figure para usar con st.pyplot().
Tema oscuro profesional con paleta de colores vibrante.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
from typing import Optional, Tuple


DARK = {
    "bg": "#0f0f0f",
    "surface": "#1a1a1a",
    "surface2": "#242424",
    "border": "#2a2a2a",
    "text": "#fafafa",
    "text_secondary": "#a1a1aa",
    "text_muted": "#71717a",
}

ACCENT = {
    "primary": "#8b5cf6",
    "secondary": "#a78bfa",
    "cyan": "#22d3ee",
    "emerald": "#34d399",
    "amber": "#fbbf24",
    "rose": "#fb7185",
    "blue": "#60a5fa",
    "orange": "#fb923c",
}

CHART_COLORS = [
    "#8b5cf6",
    "#a78bfa",
    "#c4b5fd",
    "#22d3ee",
    "#34d399",
    "#4ade80",
    "#fbbf24",
    "#fb923c",
    "#fb7185",
    "#f472b6",
    "#60a5fa",
    "#38bdf8",
]

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial", "sans-serif"],
    "font.size": 11,
    "axes.titlesize": 15,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "axes.labelweight": "normal",
    "axes.labelcolor": DARK["text_secondary"],
    "axes.titlecolor": DARK["text"],
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "xtick.color": DARK["text_muted"],
    "ytick.color": DARK["text_muted"],
    "figure.facecolor": DARK["bg"],
    "axes.facecolor": DARK["bg"],
    "axes.grid": False,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": False,
    "axes.spines.bottom": False,
    "axes.edgecolor": DARK["border"],
    "axes.linewidth": 0,
    "grid.alpha": 0.15,
    "grid.color": DARK["text_muted"],
    "legend.frameon": False,
    "legend.fontsize": 10,
    "legend.labelcolor": DARK["text_secondary"],
    "text.color": DARK["text"],
})


def _create_gradient_colors(n: int) -> list:
    """Genera una lista de colores del gradiente."""
    if n <= len(CHART_COLORS):
        return CHART_COLORS[:n]
    return (CHART_COLORS * ((n // len(CHART_COLORS)) + 1))[:n]


def _format_number(n: int) -> str:
    """Formatea número con separador de miles chileno."""
    return f"{n:,}".replace(",", ".")


def plot_bar_regiones(
    df_agg: pd.DataFrame,
    top_n: int = 10,
    figsize: Tuple[int, int] = (10, 7)
) -> plt.Figure:
    """Barras horizontales con gradiente para establecimientos por región."""
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(DARK["bg"])
    ax.set_facecolor(DARK["bg"])
    
    if df_agg.empty:
        ax.text(0.5, 0.5, "Sin datos disponibles", 
                ha="center", va="center", transform=ax.transAxes,
                fontsize=14, color=DARK["text_muted"])
        ax.set_axis_off()
        return fig
    
    data = df_agg.head(top_n).sort_values("cantidad", ascending=True)
    n_bars = len(data)
    colors = _create_gradient_colors(n_bars)[::-1]
    
    y_pos = np.arange(n_bars)
    bars = ax.barh(
        y_pos,
        data["cantidad"],
        color=colors,
        height=0.65,
        edgecolor="none"
    )
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(data["region"], fontsize=10, color=DARK["text_secondary"])
    
    max_val = data["cantidad"].max()
    for i, (bar, val) in enumerate(zip(bars, data["cantidad"])):
        if val > max_val * 0.35:
            ax.text(
                val - max_val * 0.03,
                bar.get_y() + bar.get_height() / 2,
                _format_number(int(val)),
                ha="right", va="center",
                fontsize=10, fontweight="bold",
                color=DARK["bg"]
            )
        else:
            ax.text(
                val + max_val * 0.02,
                bar.get_y() + bar.get_height() / 2,
                _format_number(int(val)),
                ha="left", va="center",
                fontsize=10, fontweight="500",
                color=DARK["text"]
            )
    
    ax.set_xlabel("Número de Establecimientos", color=DARK["text_muted"], fontsize=10)
    ax.set_title("Distribución por Región", pad=20, fontsize=16, fontweight="bold", color=DARK["text"])
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", colors=DARK["text_muted"])
    ax.set_xlim(0, max_val * 1.12)
    
    ax.xaxis.grid(True, linestyle="-", alpha=0.1, color=DARK["text_muted"])
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    return fig


def plot_donut_tipos(
    df_agg: pd.DataFrame,
    top_n: int = 6,
    figsize: Tuple[int, int] = (10, 7)
) -> plt.Figure:
    """Gráfico de dona moderno con tema oscuro."""
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(DARK["bg"])
    ax.set_facecolor(DARK["bg"])
    
    if df_agg.empty:
        ax.text(0.5, 0.5, "Sin datos disponibles", 
                ha="center", va="center", transform=ax.transAxes,
                fontsize=14, color=DARK["text_muted"])
        ax.set_axis_off()
        return fig
    
    data = df_agg.copy()
    if len(data) > top_n:
        top_data = data.head(top_n - 1)
        otros = pd.DataFrame([{
            "tipo": "Otros",
            "cantidad": data.iloc[top_n - 1:]["cantidad"].sum()
        }])
        data = pd.concat([top_data, otros], ignore_index=True)
    
    colors = _create_gradient_colors(len(data))
    
    wedges, texts, autotexts = ax.pie(
        data["cantidad"],
        labels=None,
        autopct=lambda pct: f"{pct:.1f}%" if pct > 5 else "",
        colors=colors,
        startangle=90,
        pctdistance=0.78,
        wedgeprops=dict(width=0.5, edgecolor=DARK["bg"], linewidth=3)
    )
    
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_color(DARK["bg"])
        autotext.set_fontweight("bold")
    
    total = data["cantidad"].sum()
    centre = plt.Circle((0, 0), 0.4, fc=DARK["bg"])
    ax.add_artist(centre)
    ax.text(0, 0.06, _format_number(int(total)), ha="center", va="center", 
            fontsize=24, fontweight="bold", color=DARK["text"])
    ax.text(0, -0.12, "Total", ha="center", va="center", 
            fontsize=11, color=DARK["text_muted"])
    
    legend_labels = [t[:25] + "..." if len(t) > 25 else t for t in data["tipo"]]
    legend = ax.legend(
        wedges,
        legend_labels,
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        fontsize=10,
        frameon=False,
        labelcolor=DARK["text_secondary"]
    )
    
    ax.set_title("Tipos de Establecimiento", pad=20, fontsize=16, fontweight="bold", color=DARK["text"])
    
    plt.tight_layout()
    return fig


def plot_bar_dependencia(
    df_agg: pd.DataFrame,
    figsize: Tuple[int, int] = (10, 6)
) -> plt.Figure:
    """Barras verticales con tema oscuro."""
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(DARK["bg"])
    ax.set_facecolor(DARK["bg"])
    
    if df_agg.empty:
        ax.text(0.5, 0.5, "Sin datos disponibles", 
                ha="center", va="center", transform=ax.transAxes,
                fontsize=14, color=DARK["text_muted"])
        ax.set_axis_off()
        return fig
    
    data = df_agg.head(7)
    n_bars = len(data)
    colors = [ACCENT["cyan"], ACCENT["emerald"], ACCENT["amber"], 
              ACCENT["rose"], ACCENT["blue"], ACCENT["orange"], ACCENT["primary"]][:n_bars]
    
    labels = [d[:16] + "..." if len(d) > 16 else d for d in data["dependencia"]]
    
    x_pos = np.arange(n_bars)
    bars = ax.bar(
        x_pos,
        data["cantidad"],
        color=colors,
        width=0.6,
        edgecolor="none"
    )
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, rotation=40, ha="right", fontsize=9, color=DARK["text_secondary"])
    
    max_val = data["cantidad"].max()
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + max_val * 0.03,
            _format_number(int(height)),
            ha="center", va="bottom",
            fontsize=10, fontweight="500",
            color=DARK["text"]
        )
    
    ax.set_ylabel("Establecimientos", color=DARK["text_muted"], fontsize=10)
    ax.set_title("Dependencia Administrativa", pad=20, fontsize=16, fontweight="bold", color=DARK["text"])
    ax.tick_params(axis="y", colors=DARK["text_muted"])
    ax.set_ylim(0, max_val * 1.18)
    
    ax.yaxis.grid(True, linestyle="-", alpha=0.1, color=DARK["text_muted"])
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    return fig


def plot_top_comunas(
    df: pd.DataFrame,
    top_n: int = 12,
    figsize: Tuple[int, int] = (10, 7)
) -> plt.Figure:
    """Lollipop chart con tema oscuro."""
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(DARK["bg"])
    ax.set_facecolor(DARK["bg"])
    
    if "ComunaGlosa" not in df.columns or df.empty:
        ax.text(0.5, 0.5, "Sin datos disponibles", 
                ha="center", va="center", transform=ax.transAxes,
                fontsize=14, color=DARK["text_muted"])
        ax.set_axis_off()
        return fig
    
    counts = df.groupby("ComunaGlosa").size().reset_index(name="cantidad")
    counts = counts.sort_values("cantidad", ascending=True).tail(top_n)
    
    n_bars = len(counts)
    y_pos = np.arange(n_bars)
    colors = _create_gradient_colors(n_bars)[::-1]
    
    for i, (y, val, color) in enumerate(zip(y_pos, counts["cantidad"], colors)):
        ax.hlines(y=y, xmin=0, xmax=val, color=color, alpha=0.6, linewidth=2.5)
        ax.scatter(val, y, color=color, s=140, zorder=3, edgecolor=DARK["bg"], linewidth=2)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(counts["ComunaGlosa"], fontsize=10, color=DARK["text_secondary"])
    
    max_val = counts["cantidad"].max()
    for y, val in zip(y_pos, counts["cantidad"]):
        ax.text(
            val + max_val * 0.04,
            y,
            _format_number(int(val)),
            ha="left", va="center",
            fontsize=10, fontweight="500",
            color=DARK["text"]
        )
    
    ax.set_xlabel("Número de Establecimientos", color=DARK["text_muted"], fontsize=10)
    ax.set_title(f"Top {top_n} Comunas", pad=20, fontsize=16, fontweight="bold", color=DARK["text"])
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", colors=DARK["text_muted"])
    ax.set_xlim(0, max_val * 1.2)
    
    ax.xaxis.grid(True, linestyle="-", alpha=0.1, color=DARK["text_muted"])
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    return fig


plot_pie_tipos = plot_donut_tipos
