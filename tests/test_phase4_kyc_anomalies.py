from __future__ import annotations

import os
from datetime import date
from pathlib import Path
import pytest

from backend.app.db.registry import get_registry
from backend.app.models.schemas import DPDPConsentPayload, ExtractedDocPayload
from backend.app.services.kyc_engine import (
    ANCHOR_DATE,
    KYCEngine,
    redact_signatory_id,
)


@pytest.fixture
def kyc_engine() -> KYCEngine:
    return KYCEngine(get_registry())


@pytest.fixture
def valid_consent() -> DPDPConsentPayload:
    return DPDPConsentPayload(
        consent_id="CONSENT_2026_07_15_001",
        user_id="USER_TEST_001",
        purpose="Telecom enterprise onboarding, feasibility and KYC regulatory compliance under DPDP Act 2023.",
        timestamp="2026-07-15T10:00:00Z",
        ip_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        granted=True,
    )


def test_dpdp_zero_persistence_in_memory_redaction():
    # 12-digit Aadhaar UID format
    raw_uid = "9876 5432 1098"
    redacted = redact_signatory_id(raw_uid)
    assert redacted == "XXXX-XXXX-1098"
    assert "9876" not in redacted
    assert "5432" not in redacted

    # Hyphenated 12-digit UID
    raw_hyphen = "1234-5678-9012"
    assert redact_signatory_id(raw_hyphen) == "XXXX-XXXX-9012"

    # Synthetic Alphanumeric ID
    raw_syn = "SYN-ID-346190"
    redacted_syn = redact_signatory_id(raw_syn)
    assert "XXXX" in redacted_syn
    assert redacted_syn == "SYN-XXXX-190"


def test_dpdp_consent_missing_blocker(kyc_engine: KYCEngine):
    docs = {
        "signatory_id": ExtractedDocPayload(
            file_sha256="test_sha",
            doc_type="signatory_id",
            extracted_fields={"raw_id": "SYN-123456", "signatory_name": "Test User"},
        )
    }

    res = kyc_engine.verify_application(docs, cart_requires_gstin=False, consent=None)
    assert res.status == "REJECTED"
    assert any(a.code == "DPDP_CONSENT_MISSING" for a in res.anomalies)


def test_applicant_k01_cancelled_gstin_and_blank_udyam_traps(kyc_engine: KYCEngine, valid_consent: DPDPConsentPayload):
    # Load actual bytes of K01 files
    data_dir = Path("data/kyc_documents")
    k01_gst_bytes = (data_dir / "K01_gst_certificate.png").read_bytes()
    k01_udyam_bytes = (data_dir / "K01_udyam_certificate.png").read_bytes()
    k01_sig_bytes = (data_dir / "K01_signatory_id.png").read_bytes()
    k01_addr_bytes = (data_dir / "K01_address_proof.png").read_bytes()

    # Pass bytes to engine (testing SHA-256 byte hashing, zero filename coupling!)
    docs = {
        "gst_certificate": k01_gst_bytes,
        "udyam_certificate": k01_udyam_bytes,
        "signatory_id": k01_sig_bytes,
        "address_proof": k01_addr_bytes,
    }

    res = kyc_engine.verify_application(docs, cart_requires_gstin=True, consent=valid_consent)

    assert res.status == "REJECTED"
    # Planted Trap 1: Cancelled GSTIN
    gst_inactive_anomaly = next((a for a in res.anomalies if a.code == "GSTIN_INACTIVE"), None)
    assert gst_inactive_anomaly is not None, "Applicant K01 must trigger GSTIN_INACTIVE anomaly"
    assert gst_inactive_anomaly.severity == "BLOCKER"
    assert "CANCELLED" in gst_inactive_anomaly.message
    assert "1-click switch" in gst_inactive_anomaly.remediation

    # Planted Trap 2: Blank Udyam Number
    udyam_blank_anomaly = next((a for a in res.anomalies if a.code == "BLANK_UDYAM_NUMBER"), None)
    assert udyam_blank_anomaly is not None, "Applicant K01 must trigger BLANK_UDYAM_NUMBER"
    assert udyam_blank_anomaly.severity == "BLOCKER"


def test_applicant_k05_missing_udyam_document_trap(kyc_engine: KYCEngine, valid_consent: DPDPConsentPayload):
    data_dir = Path("data/kyc_documents")
    k05_gst_bytes = (data_dir / "K05_gst_certificate.png").read_bytes()
    k05_sig_bytes = (data_dir / "K05_signatory_id.png").read_bytes()
    k05_addr_bytes = (data_dir / "K05_address_proof.png").read_bytes()
    # K05 has NO udyam_certificate file in dataset!

    docs = {
        "gst_certificate": k05_gst_bytes,
        "signatory_id": k05_sig_bytes,
        "address_proof": k05_addr_bytes,
    }

    res = kyc_engine.verify_application(docs, cart_requires_gstin=True, consent=valid_consent)

    assert res.status == "REJECTED"
    missing_anomaly = next((a for a in res.anomalies if a.code == "MISSING_UDYAM_CERTIFICATE"), None)
    assert missing_anomaly is not None, "Applicant K05 must trigger MISSING_UDYAM_CERTIFICATE"
    assert missing_anomaly.severity == "BLOCKER"


