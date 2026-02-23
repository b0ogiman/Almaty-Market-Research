"""Logging model performance for evaluation."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from app.logging_config import get_logger

logger = get_logger("evaluation.logging")


class ModelPerformanceLogger:
    """Log model performance metrics to file and structured logs."""

    def __init__(
        self,
        log_dir: str | Path = "logs/evaluation",
        prefix: str = "model",
    ) -> None:
        self.log_dir = Path(log_dir)
        self.prefix = prefix
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        model_name: str,
        metrics: dict[str, float],
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log metrics for a model run."""
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "model": model_name,
            "metrics": metrics,
            "metadata": metadata or {},
        }
        logger.info(
            "Model performance: %s | %s",
            model_name,
            json.dumps(metrics),
            extra={"model": model_name, "metrics": metrics},
        )
        fname = self.log_dir / f"{self.prefix}_{model_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(fname, "w") as f:
                json.dump(record, f, indent=2)
        except OSError as e:
            logger.warning("Could not write performance log: %s", str(e))
