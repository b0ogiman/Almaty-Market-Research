"""Tests for data collection module."""

import pytest
from app.collectors.validation import validate_listing, validate_batch, clean_string, clean_float
from app.collectors.dedup import fingerprint, detect_duplicates
from app.collectors.avito_mock import AvitoMockCollector


class TestValidation:
    def test_validate_listing_valid(self):
        item = {"external_id": "e1", "name": "Test", "category": "retail", "source": "test"}
        cleaned, err = validate_listing(item)
        assert err is None
        assert cleaned["external_id"] == "e1"
        assert cleaned["name"] == "Test"

    def test_validate_listing_missing_external_id(self):
        item = {"name": "Test", "category": "retail"}
        cleaned, err = validate_listing(item)
        assert cleaned is None
        assert "external_id" in err

    def test_validate_listing_missing_name(self):
        item = {"external_id": "e1", "category": "retail"}
        cleaned, err = validate_listing(item)
        assert cleaned is None
        assert "name" in err

    def test_validate_batch(self):
        items = [
            {"external_id": "e1", "name": "A", "category": "x"},
            {"external_id": "e2", "name": "", "category": "x"},
        ]
        valid, errors = validate_batch(items)
        assert len(valid) == 1
        assert len(errors) == 1

    def test_clean_string(self):
        assert clean_string("  a  b  ") == "a b"
        assert clean_string(None) is None

    def test_clean_float(self):
        assert clean_float("3.5") == 3.5
        assert clean_float("x") is None
        assert clean_float(10, lo=0, hi=5) == 5


class TestDedup:
    def test_fingerprint(self):
        a = {"name": "X", "category": "c", "district": "d", "address": "addr"}
        b = {"name": "X", "category": "c", "district": "d", "address": "addr"}
        assert fingerprint(a) == fingerprint(b)

    def test_detect_duplicates(self):
        items = [
            {"external_id": "e1", "name": "A", "category": "c", "district": "d"},
            {"external_id": "e1", "name": "A", "category": "c", "district": "d"},
        ]
        unique, dups = detect_duplicates(items)
        assert len(unique) == 1
        assert len(dups) == 1


class TestAvitoMock:
    @pytest.mark.asyncio
    async def test_collect(self):
        collector = AvitoMockCollector()
        result = await collector.collect(limit=5)
        assert result.source == "avito_mock"
        assert result.collected == 5
        assert len(result.raw_items) == 5
        assert all("external_id" in x for x in result.raw_items)
