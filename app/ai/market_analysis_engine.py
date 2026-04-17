"""Market analysis AI engine - MVP stub."""

from typing import Any, Optional

from app.analytics.clustering import BusinessClustering
from app.analytics.demand import DemandScorer
from app.analytics.market_gap import MarketGapScorer
from app.analytics.trends import TrendDetector
from app.logging_config import get_logger

logger = get_logger("ai.market_analysis")


class MarketAnalysisEngine:
    """
    Market analysis engine backed by analytics module.

    Consumes enriched business listing records and produces a high-level
    summary, numeric score, and structured insights.
    """

    def __init__(self) -> None:
        self._demand = DemandScorer()
        self._gap = MarketGapScorer()
        self._trends = TrendDetector()

    async def analyze(
        self,
        sector: Optional[str] = None,
        district: Optional[str] = None,
        listings: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        """
        Analyze market conditions for given sector/district using real listings.

        - Demand score from ratings, reviews, sentiment, listing density.
        - Competition/gap from MarketGapScorer.
        - Clustering to group similar businesses.
        - Simple time-based trend on listing counts.
        """
        listings = listings or []
        logger.info(
            "Running market analysis: sector=%s, district=%s, listings=%d",
            sector,
            district,
            len(listings),
        )

        SECTOR_RU = {
            "food_service": "общепит", "retail": "ритейл", "services": "услуги",
            "health": "здоровье и медицина", "beauty": "красота и уход",
            "fitness": "фитнес и спорт", "education": "образование",
            "vehicles": "авто", "electronics": "электроника",
            "clothing": "одежда и обувь", "real_estate": "недвижимость",
            "other": "другое", "all": "все секторы",
        }
        DISTRICT_RU = {
            "Bostandyq": "Бостандык", "Almaly": "Алмалы", "Medeu": "Медеу",
            "Auezov": "Ауэзов", "Alatau": "Алатау", "Turksib": "Түрксіб",
            "Zhetysu": "Жетісу", "Nauryzbay": "Наурызбай", "all": "все районы",
        }
        sector_label = SECTOR_RU.get(sector or "all", sector or "все секторы")
        district_label = DISTRICT_RU.get(district or "all", district or "все районы")

        if not listings:
            summary = (
                f"По сектору «{sector_label}» в районе «{district_label}» "
                f"данных пока недостаточно для полноценного анализа."
            )
            return {
                "summary": summary,
                "score": 0.5,
                "insights": {
                    "demand_score": 0.5,
                    "competition_index": 0.0,
                    "gap_score": 0.5,
                    "trend": {"direction": "insufficient_data", "slope": 0.0},
                    "clusters": {},
                },
                "raw_output": {"sector": sector, "district": district, "listing_count": 0},
            }

        demand_score = self._demand.score_from_listings(listings)

        # Use district/category from filters when available, otherwise infer from listings.
        sample = listings[0]
        target_district = district or sample.get("district_mapped") or sample.get("district") or "unknown"
        target_category = (
            sample.get("category_normalized") or sample.get("category") or "unknown"
        )
        gap_score = self._gap.score_from_listings(
            listings,
            district=target_district,
            category=target_category,
        )

        # Clustering for basic segment insight.
        clustering = BusinessClustering(n_clusters=3)
        labels = clustering.fit(listings)
        clusters = clustering.get_cluster_summary(listings, labels) if len(labels) else {}

        # Very lightweight trend: count listings over created_at dates if present.
        aggregates: list[dict[str, Any]] = []
        by_date: dict[str, int] = {}
        for item in listings:
            ts = item.get("created_at")
            if not ts:
                continue
            key = str(getattr(ts, "date", lambda: ts)())
            by_date[key] = by_date.get(key, 0) + 1
        for date, count in sorted(by_date.items()):
            aggregates.append({"date": date, "count": count})
        trend = self._trends.trend_from_aggregates(aggregates) if aggregates else {
            "direction": "insufficient_data",
            "slope": 0.0,
            "smoothed": [],
        }

        # Combine into overall score (simple blend of demand and gap).
        score = max(0.0, min(1.0, (demand_score + gap_score) / 2.0))

        competition_level = "высокая" if gap_score < 0.2 else "средняя" if gap_score < 0.5 else "низкая"
        demand_level = "высокий" if demand_score > 0.65 else "средний" if demand_score > 0.4 else "низкий"
        summary = (
            f"Сектор «{sector_label}», район «{district_label}». "
            f"Проанализировано {len(listings)} заведений. "
            f"Спрос — {demand_level}, конкуренция — {competition_level}."
        )
        insights: dict[str, Any] = {
            "demand_score": demand_score,
            "gap_score": gap_score,
            "trend": {
                "direction": trend.get("direction"),
                "slope": trend.get("slope"),
            },
            "clusters": clusters,
            "target_district": target_district,
            "target_category": target_category,
        }

        return {
            "summary": summary,
            "score": score,
            "insights": insights,
            "raw_output": {
                "sector": sector,
                "district": district,
                "listing_count": len(listings),
                "trend": trend,
            },
        }
