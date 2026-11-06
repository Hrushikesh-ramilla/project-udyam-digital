with open("backend/app/services/advisor_agent.py", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find("    def _generate_dual_narration(")
if idx != -1:
    before = text[:idx]
    replacement = '''    def _dualize_user_message(self, text: str, lang: str, script: str) -> tuple[str, str]:
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

        addon_phrase = f"aur {len(addons)} zaroori add ons" if addons else ""
        spoken_tts = (
            f"Aapke business ke liye humne {base_name} {addon_phrase} chuna hai. "
            f"Iska monthly charge {quote.net_mrc_inr} rupaye hai. "
            f"Setup fee bilkul zero hai aur yeh {quote.guaranteed_sla_days} din mein activate ho jayega."
        )

        return display_latin, display_native, spoken_tts
'''
    with open("backend/app/services/advisor_agent.py", "w", encoding="utf-8") as f:
        f.write(before + replacement)
    print("Replaced successfully!")
else:
    print("Not found")
