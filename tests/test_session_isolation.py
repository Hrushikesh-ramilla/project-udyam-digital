import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_session_id_multi_tenant_isolation():
    session_alpha = "UDYAM_SESSION_ALPHA_9999"
    session_beta = "UDYAM_SESSION_BETA_8888"

    # 1. Create order under session_alpha
    res_alpha = client.post(
        "/api/order/create",
        headers={"X-Session-ID": session_alpha},
        json={
            "business_name": "Alpha Diagnostics LLP",
            "bundle_name": "Alpha Secure Connect",
            "monthly_charge_inr": 3499,
            "total_sla_days": 3,
            "partner_id": "PARTNER_DIRECT"
        }
    )
    assert res_alpha.status_code == 200, res_alpha.text
    order_alpha = res_alpha.json()
    order_alpha_id = order_alpha["order_id"]

    # 2. Create order under session_beta
    res_beta = client.post(
        "/api/order/create",
        headers={"X-Session-ID": session_beta},
        json={
            "business_name": "Beta Kirana General Store",
            "bundle_name": "Kirana Smart Wi-Fi",
            "monthly_charge_inr": 1299,
            "total_sla_days": 2,
            "partner_id": "PARTNER_DIRECT"
        }
    )
    assert res_beta.status_code == 200, res_beta.text
    order_beta = res_beta.json()
    order_beta_id = order_beta["order_id"]

    # 3. List orders with X-Session-ID: session_alpha
    list_alpha = client.get("/api/orders", headers={"X-Session-ID": session_alpha})
    assert list_alpha.status_code == 200
    alpha_orders = list_alpha.json()
    alpha_ids = [o["order_id"] for o in alpha_orders]
    assert order_alpha_id in alpha_ids
    assert order_beta_id not in alpha_ids, "Session Alpha leaked Session Beta order!"

    # 4. List orders with X-Session-ID: session_beta
    list_beta = client.get("/api/orders", headers={"X-Session-ID": session_beta})
    assert list_beta.status_code == 200
    beta_orders = list_beta.json()
    beta_ids = [o["order_id"] for o in beta_orders]
    assert order_beta_id in beta_ids
    assert order_alpha_id not in beta_ids, "Session Beta leaked Session Alpha order!"

    # 5. Access specific order with matching session
    fetch_alpha_ok = client.get(f"/api/orders/{order_alpha_id}", headers={"X-Session-ID": session_alpha})
    assert fetch_alpha_ok.status_code == 200
    assert fetch_alpha_ok.json()["business_name"] == "Alpha Diagnostics LLP"

    # 6. Access specific order with conflicting session -> must be segregated / 404
    fetch_alpha_cross = client.get(f"/api/orders/{order_alpha_id}", headers={"X-Session-ID": session_beta})
    assert fetch_alpha_cross.status_code == 404, "Conflicting session was able to access cross-tenant order!"


def test_session_id_header_accepted_on_core_endpoints():
    test_session = "UDYAM_SESSION_TEST_GATEWAY_7777"

    # CPQ calculate with X-Session-ID
    cpq_res = client.post(
        "/api/cpq/calculate",
        headers={"X-Session-ID": test_session},
        json={
            "cart": [{"product_id": "P01", "quantity": 1}],
            "contract_months": 12
        }
    )
    assert cpq_res.status_code == 200
    data = cpq_res.json()
    assert data["net_mrc_inr"] > 0

    # KYC verify with X-Session-ID
    kyc_res = client.post(
        "/api/kyc/verify",
        headers={"X-Session-ID": test_session},
        json={
            "applicant_preset": "K01",
            "cart_requires_gstin": True,
            "consent": {
                "consent_id": "DPDP-CONSENT-101",
                "user_id": "APPLICANT-K01",
                "purpose": "Airtel Business Enterprise Onboarding",
                "timestamp": "2026-07-15T10:00:00Z",
                "ip_hash": "a1b2c3d4e5f6",
                "granted": True
            }
        }
    )
    assert kyc_res.status_code == 200
    assert kyc_res.json()["dpdp_consent_verified"] is True
