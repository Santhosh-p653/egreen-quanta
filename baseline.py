"""
baseline.py
Classical shortest-path baseline (Dijkstra) to benchmark QPSO against.
"""

import time
import networkx as nx


def dijkstra_route(G, source, target):
    """Return (path, cost, runtime_seconds) using Dijkstra on edge weight."""
    start = time.perf_counter()
    path = nx.dijkstra_path(G, source, target, weight="weight")
    cost = nx.dijkstra_path_length(G, source, target, weight="weight")
    runtime = time.perf_counter() - start
    return path, cost, runtime


def nearest_neighbor_route(G, depot, waypoints):
    """Classical greedy nearest-neighbor baseline for the waypoint-ordering
    VRP variant — this is what QPSO's route cost gets benchmarked against."""
    from qpso import precompute_segment_costs

    start = time.perf_counter()
    seg_costs = precompute_segment_costs(G, [depot] + waypoints)
    remaining = list(waypoints)
    route = [depot]
    total_cost = 0.0
    current = depot
    while remaining:
        next_node = min(remaining, key=lambda n: seg_costs[(current, n)])
        total_cost += seg_costs[(current, next_node)]
        route.append(next_node)
        remaining.remove(next_node)
        current = next_node
    runtime = time.perf_counter() - start
    return route, total_cost, runtime


if __name__ == "__main__":
    from graph_model import build_random_graph, apply_congestion

    G = apply_congestion(build_random_graph(n_nodes=15, seed=1), seed=1)
    path, cost, runtime = dijkstra_route(G, 0, 10)
    print(f"Path: {path}\nCost: {cost:.2f} min\nRuntime: {runtime*1000:.3f} ms")

    G2 = apply_congestion(build_random_graph(n_nodes=20, seed=1), seed=1)
    route, cost2, rt2 = nearest_neighbor_route(G2, 0, [3, 7, 11, 14, 18])
    print(f"\nNN route: {route}\nCost: {cost2:.2f} min\nRuntime: {rt2*1000:.3f} ms")
