import re

with open("backend/app/services/advisor_agent.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update imports
old_imp = """try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False"""

new_imp = """import urllib.request
try:
    from google import genai
    GENAI_AVAILABLE = True
except Exception:
    GENAI_AVAILABLE = False"""

code = code.replace(old_imp, new_imp, 1)

# 2. Add helper method _select_skus_for_slots
helper_fn = '''
    def _select_skus_for_slots(self, slots: MSMEProfileSlots) -> list[str]:
        """Determines best base plan and compatible add-ons based on profile slots."""
        segment = slots.segment or "micro"
        tier = slots.city_tier or 2
        has_gst = bool(slots.has_gstin)
        needs = set(slots.detected_needs)

        if segment == "mfg":
            base = "P05" if has_gst else "P01"
        elif segment in {"prof", "multi"}:
            base = "P02"
        elif segment == "micro":
            base = "P04"  # 5G AirFiber for micro
        else:
            base = "P01"

        skus = [base]
        if "pos_upi_uptime" in needs:
            skus.append("P09")
        if "whatsapp_catalogue" in needs:
            skus.append("P15")
        if "cloud_email" in needs:
            skus.append("P16")
        if "cctv_surveillance" in needs:
            skus.append("P23")
        if "guest_wifi" in needs:
            skus.append("P22")
        return skus
'''

# 3. Add _call_gemini_api and _consult_gemini
gemini_methods = '''
    def _call_gemini_api(self, prompt: str, timeout: float = 6.0) -> Optional[dict]:
        """Direct HTTP REST call to Google Gemini API (bypassing SDK packaging issues)."""
        if not self.api_key or os.environ.get("PYTEST_CURRENT_TEST"):
            return None

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.7,
            },
        }
        data_bytes = json.dumps(payload).encode("utf-8")
        models = [
            "gemini-flash-lite-latest",
            "gemini-2.5-flash-lite",
            "gemini-flash-latest",
        ]

        for mod in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{mod}:generateContent?key={self.api_key}"
            try:
                req = urllib.request.Request(
                    url,
                    data=data_bytes,
                    headers={"Content-Type": "application/json"},
                )
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    if resp.status == 200:
                        body = json.loads(resp.read().decode("utf-8"))
                        text = body["candidates"][0]["content"]["parts"][0]["text"]
                        return json.loads(text)
            except Exception as e:
                logging.warning("Gemini REST model %s failed: %s", mod, e)
                continue
        return None

    def _consult_gemini(
        self,
        text: str,
        existing_slots: Optional[MSMEProfileSlots] = None,
        language_code: Optional[str] = None,
        script_mode: Optional[str] = None,
        history: Optional[list[dict[str, str]]] = None,
    ) -> Optional[dict]:
        """Consults live Gemini LLM with complete Project Udyam Enterprise Knowledge Base."""
        history_context = ""
        if history:
            recent_turns = [f"{turn.get('role', 'user')}: {turn.get('content', '')}" for turn in history[-4:]]
            history_context = "RECENT CONVERSATION HISTORY:\\n" + "\\n".join(recent_turns) + "\\n\\n"

        current_profile_str = ""
        if existing_slots:
            current_profile_str = (
                f"CURRENT USER PROFILE: Segment: {existing_slots.segment or 'unknown'}, "
                f"City Tier: {existing_slots.city_tier or 'unknown'}, "
                f"Staff: {existing_slots.employee_count or 'unknown'}, "
                f"GSTIN: {existing_slots.has_gstin}, "
                f"Budget: ₹{existing_slots.monthly_budget_cap or 'unknown'}/mo, "
                f"Needs: {existing_slots.detected_needs}\\n\\n"
            )

        prompt = f"""You are the principal Multilingual AI Enterprise Telecom Advisor for Project Udyam Digital (Accel Telecom / Airtel Business).
You are a warm, witty, highly knowledgeable human consultant—NOT an automated form or robotic IVR!

OUR ENTERPRISE PRODUCT CATALOGUE & KNOWLEDGE BASE:
1. Base Connectivity:
   - Biz 5G AirFiber 100 (P04): ₹1,199/month, 100 Mbps, 3-day SLA, wireless 5G antenna, zero road-digging delay, ideal for retail shops & clinics in Tier 1-2.
   - Biz Fibre 100 (P01): ₹1,099/month, 100 Mbps symmetric, 4-day SLA, physical optical fiber, rock-solid stability.
   - Biz Fibre 300 (P02): ₹1,699/month, 300 Mbps symmetric, 4-day SLA, high bandwidth for clinics, CA firms, 10+ devices.
   - Biz Fibre 1G (P03): ₹3,999/month, 1 Gbps symmetric, high-throughput commercial fiber.
   - Biz Leased Line 100 (P05): ₹6,500/month, 1:1 dedicated, 99.95% uptime SLA, sub-5ms latency.
   - Biz Leased Line 1G (P06): ₹14,999/month, 1:1 dedicated, mission-critical factory automation.
2. Value-Added Add-ons:
   - 4G LTE Auto-Failover (P09): ₹299/mo, automatic instant switchover during fiber cuts, keeps UPI/POS active.
   - Secure Wi-Fi with Guest Network (P22): ₹199/mo, isolates customer Wi-Fi from billing/UPI.
   - Airtel Soundbox (P13): ₹149/mo, instant voice alerts for UPI payment confirmations.
   - Cloud AI CCTV (P23): ₹399/mo, 30-day offsite cloud recording, theft deterrence.
   - Static IPv4 (P08): ₹299/mo, fixed IP for billing servers, EMR software, remote access.
   - Google Workspace (P16): ₹125/user/mo, branded business email & Cloud Drive.
3. Commercial Terms:
   - 12-month agreement: 100% Setup Fee (OTC) is WAIVED (₹0 upfront!).
   - Multi-category discounts: 5% off for 2 categories, 10% for 3, 15% for 4+.
4. Regulatory & Compliance:
   - Under Indian law, MSMEs with turnover under ₹40 Lakhs are legally GST-exempt. Udyam Registration is 100% legally sufficient for enterprise telecom connection.
   - DPDP Act 2023: 12-digit national IDs are masked in-memory immediately upon ingestion.

{history_context}{current_profile_str}CURRENT USER MESSAGE: "{text}"
Language code: {language_code or 'auto'}
Script mode: {script_mode or 'auto'}

INSTRUCTIONS FOR YOUR CONVERSATIONAL RESPONSE:
1. Chat NATURALLY like Gemini: warm, sharp, conversational, empathetic, and insightful.
2. NEVER regurgitate a generic, rigid, canned questionnaire or bullet-point form letter.
3. If the user asks for COMPARISON (e.g. "compare multiple", "is it only one?", "what are other options?", "vs"):
   - Enthusiastically acknowledge that there are multiple great options!
   - Compare 2 to 3 distinct practical configurations (e.g. Wireless AirFiber vs Fixed Fiber vs Added Failover/Wi-Fi), clearly explaining prices, setup times, and real-world advantages.
4. If the user asks ANY question, answer it directly and conversationally with accurate telecom advice.
5. If the user greets or jokes, respond with warmth and natural wit, then smoothly connect back to their business connectivity.
6. Provide:
   - "display_latin": Natural conversational markdown reply in English alphabet.
   - "display_native": Corresponding natural response in authentic native Indic script (Telugu/Hindi/Tamil etc.).
   - "spoken_tts": Plain-text conversational audio summary (1-2 sentences, zero markdown symbols like *, #, []).
   - "recommended_skus": list of 1 to 4 product IDs matching the best plan discussed (e.g. ["P04", "P22"] or ["P01", "P09"]).
   - Extract business profile slots if mentioned or implied.

Return STRICTLY valid JSON:
{{
  "display_latin": "Conversational markdown in English",
  "display_native": "Conversational markdown in native Indic script",
  "spoken_tts": "Conversational plain text voice readout",
  "recommended_skus": ["P04", "P22"],
  "segment": "micro" | "prof" | "multi" | "mfg" | null,
  "city_tier": 1 | 2 | 3 | null,
  "employee_count": integer or null,
  "num_sites": integer or null,
  "has_gstin": true | false | null,
  "detected_needs": ["broadband", "wifi", ...],
  "monthly_budget_cap": integer or null,
  "next_suggested_prompts": ["Suggestion 1", "Suggestion 2", "Suggestion 3"]
}}"""
        return self._call_gemini_api(prompt)
'''

# Replace old _extract_slots_with_gemini
extract_gemini_regex = r"    def _extract_slots_with_gemini\(.*?\n    def extract_slots"
new_methods_block = gemini_methods + helper_fn + "\n    def extract_slots"
code = re.sub(extract_gemini_regex, new_methods_block, code, flags=re.DOTALL)

with open("backend/app/services/advisor_agent.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated imports and added Gemini REST / helper methods in advisor_agent.py")
