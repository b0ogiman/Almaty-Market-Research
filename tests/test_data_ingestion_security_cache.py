"""Tests for ingestion cache invalidation consistency."""

from unittest.mock import AsyncMock

import pytest

from app.schemas.data import DataIngestRequest
from app.services.data_ingestion import DataIngestionService


class _DummySession:
    def __init__(self) -> None:
        self._records = []

    def add_all(self, records):
        self._records.extend(records)

    async def flush(self):
        return None


@pytest.mark.asyncio
async def test_ingest_invalidates_all_related_cache_prefixes(monkeypatch):
    mocked_delete = AsyncMock(return_value=1)
    monkeypatch.setattr("app.services.data_ingestion.cache_delete_prefix", mocked_delete)

    db = _DummySession()
    service = DataIngestionService(db)  # type: ignore[arg-type]
    request = DataIngestRequest(
        items=[
            {
                "sector": "retail",
                "district": "Almaly",
                "metric_name": "demand_index",
                "metric_value": 0.75,
                "source": "manual_test",
            }
        ]
    )

    ingested, failed, _ = await service.ingest(request)
    assert ingested == 1
    assert failed == 0

    called_prefixes = {call.args[0] for call in mocked_delete.await_args_list}
    assert called_prefixes == {"analysis:", "opportunities:", "recommendations:"}
