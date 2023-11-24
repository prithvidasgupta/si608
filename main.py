# %%
from process_data import load_data, filter_pages, write_csv
from build_graph import build_df, build_graph
import glob
import re

# %% Process data
directory = "./data/"
pattern = "clickstream-enwiki-*.tsv"
clickstream_files = glob.glob(f"{directory}/{pattern}")

# NOTE: In March 2023, page title changed to "Russian_invasion_of_Ukraine"
for file in clickstream_files:
    if file != "clickstream-enwiki-2023-03.tsv":
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
