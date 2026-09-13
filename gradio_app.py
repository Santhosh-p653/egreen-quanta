"""
gradio_app.py — Gradio demo for the QPSO traffic-routing project.

Phase 1 (synthetic traffic graph):
  Tab 1: Single run       — one seed, one graph, route + convergence plot
  Tab 2: Multi-seed bench — N trials at fixed size, mean/std improvement
  Tab 3: Scalability      — improvement % and runtime vs. node count

Phase 2 (real CVRP dataset, routed through a sparse congested graph,
with multi-trip capacity handling):
  Tab 4: CVRP single instance — one dataset instance, route + convergence
  Tab 5: CVRP benchmark        — QPSO vs NN across N real instances

Colab: run this cell — .launch(share=True) gives a public URL directly.
Local:  python gradio_app.py
"""

import random

import gradio as gr
import matplotlib.pyplot as plt
import networkx as nx

from graph_model import build_random_graph, apply_congestion
from baseline import nearest_neighbor_route
from qpso import qpso_optimize
from benchmark import multi_seed_benchmark, scalability_sweep

from cvrp_loader import load_dataset, get_instance, num_instances
from cvrp_graph import build_congested_graph
from cvrp_qpso import qpso_optimize_cvrp
from cvrp_baseline import nearest_neighbor_cvrp
from cvrp_benchmark import run_cvrp_benchmark

CVRP_DATA = load_dataset()
CVRP_MAX_IDX = num_instances(CVRP_DATA) - 1


# ---------- Tab 1: single run (Phase 1) ----------

def run_single(n_nodes, n_waypoints, n_particles, n_iterations, seed):
    seed = int(seed)
    G = build_random_graph(n_nodes=int(n_nodes), seed=seed)
    G = apply_congestion(G, seed=seed)

    random.seed(seed)
    depot = 0
    waypoints = random.sample([n for n in G.nodes if n != depot], int(n_waypoints))

    qpso_result = qpso_optimize(
        G, depot, waypoints,
        n_particles=int(n_particles), n_iterations=int(n_iterations), seed=seed,
    )
    nn_route, nn_cost, nn_runtime = nearest_neighbor_route(G, depot, waypoints)
    improvement = (nn_cost - qpso_result["cost"]) / nn_cost * 100

    summary = (
        f"### Results\n"
        f"- **QPSO route cost:** {qpso_result['cost']:.2f} min\n"
        f"- **Nearest-Neighbor baseline cost:** {nn_cost:.2f} min\n"
        f"- **QPSO improvement over baseline:** {improvement:.1f}%\n"
        f"- **QPSO runtime:** {qpso_result['runtime']*1000:.1f} ms | "
        f"**Baseline runtime:** {nn_runtime*1000:.1f} ms\n\n"
        f"**QPSO route:** {' → '.join(map(str, qpso_result['route']))}\n\n"
        f"**Baseline route:** {' → '.join(map(str, nn_route))}"
    )

    fig1, ax1 = plt.subplots()
    ax1.plot(qpso_result["history"], label="QPSO best cost")
    ax1.axhline(nn_cost, color="red", linestyle="--", label="NN baseline")
    ax1.set_xlabel("Iteration")
    ax1.set_ylabel("Best route cost (min)")
    ax1.set_title("Convergence")
    ax1.legend()

    fig2, ax2 = plt.subplots(figsize=(7, 6))
    pos = nx.spring_layout(G, seed=seed)
    nx.draw(G, pos, ax=ax2, node_color="lightgray", node_size=200,
            with_labels=True, edge_color="lightgray")
    nx.draw_networkx_nodes(G, pos, nodelist=[depot], node_color="green", node_size=400, ax=ax2)
    nx.draw_networkx_nodes(G, pos, nodelist=waypoints, node_color="orange", node_size=300, ax=ax2)
    route_edges = list(zip(qpso_result["route"], qpso_result["route"][1:]))
    nx.draw_networkx_edges(G, pos, edgelist=route_edges, edge_color="green", width=2, ax=ax2)
    ax2.set_title("Network with QPSO route highlighted")

    return summary, fig1, fig2


# ---------- Tab 2: multi-seed benchmark (Phase 1) ----------

