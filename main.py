# %% Load modules
import networkx as nx

from process_data import load_data, filter_pages, write_csv
from build_graph import build_df, build_graph
import glob
import re
from pathlib import Path


# %% Load filepaths for processing
def get_paths(directory, pattern):
    """
    Creates list of filepaths matching the given pattern in the given directory.
    :param directory: Directory containing files of interest.
    :type directory: str
    :param pattern: Pattern of filenames of interest.
    :type pattern: str
    :return: All filenames matching the given pattern in the given directory.
    :rtype: list of strings
    """
    directory_path = Path(directory)
    return directory_path.glob(pattern)


# %% Load and process data
# NOTE: In March 2023, page title changed to "Russian_invasion_of_Ukraine"
clickstream_files = get_paths("./data/", "clickstream-enwiki-*.tsv")
for file in clickstream_files:
    if file != "./data/clickstream-enwiki-2023-03.tsv":
        # Create patterns for naming file
        filename_pattern = "clickstream-enwiki-"
        name = r"clickstream-enwiki-(\d{4}-\d{2})"
        match = re.search(name, file)
        file_date = match.group(1)

        # Load and filter data for 2022_Russian_invasion_of_Ukraine
        loaded = load_data(file)
        filtered_curr = filter_pages(loaded, column="curr")
        filtered_prev = filter_pages(loaded, column="prev")
        write_csv(filtered_prev, f"./output/{file_date}_ua_prev_clickstream.csv")
        write_csv(filtered_curr, f"./output/{file_date}_ua_curr_clickstream.csv")

# %% Load and write 2023-03 RUS-UA data
ua_202303 = load_data("./data/clickstream-enwiki-2023-03.tsv")
filtered_ua202303_curr = filter_pages(
    ua_202303, column="curr", page="Russian_invasion_of_Ukraine"
)
filtered_ua202303_prev = filter_pages(
    ua_202303, column="prev", page="Russian_invasion_of_Ukraine"
)
filtered_ua202303_curr["curr"] = "2022_russian_invasion_of_ukraine"
filtered_ua202303_prev["prev"] = "2022_russian_invasion_of_ukraine"
write_csv(filtered_ua202303_prev, "./output/2023-03_ua_prev_clickstream.csv")
write_csv(filtered_ua202303_curr, "./output/2023-03_ua_curr_clickstream.csv")

# %% Build graphs
dir_path = "./output/"
path_pattern = r"????-??_ua_????_clickstream.csv"
paths = get_paths(dir_path, path_pattern)
sorted_paths = sorted(paths)
pairs = [(sorted_paths[i], sorted_paths[i + 1]) for i in range(0, len(sorted_paths), 2)]

for pair in pairs:
    date = re.sub(r"\D", "", pair[0].stem)
    output_directory = Path("./output/")
    combined_df = build_df(pair[0], pair[1])
    graph = build_graph(combined_df)
    nx.write_gml(graph, f"{output_directory}/{date}_graph.gml")
