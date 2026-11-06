import re

path = 'backend/app/services/advisor_agent.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update fallback for foreign / unrelated queries
foreign_block = '''        # Non-Indic foreign languages / greetings and unrelated queries fallback
        is_foreign_greeting = bool(re.search(r"^(hola|bonjour|ciao|aloha|hallo|salut|wie\\s*gehts|que\\s*tal|konnichiwa|privet|merhaba|sawasdee)\\b", clean_msg))
        is_unrelated = bool(re.search(r"\\b(recipe|cricket|weather|poem|movie|python\\s*code|binary\\s*search|joke|capital of|how to cook|who won)\\b", clean_msg))
        if is_foreign_greeting or is_unrelated:
            resp_latin = (
                "Namaste! Welcome to Airtel Business Udyam Digital. "
                "We provide enterprise telecom, high-speed fiber broadband, and digital solutions for Indian businesses "
                "across all 10 Indic languages. Please tell us about your enterprise (e.g. retail shop, clinic, CA office, factory) "
                "and city to configure an optimal verified plan."
            )
            resp_native = (
                "నమస్కారం! ఎయిర్‌టెల్ బిజినెస్ ఉద్యమ్ డిజిటల్‌కు స్వాగతం. "
                "భారతీయ వ్యాపారాల కోసం హై-స్పీడ్ ఫైబర్, స్టాటిక్ ఐపీ మరియు క్లౌడ్ సేవలను మేము అందిస్తున్నాము. "
                "మీ వ్యాపార వివరాలను తెలపండి."
            )
            pure_latin, pure_native = ensure_dual_scripts(resp_latin, resp_native, active_lang)
            user_lat, user_nat = self._dualize_user_message(user_message, active_lang, effective_script)
            return AdvisorResponse(
                slots=slots,
                quote=None,
                recommended_skus=[],
                display_markdown=pure_latin if effective_script == "latin" else pure_native,
                spoken_tts_text="Namaste! Welcome to Airtel Business Udyam Digital. Please describe your business requirements.",
                next_suggested_prompts=[
                    "Broadband for Kirana shop",
                    "Clinic with 10 staff in Hyderabad",
                    "Factory setup in Surat",
                ],
                display_latin=pure_latin,
                display_native=pure_native,
                user_latin=user_lat,
                user_native=user_nat,
            )
'''

target_lang_detect = 'active_lang = "hi"\n'
if target_lang_detect in content and 'is_foreign_greeting' not in content:
    idx = content.find(target_lang_detect) + len(target_lang_detect)
    content = content[:idx] + "\n" + foreign_block + content[idx:]
    print("Added foreign / unrelated fallback")

# 2. Update greeting return block to pass through ensure_dual_scripts
old_greeting = '''            display_native = matched_native[0]
            display_latin = matched_latin[0]
            display_md = display_latin if effective_script == "latin" else display_native
            welcome_tts = matched_latin[1] if effective_script == "latin" else matched_native[1]
            user_latin, user_native = self._dualize_user_message(user_message, active_lang, effective_script)

            return AdvisorResponse(
                slots=slots,
                quote=None,
                recommended_skus=[],
                display_markdown=display_md,
                spoken_tts_text=welcome_tts,
                next_suggested_prompts=[
                    "I run a Kirana store in Tier 2 with no GST",
                    "We are a CA office in Mumbai with GST",
                    "We have a factory in Surat with 30 staff",
                ],
                display_latin=display_latin,
                display_native=display_native,
                user_latin=user_latin,
                user_native=user_native,
            )'''

