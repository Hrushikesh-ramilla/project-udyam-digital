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

export function getOrCreateSessionId(): string {
  if (typeof window === "undefined" || !window.localStorage) {
    return "UDYAM_SESSION_DEFAULT";
  }
  let sessionId = localStorage.getItem("udyam_session_id");
  if (!sessionId) {
    const randomHex = typeof crypto !== "undefined" && crypto.randomUUID
      ? crypto.randomUUID().replace(/-/g, "").toUpperCase()
      : Math.random().toString(36).substring(2).toUpperCase() + Date.now().toString(36).toUpperCase();
    sessionId = `UDYAM_SESSION_${randomHex}`;
    localStorage.setItem("udyam_session_id", sessionId);
  }
  return sessionId;
}

export function resetCustomerSession(): string {
  const randomHex = typeof crypto !== "undefined" && crypto.randomUUID
    ? crypto.randomUUID().replace(/-/g, "").toUpperCase()
    : Math.random().toString(36).substring(2).toUpperCase() + Date.now().toString(36).toUpperCase();
  const newSessionId = `UDYAM_SESSION_${randomHex}`;
  if (typeof window !== "undefined" && window.localStorage) {
    localStorage.clear();
    localStorage.setItem("udyam_session_id", newSessionId);
  }
  return newSessionId;
}

export function getSessionHeaders(customHeaders: Record<string, string> = {}): Record<string, string> {
  return {
    "X-Session-ID": getOrCreateSessionId(),
    ...customHeaders,
  };
}

export async function fetchProducts(): Promise<ProductItem[]> {
  try {
    const res = await fetch(`${API_BASE}/products`, { headers: getSessionHeaders() });
    if (!res.ok) throw new Error("Failed to fetch products");
    return await res.json();
  } catch (err) {
    console.error("API error, using fallback products", err);
    return [];
  }
}

