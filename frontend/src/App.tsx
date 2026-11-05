import React, { useState } from "react";
import { Navbar } from "./components/Navbar";
import { AdvisorChat } from "./components/AdvisorChat";
import { CPQCart } from "./components/CPQCart";
import { SmartKYC } from "./components/SmartKYC";
import { OrderTracker } from "./components/OrderTracker";
import { PartnerRescueConsole } from "./components/PartnerRescueConsole";
import { JudgeTestBench } from "./components/JudgeTestBench";
import {
  MSMEProfileSlots,
  CommercialBreakdown,
  KYCVerificationResult,
  ProvisioningOrder,
} from "./types";
import { createProvisioningOrder, calculateQuote } from "./api";
import {
  Sparkles,
  ShieldCheck,
  Truck,
  ArrowRight,
  Layers,
  Cpu,
  Activity,
  Zap,
} from "lucide-react";

export const App: React.FC = () => {
  const [currentTab, setTab] = useState<"customer" | "obo" | "partner" | "judge">("customer");
  const [customerStep, setCustomerStep] = useState<"studio" | "kyc" | "tracker">("studio");

  // Global Session State
  const [profileSlots, setProfileSlots] = useState<MSMEProfileSlots | null>(null);
  const [recommendedSkus, setRecommendedSkus] = useState<string[]>([]);
  const [quote, setQuote] = useState<CommercialBreakdown | null>(null);
  const [kycResult, setKycResult] = useState<KYCVerificationResult | null>(null);
  const [order, setOrder] = useState<ProvisioningOrder | null>(null);

  const handleProfileUpdated = (slots: MSMEProfileSlots, skus?: string[]) => {
    setProfileSlots(slots);
    if (skus && skus.length > 0) setRecommendedSkus(skus);
  };

  const handleProceedToKYC = (calculatedQuote: CommercialBreakdown) => {
    setQuote(calculatedQuote);
    setCustomerStep("kyc");
  };

  const APPLICANT_NAMES: Record<string, string> = {
    K01: "Vindhya Tours & Travels",
    K02: "Royal Mart Supermarket",
    K03: "Balaji Timber Traders",
    K04: "Saffron Dental Care LLP",
    K05: "Balaji Realty LLP",
    K06: "Meenakshi Cotton Traders",
    K07: "Neelgiri Physio",
    K08: "Green Leaf Legal Associates",
    K09: "Kaveri Insurance Advisors",
    K10: "Kaveri Stays LLP",
    K11: "Trinity Bake House Pvt Ltd",
    K12: "Star Electronics",
    KIRANA_NON_GST: "Ganesh Kirana & General Store",
  };

  const handleKYCApproved = async (kycRes: KYCVerificationResult) => {
    setKycResult(kycRes);
    try {
      const bName =
        (kycRes.applicant_id && APPLICANT_NAMES[kycRes.applicant_id]) ||
        (profileSlots?.segment ? `${profileSlots.segment} Enterprise` : "Apex Diagnostics Center");
      const bundleName = quote?.items.map((i) => i.product_name).join(" + ") || "Smart Office High-Speed Fiber";
      const monthlyPrice = quote?.net_mrc_inr || 2499;
      const slaDays = quote?.guaranteed_sla_days || 4;

      const newOrder = await createProvisioningOrder(
        bName,
        bundleName,
        monthlyPrice,
        slaDays,
        "PARTNER_DIRECT"
      );
      setOrder(newOrder);
      setCustomerStep("tracker");
    } catch (err: unknown) {
      console.error("Order creation failed", err);
      // Fallback local order structure
      setOrder({
        order_id: `ORD_${Date.now()}`,
        business_name: "Apex Diagnostics Center",
        partner_id: "PARTNER_DIRECT",
        partner_commission_inr: Math.round((quote?.net_mrc_inr || 2499) * 12 * 0.15),
        bundle_name: "Smart Office High-Speed Fiber",
        monthly_charge_inr: quote?.net_mrc_inr || 2499,
        total_sla_days: quote?.guaranteed_sla_days || 4,
        current_stage_idx: 1,
        milestones: [
          {
            stage_id: "ORDER_PLACED",
            stage_name: "Order Placed & Quote Accepted",
            status: "COMPLETED",
            timestamp: "2026-07-15T10:15:00Z",
            eta_days: 0,
            description: "Digital quote locked and commercial contract approved.",
            whatsapp_preview: "Order confirmed! SLA: 4 days.",
          },
          {
            stage_id: "KYC_VERIFIED",
            stage_name: "Smart KYC Verified",
            status: "COMPLETED",
            timestamp: "2026-07-15T10:16:00Z",
            eta_days: 0,
            description: "DPDP-compliant verification passed in 184ms.",
            whatsapp_preview: "KYC Approved instantly.",
          },
          {
            stage_id: "FEASIBILITY",
            stage_name: "Fiber Loop Feasibility",
            status: "IN_PROGRESS",
            timestamp: null,
            eta_days: 1,
            description: "Checking local splitter port and OLT port capacity.",
            whatsapp_preview: "Fiber feasibility check in progress.",
          },
        ],
        is_activated: false,
      });
      setCustomerStep("tracker");
    }
  };

  const handleSwitchToUdyamExempt = async () => {
    try {
      const newQuote = await calculateQuote(
        [
          { product_id: "P04", quantity: 1 },
          { product_id: "P19", quantity: 1 },
        ],
        12
      );
      setQuote(newQuote);
    } catch (err) {
      console.error("Failed to switch to Udyam exempt quote", err);
    }
  };

  const handleLoadDemoOrder = () => {
    setOrder({
      order_id: "ORD_DEMO_2026_8832",
      business_name: "Apex Diagnostics Center",
      partner_id: "PARTNER_BLR_9812",
      partner_commission_inr: 4498,
      bundle_name: "Smart Office Fiber 200M (P01 + P11 + P16 + P22)",
      monthly_charge_inr: 2499,
      total_sla_days: 4,
      current_stage_idx: 1,
      milestones: [
        {
          stage_id: "ORDER_PLACED",
          stage_name: "Order Placed & Quote Accepted",
          status: "COMPLETED",
          timestamp: "2026-07-15T10:15:00Z",
          eta_days: 0,
          description: "Digital quote locked and commercial contract approved.",
          whatsapp_preview: "Order #ORD_DEMO_2026_8832 confirmed! Guaranteed 4-day SLA initialized.",
        },
        {
          stage_id: "KYC_VERIFIED",
          stage_name: "Smart KYC Verified",
          status: "COMPLETED",
          timestamp: "2026-07-15T10:16:00Z",
          eta_days: 0,
          description: "DPDP-compliant verification passed in 184ms with 100% RapidFuzz score.",
          whatsapp_preview: "KYC Approved instantly. National ID masked to XXXX-XXXX-1234.",
        },
        {
          stage_id: "FEASIBILITY",
          stage_name: "Fiber Loop Feasibility",
          status: "IN_PROGRESS",
          timestamp: null,
          eta_days: 1,
          description: "Checking local splitter port and OLT port capacity.",
          whatsapp_preview: "Fiber feasibility check in progress. Splitter port reserved at local node.",
        },
        {
          stage_id: "CPE_DISPATCH",
          stage_name: "CPE Equipment Dispatch",
          status: "PENDING",
          timestamp: null,
          eta_days: 1,
          description: "Dual-band Wi-Fi 6 Optical Network Terminal assigned and barcoded.",
          whatsapp_preview: "Your Wi-Fi 6 CPE router has been dispatched from the regional warehouse.",
        },
        {
          stage_id: "FIELD_INSTALL",
          stage_name: "Field Installation & Splicing",
          status: "PENDING",
          timestamp: null,
          eta_days: 1,
          description: "Field technician scheduled for optical line splicing and signal testing.",
          whatsapp_preview: "Technician Ramesh Kumar assigned! Installation OTP: 4892.",
        },
        {
          stage_id: "ACTIVATED",
          stage_name: "Service Activated & Live",
          status: "PENDING",
          timestamp: null,
          eta_days: 1,
          description: "Radius authentication live. Static IP bound to customer gateway.",
          whatsapp_preview: "🎉 Your Airtel Business connection is LIVE! Speed test: 204 Mbps.",
        },
      ],
      is_activated: false,
    });
  };

  return (
    <div className="min-h-screen bg-[#050505] text-[#f2efea] flex flex-col font-sans selection:bg-[#e40000]/30 selection:text-white relative">
      <Navbar currentTab={currentTab} setTab={setTab} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* TAB 1: CUSTOMER ONBOARDING STUDIO */}
        {currentTab === "customer" && (
          <div className="space-y-6">
            {/* Architectural Breadcrumb Stepper */}
            <div className="glass-card rounded-2xl p-2 sm:p-2.5 flex items-center justify-between overflow-x-auto no-scrollbar shadow-2xl border border-white/[0.08]">
              <div className="flex items-center space-x-2 sm:space-x-3 shrink-0">
                <button
                  onClick={() => setCustomerStep("studio")}
                  className={`flex items-center space-x-2 px-3 sm:px-4 py-1.5 rounded-full text-xs sm:text-sm font-medium transition-all shrink-0 cursor-pointer ${
                    customerStep === "studio"
                      ? "bg-[#e40000] text-white shadow-[0_0_16px_rgba(228,0,0,0.4)]"
                      : "text-white/60 hover:text-white hover:bg-white/[0.04]"
                  }`}
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>1. Architecture Studio &amp; CPQ</span>
                </button>

                <div className="w-4 h-[1px] bg-white/20 hidden sm:block" />

                <button
                  onClick={() => setCustomerStep("kyc")}
                  className={`flex items-center space-x-2 px-3 sm:px-4 py-1.5 rounded-full text-xs sm:text-sm font-medium transition-all shrink-0 cursor-pointer ${
                    customerStep === "kyc"
                      ? "bg-[#e40000] text-white shadow-[0_0_16px_rgba(228,0,0,0.4)]"
                      : "text-white/60 hover:text-white hover:bg-white/[0.04]"
                  }`}
                >
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>2. Smart KYC &amp; DPDP Gate</span>
                </button>

                <div className="w-4 h-[1px] bg-white/20 hidden sm:block" />

                <button
                  onClick={() => setCustomerStep("tracker")}
                  className={`flex items-center space-x-2 px-3 sm:px-4 py-1.5 rounded-full text-xs sm:text-sm font-medium transition-all shrink-0 cursor-pointer ${
                    customerStep === "tracker"
                      ? "bg-[#e40000] text-white shadow-[0_0_16px_rgba(228,0,0,0.4)]"
                      : "text-white/60 hover:text-white hover:bg-white/[0.04]"
                  }`}
                >
                  <Truck className="w-3.5 h-3.5" />
                  <span>3. SLA Fulfillment Pipeline</span>
                </button>
              </div>

              <div className="hidden lg:flex items-center space-x-2 text-[11px] font-mono text-white/50 bg-[#121210] px-3.5 py-1 rounded-full border border-white/[0.07] shrink-0">
                <span className="live-pulse-dot" />
                <span>Zero-Drop Quoting &amp; 4-Day SLA Active</span>
              </div>
            </div>

            {/* Step 1: UNIFIED STUDIO (Copilot + Live Real-Time CPQ Solution) */}
            {customerStep === "studio" && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
                  {/* Left Column: Multilingual AI Copilot */}
                  <div className="lg:col-span-6">
                    <AdvisorChat
                      onProfileUpdated={handleProfileUpdated}
                      onProceedToCPQ={() => setCustomerStep("kyc")}
                    />
                  </div>

                  {/* Right Column: Live Dynamic CPQ Solution & Budget Optimizer */}
                  <div className="lg:col-span-6">
                    <CPQCart
                      profileSlots={profileSlots}
                      recommendedSkus={recommendedSkus}
                      onProceedToKYC={handleProceedToKYC}
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Step 2: SMART KYC */}
            {customerStep === "kyc" && (
              <SmartKYC
                quote={quote}
                onKYCApproved={handleKYCApproved}
                onSwitchToUdyamExempt={handleSwitchToUdyamExempt}
              />
            )}

            {/* Step 3: FULFILLMENT TRACKER */}
            {customerStep === "tracker" && (
              order ? (
                <OrderTracker order={order} onOrderUpdated={(up) => setOrder(up)} />
              ) : (
                <div className="glass-card rounded-2xl p-12 text-center space-y-4 border border-white/[0.08]">
                  <ShieldCheck className="w-12 h-12 text-white/40 mx-auto" />
                  <h3 className="font-serif text-xl font-medium text-white">No Active Order In-Flight</h3>
                  <p className="text-xs text-white/50 max-w-md mx-auto leading-relaxed">
                    Complete the Smart KYC verification step or select a pre-staged customer scenario to initialize fulfillment telemetry.
                  </p>
                  <div className="flex items-center justify-center space-x-3 pt-3">
                    <button
                      onClick={() => setCustomerStep("kyc")}
                      className="bg-[#e40000] hover:bg-[#b30000] text-white text-xs font-medium py-2.5 px-5 rounded-xl shadow-[0_0_16px_rgba(228,0,0,0.4)] transition-all cursor-pointer"
                    >
                      Run Smart KYC Gate
                    </button>
                    <button
                      onClick={handleLoadDemoOrder}
                      className="bg-white/[0.05] hover:bg-white/[0.1] text-white/80 border border-white/[0.08] text-xs font-medium py-2.5 px-5 rounded-xl transition-all cursor-pointer"
                    >
                      Load Verified Specimen Order
                    </button>
                  </div>
                </div>
              )
            )}
          </div>
        )}

        {/* TAB 2: PARTNER ML RESCUE CONSOLE */}
        {currentTab === "partner" && <PartnerRescueConsole />}

        {/* TAB 3: JUDGE TEST BENCH */}
        {currentTab === "judge" && <JudgeTestBench />}
      </main>

      {/* Footer - Architectural Telemetry Bar */}
      <footer className="border-t border-white/[0.07] bg-[#070707]/90 backdrop-blur-xl py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-white/50">
          <div className="flex items-center space-x-2 font-mono text-[11px]">
            <span className="font-semibold text-white">Bharti Airtel Enterprise</span>
            <span>·</span>
            <span>Project Udyam Digital</span>
            <span>·</span>
            <span className="text-[#d9ad63]">SYNC 2026 Track A</span>
          </div>
          <div className="flex items-center space-x-4 font-mono text-[10px] text-white/40 uppercase tracking-wider">
            <span className="hover:text-emerald-400 transition-colors">FastAPI + 3,534 GSTINs</span>
            <span>·</span>
            <span className="hover:text-amber-400 transition-colors">LightGBM SHAP 5K Leads</span>
            <span>·</span>
            <span className="hover:text-[#e40000] transition-colors">DPDP 2023 Compliant</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
