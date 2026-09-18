"""
test_auth_database.py — Unit and Integration Tests for Database, Auth & Admin Endpoints.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from fastapi.testclient import TestClient
from api import app
from auth import get_password_hash, verify_password, create_access_token, seed_default_admin
from database import SessionLocal, init_db
from models import User, OptimizationLog


class TestAuthAndDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.db = SessionLocal()
        seed_default_admin(cls.db)
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_password_hash_and_verify(self):
        plain = "secureSecret2026"
        hashed = get_password_hash(plain)
        self.assertTrue(verify_password(plain, hashed))
        self.assertFalse(verify_password("wrongPassword", hashed))

    def test_jwt_token_generation(self):
        token = create_access_token({"sub": "admin", "role": "admin"})
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 20)

    def test_admin_login_endpoint(self):
        resp = self.client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["username"], "admin")
        self.assertEqual(data["role"], "admin")

    def test_invalid_login_rejected(self):
        resp = self.client.post("/api/auth/login", json={"username": "admin", "password": "wrong_password"})
        self.assertEqual(resp.status_code, 401)

    def test_admin_system_status(self):
        resp = self.client.get("/api/admin/system")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("database", data)
        self.assertEqual(data["landmarks_count"], 36)
        self.assertIn("70+ km", data["radius_coverage_km"])

    def test_optimization_logging_and_admin_logs(self):
        # Run optimization on regional stops
        opt_resp = self.client.post(
            "/api/optimize",
            json={
                "source_id": 0,
                "intermediate_stops": [6, 18, 24, 30],
                "algorithm": "ga",
                "ga_crossover": "pmx",
                "ga_mutation_rate": 0.2,
                "iterations": 25,
            },
        )
        self.assertEqual(opt_resp.status_code, 200)

        # Query admin logs
        logs_resp = self.client.get("/api/admin/logs")
        self.assertEqual(logs_resp.status_code, 200)
        logs = logs_resp.json()
        self.assertIsInstance(logs, list)
        self.assertTrue(len(logs) > 0)
        latest = logs[0]
        self.assertIn("total_distance_km", latest)
        self.assertIn("total_time_min", latest)


if __name__ == "__main__":
    unittest.main()
