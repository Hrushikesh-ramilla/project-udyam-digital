import os
import re
import json
import urllib.request
import logging
from dotenv import load_dotenv

load_dotenv()

from backend.app.db.registry import get_registry
from backend.app.services.advisor_agent import AdvisorAgent
from backend.app.models.schemas import MSMEProfileSlots

advisor = AdvisorAgent(get_registry())

# Test 1: Compare query in live mode (with GEMINI_API_KEY)
prev = MSMEProfileSlots(segment="micro", city_tier=2, employee_count=3, has_gstin=False, monthly_budget_cap=1500)
res_live = advisor.process_turn("can u compare between multiple its not like only oie right", previous_slots=prev)
print("=== LIVE GEMINI COMPARISON TEST ===")
print("Recommended SKUs:", res_live.recommended_skus)
print("Quote Net MRC:", res_live.quote.net_mrc_inr if res_live.quote else None)
print("Display Latin:\n", res_live.display_latin[:300], "...")

# Test 2: Incomplete turn in deterministic test mode
os.environ["PYTEST_CURRENT_TEST"] = "test_run"
res_incomplete = advisor.process_turn("Hello, I want an internet connection.")
print("\n=== DETERMINISTIC INCOMPLETE TEST ===")
print("Slots complete:", res_incomplete.slots.is_complete)
print("Display Latin:", res_incomplete.display_latin[:100])
del os.environ["PYTEST_CURRENT_TEST"]
