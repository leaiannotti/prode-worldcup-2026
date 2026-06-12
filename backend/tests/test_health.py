import pytest
from app import create_app


class TestHealthEndpoint:
    """Verify /health endpoint for smoke tests (T-12-ter)."""

    def test_health_returns_200(self, client):
        """GET /health must return HTTP 200."""
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_returns_ok_status_json(self, client):
        """GET /health must return JSON with status: ok."""
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data == {"status": "ok"}
