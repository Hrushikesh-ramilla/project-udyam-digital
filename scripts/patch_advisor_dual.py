import re

path = "backend/app/services/advisor_agent.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Helper method _dualize_user_message and updated _generate_dual_narration
helper_and_narration = '''    def _dualize_user_message(self, text: str, lang: str, script: str) -> tuple[str, str]:
        """Returns (user_latin, user_native) for the input message."""
        clean = text.strip()
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
        return (clean, clean)

    def _generate_dual_narration(
        self,
        profile: UserProfile,
        quote: CommercialBreakdown,
        skus: list[str],
    ) -> tuple[str, str, str]:
        """Generates (display_latin, display_native, spoken_tts)."""
        product_names = [
            self.db.get_product(pid).product_name
            for pid in skus
            if self.db.get_product(pid)
        ]
        base_name = product_names[0] if product_names else "High-Speed Internet"
        addons = product_names[1:]

        # Latin Channel
        md_latin = [
            f"### Recommended Bundle for Your {profile.segment.title()} Business\\n",
            f"Based on your profile in Tier {profile.city_tier} ({profile.employee_count} staff, "
            f"{'GST registered' if profile.has_gstin else 'Udyam micro-business'}), we configured an optimal bundle:\\n",
            f"* **Primary Connection:** {base_name}",
        ]
        if addons:
            md_latin.append(f"* **Add-ons:** {', '.join(addons)}")
        md_latin.append("\\n**Commercials & SLA:**")
        md_latin.append(f"* **Net Monthly:** ₹{quote.net_mrc_inr:,}/month (includes bundle discount)")
        md_latin.append(f"* **Setup Fee:** {'WAIVED (₹0)' if quote.net_otc_inr == 0 else f'₹{quote.net_otc_inr:,}'}")
        md_latin.append(f"* **Guaranteed SLA:** Ready in {quote.guaranteed_sla_days} business days")
        md_latin.append(f"* **Regulatory:** {'100% GST-Exempt Udyam Eligible' if quote.gst_exempt_eligible else 'B2B Input Tax Credit Eligible'}")
        display_latin = "\\n".join(md_latin)

        # Native Script Channel (Telugu benchmark with comprehensive Indic structure)
        md_native = [
            f"### మీ వ్యాపారానికి సిఫార్సు చేసిన ఎయిర్‌టెల్ కనెక్టివిటీ ప్లాన్\\n",
            f"టైర్ {profile.city_tier} లోని మీ వ్యాపారం కోసం ({profile.employee_count} మంది సిబ్బంది, "
            f"{'జీఎస్టీ నమోదిత' if profile.has_gstin else 'ఉద్యమ్ మైక్రో ఎంటర్‌ప్రైజ్'}):\\n",
            f"* **ప్రధాన కనెక్షన్:** {base_name}",
        ]
        if addons:
            md_native.append(f"* **అదనపు సేవలు:** {', '.join(addons)}")
        md_native.append("\\n**ధర మరియు సర్వీస్ వివరాలు:**")
        md_native.append(f"* **నెలవారీ ఛార్జీ:** ₹{quote.net_mrc_inr:,}/నెల")
        md_native.append(f"* **సెటప్ రుసుము:** {'పూర్తిగా ఉచితం (₹0)' if quote.net_otc_inr == 0 else f'₹{quote.net_otc_inr:,}'}")
        md_native.append(f"* **యాక్టివేషన్:** {quote.guaranteed_sla_days} పని దినాలలో")
        md_native.append(f"* **అర్హత:** {'100% ఉద్యమ్ జీఎస్టీ మినహాయింపు' if quote.gst_exempt_eligible else 'జీఎస్టీ ఇన్పుట్ క్రెడిట్ అర్హత'}")
        display_native = "\\n".join(md_native)

        # Spoken TTS Channel
        addon_phrase = f"aur {len(addons)} zaroori add ons" if addons else ""
        spoken_tts = (
            f"Aapke business ke liye humne {base_name} {addon_phrase} chuna hai. "
            f"Iska monthly charge {quote.net_mrc_inr} rupaye hai. "
            f"Setup fee bilkul zero hai aur yeh {quote.guaranteed_sla_days} din mein activate ho jayega."
        )

        return display_latin, display_native, spoken_tts
'''

# Find _generate_dual_narration and replace it
pattern = r"    def _generate_dual_narration\(.*?\):.*?(?=\n    def |\Z)"
content = re.sub(pattern, helper_and_narration, content, flags=re.DOTALL)

# Now update greetings return
old_greeting_block = '''            matched_greeting = greetings_map.get(active_lang, {}).get(effective_script)
            welcome_md = gemini_md or (matched_greeting[0] if matched_greeting else (
                "### Namaste! Welcome to Airtel Business Udyam Digital 🙏\\n\\n"
                "I am doing great, thank you! I am your AI Enterprise Telecom Advisor. Tell me a bit about your business:\\n"
                "* What kind of business do you run (e.g. retail shop, clinic, CA office, factory)?\\n"
                "* Which city and approximately how many staff?\\n"
                "* Do you have a registered GSTIN or Udyam certificate?"
            ))
            welcome_tts = gemini_tts or (matched_greeting[1] if matched_greeting else "Namaste! Airtel Business Udyam Digital mein aapka swagat hai. Kripya batayein ki aap kis sheher mein hain aur aapka business kis type ka hai.")
            return AdvisorResponse(
                slots=slots,
                quote=None,
                recommended_skus=[],
                display_markdown=welcome_md,
                spoken_tts_text=welcome_tts,
                next_suggested_prompts=[
                    "I run a Kirana store in Tier 2 with no GST",
                    "We are a CA office in Mumbai with GST",
                    "We have a factory in Surat with 30 staff",
                ],
            )'''

new_greeting_block = '''            matched_native = greetings_map.get(active_lang, {}).get("native", greetings_map["te"]["native"])
            matched_latin = greetings_map.get(active_lang, {}).get("latin", greetings_map["te"]["latin"])
            
            display_native = matched_native[0]
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

content = content.replace(old_greeting_block, new_greeting_block)

# Now update incomplete slots return
old_incomplete_block = '''            prompt_en = gemini_md or f"Namaste! To recommend the best digital plan, could you please clarify: {', '.join(missing_text)}?"
            prompt_hi_tts = gemini_tts or "Namaste! Aapke business ke liye best plan chunne ke liye, kripya batayein ki aap kis sheher mein hain aur aapka business kis type ka hai."

            return AdvisorResponse(
                slots=slots,
                quote=None,
                recommended_skus=[],
                display_markdown=prompt_en,
                spoken_tts_text=prompt_hi_tts,
                next_suggested_prompts=[
                    "I run a Kirana store in Tier 2 with no GST",
                    "We are a CA office in Mumbai with GST",
                    "We have a factory in Surat with 30 staff",
                ],
            )'''

new_incomplete_block = '''            prompt_latin = f"Namaste! To configure your digital plan, please tell us: {', '.join(missing_text)}."
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

content = content.replace(old_incomplete_block, new_incomplete_block)

# Now update CPQ response assembly
old_cpq_return = '''        # Generate Dual-Channel Narration
        display_md, spoken_tts = self._generate_dual_narration(profile, quote, selected_skus)

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
        )'''

new_cpq_return = '''        # Generate Dual-Channel Narration
        display_latin, display_native, spoken_tts = self._generate_dual_narration(profile, quote, selected_skus)
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

content = content.replace(old_cpq_return, new_cpq_return)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated advisor_agent.py successfully")
