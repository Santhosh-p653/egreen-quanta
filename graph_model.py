"""
graph_model.py
Builds a synthetic weighted transportation network and applies a
simulated congestion factor to edge weights.
"""

import networkx as nx
import numpy as np


def build_random_graph(n_nodes=20, edge_prob=0.25, seed=42):
    """Create a random connected weighted directed graph representing
    a road network. Edge weight = base travel time (minutes)."""
    rng = np.random.default_rng(seed)
    G = nx.gnp_random_graph(n_nodes, edge_prob, seed=seed, directed=False)

    # Ensure connectivity — if not connected, stitch components together
    if not nx.is_connected(G):
        components = list(nx.connected_components(G))
        for i in range(len(components) - 1):
            u = next(iter(components[i]))
            v = next(iter(components[i + 1]))
            G.add_edge(u, v)

    DG = nx.DiGraph()
    for u, v in G.edges():
        base_time = rng.uniform(5, 20)  # minutes
        DG.add_edge(u, v, base_weight=base_time)
        DG.add_edge(v, u, base_weight=base_time)

    return DG


def apply_congestion(G, seed=None):
    """Return a copy of G with a randomized congestion multiplier
    (1.0 = free flow, up to 2.5x = heavy congestion) applied to each
    edge's weight. Call this once per simulated 'traffic snapshot'."""
    rng = np.random.default_rng(seed)
    G2 = G.copy()
    for u, v, data in G2.edges(data=True):
        congestion_factor = rng.uniform(1.0, 2.5)
        data["weight"] = data["base_weight"] * congestion_factor
        data["congestion_factor"] = congestion_factor
    return G2


if __name__ == "__main__":
    G = build_random_graph(n_nodes=15, seed=1)
    G = apply_congestion(G, seed=1)
    print(f"Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
    print("Sample edges:", list(G.edges(data=True))[:3])
