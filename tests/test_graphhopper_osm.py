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
        """Verify graph has 36 landmarks and is 100% connected."""
        self.assertEqual(len(COIMBATORE_LANDMARKS), 36)
        G = build_coimbatore_graph()
        self.assertEqual(G.number_of_nodes(), 36)
        self.assertTrue(nx.is_connected(G))

    def test_regional_radius_exceeds_60km(self):
        """Verify the expanded regional network spans across 60-70+ km."""
        depot = COIMBATORE_LANDMARKS[0]
        pollachi = COIMBATORE_LANDMARKS[24]
        mettupalayam = COIMBATORE_LANDMARKS[30]
        walayar = COIMBATORE_LANDMARKS[27]
        tiruppur_border = COIMBATORE_LANDMARKS[34]

        d_pollachi = haversine_distance_km(depot["lat"], depot["lon"], pollachi["lat"], pollachi["lon"])
        d_mettupalayam = haversine_distance_km(depot["lat"], depot["lon"], mettupalayam["lat"], mettupalayam["lon"])

        # North-South and East-West regional spans
        ns_span = haversine_distance_km(mettupalayam["lat"], mettupalayam["lon"], pollachi["lat"], pollachi["lon"])
        ew_span = haversine_distance_km(walayar["lat"], walayar["lon"], tiruppur_border["lat"], tiruppur_border["lon"])

        self.assertGreater(d_pollachi, 35.0)
        self.assertGreater(d_mettupalayam, 30.0)
        self.assertGreater(ns_span, 65.0)  # Over 65 km North-South regional diameter!
        self.assertGreater(ew_span, 50.0)  # Over 50 km East-West regional diameter!

    def test_benchmark_scenarios_presence(self):
        """Verify curated benchmark scenarios exist with valid stop IDs."""
        self.assertIn("metro_greater", BENCHMARK_SCENARIOS)
        self.assertIn("cbd_express", BENCHMARK_SCENARIOS)
        self.assertIn("regional_conglomerate", BENCHMARK_SCENARIOS)
        self.assertIn("interstate_cargo", BENCHMARK_SCENARIOS)

        regional = BENCHMARK_SCENARIOS["regional_conglomerate"]
        self.assertEqual(len(regional["stops"]), 16)
        for stop_id in regional["stops"]:
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
