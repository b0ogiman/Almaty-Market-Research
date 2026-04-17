"""Static demographic data for Almaty districts (stat.gov.kz, 2023)."""

from typing import Any

DISTRICT_DEMOGRAPHICS: dict[str, dict[str, Any]] = {
    "Alatau": {
        "population": 280_000,
        "area_km2": 710,
        "avg_income_usd": 480,
        "density_per_km2": 394,
        "commercial_zones": ["Alatau industrial", "Samal"],
        "notes": "Large industrial and residential district in south-west",
    },
    "Almaly": {
        "population": 185_000,
        "area_km2": 27,
        "avg_income_usd": 720,
        "density_per_km2": 6852,
        "commercial_zones": ["Arbat", "Green Bazaar", "Panfilov"],
        "notes": "Central district, highest foot traffic, premium rents",
    },
    "Auezov": {
        "population": 400_000,
        "area_km2": 78,
        "avg_income_usd": 390,
        "density_per_km2": 5128,
        "commercial_zones": ["Sairan", "Zhibek Zholy west"],
        "notes": "Most populous district, large working-class consumer base",
    },
    "Bostandyq": {
        "population": 300_000,
        "area_km2": 1050,
        "avg_income_usd": 650,
        "density_per_km2": 286,
        "commercial_zones": ["Dostyk", "Esentai", "Kok-Tobe"],
        "notes": "Affluent district, premium and upper-mid market segment",
    },
    "Medeu": {
        "population": 160_000,
        "area_km2": 270,
        "avg_income_usd": 850,
        "density_per_km2": 593,
        "commercial_zones": ["Dostyk Plaza area", "Nurly Tau"],
        "notes": "Highest income per capita, tourist and expat-friendly",
    },
    "Nauryzbay": {
        "population": 150_000,
        "area_km2": 560,
        "avg_income_usd": 350,
        "density_per_km2": 268,
        "commercial_zones": ["Aksay", "Shanyrak"],
        "notes": "Rapidly growing district, younger demographic",
    },
    "Turksib": {
        "population": 200_000,
        "area_km2": 165,
        "avg_income_usd": 370,
        "density_per_km2": 1212,
        "commercial_zones": ["Spartak market", "Seifullin north"],
        "notes": "North district, transport hub, wholesale trade",
    },
    "Zhetysu": {
        "population": 220_000,
        "area_km2": 56,
        "avg_income_usd": 420,
        "density_per_km2": 3929,
        "commercial_zones": ["Micro-districts 1-4", "Altyn Orta"],
        "notes": "Dense residential, growing retail demand",
    },
}


def get_all() -> list[dict[str, Any]]:
    return [
        {"district": district, **data}
        for district, data in DISTRICT_DEMOGRAPHICS.items()
    ]


def get_by_district(district: str) -> dict[str, Any] | None:
    return DISTRICT_DEMOGRAPHICS.get(district)
