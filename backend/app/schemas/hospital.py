from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class HospitalBase(BaseModel):
    name: str
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None


class HospitalResponse(HospitalBase):
    id: int
    ein: Optional[str] = None
    npi: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    last_updated: Optional[date] = None

    # Contact
    phone: Optional[str] = None
    website: Optional[str] = None
    booking_url: Optional[str] = None

    # Facility classification
    facility_type: Optional[str] = None

    # Mammography-specific
    has_3d_mammography: Optional[bool] = None
    acr_accredited: Optional[bool] = None
    accepts_new_patients: Optional[bool] = None
    availability_note: Optional[str] = None
    accepted_insurances: Optional[List[str]] = None

    model_config = {"from_attributes": True}


class HospitalWithDistanceResponse(HospitalResponse):
    distance_miles: float
