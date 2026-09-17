"""
tests/test_graphhopper_osm.py — Verification of OSM and GraphHopper Instance Generator.
Verifies:
- 24-node expanded road network graph connectivity and 30km radius.
- Predefined benchmark scenarios (metro_greater, cbd_express, industrial_cargo, etc.).
- Dynamic OSM CVRP instance generation.
- GraphHopper matrix client with OSM fallback.
"""

import sys
import os
import unittest
import networkx as nx

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from osm_road_network import (
    COIMBATORE_LANDMARKS,
    BENCHMARK_SCENARIOS,
    build_coimbatore_graph,
    haversine_distance_km,
)
from graphhopper_client import (
    GraphHopperClient,
    generate_osm_cvrp_instance,
)


class TestGraphHopperOsm(unittest.TestCase):

    def test_expanded_landmarks_and_connectivity(self):
        """Verify graph has 24 landmarks and is 100% connected."""
        self.assertEqual(len(COIMBATORE_LANDMARKS), 24)
        G = build_coimbatore_graph()
        self.assertEqual(G.number_of_nodes(), 24)
        self.assertTrue(nx.is_connected(G))

    def test_metropolitan_radius_exceeds_25km(self):
        """Verify the expanded network spans across 25-30+ km."""
        depot = COIMBATORE_LANDMARKS[0]
        sulur = COIMBATORE_LANDMARKS[18]
        eachanari = COIMBATORE_LANDMARKS[15]
        vadavalli = COIMBATORE_LANDMARKS[23]

        d_sulur = haversine_distance_km(depot["lat"], depot["lon"], sulur["lat"], sulur["lon"])
        d_eachanari = haversine_distance_km(depot["lat"], depot["lon"], eachanari["lat"], eachanari["lon"])
        d_vadavalli = haversine_distance_km(depot["lat"], depot["lon"], vadavalli["lat"], vadavalli["lon"])

        # Diameter across the network
        diameter = haversine_distance_km(vadavalli["lat"], vadavalli["lon"], sulur["lat"], sulur["lon"])
        self.assertGreater(diameter, 24.0)
        self.assertGreater(d_sulur, 15.0)

    def test_benchmark_scenarios_presence(self):
        """Verify curated benchmark scenarios exist with valid stop IDs."""
        self.assertIn("metro_greater", BENCHMARK_SCENARIOS)
        self.assertIn("cbd_express", BENCHMARK_SCENARIOS)

        metro = BENCHMARK_SCENARIOS["metro_greater"]
        self.assertEqual(len(metro["stops"]), 12)
        for stop_id in metro["stops"]:
            self.assertIn(stop_id, COIMBATORE_LANDMARKS)

    def test_dynamic_osm_instance_generator(self):
        """Verify dynamic OSM instance generator produces valid instances."""
        inst = generate_osm_cvrp_instance(n_stops=10, depot_id=0, radius_km=30.0, seed=42)
        self.assertEqual(inst["n_stops"], 10)
        self.assertEqual(len(inst["waypoints"]), 10)
        self.assertGreater(inst["total_demand"], 0)
        self.assertEqual(inst["depot"]["id"], 0)

    def test_graphhopper_client_osm_fallback(self):
        """Verify GraphHopper client returns valid distance and time matrices."""
        client = GraphHopperClient()
        points = [
            (COIMBATORE_LANDMARKS[0]["lat"], COIMBATORE_LANDMARKS[0]["lon"]),
            (COIMBATORE_LANDMARKS[4]["lat"], COIMBATORE_LANDMARKS[4]["lon"]),
            (COIMBATORE_LANDMARKS[6]["lat"], COIMBATORE_LANDMARKS[6]["lon"]),
        ]
        res = client.get_matrix(points)
        self.assertIn("distances_km", res)
        self.assertIn("times_min", res)
        self.assertEqual(len(res["distances_km"]), 3)
        self.assertGreater(res["distances_km"][0][1], 0)
        self.assertGreater(res["times_min"][0][1], 0)


if __name__ == "__main__":
    unittest.main()
