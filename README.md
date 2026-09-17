# Quantum-Inspired Traffic Route Optimization (QPSO)

**SIH 2026 — Problem Statement SIH26137** · Egreen Quanta · Quantum Technology Vertical

A production-grade traffic route optimization engine and operational dashboard that finds near-optimal delivery routes over the **real Coimbatore road network** (fetched via OpenStreetMap / OSMnx) and standard benchmark datasets. The system benchmarks **Quantum-behaved Particle Swarm Optimization (QPSO)** and **Quantum Walk State-Vector Simulation (QWOA)** against classical metaheuristics and industry-standard heuristics.

---

## System Architecture

The project is organized as a clean, decoupled fullstack system:

```
egreen-quanta/
├── backend/                  # Python FastAPI service & core optimization engine
│   ├── api.py                # RESTful & WebSocket streaming API with explainability endpoints
│   ├── explainability.py     # Deterministic Explainability Layer (zero LLMs / template & JSON)
│   ├── osm_road_network.py   # Real Coimbatore road network & GPS coordinates
│   ├── qpso.py               # Quantum-behaved Particle Swarm Optimization
│   ├── classical_pso.py      # Classical velocity- & inertia-driven PSO
│   ├── ga.py                 # Genetic Algorithm (GA-OX and GA-PMX)
│   ├── clarke_wright.py      # Clarke-Wright Savings heuristic
│   ├── cheapest_insertion.py # Cheapest Insertion heuristic
│   ├── qwoa.py               # Quantum Walk Optimization (classical state-vector)
│   ├── baseline.py           # Dijkstra shortest path & Nearest-Neighbor
│   ├── cvrp_qpso.py          # Capacitated VRP solver with multi-trip reload
│   ├── cvrp_baseline.py      # Matching classical baselines for CVRP
│   ├── cvrp_benchmark.py     # Multi-instance benchmark runner
│   ├── requirements.txt      # Python dependencies
│   └── data/                 # CVRP benchmark dataset (.npz)
├── frontend/                 # Next.js 14 App Router operational dashboard
│   ├── src/app/              # Page routes, layout, and global styles
│   ├── src/components/       # MapComponent, RouteExplanationCard, ConvergenceChart, CompareView
│   ├── tailwind.config.ts    # Traffic-signal design tokens (Dark/Light)
│   └── package.json          # Node.js dependencies
├── tests/                    # Automated verification test suite
│   ├── test_explainability.py      # Unit tests for explanation generation & constraints
│   └── test_api_explainability.py  # FastAPI integration tests for /api/optimize & /api/explain
├── docs/                     # Technical documentation & audit logs
│   ├── algorithms/           # 11 individual modular algorithm specifications
│   ├── algorithms.md         # Master algorithm index
│   ├── Intuition.md          # In-depth mathematics, concepts, and failure modes
│   └── CHANGELOG.md          # Engine change and implementation audit log
├── Dockerfile                # Root container specification for GHCR deployment
├── .github/workflows/        # Automated CI/CD pipelines (GHCR & golden evals)
├── .gitattributes            # Line-ending normalization (LF)
└── .gitignore                # Repository exclusions
```

---

## Algorithms Implemented

| Algorithm | Category | Role | Primary File |
|---|---|---|---|
| **QPSO** | Quantum-Inspired Metaheuristic | Primary route optimization engine | [`backend/qpso.py`](backend/qpso.py) |
| **QWOA** | True Quantum Simulation | Schrödinger state-vector simulation on $S_n$ | [`backend/qwoa.py`](backend/qwoa.py) |
| **Classical PSO** | Swarm Intelligence | Velocity- and momentum-based baseline | [`backend/classical_pso.py`](backend/classical_pso.py) |
| **GA-OX & GA-PMX** | Evolutionary Algorithms | Order and Partially Mapped Crossover | [`backend/ga.py`](backend/ga.py) |
| **Clarke-Wright Savings** | Classical Heuristic | Industry-standard CVRP savings matrix | [`backend/clarke_wright.py`](backend/clarke_wright.py) |
| **Cheapest Insertion** | Greedy Family Heuristic | Detour cost minimization along tour edges | [`backend/cheapest_insertion.py`](backend/cheapest_insertion.py) |
| **Nearest-Neighbor** | Greedy Baseline | Myopic proximity baseline | [`backend/baseline.py`](backend/baseline.py) |
| **Dijkstra's Algorithm** | Exact Pathfinding | Metric closure segment cost precomputation | [`backend/baseline.py`](backend/baseline.py) |
| **Multi-Trip Capacity Repair** | Constraint Handling | Dynamic vehicle capacity reload handling | [`backend/cvrp_qpso.py`](backend/cvrp_qpso.py) |

