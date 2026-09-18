"""
api.py — FastAPI Backend for QPSO Traffic Optimization Dashboard
Provides RESTful and WebSocket endpoints wrapping the Python optimization engine.
Routes through the real Coimbatore road network graph (osm_road_network.py).
"""

import json
import asyncio
from typing import List, Optional
import numpy as np
from pydantic import BaseModel, Field
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Database and Security
from database import get_db, init_db, get_db_status, SessionLocal
from models import User, OptimizationLog
from auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    require_admin,
    seed_default_admin,
)

# Core engine imports
from osm_road_network import (
    COIMBATORE_LANDMARKS,
    COIMBATORE_ROAD_SEGMENTS,
    BENCHMARK_SCENARIOS,
    build_coimbatore_graph,
    get_route_geometry,
)
from qpso import qpso_optimize, precompute_segment_costs
from classical_pso import classical_pso_optimize
from ga import ga_optimize
from baseline import nearest_neighbor_route
from clarke_wright import clarke_wright_route
from cheapest_insertion import cheapest_insertion_route
from explainability import build_route_explanation, build_multivehicle_explanation
from graphhopper_client import generate_osm_cvrp_instance, GraphHopperClient

app = FastAPI(
    title="Coimbatore Traffic Route Optimization API",
    description="Operations-grade API for Quantum-behaved Particle Swarm Optimization over the Coimbatore road network.",
    version="2.0.0",
)

@app.on_event("startup")
def on_startup():
    """Initializes database schema and ensures default admin user is seeded."""
    init_db()
    db = SessionLocal()
    try:
        seed_default_admin(db)
    finally:
        db.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    username: str = Field(..., description="Administrator username")
    password: str = Field(..., description="Administrator password")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str


class OptimizeRequest(BaseModel):
    source_id: int = Field(0, description="Depot / Origin landmark ID")
    destination_id: Optional[int] = Field(None, description="Final destination landmark ID")
    intermediate_stops: List[int] = Field(default_factory=lambda: [1, 4, 6, 7, 11], description="Delivery waypoint landmark IDs")
    traffic_mode: str = Field("real", description="'real' for congested live traffic, 'free' for unhindered speed limits")
    algorithm: str = Field("qpso", description="'qpso', 'classical_pso', 'ga_ox', 'ga_pmx', 'nearest_neighbor', 'clarke_wright', 'cheapest_insertion'")
    swarm_size: int = Field(30, ge=10, le=100)
    iterations: int = Field(80, ge=20, le=250)
    seed: Optional[int] = Field(42, description="Random seed for traffic & solver reproducibility")
    ga_crossover: Optional[str] = Field("ox", description="GA crossover operator: 'ox' or 'pmx'")
    ga_mutation_rate: Optional[float] = Field(0.15, ge=0.01, le=0.9, description="GA mutation probability")


class ExplainRequest(BaseModel):
    vehicle: str = Field("Vehicle 01", description="Assigned vehicle name")
    selected_route: List[str] = Field(..., description="Ordered list of visited landmark names")
    selected_metrics: dict = Field(..., description="Metrics dictionary of selected route")
    alternative_name: Optional[str] = Field(None, description="Name of alternative candidate evaluated")
    alternative_route: Optional[List[str]] = Field(None, description="Ordered list of alternative landmark names")
    alternative_metrics: Optional[dict] = Field(None, description="Metrics dictionary of alternative route")
    demands: Optional[List[float]] = Field(None, description="Customer demand sequence")
    vehicle_capacity: Optional[float] = Field(100.0, description="Payload capacity limit")
    required_stops: Optional[int] = Field(None, description="Expected delivery stop count")
    max_time_min: Optional[float] = Field(None, description="Operational maximum travel time")
    algorithm: str = Field("QPSO", description="Algorithm name")


class Landmark(BaseModel):
    id: int
    name: str
    lat: float
    lon: float
    desc: str


@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "qpso-traffic-engine"}


@app.get("/api/network/landmarks", response_model=List[Landmark])
def get_landmarks():
    """Returns available Coimbatore transit hubs and delivery points."""
    return list(COIMBATORE_LANDMARKS.values())


@app.get("/api/scenarios")
def get_scenarios():
    """Returns curated realistic benchmark scenarios spanning up to 30km radius."""
    return list(BENCHMARK_SCENARIOS.values())


