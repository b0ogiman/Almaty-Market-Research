"""Metrics for scoring models."""

from typing import Any, Optional

import numpy as np
from app.logging_config import get_logger

logger = get_logger("evaluation.metrics")


class ScoringMetrics:
    """Metrics for evaluating scoring/ranking models."""

    @staticmethod
    def mae(predictions: list[float], actuals: list[float]) -> float:
        """Mean absolute error."""
        if not predictions or len(predictions) != len(actuals):
            return float("nan")
        return float(np.mean(np.abs(np.array(predictions) - np.array(actuals))))

    @staticmethod
    def rmse(predictions: list[float], actuals: list[float]) -> float:
        """Root mean squared error."""
        if not predictions or len(predictions) != len(actuals):
            return float("nan")
        return float(np.sqrt(np.mean((np.array(predictions) - np.array(actuals)) ** 2)))

    @staticmethod
    def rank_correlation(predicted_ranks: list[int], actual_ranks: list[int]) -> float:
        """Spearman rank correlation. Returns value in [-1, 1]."""
        if len(predicted_ranks) != len(actual_ranks) or len(predicted_ranks) < 2:
            return float("nan")
        try:
            from scipy.stats import spearmanr
            r, _ = spearmanr(predicted_ranks, actual_ranks)
            return float(r) if not np.isnan(r) else 0.0
        except ImportError:
            return 0.0

    @staticmethod
    def ndcg_at_k(
        relevance: list[float],
        k: int = 10,
    ) -> float:
        """Normalized DCG at k. Relevance = relevance scores in rank order."""
        if not relevance or k < 1:
            return 0.0
        dcg = sum(
            (2 ** rel - 1) / np.log2(i + 2)
            for i, rel in enumerate(relevance[:k])
        )
        ideal = sorted(relevance, reverse=True)[:k]
        idcg = sum(
            (2 ** rel - 1) / np.log2(i + 2)
            for i, rel in enumerate(ideal)
        )
        if idcg <= 0:
            return 0.0
        return dcg / idcg

    @staticmethod
    def precision_at_k(relevant: set[Any], retrieved: list[Any], k: int = 10) -> float:
        """Precision at k."""
        if k < 1 or not retrieved:
            return 0.0
        top_k = retrieved[:k]
        hits = sum(1 for x in top_k if x in relevant)
        return hits / len(top_k)

    @staticmethod
    def recall_at_k(relevant: set[Any], retrieved: list[Any], k: int = 10) -> float:
        """Recall at k."""
        if not relevant:
            return 0.0
        top_k = set(retrieved[:k])
        hits = len(relevant & top_k)
        return hits / len(relevant)
