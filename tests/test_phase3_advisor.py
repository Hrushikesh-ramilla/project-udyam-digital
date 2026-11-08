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
    assert res_latin.display_latin is not None
    assert res_latin.display_native is not None
    assert res_latin.user_latin is not None
    assert res_latin.user_native is not None

    # 2. Test Telugu in Native Script ("నమస్కారం బాగున్నారా")
    res_native = advisor.process_turn("నమస్కారం బాగున్నారా", script_mode="native")
    assert "బాగున్నాను" in res_native.display_markdown or "నమస్కారం" in res_native.display_markdown
    assert res_native.display_latin is not None
    assert res_native.display_native is not None

    # 3. Test slot extraction from Romanized query ("hyderabad lo 4 staff clinic undi, budget 2500")
    res_slots = advisor.process_turn("hyderabad lo 4 staff clinic undi, budget 2500", script_mode="latin")
    assert res_slots.slots.segment == "prof"
    assert res_slots.slots.city_tier == 1  # Hyderabad is Tier 1
    assert res_slots.slots.employee_count == 4


def test_advisor_comparison_query(advisor: AdvisorAgent):
    from backend.app.models.schemas import MSMEProfileSlots

    prev = MSMEProfileSlots(
        segment="micro",
        city_tier=2,
        employee_count=3,
        has_gstin=False,
        monthly_budget_cap=1500,
        is_complete=True,
    )

    # When user asks to compare between multiple plans instead of accepting just one
    response = advisor.process_turn("can u compare between multiple its not like only oie right", previous_slots=prev)

    # Must provide comparison between options, not just dump a single rigid bundle template
    assert "Option 1" in response.display_markdown or "options" in response.display_markdown.lower() or "compare" in response.display_markdown.lower()
    assert response.quote is not None
    assert len(response.recommended_skus) > 0
    assert response.spoken_tts_text is not None
    assert "*" not in response.spoken_tts_text
    assert "#" not in response.spoken_tts_text


def test_romanized_telugu_query_preserves_language(advisor: AdvisorAgent):
    """Verifies that Romanized Telugu queries (Tenglish) trigger natural Romanized Telugu
    in 'display_latin' (English Words mode) and authentic Telugu script in 'display_native'.
    """
    import re

    query = "ekkuva money karchupettalanukovatle minimum enthalo ayipothado cheppandi"

    # 1. Romanized / English Words mode (script_mode='latin')
    res_latin = advisor.process_turn(query, script_mode="latin")
    assert res_latin.display_latin is not None
    assert res_latin.display_native is not None
    assert res_latin.display_markdown == res_latin.display_latin

    # Verify response is in Romanized Telugu (not standard English)
    lat_lower = res_latin.display_latin.lower()
    assert any(term in lat_lower for term in ["arthamaindi", "takkuva", "takkuvalo", "kavali", "cheppandi", "airfiber"])
    # Verify zero non-Latin Indic characters in Latin mode
    assert not re.search(r"[\u0900-\u0D7F]", res_latin.display_latin)

    # 2. Native Script mode (script_mode='native')
    res_native = advisor.process_turn(query, script_mode="native")
    assert res_native.display_markdown == res_native.display_native
    # Verify proper Telugu script characters are present in native output
    assert re.search(r"[\u0C00-\u0C7F]", res_native.display_native)

    # 3. Test Romanized Hindi (Hinglish) preservation
    query_hi = "zyada paise kharch nahi karna chahte minimum kitne me ho jayega bataiye"
    res_hi = advisor.process_turn(query_hi, script_mode="latin")
    assert res_hi.display_latin is not None
    hi_lower = res_hi.display_latin.lower()
    assert any(term in hi_lower for term in ["samajh", "kam", "budget", "airfiber", "bataiye"])
    assert not re.search(r"[\u0900-\u0D7F]", res_hi.display_latin)