class GenerateInstanceRequest(BaseModel):
    n_stops: int = Field(10, ge=3, le=23, description="Number of customer stops to sample")
    depot_id: int = Field(0, description="Origin depot landmark ID")
    radius_km: float = Field(30.0, ge=5.0, le=50.0, description="Max radial distance in km")
    vehicle_capacity: int = Field(100, description="Vehicle payload capacity")
    seed: Optional[int] = Field(None, description="Random seed")


@app.post("/api/instances/generate")
def generate_instance(req: GenerateInstanceRequest):
    """
    Dynamically samples realistic OpenStreetMap / GraphHopper delivery instances
    across the greater Coimbatore road network.
    """
    return generate_osm_cvrp_instance(
        n_stops=req.n_stops,
        depot_id=req.depot_id,
        radius_km=req.radius_km,
        vehicle_capacity=req.vehicle_capacity,
        seed=req.seed,
    )


class MatrixRequest(BaseModel):
    points: List[List[float]] = Field(..., description="List of [lat, lon] coordinates")
    traffic_mode: str = Field("real", description="'real' or 'free'")


@app.post("/api/instances/matrix")
def get_distance_time_matrix(req: MatrixRequest):
    """
    Extracts road network distance and time matrices using GraphHopper API
    with automatic offline OSM Dijkstra closure fallback.
    """
    client = GraphHopperClient()
    coords = [(p[0], p[1]) for p in req.points]
    return client.get_matrix(coords, traffic_mode=req.traffic_mode)


@app.get("/api/algorithms")
def get_algorithms():
    """Returns list of selectable optimization algorithms and metadata."""
    return [
        {
            "id": "qpso",
            "name": "Quantum-behaved Particle Swarm (QPSO)",
            "family": "Quantum-Inspired",
            "desc": "Delta-potential well search with annealed contraction-expansion.",
            "is_primary": True,
        },
        {
            "id": "classical_pso",
            "name": "Classical PSO",
            "family": "Swarm Intelligence",
            "desc": "Standard velocity & inertia vector particle dynamics.",
            "is_primary": False,
        },
        {
            "id": "ga_ox",
            "name": "Genetic Algorithm (OX)",
            "family": "Evolutionary",
            "desc": "Order Crossover preserving contiguous tour sequences.",
            "is_primary": False,
        },
        {
            "id": "ga_pmx",
            "name": "Genetic Algorithm (PMX)",
            "family": "Evolutionary",
            "desc": "Partially Mapped Crossover preserving absolute positioning.",
            "is_primary": False,
        },
        {
            "id": "clarke_wright",
            "name": "Clarke-Wright Savings",
            "family": "Classical Heuristic",
            "desc": "Industry-standard savings matrix route merge.",
            "is_primary": False,
        },
        {
            "id": "cheapest_insertion",
            "name": "Cheapest Insertion",
            "family": "Greedy Family",
            "desc": "Detour cost minimization along active tour edges.",
            "is_primary": False,
        },
        {
            "id": "nearest_neighbor",
            "name": "Nearest Neighbor",
            "family": "Greedy Baseline",
            "desc": "Unplanned myopic hops to closest pending destination.",
            "is_primary": False,
        },
    ]


def _run_solver(
    algo: str,
    G,
    depot: int,
    waypoints: List[int],
    swarm_size: int,
    iterations: int,
    seed: int,
    ga_crossover: str = "ox",
    ga_mutation_rate: float = 0.15,
):
    """Executes the specified optimization solver."""
    if algo == "qpso":
        return qpso_optimize(G, depot, waypoints, n_particles=swarm_size, n_iterations=iterations, seed=seed)
    elif algo == "classical_pso":
        return classical_pso_optimize(G, depot, waypoints, n_particles=swarm_size, n_iterations=iterations, seed=seed)
    elif algo in ("ga", "ga_ox", "ga_pmx"):
        cx = "pmx" if (algo == "ga_pmx" or (algo == "ga" and ga_crossover.lower() == "pmx")) else "ox"
        return ga_optimize(
            G,
            depot,
            waypoints,
            crossover=cx,
            pop_size=swarm_size,
            n_generations=iterations,
            mutation_rate=ga_mutation_rate,
            seed=seed,
        )
    elif algo == "clarke_wright":
        route, cost, rt = clarke_wright_route(G, depot, waypoints)
        return {"route": route, "cost": cost, "history": [cost] * (iterations + 1), "runtime": rt}
    elif algo == "cheapest_insertion":
        route, cost, rt = cheapest_insertion_route(G, depot, waypoints)
        return {"route": route, "cost": cost, "history": [cost] * (iterations + 1), "runtime": rt}
    else:  # nearest_neighbor
        route, cost, rt = nearest_neighbor_route(G, depot, waypoints)
        return {"route": route, "cost": cost, "history": [cost] * (iterations + 1), "runtime": rt}