new_greeting = '''            display_native = matched_native[0]
            display_latin = matched_latin[0]
            pure_latin, pure_native = ensure_dual_scripts(display_latin, display_native, active_lang)
            display_md = pure_latin if effective_script == "latin" else pure_native
            welcome_tts = matched_latin[1] if effective_script == "latin" else matched_native[1]
            user_latin, user_native = self._dualize_user_message(user_message, active_lang, effective_script)

            return AdvisorResponse(
                slots=slots,
                quote=None,
                recommended_skus=[],
                display_markdown=display_md,
                spoken_tts_text=welcome_tts,
                next_suggested_prompts=[
                    "I run a Kirana store in Tier 2 with no GST",
                    "We are a CA office in Mumbai with GST",
                    "We have a factory in Surat with 30 staff",
                ],
                display_latin=pure_latin,
                display_native=pure_native,
                user_latin=user_latin,
                user_native=user_native,
            )'''

if old_greeting in content:
    content = content.replace(old_greeting, new_greeting)
    print("Updated greeting return block")

# 3. Update incomplete slots block
old_incomplete = '''            prompt_latin = f"Namaste! To configure your digital plan, please tell us: {', '.join(missing_text)}."
            prompt_native = f"నమస్కారం! మీ వ్యాపారానికి తగిన ప్లాన్ ఎంచుకోవడానికి దయచేసి తెలపండి: మీ వ్యాపార రకం, నగరం మరియు జీఎస్టీ వివరాలు."
            display_md = prompt_latin if effective_script == "latin" else prompt_native
            spoken_tts = prompt_latin if effective_script == "latin" else "Namaste! Mee business details telapandi."
            user_latin, user_native = self._dualize_user_message(user_message, active_lang, effective_script)

            return AdvisorResponse(
                slots=slots,
                quote=None,
                recommended_skus=[],
                display_markdown=display_md,
                spoken_tts_text=spoken_tts,
                next_suggested_prompts=[
                    "I run a Kirana store in Tier 2 with no GST",
                    "We are a CA office in Mumbai with GST",
                    "We have a factory in Surat with 30 staff",
                ],
                display_latin=prompt_latin,
                display_native=prompt_native,
                user_latin=user_latin,
                user_native=user_native,
            )'''

new_incomplete = '''            prompt_latin = f"Namaste! To configure your digital plan, please tell us: {', '.join(missing_text)}."
            prompt_native = f"నమస్కారం! మీ వ్యాపారానికి తగిన ప్లాన్ ఎంచుకోవడానికి దయచేసి తెలపండి: మీ వ్యాపార రకం, నగరం మరియు జీఎస్టీ వివరాలు."
            pure_latin, pure_native = ensure_dual_scripts(prompt_latin, prompt_native, active_lang)
            display_md = pure_latin if effective_script == "latin" else pure_native
            spoken_tts = pure_latin if effective_script == "latin" else "Namaste! Mee business details telapandi."
            user_latin, user_native = self._dualize_user_message(user_message, active_lang, effective_script)

            return AdvisorResponse(
                slots=slots,
                quote=None,
                recommended_skus=[],
                display_markdown=display_md,
                spoken_tts_text=spoken_tts,
                next_suggested_prompts=[
                    "I run a Kirana store in Tier 2 with no GST",
                    "We are a CA office in Mumbai with GST",
                    "We have a factory in Surat with 30 staff",
                ],
                display_latin=pure_latin,
                display_native=pure_native,
                user_latin=user_latin,
                user_native=user_native,
            )'''

if old_incomplete in content:
    content = content.replace(old_incomplete, new_incomplete)
    print("Updated incomplete slots return block")

# 4. Update CPQ return block
old_cpq = '''        display_latin, display_native, spoken_tts = self._generate_dual_narration(profile, quote, selected_skus)
        display_md = display_latin if effective_script == "latin" else display_native
        user_latin, user_native = self._dualize_user_message(user_message, active_lang, effective_script)

        return AdvisorResponse(
            slots=slots,
            quote=quote,
            recommended_skus=selected_skus,
            display_markdown=display_md,
            spoken_tts_text=spoken_tts,
            next_suggested_prompts=[
                "Add 2 more business SIMs",
                "Can I add CCTV surveillance?",
                "Proceed to instant KYC",
            ],
            display_latin=display_latin,
            display_native=display_native,
            user_latin=user_latin,
            user_native=user_native,
        )'''

