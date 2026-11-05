import {
  AdvisorResponse,
  CommercialBreakdown,
  JudgeScenarioResult,
  KYCVerificationResult,
  LeadRescueItem,
  MSMEProfileSlots,
  ProductItem,
  ProvisioningOrder,
} from "./types";

const API_BASE = "/api";

export async function fetchProducts(): Promise<ProductItem[]> {
  try {
    const res = await fetch(`${API_BASE}/products`);
    if (!res.ok) throw new Error("Failed to fetch products");
    return await res.json();
  } catch (err) {
    console.error("API error, using fallback products", err);
    return [];
  }
}

export async function sendChatMessage(
  message: string,
  previousSlots?: MSMEProfileSlots | null
): Promise<AdvisorResponse> {
  const res = await fetch(`${API_BASE}/advisor/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_message: message, previous_slots: previousSlots }),
  });
  if (!res.ok) throw new Error("Chat request failed");
  return await res.json();
}

export async function calculateQuote(
  cart: { product_id: string; quantity: number }[],
  contractMonths: number = 12
): Promise<CommercialBreakdown> {
  const res = await fetch(`${API_BASE}/cpq/calculate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ cart, contract_months: contractMonths }),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({ detail: "Calculation failed" }));
    throw new Error(errData.detail || "Calculation failed");
  }
  return await res.json();
}

export async function optimizeBudget(
  profile: {
    segment: string;
    city_tier: number;
    employee_count: number;
    num_sites: number;
    has_gstin: boolean;
    detected_needs: string[];
    monthly_budget_cap?: number | null;
  },
  maxBudget: number
): Promise<{
  budget_inr: number;
  selected_skus: string[];
  commercials: CommercialBreakdown;
  utility_score: number;
  rationale: string;
}> {
  const res = await fetch(`${API_BASE}/cpq/optimize-budget`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ profile, max_monthly_budget: maxBudget }),
  });
  if (!res.ok) throw new Error("Budget optimization failed");
  return await res.json();
}

export async function verifyKYC(
  preset?: string,
  cartRequiresGstin: boolean = true
): Promise<KYCVerificationResult> {
  const res = await fetch(`${API_BASE}/kyc/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      applicant_preset: preset,
      cart_requires_gstin: cartRequiresGstin,
      consent: {
        consent_id: `CONSENT_${Date.now()}`,
        user_id: "MERCHANT_USER",
        purpose: "Telecom onboarding, GSTN/Udyam verification, and DPDP Act 2023 compliance.",
        timestamp: "2026-07-15T10:00:00Z",
        ip_hash: "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae",
        granted: true,
      },
    }),
  });
  if (!res.ok) throw new Error("KYC verification failed");
  return await res.json();
}

export interface KYCUploadResponse {
  filename: string;
  size_bytes: number;
  file_sha256: string;
  doc_type: string;
  extracted_fields: Record<string, string>;
  single_doc_result?: KYCVerificationResult;
  verification_result: KYCVerificationResult;
}

export async function uploadKYCDocument(
  file: File,
  docType: string = "document",
  cartRequiresGstin: boolean = true
): Promise<KYCUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("doc_type", docType);
  formData.append("cart_requires_gstin", String(cartRequiresGstin));
  formData.append("consent_granted", "true");

  const res = await fetch(`${API_BASE}/kyc/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error("Document upload and verification failed");
  return await res.json();
}

export async function fetchRescueLeads(): Promise<LeadRescueItem[]> {
  try {
    const res = await fetch(`${API_BASE}/partner/leads?limit=30`);
    if (!res.ok) throw new Error("Failed to fetch leads");
    return await res.json();
  } catch (err) {
    console.error("Failed to load partner rescue leads", err);
    return [];
  }
}

export async function createProvisioningOrder(
  businessName: string,
  bundleName: string,
  monthlyCharge: number,
  slaDays: number = 4,
  partnerId?: string
): Promise<ProvisioningOrder> {
  const res = await fetch(`${API_BASE}/order/create`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      business_name: businessName,
      bundle_name: bundleName,
      monthly_charge_inr: monthlyCharge,
      total_sla_days: slaDays,
      partner_id: partnerId,
    }),
  });
  if (!res.ok) throw new Error("Order creation failed");
  return await res.json();
}

export async function advanceOrderStage(orderId: string): Promise<ProvisioningOrder> {
  const res = await fetch(`${API_BASE}/order/${orderId}/advance`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to advance order");
  return await res.json();
}

export async function fetchJudgeScenario(scenarioId: string): Promise<JudgeScenarioResult> {
  const res = await fetch(`${API_BASE}/demo/judge-scenario/${scenarioId}`);
  if (!res.ok) throw new Error("Scenario not found");
  return await res.json();
}
