"""Tests for enrichment module."""

import pytest
from app.enrichment.district_mapping import DistrictMapper
from app.enrichment.category_normalizer import CategoryNormalizer
from app.enrichment.sentiment import score_sentiment, SentimentScorer


class TestDistrictMapper:
    def test_map_district_direct(self):
        mapper = DistrictMapper()
        assert mapper.map_district("Almaly") == "Almaly"
        assert mapper.map_district("almaly") == "Almaly"

    def test_map_district_partial(self):
        mapper = DistrictMapper()
        assert mapper.map_district("Almaty, Almaly district") == "Almaly"

    def test_map_district_unknown(self):
        mapper = DistrictMapper()
        assert mapper.map_district("Unknown") is None

    def test_enrich(self):
        mapper = DistrictMapper()
        item = {"district": "almaly"}
        mapper.enrich(item)
        assert item.get("district_mapped") == "Almaly"


class TestCategoryNormalizer:
    def test_normalize(self):
        norm = CategoryNormalizer()
        assert norm.normalize("restaurant") == "food_service"
        assert norm.normalize("cafe") == "food_service"

    def test_normalize_unknown(self):
        norm = CategoryNormalizer()
        assert norm.normalize("xyz_unknown") == "other"


class TestSentiment:
    def test_score_positive(self):
        assert score_sentiment("Great service!") >= 0

    def test_score_empty(self):
        assert score_sentiment("") == 0.0
        assert score_sentiment(None) == 0.0

    def test_sentiment_scorer_enrich(self):
        scorer = SentimentScorer()
        item = {"description": "Excellent quality"}
        scorer.enrich(item)
        assert "sentiment_score" in item
