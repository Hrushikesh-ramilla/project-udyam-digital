from __future__ import annotations

import hashlib
import hmac
import uuid
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.payment_gateway import RAZORPAY_KEY_SECRET

client = TestClient(app)


def test_payment_intent_creation_and_upi_spec():
    # 1. Create order
    ord_resp = client.post(
        "/api/orders",
        json={
            "business_name": "Balaji Electrical Works",
            "bundle_name": "Udyam Vyapar",
            "monthly_charge_inr": 1499,
            "total_sla_days": 4,
        },
    )
    assert ord_resp.status_code == 200
    order_id = ord_resp.json()["order_id"]

    # 2. Create payment intent
    intent_resp = client.post(
        "/api/payments/create-intent",
        json={
            "order_id": order_id,
            "amount_inr": 1499.0,
            "payment_method": "UPI_INTENT",
        },
    )
    assert intent_resp.status_code == 200
    data = intent_resp.json()
    assert "PAY-AIRTEL-" in data["payment_id"]
    assert data["order_id"] == order_id
    assert data["amount_inr"] == 1499.0
    assert "upi://pay?" in data["upi_uri"]
    assert "pa=airtel.enterprise%40icici" in data["upi_uri"]
    assert "am=1499.00" in data["upi_uri"]
    assert "data:image/png;base64," in data["qr_data_url"]
    assert data["razorpay_order_id"].startswith("order_")


def test_upi_utr_verification_validation_and_rejection():
    # 1. Create order & intent
    ord_resp = client.post(
        "/api/orders",
        json={
            "business_name": "Ganesh Textiles",
            "bundle_name": "Udyam Scale",
            "monthly_charge_inr": 4999,
        },
    )
    order_id = ord_resp.json()["order_id"]

    intent = client.post(
        "/api/payments/create-intent",
        json={"order_id": order_id, "amount_inr": 4999.0},
    ).json()
    payment_id = intent["payment_id"]

    # 2. Test malformed UTR (alphanumeric or wrong length)
    bad_utr_resp = client.post(
        "/api/payments/verify-upi",
        json={
            "payment_id": payment_id,
            "order_id": order_id,
            "utr_reference": "INVALID_UTR_123",
        },
    )
    assert bad_utr_resp.status_code == 200
    assert bad_utr_resp.json()["status"] == "FAILED"
    assert "12-digit numeric" in bad_utr_resp.json()["message"]

    # 3. Test short UTR (8 digits)
    short_utr_resp = client.post(
        "/api/payments/verify-upi",
        json={
            "payment_id": payment_id,
            "order_id": order_id,
            "utr_reference": "12345678",
        },
    )
    assert short_utr_resp.json()["status"] == "FAILED"

    # 4. Test valid 12-digit UTR
    valid_utr_resp = client.post(
        "/api/payments/verify-upi",
        json={
            "payment_id": payment_id,
            "order_id": order_id,
            "utr_reference": "202607159841",
        },
    )
    assert valid_utr_resp.status_code == 200
    assert valid_utr_resp.json()["status"] == "SUCCESS"
    assert "verified successfully" in valid_utr_resp.json()["message"]


def test_razorpay_hmac_sha256_cryptographic_verification():
    # 1. Create order & intent
    ord_resp = client.post(
        "/api/orders",
        json={
            "business_name": "Apex Diagnostic Labs",
            "bundle_name": "Udyam Professional",
            "monthly_charge_inr": 2499,
        },
    )
    order_id = ord_resp.json()["order_id"]

    intent = client.post(
        "/api/payments/create-intent",
        json={"order_id": order_id, "amount_inr": 2499.0},
    ).json()
    payment_id = intent["payment_id"]
    rzp_order_id = intent["razorpay_order_id"]

    rzp_payment_id = "pay_test_019283849182"
    msg = f"{rzp_order_id}|{rzp_payment_id}".encode("utf-8")
    valid_signature = hmac.new(
        RAZORPAY_KEY_SECRET.encode("utf-8"),
        msg,
        hashlib.sha256,
    ).hexdigest()

    # 2. Test forged signature
    bad_rzp = client.post(
        "/api/payments/verify-razorpay",
        json={
            "payment_id": payment_id,
            "order_id": order_id,
            "razorpay_order_id": rzp_order_id,
            "razorpay_payment_id": rzp_payment_id,
            "razorpay_signature": "forged_malicious_signature_hex",
        },
    )
    assert bad_rzp.json()["status"] == "FAILED"
    assert "signature mismatch" in bad_rzp.json()["message"]

    # 3. Test valid cryptographic signature
    good_rzp = client.post(
        "/api/payments/verify-razorpay",
        json={
            "payment_id": payment_id,
            "order_id": order_id,
            "razorpay_order_id": rzp_order_id,
            "razorpay_payment_id": rzp_payment_id,
            "razorpay_signature": valid_signature,
        },
    )
    assert good_rzp.status_code == 200
    assert good_rzp.json()["status"] == "SUCCESS"


def test_telecom_logistics_event_bus_and_whatsapp_dispatch():
    # 1. Create order
    ord_resp = client.post(
        "/api/orders",
        json={
            "business_name": "Vindhya Tours Gwalior",
            "bundle_name": "Udyam Secure Edge",
            "monthly_charge_inr": 7999,
        },
    )
    order_id = ord_resp.json()["order_id"]

    # 2. Trigger dispatch
    disp_resp = client.post(f"/api/logistics/{order_id}/dispatch")
    assert disp_resp.status_code == 200
    data = disp_resp.json()

    assert "BD-AIRTEL-" in data["awb_number"]
    assert data["carrier_name"] == "BlueDart Express Surface Priority"
    assert "Airtel Logistics Hub" in data["courier_hub"]
    assert "Rajesh Kumar" in data["field_engineer_name"]
    assert "+91 98765 43210" in data["field_engineer_phone"]
    assert "https://wa.me/" in data["whatsapp_dispatch_link"]
    assert "bluedart.com/tracking?awb=" in data["tracking_url"]

    # 3. Query logistics GET endpoint
    get_disp = client.get(f"/api/logistics/{order_id}")
    assert get_disp.status_code == 200
    assert get_disp.json()["awb_number"] == data["awb_number"]


def test_sqlite_wal_foreign_key_auto_provisioning_on_specimen_order():
    """Verifies that an ad-hoc or specimen order ID (e.g. from frontend demo mode)
    never triggers a SQLite foreign key crash when creating payment intents or dispatches."""
    specimen_id = f"SPECIMEN_ADHOC_{uuid.uuid4().hex[:6]}"

    # 1. Create payment intent directly for unseeded order
    intent_resp = client.post(
        "/api/payments/create-intent",
        json={"order_id": specimen_id, "amount_inr": 2499.0, "payment_method": "UPI_INTENT"},
    )
    assert intent_resp.status_code == 200
    intent_data = intent_resp.json()
    assert intent_data["order_id"] == specimen_id
    assert "PAY-AIRTEL-" in intent_data["payment_id"]

    # 2. Trigger dispatch directly for unseeded order
    disp_resp = client.post(f"/api/logistics/{specimen_id}/dispatch")
    assert disp_resp.status_code == 200
    disp_data = disp_resp.json()
    assert disp_data["order_id"] == specimen_id
    assert "BD-AIRTEL-" in disp_data["awb_number"]
