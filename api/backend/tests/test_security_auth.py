"""Security and Authentication tests verifying access control and credentials checks."""

import unittest
from fastapi.testclient import TestClient

from app.main import app
from app import config


class TestSecurityAndAuth(unittest.TestCase):
    """Verify authentication boundaries, token verification, and credentials checks."""

    def setUp(self):
        self.client = TestClient(app)

    def test_login_missing_credentials_returns_400(self):
        """Verify empty username/password returns 400 Bad Request."""
        res = self.client.post("/api/auth/login", json={})
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertFalse(data.get("success"))

    def test_login_invalid_password_returns_401(self):
        """Verify wrong password is rejected with 401."""
        res = self.client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "wrong_password_xyz_999"},
        )
        self.assertEqual(res.status_code, 401)
        data = res.json()
        self.assertFalse(data.get("success"))

    def test_login_weak_passwords_rejected(self):
        """Verify previously hardcoded passwords (123456, admin123) are rejected."""
        weak_passwords = ["123456", "admin123", "password", "supersecret", "cloudland"]
        for pw in weak_passwords:
            res = self.client.post(
                "/api/auth/login",
                json={"username": "admin", "password": pw},
            )
            self.assertEqual(
                res.status_code,
                401,
                f"Weak password '{pw}' should be rejected with 401",
            )

    def test_protected_routes_require_authorization_header(self):
        """Verify protected admin routes return 401 without Bearer token."""
        protected_endpoints = [
            "/api/products/admin/all",
            "/api/categories/admin/1",
            "/api/consultations/admin",
        ]
        for ep in protected_endpoints:
            res = self.client.get(ep)
            self.assertEqual(
                res.status_code,
                401,
                f"Endpoint {ep} must require authentication",
            )
            data = res.json()
            self.assertFalse(data.get("success"))

    def test_protected_routes_reject_invalid_token(self):
        """Verify invalid or forged token is rejected."""
        headers = {"Authorization": "Bearer invalid.forged.jwt.token"}
        res = self.client.get("/api/products/admin/all", headers=headers)
        self.assertEqual(res.status_code, 401)
        data = res.json()
        self.assertFalse(data.get("success"))


if __name__ == "__main__":
    unittest.main()
