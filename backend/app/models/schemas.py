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


# CPQ & DAG Schemas
class UserProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    segment: str = Field(description="Business segment: micro, prof, multi, mfg")
    city_tier: int = Field(ge=1, le=3, description="City Tier (1 or 2)")
    employee_count: int = Field(ge=1, description="Total employee count")
    num_sites: int = Field(ge=1, description="Number of operational branches/sites")
    has_gstin: bool = Field(description="Whether the business has an active GSTIN")
    detected_needs: list[str] = Field(default_factory=list, description="Extracted needs tags")
    monthly_budget_cap: Optional[int] = Field(default=None, description="Optional monthly budget cap in INR")


class CartItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product_id: str
    quantity: int = Field(default=1, ge=1)


class CartItemBreakdown(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product_id: str
    product_name: str
    category: str
    quantity: int
    unit_mrc_inr: int
    total_mrc_inr: int
    unit_otc_inr: int
    total_otc_inr: int
    install_days: int
    requires_gstin: bool


class DependencyLock(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dependent_sku: str
    dependent_name: str
    required_one_of: list[str]
    missing: bool
    reason: str


class CommercialBreakdown(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[CartItemBreakdown]
    gross_mrc_inr: int
    bundle_discount_inr: int
    net_mrc_inr: int
    total_otc_inr: int
    otc_discount_inr: int
    net_otc_inr: int
    min_contract_months: int
    guaranteed_sla_days: int
    gst_exempt_eligible: bool
    dependency_locks: list[DependencyLock]


class ReverseBudgetResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    budget_inr: int
    selected_skus: list[str]
    commercials: CommercialBreakdown
    utility_score: float
    rationale: str


# Advisor Schemas
class MSMEProfileSlots(BaseModel):
    model_config = ConfigDict(extra="forbid")

    segment: Optional[str] = Field(default=None, description="micro, prof, multi, mfg")
    city_tier: Optional[int] = Field(default=None, ge=1, le=3, description="1, 2, or 3")
    employee_count: Optional[int] = Field(default=None, ge=1, description="Number of employees")
    num_sites: Optional[int] = Field(default=None, ge=1, description="Number of locations/sites")
    has_gstin: Optional[bool] = Field(default=None, description="Whether business has active GSTIN")
    monthly_budget_cap: Optional[int] = Field(default=None, description="Monthly budget limit in INR")
    detected_needs: list[str] = Field(default_factory=list, description="Extracted needs tags")
    is_complete: bool = Field(default=False, description="Whether core slots are sufficiently populated for CPQ")
    missing_slots: list[str] = Field(default_factory=list, description="Remaining slots needed")


class AdvisorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slots: MSMEProfileSlots
    quote: Optional[CommercialBreakdown] = None
    recommended_skus: list[str] = Field(default_factory=list)
    display_markdown: str = Field(description="Formatted markdown response for chat UI")
    spoken_tts_text: str = Field(description="Clean, symbol-free text for browser TTS voice playback")
    next_suggested_prompts: list[str] = Field(default_factory=list)
    display_latin: Optional[str] = Field(default=None, description="Response rendered in English/Latin alphabet")
    display_native: Optional[str] = Field(default=None, description="Response rendered in traditional native script")
    user_latin: Optional[str] = Field(default=None, description="User message rendered in English/Latin alphabet")
    user_native: Optional[str] = Field(default=None, description="User message rendered in traditional native script")


# KYC & DPDP Schemas
class DPDPConsentPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    consent_id: str
    user_id: str
    purpose: str
    timestamp: str
    ip_hash: str
    granted: bool


class ExtractedDocPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    file_sha256: str
    doc_type: str
    extracted_fields: dict[str, str]


class KYCAnomaly(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    severity: str  # BLOCKER, WARNING, INFO
    message: str
    remediation: Optional[str] = None


class KYCVerificationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    applicant_id: Optional[str] = None
    status: str  # APPROVED, MANUAL_REVIEW, REJECTED
    anomalies: list[KYCAnomaly]
    fuzzy_scores: dict[str, float]
    dpdp_consent_verified: bool
    redacted_signatory_id: Optional[str] = None
    gst_status: Optional[str] = None
    udyam_status: Optional[str] = None
    address_bill_age_days: Optional[int] = None
    execution_latency_ms: float


# Lead Rescue ML & Provisioning Schemas
class LeadRescueItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lead_id: str
    business_name: str
    segment: str
    city: str
    city_tier: int
    has_gstin: bool
    monthly_spend_inr: int
    stage_reached: str
    drop_reason: Optional[str] = None
    propensity_score: float
    priority_tier: str  # HIGH, MEDIUM, LOW
    top_risk_factors: list[str]
    next_best_action: str
    whatsapp_rescue_link: str


class ProvisioningMilestone(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stage_id: str
    stage_name: str
    status: str  # COMPLETED, IN_PROGRESS, PENDING
    timestamp: Optional[str] = None
    eta_days: int
    description: str
    whatsapp_preview: str


class ProvisioningOrder(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: str
    business_name: str
    partner_id: Optional[str] = None
    partner_commission_inr: int = 0
    bundle_name: str
    monthly_charge_inr: int
    total_sla_days: int
    current_stage_idx: int
    milestones: list[ProvisioningMilestone]
    is_activated: bool


# API Request Schemas
class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_message: str
    previous_slots: Optional[MSMEProfileSlots] = None
    language_code: Optional[str] = None
    script_mode: Optional[str] = None


class CalculateQuoteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cart: list[CartItem]
    contract_months: int = 12


class OptimizeBudgetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile: UserProfile
    max_monthly_budget: int


class CreateOrderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    business_name: str
    bundle_name: str
    monthly_charge_inr: int
    total_sla_days: int = 4
    partner_id: Optional[str] = None


class KYCVerifyAPIRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    applicant_preset: Optional[str] = None  # K01, K03, K05, K07, K11, K12
    applicant_id: Optional[str] = None  # Alias for applicant_preset
    cart_requires_gstin: bool = True
    consent: Optional[DPDPConsentPayload] = None
    custom_doc_hashes: Optional[dict[str, str]] = None




