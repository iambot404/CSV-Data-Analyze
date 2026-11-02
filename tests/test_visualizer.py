import pandas as pd
import matplotlib.pyplot as plt
from app.visualizer import (
    generate_distribution_chart,
    generate_correlation_heatmap,
    generate_category_bar_chart,
    generate_box_plot,
    build_all_charts
)
from app.analyzer import analyze_dataframe

def test_visualizer_charts_generation():
    df = pd.DataFrame({
        "sales": [100, 200, 150, 300, 400, 250, 180, 500, 120, 310],
        "profit": [20, 45, 30, 80, 95, 50, 35, 120, 25, 70],
        "region": ["East", "West", "North", "South", "East", "West", "North", "South", "East", "West"]
    })
    meta = analyze_dataframe(df)
    charts = build_all_charts(df, meta)

    assert len(charts) >= 3
    for chart in charts:
        assert "id" in chart
        assert "title" in chart
        assert chart["image_data"].startswith("data:image/png;base64,")

    # Verify no dangling matplotlib figures in memory
    assert len(plt.get_fignums()) == 0
