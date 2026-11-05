from __future__ import annotations

from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ProductItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product_id: str = Field(description="Unique product identifier (e.g., P01)")
    category: str = Field(description="Product category (Connectivity, Security, etc.)")
    product_name: str = Field(description="Commercial product name")
    description: str = Field(description="Detailed product description")
    unit: str = Field(description="Pricing unit (per connection, per user, etc.)")
    price_min_inr_per_month: int = Field(ge=0, description="Minimum monthly price in INR")
    price_max_inr_per_month: int = Field(ge=0, description="Maximum monthly price in INR")
    one_time_setup_inr: int = Field(ge=0, description="One-time installation or setup fee in INR")
    min_contract_months: int = Field(ge=0, description="Minimum required contract duration in months")
    available_city_tiers: list[int] = Field(description="List of eligible city tiers (e.g., [1, 2])")
    min_employees: int = Field(ge=0, description="Minimum employee threshold")
    min_sites: int = Field(ge=0, description="Minimum site/branch threshold")
    requires_gstin: bool = Field(description="True if product requires active GSTIN")
    requires_one_of: list[str] = Field(default_factory=list, description="List of prerequisite parent product IDs")
    typical_install_days: int = Field(ge=0, description="Expected SLA turnaround days for activation")
    target_segments: list[str] = Field(description="Target business segments (micro, prof, multi, mfg)")


class GSTINRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gstin: str = Field(description="15-character GST identification number")
    legal_name: str = Field(description="Registered legal business or proprietor name")
    trade_name: str = Field(description="Operating trade name")
    constitution: str = Field(description="Business constitution (Proprietorship, Private Limited, LLP, etc.)")
    principal_place_of_business: str = Field(description="Registered address of principal place of business")
    state: str = Field(description="State name")
    registration_date: str = Field(description="Date of registration in YYYY-MM-DD format")
    status: str = Field(description="Taxpayer status: Active, Cancelled, Suspended, etc.")


class UdyamRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    udyam_number: str = Field(description="Official Udyam registration number (e.g. UDYAM-XX-00-XXXXXXX)")
    enterprise_name: str = Field(description="Registered enterprise name")
    enterprise_type: str = Field(description="Micro, Small, or Medium")
    major_activity: str = Field(description="Manufacturing or Services")
    nic_description: str = Field(description="National Industrial Classification description")
    state: str = Field(description="State of registered office")
    city: str = Field(description="City of registered office")
    date_of_registration: str = Field(description="Registration date in YYYY-MM-DD format")


class SMBLeadRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lead_id: str
    created_date: str
    lead_source: str
    business_name: str
    business_type: str
    segment: str
    city: str
    city_tier: int
    state: str
    preferred_language: str
    employee_count: int
    num_sites: int
    annual_turnover_band: str
    has_gstin: bool
    gstin: Optional[str] = None
    has_udyam: bool
    udyam_number: Optional[str] = None
    current_internet: Optional[str] = None
    current_provider: Optional[str] = None
    monthly_telecom_spend_inr: int
    products_of_interest: list[str]
    contact_name: str
    contact_role: str
    stage_reached: str
    outcome: str
    drop_reason: Optional[str] = None
    contacted_date: Optional[str] = None
    needs_assessed_date: Optional[str] = None
    quote_accepted_date: Optional[str] = None
    kyc_complete_date: Optional[str] = None
    activated_date: Optional[str] = None
    days_lead_to_activation: Optional[float] = None
    customer_follow_up_calls: int
    bundle_products: Optional[str] = None
    monthly_bundle_value_inr: Optional[float] = None
    one_time_setup_inr: Optional[float] = None
    contract_months: Optional[float] = None
    churned_within_6_months: Optional[str] = None
    nps_score: Optional[float] = None
    acquisition_cost_inr: int


class RegistryLookupResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    found: bool
    entity_type: str
    record: Optional[dict] = None
    query_latency_ms: float
