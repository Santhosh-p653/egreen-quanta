# Quantum-Inspired Traffic Route Optimization (QPSO)

**SIH 2026 — Problem Statement SIH26137** · E-Green Quanta · Quantum Technology Vertical

A production-grade traffic route optimization engine and executive dispatch dashboard that finds near-optimal delivery routes over the **70+ km Coimbatore Regional Road Network** (OpenStreetMap / OSMnx) and benchmark datasets. The system benchmarks **Quantum-behaved Particle Swarm Optimization (QPSO)** and **Quantum Walk State-Vector Simulation (QWOA)** against classical metaheuristics (PSO, Genetic Algorithms) and industry-standard heuristics (Clarke-Wright, Cheapest Insertion).

---

## 1. System Architecture

The project is structured as a decoupled, fullstack enterprise application:

```
egreen-quanta/
├── backend/                  # Python FastAPI service & core optimization engine
│   ├── api.py                # RESTful & WebSocket streaming API with auth & explainability
│   ├── auth.py               # JWT Bearer authentication & Bcrypt password hashing
│   ├── database.py           # SQLAlchemy PostgreSQL client with automatic SQLite fallback
│   ├── models.py             # ORM models (Users, OptimizationLogs audit trail)
│   ├── explainability.py     # Deterministic Explainability Layer (zero LLMs / template & JSON)
│   ├── osm_road_network.py   # 36-hub 70+ km Greater Coimbatore Regional OSM road graph
│   ├── graphhopper_client.py # OSM & GraphHopper matrix client (75km bounding radius)
│   ├── qpso.py               # Quantum-behaved Particle Swarm Optimization
│   ├── classical_pso.py      # Classical velocity- & inertia-driven PSO
│   ├── ga.py                 # Genetic Algorithm (OX, PMX crossover, 2-opt inversion mutation)
│   ├── clarke_wright.py      # Clarke-Wright Savings heuristic
│   ├── cheapest_insertion.py # Cheapest Insertion heuristic
│   ├── qwoa.py               # Quantum Walk Optimization (classical state-vector simulation)
│   ├── baseline.py           # Dijkstra shortest path & Nearest-Neighbor
│   ├── cvrp_qpso.py          # Capacitated VRP solver with multi-trip reload
│   ├── cvrp_baseline.py      # Matching classical baselines for CVRP
│   ├── cvrp_benchmark.py     # Multi-instance benchmark runner
│   ├── requirements.txt      # Python dependencies (FastAPI, SQLAlchemy, psycopg2, passlib)
│   └── data/                 # CVRP benchmark dataset (.npz)
├── frontend/                 # Next.js 14 App Router operations & executive dashboard
│   ├── src/app/              # Page routes, layout, and global styles
│   ├── src/components/
│   │   ├── AdminLoginPage.tsx        # Dedicated Admin Authentication landing gate
│   │   ├── AnalyticsDashboardView.tsx # Map-free executive KPI & analytics dashboard
│   │   ├── CompareView.tsx           # 5-graph multi-algorithm comparative benchmark suite
│   │   ├── ConvergenceChart.tsx      # Quantum convergence curve vs baseline
│   │   ├── MapComponent.tsx          # Animated Leaflet map with vehicle tracer & morph
│   │   ├── RouteExplanationCard.tsx  # Deterministic Explainability Layer card
│   │   ├── AdminPortalView.tsx       # PostgreSQL database audit log console
│   │   └── ThemeProvider.tsx         # Next-themes Dark/Light provider
│   ├── tailwind.config.ts    # High-contrast traffic-signal design tokens
│   └── package.json          # Node.js dependencies
├── tests/                    # Automated verification test suite (22 unit & integration tests)
│   ├── test_auth_database.py       # JWT auth, user login, DB logging & fallback tests
│   ├── test_explainability.py      # Explainability unit tests
│   ├── test_api_explainability.py  # FastAPI integration tests
│   ├── test_graphhopper_osm.py     # 70km regional network & GraphHopper tests
│   └── test_solvers.py             # QPSO, PSO, GA, CVRP heuristics tests
├── docs/                     # Technical documentation & mathematics specs
│   ├── algorithms/           # 11 individual modular algorithm specifications
│   ├── algorithms.md         # Master algorithm index
│   └── Intuition.md          # In-depth mathematics, quantum wave packets, and failure modes
├── Dockerfile                # Root container specification for GHCR deployment
├── .github/workflows/        # Automated CI/CD pipelines (GHCR & golden evals)
├── setup.md                  # Comprehensive setup & deployment guide
├── LICENSE.md                # MIT Open-Source License
└── .gitignore                # Repository exclusions (includes changelog.md & *.db)
```

---

## 2. Core Modules & Innovations

### A. Dedicated Admin Authentication Gate
* **Landing Gate (`AdminLoginPage.tsx`):** Access to dispatch operations is secured behind JWT Bearer token authentication.
* **Pre-seeded Credentials:** Built-in demo access with **`admin` / `admin123`** with a 1-click autofill shortcut.
* **Security Layer (`auth.py`):** Passwords hashed via `bcrypt`, signed JWT tokens (HS256) with role-based access control (`admin`, `dispatcher`).

