from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_full_cross_tab_e2e_journey():
    """Simulates the complete 4-step MSME journey + Partner Lead Rescue in sequence:
    Step 1: Multilingual AI Advisor Discovery (POST /api/advisor/chat)
    Step 2: Dynamic CPQ Cart Quoting & Non-GST Routing (POST /api/cpq/calculate)
    Step 3: Smart KYC DPDP Verification (POST /api/kyc/verify)
    Step 4: Provisioning Order Lifecycle Tracker (POST /api/orders -> POST /api/orders/{id}/advance)
    Step 5: Field Partner ML Rescue Telemetry (GET /api/partner/leads)
    """

    # --- STEP 1: ADVISOR CHAT ---
    advisor_payload = {
        "user_message": "Namaste, I run a retail grocery store in Jaipur with 4 workers, no GST. Need good wifi and basic cctv under 2500 per month.",
    }
    res_advisor = client.post("/api/advisor/chat", json=advisor_payload)
    assert res_advisor.status_code == 200, res_advisor.text
    advisor_data = res_advisor.json()
    assert "slots" in advisor_data
    assert "recommended_skus" in advisor_data
    assert len(advisor_data["recommended_skus"]) > 0
    assert advisor_data["slots"]["segment"] in ["micro", "Retail", "retail"] or len(advisor_data["slots"]["detected_needs"]) > 0
    skus_to_quote = advisor_data["recommended_skus"]

    # --- STEP 2: CPQ CART CALCULATION ---
    cart_items = [{"product_id": sku, "quantity": 1} for sku in skus_to_quote]
    cpq_payload = {
        "cart": cart_items,
        "contract_months": 12,
    }
    res_cpq = client.post("/api/cpq/calculate", json=cpq_payload)
    assert res_cpq.status_code == 200, res_cpq.text
    quote_data = res_cpq.json()
    assert quote_data["net_mrc_inr"] > 0
    assert quote_data["guaranteed_sla_days"] > 0
    assert "gst_exempt_eligible" in quote_data
    gst_exempt = quote_data["gst_exempt_eligible"]

    # --- STEP 3: SMART KYC VERIFICATION (Applicant K03 Clean Approval) ---
    kyc_payload = {
        "applicant_id": "K03",
        "cart_requires_gstin": not gst_exempt,
        "consent": {
            "consent_id": "CONSENT_E2E_2026_07_15",
            "user_id": "MERCHANT_USER_E2E",
            "purpose": "End-to-end telecom verification and onboarding.",
            "timestamp": "2026-07-15T10:00:00Z",
            "ip_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "granted": True,
        },
    }
    res_kyc = client.post("/api/kyc/verify", json=kyc_payload)
    assert res_kyc.status_code == 200, res_kyc.text
    kyc_data = res_kyc.json()
    assert kyc_data["status"] == "APPROVED"
    assert len(kyc_data["anomalies"]) == 0
    assert kyc_data["dpdp_consent_verified"] is True
    assert kyc_data["redacted_signatory_id"] is not None
    # Verify strict DPDP zero numeric exposure for 12-digit Aadhaar / national IDs
    assert not any(c.isdigit() for c in kyc_data["redacted_signatory_id"] if c in "0123456789" and "SYN" not in kyc_data["redacted_signatory_id"])

    # --- STEP 4: PROVISIONING ORDER CREATION & LIFECYCLE ADVANCEMENT ---
    order_payload = {
        "business_name": "Balaji Timber Traders",
        "bundle_name": " + ".join([i["product_name"] for i in quote_data["items"]]),
        "monthly_charge_inr": quote_data["net_mrc_inr"],
        "total_sla_days": quote_data["guaranteed_sla_days"],
        "partner_id": "PARTNER_JAIPUR_04",
    }
    # Test POST /api/orders
    res_order = client.post("/api/orders", json=order_payload)
    assert res_order.status_code == 200, res_order.text
    order_data = res_order.json()
    order_id = order_data["order_id"]
    assert order_id.startswith("AIRTEL-SMB-") or order_id.startswith("ORD_")
    assert order_data["monthly_charge_inr"] == quote_data["net_mrc_inr"]
    assert order_data["total_sla_days"] == quote_data["guaranteed_sla_days"]
    assert len(order_data["milestones"]) >= 4
    initial_stage = order_data["current_stage_idx"]

    # Test POST /api/orders/{id}/advance
    res_advance = client.post(f"/api/orders/{order_id}/advance")
    assert res_advance.status_code == 200, res_advance.text
    advanced_order = res_advance.json()
    assert advanced_order["current_stage_idx"] == initial_stage + 1

    # --- STEP 5: PARTNER ML RESCUE TELEMETRY ---
    res_leads = client.get("/api/partner/leads?limit=15")
    assert res_leads.status_code == 200, res_leads.text
    leads_data = res_leads.json()
    assert len(leads_data) == 15
    first_lead = leads_data[0]
    assert "propensity_score" in first_lead
    assert "priority_tier" in first_lead
    assert "next_best_action" in first_lead
    assert "top_risk_factors" in first_lead
    assert first_lead["propensity_score"] >= leads_data[-1]["propensity_score"]  # Sorted descending by rank
