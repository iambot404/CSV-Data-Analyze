import io
import base64
import logging
from typing import Dict, Any, List
import pandas as pd
import numpy as np

# Force Matplotlib to use the headless Agg backend
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

# Dark / Glassmorphism visual theme for Matplotlib
STYLE_BG = "#0f172a"        # Deep slate background
STYLE_PANEL = "#1e293b"     # Card panel
STYLE_TEXT = "#e2e8f0"      # Light slate text
STYLE_MUTED = "#64748b"     # Slate muted
STYLE_CYAN = "#06b6d4"      # Vibrant cyan
STYLE_VIOLET = "#8b5cf6"    # Vibrant violet
STYLE_INDIGO = "#6366f1"    # Indigo
STYLE_BLUE = "#3b82f6"      # Electric blue
STYLE_EMERALD = "#10b981"   # Emerald

def setup_plot_theme():
    plt.rcParams.update({
        "figure.facecolor": STYLE_BG,
        "axes.facecolor": STYLE_PANEL,
        "axes.edgecolor": "#334155",
        "axes.labelcolor": STYLE_TEXT,
        "xtick.color": STYLE_MUTED,
        "ytick.color": STYLE_MUTED,
        "grid.color": "#334155",
        "grid.alpha": 0.4,
        "text.color": STYLE_TEXT,
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "Inter", "DejaVu Sans", "Helvetica", "Arial"]
    })

def fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=130, facecolor=fig.get_facecolor(), edgecolor="none")
    buf.seek(0)
    data = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return f"data:image/png;base64,{data}"

def generate_distribution_chart(df: pd.DataFrame, col: str) -> str:
    """Generates a distribution histogram with KDE curve."""
    try:
        setup_plot_theme()
        series = df[col].dropna()
        if series.empty:
            return ""

        fig, ax = plt.subplots(figsize=(7, 3.8))
        
        # Plot histogram
        n, bins, patches = ax.hist(
            series, bins=min(25, max(8, len(series) // 10)),
            color=STYLE_CYAN, alpha=0.75, edgecolor="#0891b2", linewidth=1.2, density=True
        )
        
        # Add smooth KDE estimate if scipy or basic gaussian kernel available
        try:
            from scipy.stats import gaussian_kde
            kde = gaussian_kde(series)
            x_vals = np.linspace(series.min(), series.max(), 200)
            ax.plot(x_vals, kde(x_vals), color=STYLE_VIOLET, linewidth=2.5, label="Density Curve")
            ax.legend(facecolor=STYLE_PANEL, edgecolor="#334155", labelcolor=STYLE_TEXT, loc="upper right")
        except Exception:
            pass

        ax.set_title(f"Distribution of {col}", fontsize=13, weight="bold", color=STYLE_TEXT, pad=12)
        ax.set_xlabel(col, fontsize=10, labelpad=8)
        ax.set_ylabel("Probability Density", fontsize=10, labelpad=8)
        ax.grid(True, linestyle="--", alpha=0.3)
        
        return fig_to_base64(fig)
    except Exception as e:
        logger.error(f"Error generating distribution chart for {col}: {e}")
        plt.close("all")
        return ""

def generate_correlation_heatmap(df: pd.DataFrame, numeric_cols: List[str]) -> str:
    """Generates correlation heatmap with cyan-to-violet styling."""
    try:
        if len(numeric_cols) < 2:
            return ""

        setup_plot_theme()
        # Cap to top 8 numeric cols for legibility
        cols = numeric_cols[:8]
        corr = df[cols].corr()

        fig, ax = plt.subplots(figsize=(6.5, 5))
        cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
            "custom_cyan_violet", ["#3b82f6", "#1e1b4b", "#8b5cf6", "#06b6d4"]
        )

        cax = ax.matshow(corr, cmap=cmap, vmin=-1, vmax=1)
        fig.colorbar(cax, ax=ax, fraction=0.046, pad=0.04)

        ax.set_xticks(range(len(cols)))
        ax.set_yticks(range(len(cols)))
        ax.set_xticklabels(cols, rotation=45, ha="left", fontsize=9, color=STYLE_TEXT)
        ax.set_yticklabels(cols, fontsize=9, color=STYLE_TEXT)

        # Annotate values
        for i in range(len(cols)):
            for j in range(len(cols)):
                val = corr.iloc[i, j]
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        color="#ffffff" if abs(val) > 0.4 else STYLE_MUTED,
                        fontsize=8.5, weight="semibold")

        ax.set_title("Correlation Matrix", fontsize=13, weight="bold", color=STYLE_TEXT, pad=18)
        ax.grid(False)
        return fig_to_base64(fig)
    except Exception as e:
        logger.error(f"Error generating correlation heatmap: {e}")
        plt.close("all")
        return ""

