"""
cvrp_graph.py
Builds a sparse "road network" graph over a CVRP instance's node
coordinates (depot + customers), instead of assuming direct
point-to-point Euclidean travel. This is what lets Phase 2 unify the
CVRP dataset with the existing traffic-graph track: nodes aren't
all directly connected, congestion is applied per edge, and routing
between any two nodes goes through Dijkstra shortest-path on the
congested graph — same model as graph_model.py, applied to real
CVRP coordinates instead of synthetic random points.
"""

import networkx as nx
import numpy as np

from graph_model import apply_congestion  # reuse congestion simulation as-is


def euclidean_distance_matrix(locations):
    diffs = locations[:, None, :].astype(float) - locations[None, :, :].astype(float)
    return np.sqrt((diffs ** 2).sum(axis=-1))


def build_graph_from_locations(locations, k_neighbors=4, seed=None):
    """Connect each node to its k nearest neighbors (by Euclidean distance)
    rather than a full mesh — models the fact that real road networks
    don't offer a direct road between every pair of points. Ensures the
    graph stays connected."""
    n = locations.shape[0]
    dist = euclidean_distance_matrix(locations)

    G = nx.Graph()
    G.add_nodes_from(range(n))
    for i in range(n):
        neighbor_order = np.argsort(dist[i])
        neighbors = [j for j in neighbor_order if j != i][:k_neighbors]
        for j in neighbors:
            G.add_edge(i, int(j), base_weight=float(dist[i, j]))

    if not nx.is_connected(G):
        components = list(nx.connected_components(G))
        for c in range(len(components) - 1):
            u = next(iter(components[c]))
            v = next(iter(components[c + 1]))
            G.add_edge(u, v, base_weight=float(dist[u, v]))

    DG = nx.DiGraph()
    for u, v, data in G.edges(data=True):
        DG.add_edge(u, v, base_weight=data["base_weight"])
        DG.add_edge(v, u, base_weight=data["base_weight"])

    return DG


def build_congested_graph(locations, k_neighbors=4, seed=None):
    """One-call helper: sparse graph + congestion applied, ready for
    Dijkstra-based segment costs."""
    G = build_graph_from_locations(locations, k_neighbors=k_neighbors, seed=seed)
    return apply_congestion(G, seed=seed)


if __name__ == "__main__":
    from cvrp_loader import load_dataset, get_instance

    data = load_dataset()
    inst = get_instance(data, 0)
    G = build_congested_graph(inst["locations"], k_neighbors=4, seed=1)
    print(f"Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
    print(f"Connected: {nx.is_strongly_connected(G)}")
    print("Sample edge:", list(G.edges(data=True))[0])
