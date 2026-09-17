# Setup & Deployment Guide — Egreen Quanta

This guide walks you through setting up, running, testing, and containerizing the **Quantum-Inspired Metaheuristic Traffic Route Optimization Engine (QPSO)** and **Operations Dashboard**.

---

## 1. Prerequisites

Ensure the following tools are installed on your environment:

* **Python:** 3.10, 3.11, or 3.12 (Python 3.14 compatible)
* **Node.js:** v18.17+ or v20+ (Node v24 supported; npm v10+)
* **Git:** For cloning and version control
* **Docker:** (Optional) For containerized execution

---

## 2. Repository Layout

The project is structured into independent, production-grade workspaces:

```
egreen-quanta/
├── backend/                  # Python FastAPI service & optimization engine
│   ├── api.py                # RESTful & WebSocket API
│   ├── explainability.py     # Deterministic Explainability Layer
│   ├── osm_road_network.py   # 24-hub 30km Greater Coimbatore OSM graph
│   ├── graphhopper_client.py # OSM & GraphHopper matrix client & instance generator
│   ├── qpso.py               # Quantum-behaved Particle Swarm Optimization
│   ├── classical_pso.py      # Classical Velocity-driven PSO
│   ├── ga.py                 # Genetic Algorithms (GA-OX, GA-PMX)
│   ├── clarke_wright.py      # Clarke-Wright Savings Heuristic
│   ├── cheapest_insertion.py # Cheapest Insertion Heuristic
│   ├── qwoa.py               # Quantum Walk State-Vector Simulation
│   ├── baseline.py           # Dijkstra & Nearest-Neighbor
│   ├── cvrp_qpso.py          # Capacitated VRP solver with multi-trip reload
│   ├── requirements.txt      # Python dependencies
│   └── data/                 # CVRP benchmark dataset (cvrp_10.npz)
├── frontend/                 # Next.js 14 App Router dashboard
│   ├── src/app/              # Operational UI (3-column layout)
│   ├── src/components/       # MapComponent, RouteExplanationCard, CompareView
│   ├── package.json          # Node.js dependencies
│   └── tailwind.config.ts    # High-contrast traffic signal design tokens
├── tests/                    # Automated verification suite (16 tests)
│   ├── test_explainability.py      # Explainability unit tests
│   ├── test_api_explainability.py  # FastAPI integration tests
│   └── test_graphhopper_osm.py     # OSM & GraphHopper generator tests
├── docs/                     # Comprehensive mathematics & architecture specs
├── Dockerfile                # Root container specification
├── README.md                 # Project overview & benchmark results
├── LICENSE.md                # MIT Open-Source License
└── setup.md                  # This setup guide
```

---

## 3. Local Development Setup

### Step A: Backend API Service

1. Open a terminal and navigate to `backend/`:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment (recommended):
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI server with live reloading:
   ```bash
   uvicorn api:app --host 127.0.0.1 --port 8000 --reload
   ```
5. Verify the backend is live:
   * **Health Check:** `http://127.0.0.1:8000/api/health`
   * **Interactive OpenAPI Swagger Docs:** `http://127.0.0.1:8000/docs`

---

### Step B: Frontend Dashboard

1. Open a second terminal and navigate to `frontend/`:
   ```bash
   cd frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Start the Next.js development server:
   ```bash
   npm run dev
   ```
4. Access the operational dashboard in your browser at:
   ```
   http://localhost:3000
   ```

---

## 4. Running the Automated Test Suite

The verification suite contains **16 tests** covering deterministic explainability, constraint checks, zero-mutation optimizer consistency, GraphHopper matrix extraction, and FastAPI endpoints.

Run the tests from the repository root:

```bash
# Discover and run all test modules
python -m unittest discover tests