def test_english_query_does_not_convert_to_telugu_in_native_script_mode(advisor: AdvisorAgent):
    """Verifies that English queries remain in English even when script_mode='native'
    (Issue #8: English chat turns must not turn into hardcoded Telugu).
    """
    import re

    # 1. English greeting in native script mode
    res = advisor.process_turn("Hello", language_code="en", script_mode="native")
    assert res.display_native is not None
    # Must NOT contain Telugu characters
    assert not re.search(r"[\u0C00-\u0C7F]", res.display_native)
    assert not re.search(r"[\u0C00-\u0C7F]", res.display_markdown)
    assert "Airtel" in res.display_native or "Welcome" in res.display_native or "Namaste" in res.display_native

    # 2. English query with auto language code in native script mode
    res_auto = advisor.process_turn("Hi, I want internet for my store", language_code="auto", script_mode="native")
    assert not re.search(r"[\u0C00-\u0C7F]", res_auto.display_native)


def test_simple_greeting_fast_path_latency(advisor: AdvisorAgent):
    """Verifies that basic greetings hit an instant deterministic sub-100ms fast-path."""
    import time

    start = time.time()
    res = advisor.process_turn("Hello", language_code="en")
    elapsed_ms = (time.time() - start) * 1000

    assert elapsed_ms < 100, f"Greeting latency too high: {elapsed_ms:.1f}ms"
    assert res.display_latin is not None
    assert len(res.display_latin) > 10


def test_universal_multilingual_no_language_restriction(advisor: AdvisorAgent):
    """Verifies that international queries (e.g. Spanish 'hola', French 'bonjour')
    are auto-detected and responded to in that language without inverted punctuation
    artifacts (no ¡) or restrictive disclaimers.
    """
    import re

    # 1. Spanish 'hola'
    res_es = advisor.process_turn("hola")
    assert res_es.display_latin.startswith("Hola!"), f"Expected clean Hola!, got: {res_es.display_latin[:10]}"
    assert "¡" not in res_es.display_latin, "Found unexpected inverted exclamation mark ¡"
    assert "superpower" not in res_es.display_latin.lower()
    # Native mode must not have Telugu
    assert not re.search(r"[\u0C00-\u0C7F]", res_es.display_native)

    # 2. French 'bonjour'
    res_fr = advisor.process_turn("bonjour")
    assert res_fr.display_latin.startswith("Bonjour!")
    assert not re.search(r"[\u0C00-\u0C7F]", res_fr.display_native)


def test_turn2_only_udyam_resolves_and_calculates_bundle(advisor: AdvisorAgent):
    """Verifies that answering 'only udyam' to GST question completes profile slots
    and computes the recommended bundle without repeating the question.
    """
    from backend.app.models.schemas import MSMEProfileSlots

    prev = MSMEProfileSlots(segment="micro", city_tier=1, employee_count=4)
    res = advisor.process_turn("only udyam", previous_slots=prev)

    assert res.slots.is_complete is True
    assert res.slots.has_gstin is False
    assert len(res.recommended_skus) > 0
    assert res.quote is not None
    assert "Recommended Bundle" in res.display_markdown or "Optimal" in res.display_markdown or len(res.display_markdown) > 50


def test_session_language_inertia_preserves_english_on_entity_tokens(advisor: AdvisorAgent):
    """Verifies that entity data (shop name, city like Gwalior, phone number) in an ongoing
    English session strictly preserves English and does not over-localize to Hindi.
    """
    import re
    from backend.app.models.schemas import MSMEProfileSlots

    history = [
        {"role": "user", "content": "suggest me cheapest one for my kirana shop its just me who runs the shop"},
        {"role": "assistant", "content": "Hey there! Running a kirana shop all by yourself means you need something super reliable..."},
        {"role": "user", "content": "yeah place an order for me"},
        {"role": "assistant", "content": "Awesome! Could you please confirm your shop name, installation address, and mobile number?"}
    ]
    slots = MSMEProfileSlots(segment="micro", city_tier=2, employee_count=1, has_gstin=False)

    res = advisor.process_turn("hhh shop gwalior 1234567890 number", previous_slots=slots, history=history)

    assert res.display_latin is not None
    # Must NOT have switched to Hindi / Hinglish
    hi_leak = re.findall(r"\b(aapka|aapke|aapki|hoga|hogi|hain|hai|mein|zaroorat|karna|karke|badiya|shandar|chinta|dukaan|matlab|saste|liye)\b", res.display_latin.lower())
    assert len(hi_leak) == 0, f"Leaked Hindi words in English session: {hi_leak} - full text: {res.display_latin}"
    # Must not contain Devanagari Hindi characters
    assert not re.search(r"[\u0900-\u097F]", res.display_native)