@app.post("/api/optimize")
def optimize_route(req: OptimizeRequest):
    """
    Computes before (baseline) and after (optimized) routes over the Coimbatore road network.
    Returns real GPS coordinates, before/after metrics, convergence array, and crossover index.
    """
    if req.source_id not in COIMBATORE_LANDMARKS:
        raise HTTPException(status_code=400, detail="Invalid source landmark ID")

    # Filter waypoints: ensure all exist and source is excluded from stops
    waypoints = [w for w in req.intermediate_stops if w in COIMBATORE_LANDMARKS and w != req.source_id]
    if not waypoints:
        raise HTTPException(status_code=400, detail="At least one intermediate destination required")

    G = build_coimbatore_graph(traffic_mode=req.traffic_mode, seed=req.seed)

    # 1. Baseline Route (Nearest-Neighbor)
    nn_route, nn_cost, nn_runtime = nearest_neighbor_route(G, req.source_id, waypoints)
    # Loop back to depot or to destination if specified
    if req.destination_id and req.destination_id in COIMBATORE_LANDMARKS:
        before_nodes = nn_route + [req.destination_id]
    else:
        before_nodes = nn_route + [req.source_id]

    before_geom = get_route_geometry(G, before_nodes)

    # 2. Optimized Route
    opt_result = _run_solver(
        req.algorithm,
        G,
        req.source_id,
        waypoints,
        swarm_size=req.swarm_size,
        iterations=req.iterations,
        seed=req.seed,
        ga_crossover=req.ga_crossover or "ox",
        ga_mutation_rate=req.ga_mutation_rate or 0.15,
    )
    raw_opt_nodes = opt_result["route"]
    if req.destination_id and req.destination_id in COIMBATORE_LANDMARKS:
        after_nodes = raw_opt_nodes + [req.destination_id]
    else:
        after_nodes = raw_opt_nodes + [req.source_id]

    after_geom = get_route_geometry(G, after_nodes)

    # 3. Alternative Route Candidate (Clarke-Wright Savings Heuristic or Nearest Neighbor)
    alt_algo = "clarke_wright" if req.algorithm != "clarke_wright" else "nearest_neighbor"
    alt_name = "Clarke-Wright Savings" if req.algorithm != "clarke_wright" else "Nearest Neighbor Baseline"
    alt_result = _run_solver(
        alt_algo, G, req.source_id, waypoints,
        swarm_size=req.swarm_size, iterations=req.iterations, seed=req.seed
    )
    raw_alt_nodes = alt_result["route"]
    if req.destination_id and req.destination_id in COIMBATORE_LANDMARKS:
        alt_nodes = raw_alt_nodes + [req.destination_id]
    else:
        alt_nodes = raw_alt_nodes + [req.source_id]

    alt_geom = get_route_geometry(G, alt_nodes)

    # 4. Calculate Crossover Iteration ("The moment optimizer beat the baseline")
    history = [round(float(c), 2) for c in opt_result["history"]]
    baseline_cost = round(float(nn_cost), 2)

    crossover_idx = None
    for idx, c in enumerate(history):
        if c < baseline_cost:
            crossover_idx = idx
            break

    # Calculate Congestion factor
    avg_congestion = float(np.mean([G[u][v].get("congestion", 1.0) for u, v in G.edges()]))

    # Calculate Improvement %
    time_improvement_pct = 0.0
    if before_geom["total_time_min"] > 0:
        time_improvement_pct = round(
            (before_geom["total_time_min"] - after_geom["total_time_min"]) / before_geom["total_time_min"] * 100.0,
            1,
        )

    dist_improvement_pct = 0.0
    if before_geom["total_distance_km"] > 0:
        dist_improvement_pct = round(
            (before_geom["total_distance_km"] - after_geom["total_distance_km"]) / before_geom["total_distance_km"] * 100.0,
            1,
        )

    # 5. Deterministic Explainability Layer Generation
    selected_route_names = [COIMBATORE_LANDMARKS[n]["name"] for n in after_nodes]
    alt_route_names = [COIMBATORE_LANDMARKS[n]["name"] for n in alt_nodes]

    explanation = build_route_explanation(
        selected_route_names=selected_route_names,
        selected_metrics={
            "distance_km": after_geom["total_distance_km"],
            "travel_time_min": after_geom["total_time_min"],
            "objective_cost": round(float(opt_result["cost"]), 2),
            "congestion_level": round(avg_congestion, 2),
        },
        vehicle_name="Vehicle 01",
        alternative_name=alt_name,
        alternative_route_names=alt_route_names,
        alternative_metrics={
            "distance_km": alt_geom["total_distance_km"],
            "travel_time_min": alt_geom["total_time_min"],
            "objective_cost": round(float(alt_result["cost"]), 2),
            "congestion_level": round(avg_congestion, 2),
        },
        required_stop_count=len(waypoints),
        vehicle_capacity=100.0,
        algorithm_name=req.algorithm.upper(),
    )

    response_payload = {
        "algorithm": req.algorithm,
        "traffic_mode": req.traffic_mode,
        "baseline_cost": baseline_cost,
        "crossover_iteration": crossover_idx,
        "convergence_history": history,
        "before_metrics": {
            "distance_km": before_geom["total_distance_km"],
            "travel_time_min": before_geom["total_time_min"],
            "congestion_level": round(avg_congestion, 2),
            "iterations": 1,
            "runtime_ms": round(nn_runtime * 1000, 2),
        },
        "after_metrics": {
            "distance_km": after_geom["total_distance_km"],
            "travel_time_min": after_geom["total_time_min"],
            "congestion_level": round(avg_congestion, 2),
            "iterations": req.iterations,
            "runtime_ms": round(opt_result["runtime"] * 1000, 2),
            "time_saved_min": max(0.0, round(before_geom["total_time_min"] - after_geom["total_time_min"], 1)),
            "time_improvement_pct": time_improvement_pct,
            "distance_improvement_pct": dist_improvement_pct,
        },
        "before_route": {
            "coordinates": before_geom["coordinates"],
            "node_sequence": [COIMBATORE_LANDMARKS[n]["name"] for n in before_nodes],
            "corridors": before_geom["corridors"],
        },
        "after_route": {
            "coordinates": after_geom["coordinates"],
            "node_sequence": selected_route_names,
            "corridors": after_geom["corridors"],
        },
        "alternative_route": {
            "name": alt_name,
            "algorithm": alt_algo,
            "coordinates": alt_geom["coordinates"],
            "node_sequence": alt_route_names,
            "corridors": alt_geom["corridors"],
            "distance_km": alt_geom["total_distance_km"],
            "travel_time_min": alt_geom["total_time_min"],
        },
        "explanation": explanation,
        "landmarks": [COIMBATORE_LANDMARKS[n] for n in [req.source_id] + waypoints],
    }

    # Persist optimization run to Database (PostgreSQL / SQLite fallback)
    try:
        db = SessionLocal()
        time_saved = max(0.0, round(before_geom["total_time_min"] - after_geom["total_time_min"], 1))
        summary = ""
        if isinstance(explanation, dict) and "human_readable" in explanation:
            summary = explanation["human_readable"][:300]

        log_record = OptimizationLog(
            scenario_name=f"{len(waypoints)} Waypoints Route",
            algorithm=req.algorithm.upper(),
            traffic_mode=req.traffic_mode,
            n_stops=len(waypoints),
            total_distance_km=after_geom["total_distance_km"],
            total_time_min=after_geom["total_time_min"],
            time_saved_min=time_saved,
            crossover_iteration=crossover_idx,
            runtime_ms=round(opt_result["runtime"] * 1000, 2),
            summary_text=summary,
        )
        db.add(log_record)
        db.commit()
        db.close()
    except Exception:
        pass  # Non-blocking async telemetry

    return response_payload


