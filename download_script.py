import subprocess
import os

WIKI_ENDPOINT = "https://dumps.wikimedia.org/other/clickstream/"


def get_clicks_data(date, directory):
    response = subprocess.run(
        ["curl", "-O", f"{WIKI_ENDPOINT}/{date}/clickstream-enwiki-{date}.tsv.gz"],
        cwd=directory,
    )
    if response.returncode == 0:
        print(f"Download success: {date}")
    else:
        print(f"{date} download failed: {response.returncode}")


def main():
    """
    Entry point for program.
    :return: None
    """

    params = [
        # "2022-07",
        # "2022-08",
        # "2022-09",
        # "2022-10",
        # "2022-11",
        # "2022-12",
        # "2023-01",
        # "2023-02",
        "2023-03",
    ]
    directory = "./data/"

    if not os.path.exists(directory):
        os.makedirs(directory)

    for date in params:
        get_clicks_data(date, directory)


if __name__ == "__main__":
    main()
