"""
cheapest_insertion.py — Classical Greedy Insertion Baseline
Implementation of the Cheapest Insertion Heuristic for both Phase 1 and Phase 2.

At each step, among all unvisited nodes k and all active tour edges (u, v), finds:
    argmin_{k, (u, v)} [ c(u, k) + c(k, v) - c(u, v) ]
while checking capacity constraints for CVRP.
If no active trip has sufficient capacity to accommodate customer k,
a new feasible trip [depot, k, depot] is initiated.
"""

import time
import numpy as np

from cvrp_graph import build_congested_graph
from qpso import precompute_segment_costs


def cheapest_insertion_cvrp(instance, k_neighbors=4, seed=None):
    """
    Solves CVRP using the Cheapest Insertion heuristic on the congested graph.

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

    # Step 1: Seed the first trip with the customer having the cheapest round-trip to depot
    remaining = set(customers)
    first_cust = min(remaining, key=lambda c: seg_costs[(depot, c)] + seg_costs[(c, depot)])
    remaining.remove(first_cust)

    trips = [[depot, first_cust, depot]]
    trip_loads = [int(demands[first_cust])]

    # Step 2: Iteratively insert remaining customers at the cheapest position
    while remaining:
        best_delta = float("inf")
        best_action = None  # ("insert", trip_idx, pos, cust) or ("new_trip", None, None, cust)

        for k in remaining:
            d_k = int(demands[k])

            # Check existing trips
            for t_idx, trip in enumerate(trips):
                if trip_loads[t_idx] + d_k <= capacity:
                    # evaluate insertion between every adjacent pair (trip[p], trip[p+1])
                    for p in range(len(trip) - 1):
                        u = trip[p]
                        v = trip[p + 1]
                        delta = seg_costs[(u, k)] + seg_costs[(k, v)] - seg_costs[(u, v)]
                        if delta < best_delta:
                            best_delta = delta
                            best_action = ("insert", t_idx, p + 1, k)

            # Also evaluate opening a new trip
            new_trip_cost = seg_costs[(depot, k)] + seg_costs[(k, depot)]
            if new_trip_cost < best_delta:
                best_delta = new_trip_cost
                best_action = ("new_trip", None, None, k)

        action_type, t_idx, pos, chosen_k = best_action

        if action_type == "insert":
            trips[t_idx].insert(pos, chosen_k)
            trip_loads[t_idx] += int(demands[chosen_k])
        else:
            trips.append([depot, chosen_k, depot])
            trip_loads.append(int(demands[chosen_k]))

        remaining.remove(chosen_k)

    # Step 3: Concatenate trips into the final multi-trip route
    full_route = [depot]
    total_cost = 0.0

    for trip in trips:
        for p in range(len(trip) - 1):
            total_cost += seg_costs[(trip[p], trip[p + 1])]
        full_route.extend(trip[1:])

    runtime = time.perf_counter() - start

    return {
        "route": full_route,
        "cost": total_cost,
        "n_trips": len(trips),
        "subroutes": trips,
        "runtime": runtime,
        "feasible": True,
    }


def cheapest_insertion_route(G, depot, waypoints):
    """
    Classical Cheapest Insertion for unconstrained waypoint routing (Phase 1).
    Builds a single closed tour minimizing incremental insertion cost.
    """
    start = time.perf_counter()
    nodes = [depot] + list(waypoints)
    seg_costs = precompute_segment_costs(G, nodes)

    remaining = set(waypoints)
    # Seed with customer closest to depot
    first_wp = min(remaining, key=lambda w: seg_costs[(depot, w)] + seg_costs[(w, depot)])
    remaining.remove(first_wp)

    tour = [depot, first_wp]

    while remaining:
        best_delta = float("inf")
        best_k = None
        best_pos = None

        for k in remaining:
            # Check insertion at any position in the open tour
            # Check edge between depot and tour[1], between tour[p] and tour[p+1], and after tour[-1]
            for p in range(len(tour) - 1):
                u = tour[p]
                v = tour[p + 1]
                delta = seg_costs[(u, k)] + seg_costs[(k, v)] - seg_costs[(u, v)]
                if delta < best_delta:
                    best_delta = delta
                    best_k = k
                    best_pos = p + 1

            # End of tour insertion
            u = tour[-1]
            delta = seg_costs[(u, k)]
            if delta < best_delta:
                best_delta = delta
                best_k = k
                best_pos = len(tour)

        tour.insert(best_pos, best_k)
        remaining.remove(best_k)

    total_cost = sum(seg_costs[(tour[p], tour[p + 1])] for p in range(len(tour) - 1))
    runtime = time.perf_counter() - start

    return tour, total_cost, runtime


if __name__ == "__main__":
    from cvrp_loader import load_dataset, get_instance

    data = load_dataset()
    instance = get_instance(data, 0)
    res = cheapest_insertion_cvrp(instance, seed=1)
    print(f"Cheapest Insertion route: {res['route']}")
    print(f"Cost: {res['cost']:.2f}")
    print(f"Trips: {res['n_trips']}")
    print(f"Runtime: {res['runtime']*1000:.3f} ms")
