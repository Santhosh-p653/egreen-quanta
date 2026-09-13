%%writefile cvrp_baseline.py
"""
cvrp_baseline.py — Phase 2
Classical Nearest-Neighbor baseline for the CVRP dataset, routed
through the same sparse congested graph as cvrp_qpso.py, with the same
multi-trip depot-return rule — so the comparison to QPSO is apples to
apples (same graph, same capacity-handling mechanism, only the search
strategy differs: greedy vs. swarm search).
"""

import time

from cvrp_graph import build_congested_graph
from qpso import precompute_segment_costs
from cvrp_qpso import decode_multitrip_route


def nearest_neighbor_cvrp(instance, k_neighbors=4, seed=None):
    depot = instance["depot"]
    customers = list(instance["customers"])
    demands = instance["demands"]
    capacity = instance["capacity"]

    G = build_congested_graph(instance["locations"], k_neighbors=k_neighbors, seed=seed)
    seg_costs = precompute_segment_costs(G, [depot] + customers)

    start = time.perf_counter()
    remaining = list(customers)
    route = [depot]
    cost = 0.0
    load = 0
    current = depot
    n_trips = 1

    while remaining:
        # only consider customers that fit in remaining capacity
        feasible = [c for c in remaining if load + int(demands[c]) <= capacity]
        if not feasible:
            # forced reload
            cost += seg_costs[(current, depot)]
            route.append(depot)
            current = depot
            load = 0
            n_trips += 1
            feasible = remaining

        next_node = min(feasible, key=lambda n: seg_costs[(current, n)])
        cost += seg_costs[(current, next_node)]
        route.append(next_node)
        load += int(demands[next_node])
        remaining.remove(next_node)
        current = next_node

    cost += seg_costs[(current, depot)]
    route.append(depot)
    runtime = time.perf_counter() - start

    return {
        "route": route,
        "cost": cost,
        "n_trips": n_trips,
        "runtime": runtime,
    }


if __name__ == "__main__":
    from cvrp_loader import load_dataset, get_instance

    data = load_dataset()
    instance = get_instance(data, 0)
    result = nearest_neighbor_cvrp(instance, seed=1)
    print(f"NN route: {result['route']}")
    print(f"Cost: {result['cost']:.2f}")
    print(f"Depot trips required: {result['n_trips']}")
    print(f"Runtime: {result['runtime']*1000:.3f} ms")
