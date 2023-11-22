import networkx as nx
import pandas as pd


def build_df(file1, file2):
    lside = pd.read_csv(file1)
    rside = pd.read_csv(file2)
    return pd.concat([lside, rside])


def build_graph(df, from_node="prev", to_node="curr"):
    g = nx.DiGraph()
    from_nodes = list(df[from_node])
    to_nodes = list(df[to_node])

    for fnode, tnode in zip(from_nodes, to_nodes):
        if fnode == tnode:
            print(fnode, tnode)
        g.add_edge(fnode, tnode)
    return g


def main():
    """
    Entry point for program.
    :return: None
    """


if __name__ == "__main__":
    main()
