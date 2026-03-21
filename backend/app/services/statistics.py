import statistics as stats

from sqlalchemy.orm import Session

from app.models.price import Price
from app.models.procedure import Procedure


def get_procedure_stats(db: Session, procedure_id: int, state: str | None = None):
    procedure = db.get(Procedure, procedure_id)
    if not procedure:
        return None

    q = db.query(Price).filter(Price.procedure_id == procedure_id, Price.payer_id.is_(None))
    if state:
        q = q.join(Price.hospital).filter(Price.hospital.property.mapper.class_.state == state)

    cash_prices = [float(p.discounted_cash_price) for p in q.all() if p.discounted_cash_price]

    neg_q = db.query(Price).filter(Price.procedure_id == procedure_id, Price.payer_id.isnot(None))
    if state:
        neg_q = neg_q.join(Price.hospital).filter(Price.hospital.property.mapper.class_.state == state)
    neg_rates = [float(p.negotiated_rate) for p in neg_q.all() if p.negotiated_rate]

    result = {
        "procedure_id": procedure_id,
        "plain_language_name": procedure.plain_language_name,
        "billing_code": procedure.billing_code,
        "cash_price_avg": round(stats.mean(cash_prices), 2) if cash_prices else None,
        "cash_price_median": round(stats.median(cash_prices), 2) if cash_prices else None,
        "cash_price_min": round(min(cash_prices), 2) if cash_prices else None,
        "cash_price_max": round(max(cash_prices), 2) if cash_prices else None,
        "cash_price_count": len(cash_prices),
        "negotiated_avg": round(stats.mean(neg_rates), 2) if neg_rates else None,
        "negotiated_min": round(min(neg_rates), 2) if neg_rates else None,
        "negotiated_max": round(max(neg_rates), 2) if neg_rates else None,
        "fair_price": round(stats.median(cash_prices), 2) if cash_prices else None,
    }

    return result
