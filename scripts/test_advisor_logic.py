import os
import re
import json
import urllib.request
import logging
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

from backend.app.db.registry import get_registry
from backend.app.services.cpq_engine import CPQEngine
from backend.app.models.schemas import MSMEProfileSlots, CartItem, UserProfile

db = get_registry()
cpq = CPQEngine(db)

def test_query(msg, prev_slots=None):
    clean_msg = msg.lower().strip()
    is_comparison = bool(re.search(
        r"\b(compare|comparison|multiple|options|alternatives|vs|other plans?|not only one|only one|another plan|different plan)\b",
        clean_msg
    ))
    print(f"Query: '{msg}' | is_comparison: {is_comparison}")

test_query("can u compare between multiple its not like only oie right")
test_query("what are the options for a clinic in mumbai")
test_query("Bhaiya, meri Jaipur mein 2 medical shops hain, total 6 staff hain. Budget 2500.")
