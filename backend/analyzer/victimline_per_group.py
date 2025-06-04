from main import pd, plt
from main import df, mdates


## ----------------------------------------------- Victim timeline per group------------------------------------------------------- ###
group = "0mega"
match = df[df["group_name"].str.contains(group, case=False, na=False)]


if not match.empty:
    victims = match["victims"].iloc[0]
    dates = [pd.to_datetime(v["Discovery Date"], errors="coerce") for v in victims if v["Discovery Date"]]

    # Group by month
    dates_series = pd.Series(dates).dt.to_period("M").value_counts().sort_index()
    dates_series.index = dates_series.index.to_timestamp()

    # Clean figure
    fig, ax = plt.subplots(figsize=(10, 4))

    # Bar plot
    bars = ax.bar(
        dates_series.index,
        dates_series.values,
        width=20,  # reduce width for slimmer bars
        color="cornflowerblue"
    )

    # X-axis formatting: show as "Jan", "Feb", etc.
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # %b = abbreviated month
    plt.xticks(rotation=45)

    # Y-axis to show only integers
    ax.yaxis.get_major_locator().set_params(integer=True)

    # Labels and Title
    ax.set_title(f"{group} – Monthly Victim Discovery Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Number of Victims")

    # No grid for raw integer bars
    ax.grid(False)

    plt.tight_layout()
    plt.show()

else:
    print(f"❌ Group '{group}' not found in data.")
