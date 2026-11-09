from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["catalogue_count"] == 25
    assert data["gstin_registry_count"] == 3534
    assert data["udyam_registry_count"] == 2723
    assert data["leads_telemetry_count"] == 5000


def test_api_products():
    res = client.get("/api/products")
    assert res.status_code == 200
    products = res.json()
    assert len(products) == 25
    assert any(p["product_id"] == "P01" for p in products)


def test_api_advisor_chat():
    payload = {
        "user_message": "Bhaiya, meri Jaipur mein medical shop hai, 4 staff hain, GST nahi hai.",
    }
    res = client.post("/api/advisor/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["slots"]["segment"] == "micro"
    assert data["slots"]["city_tier"] == 2
    assert data["slots"]["has_gstin"] is False
    assert len(data["display_markdown"]) > 0
    assert len(data["spoken_tts_text"]) > 0


def test_api_cpq_calculate_and_budget_optimizer():
    # 1. Calculate Quote
    calc_payload = {
        "cart": [
            {"product_id": "P01", "quantity": 1},
            {"product_id": "P09", "quantity": 1},
        ],
        "contract_months": 12,
    }
    res_calc = client.post("/api/cpq/calculate", json=calc_payload)
    assert res_calc.status_code == 200
    quote = res_calc.json()
    assert quote["gross_mrc_inr"] == 999 + 499

    # 2. Reverse Budget Optimizer
    opt_payload = {
        "profile": {
            "segment": "micro",
            "city_tier": 2,
            "employee_count": 3,
            "num_sites": 1,
            "has_gstin": False,
            "detected_needs": ["pos_upi_uptime"],
        },
        "max_monthly_budget": 2000,
    }
    res_opt = client.post("/api/cpq/optimize-budget", json=opt_payload)
    assert res_opt.status_code == 200
    opt_data = res_opt.json()
    assert opt_data["commercials"]["net_mrc_inr"] <= 2000


def test_api_kyc_verification_preset_k01():
    payload = {
        "applicant_preset": "K01",
        "cart_requires_gstin": True,
    }
    res = client.post("/api/kyc/verify", json=payload)
    assert res.status_code == 200
    result = res.json()
    assert result["status"] == "REJECTED"
    assert any(a["code"] == "GSTIN_INACTIVE" for a in result["anomalies"])


def test_api_partner_leads_and_provisioning_flow():
    # 1. Partner Rescue Leads
    res_leads = client.get("/api/partner/leads?limit=5")
    assert res_leads.status_code == 200
    leads = res_leads.json()
    assert len(leads) > 0
    assert "propensity_score" in leads[0]

    # 2. Provisioning Order Flow
    order_payload = {
        "business_name": "Saffron Bakers",
        "bundle_name": "Biz 5G AirFiber 100",
        "monthly_charge_inr": 899,
        "total_sla_days": 2,
        "partner_id": "PARTNER_PUNJAB_01",
    }
    res_create = client.post("/api/order/create", json=order_payload)
    assert res_create.status_code == 200
    order = res_create.json()
    order_id = order["order_id"]
    assert order["current_stage_idx"] == 0

    # Advance stage
    res_adv = client.post(f"/api/order/{order_id}/advance")
    assert res_adv.status_code == 200
    adv_order = res_adv.json()
    assert adv_order["current_stage_idx"] == 1


def test_api_judge_scenarios():
    for sc in ["K01_CANCELLED_GST", "K05_MISSING_UDYAM", "K11_STALE_BILL", "K07_ENTITY_MISMATCH", "NON_GST_KIRANA"]:
        res = client.get(f"/api/demo/judge-scenario/{sc}")
        assert res.status_code == 200
        data = res.json()
        assert "expected_outcome" in data


def test_api_live_system_benchmarks():
    res = client.get("/api/benchmarks/run")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "benchmarks" in data
    assert data["benchmarks"]["cpq_dag_solver_ms"] < 50.0
    assert data["benchmarks"]["kyc_anomaly_engine_ms"] < 250.0
    assert data["benchmarks"]["sqlite_wal_persistence_ms"] < 10.0
    assert "model_card" in data
    assert data["model_card"]["test_auc"] == 0.842