> In-depth mathematical formulas, concepts, and edge cases are documented in [`docs/Intuition.md`](docs/Intuition.md) and [`docs/algorithms/`](docs/algorithms/).

---

## Operations Dashboard (UI)

The user interface is designed as an operational control console for SIH reviewers:

* **Real Coimbatore Map Canvas:** Leaflet map rendering authentic GPS coordinates across 12 arterial hubs (Gandhipuram, RS Puram, Ukkadam, Peelamedu, Hope College, Airport, Singanallur, Saravanampatti).
* **Strict Traffic-Signal Semantics:**
  * **Red (`#E5484D` / `#D92D3F`):** Unoptimized baseline route, congestion, bottlenecks.
  * **Amber (`#F5A623` / `#E0980C`):** In-progress optimization, depot hubs.
  * **Green (`#2ECC71` / `#189A5B`):** Quantum-optimized route, transit savings.
* **Persistent 3-Column Layout:** Input parameters (left) and Results KPIs (right) remain persistently visible across all 3 center canvas tabs:
  1. **Live Simulation:** Interactive map with before/after routes and animated crossfade transitions.
  2. **Compare Algorithms:** Side-by-side bar chart and multi-line convergence overlay across all 7 algorithms.
  3. **Performance Trends:** Full-size convergence chart featuring a flat red baseline reference line, green QPSO curve, and a highlighted badge for the crossover point (*"the moment QPSO beat baseline"*).
* **Deterministic Explainability Card:** Displays why the optimizer chose the selected route over alternatives, with constraint status, trade-offs, and evaluated candidate comparisons.
* **Yellow Alternative Route Highlighting (`#F5A623`):** Suggested alternative routes (such as Clarke-Wright Savings) are rendered with distinct yellow/amber styling on the Leaflet map and within the explanation card to provide clear operational contrast against optimal (green) and baseline (red) paths.

---

## Explainability Layer (Deterministic & Future LLM Ready)

The explainability layer translates raw optimizer evidence into both typed JSON and a fixed human-readable operational template **without any LLMs or non-deterministic generators**:

```
Optimizer Evidence (Road Network Distances, Travel Times, Demands, Graph Congestion)
    ↓
Structured Explanation Object (Typed Metrics, Reasons, Constraints, Trade-Offs, Alternative Comparison)
    ↓
Deterministic Human-Readable Template & Frontend Card (Instant SIH Review)
    ↓
[Future Extension] Downstream LLM Consumption (Zero Optimizer Changes Needed)
```

### Explanation Capabilities
* **Factual Decision Drivers:** Evaluates underlying optimizer metrics (`lower_travel_time`, `lower_total_distance`, `capacity_satisfied`, `all_locations_covered`, `time_constraint_satisfied`).
* **Explicit Trade-Offs:** Quantifies mileage vs. travel-time trade-offs when routes take detours to bypass high-congestion corridors.
* **Alternative Route Benchmarking:** Evaluates and highlights the alternative route candidate in **Yellow (`#F5A623`)** alongside the optimal path.

---

## Quickstart

### 1. Launch the Backend API
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn api:app --host 127.0.0.1 --port 8000 --reload
```
API docs available at: `http://127.0.0.1:8000/docs`

### 2. Launch the Frontend Dashboard
```bash
cd frontend
npm install
npm run dev
```
Open **`http://localhost:3000`** in your browser.

### 3. Containerized Deployment (Docker)
Build and run the containerized backend directly from the repository root:
```bash
docker build -t egreen-quanta .
docker run -p 8000:8000 egreen-quanta
```

### 4. Run Automated Test Suite
Run the full verification suite covering the explainability layer, constraints, and FastAPI integration:
```bash
python -m unittest discover tests
```

---

## Benchmark Highlights (Real CVRP Instances)

Tested across real-world instances with vehicle capacity constraints:
* **QPSO Win Rate vs. Nearest-Neighbor:** **100% (5/5)**
* **Average Transit Cost:** QPSO (**1519.05**) < Cheapest Insertion (**1533.23**) < Nearest-Neighbor (**1551.65**) < Clarke-Wright (**1562.41**)
* **QWOA Quantum Amplification:** Amplifies probability of measuring the ground-state route from classical uniform $4.17\%$ to **$15.80\%$ ($3.79\times$ enhancement)**.
