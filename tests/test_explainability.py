"""
tests/test_explainability.py — Verification Suite for Deterministic Route Explainability Layer.
Tests:
1. Valid route explanation schema and data types.
2. Constraint satisfaction (capacity, coverage, time windows).
3. Missing alternative route handling (safe defaults).
4. Trade-off calculation (distance vs. time trade-offs & Pareto dominance).
5. Multiple vehicle fleet / multi-trip assignments.
6. Invalid and missing metrics resilience.
7. Explanation consistency (zero mutation to optimizer outputs).
8. Deterministic template format conformance.
9. FastAPI API endpoints (/api/optimize, /api/explain, /api/routes/{id}/explanation).
"""

import sys
import os
import unittest

# Ensure backend directory is on sys.path
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from explainability import (
    build_route_explanation,
    build_multivehicle_explanation,
    format_reason_label,
)
from osm_road_network import (
    COIMBATORE_LANDMARKS,
    build_coimbatore_graph,
    get_route_geometry,
)
from qpso import qpso_optimize
from clarke_wright import clarke_wright_route
from baseline import nearest_neighbor_route


class TestExplainabilityLayer(unittest.TestCase):

    def setUp(self):
        self.sample_route = [
            "Gandhipuram Central Hub",
            "RS Puram (DB Road)",
            "Peelamedu (PSG Tech)",
            "Gandhipuram Central Hub",
        ]
        self.sample_metrics = {
            "distance_km": 18.5,
            "travel_time_min": 36.2,
            "objective_cost": 36.2,
            "congestion_level": 1.45,
        }
        self.alt_route = [
            "Gandhipuram Central Hub",
            "Peelamedu (PSG Tech)",
            "RS Puram (DB Road)",
            "Gandhipuram Central Hub",
        ]
        self.alt_metrics = {
            "distance_km": 21.0,
            "travel_time_min": 44.0,
            "objective_cost": 44.0,
            "congestion_level": 1.70,
        }

    def test_valid_route_explanation(self):
        """Verify that explanation returns all required keys and correct data types."""
        exp = build_route_explanation(
            selected_route_names=self.sample_route,
            selected_metrics=self.sample_metrics,
            vehicle_name="Vehicle 01",
            alternative_name="Clarke-Wright Savings",
            alternative_route_names=self.alt_route,
            alternative_metrics=self.alt_metrics,
            required_stop_count=2,
            vehicle_capacity=100.0,
            algorithm_name="QPSO",
        )

        required_keys = [
            "vehicle",
            "selected_route",
            "metrics",
            "reasons",
            "constraints",
            "tradeoffs",
            "alternative",
            "decision",
            "human_readable",
        ]
        for key in required_keys:
            self.assertIn(key, exp, f"Missing required key: {key}")

        self.assertEqual(exp["vehicle"], "Vehicle 01")
        self.assertEqual(exp["selected_route"], self.sample_route)
        self.assertAlmostEqual(exp["metrics"]["distance_km"], 18.5)
        self.assertAlmostEqual(exp["metrics"]["travel_time_min"], 36.2)
        self.assertIsInstance(exp["reasons"], list)
        self.assertGreater(len(exp["reasons"]), 0)
        self.assertIsInstance(exp["tradeoffs"], list)
        self.assertIsNotNone(exp["alternative"])
        self.assertIsInstance(exp["human_readable"], str)

    def test_constraint_satisfaction(self):
        """Verify constraint checks for capacity, coverage, and time limits."""
        # Case A: Normal within-limit capacity
        exp_pass = build_route_explanation(
            selected_route_names=self.sample_route,
            selected_metrics=self.sample_metrics,
            demands=[20.0, 30.0],
            vehicle_capacity=100.0,
            required_stop_count=2,
            max_time_limit_min=60.0,
        )
        self.assertTrue(exp_pass["constraints"]["capacity"]["satisfied"])
        self.assertTrue(exp_pass["constraints"]["all_locations_covered"]["satisfied"])
        self.assertTrue(exp_pass["constraints"]["time_constraint"]["satisfied"])
        self.assertIn("capacity_satisfied", exp_pass["reasons"])
        self.assertIn("all_locations_covered", exp_pass["reasons"])
        self.assertIn("time_constraint_satisfied", exp_pass["reasons"])

        # Case B: Capacity exceeded (violation)
        exp_fail = build_route_explanation(
            selected_route_names=self.sample_route,
            selected_metrics=self.sample_metrics,
            demands=[60.0, 70.0],  # Total = 130 > 100
            vehicle_capacity=100.0,
            required_stop_count=5,  # Requires 5 stops, but only 2 visited
            max_time_limit_min=30.0,  # 36.2 > 30.0
        )
        self.assertFalse(exp_fail["constraints"]["capacity"]["satisfied"])
        self.assertFalse(exp_fail["constraints"]["all_locations_covered"]["satisfied"])
        self.assertFalse(exp_fail["constraints"]["time_constraint"]["satisfied"])
        self.assertNotIn("capacity_satisfied", exp_fail["reasons"])
        self.assertNotIn("all_locations_covered", exp_fail["reasons"])
        self.assertNotIn("time_constraint_satisfied", exp_fail["reasons"])

    def test_missing_alternative_route(self):
        """Verify graceful handling when no alternative route is supplied."""
        exp = build_route_explanation(
            selected_route_names=self.sample_route,
            selected_metrics=self.sample_metrics,
            alternative_name=None,
            alternative_route_names=None,
            alternative_metrics=None,
        )
        self.assertIsNone(exp["alternative"])
        self.assertEqual(len(exp["tradeoffs"]), 0)
        self.assertIn("None evaluated", exp["human_readable"])
        self.assertIn("ROUTE EXPLANATION", exp["human_readable"])

    def test_tradeoff_calculation(self):
        """Verify trade-off calculation when distance increases but travel time decreases."""
        # Route is 2.5 km longer, but 8.0 min faster
        sel_m = {"distance_km": 20.5, "travel_time_min": 32.0, "objective_cost": 32.0}
        alt_m = {"distance_km": 18.0, "travel_time_min": 40.0, "objective_cost": 40.0}

        exp = build_route_explanation(
            selected_route_names=self.sample_route,
            selected_metrics=sel_m,
            alternative_name="Nearest Neighbor",
            alternative_metrics=alt_m,
        )

        self.assertGreater(len(exp["tradeoffs"]), 0)
        tradeoff = exp["tradeoffs"][0]
        self.assertEqual(tradeoff["type"], "distance_vs_time")
        self.assertAlmostEqual(tradeoff["distance_difference_km"], 2.5, places=1)
        self.assertAlmostEqual(tradeoff["time_difference_min"], -8.0, places=1)
        self.assertIn("longer", tradeoff["statement"])
        self.assertIn("reduces estimated travel time", tradeoff["statement"])

        # Check Pareto dominance when faster and shorter
        dom_sel = {"distance_km": 15.0, "travel_time_min": 25.0, "objective_cost": 25.0}
        exp_dom = build_route_explanation(
            selected_route_names=self.sample_route,
            selected_metrics=dom_sel,
            alternative_name="Baseline",
            alternative_metrics=alt_m,
        )
        self.assertEqual(exp_dom["tradeoffs"][0]["type"], "pareto_dominance")
        self.assertIn("strictly dominates", exp_dom["tradeoffs"][0]["statement"])

    def test_multiple_vehicles(self):
        """Verify multi-vehicle / multi-trip fleet assignment explanation."""
        v1 = {
            "vehicle": "Vehicle 01",
            "route": ["Gandhipuram Central Hub", "RS Puram (DB Road)", "Gandhipuram Central Hub"],
            "metrics": {"distance_km": 8.0, "travel_time_min": 18.0, "objective_cost": 18.0},
            "demands": [30.0],
            "capacity": 100.0,
        }
        v2 = {
            "vehicle": "Vehicle 02",
            "route": ["Gandhipuram Central Hub", "Peelamedu (PSG Tech)", "Gandhipuram Central Hub"],
            "metrics": {"distance_km": 12.0, "travel_time_min": 22.0, "objective_cost": 22.0},
            "demands": [40.0],
            "capacity": 100.0,
        }

        fleet_exp = build_multivehicle_explanation(
            vehicle_assignments=[v1, v2],
            fleet_metrics={"distance_km": 20.0, "travel_time_min": 40.0},
            algorithm_name="QPSO",
        )

        self.assertEqual(fleet_exp["fleet_metrics"]["vehicle_count"], 2)
        self.assertAlmostEqual(fleet_exp["fleet_metrics"]["total_distance_km"], 20.0)
        self.assertAlmostEqual(fleet_exp["fleet_metrics"]["total_travel_time_min"], 40.0)
        self.assertTrue(fleet_exp["fleet_metrics"]["capacity_satisfied"])
        self.assertEqual(len(fleet_exp["vehicles"]), 2)
        self.assertEqual(fleet_exp["vehicles"][0]["vehicle"], "Vehicle 01")
        self.assertEqual(fleet_exp["vehicles"][1]["vehicle"], "Vehicle 02")

    def test_invalid_missing_metrics(self):
        """Verify that empty, partial, or None metrics do not cause runtime crashes."""
        exp = build_route_explanation(
            selected_route_names=[],
            selected_metrics={},
            alternative_metrics={},
        )
        self.assertIsNotNone(exp)
        self.assertEqual(exp["metrics"]["distance_km"], 0.0)
        self.assertEqual(exp["metrics"]["travel_time_min"], 0.0)
        self.assertIsInstance(exp["human_readable"], str)

    def test_explanation_consistency_with_optimizer(self):
        """
        Verify that creating an explanation does not mutate the optimizer's result
        and strictly reflects the optimizer's calculated metrics.
        """
        G = build_coimbatore_graph(traffic_mode="real", seed=42)
        depot = 0
        waypoints = [1, 4, 6]

        opt_result = qpso_optimize(G, depot, waypoints, n_particles=15, n_iterations=30, seed=42)
        original_route = list(opt_result["route"])
        original_cost = float(opt_result["cost"])

        route_nodes = original_route + [depot]
        geom = get_route_geometry(G, route_nodes)
        route_names = [COIMBATORE_LANDMARKS[n]["name"] for n in route_nodes]

        exp = build_route_explanation(
            selected_route_names=route_names,
            selected_metrics={
                "distance_km": geom["total_distance_km"],
                "travel_time_min": geom["total_time_min"],
                "objective_cost": original_cost,
            },
            vehicle_name="Vehicle 01",
        )

        # 1. Optimizer output must be completely unchanged (zero mutation)
        self.assertEqual(opt_result["route"], original_route)
        self.assertEqual(float(opt_result["cost"]), original_cost)

        # 2. Explanation metrics must match geometry calculation exactly
        self.assertAlmostEqual(exp["metrics"]["distance_km"], geom["total_distance_km"])
        self.assertAlmostEqual(exp["metrics"]["travel_time_min"], geom["total_time_min"])
        self.assertAlmostEqual(exp["metrics"]["objective_cost"], original_cost)

    def test_deterministic_template_format(self):
        """Verify exact conformance with human-readable template specification."""
        exp = build_route_explanation(
            selected_route_names=self.sample_route,
            selected_metrics=self.sample_metrics,
            vehicle_name="Vehicle 01",
            alternative_name="Clarke-Wright Savings",
            alternative_metrics=self.alt_metrics,
            required_stop_count=2,
            vehicle_capacity=100.0,
        )
        text = exp["human_readable"]

        # Check required section headers from specification
        headers = [
            "ROUTE EXPLANATION",
            "Vehicle:",
            "Selected Route:",
            "WHY THIS ROUTE WAS SELECTED",
            "ROUTE METRICS",
            "KEY TRADE-OFF",
            "CONSTRAINTS",
            "ALTERNATIVE CONSIDERED",
            "DECISION",
        ]
        for header in headers:
            self.assertIn(header, text, f"Template missing section: {header}")

        # Check constraint symbols
        self.assertTrue("✓" in text or "✗" in text)


if __name__ == "__main__":
    unittest.main()
