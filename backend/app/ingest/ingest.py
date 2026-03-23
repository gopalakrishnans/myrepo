"""MRF ingestion orchestrator.

Reads hospital MRF and insurer MRF files, resolves entities (hospitals,
procedures, payers) against the database, and upserts price records.

Usage:
    python -m app.ingest.ingest --hospital-mrf /path/to/hospital.json
    python -m app.ingest.ingest --insurer-mrf /path/to/insurer.json
    python -m app.ingest.ingest --dir /path/to/mrf_files/
"""

import argparse
import gzip
import logging
import sys
import os
from pathlib import Path
from typing import BinaryIO

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.models import Hospital, Payer, Price, Procedure
from app.ingest.hospital_mrf import parse_hospital_mrf
from app.ingest.insurer_mrf import parse_insurer_mrf

logger = logging.getLogger(__name__)

BATCH_SIZE = 500


class EntityCache:
    """In-memory cache for resolved DB entities to avoid repeated lookups."""

    def __init__(self, db: Session):
        self.db = db
        self._hospitals_by_ein: dict[str, Hospital] = {}
        self._hospitals_by_name: dict[str, Hospital] = {}
        self._procedures: dict[str, Procedure] = {}
        self._payers: dict[str, Payer] = {}

    def get_or_create_hospital(self, data: dict) -> Hospital:
        ein = data.get("ein", "")
        name = data.get("name", "")

        # Try EIN lookup first
        if ein and ein in self._hospitals_by_ein:
            return self._hospitals_by_ein[ein]
        if name and name in self._hospitals_by_name:
            return self._hospitals_by_name[name]

        # DB lookup
        hospital = None
        if ein:
            hospital = self.db.query(Hospital).filter(Hospital.ein == ein).first()
        if not hospital and name:
            hospital = self.db.query(Hospital).filter(Hospital.name == name).first()

        if not hospital:
            hospital = Hospital(
                name=name,
                ein=ein,
                address=data.get("address", ""),
                city=data.get("city", ""),
                state=data.get("state", ""),
                zip_code=data.get("zip_code", ""),
                latitude=data.get("latitude"),
                longitude=data.get("longitude"),
                last_updated=data.get("last_updated"),
            )
            self.db.add(hospital)
            self.db.flush()

        if ein:
            self._hospitals_by_ein[ein] = hospital
        if name:
            self._hospitals_by_name[name] = hospital
        return hospital

    def get_or_create_procedure(self, data: dict) -> Procedure:
        key = f"{data['code_type']}:{data['billing_code']}"
        if key in self._procedures:
            return self._procedures[key]

        proc = (
            self.db.query(Procedure)
            .filter(
                Procedure.billing_code == data["billing_code"],
                Procedure.code_type == data["code_type"],
            )
            .first()
        )
        if not proc:
            proc = Procedure(
                billing_code=data["billing_code"],
                code_type=data["code_type"],
                description=data.get("description", ""),
                plain_language_name=data.get("description", data["billing_code"]),
                category="Uncategorized",
            )
            self.db.add(proc)
            self.db.flush()

        self._procedures[key] = proc
        return proc

    def get_or_create_payer(self, data: dict) -> Payer:
        key = f"{data['name']}|{data.get('plan_name', '')}"
        if key in self._payers:
            return self._payers[key]

        payer = (
            self.db.query(Payer)
            .filter(Payer.name == data["name"], Payer.plan_name == data.get("plan_name", ""))
            .first()
        )
        if not payer:
            payer = Payer(name=data["name"], plan_name=data.get("plan_name", ""))
            self.db.add(payer)
            self.db.flush()

        self._payers[key] = payer
        return payer

    def resolve_hospital_by_ein(self, ein: str) -> Hospital | None:
        if ein in self._hospitals_by_ein:
            return self._hospitals_by_ein[ein]
        hospital = self.db.query(Hospital).filter(Hospital.ein == ein).first()
        if hospital:
            self._hospitals_by_ein[ein] = hospital
        return hospital


def _open_file(path: Path) -> BinaryIO:
    """Open a file, handling .gz compression."""
    if path.suffix == ".gz":
        return gzip.open(path, "rb")
    return open(path, "rb")


