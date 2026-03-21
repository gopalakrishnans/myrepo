from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.price import ProcedureStats
from app.services.statistics import get_procedure_stats

router = APIRouter(prefix="/stats", tags=["statistics"])


@router.get("/procedure/{procedure_id}", response_model=ProcedureStats)
def procedure_stats(
    procedure_id: int,
    state: str | None = Query(None, max_length=2),
    db: Session = Depends(get_db),
):
    result = get_procedure_stats(db, procedure_id, state)
    if not result:
        raise HTTPException(status_code=404, detail="Procedure not found")
    return result
