from datetime import date
from typing import Optional

from pydantic import BaseModel


class HospitalBase(BaseModel):
    name: str
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None


class HospitalResponse(HospitalBase):
    id: int
    ein: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    last_updated: Optional[date] = None

    model_config = {"from_attributes": True}


class HospitalWithDistanceResponse(HospitalResponse):
    distance_miles: float
