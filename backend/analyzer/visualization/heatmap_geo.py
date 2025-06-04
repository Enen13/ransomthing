from collections import defaultdict
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

from utils import normalize_dict, get_iso3


# Geo Heatmap Function
def plot_geo_heatmap(df, save_path):
    country_weight = defaultdict(float)  # move inside for clean state

    for _, row in df.iterrows():
        victim_count = row.get("Victims count", 0)
        try:
            top_countries = row["Target"][1].get("Top 5 Countries", [{}])[0]
            norm_countries = normalize_dict(top_countries)
            for country, percent in norm_countries.items():
                country_weight[country] += percent * victim_count
        except Exception:
            continue

    # Create DataFrame
    country_df = pd.DataFrame([
        {"Country": country, "Score": round(score, 2)}
        for country, score in country_weight.items()
    ])
    country_df["Score"] = np.log1p(country_df["Score"])

    # Map to ISO3
    country_df["ISO3"] = country_df["Country"].apply(get_iso3)
    country_df = country_df.dropna(subset=["ISO3"])

    # 🌍 Plot
    fig = px.choropleth(
        country_df,
        locations="ISO3",
        color="Score",
        hover_name="Country",
        color_continuous_scale="Reds",
        title="🌐 Weighted Global Heatmap of Top Targeted Countries (Ransomware Groups)"
    )
    fig.update_geos(showcountries=True, showframe=False, showcoastlines=True)
    fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
    fig.write_html(save_path)
    # fig.show()
    