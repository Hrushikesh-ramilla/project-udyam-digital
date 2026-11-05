from __future__ import annotations

import pytest

from backend.app.db.registry import get_registry
from backend.app.services.advisor_agent import AdvisorAgent


@pytest.fixture
def advisor() -> AdvisorAgent:
    return AdvisorAgent(get_registry())


def test_hinglish_slot_filling_and_cpq_flow(advisor: AdvisorAgent):
    user_turn = (
        "Bhaiya, meri Jaipur mein 2 medical shops hain, total 6 staff hain. "
        "Shaam ko rush time pe Jio hotspot baith jata hai toh GPay atakta hai. "
        "Mere paas Udyam hai par GST number nahi hai. Budget lagbhag 2500 rupay hai."
    )

    response = advisor.process_turn(user_turn)

    # 1. Verify Slot Extraction
    assert response.slots.is_complete is True
    assert response.slots.segment == "micro"
    assert response.slots.city_tier == 2  # Jaipur is Tier 2
    assert response.slots.num_sites == 2
    assert response.slots.employee_count == 6
    assert response.slots.has_gstin is False
    assert response.slots.monthly_budget_cap == 2500
    assert "pos_upi_uptime" in response.slots.detected_needs

    # 2. Verify Deterministic Quote
    assert response.quote is not None
    assert response.quote.net_mrc_inr <= 2500
    assert response.quote.gst_exempt_eligible is True  # Non-GST customer
    assert len(response.recommended_skus) >= 1

    # 3. Verify Zero Price Divergence
    formatted_price = f"{response.quote.net_mrc_inr:,}"
    assert formatted_price in response.display_markdown
    assert str(response.quote.net_mrc_inr) in response.spoken_tts_text

    # 4. Verify Spoken TTS Text Hygiene (Zero markdown characters)
    assert "*" not in response.spoken_tts_text
    assert "#" not in response.spoken_tts_text
    assert "[" not in response.spoken_tts_text
    assert "]" not in response.spoken_tts_text
    assert "₹" not in response.spoken_tts_text  # Replaced by 'rupaye'


def test_english_ca_firm_flow(advisor: AdvisorAgent):
    user_turn = (
        "We are a CA firm in Mumbai with 15 employees, single branch, active GSTIN. "
        "Need fast broadband and cloud email backup for our files."
    )

    response = advisor.process_turn(user_turn)

    assert response.slots.is_complete is True
    assert response.slots.segment == "prof"
    assert response.slots.city_tier == 1  # Mumbai is Tier 1
    assert response.slots.employee_count == 15
    assert response.slots.has_gstin is True
    assert "cloud_email" in response.slots.detected_needs

    assert response.quote is not None
    assert response.quote.net_mrc_inr > 0
    # Professional firm in Tier 1 gets Biz Fibre 300
    assert "P02" in response.recommended_skus


def test_incomplete_turn_prompts_clarification(advisor: AdvisorAgent):
    user_turn = "Hello, I want an internet connection."

    response = advisor.process_turn(user_turn)

    assert response.slots.is_complete is False
    assert response.quote is None
    assert len(response.slots.missing_slots) > 0
    assert "Namaste" in response.display_markdown or "clarify" in response.display_markdown
    assert len(response.next_suggested_prompts) > 0
