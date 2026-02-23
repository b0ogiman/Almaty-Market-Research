"""District mapping for Almaty."""

import re
from typing import Optional

from app.logging_config import get_logger

logger = get_logger("enrichment.district")

# Canonical Almaty district names and common variants
DISTRICT_MAP: dict[str, str] = {
    "alatau": "Alatau",
    "алматау": "Alatau",
    "almaly": "Almaly",
    "алмалы": "Almaly",
    "auezov": "Auezov",
    "ауэзов": "Auezov",
    "bostandyq": "Bostandyq",
    "бостандык": "Bostandyq",
    "medeu": "Medeu",
    "медеу": "Medeu",
    "nauryzbay": "Nauryzbay",
    "наурызбай": "Nauryzbay",
    "turksib": "Turksib",
    "турксиб": "Turksib",
    "zhetysu": "Zhetysu",
    "жетісу": "Zhetysu",
    "jetysu": "Zhetysu",
}


class DistrictMapper:
    """Maps free-text district names to canonical Almaty districts."""

    def __init__(self, mapping: dict[str, str] | None = None) -> None:
        self._map = mapping or DISTRICT_MAP
        self._normalized = {k.lower().strip(): v for k, v in self._map.items()}

    def map_district(self, raw: str | None) -> Optional[str]:
        """
        Map raw district string to canonical name.
        Handles partial matches and address parsing.
        """
        if not raw or not isinstance(raw, str):
            return None
        s = raw.strip()
        if not s:
            return None
        lower = s.lower()
        # Direct lookup
        if lower in self._normalized:
            return self._normalized[lower]
        # Partial match
        for key, canonical in self._normalized.items():
            if key in lower or lower in key:
                return canonical
        # Extract from address-like string (e.g. "Almaty, Almaly district")
        match = re.search(
            r"(alatau|almaly|auezov|bostandyq|medeu|nauryzbay|turksib|zhetysu|jetysu)",
            lower,
            re.IGNORECASE,
        )
        if match:
            return self._normalized.get(match.group(1).lower())
        return None

    def enrich(self, item: dict) -> dict:
        """Add district_mapped to item. Mutates in place, returns item."""
        raw = item.get("district") or item.get("address")
        mapped = self.map_district(raw)
        if mapped:
            item["district_mapped"] = mapped
        return item
