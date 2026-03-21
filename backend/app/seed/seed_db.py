"""Seed the database with sample healthcare pricing data."""

import sys
import os

# Allow running as module from backend directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.database import Base, engine, SessionLocal
from app.models import Hospital, Payer, Price, Procedure
from app.seed.generate_data import (
    generate_hospitals,
    generate_payers,
    generate_prices,
    generate_procedures,
)


def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Hospitals
        hospitals_data = generate_hospitals()
        hospitals = []
        for h in hospitals_data:
            hospital = Hospital(**h)
            db.add(hospital)
            hospitals.append(hospital)
        db.flush()

        # Procedures
        procedures_data = generate_procedures()
        procedures = []
        for p in procedures_data:
            procedure = Procedure(**p)
            db.add(procedure)
            procedures.append(procedure)
        db.flush()

        # Payers
        payers_data = generate_payers()
        payers = []
        for p in payers_data:
            payer = Payer(**p)
            db.add(payer)
            payers.append(payer)
        db.flush()

        # Prices
        prices_data = generate_prices(hospitals_data, procedures_data, payers_data)
        for price in prices_data:
            db.add(Price(
                hospital_id=hospitals[price["hospital_idx"]].id,
                procedure_id=procedures[price["procedure_idx"]].id,
                payer_id=payers[price["payer_idx"]].id if price["payer_idx"] is not None else None,
                gross_charge=price["gross_charge"],
                discounted_cash_price=price["discounted_cash_price"],
                negotiated_rate=price["negotiated_rate"],
                min_negotiated_rate=price["min_negotiated_rate"],
                max_negotiated_rate=price["max_negotiated_rate"],
            ))

        db.commit()
        print(f"Seeded: {len(hospitals)} hospitals, {len(procedures)} procedures, "
              f"{len(payers)} payers, {len(prices_data)} price records")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
