"""Basic KMeans clustering for market segments."""

from typing import Any, Optional

import numpy as np
from app.logging_config import get_logger

logger = get_logger("analytics.clustering")


class BusinessClustering:
    """
    KMeans clustering on business features.
    Lightweight: uses sklearn if available, else simple implementation.
    """

    def __init__(self, n_clusters: int = 5, random_state: int = 42) -> None:
        self.n_clusters = n_clusters
        self.random_state = random_state
        self._model: Any = None
        self._labels: Optional[np.ndarray] = None

    def _extract_features(self, listings: list[dict[str, Any]]) -> np.ndarray:
        """Extract numeric features for clustering."""
        rows = []
        for item in listings:
            lat = item.get("latitude") or 43.25
            lon = item.get("longitude") or 76.95
            rating = item.get("rating") or 0
            reviews = np.log1p(item.get("review_count") or 0)
            # Map sentiment from [-1, 1] to [0, 1], defaulting to 0.5 when missing
            sentiment = ((item.get("sentiment_score") or 0) + 1) / 2
            rows.append([lat, lon, rating, reviews, sentiment])
        return np.array(rows, dtype=np.float64)

    def fit(self, listings: list[dict[str, Any]]) -> np.ndarray:
        """Fit KMeans and return cluster labels."""
        if not listings:
            return np.array([])
        X = self._extract_features(listings)
        try:
            from sklearn.cluster import KMeans
            km = KMeans(
                n_clusters=min(self.n_clusters, len(listings)),
                random_state=self.random_state,
                n_init=10,
            )
            self._labels = km.fit_predict(X)
            self._model = km
            return self._labels
        except ImportError:
            logger.warning("sklearn not available. Using random cluster assignment.")
            n = len(listings)
            k = min(self.n_clusters, n)
            self._labels = np.random.randint(0, k, size=n)
            return self._labels

    def predict(self, listings: list[dict[str, Any]]) -> np.ndarray:
        """Assign cluster labels to listings."""
        if self._model is None:
            return self.fit(listings)
        X = self._extract_features(listings)
        return self._model.predict(X)

    def get_cluster_summary(
        self,
        listings: list[dict[str, Any]],
        labels: np.ndarray,
    ) -> dict[int, dict[str, Any]]:
        """Summarize each cluster (count, avg rating, etc.)."""
        summary: dict[int, dict[str, Any]] = {}
        for i in range(self.n_clusters):
            mask = labels == i
            cluster_items = [listings[j] for j in range(len(listings)) if mask[j]]
            ratings = [x.get("rating") for x in cluster_items if x.get("rating")]
            summary[i] = {
                "count": len(cluster_items),
                "avg_rating": sum(ratings) / len(ratings) if ratings else None,
                "categories": list(set(x.get("category", "") for x in cluster_items))[:5],
            }
        return summary
