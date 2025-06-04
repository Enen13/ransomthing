import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

from pathlib import Path
from pprint import pprint

import config

plt.close("all")

## Data Loading; json to dataframe (if it exists, if not create a json data)
combined_path = config.COMBINED_PATH
json_dir = config.JSON_DIR
output_path = config.OUTPUT_PATH

data = []

# Try loading the pre-combined file
if combined_path.exists():
    print("✅ Combined JSON found, loading data...")
    with open(combined_path, "r", encoding="utf-8") as f:
        data = json.load(f)

else:
    print("⚠️ No combined file. Reading and merging individual JSON files...")
    for file in json_dir.glob("group_info_*.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                json_data = json.load(f)
                data.append(json_data)
        except Exception as e:
            print(f"❌ Error reading {file.name}: {e}")
    
    # Save for later use
    with open(combined_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Combined data saved to: {combined_path}")

# Create DataFrame
df = pd.DataFrame(data)
df["group_name"] = df["group_name"].apply(lambda x: x[0] if isinstance(x, list) and x else x) # ["<groupname>"] -> "groupname"

## Uncomment to observe preview
# print("✅ DataFrame preview:")
# print(df.head())

# print()
# print("-------------------------------------------------------")
# print("Columns:", "\n", f"{df.columns}")
# print()
# print("-------------------------------------------------------")
# print("Data Types:", "\n", f"{df.dtypes}")
# print()
# print("-------------------------------------------------------")
# print("Data Sample:")
# pprint(data[0])

# Refining Data (dtypes are all "objects" currently)
df["Victims count"] = pd.to_numeric(df["Victims count"], errors="coerce")
df["First discovered victims"] = pd.to_datetime(df["First discovered victims"], errors="coerce")
df["Last discovered victim"] = pd.to_datetime(df["Last discovered victim"], errors="coerce")

df["Avg Delay"] = df["Avg Delay"].replace("N/A", np.nan)
df["Avg Delay"] = df["Avg Delay"].str.extract(r'([\d.]+)').astype(float)

### ----------------------------------------------- Visualizing Top active groups ----------------------------------------------- ###
# top_groups = df.sort_values(by="Victims count", ascending=False).head(10)
# top_groups.plot.bar(x="group_name", y="Victims count", title="Top 10 Most Active Ransomware Groups")

### ----------------------------------------------- Country info ----------------------------------------------- ###
def extract_sectors(target_field):
    try:
        sectors = target_field[0].get("Top 5 Activity Sectors", {})
        return list(sectors[0].keys()) if sectors else []
    except Exception:
        return []

def extract_countries(target_field):
    try:
        countries = target_field[1].get("Top 5 Countries", {})
        return list(countries[0].keys()) if countries else []
    except Exception:
        return []

df["Targeted Sectors"] = df["Target"].apply(extract_sectors)
df["Targeted Countries"] = df["Target"].apply(extract_countries)
df.explode("Targeted Countries")["Targeted Countries"].value_counts().head(10)
df.explode("Targeted Sectors")["Targeted Sectors"].value_counts().head(10)


## -----------------------------------------------Monthly Plot------------------------------------------------------- ###

# 🧩 Aggregate all victims' discovery dates from all groups
all_dates = []

for victims_list in df["victims"]:
    if isinstance(victims_list, list):
        for v in victims_list:
            date_str = v.get("Discovery Date", None)
            if date_str:
                parsed_date = pd.to_datetime(date_str, errors="coerce")
                if not pd.isna(parsed_date):
                    all_dates.append(parsed_date)


# ⏳ Convert to monthly periods and count
date_series = pd.Series(all_dates).dt.to_period("M").value_counts().sort_index()
date_series.index = date_series.index.to_timestamp()

# 🧩 Filter for post-2021 only
filtered_series = date_series[date_series.index >= pd.Timestamp("2021-01-01")]

# 📊 Plot setup
fig, ax = plt.subplots(figsize=(13, 6))


# ✅ C. Add 3-month rolling average trendline
rolling_avg = filtered_series.rolling(3, center=True).mean()
ax.plot(
    filtered_series.index,
    rolling_avg,
    color='orange',
    linewidth=2,
    label='3-Month Avg'
)

# 🟥 Highlight top 5 spike bars with crimson, rest steelblue
top_n = 5
top_idx = filtered_series.sort_values(ascending=False).head(top_n).index
bar_colors = ['crimson' if date in top_idx else 'steelblue' for date in filtered_series.index]

# 📊 Bar plot with color emphasis
bars = ax.bar(
    filtered_series.index,
    filtered_series.values,
    width=20,
    color=bar_colors,
    label="Monthly Count"
)

# 🔢 Annotate Top Spikes: Value + Date
for i in top_idx:
    val = filtered_series[i]
    label_date = i.strftime("%Y.%m")
    ax.text(
        i, val + 25,
        f"{val}\n{label_date}",
        ha='center',
        va='bottom',
        fontsize=8,
        color='darkred'
    )

# 📉 Add horizontal mean line
mean_val = int(filtered_series.mean())
ax.axhline(mean_val, color='gray', linestyle=':', linewidth=1.2)
ax.text(
    filtered_series.index[1],
    mean_val + 10,
    f"Average: {mean_val}",
    color='gray',
    fontsize=9
)

# 🧠 Custom x-tick labels like 2021.1, 2, 3 ...
xlabels = []
last_year = None
for date in filtered_series.index:
    year = date.year
    month = date.month
    if last_year != year:
        xlabels.append(f"{year}.{month}")
        last_year = year
    else:
        xlabels.append(f"{month}")

# 👁️‍🗨️ Reduce tick density
show_every_n = 2
ax.set_xticks(filtered_series.index[::show_every_n])
ax.set_xticklabels(xlabels[::show_every_n], rotation=45)

# 🎨 Background & grid polish
ax.grid(axis='y', linestyle='--', alpha=0.5)
fig.patch.set_facecolor('whitesmoke')

# 📌 Title and Subheading
ax.set_title("Ransomware Attack Frequency (Monthly, 2021–2025)", fontsize=16, fontweight='bold')

# Axis labels, legend
ax.set_xlabel("Month")
ax.set_ylabel("Number of Victims")
ax.yaxis.get_major_locator().set_params(integer=True)
ax.legend()

plt.tight_layout()
plt.savefig("ransomware_monthly_frequency.png", dpi=300)
plt.show()

df["Targeted Countries"] = df["Target"].apply(extract_countries)

country_counts = df.explode("Targeted Countries")["Targeted Countries"].value_counts()

print(country_counts.head(15))  # Top 15 countries

# Optional: plot as bar chart
import seaborn as sns
plt.figure(figsize=(10, 5))
sns.barplot(x=country_counts.head(10).values, y=country_counts.head(10).index)
plt.title("Top 10 Most Targeted Countries by Ransomware")
plt.xlabel("Victim Count")
plt.ylabel("Country")
plt.tight_layout()
plt.show()

from collections import defaultdict
import geopandas as gpd
import pycountry
import plotly.express as px

country_weight = defaultdict(float)

def normalize_dict(d):
    total = sum(d.values())
    return {k: v / total for k, v in d.items()} if total else {}

# Accumulate weighted country frequencies
for _, row in df.iterrows():
    victim_count = row.get("Victims count", 0)
    try:
        top_countries = row["Target"][1].get("Top 5 Countries", [{}])[0]
        norm_countries = normalize_dict(top_countries)
        for country, percent in norm_countries.items():
            country_weight[country] += percent * victim_count
    except Exception as e:
        continue

# Convert to DataFrame
country_df = pd.DataFrame([
    {"Country": country, "Score": round(score, 2)}
    for country, score in country_weight.items()
])

country_df["Score"] = np.log1p(country_df["Score"])


# 🔁 Fix country naming to match ISO Alpha-3 codes
def get_iso3(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_3
    except:
        return None

country_df["ISO3"] = country_df["Country"].apply(get_iso3)
country_df = country_df.dropna(subset=["ISO3"])

# 🌍 Plot heatmap
fig = px.choropleth(
    country_df,
    locations="ISO3",
    color="Score",
    hover_name="Country",
    color_continuous_scale="Reds",
    title="🌐 Weighted Global Heatmap of Top Targeted Countries (Ransomware Groups)"
)

fig.update_geos(showcountries=True, showframe=False, showcoastlines=True)
fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
fig.show()
fig.write_html("heatmap_ransomware.html")
