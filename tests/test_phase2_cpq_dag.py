from __future__ import annotations

import time
import pytest

from backend.app.db.registry import get_registry
from backend.app.models.schemas import CartItem, UserProfile
from backend.app.services.cpq_engine import (
    BASE_CONNECTIVITY_SKUS,
    CPQEngine,
    DependencyLockError,
)


@pytest.fixture
def cpq() -> CPQEngine:
    return CPQEngine(get_registry())


def test_gstin_firewall_blocks_gst_skus_for_non_gst_users(cpq: CPQEngine):
    non_gst_user = UserProfile(
        segment="micro",
        city_tier=2,
        employee_count=4,
        num_sites=1,
        has_gstin=False,
        detected_needs=["pos_upi_uptime"],
    )

    eligible = cpq.filter_eligible_products(non_gst_user)
    eligible_ids = {sku.product_id for sku in eligible}

    # Verify no GST-mandatory SKUs are offered
    for sku in eligible:
        assert not sku.requires_gstin, f"Non-GST user must not receive GST-mandatory SKU {sku.product_id} ({sku.product_name})"

    # Specific checks
    assert "P03" not in eligible_ids  # Biz Fibre 1G requires GSTIN
    assert "P05" not in eligible_ids  # Leased line requires GSTIN
    assert "P10" not in eligible_ids  # SD-WAN requires GSTIN
    assert "P12" not in eligible_ids  # SIP requires GSTIN
    assert "P21" not in eligible_ids  # Managed Firewall requires GSTIN

    # Must include non-GST options
    assert "P01" in eligible_ids or "P04" in eligible_ids


def test_dag_dependency_validation_and_lock_error(cpq: CPQEngine):
    # P09 (Backup 4G Failover) requires one of P01|P02|P03|P05|P06
    orphan_cart = [CartItem(product_id="P09", quantity=1)]

    is_valid, locks = cpq.check_dependencies(orphan_cart)
    assert not is_valid, "Cart with orphan P09 without base connectivity must be invalid"
    assert len(locks) == 1
    assert locks[0].missing is True
    assert "P09" == locks[0].dependent_sku

    # Strict calculation must raise DependencyLockError
    with pytest.raises(DependencyLockError) as exc_info:
        cpq.calculate_commercials(orphan_cart, strict_dag=True)
    assert "Cart violates DAG dependencies" in str(exc_info.value)

    # Adding valid base connectivity P01 should satisfy dependency
    valid_cart = [
        CartItem(product_id="P01", quantity=1),
        CartItem(product_id="P09", quantity=1),
    ]
    is_valid_now, locks_now = cpq.check_dependencies(valid_cart)
    assert is_valid_now, "Cart with P01 + P09 must be valid"
    assert all(not lock.missing for lock in locks_now)

    comms = cpq.calculate_commercials(valid_cart, strict_dag=True)
    assert comms.net_mrc_inr > 0
    assert comms.guaranteed_sla_days == 5  # max(P01: 5, P09: 3)


def test_bundle_discount_and_otc_waiver(cpq: CPQEngine):
    # Build 3-category cart:
    # 1. Connectivity: P01 (₹999)
    # 2. Security: P22 (₹399, Wi-Fi)
    # 3. Cloud: P18 (₹299, Website)
    # Gross MRC = 999 + 399 + 299 = 1697
    cart = [
        CartItem(product_id="P01", quantity=1),
        CartItem(product_id="P22", quantity=1),
        CartItem(product_id="P18", quantity=1),
    ]

    comms = cpq.calculate_commercials(cart, contract_months=12)
    assert comms.gross_mrc_inr == 999 + 399 + 299
    # 3 categories get 10% bundle discount
    expected_discount = int(comms.gross_mrc_inr * 0.10)
    assert comms.bundle_discount_inr == expected_discount
    assert comms.net_mrc_inr == comms.gross_mrc_inr - expected_discount
    # SLA must be max install days
    assert comms.guaranteed_sla_days == max(5, 3, 1)


def test_reverse_budget_optimizer_dag_compliance(cpq: CPQEngine):
    user = UserProfile(
        segment="micro",
        city_tier=2,
        employee_count=3,
        num_sites=1,
        has_gstin=False,
        detected_needs=["pos_upi_uptime", "cctv_surveillance"],
    )

    # Warm-up pass to eliminate Python cold-import overhead
    cpq.optimize_budget(user, max_monthly_budget=1500)

    test_budgets = [1500, 2500, 6000, 15000]

    for budget in test_budgets:
        start = time.perf_counter()
        result = cpq.optimize_budget(user, max_monthly_budget=budget)
        elapsed_ms = (time.perf_counter() - start) * 1000.0

        # Optimizer execution must be sub-millisecond (< 5ms upper bound)
        assert elapsed_ms < 5.0, f"Optimizer took {elapsed_ms:.2f}ms for budget {budget}"

        # Result checks
        assert result.commercials.net_mrc_inr <= budget, f"Net MRC {result.commercials.net_mrc_inr} exceeded budget {budget}"
        assert len(result.selected_skus) >= 1

        # Must anchor at least one base connectivity SKU or valid base
        has_base = any(sku in BASE_CONNECTIVITY_SKUS or sku in {"P07", "P08"} for sku in result.selected_skus)
        assert has_base, f"Budget {budget} resulted in orphan cart without base connectivity: {result.selected_skus}"

        # All items in result must be valid DAG without missing dependencies
        cart_items = [CartItem(product_id=s) for s in result.selected_skus]
        is_valid, locks = cpq.check_dependencies(cart_items)
        assert is_valid, f"Budget optimizer produced invalid DAG for budget {budget}: {locks}"


def test_gstin_firewall_reversal_for_registered_businesses(cpq: CPQEngine):
    gst_user = UserProfile(
        segment="mfg",
        city_tier=1,
        employee_count=25,
        num_sites=2,
        has_gstin=True,
        detected_needs=["dedicated_ill", "cybersecurity"],
    )

    eligible = cpq.filter_eligible_products(gst_user)
    eligible_ids = {sku.product_id for sku in eligible}

    # Leased lines and managed firewall must now be accessible
    assert "P05" in eligible_ids or "P06" in eligible_ids  # ILL 20 or 100
    assert "P21" in eligible_ids  # Managed firewall
