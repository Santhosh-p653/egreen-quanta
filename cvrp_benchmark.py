"""
cvrp_benchmark.py — Phase 2
Systematic benchmarking of QPSO vs. Nearest-Neighbor across multiple
real CVRP instances (not just one), both routed through the same
sparse congested graph with multi-trip capacity handling. This is the
CVRP-track equivalent of benchmark.py's multi-seed averaging — instead
of varying the random seed on a synthetic graph, it varies which real
dataset instance is used, since the CVRP dataset provides 100
pre-built instances rather than requiring random generation.
"""

import numpy as np

from cvrp_loader import load_dataset, get_instance
from cvrp_qpso import qpso_optimize_cvrp
from cvrp_baseline import nearest_neighbor_cvrp


def run_cvrp_benchmark(n_instances=15, k_neighbors=4, n_particles=30,
                        n_iterations=100, seed=1, start_idx=0):
    data = load_dataset()
    trials = []

    for offset in range(n_instances):
        idx = start_idx + offset
        instance = get_instance(data, idx)

        q = qpso_optimize_cvrp(
            instance, k_neighbors=k_neighbors,
            n_particles=n_particles, n_iterations=n_iterations, seed=seed,
        )
        n = nearest_neighbor_cvrp(instance, k_neighbors=k_neighbors, seed=seed)

        if not q["feasible"] or not n["feasible"]:
            # skip instances no single vehicle can ever serve — they'd
            # otherwise corrupt the mean/std with None-valued costs
            trials.append({
                "instance_idx": idx,
                "qpso_cost": None,
                "nn_cost": None,
                "qpso_trips": None,
                "nn_trips": None,
                "improvement_pct": None,
                "qpso_runtime_ms": q["runtime"] * 1000,
                "nn_runtime_ms": n["runtime"] * 1000,
                "feasible": False,
            })
            continue

        improvement = (n["cost"] - q["cost"]) / n["cost"] * 100 if n["cost"] > 0 else 0.0
        trials.append({
            "instance_idx": idx,
            "qpso_cost": q["cost"],
            "nn_cost": n["cost"],
            "qpso_trips": q["n_trips"],
            "nn_trips": n["n_trips"],
            "improvement_pct": improvement,
            "qpso_runtime_ms": q["runtime"] * 1000,
            "nn_runtime_ms": n["runtime"] * 1000,
            "feasible": True,
        })

    feasible_trials = [t for t in trials if t["feasible"]]
    skipped = len(trials) - len(feasible_trials)

    improvements = np.array([t["improvement_pct"] for t in feasible_trials])
    qpso_costs = np.array([t["qpso_cost"] for t in feasible_trials])
    nn_costs = np.array([t["nn_cost"] for t in feasible_trials])

    summary = {
        "n_instances": n_instances,
        "n_feasible": len(feasible_trials),
        "n_skipped_infeasible": skipped,
        "mean_improvement_pct": float(improvements.mean()) if len(feasible_trials) else 0.0,
        "std_improvement_pct": float(improvements.std()) if len(feasible_trials) else 0.0,
        "min_improvement_pct": float(improvements.min()) if len(feasible_trials) else 0.0,
        "max_improvement_pct": float(improvements.max()) if len(feasible_trials) else 0.0,
        "qpso_wins": int((qpso_costs <= nn_costs).sum()) if len(feasible_trials) else 0,
        "mean_qpso_cost": float(qpso_costs.mean()) if len(feasible_trials) else 0.0,
        "mean_nn_cost": float(nn_costs.mean()) if len(feasible_trials) else 0.0,
        "mean_qpso_trips": float(np.mean([t["qpso_trips"] for t in feasible_trials])) if len(feasible_trials) else 0.0,
        "mean_nn_trips": float(np.mean([t["nn_trips"] for t in feasible_trials])) if len(feasible_trials) else 0.0,
    }
    return trials, summary


if __name__ == "__main__":
    trials, summary = run_cvrp_benchmark(n_instances=15, seed=1)

    print("CVRP benchmark — QPSO vs Nearest-Neighbor (15 real instances):\n")
    for t in trials:
        print(f"  inst {t['instance_idx']:3d}: QPSO={t['qpso_cost']:7.1f} "
              f"({t['qpso_trips']} trips)  NN={t['nn_cost']:7.1f} "
              f"({t['nn_trips']} trips)  improvement={t['improvement_pct']:5.1f}%")

    print("\nSummary:")
    for k, v in summary.items():
        print(f"  {k}: {v:.2f}" if isinstance(v, float) else f"  {k}: {v}")
