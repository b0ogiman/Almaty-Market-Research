"""Tests for evaluation module."""

import tempfile
from pathlib import Path

import pytest
from app.evaluation.metrics import ScoringMetrics
from app.evaluation.logging import ModelPerformanceLogger


class TestScoringMetrics:
    def test_mae(self):
        pred = [1.0, 2.0, 3.0]
        actual = [1.1, 2.1, 2.9]
        m = ScoringMetrics.mae(pred, actual)
        assert m < 0.2

    def test_rmse(self):
        pred = [1.0, 2.0]
        actual = [1.0, 2.0]
        assert ScoringMetrics.rmse(pred, actual) == 0.0

    def test_precision_at_k(self):
        relevant = {1, 2, 3}
        retrieved = [1, 4, 2, 5, 3]
        p = ScoringMetrics.precision_at_k(relevant, retrieved, k=3)
        assert p == 2 / 3

    def test_recall_at_k(self):
        relevant = {1, 2, 3}
        retrieved = [1, 4, 2]
        r = ScoringMetrics.recall_at_k(relevant, retrieved, k=5)
        assert r == 2 / 3


class TestModelPerformanceLogger:
    def test_log(self):
        with tempfile.TemporaryDirectory() as d:
            log = ModelPerformanceLogger(log_dir=d)
            log.log("test_model", {"mae": 0.1, "rmse": 0.2})
            files = list(Path(d).glob("*.json"))
            assert len(files) >= 1
