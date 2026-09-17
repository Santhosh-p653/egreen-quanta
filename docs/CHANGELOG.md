# Engine & Algorithm Change Log

This document records all architectural updates, new algorithm implementations, bug fixes, and documentation modularizations in the **`egreen-quanta`** engine.

---

## [2026-09-17] — Deterministic Explainability Layer & Fullstack Root Cleanup

### 1. Root Directory & Workspace Separation
* **Root Cleanup:** Removed all duplicate Python files from repository root (`baseline.py`, `cheapest_insertion.py`, `clarke_wright.py`, `qpso.py`, `qwoa.py`, `requirements.txt`, etc.), ensuring the root strictly contains `frontend/`, `backend/`, `tests/`, `docs/`, `Dockerfile`, and configuration files.
* **Dockerfile & CI Update:** Updated root `Dockerfile` and GitHub Actions workflows to build and execute cleanly from `backend/`.
* **Dataset Robustness:** Updated `backend/cvrp_loader.py` to resolve dataset paths relative to module location regardless of runtime working directory.

### 2. Deterministic Explainability Layer (`backend/explainability.py`)
* **Core Philosophy:** 100% deterministic, evidence-based reasoning derived exclusively from road network distances, travel times, vehicle capacity, and congestion levels. Zero external generative AI, LLM APIs, or stochastic text generators.
* **Structured Output:** Emits a typed JSON object conforming to future LLM ingestion schemas (`vehicle`, `selected_route`, `metrics`, `reasons`, `constraints`, `tradeoffs`, `alternative`, `decision`, `human_readable`).
* **Deterministic Template:** Generates the required human-readable operations report with section headers, checkmarks (`✓`/`✗`), and explicit trade-off statements.
* **API Endpoints:**
  - Integrated `explanation` and `alternative_route` directly into `POST /api/optimize`.
  - Added dedicated `POST /api/explain` and `GET /api/routes/{route_id}/explanation` endpoints.

### 3. Frontend Explainability & Yellow Alternative Route
* **Yellow Alternative Route Styling (`#F5A623`):** Suggested alternative route candidate (Clarke-Wright Savings) is rendered in distinct yellow/amber on the Leaflet map and inside the UI cards to differentiate clearly from optimal (green) and baseline (red).
* **`RouteExplanationCard` Component:** Integrated into Column 3 (Results Panel) with vehicle assignment, reason badges, constraint checks, key trade-offs, alternative route metrics, decision summary, and one-click copy of the deterministic template.

### 4. Automated Test Suite (`tests/`)
* Added `tests/test_explainability.py` and `tests/test_api_explainability.py` covering valid schemas, constraints, missing alternatives, trade-offs, multiple vehicles, missing metrics, zero optimizer mutation, and FastAPI endpoints. 11/11 tests pass.

---

## [2026-09-17] — Algorithm Suite Expansion & Modular Documentation Refactor

### 1. New Algorithm Implementations

#### A. Clarke-Wright Savings Algorithm (`clarke_wright.py`)
* **Priority:** Highest (Industry-standard classical CVRP baseline).
* **Scope:** Phase 1 (`clarke_wright_route`) and Phase 2 (`clarke_wright_cvrp`).
* **Mathematical Core:**
  $$S_{ij} = c(i, \text{depot}) + c(\text{depot}, j) - c(i, j)$$
  using Dijkstra shortest-path costs on the congested road network graph.
* **Mechanism:**
  - Evaluates savings matrix for all customer pairs $(i, j)$ with $i \neq j$.
  - Iteratively merges disjoint subroutes respecting capacity ($\sum_{u \in R_a} d_u + \sum_{v \in R_b} d_v \le C$) and endpoint adjacency.
  - Returns standardized dictionary format with route, graph travel cost, number of trips, and execution latency.

#### B. Cheapest Insertion Heuristic (`cheapest_insertion.py`)
* **Priority:** Second Classical Baseline (Greedy diversity beyond Nearest-Neighbor).
* **Scope:** Phase 1 (`cheapest_insertion_route`) and Phase 2 (`cheapest_insertion_cvrp`).
* **Mathematical Core:**
  $$\Delta c(u, k, v) = c(u, k) + c(k, v) - c(u, v)$$
* **Mechanism:**
  - Evaluates inserting pending customer $k$ between any adjacent stops $(u, v)$ across all capacity-feasible trips.
  - Simultaneously compares with opening a new trip $[v_0, k, v_0]$ with $\Delta c_{\text{new}} = c(v_0, k) + c(k, v_0)$.
  - Eliminates the myopic horizon trap of Nearest-Neighbor by allowing customer insertions anywhere along active edges.

