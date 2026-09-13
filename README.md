# Quantum-Inspired Traffic Route Optimization (QPSO)

**SIH 2026 — Problem Statement SIH26137** · Egreen Quanta · Quantum Technology Vertical

A quantum-inspired metaheuristic (QPSO) that finds near-optimal delivery
routes — first on a simulated traffic network (Phase 1), then on a real
CVRP dataset routed through a congested road-network graph with vehicle
capacity constraints (Phase 2) — benchmarked against classical algorithms.

> Full step-by-step explanation of every algorithm: [`docs/algorithms.md`](docs/algorithms.md)

## Algorithms used

| Algorithm | Type | Used for | Where |
|---|---|---|---|
| **QPSO** (Quantum-behaved Particle Swarm Optimization) | Quantum-inspired metaheuristic | Finding the best order to visit delivery points | `qpso.py`, `cvrp_qpso.py` |
| **Dijkstra's algorithm** | Exact shortest-path algorithm | Finding the cheapest path between any two points on the road graph | `baseline.py`, `qpso.py` (`precompute_segment_costs`), `cvrp_qpso.py` |
| **Nearest-Neighbor heuristic** | Classical greedy heuristic | Baseline route to compare QPSO against | `baseline.py`, `cvrp_baseline.py` |
| **k-Nearest-Neighbor graph construction** | Graph modelling | Turning a set of points into a realistic sparse road network | `graph_model.py`, `cvrp_graph.py` |
| **Congestion simulation** | Random weighting model | Making edge travel-time vary like real traffic | `graph_model.py` (`apply_congestion`) |
| **Multi-trip capacity repair** | Constraint-handling rule | Forcing a route back to the depot when the vehicle is full | `cvrp_qpso.py`, `cvrp_baseline.py` |

*(Images/diagrams for each algorithm to be added here later.)*

## Benchmarking methods used

| Method | Answers the question | Where |
|---|---|---|
| Multi-seed benchmark | Is QPSO's improvement consistent, or just a lucky run? | `benchmark.py` |
| Scalability sweep | Does QPSO still win as the problem gets bigger? | `benchmark.py` |
| Multi-instance benchmark | Does QPSO work on real data, not just synthetic graphs? | `cvrp_benchmark.py` |

## Repo structure

```
graph_model.py      # Phase 1: synthetic road network + congestion
baseline.py         # Phase 1: Dijkstra + Nearest-Neighbor baselines
qpso.py             # Phase 1: core QPSO algorithm
benchmark.py         # Phase 1: multi-seed benchmark + scalability sweep

cvrp_loader.py       # Phase 2: loads the real CVRP dataset
cvrp_graph.py        # Phase 2: builds sparse congested graph from real coordinates
cvrp_qpso.py         # Phase 2: QPSO with multi-trip capacity handling
cvrp_baseline.py     # Phase 2: matching Nearest-Neighbor baseline
cvrp_benchmark.py    # Phase 2: benchmark across many real instances

gradio_app.py        # Gradio UI — 5 tabs covering both phases
upload_dataset.py    # Colab helper to upload a new .npz dataset

requirements.txt
SETUP.md             # how to run this (Colab first, then local)
data/
  cvrp_10.npz        # real CVRP benchmark dataset (100 instances)
docs/
  algorithms.md       # step-by-step explanation of every algorithm
  images/             # (diagrams to be added)
```

## Quickstart

```bash
pip install -r requirements.txt
python gradio_app.py
```

See [`SETUP.md`](SETUP.md) for Colab instructions.

## Status

**Phase 1 (synthetic traffic graph):** graph modelling, QPSO, classical
baseline, convergence analysis, multi-seed benchmarking, scalability
sweep — all done.

**Phase 2 (real CVRP dataset):** real dataset loading, sparse congested
graph over real coordinates, capacity constraint via multi-trip depot
returns, matching baseline, multi-instance benchmarking — all done.

**Not yet done:** multi-vehicle routing (multiple vehicles at once, not
just one vehicle doing multiple trips), a second metaheuristic baseline
(e.g. Genetic Algorithm) for a stronger "conventional metaheuristics"
comparison, live/real-time traffic data instead of simulated congestion.
