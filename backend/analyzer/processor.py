import pandas as pd
import numpy as np
from utils import normalize_dict

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

def build_dataframe(data):
    df = pd.DataFrame(data)
    df["group_name"] = df["group_name"].apply(lambda x: x[0] if isinstance(x, list) and x else x)

    df["Victims count"] = pd.to_numeric(df["Victims count"], errors="coerce")
    df["First discovered victims"] = pd.to_datetime(df["First discovered victims"], errors="coerce")
    df["Last discovered victim"] = pd.to_datetime(df["Last discovered victim"], errors="coerce")

    df["Avg Delay"] = df["Avg Delay"].replace("N/A", np.nan)
    df["Avg Delay"] = df["Avg Delay"].str.extract(r'([\d.]+)').astype(float)

    df["Targeted Sectors"] = df["Target"].apply(extract_sectors)
    df["Targeted Countries"] = df["Target"].apply(extract_countries)

    return df