def run_multi_seed(n_nodes, n_waypoints, n_particles, n_iterations, n_trials, base_seed):
    trials, summary = multi_seed_benchmark(
        n_nodes=int(n_nodes), n_waypoints=int(n_waypoints),
        n_particles=int(n_particles), n_iterations=int(n_iterations),
        n_trials=int(n_trials), base_seed=int(base_seed),
    )

    text = (
        f"### Multi-seed benchmark ({summary['n_trials']} trials)\n"
        f"- **Mean improvement over baseline:** {summary['mean_improvement_pct']:.2f}% "
        f"(± {summary['std_improvement_pct']:.2f})\n"
        f"- **Range:** {summary['min_improvement_pct']:.1f}% to {summary['max_improvement_pct']:.1f}%\n"
        f"- **QPSO won or tied in:** {summary['qpso_wins']}/{summary['n_trials']} trials\n"
        f"- **Mean QPSO cost:** {summary['mean_qpso_cost']:.2f} min | "
        f"**Mean baseline cost:** {summary['mean_nn_cost']:.2f} min"
    )

    improvements = [t["improvement_pct"] for t in trials]
    fig, ax = plt.subplots()
    ax.bar(range(1, len(improvements) + 1), improvements, color="steelblue")
    ax.axhline(summary["mean_improvement_pct"], color="red", linestyle="--",
               label=f"mean = {summary['mean_improvement_pct']:.1f}%")
    ax.set_xlabel("Trial (seed)")
    ax.set_ylabel("QPSO improvement over baseline (%)")
    ax.set_title("Improvement across independent trials")
    ax.legend()

    return text, fig


# ---------- Tab 3: scalability sweep (Phase 1) ----------