# Or run specific test modules
python -m unittest tests/test_explainability.py
python -m unittest tests/test_api_explainability.py
python -m unittest tests/test_graphhopper_osm.py
```

All 16 tests should pass with `OK`.

---

## 5. Docker Containerized Deployment

You can build and deploy the containerized backend directly using the root `Dockerfile`:

```bash
# 1. Build the container image
docker build -t egreen-quanta:latest .

# 2. Run the container exposing port 8000
docker run -d --name egreen-service -p 8000:8000 egreen-quanta:latest

# 3. Test container health
curl http://localhost:8000/api/health
```

---

## 6. OpenStreetMap & GraphHopper Configuration

### High-Fidelity OSM Metric Closure (Default — Offline)
By default, the engine uses an authentic NetworkX Dijkstra metric closure computed directly over our **24-landmark, 40-segment Greater Coimbatore OpenStreetMap graph**. This guarantees:
* **Zero external API dependencies** (100% offline and reproducible for hackathon evaluations).
* Authentic GPS coordinates across a **30+ km metropolitan diameter**.
* Real arterial speed limits (Avinashi Rd, Trichy Rd, NH-544, Sathy Rd) and simulated live congestion factors.

### Live GraphHopper API (Optional)
If you wish to query GraphHopper's live routing engine or a local GraphHopper Docker container:
```bash
# Remote GraphHopper API Key
export GRAPHHOPPER_API_KEY="your-api-key-here"

# Or local GraphHopper instance URL
export GRAPHHOPPER_URL="http://localhost:8989/matrix"
```
The client in `backend/graphhopper_client.py` will automatically route matrix calls through GraphHopper with automatic fallback to the local OSM closure if unavailable.

---

## 7. Scenario Presets & High-Differentiation Benchmarks

To showcase genuine algorithmic differences between QPSO, Classical PSO, GA, and heuristics, use the **Scenario & Radius** selector in the UI or call `GET /api/scenarios`:

| Scenario ID | Name | Stops | Radius | Focus |
|---|---|---|---|---|
| `metro_greater` | **Greater Coimbatore Metro** | 12 | **32 km** | **Maximum differentiation:** Explodes search space to $4.79 \times 10^8$ permutations. QPSO out-optimizes baselines. |
| `cbd_express` | **CBD Commercial Express** | 5 | 8 km | Fast central loop around Gandhipuram core. |
| `industrial_cargo` | **Airport & Eastern Cargo** | 8 | 24 km | Highway freight loop via NH-544 and Sulur. |
| `north_south` | **North-South Arterial** | 8 | 26 km | Traverses central bottlenecks from Thudiyalur to Eachanari. |
| `western_suburbs` | **Western Suburbs** | 6 | 18 km | Foothills loop via Vadavalli and Kovaipudur. |
| `random` | **Dynamic Random OSM** | 10 | 30 km | Generates dynamic instances with randomized customer demand. |

---

## 8. Legacy Gradio Demo (Fallback Option)

If you need a quick standalone single-script demonstration without starting the Next.js frontend:

```bash
cd backend
python gradio_app.py
```
This launches a Gradio UI at `http://127.0.0.1:7860`.

---

## 9. Troubleshooting & FAQ

* **Issue: `npm run dev` fails with execution policy error on Windows PowerShell**
  * *Solution:* Use `npm.cmd run dev` or run PowerShell as Administrator and execute `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`.
* **Issue: Port 8000 is already in use**
  * *Solution:* Run `uvicorn api:app --host 127.0.0.1 --port 8080` and adjust the API URL in frontend if needed.
* **Issue: Leaflet map markers fail to render**
  * *Solution:* Leaflet CSS is imported in `frontend/src/app/globals.css`. Ensure Next.js dev server has finished bundling and open `http://localhost:3000`.
* **Issue: Line-ending LF/CRLF warnings when staging files**
  * *Solution:* The repository includes a root `.gitattributes` file enforcing `* text=auto` and `eol=lf` to keep line endings clean and uniform across Windows and Linux.