#### C. Quantum Walk Optimization Algorithm — Classical State-Vector Simulation (`qwoa.py`)
* **Priority:** Quantum Differentiation (True quantum state-vector simulation, not merely quantum-inspired).
* **Scope:** Small-scale instances ($\le 8$ nodes, $D = n!$ states).
* **Mathematical Core:**
  - Computational basis: Permutation subspace $\mathcal{H}_{S_n} = \text{span}\{|\pi\rangle : \pi \in S_n\}$ of dimension $D = n!$.
  - Problem Hamiltonian: Diagonal cost operator $H_C = \sum_{\pi} C(\pi) |\pi\rangle\langle\pi|$.
  - Mixer Hamiltonian: Continuous-time quantum walk on the Cayley graph of $S_n$ under adjacent transpositions:
    $$H_M = \sum_{\pi} \sum_{\tau \in \text{Transpositions}} |\tau \cdot \pi\rangle \langle \pi|$$
  - State propagation:
    $$|\psi(\boldsymbol{\gamma}, \boldsymbol{\beta})\rangle = \prod_{l=1}^p \left( e^{-i \beta_l H_M} e^{-i \gamma_l H_C} \right) |\psi_0\rangle$$
    computed using `scipy.sparse.linalg.expm_multiply`.
  - Measurement: Born rule $P(\pi) = |\psi_\pi|^2$ with Nelder-Mead parameter auto-tuning, demonstrating constructive interference and probability amplification of the ground-state route.

---

### 2. Core Engine Updates & Bug Fixes

