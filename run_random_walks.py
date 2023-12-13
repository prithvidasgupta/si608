import pickle
import pandas as pd
import gzip

from IPython.core.display_functions import display
from tqdm import tqdm
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import eigs
import scipy.sparse
import numpy as np


def change_prev(cell):
    if cell in [
        "other-search",
        "other-other",
        "other-external",
        "other-empty",
        "other-internal",
    ]:
        return "_excess_external_adjust_"
    return cell


def change_to_idx(cell):
    return page_idx[cell]


# Define dates for files
start_year = 2019
end_year = 2023

date_list = []

for year in range(start_year, end_year + 1):
    for month in range(1, 13):
        date_string = f"{year:04d}-{month:02d}"
        date_list.append(date_string)

for date in date_list:
    tqdm.pandas()
    dataset_tuples = []

    with open("./all_nodes.pkl", "rb") as f:
        nodes = pickle.load(f)

    with gzip.open(
        f"./data/2017-2023/clickstream-enwiki-{date}.tsv.gz", "rt", encoding="utf-8"
    ) as file:
        for line in file:
            parts = line.strip().split("\t")
            if parts[0] in nodes and parts[1] in nodes:
                dataset_tuples.append((parts[0], parts[1], parts[2], int(parts[3])))

    df = pd.DataFrame(dataset_tuples, columns=["prev", "curr", "type", "clicks"])

    df["prev"] = df["prev"].apply(change_prev)

    outflow = df.groupby("prev")["clicks"].sum().reset_index()
    inflow = df.groupby("curr")["clicks"].sum().reset_index()

    t = inflow.merge(
        outflow,
        how="left",
        left_on=["curr"],
        right_on=["prev"],
        suffixes=["_inflow", "_outflow"],
    ).fillna(0)
    t["delta"] = t["clicks_inflow"] - t["clicks_outflow"]
    net_counts = []
    for page, c_i, c_o in zip(t["prev"], t["clicks_inflow"], t["clicks_outflow"]):
        if c_i < c_o:
            net_counts.append((page, c_o))
        else:
            net_counts.append((page, c_i))

    t = pd.DataFrame(net_counts, columns=["page", "total"])

    probability_df = df.merge(t, how="left", left_on=["prev"], right_on=["page"])
    probability_df = probability_df.fillna(
        df[df["prev"] == "_excess_external_adjust_"]["clicks"].sum()
    )
    probability_df["transition_probability"] = (
        probability_df["clicks"] / probability_df["total"]
    )
    idx_page = list(
        set([*probability_df["curr"].unique(), *probability_df["prev"].unique()])
    )
    page_idx = {page: i for i, page in enumerate(idx_page)}

    probability_df["i"] = probability_df["prev"].progress_apply(change_to_idx)
    probability_df["j"] = probability_df["curr"].progress_apply(change_to_idx)

    print(type(1 - 3.341394e-09))

    pad_df = (
        probability_df.groupby("i")["transition_probability"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    pad_df["padding"] = [str(1 - p) for p in pad_df["transition_probability"]]
    s = set(pad_df["i"].unique())
    extra = [i for i in range(len(page_idx)) if i not in s]

    weight = []
    adj = []
    row = []
    col = []

    for i, j, prob in zip(
        probability_df["i"],
        probability_df["j"],
        probability_df["transition_probability"],
    ):
        row.append(i)
        col.append(j)
        weight.append(prob)
        adj.append(1)

    for i, prob in zip(pad_df["i"], pad_df["padding"]):
        if float(prob) > 0:
            row.append(i)
            col.append(page_idx["_excess_external_adjust_"])
            weight.append(float(prob))
            adj.append(1)

    for i in extra:
        row.append(i)
        col.append(page_idx["_excess_external_adjust_"])
        weight.append(1)
        adj.append(1)

    adj_matrix = csr_matrix((adj, (row, col)), shape=(len(page_idx), len(page_idx)))
    wt_matrix = csr_matrix((weight, (row, col)), shape=(len(page_idx), len(page_idx)))

    # Write to disk
    scipy.sparse.save_npz(
        f"./output/random_walks/adj_matrix/{date}_sept11.npz", adj_matrix
    )
    scipy.sparse.save_npz(
        f"./output/random_walks/wt_matrix/{date}_sept11.npz", wt_matrix
    )

    pdf = [
        1 / len(idx_page) for i in range(len(idx_page))
    ]  # initial probability uniform
    egv, egvect = eigs(wt_matrix, v0=pdf)
    prv, prank = egv[0], np.abs(egvect[:, 0]) / np.sum(np.abs(egvect[:, 0]))
    display(
        prank[page_idx["September_11_attacks"]],
        idx_page[np.argmax(prank)],
        idx_page[np.argmin(prank)],
    )

    # Write to disk
    # page_idx == index in resulting DataFrame
    eig_cents = pd.DataFrame(prank, columns=["eig_cent"])
    page_names = pd.DataFrame(idx_page, columns=["page"])
    joined_pages_eigs = page_names.join(eig_cents)
    joined_pages_eigs.to_csv(
        f"./output/random_walks/uniform_prob/{date}_sept11_uniform.csv"
    )

    pdf = np.zeros(len(page_idx))
    pdf[page_idx["September_11_attacks"]] = 1  # initial probability not uniform
    egv, egvect = eigs(wt_matrix, v0=pdf)
    prv, prank = egv[0], np.abs(egvect[:, 0]) / np.sum(np.abs(egvect[:, 0]))
    display(
        prank[page_idx["September_11_attacks"]],
        idx_page[np.argmax(prank)],
        idx_page[np.argmin(prank)],
    )

    # Write to disk
    # page_idx == index in resulting DataFrame
    eig_cents = pd.DataFrame(prank, columns=["eig_cent"])
    page_names = pd.DataFrame(idx_page, columns=["page"])
    joined_pages_eigs = page_names.join(eig_cents)
    joined_pages_eigs.to_csv(
        f"./output/random_walks/not_uniform_prob/{date}_sept11_~uniform.csv"
    )
