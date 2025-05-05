from fastapi.testclient import TestClient
from unittest.case import TestCase
from backend.main import app

client = TestClient(app)

class TestHealthCheck(TestCase):
    def setUp(self):
        self.client = client

    def tearDown(self):
        pass

    def test_health_check(self):
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})