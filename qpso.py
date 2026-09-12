"""
qpso.py
Quantum-inspired Particle Swarm Optimization (Sun, Feng & Xu, 2004)
applied to a small single-vehicle VRP: find the best order to visit a
set of waypoint nodes starting from a depot, where the cost between
any two waypoints is the shortest-path cost on the traffic graph.

Encoding: each particle is a real-valued vector, one value per
waypoint. argsort(vector) gives the visiting order (priority-based
permutation encoding — standard for QPSO/PSO on ordering problems).

Update rule (the actual QPSO mechanics, NOT classical velocity-based
PSO):
    mbest   = mean of all particles' personal-best positions
    p       = phi * pbest + (1 - phi) * gbest      (phi ~ U(0,1))
    x_new   = p ± beta * |mbest - x| * ln(1/u)      (u ~ U(0,1))
beta (contraction-expansion coefficient) is linearly annealed from
beta_max to beta_min over the run — this is what gives QPSO its
exploration -> exploitation balance without needing a velocity term.
"""

import time
import numpy as np
import networkx as nx


def precompute_segment_costs(G, nodes):
    """All-pairs shortest path cost among a set of nodes (depot + waypoints)."""
    costs = {}
    for u in nodes:
        lengths = nx.single_source_dijkstra_path_length(G, u, weight="weight")
        for v in nodes:
            costs[(u, v)] = lengths.get(v, np.inf)
    return costs


def route_cost(order, depot, waypoints, seg_costs):
    """order: sequence of indices into waypoints giving visit order."""
    route = [depot] + [waypoints[i] for i in order]
    return sum(seg_costs[(route[i], route[i + 1])] for i in range(len(route) - 1))


def qpso_optimize(
    G,
    depot,
    waypoints,
    n_particles=30,
    n_iterations=100,
    beta_max=1.0,
    beta_min=0.4,
    seed=None,
):
    rng = np.random.default_rng(seed)
    n_dim = len(waypoints)
    seg_costs = precompute_segment_costs(G, [depot] + waypoints)

    def decode_and_score(pos):
        order = np.argsort(pos)
        return route_cost(order, depot, waypoints, seg_costs), order

    # init swarm
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
            u = rng.uniform(1e-6, 1, size=n_dim)  # avoid log(0)
            sign = rng.choice([-1, 1], size=n_dim)
            positions[i] = p + sign * beta * np.abs(mbest - positions[i]) * np.log(1 / u)

            cost, _ = decode_and_score(positions[i])
            if cost < pbest_cost[i]:
                pbest[i] = positions[i].copy()
                pbest_cost[i] = cost
                if cost < gbest_cost:
                    gbest = positions[i].copy()
                    gbest_cost = cost

        history.append(gbest_cost)

    runtime = time.perf_counter() - start
    _, best_order = decode_and_score(gbest)
    best_route = [depot] + [waypoints[i] for i in best_order]

    return {
        "route": best_route,
        "cost": gbest_cost,
        "history": history,
        "runtime": runtime,
    }


if __name__ == "__main__":
    from graph_model import build_random_graph, apply_congestion

    G = apply_congestion(build_random_graph(n_nodes=20, seed=1), seed=1)
    depot = 0
    waypoints = [3, 7, 11, 14, 18]

    result = qpso_optimize(G, depot, waypoints, n_particles=30, n_iterations=80, seed=1)
    print(f"Best route: {result['route']}")
    print(f"Cost: {result['cost']:.2f} min")
    print(f"Runtime: {result['runtime']*1000:.2f} ms")
  
