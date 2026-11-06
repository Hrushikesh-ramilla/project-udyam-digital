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


def test_romanized_latin_script_indic_flow(advisor: AdvisorAgent):
    import re
    # 1. Test Telugu in Latin/English alphabet ("bagunnara ela unnaru")
    res_latin = advisor.process_turn("bagunnara ela unnaru", script_mode="latin")
    assert "Nenu bagunnanu" in res_latin.display_markdown or "dhanyavadalu" in res_latin.display_markdown
    # Verify zero non-Latin Indic characters in Latin mode
    assert not re.search(r"[\u0900-\u0D7F]", res_latin.display_markdown)

    # 2. Test Telugu in Native Script ("నమస్కారం బాగున్నారా")
    res_native = advisor.process_turn("నమస్కారం బాగున్నారా", script_mode="native")
    assert "బాగున్నాను" in res_native.display_markdown or "నమస్కారం" in res_native.display_markdown

    # 3. Test slot extraction from Romanized query ("hyderabad lo 4 staff clinic undi, budget 2500")
    res_slots = advisor.process_turn("hyderabad lo 4 staff clinic undi, budget 2500", script_mode="latin")
    assert res_slots.slots.segment == "prof"
    assert res_slots.slots.city_tier == 1  # Hyderabad is Tier 1
    assert res_slots.slots.employee_count == 4
