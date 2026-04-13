"""API integration tests for core endpoints.

These tests use FastAPI TestClient with deterministic service mocks.
No external Redis/LLM/API calls are required.
"""

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

import app.main as main_module
from app.config import get_settings
from app.database import get_db


NOW = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
UUID1 = UUID("00000000-0000-0000-0000-000000000001")
UUID2 = UUID("00000000-0000-0000-0000-000000000002")


@pytest.fixture
def client(monkeypatch):
    """Create test client with deterministic auth config and DB override."""
    monkeypatch.setenv("WRITE_AUTH_ENABLED", "true")
    monkeypatch.setenv("API_KEY", "test-api-key")
    monkeypatch.setenv("AUTH_HEADER_NAME", "X-API-Key")
    get_settings.cache_clear()

    async def _override_get_db():
        yield object()

    main_module.settings.scheduler_enabled = False
    main_module.app.dependency_overrides[get_db] = _override_get_db
    with TestClient(main_module.app) as c:
        yield c
    main_module.app.dependency_overrides.clear()


def _auth_headers() -> dict[str, str]:
    return {"X-API-Key": "test-api-key"}


def test_data_ingest_success(client, monkeypatch):
    class FakeDataService:
        def __init__(self, db):
            self.db = db

        async def ingest(self, request):
            return 1, 0, [UUID1]

    monkeypatch.setattr("app.routers.data.DataIngestionService", FakeDataService)
    payload = {
        "items": [
            {
                "sector": "retail",
                "district": "Almaly",
                "metric_name": "demand",
                "metric_value": 0.7,
                "source": "manual",
            }
        ]
    }
    resp = client.post("/api/v1/data/ingest", json=payload, headers=_auth_headers())
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["ingested"] == 1


def test_data_ingest_validation_error(client):
    resp = client.post("/api/v1/data/ingest", json={}, headers=_auth_headers())
    assert resp.status_code == 422


def test_data_ingest_auth_failure(client):
    payload = {"items": []}
    resp = client.post("/api/v1/data/ingest", json=payload)
    assert resp.status_code == 401


def test_data_ingest_failure_scenario(client, monkeypatch):
    class FailingDataService:
        def __init__(self, db):
            self.db = db

        async def ingest(self, request):
            raise RuntimeError("ingest failed")

    monkeypatch.setattr("app.routers.data.DataIngestionService", FailingDataService)
    payload = {
        "items": [
            {
                "sector": "retail",
                "district": "Almaly",
                "metric_name": "demand",
                "metric_value": 0.7,
                "source": "manual",
            }
        ]
    }
    resp = client.post("/api/v1/data/ingest", json=payload, headers=_auth_headers())
    assert resp.status_code == 500


def test_data_list_success(client, monkeypatch):
    class FakeDataService:
        def __init__(self, db):
            self.db = db

        async def list_data(self, **kwargs):
            item = SimpleNamespace(
                id=UUID1,
                sector="retail",
                district="Almaly",
                metric_name="demand",
                metric_value=0.7,
                unit=None,
                source="manual",
                created_at=NOW,
            )
            return [item], 1

    monkeypatch.setattr("app.routers.data.DataIngestionService", FakeDataService)
    resp = client.get("/api/v1/data?page=1&size=20")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


def test_data_list_validation_error(client):
    resp = client.get("/api/v1/data?page=0")
    assert resp.status_code == 422


def test_data_list_failure_scenario(client, monkeypatch):
    class FailingDataService:
        def __init__(self, db):
            self.db = db

        async def list_data(self, **kwargs):
            raise RuntimeError("list failed")

    monkeypatch.setattr("app.routers.data.DataIngestionService", FailingDataService)
    resp = client.get("/api/v1/data")
    assert resp.status_code == 500


def test_analysis_market_success(client, monkeypatch):
    class FakeAnalysisService:
        def __init__(self, db):
            self.db = db

        async def analyze(self, **kwargs):
            return SimpleNamespace(
                id=UUID1,
                sector="retail",
                district="Almaly",
                summary="ok",
                score=0.81,
                insights={"demand": 0.8},
                created_at=NOW,
            )

    monkeypatch.setattr("app.routers.analysis.MarketAnalysisService", FakeAnalysisService)
    resp = client.post("/api/v1/analysis/market", json={"sector": "retail"})
    assert resp.status_code == 200
    assert resp.json()["score"] == 0.81


def test_analysis_market_validation_error(client):
    resp = client.post("/api/v1/analysis/market", json={"sector": "x" * 300})
    assert resp.status_code == 422


def test_analysis_market_failure_scenario(client, monkeypatch):
    class FailingAnalysisService:
        def __init__(self, db):
            self.db = db

        async def analyze(self, **kwargs):
            raise RuntimeError("analysis failed")

    monkeypatch.setattr("app.routers.analysis.MarketAnalysisService", FailingAnalysisService)
    resp = client.post("/api/v1/analysis/market", json={})
    assert resp.status_code == 500


