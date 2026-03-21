from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.procedure import Procedure
from app.schemas.procedure import ProcedureResponse
from app.services.search import get_categories, search_procedures

router = APIRouter(prefix="/procedures", tags=["procedures"])


@router.get("/search", response_model=dict)
def search(
    q: str = Query("", description="Search by name or billing code"),
    category: str = Query("", description="Filter by category"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    items, total = search_procedures(db, q, category, limit, offset)
    return {
        "items": [ProcedureResponse.model_validate(p) for p in items],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/categories", response_model=list[str])
def categories(db: Session = Depends(get_db)):
    return get_categories(db)


@router.get("/{procedure_id}", response_model=ProcedureResponse)
def get_procedure(procedure_id: int, db: Session = Depends(get_db)):
    procedure = db.get(Procedure, procedure_id)
    if not procedure:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Procedure not found")
    return ProcedureResponse.model_validate(procedure)
