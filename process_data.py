import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display
from tqdm import tqdm


def load_data(filepath, headers=None, sep="\t", bad_lines="warn"):
    """
    Loads clickstream data and performs basic cleaning (lowercasing and dropping NaNs).
    :param bad_lines: Defines what to do when encountering a line with too many fields
    :type bad_lines: str (default: "warn")
    :param sep: Delimiter in file.
    :type sep: str
    :param headers: Column headers for file.
    :type headers: list (default: clickstream headers)
    :param filepath: Path to file.
    :type filepath: str
    :return: Cleaned data loaded from given file.
    :rtype: pandas dataframe
    """
    if headers is None:
        headers = ["prev", "curr", "type", "n"]
    clickstream = pd.read_csv(filepath, sep=sep, names=headers, on_bad_lines=bad_lines)
    cols = clickstream.columns
    for col in tqdm(cols, desc="Processing text"):
        try:
            if clickstream[col].dtype == "O":
                clickstream.loc[:, col] = clickstream[col].str.lower()
        except AttributeError as e:
            print(f"Check for non-string datatypes: {e}")
    clickstream.dropna(inplace=True)
    return clickstream


def filter_pages(data, page="2022_Russian_invasion_of_Ukraine", column="curr"):
    """
    Returns a subset of clickstreams for the specified Wikipedia article.
    :param data: Clickstream data.
    :type data: pandas Dataframe
    :param page: Title of Wikipedia page.
    :type page: str
    :param column: Name of column to search for matches.
    :type column: str
    :return: Subset of clickstream data matching desired page.
    :rtype: pandas Dataframe
    """
    filtered = data[data[column] == page.lower()]

    if "n" in filtered.columns:
        filtered = filtered.sort_values(by="n", axis=0, ascending=False)
    else:
        print("WARN: Data not sorted by clicks. Column 'n' does not exist.")
    return filtered


def visualize_n(data, x="prev", y="n", title="Number of Clicks"):
    """
    Creates matplotlib bar plot for clickstreams
    :param title: Title for plot
    :type title: str
    :param y: Column name with values for the y-axis.
    :type y: str
    :param x: Column name with values for the x-axis.
    :type x: str
    :param data: Clickstream data.
    :type data: pandas Dataframe
    :return: Plot of values
    :rtype: Matplotlib object
    """
    plt.figure(figsize=(12, 12))
    viz = plt.bar(data[x], data[y])
    plt.title(title)
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()
    return viz


def write_csv(dataframe, filepath):
    """
    Write pandas Dataframe to csv
    :param dataframe: Data to be written to disk.
    :type dataframe: pandas Dataframe
    :param filepath: Path for output file.
    :type filepath: str
    :return: None
    """
    dataframe.to_csv(filepath)


def main():
    ua_clicks202203 = load_data("./data/clickstream-enwiki-2022-03.tsv")
    filtered_uaclicks = filter_pages(ua_clicks202203)
    display(filtered_uaclicks[:20])
    display(filtered_uaclicks.describe())

    # Plot top 50 clicks to "2022 Russian Invasion of Ukraine" Wiki Page
    visualize_n(filtered_uaclicks[:50])

    # Write dataframe to disk
    write_csv(filtered_uaclicks, "./output/2022-03_ua_curr_clickstream.csv")


if __name__ == "__main__":
    main()
