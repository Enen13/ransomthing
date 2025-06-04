import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


### ----------------------------------------------- Weekday Attack Pattern -------------------------------------------------- ###
def get_working_days(all_dates, save_path):
    # Extract all valid discovery dates (you’ve already done this earlier)
    weekday_series = pd.Series(all_dates).dropna()
    weekday_series = weekday_series.dt.day_name()  # e.g., "Monday", "Tuesday", etc.

    # Count occurrences
    weekday_counts = weekday_series.value_counts().reindex([
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
    ], fill_value=0)

    # Normalize if you want to see proportions
    weekday_prop = weekday_counts / weekday_counts.sum() * 100

    # Plot: Attack Frequency by Weekday
    plt.figure(figsize=(10, 6))
    sns.barplot(x=weekday_counts.index, y=weekday_counts.values, 
                hue = weekday_counts.index, palette="Blues_d", legend=False)

    plt.title("Ransomware Attack Frequency by Weekday (2021–2025)", fontsize=14, weight='bold')
    plt.ylabel("Number of Attacks")
    plt.xlabel("Day of the Week")
    plt.grid(axis='y', linestyle='--', alpha=0.5)

    for i, val in enumerate(weekday_counts.values):
        plt.text(i, val + 20, str(val), ha='center', fontsize=9)
        
    # 👇 Add the percentage legend box
    percent_lines = [f"{day:<9} {pct:.1f}%" for day, pct in weekday_prop.round(2).items()]
    legend_text = "\n".join(percent_lines)

    plt.gcf().text(
        0.85, 0.82, legend_text,
        fontsize=9,
        fontfamily = "monospace",
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'),
        verticalalignment='center',
        horizontalalignment='left'
)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    # plt.show()


def get_group_working_days(df, save_path):
    df_weekday = []
    for _, row in df.iterrows():
        group = row['group_name']
        for v in row['victims']:
            date_str = v.get("Discovery Date")
            if date_str:
                date_obj = pd.to_datetime(date_str, errors="coerce")
                if not pd.isna(date_obj):
                    df_weekday.append({"Group": group, "Weekday": date_obj.day_name()})
    weekday_df = pd.DataFrame(df_weekday)

    # Count total posts per group to get top 10
    top_10_groups = weekday_df["Group"].value_counts().head(10).index.tolist()

    # Filter DataFrame
    filtered_df = weekday_df[weekday_df["Group"].isin(top_10_groups)]

    # Pivot table for heatmap
    pivot_table = filtered_df.pivot_table(
        index="Group",
        columns="Weekday",
        aggfunc="size",
        fill_value=0
    ).reindex(columns=[
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
    ])

    # Plot
    plt.figure(figsize=(10, 6))
    sns.heatmap(pivot_table, cmap="YlGnBu", annot=True, fmt="d", linewidths=0.5, cbar_kws={"label": "Post Count"})
    plt.title("Weekday Activity of Top 10 Ransomware Groups", fontsize=14, fontweight='bold')
    plt.xlabel("Day of Week")
    plt.ylabel("Threat Group")
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    # plt.show()
   