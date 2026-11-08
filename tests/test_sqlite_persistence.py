from __future__ import annotations

import tempfile
from pathlib import Path
import pytest

from backend.app.db.sqlite_engine import ProductionDatabase
from backend.app.services.provisioning_tracker import ProvisioningTracker


@pytest.fixture
def temp_db() -> ProductionDatabase:
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_udyam.db"
        yield ProductionDatabase(db_path=db_path)


def test_sqlite_wal_persistence_and_cache_survival(temp_db: ProductionDatabase):
    # 1. Initialize tracker with temp WAL DB
    tracker = ProvisioningTracker(db=temp_db)

    # 2. Create order
    order = tracker.create_order(
        business_name="Maa Durga Sweets & Bakery",
        bundle_name="Udyam Vyapar Plus",
        monthly_charge_inr=1999,
        total_sla_days=4,
        partner_id="PARTNER_GWALIOR_01",
    )
    order_id = order.order_id
    assert order.current_stage_idx == 0
    assert order.milestones[0].status == "COMPLETED"
    assert order.milestones[1].status == "PENDING"

    # 3. Advance to stage 1 (Feasibility Verified)
    adv = tracker.advance_stage(order_id)
    assert adv is not None
    assert adv.current_stage_idx == 1
    assert adv.milestones[1].status == "COMPLETED"

    # 4. Wipe in-memory dictionary to simulate cold server restart
    tracker._orders.clear()
    assert len(tracker._orders) == 0

    # 5. Retrieve order - must be seamlessly rehydrated from SQLite disk
    rehydrated = tracker.get_order(order_id)
    assert rehydrated is not None
    assert rehydrated.order_id == order_id
    assert rehydrated.business_name == "Maa Durga Sweets & Bakery"
    assert rehydrated.current_stage_idx == 1
    assert rehydrated.milestones[1].status == "COMPLETED"
    assert rehydrated.milestones[1].timestamp is not None
    assert rehydrated.milestones[2].status == "PENDING"


def test_sqlite_payments_and_upi_utr_verification(temp_db: ProductionDatabase):
    # 1. Create order
    tracker = ProvisioningTracker(db=temp_db)
    order = tracker.create_order(
        business_name="Kalyan Medical Store",
        bundle_name="Udyam Professional",
        monthly_charge_inr=2499,
    )

    # 2. Record payment intent
    payment_id = "PAY_AIRTEL_982341"
    temp_db.record_payment(
        payment_id=payment_id,
        order_id=order.order_id,
        amount_inr=2499.0,
        payment_method="UPI_INTENT",
        status="PENDING",
    )

    p = temp_db.get_payment(payment_id)
    assert p is not None
    assert p["status"] == "PENDING"
    assert p["amount_inr"] == 2499.0

    # 3. Verify via 12-digit UTR bank reference
    utr = "619482019482"
    success = temp_db.verify_upi_payment(payment_id, utr)
    assert success is True

    p_verified = temp_db.get_payment(payment_id)
    assert p_verified["status"] == "SUCCESS"
    assert p_verified["utr_reference"] == utr
    assert p_verified["verified_at"] is not None
