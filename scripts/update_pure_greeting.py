with open('backend/app/services/advisor_agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''        is_greeting = bool(re.search(r"^(hey|hi|hello|whats\\s*up|what\\'s\\s*up|good\\s*(morning|evening|afternoon)|yo|sup|bhai|bhaiya)\\b", clean_msg)) or bool(re.search(r"\\b(bagunnara|bagunara|ela\\s*unnaru|ela\\s*unnav|namaskaram|namasthe|vanakkam|eppadi\\s*iruk|kemon\\s*ac|kem\\s*cho|kase\\s*ahat|hegidd|sukhamano|kemiti\\s*ach|kaise\\s*ho|kya\\s*haal|namaste|నమస్కారం|నమస్తే|బాగున్నారా|வணக்கம்|நமஸ்கார்|নমস্কার|નમસ્તે|नमस्कार|ನಮಸ್ಕಾರ|നമസ്കാരം|ନମସ୍କାର)\\b", clean_msg))

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
        if not slots.is_complete or is_foreign or is_unrelated or is_greeting or is_terse:'''

replacement = '''        is_greeting = bool(re.search(r"^(hey|hi|hello|whats\\s*up|what\\'s\\s*up|good\\s*(morning|evening|afternoon)|yo|sup|bhai|bhaiya)\\b", clean_msg)) or bool(re.search(r"\\b(bagunnara|bagunara|ela\\s*unnaru|ela\\s*unnav|namaskaram|namasthe|vanakkam|eppadi\\s*iruk|kemon\\s*ac|kem\\s*cho|kase\\s*ahat|hegidd|sukhamano|kemiti\\s*ach|kaise\\s*ho|kya\\s*haal|namaste|నమస్కారం|నమస్తే|బాగున్నారా|வணக்கம்|நமஸ்கార్|নমস্কার|નમસ્તે|नमस्कार|ನಮಸ್ಕಾರ|നമസ്കാരം|ନମସ୍କାର)\\b", clean_msg))
        pure_greeting = is_greeting and not slots.is_complete and not bool(slots.segment or slots.city_tier or slots.has_gstin is not None or slots.detected_needs)
        should_chat_turn = (not slots.is_complete) or is_foreign or is_unrelated or pure_greeting or is_terse

        # IF GEMINI LIVE RESPONSE AVAILABLE & SLOTS NOT READY FOR QUOTE: USE LIVE LLM
        if gemini_latin and gemini_native and should_chat_turn:
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
        if should_chat_turn:'''

assert target in text, 'Target not found in text!'
new_text = text.replace(target, replacement, 1)
with open('backend/app/services/advisor_agent.py', 'w', encoding='utf-8') as f:
    f.write(new_text)
print('Successfully updated advisor_agent.py!')
