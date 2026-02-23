"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_listings():
    """Sample listing dicts for tests."""
    return [
        {
            "external_id": "ext_1",
            "source": "avito_mock",
            "name": "Cafe Central",
            "category": "restaurant",
            "district": "Almaly",
            "rating": 4.5,
            "review_count": 120,
            "description": "Great food and service.",
        },
        {
            "external_id": "ext_2",
            "source": "avito_mock",
            "name": "Shop Plus",
            "category": "retail",
            "district": "Almaly",
            "rating": 4.0,
            "review_count": 50,
        },
        {
            "external_id": "ext_3",
            "source": "avito_mock",
            "name": "Gym Fit",
            "category": "fitness",
            "district": "Auezov",
            "rating": 4.8,
            "review_count": 200,
        },
    ]


@pytest.fixture
def sample_time_series():
    """Sample (timestamp, value) for trend tests."""
    return [
        ("2024-01", 10),
        ("2024-02", 12),
        ("2024-03", 11),
        ("2024-04", 15),
        ("2024-05", 18),
    ]
