from __future__ import annotations

import time
import urllib.parse
import uuid
from typing import Any, Optional

from backend.app.db.sqlite_engine import ProductionDatabase, get_production_db
from backend.app.services.provisioning_tracker import get_provisioning_tracker

REGIONAL_HUBS = [
    {"city": "Gwalior", "hub": "Airtel Logistics Hub, South City Centre, Gwalior (MP)", "engineer": "Rajesh Kumar", "phone": "+91 98765 43210"},
    {"city": "Delhi NCR", "hub": "Airtel Enterprise Fulfillment Hub, Okhla Phase III, New Delhi", "engineer": "Amit Verma", "phone": "+91 98101 23456"},
    {"city": "Mumbai", "hub": "Airtel Metro Gateway Hub, BKC Western Hub, Mumbai", "engineer": "Sunil Shinde", "phone": "+91 98202 34567"},
    {"city": "Bengaluru", "hub": "Airtel Tech Park Logistics Center, Whitefield, Bengaluru", "engineer": "Karthik Raja", "phone": "+91 98450 12345"},
]


class LogisticsEngine:
    """Telecommunications hardware logistics & field engineer assignment event bus."""

    def __init__(self, db: Optional[ProductionDatabase] = None) -> None:
        self.db = db or get_production_db()
        self.tracker = get_provisioning_tracker()

    def dispatch_hardware(
        self,
        order_id: str,
        city_hint: str = "Gwalior",
    ) -> dict[str, Any]:
        """Dispatches hardware CPE unit, generates BlueDart AWB, assigns engineer, and saves event."""
        existing = self.db.get_dispatch_by_order(order_id)
        if existing:
            return existing

        # Match regional hub
        hub_info = REGIONAL_HUBS[0]
        for h in REGIONAL_HUBS:
            if h["city"].lower() in city_hint.lower():
                hub_info = h
                break

        dispatch_id = f"DISPATCH-{uuid.uuid4().hex[:8].upper()}"
        awb_number = f"BD-AIRTEL-{uuid.uuid4().hex[:6].upper()}"
        carrier_name = "BlueDart Express Surface Priority"
        courier_hub = hub_info["hub"]
        field_engineer = hub_info["engineer"]
        engineer_phone = hub_info["phone"]
        dispatch_status = "DISPATCHED"

        tracking_url = f"https://www.bluedart.com/tracking?awb={awb_number}"

        wa_text = (
            f"Namaste! Your Airtel Business Enterprise hardware has been dispatched!\n\n"
            f"📦 Order ID: {order_id}\n"
            f"🚚 Courier: {carrier_name}\n"
            f"📑 Tracking AWB: {awb_number}\n"
            f"👷 Field Engineer: {field_engineer} ({engineer_phone})\n"
            f"📍 Origin Hub: {courier_hub}\n\n"
            f"Track live delivery: https://udyam.hrushikeshramilla.in/track?order_id={order_id}"
        )
        whatsapp_link = f"https://wa.me/{engineer_phone.replace(' ', '').replace('+', '')}?text={urllib.parse.quote(wa_text)}"

        record = self.db.save_dispatch(
            dispatch_id=dispatch_id,
            order_id=order_id,
            awb_number=awb_number,
            carrier_name=carrier_name,
            courier_hub=courier_hub,
            field_engineer_name=field_engineer,
            field_engineer_phone=engineer_phone,
            dispatch_status=dispatch_status,
            tracking_url=tracking_url,
            whatsapp_dispatch_link=whatsapp_link,
        )

        return record

    def get_dispatch_details(self, order_id: str) -> Optional[dict[str, Any]]:
        record = self.db.get_dispatch_by_order(order_id)
        if not record:
            # Auto-create if order exists
            order = self.tracker.get_order(order_id)
            if order:
                return self.dispatch_hardware(order_id, "Gwalior")
        return record


# Global singleton
_logistics_instance: Optional[LogisticsEngine] = None


def get_logistics_engine() -> LogisticsEngine:
    global _logistics_instance
    if _logistics_instance is None:
        _logistics_instance = LogisticsEngine()
    return _logistics_instance
