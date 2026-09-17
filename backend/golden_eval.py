"""
golden_eval.py
Runs QPSO vs Nearest-Neighbor across systematically-sampled parameter
combinations (LHS, Sobol, Orthogonal Array — see sampling.py) on the
Phase 1 synthetic traffic track, and writes a multi-sheet Excel
workbook of the results. Intended to run in CI (GitHub Actions) so the
evaluation is reproducible and the .xlsx is kept as a build artifact —
evidence that isn't just a cherry-picked local run.

Usage:
    python golden_eval.py --output golden_eval_results.xlsx
    python golden_eval.py --lhs-samples 8 --sobol-samples 8
"""

import argparse
import time

import pandas as pd

from graph_model import build_random_graph, apply_congestion
from baseline import nearest_neighbor_route
from qpso import qpso_optimize
import random

from sampling import lhs_samples, sobol_samples, orthogonal_array_samples

PARAM_NAMES = ["n_particles", "n_iterations", "n_nodes", "k_neighbors"]
# k_neighbors isn't used by the Phase-1 random-graph track (that's a
# Phase-2/CVRP concept) — kept here so the same 4-factor sampling
# machinery (and the L9 orthogonal array, which needs exactly 4
# factors) can be reused as-is. It's sampled but unused in this run.
PARAM_RANGES = [(10, 80, True), (20, 300, True), (10, 40, True), (2, 8, True)]
N_WAYPOINTS = 5
BASE_SEED = 1


def run_one(params, trial_id, method):
    n_particles = int(params["n_particles"])
    n_iterations = int(params["n_iterations"])
    n_nodes = int(params["n_nodes"])
    seed = BASE_SEED + trial_id

    G = apply_congestion(build_random_graph(n_nodes=n_nodes, seed=seed), seed=seed)
    random.seed(seed)
    depot = 0
    waypoints = random.sample([n for n in G.nodes if n != depot],
                               min(N_WAYPOINTS, n_nodes - 1))

    q = qpso_optimize(G, depot, waypoints, n_particles=n_particles,
                       n_iterations=n_iterations, seed=seed)
    n = nearest_neighbor_route(G, depot, waypoints)
    nn_route, nn_cost, nn_runtime = n

    improvement = (nn_cost - q["cost"]) / nn_cost * 100 if nn_cost > 0 else 0.0

    return {
        "method": method,
        "trial_id": trial_id,
        "seed": seed,
        "n_particles": n_particles,
        "n_iterations": n_iterations,
        "n_nodes": n_nodes,
        "n_waypoints": len(waypoints),
        "qpso_cost": q["cost"],
        "nn_cost": nn_cost,
        "improvement_pct": improvement,
        "qpso_wins": bool(q["cost"] <= nn_cost),
        "qpso_runtime_ms": q["runtime"] * 1000,
        "nn_runtime_ms": nn_runtime * 1000,
    }


def run_golden_eval(lhs_n=8, sobol_n=8, seed=1):
    results = []

    for i, params in enumerate(lhs_samples(PARAM_NAMES, PARAM_RANGES, lhs_n, seed=seed)):
        results.append(run_one(params, i, "Latin Hypercube"))

    for i, params in enumerate(sobol_samples(PARAM_NAMES, PARAM_RANGES, sobol_n, seed=seed)):
        results.append(run_one(params, i, "Sobol"))

    for i, params in enumerate(orthogonal_array_samples(PARAM_NAMES, PARAM_RANGES)):
        results.append(run_one(params, i, "Orthogonal Array (L9)"))

    return pd.DataFrame(results)


def write_report(df, output_path):
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for method in df["method"].unique():
            sheet_name = method[:31]  # Excel sheet name limit
            df[df["method"] == method].to_excel(writer, sheet_name=sheet_name, index=False)

        summary_rows = []
        for method, group in df.groupby("method"):
            summary_rows.append({
                "method": method,
                "n_trials": len(group),
                "mean_improvement_pct": group["improvement_pct"].mean(),
                "std_improvement_pct": group["improvement_pct"].std(),
                "min_improvement_pct": group["improvement_pct"].min(),
                "max_improvement_pct": group["improvement_pct"].max(),
                "qpso_win_rate": group["qpso_wins"].mean() * 100,
                "mean_qpso_runtime_ms": group["qpso_runtime_ms"].mean(),
                "mean_nn_runtime_ms": group["nn_runtime_ms"].mean(),
            })
        pd.DataFrame(summary_rows).to_excel(writer, sheet_name="Summary", index=False)

        df.to_excel(writer, sheet_name="All Trials", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="golden_eval_results.xlsx")
    parser.add_argument("--lhs-samples", type=int, default=8)
    parser.add_argument("--sobol-samples", type=int, default=8)
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    start = time.time()
    df = run_golden_eval(lhs_n=args.lhs_samples, sobol_n=args.sobol_samples, seed=args.seed)
    write_report(df, args.output)
    elapsed = time.time() - start

    print(f"Ran {len(df)} trials across 3 sampling methods in {elapsed:.1f}s")
    print(f"Overall QPSO win rate: {df['qpso_wins'].mean()*100:.1f}%")
    print(f"Overall mean improvement: {df['improvement_pct'].mean():.2f}%")
    print(f"Written to: {args.output}")
