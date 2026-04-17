"""Category normalization for business listings."""

import re
from typing import Optional

from app.logging_config import get_logger

logger = get_logger("enrichment.category")

# Normalize to standard categories (English + Russian 2GIS names)
CATEGORY_MAP: dict[str, str] = {
    # English
    "restaurant": "food_service", "cafe": "food_service", "bar": "food_service",
    "food": "food_service", "meal_delivery": "food_service", "meal_takeaway": "food_service",
    "food_delivery": "food_service", "canteen": "food_service", "bakery": "food_service",
    "fast_food": "food_service", "coffee": "food_service",
    "real_estate": "real_estate", "real_estate_agency": "real_estate",
    "car_dealer": "vehicles", "car_rental": "vehicles", "car_repair": "vehicles",
    "auto": "vehicles", "tire": "vehicles",
    "electronics_store": "electronics", "electronics": "electronics",
    "hardware_store": "retail", "clothing_store": "clothing", "shoe_store": "clothing",
    "supermarket": "retail", "grocery": "retail", "store": "retail", "retail": "retail",
    "pharmacy": "health", "hospital": "health", "dentist": "health",
    "doctor": "health", "clinic": "health", "medical": "health",
    "beauty_salon": "beauty", "hair_care": "beauty", "spa": "beauty",
    "nail": "beauty", "barbershop": "beauty",
    "gym": "fitness", "fitness": "fitness", "sport": "fitness", "pool": "fitness",
    "school": "education", "university": "education", "education": "education",
    "kindergarten": "education", "courses": "education",
    "establishment": "general", "point_of_interest": "general", "general": "general",
    "services": "services", "vehicles": "vehicles", "health": "health",
    "beauty": "beauty", "clothing": "clothing",
    # Russian 2GIS categories
    "рестораны": "food_service", "ресторан": "food_service",
    "кафе": "food_service", "кофейни": "food_service", "кофейня": "food_service",
    "бары": "food_service", "бар": "food_service",
    "столовые": "food_service", "столовая": "food_service",
    "фастфуд": "food_service", "быстрое питание": "food_service",
    "доставка еды": "food_service", "пиццерии": "food_service",
    "суши": "food_service", "шашлычные": "food_service",
    "кондитерские": "food_service", "булочные": "food_service",
    "продукты": "retail", "супермаркеты": "retail", "супермаркет": "retail",
    "магазин": "retail", "магазины": "retail", "торговый центр": "retail",
    "гипермаркет": "retail", "рынок": "retail", "базар": "retail",
    "одежда": "clothing", "обувь": "clothing", "одежда и обувь": "clothing",
    "бутик": "clothing",
    "аптеки": "health", "аптека": "health",
    "больница": "health", "клиника": "health", "поликлиника": "health",
    "стоматология": "health", "стоматологии": "health",
    "медицинский центр": "health", "медицина": "health",
    "салон красоты": "beauty", "салоны красоты": "beauty",
    "парикмахерская": "beauty", "парикмахерские": "beauty",
    "маникюр": "beauty", "барбершоп": "beauty", "барбершопы": "beauty",
    "спа": "beauty", "косметология": "beauty",
    "фитнес-клуб": "fitness", "фитнес": "fitness", "спортзал": "fitness",
    "тренажерный зал": "fitness", "бассейн": "fitness", "йога": "fitness",
    "спортивные секции": "fitness",
    "школа": "education", "школы": "education",
    "детский сад": "education", "детские сады": "education",
    "университет": "education", "колледж": "education",
    "курсы": "education", "учебный центр": "education",
    "автосервис": "vehicles", "автомойка": "vehicles",
    "автозапчасти": "vehicles", "шиномонтаж": "vehicles",
    "автосалон": "vehicles", "авторемонт": "vehicles",
    "электроника": "electronics", "бытовая техника": "electronics",
    "телефоны": "electronics", "компьютеры": "electronics",
    "недвижимость": "real_estate", "агентство недвижимости": "real_estate",
    "банки": "services", "банк": "services",
    "нотариус": "services", "юридические услуги": "services",
    "страхование": "services", "бухгалтерия": "services",
    "кино": "general", "театр": "general", "развлечения": "general",
    "гостиница": "general", "отель": "general",
    "каршеринг": "vehicles",
    "ремонт": "services",
    "химчистка": "services", "прачечная": "services",
    "ветеринарная клиника": "health", "ветеринар": "health",
}


class CategoryNormalizer:
    """Normalizes category strings to canonical taxonomy."""

    def __init__(self, mapping: dict[str, str] | None = None) -> None:
        self._map = mapping or CATEGORY_MAP
        self._normalized = {k.lower().replace(" ", "_"): v for k, v in self._map.items()}

    def normalize(self, raw: str | None) -> Optional[str]:
        """Normalize category to canonical value."""
        if not raw or not isinstance(raw, str):
            return None
        key = re.sub(r"\s+", "_", raw.lower().strip())
        if not key:
            return None
        if key in self._normalized:
            return self._normalized[key]
        for map_key, canonical in self._normalized.items():
            if map_key in key or key in map_key:
                return canonical
        return "other"

    def enrich(self, item: dict) -> dict:
        """Add category_normalized to item. Mutates in place."""
        raw = item.get("category")
        norm = self.normalize(raw)
        if norm:
            item["category_normalized"] = norm
        return item