def generate_category_bar_chart(df: pd.DataFrame, col: str) -> str:
    """Generates top categories horizontal bar chart."""
    try:
        setup_plot_theme()
        top_cats = df[col].astype(str).value_counts(dropna=True).head(7)
        if top_cats.empty:
            return ""

        fig, ax = plt.subplots(figsize=(7, 3.8))
        y_pos = np.arange(len(top_cats))
        
        # Horizontal bars
        bars = ax.barh(y_pos, top_cats.values, align="center", color=STYLE_INDIGO, alpha=0.85, edgecolor=STYLE_CYAN, linewidth=1.2)
        ax.set_yticks(y_pos)
        ax.set_yticklabels([str(label)[:25] for label in top_cats.index], fontsize=9)
        ax.invert_yaxis()
        
        # Bar annotations
        for bar in bars:
            width = bar.get_width()
            ax.text(width + (max(top_cats.values) * 0.02), bar.get_y() + bar.get_height()/2,
                    f"{int(width):,}", va="center", color=STYLE_TEXT, fontsize=8.5, weight="bold")

        ax.set_title(f"Top Categories in '{col}'", fontsize=13, weight="bold", color=STYLE_TEXT, pad=12)
        ax.set_xlabel("Frequency Count", fontsize=10, labelpad=8)
        ax.grid(True, axis="x", linestyle="--", alpha=0.3)
        return fig_to_base64(fig)
    except Exception as e:
        logger.error(f"Error generating category bar chart for {col}: {e}")
        plt.close("all")
        return ""

def generate_box_plot(df: pd.DataFrame, cols: List[str]) -> str:
    """Generates box plots for detecting distribution & outliers."""
    try:
        setup_plot_theme()
        selected_cols = cols[:4]
        if not selected_cols:
            return ""

        data_to_plot = []
        valid_labels = []
        for c in selected_cols:
            clean_s = df[c].dropna()
            if not clean_s.empty:
                data_to_plot.append(clean_s)
                valid_labels.append(c)

        if not data_to_plot:
            return ""

        fig, ax = plt.subplots(figsize=(7, 4))
        bp = ax.boxplot(
            data_to_plot, patch_artist=True, tick_labels=valid_labels,
            medianprops=dict(color=STYLE_CYAN, linewidth=2),
            boxprops=dict(facecolor=STYLE_PANEL, color=STYLE_VIOLET, linewidth=1.5),
            whiskerprops=dict(color=STYLE_MUTED, linewidth=1.2),
            capprops=dict(color=STYLE_MUTED, linewidth=1.2),
            flierprops=dict(marker='o', markersize=4, markerfacecolor=STYLE_CYAN, markeredgecolor='none')
        )

        ax.set_title("Outliers & Distribution Spread (Boxplot)", fontsize=13, weight="bold", color=STYLE_TEXT, pad=12)
        ax.grid(True, linestyle="--", alpha=0.3)
        return fig_to_base64(fig)
    except Exception as e:
        logger.error(f"Error generating box plot: {e}")
        plt.close("all")
        return ""

def build_all_charts(df: pd.DataFrame, analysis_meta: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Builds a curated collection of charts for the dataset.
    """
    charts = []
    numeric_cols = analysis_meta.get("numeric_column_names", [])
    
    # 1. Distribution for first 2 numeric columns
    for col in numeric_cols[:2]:
        img = generate_distribution_chart(df, col)
        if img:
            charts.append({
                "id": f"dist_{col}",
                "title": f"Distribution: {col}",
                "type": "distribution",
                "image_data": img
            })

    # 2. Correlation heatmap
    if len(numeric_cols) >= 2:
        img = generate_correlation_heatmap(df, numeric_cols)
        if img:
            charts.append({
                "id": "corr_matrix",
                "title": "Correlation Matrix",
                "type": "correlation",
                "image_data": img
            })

    # 3. Categorical distribution for top categorical column
    cat_cols = [c["name"] for c in analysis_meta.get("columns", []) if c["type"] == "categorical"]
    if cat_cols:
        img = generate_category_bar_chart(df, cat_cols[0])
        if img:
            charts.append({
                "id": f"cat_{cat_cols[0]}",
                "title": f"Category Breakdown: {cat_cols[0]}",
                "type": "bar",
                "image_data": img
            })

    # 4. Box plot for outliers
    if numeric_cols:
        img = generate_box_plot(df, numeric_cols)
        if img:
            charts.append({
                "id": "box_outliers",
                "title": "Outlier Detection & Quartiles",
                "type": "boxplot",
                "image_data": img
            })

    return charts
