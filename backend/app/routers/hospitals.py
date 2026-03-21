from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.hospital import Hospital
from app.schemas.hospital import HospitalResponse

router = APIRouter(prefix="/hospitals", tags=["hospitals"])


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
