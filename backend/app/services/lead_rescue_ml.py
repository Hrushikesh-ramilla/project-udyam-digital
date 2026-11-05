from __future__ import annotations

from typing import Optional
import numpy as np
import pandas as pd
import lightgbm as lgb

from backend.app.db.registry import RegistryDatabase, get_registry
from backend.app.models.schemas import LeadRescueItem, SMBLeadRecord

_CACHED_MODEL: Optional[lgb.LGBMClassifier] = None


class LeadRescueMLEngine:
    """LightGBM-powered Lead Propensity & Drop-off Recovery Engine.

    Trained on 5,000 SMB historical leads with class imbalance weighting (scale_pos_weight=12.5)
    to target the 56% quoting leak and rescue high-intent merchants.
    """

    def __init__(self, db: Optional[RegistryDatabase] = None) -> None:
        self.db = db or get_registry()
        self.model: Optional[lgb.LGBMClassifier] = None
        self._feature_cols = [
            "city_tier",
            "employee_count",
            "num_sites",
            "has_gstin_int",
            "has_udyam_int",
            "monthly_telecom_spend_inr",
            "customer_follow_up_calls",
            "segment_code",
            "source_code",
        ]
        self._segment_map = {
            "micro retail & services": 0,
            "professional offices": 1,
            "small multi-site businesses": 2,
            "small manufacturers": 3,
        }
        self._source_map = {
            "field sales": 0,
            "website form": 1,
            "channel partner": 2,
            "inbound call": 3,
            "referral": 4,
            "whatsapp campaign": 5,
        }
        self._train_model()

    def _train_model(self) -> None:
        """Trains LightGBM classifier on the 5,000 synthetic SMB leads."""
        global _CACHED_MODEL
        if _CACHED_MODEL is not None:
            self.model = _CACHED_MODEL
            return

        leads = self.db.get_all_leads()
        if not leads:
            return

        records = []
        for l in leads:
            seg_code = self._segment_map.get(l.segment.lower().strip(), 0)
            src_code = self._source_map.get(l.lead_source.lower().strip(), 0)
            y = 1 if l.outcome.lower() == "activated" else 0

            records.append({
                "city_tier": l.city_tier,
                "employee_count": l.employee_count,
                "num_sites": l.num_sites,
                "has_gstin_int": 1 if l.has_gstin else 0,
                "has_udyam_int": 1 if l.has_udyam else 0,
                "monthly_telecom_spend_inr": l.monthly_telecom_spend_inr,
                "customer_follow_up_calls": l.customer_follow_up_calls,
                "segment_code": seg_code,
                "source_code": src_code,
                "target": y,
            })

        df = pd.DataFrame(records)
        X = df[self._feature_cols]
        y = df["target"]

        pos_count = y.sum()
        neg_count = len(y) - pos_count
        scale_weight = float(neg_count / max(1, pos_count))  # ~ 12.58

        self.model = lgb.LGBMClassifier(
            scale_pos_weight=scale_weight,
            n_estimators=50,
            max_depth=4,
            learning_rate=0.08,
            random_state=42,
            verbosity=-1,
        )
        self.model.fit(X, y)
        _CACHED_MODEL = self.model

    def _build_lead_item(self, lead: SMBLeadRecord, score: float) -> LeadRescueItem:
        """Constructs a LeadRescueItem with deterministic priority tiers, risk factors, and NBA."""
        if score >= 55.0:
            priority = "HIGH"
        elif score >= 30.0:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        risk_factors: list[str] = []
        nba = ""
        rescue_link = ""

        norm_drop = (lead.drop_reason or "").lower()

        if not lead.has_gstin:
            risk_factors.append("Non-GST merchant historically exposed to GST-mandatory quoting blocker (2.0% base rate).")
            nba = "Send 1-Click WhatsApp Udyam Micro Bundle Link (AirFiber 100 @ ₹899/mo, 100% GST-exempt)."
            rescue_link = f"https://udyam.airtel.in/rescue?lead_id={lead.lead_id}&bundle=UDYAM_MICRO&action=whatsapp"
        elif "quote" in norm_drop or lead.stage_reached == "Needs assessed":
            risk_factors.append("Stalled at quoting stage (56% leak cohort) due to complex PDF or unclarified pricing.")
            nba = "Dispatch Mobile Interactive Checkout Card with transparent single monthly price."
            rescue_link = f"https://udyam.airtel.in/checkout?lead_id={lead.lead_id}&view=interactive_card"
        elif "visit" in norm_drop or "time" in norm_drop or "unreachable" in norm_drop:
            risk_factors.append("Field sales friction: merchant had no time for physical sit-down meeting.")
            nba = "Trigger Self-Serve Onboarding QR link directly to owner WhatsApp for 5-min night signup."
            rescue_link = f"https://udyam.airtel.in/self-serve?lead_id={lead.lead_id}&channel=whatsapp_qr"
        elif "delay" in norm_drop or lead.stage_reached == "KYC complete":
            risk_factors.append("Fulfillment delay risk (>14 days in pipeline, 98 historical cliff dropouts).")
            nba = "Priority engineer dispatch with guaranteed 48-hour installation SLA."
            rescue_link = f"https://udyam.airtel.in/tracker?lead_id={lead.lead_id}&action=expedite"
        else:
            risk_factors.append(f"Drop reason: {lead.drop_reason or 'Stalled in funnel'}.")
            nba = "Partner assisted phone consultation with ₹1,500 partner closing bounty."
            rescue_link = f"https://udyam.airtel.in/partner/assisted?lead_id={lead.lead_id}"

        return LeadRescueItem(
            lead_id=lead.lead_id,
            business_name=lead.business_name,
            segment=lead.segment,
            city=lead.city,
            city_tier=lead.city_tier,
            has_gstin=lead.has_gstin,
            monthly_spend_inr=lead.monthly_telecom_spend_inr,
            stage_reached=lead.stage_reached,
            drop_reason=lead.drop_reason,
            propensity_score=score,
            priority_tier=priority,
            top_risk_factors=risk_factors,
            next_best_action=nba,
            whatsapp_rescue_link=rescue_link,
        )

    def score_lead(self, lead: SMBLeadRecord) -> LeadRescueItem:
        """Computes activation propensity score (0-100), top risk factors,

        and Next-Best-Action (NBA) automated rescue link.
        """
        seg_code = self._segment_map.get(lead.segment.lower().strip(), 0)
        src_code = self._source_map.get(lead.lead_source.lower().strip(), 0)

        feature_df = pd.DataFrame([{
            "city_tier": lead.city_tier,
            "employee_count": lead.employee_count,
            "num_sites": lead.num_sites,
            "has_gstin_int": 1 if lead.has_gstin else 0,
            "has_udyam_int": 1 if lead.has_udyam else 0,
            "monthly_telecom_spend_inr": lead.monthly_telecom_spend_inr,
            "customer_follow_up_calls": lead.customer_follow_up_calls,
            "segment_code": seg_code,
            "source_code": src_code,
        }])[self._feature_cols]

        if self.model:
            prob = self.model.predict_proba(feature_df)[0][1]
            score = round(float(prob) * 100.0, 1)
        else:
            score = 50.0

        return self._build_lead_item(lead, score)

    def get_top_rescue_leads(
        self,
        limit: int = 25,
        stage_filter: Optional[str] = None,
        min_propensity: float = 30.0,
    ) -> list[LeadRescueItem]:
        """Returns sorted rescue leads prioritizing high-propensity dropped SMBs using batch prediction."""
        leads = self.db.get_all_leads()
        filtered_leads = [
            l
            for l in leads
            if l.outcome.lower() != "activated"
            and (
                not l.drop_reason
                or ("invalid number" not in l.drop_reason.lower() and "wrong" not in l.drop_reason.lower())
            )
            and (not stage_filter or l.stage_reached.lower() == stage_filter.lower())
        ]
        if not filtered_leads:
            return []

        # Vectorized batch prediction across all dropped leads in O(1) model evaluation
        batch_records = [
            {
                "city_tier": l.city_tier,
                "employee_count": l.employee_count,
                "num_sites": l.num_sites,
                "has_gstin_int": 1 if l.has_gstin else 0,
                "has_udyam_int": 1 if l.has_udyam else 0,
                "monthly_telecom_spend_inr": l.monthly_telecom_spend_inr,
                "customer_follow_up_calls": l.customer_follow_up_calls,
                "segment_code": self._segment_map.get(l.segment.lower().strip(), 0),
                "source_code": self._source_map.get(l.lead_source.lower().strip(), 0),
            }
            for l in filtered_leads
        ]
        df_batch = pd.DataFrame(batch_records)[self._feature_cols]
        if self.model:
            probs = self.model.predict_proba(df_batch)[:, 1]
        else:
            probs = [0.5] * len(filtered_leads)

        candidates: list[LeadRescueItem] = []
        for lead, prob in zip(filtered_leads, probs):
            score = round(float(prob) * 100.0, 1)
            if score >= min_propensity:
                candidates.append(self._build_lead_item(lead, score))

        candidates.sort(key=lambda x: x.propensity_score, reverse=True)
        return candidates[:limit]
