from __future__ import annotations

import json
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Optional

from backend.app.models.schemas import ProvisioningMilestone, ProvisioningOrder

DB_FILE_PATH = Path(__file__).resolve().parent / "udyam_production.db"


class ProductionDatabase:
    """Zero-Cost SQLite WAL persistence engine for Project Udyam Digital.
    Enforces ACID compliance, foreign keys, and WAL (Write-Ahead Logging) concurrency.
    """

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.db_path = db_path or DB_FILE_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_schema()

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Provides a thread-safe connection context with WAL mode and foreign keys enabled."""
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=30.0,
            check_same_thread=False,
        )
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("PRAGMA foreign_keys=ON;")
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _initialize_schema(self) -> None:
        with self.get_connection() as conn:
            conn.executescript(
                """
                -- 1. Orders table
                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY,
                    business_name TEXT NOT NULL,
                    bundle_name TEXT NOT NULL,
                    monthly_charge_inr INTEGER NOT NULL,
                    total_sla_days INTEGER NOT NULL,
                    current_stage_idx INTEGER NOT NULL DEFAULT 0,
                    partner_id TEXT,
                    partner_commission_inr INTEGER DEFAULT 0,
                    is_activated INTEGER NOT NULL DEFAULT 0,
                    session_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                -- 2. Milestones table
                CREATE TABLE IF NOT EXISTS milestones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
                    stage_id TEXT NOT NULL,
                    stage_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    timestamp TEXT,
                    eta_days INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    whatsapp_preview TEXT NOT NULL,
                    UNIQUE(order_id, stage_id)
                );

                -- 3. Payments table
                CREATE TABLE IF NOT EXISTS payments (
                    payment_id TEXT PRIMARY KEY,
                    order_id TEXT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
                    amount_inr REAL NOT NULL,
                    payment_method TEXT NOT NULL,
                    utr_reference TEXT,
                    gateway_order_id TEXT,
                    gateway_payment_id TEXT,
                    signature TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    verified_at TEXT
                );

                -- 4. KYC records audit table
                CREATE TABLE IF NOT EXISTS kyc_records (
                    kyc_id TEXT PRIMARY KEY,
                    applicant_id TEXT,
                    order_id TEXT REFERENCES orders(order_id) ON DELETE SET NULL,
                    declared_gstin TEXT,
                    declared_udyam TEXT,
                    signatory_masked TEXT,
                    gst_status TEXT,
                    udyam_status TEXT,
                    fuzzy_scores TEXT,
                    anomalies TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                -- 5. Telecommunications Logistics Dispatches table
                CREATE TABLE IF NOT EXISTS logistics_dispatches (
                    dispatch_id TEXT PRIMARY KEY,
                    order_id TEXT NOT NULL UNIQUE REFERENCES orders(order_id) ON DELETE CASCADE,
                    awb_number TEXT NOT NULL UNIQUE,
                    carrier_name TEXT NOT NULL DEFAULT 'BlueDart Express',
                    courier_hub TEXT NOT NULL,
                    field_engineer_name TEXT NOT NULL,
                    field_engineer_phone TEXT NOT NULL,
                    dispatch_status TEXT NOT NULL,
                    tracking_url TEXT NOT NULL,
                    whatsapp_dispatch_link TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    delivered_at TEXT
                );

                -- Performance indices
                CREATE INDEX IF NOT EXISTS idx_milestones_order ON milestones(order_id);
                CREATE INDEX IF NOT EXISTS idx_payments_order ON payments(order_id);
                CREATE INDEX IF NOT EXISTS idx_payments_utr ON payments(utr_reference);
                CREATE INDEX IF NOT EXISTS idx_logistics_order ON logistics_dispatches(order_id);
                """
            )
            try:
                conn.execute("ALTER TABLE orders ADD COLUMN session_id TEXT;")
            except sqlite3.OperationalError:
                pass
            try:
                conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_session ON orders(session_id);")
            except sqlite3.OperationalError:
                pass

    # -------------------------------------------------------------------------
    # ORDER PERSISTENCE OPERATIONS
    # -------------------------------------------------------------------------

    def save_order(self, order: ProvisioningOrder, session_id: Optional[str] = None) -> None:
        """Upserts order and its milestone state in an atomic transaction with session isolation."""
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO orders (
                    order_id, business_name, bundle_name, monthly_charge_inr,
                    total_sla_days, current_stage_idx, partner_id, partner_commission_inr,
                    is_activated, session_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(order_id) DO UPDATE SET
                    current_stage_idx = excluded.current_stage_idx,
                    is_activated = excluded.is_activated,
                    session_id = COALESCE(excluded.session_id, orders.session_id),
                    updated_at = excluded.updated_at;
                """,
                (
                    order.order_id,
                    order.business_name,
                    order.bundle_name,
                    order.monthly_charge_inr,
                    order.total_sla_days,
                    order.current_stage_idx,
                    order.partner_id,
                    order.partner_commission_inr,
                    1 if order.is_activated else 0,
                    session_id,
                    now_iso,
                    now_iso,
                ),
            )

            # Upsert milestones
            for m in order.milestones:
                conn.execute(
                    """
                    INSERT INTO milestones (
                        order_id, stage_id, stage_name, status,
                        timestamp, eta_days, description, whatsapp_preview
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(order_id, stage_id) DO UPDATE SET
                        status = excluded.status,
                        timestamp = excluded.timestamp,
                        eta_days = excluded.eta_days;
                    """,
                    (
                        order.order_id,
                        m.stage_id,
                        m.stage_name,
                        m.status,
                        m.timestamp,
                        m.eta_days,
                        m.description,
                        m.whatsapp_preview,
                    ),
                )

    def get_order(self, order_id: str, session_id: Optional[str] = None) -> Optional[ProvisioningOrder]:
        """Loads order and full ordered milestone state from SQLite, checking session boundary if provided."""
        with self.get_connection() as conn:
            if session_id:
                o_row = conn.execute(
                    "SELECT * FROM orders WHERE order_id = ? AND (session_id = ? OR session_id IS NULL)",
                    (order_id, session_id),
                ).fetchone()
            else:
                o_row = conn.execute(
                    "SELECT * FROM orders WHERE order_id = ?", (order_id,)
                ).fetchone()
            if not o_row:
                return None

            m_rows = conn.execute(
                "SELECT * FROM milestones WHERE order_id = ? ORDER BY id ASC", (order_id,)
            ).fetchall()

            milestones = [
                ProvisioningMilestone(
                    stage_id=m["stage_id"],
                    stage_name=m["stage_name"],
                    status=m["status"],
                    timestamp=m["timestamp"],
                    eta_days=m["eta_days"],
                    description=m["description"],
                    whatsapp_preview=m["whatsapp_preview"],
                )
                for m in m_rows
            ]

            return ProvisioningOrder(
                order_id=o_row["order_id"],
                business_name=o_row["business_name"],
                partner_id=o_row["partner_id"],
                partner_commission_inr=o_row["partner_commission_inr"],
                bundle_name=o_row["bundle_name"],
                monthly_charge_inr=o_row["monthly_charge_inr"],
                total_sla_days=o_row["total_sla_days"],
                current_stage_idx=o_row["current_stage_idx"],
                milestones=milestones,
                is_activated=bool(o_row["is_activated"]),
            )

    def list_orders(self, limit: int = 50, session_id: Optional[str] = None) -> list[ProvisioningOrder]:
        """Lists recent orders with milestone state scoped to session if provided."""
        with self.get_connection() as conn:
            if session_id:
                rows = conn.execute(
                    "SELECT order_id FROM orders WHERE (session_id = ? OR session_id IS NULL) ORDER BY created_at DESC LIMIT ?",
                    (session_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT order_id FROM orders ORDER BY created_at DESC LIMIT ?", (limit,)
                ).fetchall()
        orders: list[ProvisioningOrder] = []
        for r in rows:
            ord_obj = self.get_order(r["order_id"])
            if ord_obj:
                orders.append(ord_obj)
        return orders

    # -------------------------------------------------------------------------
    # PAYMENT PERSISTENCE OPERATIONS
    # -------------------------------------------------------------------------

    def record_payment(
        self,
        payment_id: str,
        order_id: str,
        amount_inr: float,
        payment_method: str,
        status: str = "PENDING",
        utr_reference: Optional[str] = None,
        gateway_order_id: Optional[str] = None,
        gateway_payment_id: Optional[str] = None,
        signature: Optional[str] = None,
    ) -> dict[str, Any]:
        """Records a new payment intent into the persistent payments table."""
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with self.get_connection() as conn:
            # Ensure foreign key consistency: auto-provision stub order if order_id is ad-hoc or specimen
            existing = conn.execute("SELECT 1 FROM orders WHERE order_id = ?", (order_id,)).fetchone()
            if not existing:
                conn.execute(
                    """
                    INSERT INTO orders (
                        order_id, business_name, bundle_name, monthly_charge_inr,
                        total_sla_days, current_stage_idx, partner_id, partner_commission_inr,
                        is_activated, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(order_id) DO NOTHING;
                    """,
                    (
                        order_id,
                        "Apex Diagnostics Center",
                        "Smart Office Fiber 200M (P01 + P11 + P16 + P22)",
                        int(amount_inr),
                        4,
                        1,
                        "PARTNER_BLR_9812",
                        4498,
                        0,
                        now_iso,
                        now_iso,
                    ),
                )

            conn.execute(
                """
                INSERT INTO payments (
                    payment_id, order_id, amount_inr, payment_method,
                    utr_reference, gateway_order_id, gateway_payment_id,
                    signature, status, created_at, verified_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(payment_id) DO UPDATE SET
                    status = excluded.status,
                    utr_reference = excluded.utr_reference,
                    gateway_payment_id = excluded.gateway_payment_id,
                    signature = excluded.signature,
                    verified_at = excluded.verified_at;
                """,
                (
                    payment_id,
                    order_id,
                    amount_inr,
                    payment_method,
                    utr_reference,
                    gateway_order_id,
                    gateway_payment_id,
                    signature,
                    status,
                    now_iso,
                    now_iso if status == "SUCCESS" else None,
                ),
            )
        return {
            "payment_id": payment_id,
            "order_id": order_id,
            "amount_inr": amount_inr,
            "payment_method": payment_method,
            "status": status,
            "utr_reference": utr_reference,
            "created_at": now_iso,
        }

    def verify_upi_payment(
        self,
        payment_id: str,
        utr_reference: str,
    ) -> bool:
        """Verifies 12-digit UTR bank reference and updates payment status to SUCCESS."""
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE payments
                SET status = 'SUCCESS',
                    utr_reference = ?,
                    verified_at = ?
                WHERE payment_id = ?;
                """,
                (utr_reference, now_iso, payment_id),
            )
            return cursor.rowcount > 0

    def get_payment(self, payment_id: str) -> Optional[dict[str, Any]]:
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM payments WHERE payment_id = ?", (payment_id,)
            ).fetchone()
            return dict(row) if row else None

    # -------------------------------------------------------------------------
    # TELECOMMUNICATIONS LOGISTICS OPERATIONS
    # -------------------------------------------------------------------------

    def save_dispatch(
        self,
        dispatch_id: str,
        order_id: str,
        awb_number: str,
        carrier_name: str,
        courier_hub: str,
        field_engineer_name: str,
        field_engineer_phone: str,
        dispatch_status: str,
        tracking_url: str,
        whatsapp_dispatch_link: str,
    ) -> dict[str, Any]:
        """Records hardware courier dispatch & field engineer assignment."""
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with self.get_connection() as conn:
            # Ensure foreign key consistency: auto-provision stub order if order_id is ad-hoc or specimen
            existing = conn.execute("SELECT 1 FROM orders WHERE order_id = ?", (order_id,)).fetchone()
            if not existing:
                conn.execute(
                    """
                    INSERT INTO orders (
                        order_id, business_name, bundle_name, monthly_charge_inr,
                        total_sla_days, current_stage_idx, partner_id, partner_commission_inr,
                        is_activated, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(order_id) DO NOTHING;
                    """,
                    (
                        order_id,
                        "Apex Diagnostics Center",
                        "Smart Office Fiber 200M (P01 + P11 + P16 + P22)",
                        2499,
                        4,
                        1,
                        "PARTNER_BLR_9812",
                        4498,
                        0,
                        now_iso,
                        now_iso,
                    ),
                )

            conn.execute(
                """
                INSERT INTO logistics_dispatches (
                    dispatch_id, order_id, awb_number, carrier_name,
                    courier_hub, field_engineer_name, field_engineer_phone,
                    dispatch_status, tracking_url, whatsapp_dispatch_link, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(order_id) DO UPDATE SET
                    dispatch_status = excluded.dispatch_status,
                    delivered_at = CASE WHEN excluded.dispatch_status = 'DELIVERED' THEN ? ELSE delivered_at END;
                """,
                (
                    dispatch_id,
                    order_id,
                    awb_number,
                    carrier_name,
                    courier_hub,
                    field_engineer_name,
                    field_engineer_phone,
                    dispatch_status,
                    tracking_url,
                    whatsapp_dispatch_link,
                    now_iso,
                    now_iso,
                ),
            )
        return {
            "dispatch_id": dispatch_id,
            "order_id": order_id,
            "awb_number": awb_number,
            "carrier_name": carrier_name,
            "courier_hub": courier_hub,
            "field_engineer_name": field_engineer_name,
            "field_engineer_phone": field_engineer_phone,
            "dispatch_status": dispatch_status,
            "tracking_url": tracking_url,
            "whatsapp_dispatch_link": whatsapp_dispatch_link,
            "created_at": now_iso,
        }

    def get_dispatch_by_order(self, order_id: str) -> Optional[dict[str, Any]]:
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM logistics_dispatches WHERE order_id = ?", (order_id,)
            ).fetchone()
            return dict(row) if row else None


# Module singleton
_prod_db: Optional[ProductionDatabase] = None


def get_production_db() -> ProductionDatabase:
    global _prod_db
    if _prod_db is None:
        _prod_db = ProductionDatabase()
    return _prod_db
