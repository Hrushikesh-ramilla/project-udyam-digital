from __future__ import annotations

import time
import uuid
from typing import Optional

from backend.app.models.schemas import ProvisioningMilestone, ProvisioningOrder

STAGES_METADATA = [
    {
        "id": "ORDER_PLACED",
        "name": "Order Confirmed & Cart Locked",
        "desc": "Commercial quote confirmed, bundle SKUs reserved, and digital order registered.",
        "whatsapp": "Namaste! Your Airtel Business order #{order_id} for {bundle_name} is confirmed. Track live status anytime here: {tracker_url}",
    },
    {
        "id": "FEASIBILITY_VERIFIED",
        "name": "Coverage & Port Feasibility Approved",
        "desc": "Local distribution point port availability and 5G/Fiber coverage verified.",
        "whatsapp": "Great news! Port feasibility confirmed at your premises. Next step: complete your 2-minute Smart KYC.",
    },
    {
        "id": "KYC_APPROVED",
        "name": "Smart KYC Verified & Agreement Stamped",
        "desc": "Registry verification passed, DPDP consent logged, digital agreement counter-signed.",
        "whatsapp": "Smart KYC Approved! Your digital contract is stamped under DPDP Act 2023 compliance. Hardware is being dispatched.",
    },
    {
        "id": "HARDWARE_DISPATCHED",
        "name": "Airtel CPE & Router Dispatched",
        "desc": "Pre-configured dual-band Wi-Fi 6 router / 5G AirFiber unit dispatched via express courier.",
        "whatsapp": "Your Airtel Business hardware has been dispatched (Tracking: AWB-7729103). Delivery expected tomorrow.",
    },
    {
        "id": "ENGINEER_SCHEDULED",
        "name": "Field Engineer Assigned",
        "desc": "Certified field installation engineer assigned for on-site cabling, setup, and Wi-Fi optimization.",
        "whatsapp": "Engineer Assigned: Rajesh Kumar (+91 98765 43210) will visit your shop tomorrow between 11 AM - 1 PM.",
    },
    {
        "id": "SERVICE_ACTIVATED",
        "name": "High-Speed Service Live",
        "desc": "Bandwidth speed-test verified, 4G failover active, billing counter commenced.",
        "whatsapp": "Congratulations! Your Airtel Business connection is LIVE with 100% SLA uptime. Welcome to digital empowerment!",
    },
]


class ProvisioningTracker:
    """State machine and telemetry tracker for 6-stage enterprise provisioning."""

    def __init__(self) -> None:
        self._orders: dict[str, ProvisioningOrder] = {}

    def create_order(
        self,
        business_name: str,
        bundle_name: str,
        monthly_charge_inr: int,
        total_sla_days: int = 4,
        partner_id: Optional[str] = None,
    ) -> ProvisioningOrder:
        """Initializes a new enterprise order with milestone pipeline and partner attribution."""
        order_id = f"AIRTEL-SMB-{uuid.uuid4().hex[:8].upper()}"
        commission = int(monthly_charge_inr * 0.15) if partner_id else 0
        tracker_url = f"https://udyam.airtel.in/track?order_id={order_id}"

        milestones: list[ProvisioningMilestone] = []
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        for idx, stage in enumerate(STAGES_METADATA):
            status = "COMPLETED" if idx == 0 else "PENDING"
            ts = now_iso if idx == 0 else None
            eta = max(1, int((total_sla_days / len(STAGES_METADATA)) * (idx + 1)))

            wa_msg = stage["whatsapp"].format(
                order_id=order_id,
                bundle_name=bundle_name,
                tracker_url=tracker_url,
            )

            milestones.append(
                ProvisioningMilestone(
                    stage_id=stage["id"],
                    stage_name=stage["name"],
                    status=status,
                    timestamp=ts,
                    eta_days=eta,
                    description=stage["desc"],
                    whatsapp_preview=wa_msg,
                )
            )

        order = ProvisioningOrder(
            order_id=order_id,
            business_name=business_name,
            partner_id=partner_id,
            partner_commission_inr=commission,
            bundle_name=bundle_name,
            monthly_charge_inr=monthly_charge_inr,
            total_sla_days=total_sla_days,
            current_stage_idx=0,
            milestones=milestones,
            is_activated=False,
        )
        self._orders[order_id] = order
        return order

    def advance_stage(self, order_id: str) -> Optional[ProvisioningOrder]:
        """Advances order to the next milestone and updates status timestamps."""
        order = self._orders.get(order_id)
        if not order:
            return None

        if order.current_stage_idx < len(order.milestones) - 1:
            order.current_stage_idx += 1
            now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            order.milestones[order.current_stage_idx].status = "COMPLETED"
            order.milestones[order.current_stage_idx].timestamp = now_iso

            if order.current_stage_idx == len(order.milestones) - 1:
                order.is_activated = True

        return order

    def get_order(self, order_id: str) -> Optional[ProvisioningOrder]:
        return self._orders.get(order_id)

    def generate_obo_handshake_link(self, order: ProvisioningOrder, partner_id: str) -> str:
        """Generates cryptographically signed deep-link for assisted On-Behalf-Of (OBO) mode."""
        return (
            f"https://udyam.airtel.in/obo-approval?"
            f"order_id={order.order_id}&partner_id={partner_id}&mrc={order.monthly_charge_inr}"
        )


# Global singleton
_tracker_instance: Optional[ProvisioningTracker] = None


def get_provisioning_tracker() -> ProvisioningTracker:
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = ProvisioningTracker()
    return _tracker_instance