def test_applicant_k11_stale_utility_bill_trap(kyc_engine: KYCEngine, valid_consent: DPDPConsentPayload):
    data_dir = Path("data/kyc_documents")
    k11_addr_bytes = (data_dir / "K11_address_proof.png").read_bytes()
    k11_gst_bytes = (data_dir / "K11_gst_certificate.png").read_bytes()
    k11_udyam_bytes = (data_dir / "K11_udyam_certificate.png").read_bytes()
    k11_sig_bytes = (data_dir / "K11_signatory_id.png").read_bytes()

    docs = {
        "gst_certificate": k11_gst_bytes,
        "udyam_certificate": k11_udyam_bytes,
        "signatory_id": k11_sig_bytes,
        "address_proof": k11_addr_bytes,
    }

    res = kyc_engine.verify_application(docs, cart_requires_gstin=True, consent=valid_consent)

    assert res.status == "REJECTED"
    # Bill is dated 2025-10-31, which is 257 days old from ANCHOR_DATE 2026-07-15!
    stale_anomaly = next((a for a in res.anomalies if a.code == "STALE_ADDRESS_PROOF"), None)
    assert stale_anomaly is not None, "Applicant K11 must trigger STALE_ADDRESS_PROOF"
    assert stale_anomaly.severity == "BLOCKER"
    assert res.address_bill_age_days is not None
    assert res.address_bill_age_days > 90


def test_applicant_k07_entity_mismatch_trap(kyc_engine: KYCEngine, valid_consent: DPDPConsentPayload):
    data_dir = Path("data/kyc_documents")
    k07_gst_bytes = (data_dir / "K07_gst_certificate.png").read_bytes()
    k07_udyam_bytes = (data_dir / "K07_udyam_certificate.png").read_bytes()
    k07_sig_bytes = (data_dir / "K07_signatory_id.png").read_bytes()
    k07_addr_bytes = (data_dir / "K07_address_proof.png").read_bytes()

    docs = {
        "gst_certificate": k07_gst_bytes,
        "udyam_certificate": k07_udyam_bytes,
        "signatory_id": k07_sig_bytes,
        "address_proof": k07_addr_bytes,
    }

    res = kyc_engine.verify_application(docs, cart_requires_gstin=True, consent=valid_consent)

    # K07 has legal name 'Neha Banerjee (Prop. Shri Physio Clinic)' vs declared trade name 'Neelgiri Physio Clinic'
    assert res.status == "REJECTED"
    assert any(a.code == "TRADE_NAME_MISMATCH_WITH_LEGAL" for a in res.anomalies)
    assert "signatory_vs_legal_name" in res.fuzzy_scores
    assert res.fuzzy_scores["signatory_vs_legal_name"] >= 80.0


def test_valid_applicant_k03_approval(kyc_engine: KYCEngine, valid_consent: DPDPConsentPayload):
    data_dir = Path("data/kyc_documents")
    k03_gst_bytes = (data_dir / "K03_gst_certificate.png").read_bytes()
    k03_udyam_bytes = (data_dir / "K03_udyam_certificate.png").read_bytes()
    k03_sig_bytes = (data_dir / "K03_signatory_id.png").read_bytes()
    k03_addr_bytes = (data_dir / "K03_address_proof.png").read_bytes()

    docs = {
        "gst_certificate": k03_gst_bytes,
        "udyam_certificate": k03_udyam_bytes,
        "signatory_id": k03_sig_bytes,
        "address_proof": k03_addr_bytes,
    }

    res = kyc_engine.verify_application(docs, cart_requires_gstin=True, consent=valid_consent)

    assert res.status == "APPROVED"
    assert res.gst_status == "ACTIVE"
    assert res.address_bill_age_days is not None
    assert res.address_bill_age_days <= 90  # 2026-06-20 is 25 days old
    assert len([a for a in res.anomalies if a.severity == "BLOCKER"]) == 0


def test_valid_applicant_k09_approval(kyc_engine: KYCEngine, valid_consent: DPDPConsentPayload):
    data_dir = Path("data/kyc_documents")
    docs = {
        "gst_certificate": (data_dir / "K09_gst_certificate.png").read_bytes(),
        "udyam_certificate": (data_dir / "K09_udyam_certificate.png").read_bytes(),
        "signatory_id": (data_dir / "K09_signatory_id.png").read_bytes(),
        "address_proof": (data_dir / "K09_address_proof.png").read_bytes(),
    }
    res = kyc_engine.verify_application(docs, cart_requires_gstin=True, consent=valid_consent)
    assert res.status == "APPROVED"
    assert res.gst_status == "ACTIVE"
    assert len([a for a in res.anomalies if a.severity == "BLOCKER"]) == 0


def test_valid_applicant_k12_approval(kyc_engine: KYCEngine, valid_consent: DPDPConsentPayload):
    data_dir = Path("data/kyc_documents")
    docs = {
        "gst_certificate": (data_dir / "K12_gst_certificate.png").read_bytes(),
        "udyam_certificate": (data_dir / "K12_udyam_certificate.png").read_bytes(),
        "signatory_id": (data_dir / "K12_signatory_id.png").read_bytes(),
        "address_proof": (data_dir / "K12_address_proof.png").read_bytes(),
    }
    res = kyc_engine.verify_application(docs, cart_requires_gstin=True, consent=valid_consent)
    assert res.status == "APPROVED"
    assert res.gst_status == "ACTIVE"
    assert len([a for a in res.anomalies if a.severity == "BLOCKER"]) == 0
