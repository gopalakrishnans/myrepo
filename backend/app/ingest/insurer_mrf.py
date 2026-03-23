"""Parser for Transparency in Coverage (TiC) insurer MRF files.

Handles the CMS-mandated in-network rate JSON files published by insurers.
These follow the schema at:
https://github.com/CMSgov/price-transparency-guide/tree/master/schemas/in-network-rates

The files are typically very large (multi-GB), so we use ijson for streaming.
"""

import ijson
import logging
from typing import BinaryIO, Generator

logger = logging.getLogger(__name__)


def parse_insurer_mrf(
    fileobj: BinaryIO, source_file: str = ""
) -> Generator[dict, None, None]:
    """Stream-parse a TiC in-network rates MRF JSON file.

    Yields normalized dicts:
    {
        "reporting_entity": { name, type },
        "procedure": { billing_code, code_type, description },
        "payer": { name, plan_name },
        "providers": [ { npi: [...], ein: "..." } ],
        "price": { negotiated_rate, negotiated_type, billing_class },
        "source_type": "insurer_mrf",
        "source_file": "...",
    }
    """
    # Read reporting entity metadata
    entity_name = ""
    entity_type = ""
    plan_name = ""

    for prefix, event, value in ijson.parse(fileobj):
        if prefix == "reporting_entity_name":
            entity_name = value or ""
        elif prefix == "reporting_entity_type":
            entity_type = value or ""
        elif prefix == "plan_name":
            plan_name = value or ""
        elif prefix == "in_network":
            break

    fileobj.seek(0)

    # Stream in_network items
    items = ijson.items(fileobj, "in_network.item")
    for item in items:
        billing_code = item.get("billing_code", "")
        code_type = item.get("billing_code_type", "CPT").upper()
        name = item.get("name", "")
        description = item.get("description", name)

        if not billing_code:
            continue

        for rate_group in item.get("negotiated_rates", []):
            # Extract provider group info (EINs for hospital matching)
            provider_groups = rate_group.get("provider_groups", [])
            provider_eins = set()
            for pg in provider_groups:
                tin = pg.get("tin", {})
                if tin.get("type") == "ein" and tin.get("value"):
                    provider_eins.add(tin["value"])

            for neg_price in rate_group.get("negotiated_prices", []):
                neg_rate = neg_price.get("negotiated_rate")
                neg_type = neg_price.get("negotiated_type", "")
                billing_class = neg_price.get("billing_class", "")

                if neg_rate is None:
                    continue

                try:
                    neg_rate = round(float(neg_rate), 2)
                except (ValueError, TypeError):
                    continue

                yield {
                    "reporting_entity": {
                        "name": entity_name,
                        "type": entity_type,
                    },
                    "procedure": {
                        "billing_code": billing_code,
                        "code_type": code_type,
                        "description": description,
                    },
                    "payer": {
                        "name": entity_name,
                        "plan_name": plan_name or entity_name,
                    },
                    "provider_eins": list(provider_eins),
                    "price": {
                        "negotiated_rate": neg_rate,
                        "negotiated_type": neg_type,
                        "billing_class": billing_class,
                    },
                    "source_type": "insurer_mrf",
                    "source_file": source_file,
                }