export async function sendChatMessage(
  message: string,
  previousSlots?: MSMEProfileSlots | null,
  languageCode?: string | null,
  scriptMode?: "native" | "latin" | null,
  history?: Array<{ role: string; content: string }> | null
): Promise<AdvisorResponse> {
  const res = await fetch(`${API_BASE}/advisor/chat`, {
    method: "POST",
    headers: getSessionHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({
      user_message: message,
      previous_slots: previousSlots,
      language_code: languageCode,
      script_mode: scriptMode,
      history: history || null,
    }),
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
    headers: getSessionHeaders({ "Content-Type": "application/json" }),
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
    headers: getSessionHeaders({ "Content-Type": "application/json" }),
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
    headers: getSessionHeaders({ "Content-Type": "application/json" }),
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

export async function verifyDigiLocker(params: {
  aadhaarNumber: string;
  otp: string;
  declaredGstin?: string;
  declaredUdyam?: string;
  applicantId?: string;
  cartRequiresGstin?: boolean;
}): Promise<KYCVerificationResult> {
  const res = await fetch(`${API_BASE}/kyc/digilocker`, {
    method: "POST",
    headers: getSessionHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({
      aadhaar_number: params.aadhaarNumber,
      otp: params.otp,
      declared_gstin: params.declaredGstin || null,
      declared_udyam: params.declaredUdyam || null,
      applicant_id: params.applicantId || null,
      cart_requires_gstin: params.cartRequiresGstin ?? false,
      consent: {
        consent_id: `CONSENT_DIGI_${Date.now()}`,
        user_id: "DIGILOCKER_USER",
        purpose: "DigiLocker telecom onboarding, instant registry pull, and DPDP Act 2023 compliance.",
        timestamp: "2026-07-15T10:00:00Z",
        ip_hash: "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae",
        granted: true,
      },
    }),
  });
  if (!res.ok) throw new Error("DigiLocker verification failed");
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
    headers: getSessionHeaders(),
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error("Document upload and verification failed");
  return await res.json();
}

export async function fetchRescueLeads(): Promise<LeadRescueItem[]> {
  try {
    const res = await fetch(`${API_BASE}/partner/leads?limit=30`, { headers: getSessionHeaders() });
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
    headers: getSessionHeaders({ "Content-Type": "application/json" }),
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
    headers: getSessionHeaders(),
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to advance order");
  return await res.json();
}

export async function fetchJudgeScenario(scenarioId: string): Promise<JudgeScenarioResult> {
  const res = await fetch(`${API_BASE}/demo/judge-scenario/${scenarioId}`, { headers: getSessionHeaders() });
  if (!res.ok) throw new Error("Scenario not found");
  return await res.json();
}

export interface PaymentIntent {
  payment_id: string;
  order_id: string;
  amount_inr: number;
  upi_uri: string;
  upi_pa: string;
  upi_pn: string;
  qr_data_url: string;
  razorpay_order_id: string;
  razorpay_key_id: string;
}

export interface PaymentVerificationResult {
  payment_id: string;
  order_id: string;
  status: "SUCCESS" | "FAILED";
  message: string;
  verified_at?: string | null;
}

export interface LogisticsDispatch {
  dispatch_id: string;
  order_id: string;
  awb_number: string;
  carrier_name: string;
  courier_hub: string;
  field_engineer_name: string;
  field_engineer_phone: string;
  dispatch_status: string;
  tracking_url: string;
  whatsapp_dispatch_link: string;
  created_at: string;
}

export async function createPaymentIntent(
  orderId: string,
  amountInr: number,
  paymentMethod: string = "UPI_INTENT"
): Promise<PaymentIntent> {
  const res = await fetch(`${API_BASE}/payments/create-intent`, {
    method: "POST",
    headers: getSessionHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({
      order_id: orderId,
      amount_inr: amountInr,
      payment_method: paymentMethod,
    }),
  });
  if (!res.ok) throw new Error("Payment intent creation failed");
  return await res.json();
}

export async function verifyUPIPayment(
  paymentId: string,
  orderId: string,
  utrReference: string
): Promise<PaymentVerificationResult> {
  const res = await fetch(`${API_BASE}/payments/verify-upi`, {
    method: "POST",
    headers: getSessionHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({
      payment_id: paymentId,
      order_id: orderId,
      utr_reference: utrReference,
    }),
  });
  if (!res.ok) throw new Error("UPI payment verification failed");
  return await res.json();
}

export async function verifyRazorpayPayment(
  paymentId: string,
  orderId: string,
  razorpayOrderId: string,
  razorpayPaymentId: string,
  razorpaySignature: string
): Promise<PaymentVerificationResult> {
  const res = await fetch(`${API_BASE}/payments/verify-razorpay`, {
    method: "POST",
    headers: getSessionHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({
      payment_id: paymentId,
      order_id: orderId,
      razorpay_order_id: razorpayOrderId,
      razorpay_payment_id: razorpayPaymentId,
      razorpay_signature: razorpaySignature,
    }),
  });
  if (!res.ok) throw new Error("Razorpay payment verification failed");
  return await res.json();
}

export async function fetchOrderLogistics(orderId: string): Promise<LogisticsDispatch> {
  const res = await fetch(`${API_BASE}/logistics/${orderId}`, { headers: getSessionHeaders() });
  if (!res.ok) throw new Error("Failed to fetch logistics dispatch");
  return await res.json();
}

export async function triggerHardwareDispatch(orderId: string): Promise<LogisticsDispatch> {
  const res = await fetch(`${API_BASE}/logistics/${orderId}/dispatch`, {
    headers: getSessionHeaders(),
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to trigger hardware dispatch");
  return await res.json();
}


export async function fetchLiveBenchmarks(): Promise<any> {
  const res = await fetch(`${API_BASE}/benchmarks/run`, { headers: getSessionHeaders() });
  if (!res.ok) throw new Error("Failed to run live system benchmarks");
  return await res.json();
}
