"""Unit and integration tests for API health and metadata endpoints."""

import unittest
from fastapi.testclient import TestClient
from app.main import app


class TestHealthEndpoint(unittest.TestCase):
    """Test health check and application bootstrap."""

    def setUp(self):
        self.client = TestClient(app)

    def test_health_check_returns_200_and_success_envelope(self):
        """Verify GET /api/health returns 200 with standard envelope."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsInstance(data, dict)
        self.assertTrue(data.get("success"))
        self.assertIn("message", data)
        self.assertEqual(data["message"], "CloudLand API is running")

    def test_openapi_schema_accessible(self):
        """Verify OpenAPI JSON schema is generated correctly."""
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)

        schema = response.json()
        self.assertEqual(schema.get("info", {}).get("title"), "CloudLand API")
        self.assertEqual(schema.get("info", {}).get("version"), "1.0.0")


if __name__ == "__main__":
    unittest.main()
