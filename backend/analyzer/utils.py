import numpy as np
import pycountry

def normalize_dict(d: dict) -> dict:
    """
    Normalize the values in a dictionary to sum to 1.
    """
    total = sum(d.values())
    return {k: v / total for k, v in d.items()} if total else {}

def extract_sectors(target_field) -> list:
    """
    Extracts top activity sectors from the nested JSON target field.
    Returns a list of sector names.
    """
    try:
        sectors = target_field[0].get("Top 5 Activity Sectors", {})
        return list(sectors[0].keys()) if sectors else []
    except Exception:
        return []

def extract_countries(target_field) -> list:
    """
    Extracts top targeted countries from the nested JSON target field.
    Returns a list of country names.
    """
    try:
        countries = target_field[1].get("Top 5 Countries", {})
        return list(countries[0].keys()) if countries else []
    except Exception:
        return []

def get_iso3(country_name: str) -> str:
    """
    Converts a country name into ISO Alpha-3 country code.
    Used for mapping with plotly / geopandas.
    """
    try:
        return pycountry.countries.lookup(country_name).alpha_3
    except:
        return None

def safe_str_to_float(val) -> float:
    """
    Extracts numeric float from strings like '12.3 days' or 'N/A'.
    Returns np.nan if conversion fails.
    """
    try:
        if val == "N/A":
            return np.nan
        return float(val.strip().split()[0])
    except:
        return np.nan