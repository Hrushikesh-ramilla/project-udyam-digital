from __future__ import annotations

import re
from typing import Optional

from backend.app.db.registry import RegistryDatabase, get_registry
from backend.app.models.schemas import (
    AdvisorResponse,
    CartItem,
    CommercialBreakdown,
    MSMEProfileSlots,
    UserProfile,
)
from backend.app.services.cpq_engine import CPQEngine

TIER_1_CITIES = {
    "mumbai", "delhi", "bengaluru", "bangalore", "hyderabad",
    "chennai", "kolkata", "pune", "ahmedabad", "gurugram", "noida"
}


class AdvisorAgent:
    """Multilingual Neuro-Symbolic Conversational Advisor.

    Combines robust multilingual slot-filling (Hindi, Hinglish, English)
    with a deterministic CPQ engine and dual-channel narration (Markdown + Voice TTS).
    """

    def __init__(self, db: Optional[RegistryDatabase] = None) -> None:
        self.db = db or get_registry()
        self.cpq = CPQEngine(self.db)

    def extract_slots(self, text: str, existing_slots: Optional[MSMEProfileSlots] = None) -> MSMEProfileSlots:
        """Extracts MSME profile parameters from conversational Hindi, Hinglish, or English."""
        norm_text = text.lower().strip()
        slots = existing_slots.model_copy() if existing_slots else MSMEProfileSlots()

        # 1. Segment Extraction
        if not slots.segment:
            if re.search(r"\b(kirana|grocery|salon|parlour|pharmacy|chemist|medical|bakery|cafe|boutique|dhaba|stationery|repair|shop|dukan|retail)\b", norm_text):
                slots.segment = "micro"
            elif re.search(r"\b(clinic|doctor|hospital|ca\s*firm|chartered\s*accountant|lawyer|advocate|coaching|tuition|consultan|architect|diagnostic|office)\b", norm_text):
                slots.segment = "prof"
            elif re.search(r"\b(chain|multi[\s-]*site|outlets|stores|branches|restaurant\s*chain)\b", norm_text):
                slots.segment = "multi"
            elif re.search(r"\b(factory|textile|auto[\s-]*parts|manufacturing|plant|foundry|workshop|mill|industrial)\b", norm_text):
                slots.segment = "mfg"

        # 2. City Tier Extraction
        if not slots.city_tier:
            # Check city names
            for t1 in TIER_1_CITIES:
                if re.search(rf"\b{t1}\b", norm_text):
                    slots.city_tier = 1
                    break
            if not slots.city_tier:
                # Common Tier 2 city keywords or explicit mentions
                if re.search(r"\b(jaipur|lucknow|surat|kanpur|nagpur|indore|bhopal|vizag|visakhapatnam|patna|vadodara|ludhiana|agra|nashik|coimbatore|kochi|chandigarh|tier\s*2)\b", norm_text):
                    slots.city_tier = 2
                elif re.search(r"\btier\s*1\b", norm_text):
                    slots.city_tier = 1
                else:
                    # Default reasonable assumption if location mentioned but not Tier 1
                    if any(word in norm_text for word in ["city", "town", "in"]):
                        slots.city_tier = 2

        # 3. Employee Count Extraction
        if not slots.employee_count:
            emp_match = re.search(r"\b(\d+)\s*(?:staff|employees|workers|log|members|people|kam\s*karne\s*wale)\b", norm_text)
            if emp_match:
                slots.employee_count = int(emp_match.group(1))
            else:
                # Check for single word numbers
                word_numbers = {
                    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
                    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "ek": 1, "do": 2,
                    "teen": 3, "char": 4, "paanch": 5, "chhe": 6, "saat": 7, "aath": 8
                }
                for w, val in word_numbers.items():
                    if re.search(rf"\b{w}\s*(?:staff|employees|workers|log)\b", norm_text):
                        slots.employee_count = val
                        break

        # 4. Site Count Extraction
        if not slots.num_sites:
            site_match = re.search(r"\b(\d+)\s*(?:[a-z0-9_-]+\s+)?(?:shops|stores|branches|sites|locations|dukaan|outlets|units|factories)\b", norm_text)
            if site_match:
                slots.num_sites = int(site_match.group(1))
            elif "2 store" in norm_text or "2 shop" in norm_text or "do dukan" in norm_text:
                slots.num_sites = 2
            elif "single" in norm_text or "one shop" in norm_text or "ek dukan" in norm_text:
                slots.num_sites = 1
            else:
                slots.num_sites = 1  # Default to single site if not specified

        # 5. GSTIN Presence Extraction
        if slots.has_gstin is None:
            if re.search(r"\b(no\s*gst(?:in)?|without\s*gst(?:in)?|gst(?:in)?\s*nahi|dont\s*have\s*gst(?:in)?|don't\s*have\s*gst(?:in)?|gst\s*number\s*nahi|zero\s*gst)\b", norm_text):
                slots.has_gstin = False
            elif re.search(r"\b(have\s*gst(?:in)?|has\s*gst(?:in)?|with\s*gst(?:in)?|gst\s*registered|gst\s*hai|gstin\s*hai|gst\s*number\s*hai|gstin\s*available|active\s*gst(?:in)?)\b", norm_text):
                slots.has_gstin = True

        # 6. Budget Extraction
        if not slots.monthly_budget_cap:
            budget_match = re.search(r"\b(?:budget|spending|kharcha|rupaye|rs|inr|₹)\s*(?:is|hai|of|around|lagbhag)?\s*(?:rs\.?|inr|₹)?\s*(\d{3,6})\b", norm_text)
            if not budget_match:
                budget_match = re.search(r"\b(\d{3,6})\s*(?:rupaye|rupees|rs|per\s*month|\/mo)\b", norm_text)
            if budget_match:
                slots.monthly_budget_cap = int(budget_match.group(1))

        # 7. Needs Extraction
        detected = set(slots.detected_needs)
        if re.search(r"\b(upi|gpay|phonepe|paytm|pos|qr|hotspot|failover|backup|payment\s*atak|counter)\b", norm_text):
            detected.add("pos_upi_uptime")
        if re.search(r"\b(whatsapp|catalog|catalogue|broadcast|sms|message\s*bhejna)\b", norm_text):
            detected.add("whatsapp_catalogue")
        if re.search(r"\b(email|tally|cloud|drive|storage|office\s*365|google\s*workspace|data\s*safe)\b", norm_text):
            detected.add("cloud_email")
        if re.search(r"\b(cctv|camera|surveillance|nvr|dvr)\b", norm_text):
            detected.add("cctv_surveillance")
        if re.search(r"\b(guest\s*wifi|customer\s*wifi|wifi)\b", norm_text):
            detected.add("guest_wifi")
        if re.search(r"\b(static\s*ip|fixed\s*ip|erp|server)\b", norm_text):
            detected.add("static_ip")
        if re.search(r"\b(leased\s*line|ill|dedicated\s*internet|fiber\s*cut)\b", norm_text):
            detected.add("dedicated_ill")
        if re.search(r"\b(iot|machine|sensor|monitoring)\b", norm_text):
            detected.add("iot_monitoring")
        slots.detected_needs = sorted(list(detected))

        # Check completeness
        missing = []
        if not slots.segment:
            missing.append("business_type")
        if not slots.city_tier:
            missing.append("city_or_tier")
        if slots.has_gstin is None:
            missing.append("gstin_status")

        slots.is_complete = len(missing) == 0
        slots.missing_slots = missing
        return slots

    def process_turn(self, user_message: str, previous_slots: Optional[MSMEProfileSlots] = None) -> AdvisorResponse:
        """Executes full neuro-symbolic turn: Slot Extraction -> CPQ Engine -> Dual Narration."""
        slots = self.extract_slots(user_message, previous_slots)

        # If missing critical slots, formulate conversational clarifying question
        if not slots.is_complete:
            missing_text = []
            if "business_type" in slots.missing_slots:
                missing_text.append("what kind of business you run (e.g. retail shop, clinic, CA office, factory)")
            if "city_or_tier" in slots.missing_slots:
                missing_text.append("which city or town you are located in")
            if "gstin_status" in slots.missing_slots:
                missing_text.append("whether you have a registered GST number or only Udyam")

            prompt_en = f"Namaste! To recommend the best digital plan, could you please clarify: {', '.join(missing_text)}?"
            prompt_hi_tts = "Namaste! Aapke business ke liye best plan chunne ke liye, kripya batayein ki aap kis sheher mein hain aur aapka business kis type ka hai."

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
            )

        # Slots are complete: Build user profile for deterministic CPQ
        profile = UserProfile(
            segment=slots.segment or "micro",
            city_tier=slots.city_tier or 2,
            employee_count=slots.employee_count or 3,
            num_sites=slots.num_sites or 1,
            has_gstin=slots.has_gstin if slots.has_gstin is not None else False,
            detected_needs=slots.detected_needs,
            monthly_budget_cap=slots.monthly_budget_cap,
        )

        # Run deterministic CPQ Engine
        if slots.monthly_budget_cap and slots.monthly_budget_cap > 0:
            budget_res = self.cpq.optimize_budget(profile, slots.monthly_budget_cap)
            quote = budget_res.commercials
            selected_skus = budget_res.selected_skus
        else:
            # Standard recommendation based on segment and needs
            eligible = self.cpq.filter_eligible_products(profile)
            eligible_ids = {sku.product_id for sku in eligible}

            # Select best base plan
            base_sku = "P01"  # Default Biz Fibre 100
            if profile.segment == "mfg" and ("P05" in eligible_ids or "P06" in eligible_ids):
                base_sku = "P05" if "P05" in eligible_ids else "P06"
            elif profile.segment in {"prof", "multi"} and "P02" in eligible_ids:
                base_sku = "P02"
            elif profile.segment == "micro" and "P04" in eligible_ids:
                base_sku = "P04"  # 5G AirFiber for micro
            elif "P01" in eligible_ids:
                base_sku = "P01"

            cart_pids = [base_sku]
            # Add compatible need-based add-ons
            if "pos_upi_uptime" in profile.detected_needs and "P09" in eligible_ids:
                cart_pids.append("P09")
            if "whatsapp_catalogue" in profile.detected_needs and "P15" in eligible_ids:
                cart_pids.append("P15")
            if "cloud_email" in profile.detected_needs and "P16" in eligible_ids:
                cart_pids.append("P16")
            if "cctv_surveillance" in profile.detected_needs and "P23" in eligible_ids:
                cart_pids.append("P23")
            if "guest_wifi" in profile.detected_needs and "P22" in eligible_ids:
                cart_pids.append("P22")

            cart_items = [CartItem(product_id=pid) for pid in cart_pids]
            quote = self.cpq.calculate_commercials(cart_items, contract_months=12, strict_dag=True)
            selected_skus = cart_pids

        # Generate Dual-Channel Narration
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
        )

    def _generate_dual_narration(
        self,
        profile: UserProfile,
        quote: CommercialBreakdown,
        skus: list[str],
    ) -> tuple[str, str]:
        """Generates both rich Markdown for the chat bubble and clean symbol-free text for TTS."""
        product_names = [
            self.db.get_product(pid).product_name
            for pid in skus
            if self.db.get_product(pid)
        ]
        base_name = product_names[0] if product_names else "High-Speed Internet"
        addons = product_names[1:]

        # Markdown Channel
        md_lines = [
            f"### Recommended Bundle for Your {profile.segment.title()} Business\n",
            f"Based on your profile in **Tier {profile.city_tier}** ({profile.employee_count} staff, "
            f"{'GST registered' if profile.has_gstin else 'Udyam micro-business'}), we configured a custom bundle:\n",
            f"* **Primary Connection:** {base_name}",
        ]
        if addons:
            md_lines.append(f"* **Add-ons:** {', '.join(addons)}")

        # Value rationale
        md_lines.append("\n**Why this bundle works for you:**")
        if "P09" in skus:
            md_lines.append("* **4G Auto-Failover:** Your UPI QR and card swipe machine will never stop working, even during a cable cut.")
        if "P04" in skus:
            md_lines.append("* **Biz 5G AirFiber:** Instant plug-and-play setup active in 48 hours without trenching or delays.")
        if "P16" in skus:
            md_lines.append("* **Cloud Suite:** Secure business email and cloud storage to keep client and account files safe.")
        if "P23" in skus:
            md_lines.append("* **Cloud CCTV:** Live video feed viewable directly on your smartphone from anywhere.")

        md_lines.append(
            f"\n**Commercials & SLA:**\n"
            f"- **Net Monthly Price:** ₹{quote.net_mrc_inr:,}/month (includes bundle discount)\n"
            f"- **One-Time Setup Fee:** {'WAIVED (₹0)' if quote.net_otc_inr == 0 else f'₹{quote.net_otc_inr:,}'}\n"
            f"- **Guaranteed SLA:** Ready to activate in **{quote.guaranteed_sla_days} business days**\n"
            f"- **GST Status:** {'100% GST-Exempt Udyam Eligible' if quote.gst_exempt_eligible else 'Standard B2B Input Tax Credit Eligible'}"
        )
        display_md = "\n".join(md_lines)

        # Spoken TTS Channel (Pure phonetic words, zero symbols, zero markdown, zero asterisks)
        addon_phrase = f"aur {len(addons)} zaroori add ons" if addons else ""
        spoken_tts = (
            f"Aapke business ke liye humne {base_name} {addon_phrase} chuna hai. "
            f"Iska monthly charge {quote.net_mrc_inr} rupaye hai. "
            f"Setup fee bilkul zero hai aur yeh {quote.guaranteed_sla_days} din mein activate ho jayega. "
            f"Aap niche button dabakar instant KYC pura kar sakte hain."
        )

        return display_md, spoken_tts