def run_scalability(node_min, node_max, node_step, n_waypoints, n_particles, n_iterations, seed):
    node_counts = list(range(int(node_min), int(node_max) + 1, int(node_step)))
    results = scalability_sweep(
        node_counts=node_counts, n_waypoints=int(n_waypoints),
        n_particles=int(n_particles), n_iterations=int(n_iterations), seed=int(seed),
    )

    rows = "\n".join(
        f"| {r['n_nodes']} | {r['qpso_cost']:.1f} | {r['nn_cost']:.1f} | "
        f"{r['improvement_pct']:.1f}% | {r['qpso_runtime_ms']:.1f} |"
        for r in results
    )
    text = (
        "### Scalability sweep\n\n"
        "| Nodes | QPSO cost | Baseline cost | Improvement | QPSO runtime (ms) |\n"
        "|---|---|---|---|---|\n" + rows
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
    nodes = [r["n_nodes"] for r in results]
    ax1.plot(nodes, [r["improvement_pct"] for r in results], marker="o")
    ax1.set_xlabel("Number of nodes")
    ax1.set_ylabel("Improvement over baseline (%)")
    ax1.set_title("Improvement vs. problem size")

    ax2.plot(nodes, [r["qpso_runtime_ms"] for r in results], marker="o", label="QPSO")
    ax2.plot(nodes, [r["nn_runtime_ms"] for r in results], marker="o", label="Baseline")
    ax2.set_xlabel("Number of nodes")
    ax2.set_ylabel("Runtime (ms)")
    ax2.set_title("Runtime vs. problem size")
    ax2.legend()
    fig.tight_layout()

    return text, fig


# ---------- Tab 4: CVRP single instance (Phase 2) ----------

def run_cvrp_single(instance_idx, k_neighbors, n_particles, n_iterations, seed):
    instance_idx = int(instance_idx)
    seed = int(seed)
    instance = get_instance(CVRP_DATA, instance_idx)

    q = qpso_optimize_cvrp(
        instance, k_neighbors=int(k_neighbors),
        n_particles=int(n_particles), n_iterations=int(n_iterations), seed=seed,
    )
    n = nearest_neighbor_cvrp(instance, k_neighbors=int(k_neighbors), seed=seed)
    improvement = (n["cost"] - q["cost"]) / n["cost"] * 100 if n["cost"] > 0 else 0.0

    summary = (
        f"### Results — instance {instance_idx}\n"
        f"- **Customers:** {len(instance['customers'])} | "
        f"**Capacity:** {instance['capacity']} | "
        f"**Total demand:** {int(instance['demands'].sum())}\n"
        f"- **QPSO cost:** {q['cost']:.2f}  ({q['n_trips']} depot trips)\n"
        f"- **Nearest-Neighbor cost:** {n['cost']:.2f}  ({n['n_trips']} depot trips)\n"
        f"- **QPSO improvement over baseline:** {improvement:.1f}%\n"
        f"- **QPSO runtime:** {q['runtime']*1000:.1f} ms | "
        f"**Baseline runtime:** {n['runtime']*1000:.1f} ms\n\n"
        f"**QPSO route:** {' → '.join(map(str, q['route']))}\n\n"
        f"**Baseline route:** {' → '.join(map(str, n['route']))}"
    )

    fig1, ax1 = plt.subplots()
    ax1.plot(q["history"], label="QPSO best cost")
    ax1.axhline(n["cost"], color="red", linestyle="--", label="NN baseline")
    ax1.set_xlabel("Iteration")
    ax1.set_ylabel("Best route cost")
    ax1.set_title("Convergence")
    ax1.legend()

    # Plot using real coordinates (not spring layout) — this is real
    # geography, so node positions should reflect actual locations.
    G = build_congested_graph(instance["locations"], k_neighbors=int(k_neighbors), seed=seed)
    locations = instance["locations"]
    pos = {i: (float(locations[i][0]), float(locations[i][1])) for i in G.nodes}

    fig2, ax2 = plt.subplots(figsize=(7, 6))
    nx.draw(G, pos, ax=ax2, node_color="lightgray", node_size=150,
            with_labels=True, edge_color="lightgray", width=0.5)
    nx.draw_networkx_nodes(G, pos, nodelist=[instance["depot"]],
                            node_color="green", node_size=350, ax=ax2)
    nx.draw_networkx_nodes(G, pos, nodelist=instance["customers"],
                            node_color="orange", node_size=250, ax=ax2)
    route_edges = list(zip(q["route"], q["route"][1:]))
    nx.draw_networkx_edges(G, pos, edgelist=route_edges, edge_color="green", width=2, ax=ax2)
    ax2.set_title(f"CVRP instance {instance_idx} — QPSO route (green = depot)")

    return summary, fig1, fig2


# ---------- Tab 5: CVRP multi-instance benchmark (Phase 2) ----------

def run_cvrp_multi(n_instances, start_idx, k_neighbors, n_particles, n_iterations, seed):
    trials, summary = run_cvrp_benchmark(
        n_instances=int(n_instances), start_idx=int(start_idx),
        k_neighbors=int(k_neighbors), n_particles=int(n_particles),
        n_iterations=int(n_iterations), seed=int(seed),
    )

    text = (
        f"### CVRP benchmark ({summary['n_instances']} real instances, "
        f"starting at index {int(start_idx)})\n"
        f"- **Mean improvement over baseline:** {summary['mean_improvement_pct']:.2f}% "
        f"(± {summary['std_improvement_pct']:.2f})\n"
        f"- **Range:** {summary['min_improvement_pct']:.1f}% to {summary['max_improvement_pct']:.1f}%\n"
        f"- **QPSO won or tied in:** {summary['qpso_wins']}/{summary['n_instances']} instances\n"
        f"- **Mean QPSO cost:** {summary['mean_qpso_cost']:.2f} | "
        f"**Mean baseline cost:** {summary['mean_nn_cost']:.2f}\n"
        f"- **Mean depot trips — QPSO:** {summary['mean_qpso_trips']:.2f} | "
        f"**Baseline:** {summary['mean_nn_trips']:.2f}"
    )

    improvements = [t["improvement_pct"] for t in trials]
    fig, ax = plt.subplots()
    ax.bar(range(1, len(improvements) + 1), improvements, color="seagreen")
    ax.axhline(summary["mean_improvement_pct"], color="red", linestyle="--",
               label=f"mean = {summary['mean_improvement_pct']:.1f}%")
    ax.set_xlabel("Instance (offset from start index)")
    ax.set_ylabel("QPSO improvement over baseline (%)")
    ax.set_title("Improvement across real CVRP instances")
    ax.legend()

    return text, fig


# ---------- UI ----------

with gr.Blocks(title="QPSO Traffic & CVRP Routing") as demo:
    gr.Markdown("# Quantum-Inspired Route Optimization (QPSO)")
    gr.Markdown("SIH26137 — Egreen Quanta, Quantum Technology Vertical")

    with gr.Tabs():
        with gr.Tab("Phase 1: Single run (synthetic traffic)"):
            with gr.Row():
                with gr.Column(scale=1):
                    s_nodes = gr.Slider(10, 40, value=20, step=1, label="Number of intersections (nodes)")
                    s_wp = gr.Slider(2, 8, value=5, step=1, label="Number of delivery waypoints")
                    s_particles = gr.Slider(10, 80, value=30, step=1, label="QPSO swarm size")
                    s_iters = gr.Slider(20, 300, value=100, step=1, label="QPSO iterations")
                    s_seed = gr.Number(value=1, label="Random seed")
                    s_btn = gr.Button("Run simulation", variant="primary")
                with gr.Column(scale=2):
                    s_summary = gr.Markdown()
            with gr.Row():
                s_conv = gr.Plot(label="Convergence curve")
                s_graph = gr.Plot(label="Network graph")
            s_btn.click(run_single, [s_nodes, s_wp, s_particles, s_iters, s_seed],
                        [s_summary, s_conv, s_graph])

        with gr.Tab("Phase 1: Multi-seed benchmark"):
            gr.Markdown("Runs QPSO vs. baseline across N independent seeds at a fixed "
                        "problem size — use this to report mean ± std improvement instead "
                        "of a single run's number.")
            with gr.Row():
                with gr.Column(scale=1):
                    m_nodes = gr.Slider(10, 40, value=20, step=1, label="Number of nodes")
                    m_wp = gr.Slider(2, 8, value=5, step=1, label="Number of waypoints")
                    m_particles = gr.Slider(10, 80, value=30, step=1, label="QPSO swarm size")
                    m_iters = gr.Slider(20, 300, value=100, step=1, label="QPSO iterations")
                    m_trials = gr.Slider(3, 30, value=10, step=1, label="Number of trials (seeds)")
                    m_seed = gr.Number(value=1, label="Base seed")
                    m_btn = gr.Button("Run benchmark", variant="primary")
                with gr.Column(scale=2):
                    m_summary = gr.Markdown()
            m_plot = gr.Plot(label="Improvement per trial")
            m_btn.click(run_multi_seed, [m_nodes, m_wp, m_particles, m_iters, m_trials, m_seed],
                        [m_summary, m_plot])

        with gr.Tab("Phase 1: Scalability sweep"):
            gr.Markdown("Runs one trial at each node count — use this to show how QPSO's "
                        "improvement and runtime behave as problem size grows.")
            with gr.Row():
                with gr.Column(scale=1):
                    sc_min = gr.Slider(10, 60, value=10, step=5, label="Min nodes")
                    sc_max = gr.Slider(10, 100, value=50, step=5, label="Max nodes")
                    sc_step = gr.Slider(5, 20, value=10, step=5, label="Step")
                    sc_wp = gr.Slider(2, 8, value=5, step=1, label="Number of waypoints")
                    sc_particles = gr.Slider(10, 80, value=30, step=1, label="QPSO swarm size")
                    sc_iters = gr.Slider(20, 300, value=100, step=1, label="QPSO iterations")
                    sc_seed = gr.Number(value=1, label="Seed")
                    sc_btn = gr.Button("Run sweep", variant="primary")
                with gr.Column(scale=2):
                    sc_summary = gr.Markdown()
            sc_plot = gr.Plot(label="Scalability plots")
            sc_btn.click(run_scalability,
                         [sc_min, sc_max, sc_step, sc_wp, sc_particles, sc_iters, sc_seed],
                         [sc_summary, sc_plot])

        with gr.Tab("Phase 2: CVRP single instance"):
            gr.Markdown("Routes a real CVRP dataset instance through a sparse congested "
                        "graph (not straight-line distance), with genuine multi-trip "
                        "capacity handling — exceeding capacity mid-route forces a real "
                        "depot reload, which QPSO has to plan around.")
            with gr.Row():
                with gr.Column(scale=1):
                    c_idx = gr.Slider(0, CVRP_MAX_IDX, value=0, step=1, label="Dataset instance index")
                    c_k = gr.Slider(2, 8, value=4, step=1, label="Graph connectivity (k nearest neighbors)")
                    c_particles = gr.Slider(10, 80, value=30, step=1, label="QPSO swarm size")
                    c_iters = gr.Slider(20, 300, value=100, step=1, label="QPSO iterations")
                    c_seed = gr.Number(value=1, label="Random seed")
                    c_btn = gr.Button("Run simulation", variant="primary")
                with gr.Column(scale=2):
                    c_summary = gr.Markdown()
            with gr.Row():
                c_conv = gr.Plot(label="Convergence curve")
                c_graph = gr.Plot(label="Real-coordinate network with QPSO route")
            c_btn.click(run_cvrp_single, [c_idx, c_k, c_particles, c_iters, c_seed],
                        [c_summary, c_conv, c_graph])

        with gr.Tab("Phase 2: CVRP benchmark"):
            gr.Markdown("Runs QPSO vs. Nearest-Neighbor across N real dataset instances "
                        "(not synthetic random seeds) — systematic benchmarking on real "
                        "CVRP data, per the problem statement's requirement.")
            with gr.Row():
                with gr.Column(scale=1):
                    cm_n = gr.Slider(3, 30, value=15, step=1, label="Number of instances")
                    cm_start = gr.Slider(0, CVRP_MAX_IDX, value=0, step=1, label="Start index")
                    cm_k = gr.Slider(2, 8, value=4, step=1, label="Graph connectivity (k)")
                    cm_particles = gr.Slider(10, 80, value=30, step=1, label="QPSO swarm size")
                    cm_iters = gr.Slider(20, 300, value=100, step=1, label="QPSO iterations")
                    cm_seed = gr.Number(value=1, label="Seed")
                    cm_btn = gr.Button("Run benchmark", variant="primary")
                with gr.Column(scale=2):
                    cm_summary = gr.Markdown()
            cm_plot = gr.Plot(label="Improvement per instance")
            cm_btn.click(run_cvrp_multi,
                         [cm_n, cm_start, cm_k, cm_particles, cm_iters, cm_seed],
                         [cm_summary, cm_plot])

if __name__ == "__main__":
    demo.launch(share=True)
