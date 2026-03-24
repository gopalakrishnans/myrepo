"""
Ingest mammography providers from the NPPES NPI Registry into the database.

Usage:
    cd backend
    python -m app.seed.ingest_nppes                  # Seattle metro, dry run
    python -m app.seed.ingest_nppes --commit          # write to DB
    python -m app.seed.ingest_nppes --commit --state WA --cities "Seattle,Bellevue"
"""

import argparse
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import httpx
import pgeocode

from app.database import Base, engine, SessionLocal
from app.models.hospital import Hospital

# ---------------------------------------------------------------------------
# Taxonomy codes considered relevant for mammography / breast imaging
# ---------------------------------------------------------------------------
MAMMOGRAPHY_TAXONOMY_CODES = {
    "261QR0208X",  # Radiology, Clinic/Center
    "261QR0200X",  # Radiology (generic clinic)
    "2085R0202X",  # Diagnostic Radiology (physician specialty org)
    "261QX0200X",  # Oncology, Clinic/Center (includes breast centers)
}

# Seattle metro area cities to query
DEFAULT_CITIES = [
    "Seattle",
    "Bellevue",
    "Kirkland",
    "Redmond",
    "Renton",
    "Issaquah",
    "Bothell",
    "Edmonds",
    "Lynnwood",
    "Shoreline",
    "Burien",
    "Federal Way",
    "Kent",
    "Auburn",
    "Everett",
]

NPPES_API = "https://npiregistry.cms.hhs.gov/api/"
REQUEST_DELAY = 0.5  # seconds between NPPES requests to be polite

geo = pgeocode.Nominatim("us")


# ---------------------------------------------------------------------------
# NPPES helpers
# ---------------------------------------------------------------------------

def _fetch_page(city: str, state: str, skip: int) -> dict:
    """Fetch one page of NPI-2 (organization) results from NPPES."""
    params = {
        "version": "2.1",
        "enumeration_type": "NPI-2",
        "taxonomy_description": "radiology",
        "city": city,
        "state": state,
        "limit": 200,
        "skip": skip,
    }
    resp = httpx.get(NPPES_API, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_providers(cities: list[str], state: str) -> list[dict]:
    """Fetch all radiology organizations from NPPES for the given cities."""
    seen_npis = set()
    providers = []

    for city in cities:
        skip = 0
        while True:
            print(f"  Fetching {city}, {state} (skip={skip})...")
            data = _fetch_page(city, state, skip)
            results = data.get("results", [])
            if not results:
                break

            for r in results:
                npi = r.get("number")
                if not npi or npi in seen_npis:
                    continue

                # Filter: must have at least one mammography-relevant taxonomy
                taxonomies = r.get("taxonomies", [])
                codes = {t.get("code") for t in taxonomies}
                if not codes & MAMMOGRAPHY_TAXONOMY_CODES:
                    continue

                seen_npis.add(npi)
                providers.append(r)

            if len(results) < 200:
                break
            skip += 200
            time.sleep(REQUEST_DELAY)

        time.sleep(REQUEST_DELAY)

    return providers


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def _location_address(addresses: list[dict]) -> dict | None:
    """Return the LOCATION address, falling back to MAILING."""
    by_purpose = {a.get("address_purpose"): a for a in addresses}
    return by_purpose.get("LOCATION") or by_purpose.get("MAILING")


def _geocode_zip(zip_code: str) -> tuple[float | None, float | None]:
    if not zip_code:
        return None, None
    result = geo.query_postal_code(zip_code[:5])
    if result is None:
        return None, None
    lat = result.get("latitude")
    lon = result.get("longitude")
    if lat != lat or lon != lon:  # NaN check
        return None, None
    return float(lat), float(lon)


def parse_provider(raw: dict) -> dict:
    """Convert a raw NPPES result into a Hospital field dict."""
    basic = raw.get("basic", {})
    addresses = raw.get("addresses", [])
    addr = _location_address(addresses) or {}

    zip_code = (addr.get("postal_code") or "")[:10]
    lat, lon = _geocode_zip(zip_code)

    phone = addr.get("telephone_number") or basic.get("phone")

    return {
        "npi": raw.get("number"),
        "name": basic.get("organization_name") or basic.get("authorized_official_name_prefix", ""),
        "address": addr.get("address_1"),
        "city": addr.get("city"),
        "state": addr.get("state"),
        "zip_code": zip_code,
        "latitude": lat,
        "longitude": lon,
        "phone": phone,
        "facility_type": "imaging_center",
        # Fields left for manual curation or future enrichment
        "website": None,
        "booking_url": None,
        "has_3d_mammography": None,
        "acr_accredited": None,
        "accepts_new_patients": None,
        "availability_note": None,
        "accepted_insurances": None,
    }


# ---------------------------------------------------------------------------
# Database upsert
# ---------------------------------------------------------------------------

def upsert_providers(providers: list[dict], commit: bool) -> tuple[int, int]:
    """Insert new providers; update existing ones matched by NPI. Returns (inserted, updated)."""
    db = SessionLocal()
    inserted = updated = 0
    try:
        for p in providers:
            npi = p["npi"]
            existing = db.query(Hospital).filter(Hospital.npi == npi).first()
            if existing:
                for k, v in p.items():
                    if v is not None:
                        setattr(existing, k, v)
                updated += 1
            else:
                db.add(Hospital(**p))
                inserted += 1

        if commit:
            db.commit()
        else:
            db.rollback()
    finally:
        db.close()

    return inserted, updated


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Ingest mammography providers from NPPES")
    parser.add_argument("--state", default="WA")
    parser.add_argument("--cities", default=None, help="Comma-separated list of cities")
    parser.add_argument("--commit", action="store_true", help="Write results to the database")
    args = parser.parse_args()

    cities = [c.strip() for c in args.cities.split(",")] if args.cities else DEFAULT_CITIES

    print(f"Querying NPPES for radiology orgs in {len(cities)} cities ({args.state})...")
    raw_providers = fetch_providers(cities, args.state)
    print(f"Found {len(raw_providers)} matching providers after taxonomy filter\n")

    parsed = [parse_provider(r) for r in raw_providers]

    if not args.commit:
        print("DRY RUN — pass --commit to write to the database\n")
        for p in parsed:
            print(f"  [{p['npi']}] {p['name']} — {p['city']}, {p['state']} {p['zip_code']}")
        print(f"\nTotal: {len(parsed)}")
        return

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    inserted, updated = upsert_providers(parsed, commit=True)
    print(f"Done — inserted: {inserted}, updated: {updated}")


if __name__ == "__main__":
    main()