def test_session_language_switches_when_user_explicitly_speaks_hindi(advisor: AdvisorAgent):
    """Verifies that if the user explicitly switches language (e.g. typing Hindi/Hinglish),
    the advisor transitions to that language properly.
    """
    from backend.app.models.schemas import MSMEProfileSlots

    history = [
        {"role": "user", "content": "suggest me cheapest one for my kirana shop"},
        {"role": "assistant", "content": "Hey there! We have Biz 5G AirFiber 100 for you."},
    ]
    slots = MSMEProfileSlots(segment="micro", city_tier=2, employee_count=1, has_gstin=False)

    res = advisor.process_turn("bhai ab mujhe hindi me samjhao kya sasta plan hai dukan ke liye", previous_slots=slots, history=history)

    assert res.display_latin is not None
    # Should contain Hindi/Hinglish words acknowledging the request
    hi_text = res.display_latin.lower()
    assert any(w in hi_text for w in ["bhai", "aapki", "dukan", "plan", "airfiber", "sasta", "hoga", "hai"])


def test_order_intent_strictly_guides_to_cart_and_forbids_ghost_booking_codes(advisor: AdvisorAgent):
    """Verifies Issue #12: when user requests order placement, advisor must NEVER
    hallucinate fake booking IDs (e.g. AUDYAM-*) and must guide user to Dynamic Cart & Smart KYC.
    """
    import re
    from backend.app.models.schemas import MSMEProfileSlots

    slots = MSMEProfileSlots(segment="mfg", city_tier=1, employee_count=50, has_gstin=True)
    res = advisor.process_turn("YEAH PLEASE PLACE THE ORDER", previous_slots=slots)

    # Must not contain synthetic AUDYAM booking code
    assert not re.search(r"AUDYAM-\d{4}-[A-Z0-9]+", res.display_markdown, re.IGNORECASE)
    assert not re.search(r"AUDYAM-[A-Z0-9-]+", res.display_markdown, re.IGNORECASE)
    # Must explicitly direct user to the Dynamic Cart and Smart KYC
    combined_text = (res.display_markdown + " " + res.spoken_tts_text).lower()
    assert "cart" in combined_text or "kyc" in combined_text or "staged" in combined_text


def test_navigation_query_accurately_explains_cart_and_order_tracker(advisor: AdvisorAgent):
    """Verifies Issue #13: when user asks where to find or track their order in the app,
    advisor accurately references the Dynamic Cart directly below chat and Order Tracker tab.
    """
    from backend.app.models.schemas import MSMEProfileSlots

    slots = MSMEProfileSlots(segment="micro", city_tier=2, employee_count=3, has_gstin=False)
    res = advisor.process_turn("SO CAN U NAVIGATE ME WHERE I CAN SEE MY PLACED ORDER IN THIS APP", previous_slots=slots)

    combined_text = (res.display_markdown + " " + res.spoken_tts_text).lower()
    # Must refer to the Cart below or Order Tracker
    assert "cart" in combined_text or "tracker" in combined_text or "below" in combined_text
    # Must NOT hallucinate that the app dashboard is 'booting up'
    assert "booting up" not in combined_text


def test_mid_conversation_pivot_to_campus_leased_line_updates_skus(advisor: AdvisorAgent):
    """Verifies Issue #15: when user pivots mid-conversation to campus scale,
    advisor extracts P06, P08, P22 and updates recommended_skus and quote in real-time.
    """
    from backend.app.models.schemas import MSMEProfileSlots

    # Initial retail store slots
    initial_slots = MSMEProfileSlots(segment="micro", city_tier=2, employee_count=3, has_gstin=False)

    # Pivot query
    pivot_msg = "I have another college with 500 students... heavy ML work center, let's go with Biz Leased Line 1G (P06) + Static IPv4 (P08) + Secure Wi-Fi (P22)"
    res = advisor.process_turn(pivot_msg, previous_slots=initial_slots)

    assert "P06" in res.recommended_skus
    assert "P08" in res.recommended_skus or "P11" in res.recommended_skus
    assert "P22" in res.recommended_skus
    assert res.quote is not None
    assert res.quote.net_mrc_inr > 10000
