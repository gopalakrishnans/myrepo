"""Load Seattle mammography providers from the curated JSON file into the database.

Usage:
    cd backend
    python -m app.seed.load_providers            # dry run
    python -m app.seed.load_providers --commit   # write to DB
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.database import Base, engine, SessionLocal
from app.models.hospital import Hospital

DATA_FILE = os.path.join(os.path.dirname(__file__), "seattle_mammography_providers.json")


def load(commit: bool) -> None:
    with open(DATA_FILE) as f:
        providers = json.load(f)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    inserted = updated = 0

    try:
        for p in providers:
            # Match on NPI if present, otherwise fall back to name+city
            existing = None
            if p.get("npi"):
                existing = db.query(Hospital).filter(Hospital.npi == p["npi"]).first()
            if existing is None:
                existing = (
                    db.query(Hospital)
                    .filter(Hospital.name == p["name"], Hospital.city == p["city"])
                    .first()
                )

            if existing:
                for k, v in p.items():
                    if v is not None:
                        setattr(existing, k, v)
                updated += 1
                action = "update"
            else:
                db.add(Hospital(**p))
                inserted += 1
                action = "insert"

            print(f"  [{action}] {p['name']} — {p['city']}, {p['state']}")

        if commit:
            db.commit()
            print(f"\nDone — inserted: {inserted}, updated: {updated}")
        else:
            db.rollback()
            print(f"\nDRY RUN — would insert: {inserted}, update: {updated}  (pass --commit to write)")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", action="store_true")
    args = parser.parse_args()
    load(commit=args.commit)
