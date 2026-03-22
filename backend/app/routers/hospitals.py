from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.hospital import Hospital
from app.schemas.hospital import HospitalResponse, HospitalWithDistanceResponse
from app.services.geo import find_hospitals_near_zip

router = APIRouter(prefix="/hospitals", tags=["hospitals"])


@router.get("/nearby", response_model=dict)
def nearby_hospitals(
    zip_code: str = Query(..., min_length=5, max_length=5),
    radius: int | None = Query(None),
    procedure_id: int | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    if not zip_code.isdigit():
        raise HTTPException(status_code=400, detail="ZIP code must be 5 digits")
    try:
        results, total = find_hospitals_near_zip(
            db, zip_code, radius, procedure_id, limit, offset
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    items = []
    for hospital, distance in results:
        resp = HospitalWithDistanceResponse.model_validate(hospital)
        resp.distance_miles = distance
        items.append(resp)

    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("", response_model=dict)
def list_hospitals(
    q: str = Query("", description="Search by name"),
    state: str | None = Query(None, max_length=2),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Hospital)

    if q:
        pattern = f"%{q}%"
        query = query.filter(
            or_(Hospital.name.ilike(pattern), Hospital.city.ilike(pattern))
        )
    if state:
        query = query.filter(Hospital.state == state.upper())

    total = query.count()
    items = query.order_by(Hospital.name).offset(offset).limit(limit).all()
    return {
        "items": [HospitalResponse.model_validate(h) for h in items],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{hospital_id}", response_model=HospitalResponse)
def get_hospital(hospital_id: int, db: Session = Depends(get_db)):
    hospital = db.get(Hospital, hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return HospitalResponse.model_validate(hospital)
