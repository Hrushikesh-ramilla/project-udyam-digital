from __future__ import annotations

import pytest

from backend.app.db.registry import get_registry
from backend.app.services.lead_rescue_ml import LeadRescueMLEngine
from backend.app.services.provisioning_tracker import ProvisioningTracker


@pytest.fixture
def ml_engine() -> LeadRescueMLEngine:
    return LeadRescueMLEngine(get_registry())


@pytest.fixture
def tracker() -> ProvisioningTracker:
    return ProvisioningTracker()


def test_lightgbm_lead_rescue_training_and_scoring(ml_engine: LeadRescueMLEngine):
    assert ml_engine.model is not None, "LightGBM model must be fitted on smb_leads.csv"

    # Fetch a sample dropped lead
    leads = get_registry().get_all_leads()
    dropped_leads = [l for l in leads if l.outcome.lower() == "dropped"]
    sample_lead = dropped_leads[0]

    scored = ml_engine.score_lead(sample_lead)

    assert scored.lead_id == sample_lead.lead_id
    assert 0.0 <= scored.propensity_score <= 100.0
    assert scored.priority_tier in {"HIGH", "MEDIUM", "NURTURE", "LOW"}
    assert len(scored.top_risk_factors) >= 1
    assert len(scored.next_best_action) >= 5
    assert "udyam.airtel.in" in scored.whatsapp_rescue_link


def test_rescue_cohort_ranking_and_filtering(ml_engine: LeadRescueMLEngine):
    # Fetch top rescue leads for the 56% quote leak stage
    cohort = ml_engine.get_top_rescue_leads(limit=10, stage_filter="Needs assessed")

    assert len(cohort) > 0
    # Must be sorted descending by propensity score
    scores = [item.propensity_score for item in cohort]
    assert scores == sorted(scores, reverse=True)

    for item in cohort:
        assert item.stage_reached == "Needs assessed"
        assert "Quote" in item.next_best_action or "WhatsApp" in item.next_best_action or "Interactive" in item.next_best_action


def test_provisioning_state_machine_and_partner_commission(tracker: ProvisioningTracker):
    # Create order with partner attribution (REP_402)
    order = tracker.create_order(
        business_name="Balaji Medicos",
        bundle_name="Biz 5G AirFiber 100 + Failover",
        monthly_charge_inr=2000,
        total_sla_days=4,
        partner_id="REP_402",
    )

    assert order.order_id.startswith("AIRTEL-SMB-")
    assert order.partner_id == "REP_402"
    # 15% of ₹2,000 = ₹300 commission
    assert order.partner_commission_inr == 300
    assert order.current_stage_idx == 0
    assert not order.is_activated
    assert len(order.milestones) == 6
    assert order.milestones[0].status == "COMPLETED"
    assert "Airtel Business" in order.milestones[0].whatsapp_preview

    # Advance stage to FEASIBILITY_VERIFIED
    advanced = tracker.advance_stage(order.order_id)
    assert advanced is not None
    assert advanced.current_stage_idx == 1
    assert advanced.milestones[1].status == "COMPLETED"

    # Advance through all remaining stages to activation
    for _ in range(4):
        advanced = tracker.advance_stage(order.order_id)

    assert advanced.current_stage_idx == 5
    assert advanced.is_activated is True
    assert advanced.milestones[5].status == "COMPLETED"


def test_phygital_obo_handshake_link(tracker: ProvisioningTracker):
    order = tracker.create_order(
        business_name="City Clinic",
        bundle_name="Biz Fibre 300",
        monthly_charge_inr=1500,
        partner_id="PARTNER_KOLKATA_09",
    )

    obo_link = tracker.generate_obo_handshake_link(order, "PARTNER_KOLKATA_09")
    assert "obo-approval" in obo_link
    assert order.order_id in obo_link
    assert "PARTNER_KOLKATA_09" in obo_link


def test_calibrated_propensity_distribution_and_factor_chips(ml_engine: LeadRescueMLEngine):
    """Verifies Issue #26: rescue propensity scores are calibrated across stratified tiers
    (HIGH, MEDIUM, NURTURE) with explanatory factor chips.
    """
    top_leads = ml_engine.get_top_rescue_leads(limit=50)
    assert len(top_leads) > 0

    scores = [l.propensity_score for l in top_leads]
    assert max(scores) >= 85.0
    # Must have factor chips explaining the prediction
    for l in top_leads:
        assert isinstance(l.factor_chips, list)
        assert len(l.factor_chips) <= 2
        assert l.priority_tier in {"HIGH", "MEDIUM", "NURTURE"}
        if l.propensity_score >= 80.0:
            assert l.priority_tier == "HIGH"
        elif l.propensity_score >= 60.0:
            assert l.priority_tier == "MEDIUM"
        else:
            assert l.priority_tier == "NURTURE"
