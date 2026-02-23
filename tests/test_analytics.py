"""Tests for analytics module."""

import pytest
from app.analytics.demand import DemandScorer
from app.analytics.competition import CompetitionIndex
from app.analytics.market_gap import MarketGapScorer
from app.analytics.trends import TrendDetector
from app.analytics.clustering import BusinessClustering


class TestDemandScorer:
    def test_score_basic(self):
        scorer = DemandScorer()
        s = scorer.score(avg_rating=4.0, total_reviews=100)
        assert 0 <= s <= 1

    def test_score_from_listings(self, sample_listings):
        scorer = DemandScorer()
        s = scorer.score_from_listings(sample_listings)
        assert 0 <= s <= 1


class TestCompetitionIndex:
    def test_district_index(self, sample_listings):
        ci = CompetitionIndex(sample_listings)
        assert 0 <= ci.district_index("Almaly") <= 1

    def test_combined_index(self, sample_listings):
        ci = CompetitionIndex(sample_listings)
        assert 0 <= ci.combined_index("Almaly", "retail") <= 1


class TestMarketGapScorer:
    def test_score(self):
        scorer = MarketGapScorer()
        s = scorer.score(demand_score=0.8, competition_index=0.2)
        assert 0 <= s <= 1
        assert s > 0.5

    def test_score_from_listings(self, sample_listings):
        scorer = MarketGapScorer()
        s = scorer.score_from_listings(sample_listings, "Almaly", "retail")
        assert 0 <= s <= 1


class TestTrendDetector:
    def test_detect_trend_up(self, sample_time_series):
        td = TrendDetector(window=2)
        r = td.detect_trend(sample_time_series)
        assert r["direction"] in ("up", "down", "stable")
        assert "slope" in r

    def test_insufficient_data(self):
        td = TrendDetector(window=5)
        r = td.detect_trend([("a", 1)])
        assert r["direction"] == "insufficient_data"


class TestClustering:
    def test_fit(self, sample_listings):
        cl = BusinessClustering(n_clusters=2)
        labels = cl.fit(sample_listings)
        assert len(labels) == len(sample_listings)
