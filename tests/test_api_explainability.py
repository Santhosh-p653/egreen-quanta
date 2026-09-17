"""
tests/test_api_explainability.py — API Integration Tests for Explainability Endpoints.
Verifies:
- POST /api/optimize returns valid explanation and alternative route in yellow format
- POST /api/explain processes explain requests deterministically
- GET /api/routes/{id}/explanation returns structured explanation
"""

import sys
import os
import unittest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi.testclient import TestClient
from api import app


class TestApiExplainability(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_optimize_endpoint_has_explanation_and_alternative(self):
        """Test POST /api/optimize contains explanation and alternative_route."""
        res = self.client.post("/api/optimize", json={
            "source_id": 0,
            "intermediate_stops": [1, 4, 6],
            "algorithm": "qpso",
            "iterations": 20,
            "swarm_size": 15,
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()

        # Verify alternative route exists with coordinates
        self.assertIn("alternative_route", data)
        self.assertIn("coordinates", data["alternative_route"])
        self.assertGreater(len(data["alternative_route"]["coordinates"]), 0)
        self.assertIn("name", data["alternative_route"])

        # Verify explanation structure
        self.assertIn("explanation", data)
        exp = data["explanation"]
        self.assertIn("vehicle", exp)
        self.assertIn("selected_route", exp)
        self.assertIn("metrics", exp)
        self.assertIn("reasons", exp)
        self.assertIn("constraints", exp)
        self.assertIn("human_readable", exp)

    def test_dedicated_explain_endpoint(self):
        """Test POST /api/explain accepts custom routes and metrics."""
        payload = {
            "vehicle": "Vehicle 02",
            "selected_route": ["Gandhipuram Central Hub", "RS Puram (DB Road)", "Gandhipuram Central Hub"],
            "selected_metrics": {"distance_km": 10.0, "travel_time_min": 22.0, "objective_cost": 22.0},
            "alternative_name": "Nearest Neighbor",
            "alternative_route": ["Gandhipuram Central Hub", "Peelamedu (PSG Tech)", "Gandhipuram Central Hub"],
            "alternative_metrics": {"distance_km": 14.0, "travel_time_min": 30.0, "objective_cost": 30.0},
            "vehicle_capacity": 100.0,
            "demands": [30.0],
            "required_stops": 1,
            "algorithm": "QPSO",
        }
        res = self.client.post("/api/explain", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["vehicle"], "Vehicle 02")
        self.assertIn("lower_travel_time", data["reasons"])
        self.assertIn("lower_total_distance", data["reasons"])
        self.assertTrue(data["constraints"]["capacity"]["satisfied"])

    def test_get_route_explanation_by_id(self):
        """Test GET /api/routes/{route_id}/explanation."""
        res = self.client.get("/api/routes/route_42/explanation")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("vehicle", data)
        self.assertIn("Vehicle-route_42", data["vehicle"])
        self.assertIn("human_readable", data)


if __name__ == "__main__":
    unittest.main()
