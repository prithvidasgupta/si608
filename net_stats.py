import networkx as nx
import pandas as pd
from tqdm import tqdm

# Define dates for files
start_year = 2019
end_year = 2023
missing = ["2023-12", "2023-11"]

date_list = []
stats_list = []

for year in range(start_year, end_year + 1):
    for month in range(1, 13):
        if f"{year:04d}-{month:02d}" not in missing:
            date_string = f"{year:04d}-{month:02d}"
            date_list.append(date_string)

for date in tqdm(date_list, desc="Processing Stats"):
    wiki_net_data = pd.read_csv(
        f"./output/random_walks/probability_dfs/{date}_sept11_probability.csv"
    )

    # Build graph
    wiki_net = nx.DiGraph()
    for index, row in wiki_net_data.iterrows():
        wiki_net.add_edge(row["prev"], row["curr"], weight=row["clicks"])

    # Calculate stats
    h, a = nx.hits(wiki_net)

    hubs = pd.DataFrame.from_dict(h, columns=["hub_val"], orient="index")
    hubs.index.rename("page", inplace=True)
    auths = pd.DataFrame.from_dict(a, columns=["auth_val"], orient="index")
    auths.index.rename("page", inplace=True)
    hubs_sorted = hubs.sort_values(by="hub_val", ascending=False)
    auths_sorted = auths.sort_values(by="auth_val", ascending=False)
    hubs_sorted.to_csv(f"./output/topology/{date}_hubs.csv")
    auths_sorted.to_csv(f"./output/topology/{date}_auths.csv")

    num_nodes = nx.number_of_nodes(wiki_net)
    num_edges = nx.number_of_edges(wiki_net)
    weak_connected = nx.is_weakly_connected(wiki_net)
    strong_connected = nx.is_strongly_connected(wiki_net)
    density = nx.density(wiki_net)
    degree_assort = nx.degree_assortativity_coefficient(wiki_net)

    stats = pd.DataFrame(
        {
            "num_nodes": num_nodes,
            "num_edges": num_edges,
            "weakly_connect": weak_connected,
            "strong_connect": strong_connected,
            "density": density,
            "degree_assort": degree_assort,
        },
        index=["2019-01"],
    )
    stats_list.append(stats)

combined_stats = pd.concat(stats_list)
combined_stats.to_csv("./output/topology/network_stats")
