"""Time-based trend detection using simple moving average."""

from typing import Any, Optional

from app.logging_config import get_logger

logger = get_logger("analytics.trends")


class TrendDetector:
    """
    Simple trend detection via moving average.
    No Prophet (heavy) - uses SMA for lightweight analysis.
    """

    def __init__(self, window: int = 3) -> None:
        self.window = window

    @staticmethod
    def _sma(values: list[float], window: int) -> list[Optional[float]]:
        """Simple moving average."""
        if not values or window < 1:
            return []
        result = []
        for i in range(len(values)):
            if i < window - 1:
                result.append(None)
            else:
                result.append(sum(values[i - window + 1 : i + 1]) / window)
        return result

    def detect_trend(
        self,
        time_series: list[tuple[Any, float]],
        window: int | None = None,
    ) -> dict[str, Any]:
        """
        Detect trend from (timestamp, value) pairs.
        Returns direction (up/down/stable), slope, and smoothed values.
        """
        w = window or self.window
        if len(time_series) < w:
            return {"direction": "insufficient_data", "slope": 0.0, "smoothed": []}
        values = [v for _, v in time_series]
        smoothed = self._sma(values, w)
        valid = [s for s in smoothed if s is not None]
        if len(valid) < 2:
            return {"direction": "stable", "slope": 0.0, "smoothed": smoothed}
        slope = (valid[-1] - valid[0]) / (len(valid) - 1)
        threshold = 0.05 * (max(valid) - min(valid) or 1)
        if slope > threshold:
            direction = "up"
        elif slope < -threshold:
            direction = "down"
        else:
            direction = "stable"
        return {
            "direction": direction,
            "slope": slope,
            "smoothed": smoothed,
        }

    def trend_from_aggregates(
        self,
        aggregates: list[dict[str, Any]],
        value_key: str = "count",
        date_key: str = "date",
    ) -> dict[str, Any]:
        """Detect trend from pre-aggregated data."""
        series = [(a.get(date_key), float(a.get(value_key, 0))) for a in aggregates]
        return self.detect_trend(series)
