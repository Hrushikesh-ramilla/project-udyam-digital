path = 'backend/app/services/advisor_agent.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_guardrail = '''        norm_msg = user_message.lower().strip()
        # Prompt injection & arbitrary price override guardrail
        if "ignore previous instructions" in norm_msg or "ignore all instructions" in norm_msg or re.search(r"\\b(?:for|at)\\s*(?:rs\\.?|inr|₹)?\\s*(?:10|1|5|0)\\s*(?:per\\s*month|\\/mo|month)?\\b", norm_msg):
            slots = previous_slots or MSMEProfileSlots()
            return AdvisorResponse(
                slots=slots,
                quote=None,
                recommended_skus=[],
                display_markdown="⚠️ **Airtel Business Enterprise Policy Guardrail:** Plan pricing is strictly determined by central regulatory tariff filings and cannot be modified via conversational prompts. Biz Fibre 1G (P03) is **₹3,999/month** (OTC Setup: ₹0). We can, however, help you find an authentic bundle matching your budget.",
                spoken_tts_text="Airtel Business plan pricing is strictly fixed and audited by regulatory filings. Biz Fibre 1G is 3,999 Rupees per month. Prompt price overrides are not permitted.",
                next_suggested_prompts=[
                    "Show plans under ₹1,500/month",
                    "What are the benefits of Biz Fibre 1G?",
                    "Check Udyam micro-retail bundles",
                ],
            )'''

new_guardrail = '''        norm_msg = user_message.lower().strip()
        # Prompt injection & arbitrary price override guardrail
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
            )'''

if old_guardrail in content:
    content = content.replace(old_guardrail, new_guardrail, 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Guardrail block successfully modernized with dual-script guarantees")
else:
    print("Old guardrail block not found")