new_cpq = '''        display_latin, display_native, spoken_tts = self._generate_dual_narration(profile, quote, selected_skus)
        pure_latin, pure_native = ensure_dual_scripts(display_latin, display_native, active_lang)
        display_md = pure_latin if effective_script == "latin" else pure_native
        user_latin, user_native = self._dualize_user_message(user_message, active_lang, effective_script)

        return AdvisorResponse(
            slots=slots,
            quote=quote,
            recommended_skus=selected_skus,
            display_markdown=display_md,
            spoken_tts_text=spoken_tts,
            next_suggested_prompts=[
                "Add 2 more business SIMs",
                "Can I add CCTV surveillance?",
                "Proceed to instant KYC",
            ],
            display_latin=pure_latin,
            display_native=pure_native,
            user_latin=user_latin,
            user_native=user_native,
        )'''

if old_cpq in content:
    content = content.replace(old_cpq, new_cpq)
    print("Updated CPQ return block")

# 5. Update _dualize_user_message to use ensure_dual_scripts
old_dualize = '''    def _dualize_user_message(
        self,
        user_message: str,
        active_lang: str,
        effective_script: str,
    ) -> tuple[str, str]:
        """Translates user query between Latin Romanized and Native Regional Script."""
        clean = user_message.strip()
        lower = clean.lower()
        if "bagunnara" in lower or "ela unna" in lower:
            return ("bagunnara ela unnaru", "బాగున్నారా ఎలా ఉన్నారు")
        if "నమస్కారం" in clean or "బాగున్నారా" in clean:
            return ("namaskaram bagunnara", "నమస్కారం బాగున్నారా")
        if "vanakkam" in lower:
            return ("vanakkam eppadi irukkeenga", "வணக்கம் எப்படி இருக்கிறீர்கள்")
        if "வணக்கம்" in clean:
            return ("vanakkam eppadi irukkeenga", "வணக்கம் எப்படி இருக்கிறீர்கள்")
        if "kaise ho" in lower:
            return ("namaste kaise hain aap", "नमस्ते कैसे हैं आप")
        if "नमस्ते" in clean:
            return ("namaste kaise hain aap", "नमस्ते कैसे हैं आप")
        if "clinic" in lower and ("hyderabad" in lower or "hyd" in lower):
            return (clean, "హైదరాబాద్‌లో 10 మంది సిబ్బందితో క్లినిక్")
        if "kirana" in lower:
            return (clean, "టైర్ 2 లో కిరాణా షాప్, జీఎస్టీ లేదు")
        if "textile" in lower or "surat" in lower:
            return (clean, "સુરતમાં કાપડનું કારખાનું, ૨૫ કારીગરો")
        return (clean, clean)'''

new_dualize = '''    def _dualize_user_message(
        self,
        user_message: str,
        active_lang: str,
        effective_script: str,
    ) -> tuple[str, str]:
        """Translates user query between Latin Romanized and Native Regional Script."""
        clean = user_message.strip()
        return ensure_dual_scripts(clean, clean, active_lang)'''

if old_dualize in content:
    content = content.replace(old_dualize, new_dualize)
    print("Updated _dualize_user_message")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Advisor agent successfully synchronized with bidirectional transliteration engine.")

with open('backend/app/services/advisor_agent.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if 'def _dualize_user_message(self, text: str, lang: str, script: str)' in line:
        new_lines.append(line)
        new_lines.append('        """Returns (user_latin, user_native) for the input message."""\n')
        new_lines.append('        clean = text.strip()\n')
        new_lines.append('        return ensure_dual_scripts(clean, clean, lang)\n')
        skip = True
        continue
    if skip:
        if line.startswith('    def _generate_dual_narration'):
            skip = False
            new_lines.append('\n')
            new_lines.append(line)
        continue
    new_lines.append(line)

with open('backend/app/services/advisor_agent.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Updated _dualize_user_message successfully')
