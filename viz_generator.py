import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from functools import reduce
from tqdm import tqdm


def read_and_rename_csv(file_path):
    """
    Reads random walk files from disk and properly names index column
    :param file_path: Path to file.
    :type file_path: str
    :return: Processed dataframe.
    :rtype: pandas Dataframe
    """
    df = pd.read_csv(file_path)
    df.rename(columns={"Unnamed: 0": "index"}, inplace=True)
    df["eig_cent_scaled"] = df["eig_cent"] * 1000000
    return df


def merge_dataframes(df_dict):
    """
    Merges dictionary of Dataframes into a single Dataframe, based on page (outer join).
    :param df_dict: Dictionary of dataframes
    :type df_dict: dict
    :return: Merged Dataframe
    :rtype: pandas Dataframe
    """
    return reduce(
        lambda left, right: pd.merge(left, right, on="page", how="outer"),
        df_dict.values(),
    )


def create_top_month_dict(top_dict, year):
    """
    Accepts a dictionary containing Dataframes with a subset of top eigenvector centrality pages in a month of clickstream data and adds a column for the month filled with 1, indicating the presence of that page in that month. This is preparation for creating a yearly heatmap with the presence of pages over months.
    :param top_dict: Dictionary of Dataframes with pages of top eigenvector centrality for a year.
    :type top_dict: dict
    :param year: The year in which the data was observed.
    :type year: str
    :return: Dictionary of enhanced Dataframes with pages of top eigenvector centrality for a year.
    :rtype: dict
    """
    top_month_dict = {}
    for month in range(1, 13):
        key = f"top_sept11_{year}{month:02d}"
        data = top_dict.get(key, {})
        month_df = pd.DataFrame({"page": data.get("page", []), f"{month:02d}": 1})
        top_month_dict[f"month_{month:02d}"] = month_df
    return top_month_dict


# Define dates for files
start_year = 2019
end_year = 2023
missing = ["2023-12", "2023-11"]

date_list = []

for year in range(start_year, end_year + 1):
    for month in range(1, 13):
        if f"{year:04d}-{month:02d}" not in missing:
            date_string = f"{year:04d}-{month:02d}"
            date_list.append(date_string)

for date in tqdm(date_list, desc="Processing for Eig Viz"):
    # Load data
    sept11_months = dict()
    top_eigs = dict()

    file_path = f"./output/random_walks/not_uniform_prob/{date}_sept11_~uniform.csv"
    eig_data = read_and_rename_csv(file_path)
    top_5 = eig_data.nlargest(5, "eig_cent_scaled")
    bottom_5 = eig_data.nsmallest(5, "eig_cent_scaled")

    # Create eigs visualizations
    plt.figure(figsize=(12, 7))

    sns.scatterplot(eig_data, x="index", y="eig_cent_scaled")

    # Add labels
    for idx, row in top_5.iterrows():
        plt.text(
            row["index"],
            row["eig_cent_scaled"],
            f"{row['page']}",
            ha="right",
            va="bottom",
            fontsize=8,
        )

    for idx, row in bottom_5.iterrows():
        plt.text(
            row["index"],
            row["eig_cent_scaled"],
            f"{row['page']}",
            ha="right",
            va="bottom",
            fontsize=5,
        )

    # Add colors
    top_mask = eig_data["index"].isin(top_5["index"])
    bottom_mask = eig_data["index"].isin(bottom_5["index"])
    sns.scatterplot(
        x="index",
        y="eig_cent_scaled",
        data=eig_data[top_mask],
        color="#9a3324",
        label="Top 5",
    )
    sns.scatterplot(
        x="index",
        y="eig_cent_scaled",
        data=eig_data[bottom_mask],
        color="#cbcc8d",
        label="Bottom 5",
    )

    plt.grid(True, which="both")
    decimal_places = 15  # Adjust as needed
    plt.gca().yaxis.set_major_formatter(FormatStrFormatter(f"%.{decimal_places}f"))
    plt.legend()
    plt.ylabel("Eigenvalue Centrality Scaled Up by 10e6")
    plt.xlabel("Page Index")
    plt.suptitle("Eigenvalue Centrality After Random Walk", x=0.565, fontsize=14)
    plt.title(f"{date} Wikipedia Clickstream Data")
    plt.tight_layout()
    plt.savefig(f"./output/plots/eigs/{date}_eigs.pdf", format="pdf")
    plt.close()

# Create heatmaps
for year in tqdm(range(start_year, end_year + 1), desc="Processing Heatmaps"):
    sept11_months = dict()
    top_2019 = dict()

    for month in range(1, 13):
        if f"{year}-{month:02d}" not in missing:
            file_path = f"./output/random_walks/not_uniform_prob/{year}-{month:02d}_sept11_~uniform.csv"
            df = read_and_rename_csv(file_path)
            sept11_months[f"sept11_{year}{month:02d}"] = df

    for k, df in sept11_months.items():
        top = df.nlargest(5, "eig_cent")
        top_2019[f"top_{k}"] = top

    top_month_dict = create_top_month_dict(top_2019, f"{year}")
    combine_top = merge_dataframes(top_month_dict)

    # Generate viz
    plt.figure(figsize=(10, 10))
    sns.heatmap(
        combine_top.set_index("page"),
        cmap="Paired",
        cbar=False,
    )
    plt.title(f"Persistence of Pages in Top 5 ({year})")
    plt.xlabel("Month")
    plt.ylabel("Page")
    plt.tight_layout()
    plt.savefig(f"./output/plots/{year}_persist.pdf", format="pdf")
    plt.close()
