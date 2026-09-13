%%writefile cvrp_qpso.py
"""
cvrp_qpso.py — Phase 2
QPSO on the CVRP dataset, routed through the sparse congested graph
(cvrp_graph.py) instead of raw Euclidean distance, with genuine
multi-trip capacity handling: when the next customer's demand would
exceed the vehicle's remaining capacity, the route is forced back to
the depot to reload before continuing. This makes capacity a real
route-order-dependent decision (fewer, better-timed depot returns =
lower cost) rather than a fixed pass/fail check on the instance.

Same core QPSO update rule as qpso.py (Sun, Feng & Xu, 2004 — mbest,
delta-potential-well position update, no velocity term) and the same
priority-based permutation encoding (argsort of a real-valued vector
gives the customer visiting order). What's new in Phase 2 is the
fitness function: it decodes the order into an actual multi-trip route
over the graph and returns total travel cost + number of depot
reloads.
"""

import time
import numpy as np

from cvrp_graph import build_congested_graph
from qpso import precompute_segment_costs


def decode_multitrip_route(order, instance, seg_costs):
    """order: sequence of customer node indices (already in visit order,
    NOT indices-into-customers — see qpso_optimize_cvrp for the argsort
    step that produces this).
    Returns (full_route, total_cost, n_trips) where full_route includes
    every depot visit (start, any forced reloads, and the final return)."""
    depot = instance["depot"]
    demands = instance["demands"]
    capacity = instance["capacity"]

    route = [depot]
    cost = 0.0
    load = 0
    current = depot
    n_trips = 1  # count the initial departure from depot as trip 1

    for c in order:
        d = int(demands[c])
        if load + d > capacity:
            # forced reload: return to depot before continuing
            cost += seg_costs[(current, depot)]
            route.append(depot)
            current = depot
            load = 0
            n_trips += 1
        cost += seg_costs[(current, c)]
        route.append(c)
        load += d
        current = c

    # final return to depot
    cost += seg_costs[(current, depot)]
    route.append(depot)

    return route, cost, n_trips


def qpso_optimize_cvrp(
    instance,
    k_neighbors=4,
    n_particles=30,
    n_iterations=100,
    beta_max=1.0,
    beta_min=0.4,
    seed=None,
):
    rng = np.random.default_rng(seed)
    depot = instance["depot"]
    customers = instance["customers"]
    n_dim = len(customers)

    G = build_congested_graph(instance["locations"], k_neighbors=k_neighbors, seed=seed)
    seg_costs = precompute_segment_costs(G, [depot] + customers)

    def decode_and_score(pos):
        order = [customers[i] for i in np.argsort(pos)]
        route, cost, n_trips = decode_multitrip_route(order, instance, seg_costs)
        return cost, route, n_trips

    positions = rng.uniform(0, 1, size=(n_particles, n_dim))
    pbest = positions.copy()
    pbest_cost = np.array([decode_and_score(p)[0] for p in positions])

    gbest_idx = np.argmin(pbest_cost)
    gbest = pbest[gbest_idx].copy()
    gbest_cost = pbest_cost[gbest_idx]

    history = [gbest_cost]
    start = time.perf_counter()

    for it in range(n_iterations):
        beta = beta_max - (beta_max - beta_min) * (it / n_iterations)
        mbest = pbest.mean(axis=0)

        for i in range(n_particles):
            phi = rng.uniform(0, 1, size=n_dim)
            p = phi * pbest[i] + (1 - phi) * gbest
            u = rng.uniform(1e-6, 1, size=n_dim)
            sign = rng.choice([-1, 1], size=n_dim)
            positions[i] = p + sign * beta * np.abs(mbest - positions[i]) * np.log(1 / u)

            cost, _, _ = decode_and_score(positions[i])
            if cost < pbest_cost[i]:
                pbest[i] = positions[i].copy()
                pbest_cost[i] = cost
                if cost < gbest_cost:
                    gbest = positions[i].copy()
                    gbest_cost = cost

        history.append(gbest_cost)

    runtime = time.perf_counter() - start
    _, best_route, n_trips = decode_and_score(gbest)

    return {
        "route": best_route,
        "cost": gbest_cost,
        "n_trips": n_trips,
        "history": history,
        "runtime": runtime,
    }


if __name__ == "__main__":
    from cvrp_loader import load_dataset, get_instance

    data = load_dataset()
    instance = get_instance(data, 0)
    print(f"Instance 0: {len(instance['customers'])} customers, "
          f"capacity={instance['capacity']}, total demand={instance['demands'].sum()}")

    result = qpso_optimize_cvrp(instance, n_particles=30, n_iterations=100, seed=1)
    print(f"\nBest route: {result['route']}")
    print(f"Cost (graph-routed distance): {result['cost']:.2f}")
    print(f"Depot trips required: {result['n_trips']}")
    print(f"Runtime: {result['runtime']*1000:.2f} ms")
