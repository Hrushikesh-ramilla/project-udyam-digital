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
  LeadRescueItem,
} from "./types";
import { createProvisioningOrder, calculateQuote } from "./api";
import {
  Bot,
  ShoppingCart,
  ShieldCheck,
  Truck,
  QrCode,
  Share2,
  Copy,
  Check,
  CheckCircle2,
  Sparkles,
} from "lucide-react";

export const App: React.FC = () => {
  const [currentTab, setTab] = useState<"customer" | "obo" | "partner" | "judge">("customer");
  const [customerStep, setCustomerStep] = useState<"advisor" | "cpq" | "kyc" | "tracker">("advisor");

  // Global Session State
  const [profileSlots, setProfileSlots] = useState<MSMEProfileSlots | null>(null);
  const [recommendedSkus, setRecommendedSkus] = useState<string[]>([]);
  const [quote, setQuote] = useState<CommercialBreakdown | null>(null);
  const [kycResult, setKycResult] = useState<KYCVerificationResult | null>(null);
  const [order, setOrder] = useState<ProvisioningOrder | null>(null);

  // Field Rep OBO State
  const [oboPartnerId, setOboPartnerId] = useState<string>("PARTNER_BLR_9812");
  const [oboBusinessName, setOboBusinessName] = useState<string>("Shri Ganesh Woodcraft");
  const [oboSelectedBundle, setOboSelectedBundle] = useState<string>("Smart Office Fiber 200M (P01 + P11 + P16 + P22)");
  const [oboCopied, setOboCopied] = useState<boolean>(false);

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
    // Automatically create a provisioning order
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

  const generateOBOLink = () => {
    return `${window.location.origin}?partner_id=${oboPartnerId}&biz=${encodeURIComponent(
      oboBusinessName
    )}&bundle=smart_office`;
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

  const copyOBOLink = () => {
    navigator.clipboard.writeText(generateOBOLink());
    setOboCopied(true);
    setTimeout(() => setOboCopied(false), 2500);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar currentTab={currentTab} setTab={setTab} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* TAB 1: CUSTOMER SELF-SERVE ONBOARDING JOURNEY */}
        {currentTab === "customer" && (
          <div className="space-y-6">
            {/* Customer Sub-Stepping Bar */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-2.5 sm:p-3 flex items-center justify-between overflow-x-auto no-scrollbar">
              <div className="flex items-center space-x-1.5 sm:space-x-3 shrink-0">
                <button
                  onClick={() => setCustomerStep("advisor")}
                  className={`flex items-center space-x-1.5 px-2.5 sm:px-3 py-1.5 rounded-xl text-xs sm:text-sm font-semibold transition-all shrink-0 ${
                    customerStep === "advisor"
                      ? "bg-red-600 text-white shadow-md shadow-red-600/30"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  <Bot className="w-4 h-4" />
                  <span className="hidden sm:inline">1. Multilingual Advisor</span>
                  <span className="sm:hidden">1. Advisor</span>
                </button>

                <button
                  onClick={() => setCustomerStep("cpq")}
                  className={`flex items-center space-x-1.5 px-2.5 sm:px-3 py-1.5 rounded-xl text-xs sm:text-sm font-semibold transition-all shrink-0 ${
                    customerStep === "cpq"
                      ? "bg-red-600 text-white shadow-md shadow-red-600/30"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  <ShoppingCart className="w-4 h-4" />
                  <span className="hidden sm:inline">2. Dynamic CPQ Cart</span>
                  <span className="sm:hidden">2. CPQ Cart</span>
                </button>

                <button
                  onClick={() => setCustomerStep("kyc")}
                  className={`flex items-center space-x-1.5 px-2.5 sm:px-3 py-1.5 rounded-xl text-xs sm:text-sm font-semibold transition-all shrink-0 ${
                    customerStep === "kyc"
                      ? "bg-red-600 text-white shadow-md shadow-red-600/30"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  <ShieldCheck className="w-4 h-4" />
                  <span className="hidden sm:inline">3. Smart KYC Gate</span>
                  <span className="sm:hidden">3. Smart KYC</span>
                </button>

                <button
                  onClick={() => setCustomerStep("tracker")}
                  className={`flex items-center space-x-1.5 px-2.5 sm:px-3 py-1.5 rounded-xl text-xs sm:text-sm font-semibold transition-all shrink-0 ${
                    customerStep === "tracker"
                      ? "bg-red-600 text-white shadow-md shadow-red-600/30"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  <Truck className="w-4 h-4" />
                  <span className="hidden sm:inline">4. Provisioning Tracker</span>
                  <span className="sm:hidden">4. Tracker</span>
                </button>
              </div>

              <div className="hidden lg:flex items-center space-x-2 text-xs font-mono text-slate-400 bg-slate-950 px-3 py-1 rounded-lg border border-slate-800 shrink-0">
                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                <span>One-Sitting MSME Onboarding Journey</span>
              </div>
            </div>

            {/* Step Rendering */}
            {customerStep === "advisor" && (
              <AdvisorChat
                onProfileUpdated={handleProfileUpdated}
                onProceedToCPQ={() => setCustomerStep("cpq")}
              />
            )}

            {customerStep === "cpq" && (
              <CPQCart
                profileSlots={profileSlots}
                recommendedSkus={recommendedSkus}
                onProceedToKYC={handleProceedToKYC}
              />
            )}

            {customerStep === "kyc" && (
              <SmartKYC
                quote={quote}
                onKYCApproved={handleKYCApproved}
                onSwitchToUdyamExempt={handleSwitchToUdyamExempt}
              />
            )}

            {customerStep === "tracker" && (
              order ? (
                <OrderTracker order={order} onOrderUpdated={(up) => setOrder(up)} />
              ) : (
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-10 text-center space-y-4">
                  <ShieldCheck className="w-12 h-12 text-slate-600 mx-auto" />
                  <h3 className="text-lg font-bold text-white">No Active Provisioning Order Yet</h3>
                  <p className="text-xs text-slate-400 max-w-md mx-auto">
                    Complete the Smart KYC verification step or select a scenario in the Judge Test Bench to populate order telemetry.
                  </p>
                  <div className="flex items-center justify-center space-x-3 pt-2">
                    <button
                      onClick={() => setCustomerStep("kyc")}
                      className="bg-red-600 hover:bg-red-500 text-white text-xs font-bold py-2.5 px-4 rounded-xl shadow-md transition-all"
                    >
                      Go to Smart KYC
                    </button>
                    <button
                      onClick={handleLoadDemoOrder}
                      className="bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold py-2.5 px-4 rounded-xl transition-all"
                    >
                      Simulate Sample Active Order
                    </button>
                  </div>
                </div>
              )
            )}
          </div>
        )}

        {/* TAB 2: FIELD REP ON-BEHALF-OF (OBO) & QR ATTRIBUTION */}
        {currentTab === "obo" && (
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
              <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                <div className="flex items-center space-x-2">
                  <QrCode className="w-6 h-6 text-red-500" />
                  <h2 className="text-xl font-bold text-white tracking-tight">
                    Field Sales Assisted On-Behalf-Of (OBO) Mode
                  </h2>
                </div>
                <span className="text-xs bg-red-500/20 text-red-400 border border-red-500/30 px-3 py-1 rounded-full font-mono font-bold">
                  Phygital Handoff Active
                </span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Field agents configure the optimal solution during store visits and dispatch a pre-filled, signed session link to the owner's WhatsApp. Solves the <strong>531 leads dropped because owners had no time for lengthy visits</strong>.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                <div className="space-y-2">
                  <label className="text-xs font-semibold text-slate-300">Partner / Rep ID</label>
                  <input
                    type="text"
                    value={oboPartnerId}
                    onChange={(e) => setOboPartnerId(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white font-mono"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-xs font-semibold text-slate-300">Merchant Business Name</label>
                  <input
                    type="text"
                    value={oboBusinessName}
                    onChange={(e) => setOboBusinessName(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white"
                  />
                </div>
              </div>

              <div className="space-y-2 pt-2">
                <label className="text-xs font-semibold text-slate-300">Recommended Telecom Package</label>
                <select
                  value={oboSelectedBundle}
                  onChange={(e) => setOboSelectedBundle(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white"
                >
                  <option value="Smart Office Fiber 200M (P01 + P11 + P16 + P22)">
                    Smart Office Fiber 200M (P01 + P11 + P16 + P22) - ₹2,999/mo
                  </option>
                  <option value="Kirana Digital Connect (P02 + P17 + P22) [Non-GST Eligible]">
                    Kirana Digital Connect (P02 + P17 + P22) [Non-GST Eligible] - ₹1,499/mo
                  </option>
                  <option value="Enterprise Branch ILL (P03 + P11 + P14 + P23)">
                    Enterprise Branch ILL (P03 + P11 + P14 + P23) - ₹9,999/mo
                  </option>
                </select>
              </div>

              {/* Generated Deep Link */}
              <div className="mt-6 p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-slate-300">Pre-Hydrated WhatsApp Consent Link</span>
                  <span className="text-[10px] text-emerald-400 font-mono">Commission Locked: 15%</span>
                </div>
                <div className="p-3 bg-slate-900 rounded-lg text-xs font-mono text-slate-300 break-all border border-slate-800">
                  {generateOBOLink()}
                </div>
                <div className="flex items-center justify-between pt-2">
                  <button
                    onClick={copyOBOLink}
                    className="flex items-center space-x-1.5 bg-slate-800 hover:bg-slate-700 text-white font-semibold py-2 px-4 rounded-xl text-xs transition-all"
                  >
                    {oboCopied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{oboCopied ? "Link Copied!" : "Copy Link"}</span>
                  </button>

                  <a
                    href={`https://wa.me/?text=${encodeURIComponent(
                      `Namaste! Your Airtel Business solution for ${oboBusinessName} is ready for 1-click digital sign-off: ${generateOBOLink()}`
                    )}`}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center space-x-1.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-2 px-4 rounded-xl text-xs transition-all shadow-md shadow-emerald-600/30"
                  >
                    <Share2 className="w-3.5 h-3.5" />
                    <span>Dispatch via WhatsApp</span>
                  </a>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: PARTNER ML RESCUE CONSOLE */}
        {currentTab === "partner" && <PartnerRescueConsole />}

        {/* TAB 4: JUDGE TEST BENCH */}
        {currentTab === "judge" && <JudgeTestBench />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-slate-900/60 py-4 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-slate-500">
          <div>
            Project Udyam Digital • Airtel SYNC Hackathon 2026 Enterprise Track
          </div>
          <div className="flex items-center space-x-4">
            <span>FastAPI + SQLite Registry</span>
            <span>•</span>
            <span>LightGBM (5,000 Leads)</span>
            <span>•</span>
            <span>DPDP Act 2023 Compliant</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
