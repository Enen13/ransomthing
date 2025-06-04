import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path



def plot_top_countries(df, save_path):
    country_counts = df.explode("Targeted Countries")["Targeted Countries"].value_counts().head(10)
    plt.figure(figsize=(10, 5))
    sns.barplot(x=country_counts.values, y=country_counts.index)
    plt.title("Top 10 Most Targeted Countries by Ransomware")
    plt.xlabel("Victim Count")
    plt.ylabel("Country")
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    # plt.show()
    