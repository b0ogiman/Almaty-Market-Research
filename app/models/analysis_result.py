"""Market analysis result model."""

from typing import Optional

from sqlalchemy import Float, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class AnalysisResult(Base, UUIDMixin, TimestampMixin):
    """Cached market analysis results."""

    __tablename__ = "analysis_results"

    sector: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    district: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    insights: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    raw_output: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    def __repr__(self) -> str:
        return f"<AnalysisResult(id={self.id}, sector={self.sector}, district={self.district})>"
