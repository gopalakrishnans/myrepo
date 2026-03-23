"""Tests for MRF ingestion parsers and orchestrator."""

import io
import json
import pytest

from app.ingest.hospital_mrf import parse_hospital_mrf
from app.ingest.insurer_mrf import parse_insurer_mrf


def _make_binary(data: dict) -> io.BytesIO:
    return io.BytesIO(json.dumps(data).encode("utf-8"))


class TestHospitalMRFParser:
    def test_parses_standard_charges_with_payer(self):
        mrf = {
            "hospital_name": "Test General Hospital",
            "ein": "12-3456789",
            "last_updated_on": "2025-06-01",
            "hospital_address": "123 Main St",
            "standard_charge_information": [
                {
                    "description": "MRI brain without contrast",
                    "code_information": [
                        {"code": "70551", "type": "CPT"}
                    ],
                    "standard_charges": [
                        {
                            "gross_charge": 5000.00,
                            "discounted_cash_price": 2000.00,
                            "minimum": 1200.00,
                            "maximum": 3500.00,
                            "payers_information": [
                                {
                                    "payer_name": "Aetna",
                                    "plan_name": "PPO",
                                    "standard_charge_dollar": 1500.00,
                                    "standard_charge_methodology": "fee schedule",
                                }
                            ],
                        }
                    ],
                }
            ],
        }

        records = list(parse_hospital_mrf(_make_binary(mrf), source_file="test.json"))

        assert len(records) == 1
        r = records[0]
        assert r["hospital"]["name"] == "Test General Hospital"
        assert r["hospital"]["ein"] == "12-3456789"
        assert r["procedure"]["billing_code"] == "70551"
        assert r["procedure"]["code_type"] == "CPT"
        assert r["payer"]["name"] == "Aetna"
        assert r["payer"]["plan_name"] == "PPO"
        assert r["price"]["gross_charge"] == 5000.00
        assert r["price"]["discounted_cash_price"] == 2000.00
        assert r["price"]["negotiated_rate"] == 1500.00
        assert r["source_type"] == "hospital_mrf"

    def test_parses_cash_only_row(self):
        mrf = {
            "hospital_name": "Cash Hospital",
            "ein": "99-0000000",
            "standard_charge_information": [
                {
                    "description": "Chest X-Ray",
                    "code_information": [{"code": "71046", "type": "CPT"}],
                    "standard_charges": [
                        {
                            "gross_charge": 600.00,
                            "discounted_cash_price": 200.00,
                        }
                    ],
                }
            ],
        }

        records = list(parse_hospital_mrf(_make_binary(mrf)))
        assert len(records) == 1
        assert records[0]["payer"] is None
        assert records[0]["price"]["gross_charge"] == 600.00

    def test_skips_entries_with_no_code(self):
        mrf = {
            "hospital_name": "Test",
            "standard_charge_information": [
                {
                    "description": "Unknown",
                    "code_information": [{"code": "", "type": "CPT"}],
                    "standard_charges": [{"gross_charge": 100}],
                }
            ],
        }
        records = list(parse_hospital_mrf(_make_binary(mrf)))
        assert len(records) == 0

    def test_multiple_payers_per_charge(self):
        mrf = {
            "hospital_name": "Multi Payer Hospital",
            "standard_charge_information": [
                {
                    "description": "CBC",
                    "code_information": [{"code": "85025", "type": "CPT"}],
                    "standard_charges": [
                        {
                            "gross_charge": 150.00,
                            "discounted_cash_price": 50.00,
                            "payers_information": [
                                {"payer_name": "Aetna", "plan_name": "PPO", "standard_charge_dollar": 80.00},
                                {"payer_name": "BCBS", "plan_name": "HMO", "standard_charge_dollar": 65.00},
                            ],
                        }
                    ],
                }
            ],
        }

        records = list(parse_hospital_mrf(_make_binary(mrf)))
        assert len(records) == 2
        payer_names = {r["payer"]["name"] for r in records}
        assert payer_names == {"Aetna", "BCBS"}


class TestInsurerMRFParser:
    def test_parses_in_network_rates(self):
        mrf = {
            "reporting_entity_name": "Aetna",
            "reporting_entity_type": "health insurance issuer",
            "plan_name": "Open Access PPO",
            "in_network": [
                {
                    "negotiation_arrangement": "ffs",
                    "name": "MRI Brain",
                    "billing_code_type": "CPT",
                    "billing_code": "70553",
                    "negotiated_rates": [
                        {
                            "provider_groups": [
                                {
                                    "npi": [1234567890],
                                    "tin": {"type": "ein", "value": "12-3456789"},
                                }
                            ],
                            "negotiated_prices": [
                                {
                                    "negotiated_type": "negotiated",
                                    "negotiated_rate": 1500.00,
                                    "service_code": ["11"],
                                    "billing_class": "professional",
                                }
                            ],
                        }
                    ],
                }
            ],
        }

        records = list(parse_insurer_mrf(_make_binary(mrf)))

        assert len(records) == 1
        r = records[0]
        assert r["reporting_entity"]["name"] == "Aetna"
        assert r["procedure"]["billing_code"] == "70553"
        assert r["payer"]["name"] == "Aetna"
        assert r["payer"]["plan_name"] == "Open Access PPO"
        assert r["provider_eins"] == ["12-3456789"]
        assert r["price"]["negotiated_rate"] == 1500.00
        assert r["source_type"] == "insurer_mrf"

    def test_multiple_provider_groups(self):
        mrf = {
            "reporting_entity_name": "UHC",
            "reporting_entity_type": "health insurance issuer",
            "in_network": [
                {
                    "billing_code": "85025",
                    "billing_code_type": "CPT",
                    "name": "CBC",
                    "negotiated_rates": [
                        {
                            "provider_groups": [
                                {"npi": [111], "tin": {"type": "ein", "value": "11-1111111"}},
                                {"npi": [222], "tin": {"type": "ein", "value": "22-2222222"}},
                            ],
                            "negotiated_prices": [
                                {"negotiated_rate": 45.00, "negotiated_type": "negotiated", "billing_class": "professional"}
                            ],
                        }
                    ],
                }
            ],
        }

        records = list(parse_insurer_mrf(_make_binary(mrf)))
        assert len(records) == 1
        assert set(records[0]["provider_eins"]) == {"11-1111111", "22-2222222"}

    def test_skips_null_rates(self):
        mrf = {
            "reporting_entity_name": "Test",
            "in_network": [
                {
                    "billing_code": "99213",
                    "billing_code_type": "CPT",
                    "name": "Office visit",
                    "negotiated_rates": [
                        {
                            "provider_groups": [],
                            "negotiated_prices": [
                                {"negotiated_rate": None, "negotiated_type": "negotiated"}
                            ],
                        }
                    ],
                }
            ],
        }
        records = list(parse_insurer_mrf(_make_binary(mrf)))
        assert len(records) == 0

    def test_skips_empty_billing_code(self):
        mrf = {
            "reporting_entity_name": "Test",
            "in_network": [
                {
                    "billing_code": "",
                    "billing_code_type": "CPT",
                    "name": "Unknown",
                    "negotiated_rates": [],
                }
            ],
        }
        records = list(parse_insurer_mrf(_make_binary(mrf)))
        assert len(records) == 0