#### A. Removal of Jupyter Notebook Cell Magics
* Removed corrupted `%%writefile` lines from the top of:
  - [`cvrp_graph.py`](file:///c:/Users/Nivetha%20A/OneDrive/Documents/egreen-quanta/cvrp_graph.py)
  - [`cvrp_qpso.py`](file:///c:/Users/Nivetha%20A/OneDrive/Documents/egreen-quanta/cvrp_qpso.py)
  - [`cvrp_baseline.py`](file:///c:/Users/Nivetha%20A/OneDrive/Documents/egreen-quanta/cvrp_baseline.py)
* Restored native Python script execution and module importability.

#### B. Baseline Interface Standardization
* Updated [`cvrp_baseline.py`](file:///c:/Users/Nivetha%20A/OneDrive/Documents/egreen-quanta/cvrp_baseline.py) and [`baseline.py`](file:///c:/Users/Nivetha%20A/OneDrive/Documents/egreen-quanta/baseline.py) to export:
  - `nearest_neighbor_cvrp`, `clarke_wright_cvrp`, `cheapest_insertion_cvrp`
  - `nearest_neighbor_route`, `clarke_wright_route`, `cheapest_insertion_route`
* Added explicit `"feasible": True` flag to all solver outputs.

#### C. Multi-Baseline CVRP Benchmark Suite
* Updated [`cvrp_benchmark.py`](file:///c:/Users/Nivetha%20A/OneDrive/Documents/egreen-quanta/cvrp_benchmark.py) to benchmark all four algorithms side-by-side:
  - QPSO vs. Nearest-Neighbor vs. Clarke-Wright Savings vs. Cheapest Insertion.
  - Tracks individual and mean costs, trip counts, and execution runtimes across multiple real dataset instances.

---

### 3. Documentation Modularization

Split `docs/algorithms.md` into 11 dedicated, deep-dive technical documents in [`docs/algorithms/`](file:///c:/Users/Nivetha%20A/OneDrive/Documents/egreen-quanta/docs/algorithms):

1. [`01_knn_graph.md`](file:///c:/Users/Nivetha%20A/OneDrive/Documents/egreen-quanta/docs/algorithms/01_knn_graph.md): $k$-NN sparse graph modeling & island reconnection.
2. [`02_traffic_congestion.md`](file:///c:/Users/Nivetha%20A/OneDrive/Documents/egreen-quanta/docs/algorithms/02_traffic_congestion.md): Stochastic edge congestion model.
3. [`03_dijkstra.md`](file:///c:/Users/Nivetha%20A/OneDrive/Documents/egreen-quanta/docs/algorithms/03_dijkstra.md): Dijkstra point-to-point shortest paths & segment lookup tables.
4. [`04_nearest_neighbor.md`](file:///c:/Users/Nivetha%20A/OneDrive/Documents/egreen-quanta/docs/algorithms/04_nearest_neighbor.md): Greedy Nearest-Neighbor heuristic & greedy horizon traps.
5. [`05_qpso.md`](file:///c:/Users/Nivetha%20A/OneDrive/Documents/egreen-quanta/docs/algorithms/05_qpso.md): Quantum-behaved PSO, delta-potential well mechanics, and $m_{\text{best}}$ contraction.
6. [`06_permutation_encoding.md`](file:///c:/Users/Nivetha%20A/OneDrive/Documents/egreen-quanta/docs/algorithms/06_permutation_encoding.md): Priority-based random key continuous-to-discrete decoding.
7. [`07_capacity_repair.md`](file:///c:/Users/Nivetha%20A/OneDrive/Documents/egreen-quanta/docs/algorithms/07_capacity_repair.md): Multi-trip depot return constraint handling.
8. [`08_clarke_wright.md`](file:///c:/Users/Nivetha%20A/OneDrive/Documents/egreen-quanta/docs/algorithms/08_clarke_wright.md): Clarke-Wright Savings algorithm, savings matrix, and capacity merge rules.
9. [`09_cheapest_insertion.md`](file:///c:/Users/Nivetha%20A/OneDrive/Documents/egreen-quanta/docs/algorithms/09_cheapest_insertion.md): Cheapest Insertion heuristic, incremental cost minimization $\Delta c$, and subroute expansion.
10. [`10_qwoa_quantum_walk.md`](file:///c:/Users/Nivetha%20A/OneDrive/Documents/egreen-quanta/docs/algorithms/10_qwoa_quantum_walk.md): QWOA state-vector simulation, permutation Hilbert space, Hamiltonians, unitary evolution, and interference demonstration.
11. [`11_benchmarking.md`](file:///c:/Users/Nivetha%20A/OneDrive/Documents/egreen-quanta/docs/algorithms/11_benchmarking.md): Multi-seed, scalability sweep, and multi-instance benchmark methodologies.

---

### 4. UI Status
* Per instructions, [`gradio_app.py`](file:///c:/Users/Nivetha%20A/OneDrive/Documents/egreen-quanta/gradio_app.py) remains completely untouched until the engine work is finalized and approved.

---

### 5. Containerization & CI/CD Pipeline
* **[NEW] [`.gitignore`](file:///c:/Users/Nivetha%20A/OneDrive/Documents/egreen-quanta/.gitignore):** Comprehensive exclusions for Python artifacts, virtual environments (`.venv`), Jupyter checkpoints, and build files.
* **[NEW] [`Dockerfile`](file:///c:/Users/Nivetha%20A/OneDrive/Documents/egreen-quanta/Dockerfile):** Production container configuration utilizing `python:3.12-slim`, pre-configured with `GRADIO_SERVER_NAME="0.0.0.0"` and `GRADIO_SERVER_PORT=7860`, exposing port `7860` for web UI access.
* **[NEW] [`.dockerignore`](file:///c:/Users/Nivetha%20A/OneDrive/Documents/egreen-quanta/.dockerignore):** Excludes `.git`, `.github`, cache directories, and temporary data from Docker build contexts.
* **[NEW] [`.github/workflows/containerize.yml`](file:///c:/Users/Nivetha%20A/OneDrive/Documents/egreen-quanta/.github/workflows/containerize.yml):** GitHub Actions workflow to build, tag, and publish Docker container images directly to GitHub Container Registry (`ghcr.io`), featuring Buildx build caching and automated image versioning tags.

---

### 6. Operations Dashboard Migration (FastAPI + Next.js)
* **[NEW] [`osm_road_network.py`](file:///c:/Users/Nivetha%20A/OneDrive/Documents/egreen-quanta/osm_road_network.py):** Authentic Coimbatore road network graph featuring 12 landmark nodes with genuine GPS coordinates (~11.00–11.08° N, ~76.92–77.05° E), arterial roads (Avinashi, Trichy, Sathy, Mettupalayam), dynamic traffic congestion, and polyline route geometry generation.
* **[NEW] [`classical_pso.py`](file:///c:/Users/Nivetha%20A/OneDrive/Documents/egreen-quanta/classical_pso.py):** Standard velocity- and inertia-driven Particle Swarm Optimization baseline ($v_{t+1} = w v_t + c_1 r_1 (p - x) + c_2 r_2 (g - x)$) to demonstrate the classical swarm baseline that QPSO outperforms.
* **[NEW] [`ga.py`](file:///c:/Users/Nivetha%20A/OneDrive/Documents/egreen-quanta/ga.py):** Genetic Algorithm baseline supporting both Order Crossover (GA-OX) and Partially Mapped Crossover (GA-PMX).
* **[NEW] [`api.py`](file:///c:/Users/Nivetha%20A/OneDrive/Documents/egreen-quanta/api.py):** FastAPI backend providing `/api/optimize`, `/api/compare`, `/api/algorithms`, `/api/network/landmarks`, and WebSocket streaming (`/api/optimize/stream`).
* **[NEW] [`frontend/`](file:///c:/Users/Nivetha%20A/OneDrive/Documents/egreen-quanta/frontend):** Next.js (App Router, TypeScript, Tailwind CSS) operations dashboard:
  - **Design Tokens:** Strict traffic-signal semantics (`signal-red` for before/congestion, `signal-amber` for in-progress, `signal-green` for after/optimized) across Dark and Light modes (`next-themes`).
  - **Typography:** IBM Plex Sans for general UI text; IBM Plex Mono strictly for numeric readouts.
  - **Persistent 3-Column Layout:** Left Input Panel (always visible), Center Canvas (Live Simulation with real Leaflet Coimbatore map, Compare Algorithms, Performance Trends), Right Results Panel (always visible).
  - **Convergence Graph:** Flat red reference line at baseline cost, green QPSO curve, highlighted crossover point (*"the moment QPSO beat baseline"*), and terminal cost label.
  - **Anti-Pattern Compliance:** No purple/violet gradients, no warm cream/terracotta, no decorative monospace, and zero internal phase jargon.
