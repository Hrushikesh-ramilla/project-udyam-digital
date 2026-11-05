from __future__ import annotations

from pathlib import Path
from typing import Optional
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.app.db.registry import get_registry
from backend.app.models.schemas import (
    AdvisorResponse,
    CalculateQuoteRequest,
    ChatRequest,
    CommercialBreakdown,
    CreateOrderRequest,
    DPDPConsentPayload,
    KYCVerificationResult,
    KYCVerifyAPIRequest,
    LeadRescueItem,
    OptimizeBudgetRequest,
    ProductItem,
    ProvisioningOrder,
    ReverseBudgetResult,
)
from backend.app.services.advisor_agent import AdvisorAgent
from backend.app.services.cpq_engine import CPQEngine
from backend.app.services.kyc_engine import KYCEngine
from backend.app.services.lead_rescue_ml import LeadRescueMLEngine
from backend.app.services.provisioning_tracker import get_provisioning_tracker

app = FastAPI(
    title="Project Udyam Digital - Accel Business API",
    version="1.0.0",
    description="Deterministic CPQ DAG, DPDP Smart KYC, and LightGBM Lead Rescue API for MSME Onboarding.",
)

# CORS configuration for seamless PWA integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy singletons
db = get_registry()
cpq = CPQEngine(db)
advisor = AdvisorAgent(db)
kyc = KYCEngine(db)
lead_ml = LeadRescueMLEngine(db)
tracker = get_provisioning_tracker()


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "service": "Project Udyam Digital",
        "catalogue_count": db.product_count,
        "gstin_registry_count": db.gstin_count,
        "udyam_registry_count": db.udyam_count,
        "leads_telemetry_count": db.lead_count,
    }


@app.get("/api/products", response_model=list[ProductItem])
def get_products():
    return db.get_all_products()


@app.post("/api/advisor/chat", response_model=AdvisorResponse)
def advisor_chat(req: ChatRequest):
    return advisor.process_turn(req.user_message, req.previous_slots)


