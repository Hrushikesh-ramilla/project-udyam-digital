from __future__ import annotations

import csv
import os
import re
import time
from pathlib import Path
from typing import Optional

from backend.app.models.schemas import (
    GSTINRecord,
    ProductItem,
    SMBLeadRecord,
    UdyamRecord,
)

# Deterministic regex patterns per AGENTS.md constitution
# Accepts synthetic 'X' as 4th char of embedded PAN (char index 5)
GSTIN_REGEX = re.compile(r"^[0-9]{2}[A-Z]{3}[ABCFGHLJPTFX][A-Z][0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$")
# Synthetic Udyam format accepting synthetic district code '00'
UDYAM_REGEX = re.compile(r"^UDYAM-[A-Z]{2}-00-[0-9]{7}$")


class RegistryDatabase:
    """In-memory O(1) hash-indexed database for synthetic telecom enterprise registries."""

    def __init__(self, data_dir: Optional[Path | str] = None) -> None:
        if data_dir is None:
            # Look for data directory relative to repo root
            current_path = Path(__file__).resolve()
            # Climb up until we find data/ or project root
            repo_root = current_path.parents[3] if len(current_path.parents) >= 4 else Path.cwd()
            candidate = repo_root / "data"
            if candidate.exists():
                self.data_dir = candidate
            else:
                self.data_dir = Path.cwd() / "data"
        else:
            self.data_dir = Path(data_dir)

        self._gstin_index: dict[str, GSTINRecord] = {}
        self._udyam_index: dict[str, UdyamRecord] = {}
        self._product_index: dict[str, ProductItem] = {}
        self._leads_index: dict[str, SMBLeadRecord] = {}
        self._is_loaded = False

    def load_all(self) -> None:
        """Loads and indexes all registries into high-speed memory maps."""
        if self._is_loaded:
            return

        self._load_products()
        self._load_gstin_registry()
        self._load_udyam_registry()
        self._load_smb_leads()
        self._is_loaded = True

    def _load_products(self) -> None:
        filepath = self.data_dir / "product_catalogue.csv"
        if not filepath.exists():
            raise FileNotFoundError(f"Missing product catalogue: {filepath}")

        with open(filepath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                pid = row["product_id"].strip()
                # Parse city tiers "1;2" or "1"
                tiers_str = row["available_city_tiers"].strip()
                tiers = [int(t.strip()) for t in tiers_str.split(";") if t.strip().isdigit()]

                # Parse requires_one_of "P01|P02" -> list
                req_one_str = row.get("requires_one_of", "").strip()
                req_one = [x.strip() for x in req_one_str.split("|") if x.strip()] if req_one_str else []

                # Parse target_segments "micro;prof" -> list
                targets_str = row.get("target_segments", "").strip()
                targets = [x.strip() for x in targets_str.split(";") if x.strip()] if targets_str else []

                item = ProductItem(
                    product_id=pid,
                    category=row["category"].strip(),
                    product_name=row["product_name"].strip(),
                    description=row["description"].strip(),
                    unit=row["unit"].strip(),
                    price_min_inr_per_month=int(row["price_min_inr_per_month"]),
                    price_max_inr_per_month=int(row["price_max_inr_per_month"]),
                    one_time_setup_inr=int(row["one_time_setup_inr"]),
                    min_contract_months=int(row["min_contract_months"]),
                    available_city_tiers=tiers,
                    min_employees=int(row["min_employees"]),
                    min_sites=int(row["min_sites"]),
                    requires_gstin=row["requires_gstin"].strip().upper() == "Y",
                    requires_one_of=req_one,
                    typical_install_days=int(row["typical_install_days"]),
                    target_segments=targets,
                )
                self._product_index[pid] = item

    def _load_gstin_registry(self) -> None:
        filepath = self.data_dir / "mock_gstin_registry.csv"
        if not filepath.exists():
            raise FileNotFoundError(f"Missing GSTIN registry: {filepath}")

        with open(filepath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                gstin = row["gstin"].strip().upper()
                rec = GSTINRecord(
                    gstin=gstin,
                    legal_name=row["legal_name"].strip(),
                    trade_name=row["trade_name"].strip(),
                    constitution=row["constitution"].strip(),
                    principal_place_of_business=row["principal_place_of_business"].strip(),
                    state=row["state"].strip(),
                    registration_date=row["registration_date"].strip(),
                    status=row["status"].strip(),
                )
                self._gstin_index[gstin] = rec

    def _load_udyam_registry(self) -> None:
        filepath = self.data_dir / "mock_udyam_registry.csv"
        if not filepath.exists():
            raise FileNotFoundError(f"Missing Udyam registry: {filepath}")

        with open(filepath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                udyam = row["udyam_number"].strip().upper()
                rec = UdyamRecord(
                    udyam_number=udyam,
                    enterprise_name=row["enterprise_name"].strip(),
                    enterprise_type=row["enterprise_type"].strip(),
                    major_activity=row["major_activity"].strip(),
                    nic_description=row["nic_description"].strip(),
                    state=row["state"].strip(),
                    city=row["city"].strip(),
                    date_of_registration=row["date_of_registration"].strip(),
                )
                self._udyam_index[udyam] = rec

    def _load_smb_leads(self) -> None:
        filepath = self.data_dir / "smb_leads.csv"
        if not filepath.exists():
            raise FileNotFoundError(f"Missing SMB leads data: {filepath}")

        with open(filepath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                lid = row["lead_id"].strip()
                poi_str = row.get("products_of_interest", "").strip()
                pois = [p.strip() for p in poi_str.split(";") if p.strip()]

                def opt_str(val: Optional[str]) -> Optional[str]:
                    if val is None or not val.strip() or val.strip().lower() == "nan":
                        return None
                    return val.strip()

                def opt_float(val: Optional[str]) -> Optional[float]:
                    if val is None or not val.strip() or val.strip().lower() == "nan":
                        return None
                    try:
                        return float(val.strip())
                    except ValueError:
                        return None

                rec = SMBLeadRecord(
                    lead_id=lid,
                    created_date=row["created_date"].strip(),
                    lead_source=row["lead_source"].strip(),
                    business_name=row["business_name"].strip(),
                    business_type=row["business_type"].strip(),
                    segment=row["segment"].strip(),
                    city=row["city"].strip(),
                    city_tier=int(row["city_tier"]),
                    state=row["state"].strip(),
                    preferred_language=row["preferred_language"].strip(),
                    employee_count=int(row["employee_count"]),
                    num_sites=int(row["num_sites"]),
                    annual_turnover_band=row["annual_turnover_band"].strip(),
                    has_gstin=row["has_gstin"].strip().upper() == "Y",
                    gstin=opt_str(row.get("gstin")),
                    has_udyam=row["has_udyam"].strip().upper() == "Y",
                    udyam_number=opt_str(row.get("udyam_number")),
                    current_internet=opt_str(row.get("current_internet")),
                    current_provider=opt_str(row.get("current_provider")),
                    monthly_telecom_spend_inr=int(row["monthly_telecom_spend_inr"]),
                    products_of_interest=pois,
                    contact_name=row["contact_name"].strip(),
                    contact_role=row["contact_role"].strip(),
                    stage_reached=row["stage_reached"].strip(),
                    outcome=row["outcome"].strip(),
                    drop_reason=opt_str(row.get("drop_reason")),
                    contacted_date=opt_str(row.get("contacted_date")),
                    needs_assessed_date=opt_str(row.get("needs_assessed_date")),
                    quote_accepted_date=opt_str(row.get("quote_accepted_date")),
                    kyc_complete_date=opt_str(row.get("kyc_complete_date")),
                    activated_date=opt_str(row.get("activated_date")),
                    days_lead_to_activation=opt_float(row.get("days_lead_to_activation")),
                    customer_follow_up_calls=int(row["customer_follow_up_calls"]),
                    bundle_products=opt_str(row.get("bundle_products")),
                    monthly_bundle_value_inr=opt_float(row.get("monthly_bundle_value_inr")),
                    one_time_setup_inr=opt_float(row.get("one_time_setup_inr")),
                    contract_months=opt_float(row.get("contract_months")),
                    churned_within_6_months=opt_str(row.get("churned_within_6_months")),
                    nps_score=opt_float(row.get("nps_score")),
                    acquisition_cost_inr=int(row["acquisition_cost_inr"]),
                )
                self._leads_index[lid] = rec

    # O(1) Accessors
    def lookup_gstin(self, gstin: str) -> tuple[Optional[GSTINRecord], float]:
        """O(1) GSTIN lookup returning record and query execution latency in ms."""
        start = time.perf_counter()
        normalized = gstin.strip().upper()
        record = self._gstin_index.get(normalized)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return record, elapsed_ms

    def lookup_udyam(self, udyam_number: str) -> tuple[Optional[UdyamRecord], float]:
        """O(1) Udyam lookup returning record and query execution latency in ms."""
        start = time.perf_counter()
        normalized = udyam_number.strip().upper()
        record = self._udyam_index.get(normalized)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return record, elapsed_ms

    def get_product(self, product_id: str) -> Optional[ProductItem]:
        return self._product_index.get(product_id.strip().upper())

    def get_all_products(self) -> list[ProductItem]:
        return list(self._product_index.values())

    def get_lead(self, lead_id: str) -> Optional[SMBLeadRecord]:
        return self._leads_index.get(lead_id.strip().upper())

    def get_all_leads(self) -> list[SMBLeadRecord]:
        return list(self._leads_index.values())

    @property
    def product_count(self) -> int:
        return len(self._product_index)

    @property
    def gstin_count(self) -> int:
        return len(self._gstin_index)

    @property
    def udyam_count(self) -> int:
        return len(self._udyam_index)

    @property
    def lead_count(self) -> int:
        return len(self._leads_index)


# Global singleton instance
_registry_instance: Optional[RegistryDatabase] = None


def get_registry(data_dir: Optional[Path | str] = None) -> RegistryDatabase:
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = RegistryDatabase(data_dir=data_dir)
        _registry_instance.load_all()
    return _registry_instance
