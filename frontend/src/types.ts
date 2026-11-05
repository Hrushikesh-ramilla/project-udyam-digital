export interface ProductItem {
  product_id: string;
  category: string;
  product_name: string;
  description: string;
  unit: string;
  price_min_inr_per_month: number;
  price_max_inr_per_month: number;
  one_time_setup_inr: number;
  min_contract_months: number;
  available_city_tiers: number[];
  min_employees: number;
  min_sites: number;
  requires_gstin: boolean;
  requires_one_of: string[];
  typical_install_days: number;
  target_segments: string[];
}

export interface MSMEProfileSlots {
  segment?: string | null;
  city_tier?: number | null;
  employee_count?: number | null;
  num_sites?: number | null;
  has_gstin?: boolean | null;
  monthly_budget_cap?: number | null;
  detected_needs: string[];
  is_complete: boolean;
  missing_slots: string[];
}

export interface CartItemBreakdown {
  product_id: string;
  product_name: string;
  category: string;
  quantity: number;
  unit_mrc_inr: number;
  total_mrc_inr: number;
  unit_otc_inr: number;
  total_otc_inr: number;
  install_days: number;
  requires_gstin: boolean;
}

export interface DependencyLock {
  dependent_sku: string;
  dependent_name: string;
  required_one_of: string[];
  missing: boolean;
  reason: string;
}

export interface CommercialBreakdown {
  items: CartItemBreakdown[];
  gross_mrc_inr: number;
  bundle_discount_inr: number;
  net_mrc_inr: number;
  total_otc_inr: number;
  otc_discount_inr: number;
  net_otc_inr: number;
  min_contract_months: number;
  guaranteed_sla_days: number;
  gst_exempt_eligible: boolean;
  dependency_locks: DependencyLock[];
}

export interface AdvisorResponse {
  slots: MSMEProfileSlots;
  quote?: CommercialBreakdown | null;
  recommended_skus: string[];
  display_markdown: string;
  spoken_tts_text: string;
  next_suggested_prompts: string[];
}

export interface KYCAnomaly {
  code: string;
  severity: "BLOCKER" | "WARNING" | "INFO";
  message: string;
  remediation?: string | null;
}

export interface KYCVerificationResult {
  applicant_id?: string | null;
  status: "APPROVED" | "MANUAL_REVIEW" | "REJECTED";
  anomalies: KYCAnomaly[];
  fuzzy_scores: Record<string, number>;
  dpdp_consent_verified: boolean;
  redacted_signatory_id?: string | null;
  gst_status?: string | null;
  udyam_status?: string | null;
  address_bill_age_days?: number | null;
  execution_latency_ms: number;
}

export interface LeadRescueItem {
  lead_id: string;
  business_name: string;
  segment: string;
  city: string;
  city_tier: number;
  has_gstin: boolean;
  monthly_spend_inr: number;
  stage_reached: string;
  drop_reason?: string | null;
  propensity_score: number;
  priority_tier: "HIGH" | "MEDIUM" | "LOW";
  top_risk_factors: string[];
  next_best_action: string;
  whatsapp_rescue_link: string;
}

export interface ProvisioningMilestone {
  stage_id: string;
  stage_name: string;
  status: "COMPLETED" | "IN_PROGRESS" | "PENDING";
  timestamp?: string | null;
  eta_days: number;
  description: string;
  whatsapp_preview: string;
}

export interface ProvisioningOrder {
  order_id: string;
  business_name: string;
  partner_id?: string | null;
  partner_commission_inr: number;
  bundle_name: string;
  monthly_charge_inr: number;
  total_sla_days: number;
  current_stage_idx: number;
  milestones: ProvisioningMilestone[];
  is_activated: boolean;
}

export interface JudgeScenarioResult {
  scenario_id: string;
  title: string;
  applicant: string;
  expected_outcome: string;
  expected_behavior: string;
  notes: string;
  remediation: string;
  verification_result: KYCVerificationResult;
}

