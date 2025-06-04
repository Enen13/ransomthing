from data_loader import load_combined_json
from processor import build_dataframe
from visualization.monthly_plot import extract_discovery_dates, generate_monthly_series, plot_monthly_series
from visualization.country_barplot import plot_top_countries
from visualization.heatmap_geo import plot_geo_heatmap
from visualization.weekdays import get_group_working_days, get_working_days
from pathlib import Path
from datetime import datetime

from config import OUTPUT_PATH

save_path = OUTPUT_PATH
timestamp = datetime.now().strftime("%Y%m%d_%H%M")

def main():
    data = load_combined_json()
    df = build_dataframe(data)
    dates = extract_discovery_dates(df)
    monthly = generate_monthly_series(dates)
    
    plot_monthly_series(monthly, save_path=Path(save_path/f"ransomware_monthly_frequency_{timestamp}.png"))
    get_working_days(dates, save_path=Path(save_path/f"weekday_attack_distribution_{timestamp}.png"))
    get_group_working_days(df, save_path=Path(save_path/f"activity_Ransomware_Groups_{timestamp}.png"))
    
    plot_geo_heatmap(df, save_path=Path(save_path/"heatmap_ransomware.html"))
    plot_top_countries(df, save_path=Path(save_path/f"Top_10_countries_attacked_{timestamp}.png"))


if __name__ == "__main__":
    main()