import re

with open("backend/app/services/advisor_agent.py", "r", encoding="utf-8") as f:
    code = f.read()

# Let's inspect where process_turn starts and where it builds profile for CPQ
turn_start_marker = "        # Attempt Gemini LLM enhancement for conversational nuances\n        gemini_result = self._extract_slots_with_gemini("
cpq_start_marker = "        # Slots are complete: Build user profile for deterministic CPQ"

idx_start = code.find(turn_start_marker)
idx_cpq = code.find(cpq_start_marker)

if idx_start == -1 or idx_cpq == -1:
    print(f"Indices not found! start={idx_start}, cpq={idx_cpq}")
    exit(1)

# Replacement block for lines between gemini call and CPQ execution
replacement = '''        # Attempt Gemini LLM enhancement for conversational nuances
        gemini_result = self._extract_slots_with_gemini(
            user_message, slots, language_code=language_code, script_mode=script_mode
        )
        if gemini_result:
            slots, gemini_latin, gemini_native, gemini_tts = gemini_result
        else:
            gemini_latin, gemini_native, gemini_tts = None, None, None

        clean_msg = user_message.strip().lower()
        has_indic_script = bool(re.search(r"[\u0900-\u0D7F]", user_message))
        effective_script = script_mode or ("native" if has_indic_script else "latin")

        # Detect active language
        active_lang = language_code or "en"
        if re.search(r"[\u0C00-\u0C7F]", user_message) or re.search(r"\\b(bagunnara|bagunara|ela\\s*unnaru|ela\\s*unnav|namaskaram|namasthe|kavali|kavala|enti|eppudu|undi|ledu|meeru)\\b", clean_msg):
            active_lang = "te"
        elif re.search(r"[\u0B80-\u0BFF]", user_message) or re.search(r"\\b(vanakkam|eppadi\\s*iruk|nalama|sollunga|irukku|illa|venum|ungalukku)\\b", clean_msg):
            active_lang = "ta"
        elif re.search(r"[\u0980-\u09FF]", user_message) or re.search(r"\\b(nomoshkar|kemon\\s*ac|bhalo|lagbe|nei|apnar)\\b", clean_msg):
            active_lang = "bn"
        elif re.search(r"[\u0A80-\u0AFF]", user_message) or re.search(r"\\b(kem\\s*cho|majama|tamare|joie|nathi)\\b", clean_msg):
            active_lang = "gu"
        elif re.search(r"\\b(kase\\s*ahat|pahije|ahe|nahi|tumhi)\\b", clean_msg):
            active_lang = "mr"
        elif re.search(r"[\u0C80-\u0CFF]", user_message) or re.search(r"\\b(namaskara|hegidd|hegiddira|beku|illa|nimma)\\b", clean_msg):
            active_lang = "kn"
        elif re.search(r"[\u0D00-\u0D7F]", user_message) or re.search(r"\\b(namaskaram|sukhamano|sukham\\s*anu|venam|illa|ningal)\\b", clean_msg):
            active_lang = "ml"
        elif re.search(r"[\u0B00-\u0B7F]", user_message) or re.search(r"\\b(kemiti\\s*ach|bhalare|darkar|nahin|apana)\\b", clean_msg):
            active_lang = "or"
        elif re.search(r"[\u0900-\u097F]", user_message) or re.search(r"\\b(kaise\\s*ho|kya\\s*haal|sab\\s*theek|bhai|bhaiya|chahiye|aapka)\\b", clean_msg):
            active_lang = "hi"

        is_foreign = bool(re.search(r"^(hola|bonjour|ciao|aloha|hallo|salut|wie\\s*gehts|que\\s*tal|konnichiwa|privet|merhaba|sawasdee)\\b", clean_msg))
        is_unrelated = bool(re.search(r"\\b(recipe|biryani|butter\\s*chicken|cook|weather|monsoon|rain|poem|movie|sci-fi|python|binary\\s*search|code|joke|capital\\s*of|capital\\s*city|who\\s*won)\\b", clean_msg))
        is_terse = clean_msg in {"internet", "broadband", "plans", "price", "how much", "speed", "enterprise", "connection", "quote", "airtel"}
        is_greeting = bool(re.search(r"^(hey|hi|hello|whats\\s*up|what\\'s\\s*up|good\\s*(morning|evening|afternoon)|yo|sup|bhai|bhaiya)\\b", clean_msg)) or bool(re.search(r"\\b(bagunnara|bagunara|ela\\s*unnaru|ela\\s*unnav|namaskaram|namasthe|vanakkam|eppadi\\s*iruk|kemon\\s*ac|kem\\s*cho|kase\\s*ahat|hegidd|sukhamano|kemiti\\s*ach|kaise\\s*ho|kya\\s*haal|namaste|నమస్కారం|నమస్తే|బాగున్నారా|வணக்கம்|நமஸ்கார்|নমস্কার|નમસ્તે|नमस्कार|ನಮಸ್ಕಾರ|നമസ്കാരം|ନମସ୍କାର)\\b", clean_msg))

        # IF GEMINI LIVE RESPONSE AVAILABLE & SLOTS NOT READY FOR QUOTE: USE LIVE LLM
        if gemini_latin and gemini_native and (not slots.is_complete or is_foreign or is_unrelated or is_greeting or is_terse):
            pure_latin, pure_native = ensure_dual_scripts(gemini_latin, gemini_native, active_lang)
            user_lat, user_nat = self._dualize_user_message(user_message, active_lang, effective_script)
            return AdvisorResponse(
                slots=slots,
                quote=None,
                recommended_skus=[],
                display_markdown=pure_latin if effective_script == "latin" else pure_native,
                spoken_tts_text=gemini_tts or (pure_latin if effective_script == "latin" else pure_native),
                next_suggested_prompts=[
                    "I run a Kirana store in Tier 2 with no GST",
                    "We are a CA office in Mumbai with GST",
                    "We have a factory in Surat with 30 staff",
                ],
                display_latin=pure_latin,
                display_native=pure_native,
                user_latin=user_lat,
                user_native=user_nat,
            )

        # DETERMINISTIC HUMAN-LIKE FALLBACK ENGINE (when Gemini is unavailable, offline, or pytest)
        if not slots.is_complete or is_foreign or is_unrelated or is_greeting or is_terse:
            f_latin, f_native, f_tts = self._generate_human_fallback(
                user_message, clean_msg, active_lang, effective_script, slots,
                is_foreign=is_foreign, is_unrelated=is_unrelated, is_terse=is_terse, is_greeting=is_greeting
            )
            pure_latin, pure_native = ensure_dual_scripts(f_latin, f_native, active_lang)
            user_lat, user_nat = self._dualize_user_message(user_message, active_lang, effective_script)
            return AdvisorResponse(
                slots=slots,
                quote=None,
                recommended_skus=[],
                display_markdown=pure_latin if effective_script == "latin" else pure_native,
                spoken_tts_text=f_tts or (pure_latin if effective_script == "latin" else pure_native),
                next_suggested_prompts=[
                    "I run a Kirana store in Tier 2 with no GST",
                    "We are a CA office in Mumbai with GST",
                    "We have a factory in Surat with 30 staff",
                ],
                display_latin=pure_latin,
                display_native=pure_native,
                user_latin=user_lat,
                user_native=user_nat,
            )

'''

code = code[:idx_start] + replacement + code[idx_cpq:]

with open("backend/app/services/advisor_agent.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated process_turn to use live Gemini LLM + human fallback engine.")
