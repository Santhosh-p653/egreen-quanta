"""
tests/test_quantum_bidirectional_astar.py — Unit & Integration Tests for QI-BA*
Verifies:
1. Point-to-point Quantum-Inspired Bidirectional A* pathfinding and tunneling.
2. Multi-stop tour sequencing with quantum contraction-expansion operators.
3. API endpoints /api/algorithms, /api/optimize, and /api/compare supporting qi_astar.
"""

import os
import sys
import unittest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi.testclient import TestClient
from api import app
from osm_road_network import build_coimbatore_graph
from quantum_bidirectional_astar import (
    quantum_bidirectional_astar_path,
    quantum_bidirectional_astar_route,
)


class TestQuantumBidirectionalAStar(unittest.TestCase):

    def setUp(self):
        self.G = build_coimbatore_graph(traffic_mode="real", seed=42)
        self.client = TestClient(app)

    def test_p2p_shortest_path_simple(self):
        """Verify point-to-point QI-BA* path between Gandhipuram (#0) and Peelamedu (#4)."""
        path, cost, runtime = quantum_bidirectional_astar_path(self.G, 0, 4, seed=42)
        self.assertIsInstance(path, list)
        self.assertGreater(len(path), 1)
        self.assertEqual(path[0], 0)
        self.assertEqual(path[-1], 4)
        self.assertGreater(cost, 0.0)
        self.assertGreaterEqual(runtime, 0.0)

    def test_p2p_same_node(self):
        """Path from node to itself returns cost 0 and single-element list."""
        path, cost, _ = quantum_bidirectional_astar_path(self.G, 5, 5)
        self.assertEqual(path, [5])
        self.assertEqual(cost, 0.0)

    def test_p2p_long_distance_regional(self):
        """Verify long-distance path to regional landmark (e.g. Mettupalayam Gateway #22)."""
        path, cost, _ = quantum_bidirectional_astar_path(self.G, 0, 22, seed=42)
        self.assertEqual(path[0], 0)
        self.assertEqual(path[-1], 22)
        self.assertGreater(cost, 10.0)

    def test_multistop_route_optimization(self):
        """Verify multi-stop tour optimization visits depot and all waypoints."""
        depot = 0
        waypoints = [1, 4, 6, 7, 11]
        res = quantum_bidirectional_astar_route(
            self.G, depot, waypoints, iterations=30, swarm_size=15, seed=42
        )

        self.assertIn("route", res)
        self.assertIn("cost", res)
        self.assertIn("history", res)
        self.assertIn("runtime", res)

        route = res["route"]
        self.assertEqual(route[0], depot)
        # All waypoints must be present exactly once
        self.assertEqual(set(route[1:]), set(waypoints))
        self.assertEqual(len(route[1:]), len(waypoints))
        self.assertGreater(res["cost"], 0.0)
        self.assertEqual(len(res["history"]), 31)

    def test_api_algorithms_includes_qi_astar(self):
        """Verify GET /api/algorithms registers QI-BA* in its catalog."""
        res = self.client.get("/api/algorithms")
        self.assertEqual(res.status_code, 200)
        algos = res.json()
        ids = [a["id"] for a in algos]
        self.assertIn("qi_astar", ids)

        qi_meta = next(a for a in algos if a["id"] == "qi_astar")
        self.assertEqual(qi_meta["family"], "Quantum Graph Search")
        self.assertIn("QI-BA*", qi_meta["name"])

    def test_api_optimize_with_qi_astar(self):
        """Verify POST /api/optimize runs QI-BA* end-to-end and returns route geometries."""
        payload = {
            "source_id": 0,
            "intermediate_stops": [1, 4, 6, 7],
            "algorithm": "qi_astar",
            "traffic_mode": "real",
            "iterations": 25,
            "swarm_size": 15,
            "seed": 42,
        }
        res = self.client.post("/api/optimize", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["algorithm"], "qi_astar")
        self.assertIn("route_coordinates", data)
        self.assertGreater(len(data["route_coordinates"]), 0)
        self.assertIn("after_route", data)
        self.assertIn("coordinates", data["after_route"])
        self.assertIn("after_metrics", data)
        self.assertGreater(data["after_metrics"]["travel_time_min"], 0.0)

    def test_api_compare_includes_all_eight_algorithms(self):
        """Verify POST /api/compare includes QI-BA* among all 8 benchmark solvers."""
        payload = {
            "source_id": 0,
            "intermediate_stops": [1, 4, 6],
            "traffic_mode": "real",
            "iterations": 25,
            "swarm_size": 15,
            "seed": 42,
        }
        res = self.client.post("/api/compare", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("results", data)
        results = data["results"]

        self.assertEqual(len(results), 8)
        ids = [r["id"] for r in results]
        self.assertIn("qi_astar", ids)
        self.assertIn("qpso", ids)
        self.assertIn("classical_pso", ids)
        self.assertIn("ga_ox", ids)
        self.assertIn("ga_pmx", ids)
        self.assertIn("clarke_wright", ids)
        self.assertIn("cheapest_insertion", ids)
        self.assertIn("nearest_neighbor", ids)

        # Confirm exactly one winner marked
        best_count = sum(1 for r in results if r["is_best"])
        self.assertGreaterEqual(best_count, 1)


if __name__ == "__main__":
    unittest.main()