### B. PostgreSQL Integration with Zero-Crash SQLite Fallback
* **Production Database (`database.py`, `models.py`):** Configured for PostgreSQL (`psycopg2-binary`).
* **Resilient Fallback:** Includes a 2-second connection pre-ping probe. If PostgreSQL is offline or unconfigured, the backend automatically and seamlessly switches to an embedded SQLite database (`sqlite:///./egreen_quanta.db`) with zero downtime.
* **Audit Logging:** Every optimization run records timestamp, scenario, stops count, distance, time, and crossover iteration.

### C. 70+ km Regional Road Network
* **36 Authentic Regional Hubs (`osm_road_network.py`):** Expanded from city center to greater Coimbatore district spanning:
  * **North:** Mettupalayam, Karamadai, Annur (Nilgiris gateway)
  * **East:** Avinashi, Karumathampatti, Palladam, Perumanallur (Tiruppur interstate border)
  * **South:** Pollachi Central, Kinathukadavu, Negamam, Othakkalmandapam
  * **West:** Walayar Interstate Freight Border, Madukkarai Cement Corridor, Ettimadai
* **57 Regional Highway Segments:** Connects National Expressways (NH-544 6-lane, NH-83, NH-181).

### D. Operations Dashboard & UX Customization
* **Left-Side Persistent Sidebar:** Quick navigation between Live Simulation, Analytics Dashboard, and Admin Console.
* **Customizable Tab Density (UX):** Global switcher (`Compact`, `Comfortable`, `Large`) dynamically scales tab padding, button sizing, and typography across all views with `localStorage` persistence.
* **Live Simulation Page:** Interactive Leaflet map featuring:
  * Dynamic Depot (`D`) and Destination (`🏁`) markers updating to the user's selected hubs.
  * Live animated delivery vehicle tracer (`🚛 Tracing Live`).
  * **Route Morph / Transition Animation:** Sequentially compares Baseline (Red) $\to$ Alternative (Yellow) $\to$ Optimal (Green).
  * Collapsible Turn-by-Turn Route Legs Drawer.
* **Analytics Dashboard (Strictly Map-Free):** Dedicated executive analytics view:
  * 4 Executive KPI Metric Cards (large readable typography).
  * Deterministic Explainability & Constraint Verification Card.
  * Convergence Trajectory Curves.
* **5-Graph Benchmark Suite (`CompareView.tsx`):**
  1. *Normalized Performance Bars* (Time, Distance, Latency).
  2. *Multi-Line Convergence Trajectories* across all 7 algorithms.
  3. *Carbon & Energy Impact* (kg CO2 emitted factoring congestion delays).
  4. *Pareto Frontier Matrix* (Computation Latency vs Time Savings).
  5. *Comprehensive Multi-Criteria Scorecard* with true winner evaluation.

---

## 3. Algorithms Implemented

| Algorithm | Category | Role | Primary File |
|---|---|---|---|
| **QPSO** | Quantum-Inspired Metaheuristic | Primary route optimization engine | [`backend/qpso.py`](backend/qpso.py) |
| **QWOA** | True Quantum Simulation | Schrödinger state-vector simulation on $S_n$ | [`backend/qwoa.py`](backend/qwoa.py) |
| **Classical PSO** | Swarm Intelligence | Velocity- and momentum-based baseline | [`backend/classical_pso.py`](backend/classical_pso.py) |
| **GA-OX & GA-PMX** | Evolutionary Algorithms | Order and Partially Mapped Crossover + 2-opt inversion | [`backend/ga.py`](backend/ga.py) |
| **Clarke-Wright Savings** | Classical Heuristic | Industry-standard CVRP savings matrix | [`backend/clarke_wright.py`](backend/clarke_wright.py) |
| **Cheapest Insertion** | Greedy Family Heuristic | Detour cost minimization along tour edges | [`backend/cheapest_insertion.py`](backend/cheapest_insertion.py) |
| **Nearest-Neighbor** | Greedy Baseline | Myopic proximity baseline | [`backend/baseline.py`](backend/baseline.py) |
| **Dijkstra's Algorithm** | Exact Pathfinding | Metric closure segment cost precomputation | [`backend/baseline.py`](backend/baseline.py) |
| **Capacity Repair** | Constraint Handling | Dynamic vehicle capacity reload handling | [`backend/cvrp_qpso.py`](backend/cvrp_qpso.py) |

---

## 4. Quickstart

### 1. Launch Backend Service
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn api:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation available at: `http://127.0.0.1:8000/docs`

### 2. Launch Operations Frontend
```bash
cd frontend
npm install
npm run dev
```
Open **`http://localhost:3000`** in your browser.
1. Sign in on the Admin page using **`admin` / `admin123`** (or click *Fill Demo Credentials*).
2. Use the left-side menu to explore **Live Simulation**, **Analytics Dashboard**, and **Admin Console**.

### 3. Run Automated Unit Tests
```bash
python -m unittest discover tests
```
Runs all 22 tests covering auth, JWT, database logging, OSM network, explainability, and solvers.

---

## 5. Documentation & Technical Specifications

* [Setup & Deployment Guide](setup.md) — Comprehensive local setup, Docker containerization, PostgreSQL configuration, and API reference.
* [Algorithm Intuition & Specs](docs/Intuition.md) — Quantum potential wells, wave packets, and contraction-expansion annealing mathematics.
* [LICENSE](LICENSE.md) — MIT License.
