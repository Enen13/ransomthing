import matplotlib.pyplot as plt
import pandas as pd

from pathlib import Path


def extract_discovery_dates(df) -> list:
    """
    From the full DataFrame, extract all valid datetime objects from victims list.
    """
    all_dates = []
    for victims_list in df["victims"]:
        if isinstance(victims_list, list):
            for v in victims_list:
                date_str = v.get("Discovery Date", None)
                if date_str:
                    parsed_date = pd.to_datetime(date_str, errors="coerce")
                    if not pd.isna(parsed_date):
                        all_dates.append(parsed_date)
    return all_dates


def generate_monthly_series(dates, cutoff="2021-01-01") -> pd.Series:
    """
    Converts list of datetime objects into a monthly count time series.
    """
    date_series = pd.Series(dates).dt.to_period("M").value_counts().sort_index()
    date_series.index = date_series.index.to_timestamp()
    return date_series[date_series.index >= pd.Timestamp(cutoff)]


def plot_monthly_series(monthly_series: pd.Series, save_path):
    """
    Plots the time series with rolling average and highlights top 5 months.
    """
    fig, ax = plt.subplots(figsize=(13, 6))

    rolling_avg = monthly_series.rolling(3, center=True).mean()
    ax.plot(monthly_series.index, rolling_avg, color='orange', linewidth=2, label='3-Month Avg')

    top_n = 5
    top_idx = monthly_series.sort_values(ascending=False).head(top_n).index
    bar_colors = ['crimson' if date in top_idx else 'steelblue' for date in monthly_series.index]
    ax.bar(monthly_series.index, monthly_series.values, width=20, color=bar_colors, label="Monthly Count")

    for i in top_idx:
        val = monthly_series[i]
        label_date = i.strftime("%Y.%m")
        ax.text(i, val + 25, f"{val}\n{label_date}", ha='center', va='bottom', fontsize=8, color='darkred')

    mean_val = int(monthly_series.mean())
    ax.axhline(mean_val, color='gray', linestyle=':', linewidth=1.2)
    ax.text(monthly_series.index[1], mean_val + 10, f"Average: {mean_val}", color='gray', fontsize=9)

    xlabels = []
    last_year = None
    for date in monthly_series.index:
        year, month = date.year, date.month
        if last_year != year:
            xlabels.append(f"{year}.{month}")
            last_year = year
        else:
            xlabels.append(f"{month}")
    ax.set_xticks(monthly_series.index[::2])
    ax.set_xticklabels(xlabels[::2], rotation=45)

    ax.grid(axis='y', linestyle='--', alpha=0.5)
    fig.patch.set_facecolor('whitesmoke')
    ax.set_title("Ransomware Attack Frequency (Monthly, 2021–2025)", fontsize=16, fontweight='bold')
    ax.set_xlabel("Month")
    ax.set_ylabel("Number of Victims")
    ax.yaxis.get_major_locator().set_params(integer=True)
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    # plt.show()