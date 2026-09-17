
"""
benchmark.py
Systematic benchmarking utilities for the QPSO traffic-routing prototype:

1. multi_seed_benchmark — run QPSO vs baseline across many random seeds at
   fixed problem size, so you can report mean/std improvement instead of a
   single lucky/unlucky run.

2. scalability_sweep — run QPSO vs baseline across increasing node counts,
   so you can report how improvement % and runtime scale with problem size
   (this is the evidence for the "demonstrate scalability" objective).
"""

import random
import numpy as np

from graph_model import build_random_graph, apply_congestion
from baseline import nearest_neighbor_route
from qpso import qpso_optimize


def _single_trial(n_nodes, n_waypoints, n_particles, n_iterations, seed):
    G = apply_congestion(build_random_graph(n_nodes=n_nodes, seed=seed), seed=seed)
    random.seed(seed)
    depot = 0
    waypoints = random.sample([n for n in G.nodes if n != depot], n_waypoints)

    qpso_result = qpso_optimize(
        G, depot, waypoints,
        n_particles=n_particles, n_iterations=n_iterations, seed=seed,
    )
    _, nn_cost, nn_runtime = nearest_neighbor_route(G, depot, waypoints)

    improvement = (nn_cost - qpso_result["cost"]) / nn_cost * 100
    return {
        "seed": seed,
        "qpso_cost": qpso_result["cost"],
        "nn_cost": nn_cost,
        "improvement_pct": improvement,
        "qpso_runtime_ms": qpso_result["runtime"] * 1000,
        "nn_runtime_ms": nn_runtime * 1000,
    }


def multi_seed_benchmark(n_nodes, n_waypoints, n_particles, n_iterations,
                          n_trials=10, base_seed=1):
    """Run n_trials independent trials (different seeds) at fixed size.
    Returns (list_of_trial_dicts, summary_dict)."""
    trials = [
        _single_trial(n_nodes, n_waypoints, n_particles, n_iterations, base_seed + i)
        for i in range(n_trials)
    ]
    improvements = np.array([t["improvement_pct"] for t in trials])
    qpso_costs = np.array([t["qpso_cost"] for t in trials])
    nn_costs = np.array([t["nn_cost"] for t in trials])

    summary = {
        "n_trials": n_trials,
        "mean_improvement_pct": float(improvements.mean()),
        "std_improvement_pct": float(improvements.std()),
        "min_improvement_pct": float(improvements.min()),
        "max_improvement_pct": float(improvements.max()),
        "qpso_wins": int((qpso_costs <= nn_costs).sum()),
        "mean_qpso_cost": float(qpso_costs.mean()),
        "mean_nn_cost": float(nn_costs.mean()),
    }
    return trials, summary


def scalability_sweep(node_counts, n_waypoints, n_particles, n_iterations, seed=1):
    """Run one trial per node count. Returns list of dicts with cost and
    runtime for both QPSO and baseline at each size."""
    results = []
    for n_nodes in node_counts:
        wp = min(n_waypoints, n_nodes - 1)
        trial = _single_trial(n_nodes, wp, n_particles, n_iterations, seed)
        trial["n_nodes"] = n_nodes
        results.append(trial)
    return results


if __name__ == "__main__":
    trials, summary = multi_seed_benchmark(
        n_nodes=20, n_waypoints=5, n_particles=30, n_iterations=100, n_trials=10
    )
    print("Multi-seed benchmark (n=10 trials):")
    for k, v in summary.items():
        print(f"  {k}: {v:.2f}" if isinstance(v, float) else f"  {k}: {v}")

    print("\nScalability sweep:")
    sweep = scalability_sweep(
        node_counts=[10, 20, 30, 40], n_waypoints=5,
        n_particles=30, n_iterations=100, seed=1,
    )
    for r in sweep:
        print(f"  nodes={r['n_nodes']:3d}  qpso={r['qpso_cost']:.1f}  "
              f"nn={r['nn_cost']:.1f}  improvement={r['improvement_pct']:.1f}%  "
              f"qpso_runtime={r['qpso_runtime_ms']:.1f}ms")