def test_analysis_list_success(client, monkeypatch):
    class FakeAnalysisService:
        def __init__(self, db):
            self.db = db

        async def list_analyses(self, **kwargs):
            item = SimpleNamespace(
                id=UUID1,
                sector="retail",
                district="Almaly",
                summary="ok",
                score=0.8,
                insights={"trend": "up"},
                created_at=NOW,
            )
            return [item], 1

    monkeypatch.setattr("app.routers.analysis.MarketAnalysisService", FakeAnalysisService)
    resp = client.get("/api/v1/analysis")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


def test_analysis_list_validation_error(client):
    resp = client.get("/api/v1/analysis?size=101")
    assert resp.status_code == 422


def test_analysis_list_failure_scenario(client, monkeypatch):
    class FailingAnalysisService:
        def __init__(self, db):
            self.db = db

        async def list_analyses(self, **kwargs):
            raise RuntimeError("list analyses failed")

    monkeypatch.setattr("app.routers.analysis.MarketAnalysisService", FailingAnalysisService)
    resp = client.get("/api/v1/analysis")
    assert resp.status_code == 500


def test_opportunities_score_success(client, monkeypatch):
    class FakeOpportunityService:
        def __init__(self, db):
            self.db = db

        async def score_opportunities(self, **kwargs):
            return [
                SimpleNamespace(
                    id=UUID1,
                    sector="retail",
                    district="Almaly",
                    title="Retail expansion",
                    description="desc",
                    score=0.9,
                    score_breakdown={"gap": 0.9},
                    created_at=NOW,
                )
            ]

    monkeypatch.setattr(
        "app.routers.opportunities.OpportunityScoringService",
        FakeOpportunityService,
    )
    resp = client.post(
        "/api/v1/opportunities/score",
        json={"sector": "retail", "limit": 5},
        headers=_auth_headers(),
    )
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


def test_opportunities_score_validation_error(client):
    resp = client.post(
        "/api/v1/opportunities/score",
        json={"limit": 101},
        headers=_auth_headers(),
    )
    assert resp.status_code == 422


def test_opportunities_score_auth_failure(client):
    resp = client.post("/api/v1/opportunities/score", json={"limit": 5})
    assert resp.status_code == 401


def test_opportunities_score_failure_scenario(client, monkeypatch):
    class FailingOpportunityService:
        def __init__(self, db):
            self.db = db

        async def score_opportunities(self, **kwargs):
            raise RuntimeError("score failed")

    monkeypatch.setattr(
        "app.routers.opportunities.OpportunityScoringService",
        FailingOpportunityService,
    )
    resp = client.post(
        "/api/v1/opportunities/score",
        json={"limit": 5},
        headers=_auth_headers(),
    )
    assert resp.status_code == 500


def test_opportunities_list_success(client, monkeypatch):
    class FakeOpportunityService:
        def __init__(self, db):
            self.db = db

        async def list_opportunities(self, **kwargs):
            item = SimpleNamespace(
                id=UUID1,
                sector="retail",
                district="Almaly",
                title="Retail expansion",
                description="desc",
                score=0.9,
                score_breakdown={"gap": 0.9},
                created_at=NOW,
            )
            return [item], 1

    monkeypatch.setattr(
        "app.routers.opportunities.OpportunityScoringService",
        FakeOpportunityService,
    )
    resp = client.get("/api/v1/opportunities")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


def test_opportunities_list_validation_error(client):
    resp = client.get("/api/v1/opportunities?page=0")
    assert resp.status_code == 422


def test_opportunities_list_failure_scenario(client, monkeypatch):
    class FailingOpportunityService:
        def __init__(self, db):
            self.db = db

        async def list_opportunities(self, **kwargs):
            raise RuntimeError("list opportunities failed")

    monkeypatch.setattr(
        "app.routers.opportunities.OpportunityScoringService",
        FailingOpportunityService,
    )
    resp = client.get("/api/v1/opportunities")
    assert resp.status_code == 500


def test_recommendations_success(client, monkeypatch):
    class FakeRecommendationService:
        def __init__(self, db):
            self.db = db

        async def get_recommendations(self, **kwargs):
            return [
                SimpleNamespace(
                    id=UUID2,
                    sector="retail",
                    district="Almaly",
                    title="Open convenience mini-market",
                    rationale="strong local demand",
                    score=0.88,
                    rank=1,
                    created_at=NOW,
                )
            ]

    monkeypatch.setattr(
        "app.routers.recommendations.RecommendationService",
        FakeRecommendationService,
    )
    resp = client.get("/api/v1/recommendations?limit=5", headers=_auth_headers())
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


def test_recommendations_validation_error(client):
    resp = client.get("/api/v1/recommendations?limit=0", headers=_auth_headers())
    assert resp.status_code == 422


def test_recommendations_auth_failure(client):
    resp = client.get("/api/v1/recommendations?limit=5")
    assert resp.status_code == 401


def test_recommendations_failure_scenario(client, monkeypatch):
    class FailingRecommendationService:
        def __init__(self, db):
            self.db = db

        async def get_recommendations(self, **kwargs):
            raise RuntimeError("recommendation failed")

    monkeypatch.setattr(
        "app.routers.recommendations.RecommendationService",
        FailingRecommendationService,
    )
    resp = client.get("/api/v1/recommendations?limit=5", headers=_auth_headers())
    assert resp.status_code == 500
