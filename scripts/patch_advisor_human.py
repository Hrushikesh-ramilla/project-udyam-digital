# Script to patch backend/app/services/advisor_agent.py with the human conversational engine
import re

with open("backend/app/services/advisor_agent.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update _extract_slots_with_gemini
old_gemini_func_start = "    def _extract_slots_with_gemini("
old_gemini_func_end = "    def extract_slots("

idx1 = code.find(old_gemini_func_start)
idx2 = code.find(old_gemini_func_end)

if idx1 == -1 or idx2 == -1:
    print("Could not find _extract_slots_with_gemini boundaries!")
    exit(1)

new_gemini_func = '''    def _extract_slots_with_gemini(
        self,
        text: str,
        existing_slots: Optional[MSMEProfileSlots] = None,
        language_code: Optional[str] = None,
        script_mode: Optional[str] = None,
    ) -> Optional[tuple[MSMEProfileSlots, Optional[str], Optional[str], Optional[str]]]:
        """Tier 1: Live Multimodal LLM slot-extraction and natural conversational response via Gemini API."""
        if os.environ.get("PYTEST_CURRENT_TEST") or not self.client:
            return None

        prompt = f"""You are the principal Multilingual AI Enterprise Telecom Advisor for Project Udyam Digital (Accel Telecom / Airtel Business).
You are a warm, witty, charismatic, and highly intelligent human advisor—NOT a robotic form filler or IVR!

User message: "{text}"
Language code: {language_code or 'auto'}
Preferred Script mode: {script_mode or 'auto'}

GUIDELINES FOR YOUR CONVERSATIONAL RESPONSE:
1. NEVER dump a generic, canned, bullet-point questionnaire or repetitive template.
2. If the user greets in any language (e.g. "hola", "bonjour", "namaste", "bagunnara"), warmly acknowledge their greeting in that language or cultural style with genuine hospitality.
3. If the user asks something off-topic (e.g. recipe, weather, movie, joke, poetry, coding), respond with witty charm, playful personality, and a natural chuckle, then seamlessly ask if they run a business (like a cafe, studio, tech firm) that needs blazing fiber broadband.
4. If the user gives terse or ambiguous input (e.g. "internet", "price", "speed"), respond with high energy and ask 1 single natural, friendly question about their setup.
5. If the user writes in Romanized Indic (e.g. Tenglish, Hinglish, Tanglish like "bagunnara ela unnaru nenu kotha business start chesthunna"), respond naturally in that EXACT conversational style!
6. Generate both:
   - "display_latin": Natural conversational markdown reply in pure English alphabet (Latin characters only, zero Indic script characters).
   - "display_native": The corresponding natural response in authentic native Indic script (or English if foreign/unrelated).
   - "spoken_tts": A short, friendly 1-2 sentence voice TTS version without markdown symbols.
7. Extract business slots if mentioned (segment, city_tier, employee_count, num_sites, has_gstin, detected_needs, monthly_budget_cap).

Return STRICTLY valid JSON:
{{
  "segment": "micro" | "prof" | "multi" | "mfg" | null,
  "city_tier": 1 | 2 | 3 | null,
  "employee_count": integer or null,
  "num_sites": integer or null,
  "has_gstin": true | false | null,
  "detected_needs": ["broadband", "wifi", "calling", "cloud", "security", "cctv", "iot"],
  "monthly_budget_cap": integer or null,
  "display_latin": "Conversational markdown response in English alphabet",
  "display_native": "Conversational markdown response in native Indic script",
  "spoken_tts": "Natural plain text voice response"
}}"""
        try:
            def _call():
                for mod in ["gemini-flash-lite-latest", "gemini-flash-latest"]:
                    try:
                        return self.client.models.generate_content(
                            model=mod,
                            contents=prompt,
                            config={"response_mime_type": "application/json"}
                        )
                    except Exception as e:
                        logging.warning("Gemini model %s failed: %s", mod, e)
                        continue
                return None

            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            try:
                future = executor.submit(_call)
                res = future.result(timeout=4.0)
            finally:
                executor.shutdown(wait=False, cancel_futures=True)

            if not res or not res.text:
                return None

            raw_text = res.text.strip()
            data = json.loads(raw_text)

            slots = existing_slots.model_copy() if existing_slots else MSMEProfileSlots()
            if not slots.segment and data.get("segment"):
                slots.segment = str(data["segment"]).lower()
            if not slots.city_tier and data.get("city_tier"):
                slots.city_tier = int(data["city_tier"])
            if not slots.employee_count and data.get("employee_count"):
                slots.employee_count = int(data["employee_count"])
            if not slots.num_sites and data.get("num_sites"):
                slots.num_sites = int(data["num_sites"])
            if slots.has_gstin is None and data.get("has_gstin") is not None:
                slots.has_gstin = bool(data["has_gstin"])
            if data.get("detected_needs"):
                existing_needs = set(slots.detected_needs)
                for n in data["detected_needs"]:
                    existing_needs.add(str(n).lower())
                slots.detected_needs = list(existing_needs)
            if not slots.monthly_budget_cap and data.get("monthly_budget_cap"):
                slots.monthly_budget_cap = int(data["monthly_budget_cap"])

            # Validate missing slots
            missing = []
            if not slots.segment:
                missing.append("business_type")
            if not slots.city_tier:
                missing.append("city_or_tier")
            if slots.has_gstin is None:
                missing.append("gstin_status")
            slots.is_complete = len(missing) == 0
            slots.missing_slots = missing

            disp_lat = data.get("display_latin") or data.get("display_markdown")
            disp_nat = data.get("display_native")
            spoken = data.get("spoken_tts")

            return slots, disp_lat, disp_nat, spoken
        except Exception as e:
            logging.info("Gemini slot extraction unavailable (%s); using deterministic symbolic fallback.", e)
            return None

'''

code = code[:idx1] + new_gemini_func + code[idx2:]

with open("backend/app/services/advisor_agent.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated _extract_slots_with_gemini in advisor_agent.py")
