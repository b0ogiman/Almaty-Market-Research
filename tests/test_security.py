"""Tests for write-endpoint API key protection."""

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.config import get_settings
from app.security import require_write_api_key


def _build_app() -> FastAPI:
    app = FastAPI()

    @app.post("/protected")
    async def protected(_: None = Depends(require_write_api_key)) -> dict[str, bool]:
        return {"ok": True}

    return app


def test_write_auth_rejects_missing_api_key(monkeypatch):
    monkeypatch.setenv("WRITE_AUTH_ENABLED", "true")
    monkeypatch.setenv("API_KEY", "test-secret")
    get_settings.cache_clear()

    client = TestClient(_build_app())
    resp = client.post("/protected")
    assert resp.status_code == 401


def test_write_auth_accepts_valid_api_key(monkeypatch):
    monkeypatch.setenv("WRITE_AUTH_ENABLED", "true")
    monkeypatch.setenv("API_KEY", "test-secret")
    monkeypatch.setenv("AUTH_HEADER_NAME", "X-API-Key")
    get_settings.cache_clear()

    client = TestClient(_build_app())
    resp = client.post("/protected", headers={"X-API-Key": "test-secret"})
    assert resp.status_code == 200
    assert resp.json()["ok"] is True