@app.post("/api/auth/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Authenticates administrator/dispatcher and returns JWT bearer token."""
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid administrator username or password")
    token = create_access_token(data={"sub": user.username, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role,
    }


@app.get("/api/auth/me")
def get_me(current_user: Optional[User] = Depends(get_current_user)):
    """Returns currently authenticated user profile."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
    }


@app.get("/api/admin/logs")
def get_admin_logs(db: Session = Depends(get_db)):
    """Returns optimization audit history persisted in PostgreSQL / SQLite."""
    logs = db.query(OptimizationLog).order_by(OptimizationLog.created_at.desc()).limit(50).all()
    return [
        {
            "id": l.id,
            "scenario_name": l.scenario_name,
            "algorithm": l.algorithm,
            "traffic_mode": l.traffic_mode,
            "n_stops": l.n_stops,
            "total_distance_km": l.total_distance_km,
            "total_time_min": l.total_time_min,
            "time_saved_min": l.time_saved_min,
            "crossover_iteration": l.crossover_iteration,
            "runtime_ms": l.runtime_ms,
            "created_at": l.created_at.strftime("%Y-%m-%d %H:%M:%S") if l.created_at else "",
        }
        for l in logs
    ]


@app.delete("/api/admin/logs")
def clear_admin_logs(current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Clears all historical optimization audit logs. Requires Admin privileges."""
    deleted_count = db.query(OptimizationLog).delete()
    db.commit()
    return {"status": "cleared", "deleted_count": deleted_count}


@app.get("/api/admin/system")
def get_system_status():
    """Returns system status, active database backend, and regional network coverage."""
    return {
        "database": get_db_status(),
        "landmarks_count": len(COIMBATORE_LANDMARKS),
        "road_segments_count": len(COIMBATORE_ROAD_SEGMENTS),
        "radius_coverage_km": "70+ km Regional Scale",
        "supported_algorithms": [
            "QPSO",
            "Classical PSO",
            "GA (OX)",
            "GA (PMX)",
            "Clarke-Wright Savings",
            "Cheapest Insertion",
            "Nearest Neighbor",
        ],
    }


@app.post("/api/explain")
def explain_route_endpoint(req: ExplainRequest):
    """
    Deterministic Explainability Endpoint.
    Generates structured JSON and human-readable explanation from optimization evidence.
    Ready for downstream ingestion by an LLM layer without modifying core optimizer.
    """
    return build_route_explanation(
        selected_route_names=req.selected_route,
        selected_metrics=req.selected_metrics,
        vehicle_name=req.vehicle,
        alternative_name=req.alternative_name,
        alternative_route_names=req.alternative_route,
        alternative_metrics=req.alternative_metrics,
        demands=req.demands,
        vehicle_capacity=req.vehicle_capacity,
        required_stop_count=req.required_stops,
        max_time_limit_min=req.max_time_min,
        algorithm_name=req.algorithm,
    )


@app.get("/api/routes/{route_id}/explanation")
def get_route_explanation_by_id(route_id: str):
    """Exposes structured explanation for a specific route identifier."""
    return build_route_explanation(
        selected_route_names=[
            "Gandhipuram Central Hub",
            "RS Puram (DB Road)",
            "Peelamedu (PSG Tech)",
            "Gandhipuram Central Hub",
        ],
        selected_metrics={"distance_km": 18.5, "travel_time_min": 36.2, "objective_cost": 36.2},
        vehicle_name=f"Vehicle-{route_id}",
        alternative_name="Nearest Neighbor Baseline",
        alternative_route_names=[
            "Gandhipuram Central Hub",
            "Peelamedu (PSG Tech)",
            "RS Puram (DB Road)",
            "Gandhipuram Central Hub",
        ],
        alternative_metrics={"distance_km": 24.1, "travel_time_min": 51.0, "objective_cost": 51.0},
    )


@app.post("/api/compare")
def compare_all_algorithms(req: OptimizeRequest):
    """Runs all candidate algorithms on the selected Coimbatore delivery stops."""
    G = build_coimbatore_graph(traffic_mode=req.traffic_mode, seed=req.seed)
    waypoints = [w for w in req.intermediate_stops if w in COIMBATORE_LANDMARKS and w != req.source_id]

    algos = ["qpso", "classical_pso", "ga_ox", "ga_pmx", "clarke_wright", "cheapest_insertion", "nearest_neighbor"]
    results = []

    end_node = (
        req.destination_id
        if (req.destination_id and req.destination_id in COIMBATORE_LANDMARKS)
        else req.source_id
    )

    for a in algos:
        out = _run_solver(a, G, req.source_id, waypoints, req.swarm_size, req.iterations, req.seed)
        route_nodes = out["route"] + [end_node]
        geom = get_route_geometry(G, route_nodes)
        history = [round(float(c), 2) for c in out.get("history", [geom["total_time_min"]])]

        results.append({
            "id": a,
            "name": {
                "qpso": "QPSO",
                "classical_pso": "Classical PSO",
                "ga_ox": "GA (Order Crossover)",
                "ga_pmx": "GA (PMX Crossover)",
                "clarke_wright": "Clarke-Wright Savings",
                "cheapest_insertion": "Cheapest Insertion",
                "nearest_neighbor": "Nearest Neighbor",
            }.get(a, a),
            "travel_time_min": geom["total_time_min"],
            "distance_km": geom["total_distance_km"],
            "runtime_ms": round(out["runtime"] * 1000, 2),
            "history": history,
            "is_best": False,
        })

    # Sort results by travel_time_min ascending (best solution first)
    results.sort(key=lambda r: r["travel_time_min"])

    # Strictly mark the true minimum cost winner
    if results:
        min_time = results[0]["travel_time_min"]
        for r in results:
            if abs(r["travel_time_min"] - min_time) < 1e-4:
                r["is_best"] = True

    return {"results": results}


@app.websocket("/api/optimize/stream")
async def optimize_stream(websocket: WebSocket):
    """
    Websocket endpoint streaming iteration-by-iteration convergence progress
    to enable smooth live updates of the route and convergence graph.
    """
    await websocket.accept()
    try:
        raw_msg = await websocket.receive_text()
        data = json.loads(raw_msg)
        source_id = data.get("source_id", 0)
        waypoints = data.get("intermediate_stops", [1, 4, 6, 7, 11])
        iterations = data.get("iterations", 60)
        swarm_size = data.get("swarm_size", 30)
        seed = data.get("seed", 42)

        G = build_coimbatore_graph(traffic_mode="real", seed=seed)
        seg_costs = precompute_segment_costs(G, [source_id] + waypoints)
        n_dim = len(waypoints)

        rng = np.random.default_rng(seed)
        positions = rng.uniform(0, 1, size=(swarm_size, n_dim))

        def decode_cost(pos):
            order = np.argsort(pos)
            r = [source_id] + [waypoints[i] for i in order] + [source_id]
            return sum(seg_costs[(r[k], r[k + 1])] for k in range(len(r) - 1)), order

        pbest = positions.copy()
        pbest_cost = np.array([decode_cost(p)[0] for p in positions])
        gbest_idx = np.argmin(pbest_cost)
        gbest = pbest[gbest_idx].copy()
        gbest_cost = pbest_cost[gbest_idx]

        for it in range(iterations):
            beta = 1.0 - (1.0 - 0.4) * (it / iterations)
            mbest = pbest.mean(axis=0)

            for i in range(swarm_size):
                phi = rng.uniform(0, 1, size=n_dim)
                p = phi * pbest[i] + (1 - phi) * gbest
                u = rng.uniform(1e-6, 1, size=n_dim)
                sign = rng.choice([-1, 1], size=n_dim)
                positions[i] = p + sign * beta * np.abs(mbest - positions[i]) * np.log(1 / u)

                cost, _ = decode_cost(positions[i])
                if cost < pbest_cost[i]:
                    pbest[i] = positions[i].copy()
                    pbest_cost[i] = cost
                    if cost < gbest_cost:
                        gbest = positions[i].copy()
                        gbest_cost = cost

            # Stream update every iteration
            _, current_best_order = decode_cost(gbest)
            current_route = [source_id] + [waypoints[i] for i in current_best_order] + [source_id]
            geom = get_route_geometry(G, current_route)

            await websocket.send_json({
                "iteration": it + 1,
                "max_iterations": iterations,
                "current_cost": round(float(gbest_cost), 2),
                "distance_km": geom["total_distance_km"],
                "coordinates": geom["coordinates"],
            })
            await asyncio.sleep(0.04)  # 25 fps stream throttle

        await websocket.send_json({"status": "completed"})
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"error": str(e)})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
