"""
clarke_wright.py — Classical Industry-Standard CVRP Baseline
Implementation of the Clarke-Wright Savings Algorithm (Clarke & Wright, 1964).

Computes savings matrix:
    S_{i, j} = c(i, depot) + c(depot, j) - c(i, j)
using Dijkstra shortest-path costs on the congested road network graph.
Iteratively merges routes while strictly respecting vehicle capacity constraints
and endpoint adjacency to the depot.
"""

import time
import numpy as np

from cvrp_graph import build_congested_graph
from qpso import precompute_segment_costs


def clarke_wright_cvrp(instance, k_neighbors=4, seed=None):
    """
    Solves CVRP using the Clarke-Wright Savings heuristic on the congested graph.

    Parameters:
        instance: dict containing 'depot', 'customers', 'demands', 'capacity', 'locations'
        k_neighbors: number of nearest neighbors for graph construction
        seed: random seed for graph congestion

    Returns:
        dict: {
            "route": full_route_with_depot_visits,
            "cost": total_travel_cost,
            "n_trips": number_of_depot_trips,
            "subroutes": list_of_individual_trips,
            "runtime": runtime_in_seconds,
            "feasible": True
        }
    """
    depot = instance["depot"]
    customers = list(instance["customers"])
    demands = instance["demands"]
    capacity = instance["capacity"]

    G = build_congested_graph(instance["locations"], k_neighbors=k_neighbors, seed=seed)
    seg_costs = precompute_segment_costs(G, [depot] + customers)

    start = time.perf_counter()

    # Step 1: Initialize each customer in an isolated back-and-forth route [depot, c, depot]
    # Represent each route as a list of customer nodes (excluding depot)
    routes = {c: [c] for c in customers}
    route_demands = {c: int(demands[c]) for c in customers}
    # Track which route ID contains which customer
    node_to_route = {c: c for c in customers}

    # Step 2: Calculate savings S_ij for all customer pairs (i, j), i != j
    savings = []
    for i in customers:
        for j in customers:
            if i != j:
                s = seg_costs[(i, depot)] + seg_costs[(depot, j)] - seg_costs[(i, j)]
                savings.append((s, i, j))

    # Sort pairs by savings descending
    savings.sort(key=lambda x: x[0], reverse=True)

    # Step 3: Greedily merge routes based on savings and capacity feasibility
    for s, i, j in savings:
        if s <= 0:
            break

        r_id_i = node_to_route[i]
        r_id_j = node_to_route[j]

        # Cannot merge if already in the same route
        if r_id_i == r_id_j:
            continue

        route_i = routes[r_id_i]
        route_j = routes[r_id_j]

        # Capacity check
        if route_demands[r_id_i] + route_demands[r_id_j] > capacity:
            continue

        # End-point adjacency check:
        # i must be first or last in route_i; j must be first or last in route_j
        i_is_first = (route_i[0] == i)
        i_is_last = (route_i[-1] == i)
        j_is_first = (route_j[0] == j)
        j_is_last = (route_j[-1] == j)

        if not (i_is_first or i_is_last) or not (j_is_first or j_is_last):
            continue

        # Merge orientation
        if i_is_last and j_is_first:
            merged = route_i + route_j
        elif i_is_last and j_is_last:
            merged = route_i + route_j[::-1]
        elif i_is_first and j_is_first:
            merged = route_i[::-1] + route_j
        elif i_is_first and j_is_last:
            merged = route_j + route_i
        else:
            continue

        # Update route data structures
        new_demand = route_demands[r_id_i] + route_demands[r_id_j]
        routes[r_id_i] = merged
        route_demands[r_id_i] = new_demand
        del routes[r_id_j]
        del route_demands[r_id_j]

        for node in merged:
            node_to_route[node] = r_id_i

    # Step 4: Assemble final route and compute exact graph-routed cost
    full_route = [depot]
    subroutes = []
    total_cost = 0.0

    for r_id, cust_list in routes.items():
        subroute = [depot] + cust_list + [depot]
        subroutes.append(subroute)
        for k in range(len(subroute) - 1):
            total_cost += seg_costs[(subroute[k], subroute[k + 1])]
        full_route.extend(cust_list + [depot])

    runtime = time.perf_counter() - start

    return {
        "route": full_route,
        "cost": total_cost,
        "n_trips": len(subroutes),
        "subroutes": subroutes,
        "runtime": runtime,
        "feasible": True,
    }


def clarke_wright_route(G, depot, waypoints):
    """
    Classical Clarke-Wright Savings for unconstrained waypoint routing (Phase 1).
    Constructs a single connected tour without capacity restrictions.
    """
    start = time.perf_counter()
    nodes = [depot] + list(waypoints)
    seg_costs = precompute_segment_costs(G, nodes)

    routes = {w: [w] for w in waypoints}
    node_to_route = {w: w for w in waypoints}

    savings = []
    for i in waypoints:
        for j in waypoints:
            if i != j:
                s = seg_costs[(i, depot)] + seg_costs[(depot, j)] - seg_costs[(i, j)]
                savings.append((s, i, j))

    savings.sort(key=lambda x: x[0], reverse=True)

    for s, i, j in savings:
        if s <= 0:
            break
        r_id_i = node_to_route[i]
        r_id_j = node_to_route[j]
        if r_id_i == r_id_j:
            continue

        route_i = routes[r_id_i]
        route_j = routes[r_id_j]

        i_is_first = (route_i[0] == i)
        i_is_last = (route_i[-1] == i)
        j_is_first = (route_j[0] == j)
        j_is_last = (route_j[-1] == j)

        if not (i_is_first or i_is_last) or not (j_is_first or j_is_last):
            continue

        if i_is_last and j_is_first:
            merged = route_i + route_j
        elif i_is_last and j_is_last:
            merged = route_i + route_j[::-1]
        elif i_is_first and j_is_first:
            merged = route_i[::-1] + route_j
        elif i_is_first and j_is_last:
            merged = route_j + route_i
        else:
            continue

        routes[r_id_i] = merged
        del routes[r_id_j]
        for node in merged:
            node_to_route[node] = r_id_i

    # Join any remaining disjoint subroutes
    final_order = []
    for r_id, cust_list in routes.items():
        final_order.extend(cust_list)

    full_route = [depot] + final_order
    cost = sum(seg_costs[(full_route[k], full_route[k + 1])] for k in range(len(full_route) - 1))
    runtime = time.perf_counter() - start

    return full_route, cost, runtime


if __name__ == "__main__":
    from cvrp_loader import load_dataset, get_instance

    data = load_dataset()
    instance = get_instance(data, 0)
    res = clarke_wright_cvrp(instance, seed=1)
    print(f"Clarke-Wright route: {res['route']}")
    print(f"Cost: {res['cost']:.2f}")
    print(f"Trips: {res['n_trips']}")
    print(f"Runtime: {res['runtime']*1000:.3f} ms")