@app.post("/api/cpq/calculate", response_model=CommercialBreakdown)
def calculate_quote(req: CalculateQuoteRequest):
    try:
        return cpq.calculate_commercials(req.cart, contract_months=req.contract_months, strict_dag=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/cpq/optimize-budget", response_model=ReverseBudgetResult)
def optimize_budget(req: OptimizeBudgetRequest):
    return cpq.optimize_budget(req.profile, max_monthly_budget=req.max_monthly_budget)


@app.post("/api/kyc/verify", response_model=KYCVerificationResult)
def verify_kyc(req: KYCVerifyAPIRequest):
    data_dir = Path("data/kyc_documents")
    docs: dict[str, bytes] = {}

    if req.applicant_preset or req.applicant_id:
        preset = (req.applicant_preset or req.applicant_id or "").upper().strip()
        # Find files matching preset
        doc_types = ["gst_certificate", "udyam_certificate", "signatory_id", "address_proof"]
        for dt in doc_types:
            path = data_dir / f"{preset}_{dt}.png"
            if path.exists():
                docs[dt] = path.read_bytes()

    # Default consent if not explicitly provided
    consent = req.consent or DPDPConsentPayload(
        consent_id="CONSENT_AUTO_SESSION",
        user_id="USER_SESSION",
        purpose="Airtel Business telecom provisioning, regulatory identity check, and DPDP Act 2023 compliance.",
        timestamp="2026-07-15T10:00:00Z",
        ip_hash="d59b20e0e0149023ab9450c2656e1cb1ef92ca157bb6be29e843b0281b67104b",
        granted=True,
    )

    return kyc.verify_application(docs, cart_requires_gstin=req.cart_requires_gstin, consent=consent)


@app.post("/api/kyc/upload")
async def upload_and_verify_document(
    file: UploadFile = File(...),
    doc_type: str = Form("document"),
    cart_requires_gstin: bool = Form(True),
    consent_granted: bool = Form(True),
):
    """Uploads any arbitrary PDF, PNG, JPG document from judge's laptop, parses it
    live via PyMuPDF/Gemini Vision/Regex, and verifies it against registries."""
    file_bytes = await file.read()
    parsed_doc = kyc.parse_document_bytes(file_bytes, fallback_type=doc_type)

    consent = DPDPConsentPayload(
        consent_id="CONSENT_UPLOAD_SESSION",
        user_id="UPLOAD_USER",
        purpose="Airtel Business telecom KYC verification, live document extraction, and DPDP Act 2023 compliance.",
        timestamp="2026-07-15T10:00:00Z",
        ip_hash="d59b20e0e0149023ab9450c2656e1cb1ef92ca157bb6be29e843b0281b67104b",
        granted=consent_granted,
    )

    docs = {parsed_doc.doc_type: parsed_doc}
    single_res = kyc.verify_application(docs, cart_requires_gstin=cart_requires_gstin, consent=consent, single_doc_mode=True)
    package_res = kyc.verify_application(docs, cart_requires_gstin=cart_requires_gstin, consent=consent, single_doc_mode=False)

    return {
        "filename": file.filename,
        "size_bytes": len(file_bytes),
        "file_sha256": parsed_doc.file_sha256,
        "doc_type": parsed_doc.doc_type,
        "extracted_fields": parsed_doc.extracted_fields,
        "single_doc_result": single_res.model_dump(),
        "verification_result": package_res.model_dump(),
    }


@app.get("/api/partner/leads", response_model=list[LeadRescueItem])
def get_partner_rescue_leads(limit: int = 30, stage: Optional[str] = None):
    return lead_ml.get_top_rescue_leads(limit=limit, stage_filter=stage)


@app.post("/api/orders", response_model=ProvisioningOrder)
@app.post("/api/order/create", response_model=ProvisioningOrder)
def create_order(req: CreateOrderRequest):
    return tracker.create_order(
        business_name=req.business_name,
        bundle_name=req.bundle_name,
        monthly_charge_inr=req.monthly_charge_inr,
        total_sla_days=req.total_sla_days,
        partner_id=req.partner_id,
    )


@app.post("/api/orders/{order_id}/advance", response_model=ProvisioningOrder)
@app.post("/api/order/{order_id}/advance", response_model=ProvisioningOrder)
def advance_order_stage(order_id: str):
    res = tracker.advance_stage(order_id)
    if not res:
        raise HTTPException(status_code=404, detail="Order not found")
    return res


@app.get("/api/orders/{order_id}", response_model=ProvisioningOrder)
@app.get("/api/order/{order_id}", response_model=ProvisioningOrder)
def get_order_status(order_id: str):
    order = tracker.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.get("/api/demo/judge-scenario/{scenario_id}")
def get_judge_scenario(scenario_id: str):
    """Provides structured data for the Judge Test Bench drawer to demonstrate regulatory edge cases live."""
    s_id = scenario_id.upper().strip()

    # Determine preset and parameters
    preset = "K03"
    cart_requires_gstin = True
    title = ""
    expected_outcome = ""
    expected_behavior = ""
    notes = ""
    remediation = ""

    if "K01" in s_id:
        preset = "K01"
        title = "Applicant K01: Cancelled GSTIN & Incomplete Udyam"
        expected_outcome = "REJECTED (Regulatory Inactive GSTIN)"
        expected_behavior = "Engine queries mock_gstin_registry.csv (3,534 rows) and identifies 'Cancelled' status on 2026-06-01. Evaluates Udyam regex rejecting blank registration number."
        notes = "Regulatory blocker identified: GSTIN status CANCELLED and Udyam regex failure. Actionable remediation provided to switch to non-GST bundle."
        remediation = "1-click switch to GST-exempt Udyam AirFiber bundle or provide active GSTIN"
    elif "K05" in s_id:
        preset = "K05"
        title = "Applicant K05: Missing Mandatory Udyam Certificate"
        expected_outcome = "REJECTED (Missing Document)"
        expected_behavior = "Payload validation intercepts missing Udyam certificate without crashing. Enforces mandatory KYC document checklist."
        notes = "Mandatory document check: Missing Udyam document. Flags UDYAM_DOC_MISSING."
        remediation = "Upload official Udyam certificate to proceed"
    elif "K11" in s_id:
        preset = "K11"
        title = "Applicant K11: Stale Utility Bill (>90 Days Old from 2026-07-15)"
        expected_outcome = "REJECTED (Stale Address Proof)"
        expected_behavior = "Enforces Hackathon Anchor Date 2026-07-15. Calculates bill date (2025-10-31) = 257 days old > 90-day validity window."
        notes = "Statutory document freshness check: Utility bill age 257 days exceeds statutory 90-day threshold."
        remediation = "Upload recent utility bill issued within the last 90 days"
    elif "K07" in s_id:
        preset = "K07"
        title = "Applicant K07: Entity Name Discrepancy"
        expected_outcome = "REJECTED (Trade Name Conflicting)"
        expected_behavior = "RapidFuzz token sorting compares legal proprietor trade name against declared invoice trade name (<70% similarity threshold)."
        notes = "Entity identity reconciliation: Legal name says '(Prop. Shri Physio Clinic)' vs declared 'Neelgiri Physio Clinic'."
        remediation = "Re-upload authentic unedited certificate matching GST registry"
    elif "K03" in s_id:
        preset = "K03"
        title = "Applicant K03: Clean 100% Instant Approval"
        expected_outcome = "APPROVED (Golden Path)"
        expected_behavior = "Valid GSTIN + valid Udyam + fresh bill. Proprietor title extraction ('Joseph Singh (Prop. Ganesh Woodcraft)') scores 100% RapidFuzz match."
        notes = "Clean golden path passed: In-memory national ID masked to XXXX-XXXX-1234, registry active, zero anomalies."
        remediation = "None required. Order immediately ready for provisioning."
    elif "NON_GST" in s_id or "KIRANA" in s_id:
        preset = "K03"
        cart_requires_gstin = False
        title = "Non-GST Kirana Merchant (Micro-Bundle Pathway)"
        expected_outcome = "APPROVED via GST-Exempt Udyam Pathway"
        expected_behavior = "GSTIN Firewall bypass for micro-bundles: Kirana applicant onboarded using Udyam and Electricity Bill without demanding GSTIN."
        notes = "Attacks the 2.0% non-GST conversion gap: Micro-bundle passes Smart KYC with zero GSTIN blockers."
        remediation = "100% zero-friction digital onboarding"
    else:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Execute live KYC verification
    data_dir = Path("data/kyc_documents")
    docs: dict[str, bytes] = {}
    doc_types = ["gst_certificate", "udyam_certificate", "signatory_id", "address_proof"]
    for dt in doc_types:
        path = data_dir / f"{preset}_{dt}.png"
        if path.exists():
            docs[dt] = path.read_bytes()

    consent = DPDPConsentPayload(
        consent_id=f"CONSENT_BENCH_{preset}",
        user_id="JUDGE_BENCH_SESSION",
        purpose="Hackathon jury evaluation, DPDP Act 2023 compliance, and deterministic verification.",
        timestamp="2026-07-15T10:00:00Z",
        ip_hash="2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae",
        granted=True,
    )

    kyc_res = kyc.verify_application(docs, cart_requires_gstin=cart_requires_gstin, consent=consent)

    return {
        "scenario_id": s_id,
        "title": title,
        "applicant": preset,
        "expected_outcome": expected_outcome,
        "expected_behavior": expected_behavior,
        "notes": notes,
        "remediation": remediation,
        "verification_result": kyc_res.model_dump(),
    }
