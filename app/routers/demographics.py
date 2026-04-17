"""Demographics API — static district demographic data."""

from typing import Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.data.demographics import get_all, get_by_district

router = APIRouter(prefix="/demographics", tags=["demographics"])


class DistrictDemographics(BaseModel):
    district: str
    population: int
    area_km2: float
    avg_income_usd: int
    density_per_km2: float
    commercial_zones: list[str]
    notes: str


class DemographicsListResponse(BaseModel):
    success: bool
    items: list[DistrictDemographics]


@router.get("", response_model=DemographicsListResponse)
async def list_demographics() -> DemographicsListResponse:
    """Return demographic data for all Almaty districts."""
    return DemographicsListResponse(success=True, items=get_all())


@router.get("/{district}", response_model=DistrictDemographics)
async def get_district_demographics(district: str) -> DistrictDemographics:
    """Return demographic data for a specific district."""
    data = get_by_district(district)
    if not data:
        raise HTTPException(status_code=404, detail=f"District '{district}' not found")
    return DistrictDemographics(district=district, **data)
