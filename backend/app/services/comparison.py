from sqlalchemy.orm import Session

from app.models.price import Price


def get_prices(
    db: Session,
    procedure_id: int,
    hospital_id: int | None = None,
    payer_id: int | None = None,
    state: str | None = None,
    sort_by: str = "price",
    limit: int = 50,
    offset: int = 0,
):
    q = db.query(Price).filter(Price.procedure_id == procedure_id)

    if hospital_id:
        q = q.filter(Price.hospital_id == hospital_id)
    if payer_id:
        q = q.filter(Price.payer_id == payer_id)
    if state:
        q = q.join(Price.hospital).filter(Price.hospital.property.mapper.class_.state == state)

    total = q.count()

    if sort_by == "price":
        q = q.order_by(Price.discounted_cash_price.asc())
    else:
        q = q.order_by(Price.hospital_id)

    items = q.offset(offset).limit(limit).all()
    return items, total


def compare_prices(db: Session, procedure_id: int, hospital_ids: list[int]):
    """Get prices for a procedure across specific hospitals, grouped by hospital."""
    prices = (
        db.query(Price)
        .filter(Price.procedure_id == procedure_id, Price.hospital_id.in_(hospital_ids))
        .all()
    )

    hospitals = {}
    for price in prices:
        h_id = price.hospital_id
        if h_id not in hospitals:
            hospitals[h_id] = {
                "hospital_id": h_id,
                "hospital_name": price.hospital.name,
                "city": price.hospital.city,
                "state": price.hospital.state,
                "cash_price": None,
                "gross_charge": price.gross_charge,
                "payer_rates": [],
            }

        if price.payer_id is None:
            hospitals[h_id]["cash_price"] = price.discounted_cash_price
        else:
            hospitals[h_id]["payer_rates"].append({
                "payer_name": price.payer.name,
                "plan_name": price.payer.plan_name,
                "negotiated_rate": price.negotiated_rate,
            })

    return list(hospitals.values())
