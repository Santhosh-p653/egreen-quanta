# Setup & Deployment Guide — E-Green Quanta

This comprehensive guide details how to install, configure, execute, test, and deploy the **E-Green Quanta Quantum-Inspired Traffic Route Optimization System**.

---

## 1. Prerequisites & System Requirements

* **Python:** 3.10, 3.11, 3.12, or 3.14
* **Node.js:** v18.17+ or v20+ (Node v22 / v24 fully supported; npm v10+)
* **PostgreSQL:** (Optional, version 14+) — If not installed or running, the backend automatically uses an embedded SQLite database (`sqlite:///./egreen_quanta.db`) with zero manual setup required.
* **Git:** Version control
* **Docker:** (Optional) For containerized execution

---

## 2. Directory Architecture

```
egreen-quanta/
├── backend/                  # Python FastAPI service & core optimization engine
│   ├── api.py                # RESTful & WebSocket API with authentication & telemetry
│   ├── auth.py               # JWT token generation, verification & bcrypt hashing
│   ├── database.py           # SQLAlchemy client with automatic PostgreSQL/SQLite detection
│   ├── models.py             # User and OptimizationLog database models
│   ├── osm_road_network.py   # 36-hub 70+ km Greater Coimbatore Regional network
│   ├── graphhopper_client.py # OSM matrix client (75km radius)
│   ├── qpso.py               # Quantum-behaved Particle Swarm Optimization
│   ├── quantum_bidirectional_astar.py # Quantum-Inspired Bidirectional A* (wavepacket & tunneling)
│   ├── classical_pso.py      # Classical Velocity PSO baseline
│   ├── ga.py                 # Genetic Algorithm (OX, PMX, 2-opt inversion mutation)
│   ├── clarke_wright.py      # Clarke-Wright Savings heuristic
│   ├── cheapest_insertion.py # Cheapest Insertion heuristic
│   ├── cvrp_qpso.py          # Capacitated VRP solver with multi-trip reload
│   ├── requirements.txt      # Python dependencies
│   └── data/                 # Benchmark datasets (.npz)
├── frontend/                 # Next.js 14 App Router operations dashboard
│   ├── src/app/              # Root layout, theme provider, and primary views
│   ├── src/components/
│   │   ├── AdminLoginPage.tsx        # Dedicated Admin Authentication landing gate
│   │   ├── AnalyticsDashboardView.tsx # Map-free executive KPI & analytics dashboard
│   │   ├── CompareView.tsx           # 5-graph multi-algorithm comparative benchmark suite
│   │   ├── ConvergenceChart.tsx      # Quantum convergence curve vs baseline
│   │   ├── MapComponent.tsx          # Animated Leaflet map with vehicle tracer & morph
│   │   ├── RouteExplanationCard.tsx  # Deterministic Explainability Layer card
│   │   └── AdminPortalView.tsx       # PostgreSQL database audit log console
│   ├── package.json          # Node dependencies
│   └── tailwind.config.ts    # High-contrast traffic signal design tokens
├── tests/                    # Automated verification test suite (29 tests)
├── Dockerfile                # Root container specification
├── README.md                 # Master documentation
└── setup.md                  # This setup guide
```

---

## 3. Backend Setup & Execution

### A. Environment Configuration
Navigate to the `backend/` directory and create a virtual environment:

```bash
cd backend

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### B. Dependency Installation
Install dependencies including FastAPI, SQLAlchemy, PostgreSQL drivers, and crypto security libraries:
```bash
pip install -r requirements.txt
```

### C. Database Configuration
By default, the backend checks for PostgreSQL at `postgresql://postgres:postgres@localhost:5432/egreen_quanta`.
* **If PostgreSQL is available:** It connects and synchronizes tables automatically.
* **If PostgreSQL is offline:** It automatically logs a graceful notice and falls back to an embedded SQLite database (`sqlite:///./egreen_quanta.db`). Zero configuration required.
* To specify custom credentials, set the `DATABASE_URL` environment variable:
  ```bash
  # Example custom PostgreSQL URI:
  export DATABASE_URL="postgresql://user:password@localhost:5432/my_db"
  ```

### D. Starting the Server
Start the FastAPI server:
```bash
python -m uvicorn api:app --host 127.0.0.1 --port 8000 --reload
```
* **API Documentation (Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **System Status Probe:** [http://127.0.0.1:8000/api/admin/system](http://127.0.0.1:8000/api/admin/system)

---

## 4. Frontend Setup & Execution

Open a separate terminal window and navigate to `frontend/`:

```bash
cd frontend
npm install
```

### A. Running in Development Mode
```bash
npm run dev
# Or on Windows PowerShell:
npm.cmd run dev
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser.

### B. Building for Production
To verify production bundle compilation:
```bash
npm run build
# Or on Windows PowerShell:
npm.cmd run build
```

---

## 5. User Guide & Core Workflows

### 1. Administrator Authentication
* When opening `http://localhost:3000`, you will be greeted by the **Admin Sign In** page.
* **Default Admin Credentials:**
  * **Username:** `admin`
  * **Password:** `admin123`
* Use the **"Click to Fill Demo Credentials"** button for instant one-click login.

### 2. Left-Side Navigation Sidebar
Use the persistent left sidebar to switch between views:
* 🛰️ **Live Simulation:** Spatial routing, animated Leaflet map, and turn-by-turn legs.
* 📊 **Analytics Dashboard:** Map-free executive KPI reporting, 5 rich benchmark charts, and deterministic explainability.
* 🛡️ **Admin Console:** PostgreSQL telemetry and historical audit logs.
* **Tab Density Control:** Adjust tab size (`Compact` / `Normal` / `Large`) from the dashboard or sidebar to suit your display preferences.
* **Theme Switcher:** Toggle between Dark and Light mode.
* **Sign Out:** Returns to the login gate.

### 3. Live Route Simulation & Morph Animation
* Select any 70km Regional preset (e.g. `Regional Conglomerate`, `Interstate Freight Corridor`).
* Pick an **Origin Depot** and optional **Destination Hub**. Notice the Leaflet map immediately updates the gold **`D`** depot marker and blue **`🏁`** destination marker at those exact hubs.
* Click **"Play Route Morph"** on the map to trigger a visual transition animation that cycles through:
  1. *Baseline Route (Red, dashed)* with live moving vehicle.
  2. *Alternative Suboptimal Candidate (Yellow)* with live moving vehicle.
  3. *Quantum-behaved PSO Optimal Route (Green)* with live moving vehicle.

---

## 6. Automated Verification Test Suite

Run the full suite of 29 automated tests:

```bash
# From repository root:
python -m unittest discover tests
```

Tests verify:
1. `tests/test_quantum_bidirectional_astar.py`: QI-BA* point-to-point pathfinding, delta-potential barrier tunneling, and multi-stop tour optimization.
2. `tests/test_auth_database.py`: JWT token generation, admin authentication, SQLite fallback, and audit logging.
3. `tests/test_graphhopper_osm.py`: 70+ km regional network, 36 landmarks, 57 road edges, and GraphHopper matrix client.
4. `tests/test_explainability.py`: Deterministic route explainability and constraint verification.
5. `tests/test_api_explainability.py`: FastAPI endpoints for optimization and explanation retrieval.
6. `tests/test_solvers.py`: QPSO, Classical PSO, GA (OX/PMX), and classical heuristics.
