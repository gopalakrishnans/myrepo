from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.procedure import Procedure
from app.schemas.price import PriceCompareResponse, PriceResponse
from app.services.comparison import compare_prices, get_prices

router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("", response_model=dict)
def list_prices(
    procedure_id: int = Query(..., description="Required procedure ID"),
    hospital_id: int | None = Query(None),
    payer_id: int | None = Query(None),
    state: str | None = Query(None, max_length=2),
    sort_by: str = Query("price", pattern="^(price|hospital)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    items, total = get_prices(db, procedure_id, hospital_id, payer_id, state, sort_by, limit, offset)
    return {
        "items": [
            PriceResponse(
                id=p.id,
                hospital_name=p.hospital.name,
                hospital_city=p.hospital.city,
                hospital_state=p.hospital.state,
                procedure_name=p.procedure.plain_language_name,
                billing_code=p.procedure.billing_code,
                payer_name=p.payer.name if p.payer else None,
                plan_name=p.payer.plan_name if p.payer else None,
                gross_charge=float(p.gross_charge) if p.gross_charge else None,
                discounted_cash_price=float(p.discounted_cash_price) if p.discounted_cash_price else None,
                negotiated_rate=float(p.negotiated_rate) if p.negotiated_rate else None,
                min_negotiated_rate=float(p.min_negotiated_rate) if p.min_negotiated_rate else None,
                max_negotiated_rate=float(p.max_negotiated_rate) if p.max_negotiated_rate else None,
            )
            for p in items
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/compare", response_model=PriceCompareResponse)
def compare(
    procedure_id: int = Query(...),
    hospital_ids: str = Query(..., description="Comma-separated hospital IDs"),
    db: Session = Depends(get_db),
):
    try:
        ids = [int(x.strip()) for x in hospital_ids.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="hospital_ids must be comma-separated integers")
    if len(ids) < 2 or len(ids) > 4:
        raise HTTPException(status_code=400, detail="Provide 2-4 hospital IDs")

    procedure = db.get(Procedure, procedure_id)
    if not procedure:
        raise HTTPException(status_code=404, detail="Procedure not found")

    hospitals = compare_prices(db, procedure_id, ids)
    return PriceCompareResponse(
        procedure_name=procedure.plain_language_name,
        billing_code=procedure.billing_code,
        hospitals=hospitals,
    )
