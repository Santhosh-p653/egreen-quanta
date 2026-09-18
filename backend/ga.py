"""
ga.py — Genetic Algorithm with Order Crossover (OX) and Partially Mapped Crossover (PMX)
Provides two distinct GA metaheuristic variants to compare against QPSO.
"""

import time
import numpy as np

from qpso import precompute_segment_costs


def crossover_ox(p1, p2, rng):
    """Order Crossover (OX): Preserves relative order and contiguous sub-tours."""
    size = len(p1)
    cx1, cx2 = sorted(rng.choice(range(size + 1), size=2, replace=False))

    child = [-1] * size
    child[cx1:cx2] = p1[cx1:cx2]

    curr_p2 = cx2
    curr_c = cx2

    while -1 in child:
        item = p2[curr_p2 % size]
        if item not in child:
            child[curr_c % size] = item
            curr_c += 1
        curr_p2 += 1

    return child


def crossover_pmx(p1, p2, rng):
    """Partially Mapped Crossover (PMX): Preserves absolute positions via mapping."""
    size = len(p1)
    cx1, cx2 = sorted(rng.choice(range(size + 1), size=2, replace=False))

    child = [-1] * size
    child[cx1:cx2] = p1[cx1:cx2]

    # Map remaining positions
    for i in range(cx1, cx2):
        if p2[i] not in child:
            val = p2[i]
            pos = i
            while cx1 <= pos < cx2:
                idx_in_p2 = p2.index(p1[pos])
                pos = idx_in_p2
            child[pos] = val

    for i in range(size):
        if child[i] == -1:
            child[i] = p2[i]

    return child


def ga_optimize(
    G,
    depot,
    waypoints,
    crossover="ox",  # "ox" or "pmx"
    pop_size=40,
    n_generations=100,
    mutation_rate=0.15,
    tournament_size=3,
    seed=None,
):
    rng = np.random.default_rng(seed)
    n_dim = len(waypoints)
    seg_costs = precompute_segment_costs(G, [depot] + waypoints)

    def evaluate_perm(perm):
        route = [depot] + [waypoints[i] for i in perm]
        return sum(seg_costs[(route[k], route[k + 1])] for k in range(len(route) - 1))

    # Initialize population of permutations
    population = [list(rng.permutation(n_dim)) for _ in range(pop_size)]
    costs = np.array([evaluate_perm(ind) for ind in population])

    best_idx = np.argmin(costs)
    best_ind = population[best_idx]
    best_cost = costs[best_idx]
    history = [best_cost]

    cx_fn = crossover_pmx if crossover.lower() == "pmx" else crossover_ox
    start = time.perf_counter()

    for gen in range(n_generations):
        new_pop = [best_ind.copy()]  # Elitism: carry over best individual

        while len(new_pop) < pop_size:
            # Tournament selection
            cand1 = rng.choice(pop_size, size=tournament_size, replace=False)
            p1_idx = cand1[np.argmin(costs[cand1])]
            cand2 = rng.choice(pop_size, size=tournament_size, replace=False)
            p2_idx = cand2[np.argmin(costs[cand2])]

            p1 = population[p1_idx]
            p2 = population[p2_idx]

            child = cx_fn(p1, p2, rng)

            # Combined Inversion & Swap Mutation for routing permutations
            if rng.uniform(0, 1) < mutation_rate:
                if n_dim >= 3 and rng.uniform(0, 1) < 0.5:
                    # Inversion mutation (reverses a contiguous segment)
                    i1, i2 = sorted(rng.choice(n_dim, size=2, replace=False))
                    child[i1:i2 + 1] = list(reversed(child[i1:i2 + 1]))
                else:
                    # Swap mutation
                    i1, i2 = rng.choice(n_dim, size=2, replace=False)
                    child[i1], child[i2] = child[i2], child[i1]

            new_pop.append(child)

        population = new_pop
        costs = np.array([evaluate_perm(ind) for ind in population])

        cur_best_idx = np.argmin(costs)
        if costs[cur_best_idx] < best_cost:
            best_cost = costs[cur_best_idx]
            best_ind = population[cur_best_idx]

        history.append(best_cost)

    runtime = time.perf_counter() - start
    best_route = [depot] + [waypoints[i] for i in best_ind]

    return {
        "route": best_route,
        "cost": best_cost,
        "history": history,
        "runtime": runtime,
    }


if __name__ == "__main__":
    from osm_road_network import build_coimbatore_graph

    G = build_coimbatore_graph(traffic_mode="real", seed=1)
    depot = 0
    waypoints = [1, 4, 6, 7, 11]

    ox_res = ga_optimize(G, depot, waypoints, crossover="ox", seed=1)
    pmx_res = ga_optimize(G, depot, waypoints, crossover="pmx", seed=1)

    print(f"GA-OX  Cost: {ox_res['cost']:.2f} min | Time: {ox_res['runtime']*1000:.2f} ms")
    print(f"GA-PMX Cost: {pmx_res['cost']:.2f} min | Time: {pmx_res['runtime']*1000:.2f} ms")
