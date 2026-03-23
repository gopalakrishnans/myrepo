"""Parser for CMS Hospital Price Transparency MRF files.

Handles the CMS-mandated JSON schema where hospitals publish their standard
charges, including gross charges, discounted cash prices, and payer-specific
negotiated rates.

Spec: https://www.cms.gov/hospital-price-transparency/resources
"""

import ijson
import logging
from datetime import date
from pathlib import Path
from typing import BinaryIO, Generator

logger = logging.getLogger(__name__)


def _parse_date(val: str | None) -> date | None:
    if not val:
        return None
    try:
        return date.fromisoformat(val)
    except (ValueError, TypeError):
        return None


def parse_hospital_mrf(
    fileobj: BinaryIO, source_file: str = ""
) -> Generator[dict, None, None]:
    """Stream-parse a CMS hospital MRF JSON file.

    Yields normalized dicts ready for DB insertion:
    {
        "hospital": { name, ein, address, city, state, zip_code, lat, lon, last_updated },
        "procedure": { billing_code, code_type, description },
        "payer": { name, plan_name } | None,
        "price": { gross_charge, discounted_cash_price, negotiated_rate },
        "source_type": "hospital_mrf",
        "source_file": "...",
    }
    """
    # First pass: read hospital-level metadata (small, at top of file)
    hospital_meta = {}
    for prefix, event, value in ijson.parse(fileobj):
        if prefix == "hospital_name":
            hospital_meta["name"] = value
        elif prefix == "ein":
            hospital_meta["ein"] = value
        elif prefix == "last_updated_on":
            hospital_meta["last_updated"] = _parse_date(value)
        elif prefix == "hospital_address":
            hospital_meta["address"] = value
        elif prefix == "hospital_location.item" and "city" not in hospital_meta:
            # CMS schema: hospital_location is [street, city, state, zip]
            hospital_meta.setdefault("_location_parts", []).append(value)
        elif prefix == "standard_charge_information":
            break

    # Parse location parts if present
    parts = hospital_meta.pop("_location_parts", [])
    if len(parts) >= 4:
        hospital_meta.setdefault("address", parts[0])
        hospital_meta["city"] = parts[1]
        hospital_meta["state"] = parts[2]
        hospital_meta["zip_code"] = parts[3]

    # Rewind for streaming the items
    fileobj.seek(0)

    # Stream standard_charge_information items
    items = ijson.items(fileobj, "standard_charge_information.item")
    for item in items:
        codes = item.get("code_information", [])
        description = item.get("description", "")

        for code_info in codes:
            billing_code = code_info.get("code", "")
            code_type = code_info.get("type", "CPT").upper()

            if not billing_code:
                continue

            for charge_entry in item.get("standard_charges", []):
                gross = charge_entry.get("gross_charge")
                cash = charge_entry.get("discounted_cash_price")
                minimum = charge_entry.get("minimum")
                maximum = charge_entry.get("maximum")

                # Payer-specific negotiated rates
                payers_info = charge_entry.get("payers_information", [])
                if payers_info:
                    for payer_info in payers_info:
                        payer_name = payer_info.get("payer_name", "")
                        plan_name = payer_info.get("plan_name", "")
                        neg_rate = payer_info.get("standard_charge_dollar")

                        if neg_rate is None and gross is None and cash is None:
                            continue

                        yield {
                            "hospital": dict(hospital_meta),
                            "procedure": {
                                "billing_code": billing_code,
                                "code_type": code_type,
                                "description": description,
                            },
                            "payer": {
                                "name": payer_name,
                                "plan_name": plan_name,
                            },
                            "price": {
                                "gross_charge": _to_decimal(gross),
                                "discounted_cash_price": _to_decimal(cash),
                                "negotiated_rate": _to_decimal(neg_rate),
                                "min_negotiated_rate": _to_decimal(minimum),
                                "max_negotiated_rate": _to_decimal(maximum),
                            },
                            "source_type": "hospital_mrf",
                            "source_file": source_file,
                        }
                else:
                    # Cash/gross-only row (no payer)
                    if gross is None and cash is None:
                        continue

                    yield {
                        "hospital": dict(hospital_meta),
                        "procedure": {
                            "billing_code": billing_code,
                            "code_type": code_type,
                            "description": description,
                        },
                        "payer": None,
                        "price": {
                            "gross_charge": _to_decimal(gross),
                            "discounted_cash_price": _to_decimal(cash),
                            "negotiated_rate": None,
                            "min_negotiated_rate": _to_decimal(minimum),
                            "max_negotiated_rate": _to_decimal(maximum),
                        },
                        "source_type": "hospital_mrf",
                        "source_file": source_file,
                    }


def _to_decimal(val) -> float | None:
    if val is None:
        return None
    try:
        return round(float(val), 2)
    except (ValueError, TypeError):
        return None
