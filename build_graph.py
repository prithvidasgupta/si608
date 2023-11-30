# %%
import networkx as nx
import pandas as pd
from IPython.display import display
import matplotlib.pyplot as plt


# %%
def build_df(file1, file2):
    """
    Combines dataframes where focus page is source and sink
    :param file1: Path to file where focus page is sink (curr).
    :type file1: str
    :param file2: Path to file where focus page is source (prev).
    :type file2: str
    :return: Combined dataframe of clickstream data.
    :rtype: Dataframe
    """
    lside = pd.read_csv(file1)
    rside = pd.read_csv(file2)
    return pd.concat([lside, rside])


def build_graph(df, from_node="prev", to_node="curr", weight="n"):
    """
    Creates directed graph from given dataframe, with edge weights equal to clicks.
    :param df: Pages with clickstream data.
    :type df: Dataframe
    :param from_node: Name of column containing click origin pages
    :type from_node: str
    :param to_node: Name of column where containing click destination pages
    :type to_node: str
    :param weight: Number of clicks
    :type weight: int
    :return: Clickstream graph
    :rtype: NetworkX object
    """
    g = nx.DiGraph()
    from_nodes = list(df[from_node])
    to_nodes = list(df[to_node])
    weights = list(df[weight])

    for fnode, tnode, wt in zip(from_nodes, to_nodes, weights):
        if fnode == tnode:
            print(f" WARN: self-edge {fnode, tnode}")
        g.add_edge(fnode, tnode, weight=wt)
    return g


def draw_graph(graph, focus_page):
    """
    Creates a visualization of clickstream data.
    :param graph: Graph to visualize
    :type graph: NetworkX object
    :param focus_page: Page title for page users travel to and from.
    :type focus_page: str
    :return: None
    :rtype: None
    """
    node_colors = ["blue" if node == focus_page else "yellow" for node in graph.nodes()]
    node_size = [5 if node != focus_page else 1000 for node in graph.nodes()]
    plt.figure(figsize=(10, 10))
    nx.draw(
        graph, pos=nx.spring_layout(graph), node_size=node_size, node_color=node_colors
    )
    plt.show()


# %%
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

    # Build and visualize graph
    ua_2022_03 = build_graph(combined)
    draw_graph(ua_2022_03, "2022_russian_invasion_of_ukraine")

    # Check graph
    in_degs = dict(ua_2022_03.in_degree)
    out_degs = dict(ua_2022_03.out_degree)
    in_node, in_degree = max(in_degs.items(), key=lambda x: x[1])
    out_node, out_degree = max(out_degs.items(), key=lambda x: x[1])
    weights = {(u, v): data["weight"] for u, v, data in ua_2022_03.edges(data=True)}
    node_pair, max_weight = max(weights.items(), key=lambda x: x[1])
    print(f"max in degree: {(in_node, in_degree)}")
    print(f"max out degree: {out_node, out_degree}")
    print(f"max edge weight: {node_pair, max_weight}")

    # %% Test output from main
    main_ua_202203 = nx.read_gml("./output/202203_graph.gml")
    main_in_degs = dict(main_ua_202203.in_degree)
    main_out_degs = dict(main_ua_202203.out_degree)
    in_node, in_degree = max(main_in_degs.items(), key=lambda x: x[1])
    out_node, out_degree = max(main_out_degs.items(), key=lambda x: x[1])
    weights = {(u, v): data["weight"] for u, v, data in ua_2022_03.edges(data=True)}
    node_pair, max_weight = max(weights.items(), key=lambda x: x[1])
    print(f"max in degree: {(in_node, in_degree)}")
    print(f"max out degree: {out_node, out_degree}")
    print(f"max edge weight: {node_pair, max_weight}")


if __name__ == "__main__":
    main()
