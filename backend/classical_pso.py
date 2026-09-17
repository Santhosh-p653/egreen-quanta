"""
classical_pso.py — Classical Velocity-Based Particle Swarm Optimization
Implementation of standard classical PSO (Kennedy & Eberhart, 1995) to serve
as a direct baseline comparison against Quantum-behaved PSO (QPSO).

Unlike QPSO (which discards velocity and relies on delta-potential well wave mechanics),
classical PSO updates particles using Newtonian velocity vectors and momentum:
    v_i(t+1) = w * v_i(t) + c1 * r1 * (pbest_i - x_i(t)) + c2 * r2 * (gbest - x_i(t))
    x_i(t+1) = x_i(t) + v_i(t+1)
"""

import time
import numpy as np

from qpso import precompute_segment_costs, route_cost


def classical_pso_optimize(
    G,
    depot,
    waypoints,
    n_particles=30,
    n_iterations=100,
    w=0.7,
    c1=1.5,
    c2=1.5,
    v_max=0.5,
    seed=None,
):
    rng = np.random.default_rng(seed)
    n_dim = len(waypoints)
    seg_costs = precompute_segment_costs(G, [depot] + waypoints)

    def decode_and_score(pos):
        order = np.argsort(pos)
        return route_cost(order, depot, waypoints, seg_costs), order

    # Initialize positions and velocities
    positions = rng.uniform(0, 1, size=(n_particles, n_dim))
    velocities = rng.uniform(-v_max, v_max, size=(n_particles, n_dim))

    pbest = positions.copy()
    pbest_cost = np.array([decode_and_score(p)[0] for p in positions])

    gbest_idx = np.argmin(pbest_cost)
    gbest = pbest[gbest_idx].copy()
    gbest_cost = pbest_cost[gbest_idx]

    history = [gbest_cost]
    start = time.perf_counter()

    for it in range(n_iterations):
        for i in range(n_particles):
            r1 = rng.uniform(0, 1, size=n_dim)
            r2 = rng.uniform(0, 1, size=n_dim)

            # Classical velocity update
            velocities[i] = (
                w * velocities[i]
                + c1 * r1 * (pbest[i] - positions[i])
                + c2 * r2 * (gbest - positions[i])
            )
            # Velocity clamping
            velocities[i] = np.clip(velocities[i], -v_max, v_max)

            # Position update
            positions[i] += velocities[i]

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
    from osm_road_network import build_coimbatore_graph

    G = build_coimbatore_graph(traffic_mode="real", seed=1)
    depot = 0
    waypoints = [1, 4, 6, 7, 11]
    res = classical_pso_optimize(G, depot, waypoints, n_particles=30, n_iterations=80, seed=1)
    print(f"Classical PSO Route: {res['route']}")
    print(f"Cost: {res['cost']:.2f} min | Time: {res['runtime']*1000:.2f} ms")
