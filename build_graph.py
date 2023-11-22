import networkx as nx
import pandas as pd
from IPython.display import display
import matplotlib.pyplot as plt


def build_df(file1, file2):
    lside = pd.read_csv(file1)
    print(len(lside))
    rside = pd.read_csv(file2)
    print(len(rside))
    return pd.concat([lside, rside])


def build_graph(df, from_node="prev", to_node="curr", weight="n"):
    g = nx.DiGraph()
    from_nodes = list(df[from_node])
    to_nodes = list(df[to_node])
    weights = list(df[weight])

    for fnode, tnode, wt in zip(from_nodes, to_nodes, weights):
        if fnode == tnode:
            print(f" WARN: self-edge {fnode, tnode}")
        g.add_edge(fnode, tnode, weight=wt)
    return g


def main():
    """
    Entry point for program.
    :return: None
    """
    # Merge files in preparation for building graph
    combined = build_df(
        "./output/2022-03_ua_curr_clickstream.csv",
        "./output/2022-03_ua_prev_clickstream.csv",
    )
    display(combined.head())
    display(combined.tail())

    # Build graph
    ua_2022_03 = build_graph(combined)
    plt.figure(figsize=(10, 10))
    nx.draw(ua_2022_03, pos=nx.spring_layout(ua_2022_03), node_size=10)
    plt.show()

    # Check graph
    in_degs = dict(ua_2022_03.in_degree)
    out_degs = dict(ua_2022_03.out_degree)
    in_node, in_degree = max(in_degs.items(), key=lambda x: x[1])
    out_node, out_degree = max(out_degs.items(), key=lambda x: x[1])
    print(f"max in degree: {(in_node, in_degree)}")
    print(f"max out degree: {out_node, out_degree}")


if __name__ == "__main__":
    main()
