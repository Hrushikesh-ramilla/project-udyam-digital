import re

with open("backend/app/services/advisor_agent.py", "r", encoding="utf-8") as f:
    code = f.read()

# Let's inspect where process_turn starts and ends
proc_turn_start = "    def process_turn("
proc_turn_end = "    def _dualize_user_message("

new_process_turn = '''    def process_turn(
        self,
        user_message: str,
        previous_slots: Optional[MSMEProfileSlots] = None,
        language_code: Optional[str] = None,
        script_mode: Optional[str] = None,
        history: Optional[list[dict[str, str]]] = None,
    ) -> AdvisorResponse:
        norm_msg = user_message.lower().strip()
        # Security guardrails: prompt injection & arbitrary price override
        is_injection = "ignore previous instructions" in norm_msg or "ignore all instructions" in norm_msg or "say hacked" in norm_msg
        is_illegal_price = bool(re.search(r"\\b(?:at|for|give me.*?at)\\s*(?:rs\\.?|inr|₹)\\s*(?:10|1|5|0|500)\\b", norm_msg) or re.search(r"\\b(?:10|1|5|0|500)\\s*(?:rupees|rs)\\s*(?:per\\s*month|\\/mo)\\b", norm_msg))
        if is_injection or is_illegal_price:
            slots = previous_slots or MSMEProfileSlots()
            guard_latin = (
                "⚠️ **Airtel Business Enterprise Policy Guardrail:** Plan pricing is strictly determined by central "
                "regulatory tariff filings and cannot be modified via conversational prompts. Biz Fibre 1G (P03) is "
                "**₹3,999/month** (OTC Setup: ₹0). We can, however, help you find an authentic bundle matching your budget."
            )
            guard_native = (
                "⚠️ **ఎయిర్‌టెల్ బిజినెస్ ఎంటర్‌ప్రైజ్ పాలసీ గార్డ్‌రైల్:** ప్లాన్ ధరలు కేంద్ర టారిఫ్ నిబంధనలకు కట్టుబడి ఉంటాయి. "
                "బిజ్ ఫైబర్ 1G (P03) ధర నెలకు ₹3,999 (సెటప్ రుసుము: ₹0). మీ బడ్జెట్‌కు సరిపోయే ప్రామాణికమైన ప్లాన్‌ను ఎంచుకోవడంలో మేము సహాయం చేయగలము."
            )
            p_lat, p_nat = ensure_dual_scripts(guard_latin, guard_native, language_code or "te")
            u_lat, u_nat = ensure_dual_scripts(user_message, user_message, language_code or "te")
            eff_script = script_mode or ("native" if has_indic_script(user_message) else "latin")

            return AdvisorResponse(
                slots=slots,
                quote=None,
                recommended_skus=[],
                display_markdown=p_lat if eff_script == "latin" else p_nat,
                spoken_tts_text="Airtel Business plan pricing is strictly fixed and audited by regulatory filings. Prompt price overrides are not permitted.",
                next_suggested_prompts=[
                    "Show plans under ₹1,500/month",
                    "What are the benefits of Biz Fibre 1G?",
                    "Check Udyam micro-retail bundles",
                ],
                display_latin=p_lat,
                display_native=p_nat,
                user_latin=u_lat,
                user_native=u_nat,
            )

        # Baseline deterministic extraction (bedrock guarantee)
        slots = self.extract_slots(user_message, previous_slots)

        clean_msg = user_message.strip().lower()
        has_indic = bool(re.search(r"[ऀ-ൿ]", user_message))
        effective_script = script_mode or ("native" if has_indic else "latin")

        # Detect active language
        active_lang = language_code or "en"
        if re.search(r"[ఀ-౿]", user_message) or re.search(r"\\b(bagunnara|bagunara|ela\\s*unnaru|ela\\s*unnav|namaskaram|namasthe|kavali|kavala|enti|eppudu|undi|ledu|meeru)\\b", clean_msg):
            active_lang = "te"
        elif re.search(r"[஀-௿]", user_message) or re.search(r"\\b(vanakkam|eppadi\\s*iruk|nalama|sollunga|irukku|illa|venum|ungalukku)\\b", clean_msg):
            active_lang = "ta"
        elif re.search(r"[ঀ-৿]", user_message) or re.search(r"\\b(nomoshkar|kemon\\s*ac|bhalo|lagbe|nei|apnar)\\b", clean_msg):
            active_lang = "bn"
        elif re.search(r"[઀-૿]", user_message) or re.search(r"\\b(kem\\s*cho|majama|tamare|joie|nathi)\\b", clean_msg):
            active_lang = "gu"
        elif re.search(r"\\b(kase\\s*ahat|pahije|ahe|nahi|tumhi)\\b", clean_msg):
            active_lang = "mr"
        elif re.search(r"[ಀ-೿]", user_message) or re.search(r"\\b(namaskara|hegidd|hegiddira|beku|illa|nimma)\\b", clean_msg):
            active_lang = "kn"
        elif re.search(r"[ഀ-ൿ]", user_message) or re.search(r"\\b(namaskaram|sukhamano|sukham\\s*anu|venam|illa|ningal)\\b", clean_msg):
            active_lang = "ml"
        elif re.search(r"[଀-୿]", user_message) or re.search(r"\\b(kemiti\\s*ach|bhalare|darkar|nahin|apana)\\b", clean_msg):
            active_lang = "or"
        elif re.search(r"[ऀ-ॿ]", user_message) or re.search(r"\\b(kaise\\s*ho|kya\\s*haal|sab\\s*theek|bhai|bhaiya|chahiye|aapka)\\b", clean_msg):
            active_lang = "hi"

        # Intent detection
        is_comparison = bool(re.search(
            r"\\b(compare|comparison|multiple|options|alternatives|vs|other plans?|not only one|only one|another plan|different plan|kore option|aur option)\\b",
            clean_msg
        ))
        is_question = bool(re.search(
            r"\\b(what|why|how|can|is|will|do|explain|tell|difference|kya|kaise|kyun|enti|ela|eppudu)\\b",
            clean_msg
        ))
        is_foreign = bool(re.search(r"^(hola|bonjour|ciao|aloha|hallo|salut|wie\\s*gehts|que\\s*tal|konnichiwa|privet|merhaba|sawasdee)\\b", clean_msg))
        is_unrelated = bool(re.search(r"\\b(recipe|biryani|butter\\s*chicken|cook|weather|monsoon|rain|poem|movie|sci-fi|python|binary\\s*search|code|joke|capital\\s*of|capital\\s*city|who\\s*won)\\b", clean_msg))
        is_terse = clean_msg in {"internet", "broadband", "plans", "price", "how much", "speed", "enterprise", "connection", "quote", "airtel"}
        is_greeting = bool(re.search(r"^(hey|hi|hello|whats\\s*up|what\\'s\\s*up|good\\s*(morning|evening|afternoon)|yo|sup|bhai|bhaiya)\\b", clean_msg)) or bool(re.search(r"\\b(bagunnara|bagunara|ela\\s*unnaru|ela\\s*unnav|namaskaram|namasthe|vanakkam|eppadi\\s*iruk|kemon\\s*ac|kem\\s*cho|kase\\s*ahat|hegidd|sukhamano|kemiti\\s*ach|kaise\\s*ho|kya\\s*haal|namaste|నమస్కారం|నమస్తే|బాగున్నారా|வணக்கம்|நமஸ்கார்|নমস্কার|નમસ્તે|नमस्कार|ನಮಸ್ಕಾರ|നമസ്കാരം|ନମସ୍କାର)\\b", clean_msg))

        # -------------------------------------------------------------
        # TIER 1: LIVE GEMINI ENTERPRISE CONSULTATION (If online)
        # -------------------------------------------------------------
        gemini_data = self._consult_gemini(
            user_message,
            existing_slots=slots,
            language_code=active_lang,
            script_mode=effective_script,
            history=history,
        )

        if gemini_data:
            # Update slots from Gemini
            if not slots.segment and gemini_data.get("segment"):
                slots.segment = str(gemini_data["segment"]).lower()
            if not slots.city_tier and gemini_data.get("city_tier"):
                slots.city_tier = int(gemini_data["city_tier"])
            if not slots.employee_count and gemini_data.get("employee_count"):
                slots.employee_count = int(gemini_data["employee_count"])
            if not slots.num_sites and gemini_data.get("num_sites"):
                slots.num_sites = int(gemini_data["num_sites"])
            if slots.has_gstin is None and gemini_data.get("has_gstin") is not None:
                slots.has_gstin = bool(gemini_data["has_gstin"])
            if gemini_data.get("detected_needs"):
                existing_needs = set(slots.detected_needs)
                for n in gemini_data["detected_needs"]:
                    existing_needs.add(str(n).lower())
                slots.detected_needs = sorted(list(existing_needs))
            if not slots.monthly_budget_cap and gemini_data.get("monthly_budget_cap"):
                slots.monthly_budget_cap = int(gemini_data["monthly_budget_cap"])

            missing = []
            if not slots.segment:
                missing.append("business_type")
            if not slots.city_tier:
                missing.append("city_or_tier")
            if slots.has_gstin is None:
                missing.append("gstin_status")
            slots.is_complete = len(missing) == 0
            slots.missing_slots = missing

            disp_lat = gemini_data.get("display_latin") or gemini_data.get("display_markdown") or ""
            disp_nat = gemini_data.get("display_native") or disp_lat
            spoken = gemini_data.get("spoken_tts") or ""
            spoken = re.sub(r"[\\*#\\[\\]]", "", spoken).replace("₹", "rupaye ").strip()

            gem_skus = gemini_data.get("recommended_skus") or []
            valid_skus = [s for s in gem_skus if self.db.get_product(s)]
            if not valid_skus:
                valid_skus = self._select_skus_for_slots(slots)

            # Deterministic CPQ Engine execution for live commercials & cart sync
            quote = None
            if slots.is_complete or len(valid_skus) > 0:
                try:
                    cart_items = [CartItem(product_id=s) for s in valid_skus]
                    quote = self.cpq.calculate_commercials(cart_items, contract_months=12, strict_dag=True)
                except Exception as e:
                    logging.warning("CPQ calculation on Gemini SKUs failed: %s", e)

            pure_latin, pure_native = ensure_dual_scripts(disp_lat, disp_nat, active_lang)
            user_lat, user_nat = self._dualize_user_message(user_message, active_lang, effective_script)

            prompts = gemini_data.get("next_suggested_prompts") or [
                "Show details of Biz 5G AirFiber",
                "Can I add 4G Auto-Failover?",
                "Proceed to instant KYC",
            ]

            return AdvisorResponse(
                slots=slots,
                quote=quote,
                recommended_skus=valid_skus,
                display_markdown=pure_latin if effective_script == "latin" else pure_native,
                spoken_tts_text=spoken or (pure_latin if effective_script == "latin" else pure_native),
                next_suggested_prompts=prompts,
                display_latin=pure_latin,
                display_native=pure_native,
                user_latin=user_lat,
                user_native=user_nat,
            )

        # -------------------------------------------------------------
        # TIER 2: DETERMINISTIC SYMBOLIC / HUMAN FALLBACK (offline / pytest)
        # -------------------------------------------------------------
        # 1. Comparison & Multiple Options request
        if is_comparison:
            f_latin, f_native, f_tts = self._generate_human_fallback(
                user_message, clean_msg, active_lang, effective_script, slots,
                is_foreign=False, is_unrelated=False, is_terse=False, is_greeting=False
            )
            valid_skus = self._select_skus_for_slots(slots)
            cart_items = [CartItem(product_id=s) for s in valid_skus]
            quote = self.cpq.calculate_commercials(cart_items, contract_months=12, strict_dag=True)
            pure_latin, pure_native = ensure_dual_scripts(f_latin, f_native, active_lang)
            user_lat, user_nat = self._dualize_user_message(user_message, active_lang, effective_script)
            return AdvisorResponse(
                slots=slots,
                quote=quote,
                recommended_skus=valid_skus,
                display_markdown=pure_latin if effective_script == "latin" else pure_native,
                spoken_tts_text=f_tts,
                next_suggested_prompts=[
                    "Tell me more about AirFiber",
                    "What if I choose Fixed Fiber?",
                    "Proceed to instant KYC",
                ],
                display_latin=pure_latin,
                display_native=pure_native,
                user_latin=user_lat,
                user_native=user_nat,
            )

        # 2. Greeting, Unrelated, Terse, Foreign
        if is_foreign or is_unrelated or is_terse or (is_greeting and not slots.is_complete):
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
                spoken_tts_text=f_tts,
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

        # 3. Slots are incomplete: prompt for clarification
        if not slots.is_complete:
            f_latin, f_native, f_tts = self._generate_human_fallback(
                user_message, clean_msg, active_lang, effective_script, slots
            )
            pure_latin, pure_native = ensure_dual_scripts(f_latin, f_native, active_lang)
            user_lat, user_nat = self._dualize_user_message(user_message, active_lang, effective_script)
            return AdvisorResponse(
                slots=slots,
                quote=None,
                recommended_skus=[],
                display_markdown=pure_latin if effective_script == "latin" else pure_native,
                spoken_tts_text=f_tts,
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

        # 4. Slots are complete & standard recommendation requested
        profile = UserProfile(
            segment=slots.segment or "micro",
            city_tier=slots.city_tier or 2,
            employee_count=slots.employee_count or 3,
            num_sites=slots.num_sites or 1,
            has_gstin=slots.has_gstin if slots.has_gstin is not None else False,
            detected_needs=slots.detected_needs,
            monthly_budget_cap=slots.monthly_budget_cap,
        )

        if slots.monthly_budget_cap and slots.monthly_budget_cap > 0:
            budget_res = self.cpq.optimize_budget(profile, slots.monthly_budget_cap)
            quote = budget_res.commercials
            selected_skus = budget_res.selected_skus
        else:
            selected_skus = self._select_skus_for_slots(slots)
            cart_items = [CartItem(product_id=pid) for pid in selected_skus]
            quote = self.cpq.calculate_commercials(cart_items, contract_months=12, strict_dag=True)

        display_latin, display_native, spoken_tts = self._generate_dual_narration(profile, quote, selected_skus)
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
                "Can you compare with other options?",
                "Can I add CCTV surveillance?",
                "Proceed to instant KYC",
            ],
            display_latin=pure_latin,
            display_native=pure_native,
            user_latin=user_latin,
            user_native=user_native,
        )
'''

# Match and replace process_turn
start_idx = code.find(proc_turn_start)
end_idx = code.find(proc_turn_end)
assert start_idx != -1 and end_idx != -1, f"Could not find indices: {start_idx}, {end_idx}"

code = code[:start_idx] + new_process_turn + "\n" + code[end_idx:]

with open("backend/app/services/advisor_agent.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Successfully patched process_turn in advisor_agent.py")
