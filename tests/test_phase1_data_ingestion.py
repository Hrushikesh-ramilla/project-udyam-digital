from __future__ import annotations

import time
import pytest
from pydantic import ValidationError

from backend.app.db.registry import (
    GSTIN_REGEX,
    UDYAM_REGEX,
    RegistryDatabase,
    get_registry,
)
from backend.app.models.schemas import GSTINRecord, ProductItem


def test_registry_row_counts_and_completeness():
    db = get_registry()
    assert db.product_count == 25, f"Expected 25 products, got {db.product_count}"
    assert db.gstin_count == 3534, f"Expected 3534 GSTINs, got {db.gstin_count}"
    assert db.udyam_count == 2723, f"Expected 2723 Udyam records, got {db.udyam_count}"
    assert db.lead_count == 5000, f"Expected 5000 SMB leads, got {db.lead_count}"


def test_schema_extra_forbid():
    # Attempting to supply extraneous fields to ProductItem must raise ValidationError
    with pytest.raises(ValidationError):
        ProductItem(
            product_id="P99",
            category="Test",
            product_name="Test Product",
            description="Test Description",
            unit="per user",
            price_min_inr_per_month=100,
            price_max_inr_per_month=200,
            one_time_setup_inr=0,
            min_contract_months=1,
            available_city_tiers=[1],
            min_employees=1,
            min_sites=1,
            requires_gstin=False,
            requires_one_of=[],
            typical_install_days=1,
            target_segments=["micro"],
            unauthorized_field="malicious_payload",
        )


def test_applicant_k01_gstin_cancelled_status():
    db = get_registry()
    # K01 GSTIN from synthetic document
    k01_gstin = "37IHKXV5167L1ZS"
    rec, latency = db.lookup_gstin(k01_gstin)
    assert rec is not None, "Applicant K01 GSTIN must exist in mock_gstin_registry"
    assert rec.status.upper() == "CANCELLED", f"Applicant K01 status must be Cancelled, got {rec.status}"
    assert rec.trade_name == "Vindhya Tours & Travels"
    assert "Tech Park Road" in rec.principal_place_of_business


def test_synthetic_identifiers_regex_invariants():
    # Invariant 1: 4th char of embedded PAN is 'X'
    k01_gstin = "37IHKXV5167L1ZS"
    assert GSTIN_REGEX.match(k01_gstin), f"GSTIN regex must accept 'X' in PAN 4th position: {k01_gstin}"

    # Standard valid GSTIN with 'C' (Company)
    valid_c_gstin = "27AABCB1234A1Z5"
    assert GSTIN_REGEX.match(valid_c_gstin), "Standard valid GSTIN must match"

    # Malformed GSTIN
    assert not GSTIN_REGEX.match("INVALID_GSTIN_123")
    assert not GSTIN_REGEX.match("27AABCB1234A1Z")  # 14 chars

    # Invariant 2: Synthetic Udyam format accepting district code '00'
    sample_udyam = "UDYAM-KL-00-3078801"
    assert UDYAM_REGEX.match(sample_udyam), f"Udyam regex must accept district code '00': {sample_udyam}"
    assert not UDYAM_REGEX.match("UDYAM-KL-99-3078801")  # non-00 district
    assert not UDYAM_REGEX.match("INVALID_UDYAM")


def test_lookup_latency_sub_millisecond():
    db = get_registry()
    leads = db.get_all_leads()
    test_gstins = [lead.gstin for lead in leads if lead.gstin][:500]

    latencies = []
    for g in test_gstins:
        rec, lat_ms = db.lookup_gstin(g)
        assert rec is not None
        latencies.append(lat_ms)

    avg_lat = sum(latencies) / len(latencies)
    assert avg_lat < 0.5, f"Expected average lookup latency < 0.5ms, got {avg_lat:.4f}ms"


def test_case_insensitivity_and_whitespace_handling():
    db = get_registry()
    rec1, _ = db.lookup_gstin("  37ihkxv5167l1zs  ")
    assert rec1 is not None
    assert rec1.gstin == "37IHKXV5167L1ZS"

    rec2, _ = db.lookup_udyam("  udyam-kl-00-3078801  ")
    assert rec2 is not None
    assert rec2.enterprise_name == "Balaji Dental Care LLP"


def test_nonexistent_records_return_none_safely():
    db = get_registry()
    rec_gst, lat1 = db.lookup_gstin("99XXXXX0000X1Z9")
    assert rec_gst is None
    assert lat1 >= 0

    rec_udyam, lat2 = db.lookup_udyam("UDYAM-ZZ-00-9999999")
    assert rec_udyam is None
    assert lat2 >= 0
