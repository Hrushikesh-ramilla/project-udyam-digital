from __future__ import annotations

from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
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

    if req.applicant_preset:
        preset = req.applicant_preset.upper().strip()
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


@app.get("/api/partner/leads", response_model=list[LeadRescueItem])
def get_partner_rescue_leads(limit: int = 30, stage: Optional[str] = None):
    return lead_ml.get_top_rescue_leads(limit=limit, stage_filter=stage)


@app.post("/api/order/create", response_model=ProvisioningOrder)
def create_order(req: CreateOrderRequest):
    return tracker.create_order(
        business_name=req.business_name,
        bundle_name=req.bundle_name,
        monthly_charge_inr=req.monthly_charge_inr,
        total_sla_days=req.total_sla_days,
        partner_id=req.partner_id,
    )


@app.post("/api/order/{order_id}/advance", response_model=ProvisioningOrder)
def advance_order_stage(order_id: str):
    res = tracker.advance_stage(order_id)
    if not res:
        raise HTTPException(status_code=404, detail="Order not found")
    return res


@app.get("/api/order/{order_id}", response_model=ProvisioningOrder)
def get_order_status(order_id: str):
    order = tracker.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.get("/api/demo/judge-scenario/{scenario_id}")
def get_judge_scenario(scenario_id: str):
    """Provides structured data for the Judge Test Bench drawer to demonstrate planted defects live."""
    s_id = scenario_id.upper().strip()

    if s_id == "K01_CANCELLED_GST":
        return {
            "scenario": "Applicant K01: Cancelled GSTIN & Blank Udyam Trap",
            "applicant": "K01",
            "business_name": "Vindhya Tours & Travels",
            "expected_outcome": "REJECTED (Planted Blocker)",
            "key_traps": ["GSTIN 37IHKXV5167L1ZS has status CANCELLED in registry", "Udyam Certificate reg number is blank"],
            "remediation": "1-click switch to GST-exempt Udyam AirFiber bundle or provide active GSTIN",
        }
    elif s_id == "K05_MISSING_UDYAM":
        return {
            "scenario": "Applicant K05: Missing Mandatory Udyam Certificate",
            "applicant": "K05",
            "business_name": "Balaji Realty LLP",
            "expected_outcome": "REJECTED (Missing Document)",
            "key_traps": ["Applicant only uploaded 3 documents; Udyam registration certificate is absent"],
            "remediation": "Upload official Udyam certificate to proceed",
        }
    elif s_id == "K11_STALE_BILL":
        return {
            "scenario": "Applicant K11: Stale Utility Bill (>90 Days Old from 2026-07-15)",
            "applicant": "K11",
            "business_name": "Trinity Bake House Pvt Ltd",
            "expected_outcome": "REJECTED (Stale Address Proof)",
            "key_traps": ["Electricity bill dated 2025-10-31 is 257 days old relative to reference date 2026-07-15"],
            "remediation": "Upload recent utility bill issued within the last 90 days",
        }
    elif s_id == "K07_ENTITY_MISMATCH":
        return {
            "scenario": "Applicant K07: Entity Name Discrepancy",
            "applicant": "K07",
            "business_name": "Neelgiri Physio Clinic",
            "expected_outcome": "REJECTED (Trade Name Conflicting)",
            "key_traps": ["Legal name on certificate declared as '(Prop. Shri Physio Clinic)' while declared trade name is 'Neelgiri Physio Clinic'"],
            "remediation": "Re-upload authentic unedited certificate matching GST registry",
        }
    elif s_id == "NON_GST_KIRANA":
        return {
            "scenario": "Non-GST Kirana Merchant (55% Base Segment)",
            "applicant": "K02",
            "business_name": "Saffron Kirana Store",
            "expected_outcome": "APPROVED via GST-Exempt Udyam Pathway",
            "key_traps": ["No GSTIN: Standard telco CPQ fails; Udyam Digital automatically routes to 5G AirFiber 100 + Failover @ ₹1,398/mo"],
            "remediation": "100% zero-friction digital onboarding",
        }
    else:
        raise HTTPException(status_code=404, detail="Scenario not found")
