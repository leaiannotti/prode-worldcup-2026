import os
import pytest
from app import create_app


class TestCORSConfiguration:
    """Verify CORS origin is driven by FRONTEND_URL env var (REQ-7)."""

    def test_cors_uses_frontend_url_env_var(self, monkeypatch):
        """When FRONTEND_URL is set, CORS origin must equal that URL."""
        monkeypatch.setenv("FRONTEND_URL", "https://example.test")
        app = create_app("testing")
        with app.test_client() as client:
            resp = client.options(
                "/api/auth/login",
                headers={"Origin": "https://example.test"},
            )
        assert resp.headers.get("Access-Control-Allow-Origin") == "https://example.test"

    def test_cors_defaults_to_localhost_in_dev(self, monkeypatch):
        """When FRONTEND_URL is unset and not production, default to localhost:5173."""
        monkeypatch.delenv("FRONTEND_URL", raising=False)
        app = create_app("testing")
        with app.test_client() as client:
            resp = client.options(
                "/api/auth/login",
                headers={"Origin": "http://localhost:5173"},
            )
        assert resp.headers.get("Access-Control-Allow-Origin") == "http://localhost:5173"

    def test_cors_fails_fast_in_production_without_frontend_url(self, monkeypatch):
        """When FRONTEND_URL is unset in production, app init must raise RuntimeError."""
        monkeypatch.delenv("FRONTEND_URL", raising=False)
        monkeypatch.setenv("FLASK_ENV", "production")
        monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/db")
        with pytest.raises(RuntimeError, match="FRONTEND_URL is required in production"):
            create_app()