def ingest_hospital_mrf(db: Session, path: Path) -> int:
    """Ingest a CMS hospital MRF file. Returns number of price records created."""
    cache = EntityCache(db)
    count = 0
    source = path.name

    with _open_file(path) as f:
        for record in parse_hospital_mrf(f, source_file=source):
            hospital = cache.get_or_create_hospital(record["hospital"])
            procedure = cache.get_or_create_procedure(record["procedure"])
            payer = cache.get_or_create_payer(record["payer"]) if record["payer"] else None

            price = Price(
                hospital_id=hospital.id,
                procedure_id=procedure.id,
                payer_id=payer.id if payer else None,
                gross_charge=record["price"].get("gross_charge"),
                discounted_cash_price=record["price"].get("discounted_cash_price"),
                negotiated_rate=record["price"].get("negotiated_rate"),
                min_negotiated_rate=record["price"].get("min_negotiated_rate"),
                max_negotiated_rate=record["price"].get("max_negotiated_rate"),
                source_type="hospital_mrf",
                source_file=source,
            )
            db.add(price)
            count += 1

            if count % BATCH_SIZE == 0:
                db.flush()
                logger.info("Hospital MRF: %d records ingested from %s", count, source)

    db.commit()
    logger.info("Hospital MRF: completed %d records from %s", count, source)
    return count


def ingest_insurer_mrf(db: Session, path: Path) -> int:
    """Ingest a TiC insurer in-network rates MRF file.

    Maps negotiated rates to hospitals via provider EINs. Records that can't
    be matched to a known hospital are skipped (insurer MRFs don't contain
    enough info to create hospital records).
    """
    cache = EntityCache(db)
    count = 0
    skipped = 0
    source = path.name

    with _open_file(path) as f:
        for record in parse_insurer_mrf(f, source_file=source):
            procedure = cache.get_or_create_procedure(record["procedure"])
            payer = cache.get_or_create_payer(record["payer"])

            # Match to hospitals by EIN
            matched_hospitals = []
            for ein in record.get("provider_eins", []):
                hospital = cache.resolve_hospital_by_ein(ein)
                if hospital:
                    matched_hospitals.append(hospital)

            if not matched_hospitals:
                skipped += 1
                continue

            neg_rate = record["price"].get("negotiated_rate")

            for hospital in matched_hospitals:
                price = Price(
                    hospital_id=hospital.id,
                    procedure_id=procedure.id,
                    payer_id=payer.id,
                    negotiated_rate=neg_rate,
                    source_type="insurer_mrf",
                    source_file=source,
                )
                db.add(price)
                count += 1

                if count % BATCH_SIZE == 0:
                    db.flush()
                    logger.info("Insurer MRF: %d records ingested from %s", count, source)

    db.commit()
    logger.info(
        "Insurer MRF: completed %d records from %s (%d skipped, no hospital match)",
        count, source, skipped,
    )
    return count


def ingest_file(path: str | Path, file_type: str | None = None) -> int:
    """Ingest a single MRF file.

    Args:
        path: Path to the MRF file (.json or .json.gz)
        file_type: "hospital" or "insurer". Auto-detected if None.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"MRF file not found: {path}")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if file_type == "hospital":
            return ingest_hospital_mrf(db, path)
        elif file_type == "insurer":
            return ingest_insurer_mrf(db, path)
        else:
            # Auto-detect: hospital MRFs have "hospital_name" at top level
            with _open_file(path) as f:
                # Read first 4KB to check
                head = f.read(4096).decode("utf-8", errors="ignore")
            if "hospital_name" in head or "standard_charge_information" in head:
                return ingest_hospital_mrf(db, path)
            elif "reporting_entity_name" in head or "in_network" in head:
                return ingest_insurer_mrf(db, path)
            else:
                raise ValueError(
                    f"Cannot auto-detect MRF type for {path}. "
                    "Use --type hospital or --type insurer."
                )
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Ingest healthcare MRF files")
    parser.add_argument(
        "--hospital-mrf", type=Path, action="append", default=[],
        help="Path to a CMS hospital MRF JSON file (can be repeated)",
    )
    parser.add_argument(
        "--insurer-mrf", type=Path, action="append", default=[],
        help="Path to a TiC insurer in-network rates MRF JSON file (can be repeated)",
    )
    parser.add_argument(
        "--dir", type=Path,
        help="Directory to scan for MRF files (auto-detects type)",
    )
    parser.add_argument(
        "--type", choices=["hospital", "insurer"],
        help="Force file type (used with --dir)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Enable verbose logging",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    total = 0

    for path in args.hospital_mrf:
        total += ingest_file(path, "hospital")

    for path in args.insurer_mrf:
        total += ingest_file(path, "insurer")

    if args.dir:
        mrf_dir = args.dir
        if not mrf_dir.is_dir():
            logger.error("Not a directory: %s", mrf_dir)
            sys.exit(1)
        for f in sorted(mrf_dir.glob("*.json")) + sorted(mrf_dir.glob("*.json.gz")):
            try:
                total += ingest_file(f, args.type)
            except Exception:
                logger.exception("Failed to ingest %s", f)

    print(f"\nTotal records ingested: {total}")


if __name__ == "__main__":
    main()
