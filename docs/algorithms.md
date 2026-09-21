# Algorithms Suite Overview

This directory contains the mathematical intuition, step-by-step algorithms, failure mode analyses, and Mermaid flowcharts for all methods implemented in the **`egreen-quanta`** engine.

To provide clear, in-depth documentation, each algorithm is documented in its own dedicated document:

---

## Algorithm Index

| # | Document | Category | Key Equations / Concept | Implementation |
|---|---|---|---|---|
| **01** | [**$k$-NN Sparse Graph Construction**](algorithms/01_knn_graph.md) | Graph Modeling | $d(u, v) = \|\mathbf{x}_u - \mathbf{x}_v\|_2$, $E = E_{\text{raw}} \cup \text{Islands}$ | [`graph_model.py`](../graph_model.py), [`cvrp_graph.py`](../cvrp_graph.py) |
| **02** | [**Stochastic Traffic Congestion**](algorithms/02_traffic_congestion.md) | Traffic Modeling | $w(u, v) = w_{\text{base}}(u, v) \times \mathcal{U}(1.0, 2.5)$ | [`graph_model.py`](../graph_model.py) |
| **03** | [**Dijkstra Shortest Path**](algorithms/03_dijkstra.md) | Pathfinding | $\min \sum w(u, v)$ & All-Pairs precomputed $\mathbf{C}_{uv}$ | [`baseline.py`](../baseline.py), [`qpso.py`](../qpso.py) |
| **04** | [**Nearest-Neighbor Heuristic**](algorithms/04_nearest_neighbor.md) | Classical Greedy Baseline | $v_{t+1} = \arg\min c(v_t, u)$ (Myopic greedy search) | [`baseline.py`](../baseline.py), [`cvrp_baseline.py`](../cvrp_baseline.py) |
| **05** | [**QPSO**](algorithms/05_qpso.md) | Quantum-Inspired Metaheuristic | $\mathbf{x} = \mathbf{p} \pm \beta \|m_{\text{best}} - \mathbf{x}\| \ln(1/\mathbf{u})$ | [`qpso.py`](../qpso.py), [`cvrp_qpso.py`](../cvrp_qpso.py) |
| **06** | [**Priority Permutation Encoding**](algorithms/06_permutation_encoding.md) | Representation Mapping | $\pi = \text{argsort}(\mathbf{x}) \implies \mathbb{R}^D \to S_D$ | [`qpso.py`](../qpso.py), [`cvrp_qpso.py`](../cvrp_qpso.py) |
| **07** | [**Multi-Trip Capacity Repair**](algorithms/07_capacity_repair.md) | CVRP Constraint Handling | $\text{If } L + d_c > C \implies \text{depot return}$ | [`cvrp_qpso.py`](../cvrp_qpso.py), [`cvrp_baseline.py`](../cvrp_baseline.py) |
| **08** | [**Clarke-Wright Savings**](algorithms/08_clarke_wright.md) | Industry-Standard CVRP Baseline | $S_{ij} = c(i, 0) + c(0, j) - c(i, j)$ | [`clarke_wright.py`](../clarke_wright.py) |
| **09** | [**Cheapest Insertion Heuristic**](algorithms/09_cheapest_insertion.md) | Classical Greedy Diversity | $\Delta c = c(u, k) + c(k, v) - c(u, v)$ | [`cheapest_insertion.py`](../cheapest_insertion.py) |
| **10** | [**QWOA (State-Vector Quantum Walk)**](algorithms/10_qwoa_quantum_walk.md) | True Quantum Simulation | $|\psi\rangle = \prod e^{-i\beta H_M} e^{-i\gamma H_C} |\psi_0\rangle$ on $S_n$ | [`qwoa.py`](../qwoa.py) |
| **11** | [**Benchmarking Methodologies**](algorithms/11_benchmarking.md) | Evaluation & Validation | Multi-seed, scalability sweep, multi-instance | [`benchmark.py`](../benchmark.py), [`cvrp_benchmark.py`](../cvrp_benchmark.py) |
| **12** | [**Quantum-Inspired Bidirectional A* (QI-BA*)**](algorithms/12_quantum_bidirectional_astar.md) | Quantum Graph Search | Dual wavepackets, $\delta$-well tunneling, and constructive interference | [`quantum_bidirectional_astar.py`](../backend/quantum_bidirectional_astar.py) |

---

## Change Log
For a full audit of all new implementations, equation derivations, and bug fixes, refer to [`docs/CHANGELOG.md`](CHANGELOG.md).
