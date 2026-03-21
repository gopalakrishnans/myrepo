from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.procedure import Procedure


def search_procedures(db: Session, query: str = "", category: str = "", limit: int = 20, offset: int = 0):
    q = db.query(Procedure)

    if query:
        pattern = f"%{query}%"
        q = q.filter(
            or_(
                Procedure.plain_language_name.ilike(pattern),
                Procedure.billing_code.ilike(pattern),
                Procedure.description.ilike(pattern),
            )
        )

    if category:
        q = q.filter(Procedure.category.ilike(f"%{category}%"))

    total = q.count()
    items = q.order_by(Procedure.plain_language_name).offset(offset).limit(limit).all()
    return items, total


def get_categories(db: Session) -> list[str]:
    rows = db.query(Procedure.category).distinct().order_by(Procedure.category).all()
    return [r[0] for r in rows if r[0]]
