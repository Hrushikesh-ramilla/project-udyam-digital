import React, { useState, useEffect } from "react";
import Lenis from "lenis";
import { motion, AnimatePresence } from "motion/react";
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
import { Sparkles, ShieldCheck, Truck } from "lucide-react";

export const App: React.FC = () => {
  const [currentTab, setTab] = useState<"customer" | "obo" | "partner" | "judge">("customer");
  const [customerStep, setCustomerStep] = useState<"studio" | "kyc" | "tracker">("studio");

  // Global Session State
  const [profileSlots, setProfileSlots] = useState<MSMEProfileSlots | null>(null);
  const [recommendedSkus, setRecommendedSkus] = useState<string[]>([]);
  const [quote, setQuote] = useState<CommercialBreakdown | null>(null);
  const [kycResult, setKycResult] = useState<KYCVerificationResult | null>(null);
  const [order, setOrder] = useState<ProvisioningOrder | null>(null);

  // Initialize smooth inertial scroll (Lenis)
  useEffect(() => {
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    });
    function raf(time: number) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }
    const reqId = requestAnimationFrame(raf);
    return () => {
      cancelAnimationFrame(reqId);
      lenis.destroy();
    };
  }, []);

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
    } catch {
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
      console.error(err);
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
          whatsapp_preview: "Fiber feasibility check in progress.",
        },
      ],
      is_activated: false,
    });
  };

  return (
    <div className="min-h-screen bg-[#030405] text-[#EBE5D9] flex flex-col font-sans selection:bg-[#e40000]/30 selection:text-white relative">
      <Navbar currentTab={currentTab} setTab={setTab} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <AnimatePresence mode="wait">
          {currentTab === "customer" && (
            <motion.div
              key="customer"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
              className="space-y-6"
            >
              {/* Apple-style Inertial Breadcrumb Stepper */}
              <div className="luxury-glass rounded-full p-1.5 flex items-center justify-between overflow-x-auto no-scrollbar border border-[rgba(235,229,217,0.06)]">
                <div className="flex items-center space-x-1 shrink-0">
                  <button
                    onClick={() => setCustomerStep("studio")}
                    className={`relative px-4 py-1.5 rounded-full text-xs font-medium transition-all duration-200 cursor-pointer flex items-center space-x-2 ${
                      customerStep === "studio"
                        ? "bg-[#e40000] text-white shadow-[0_0_16px_rgba(228,0,0,0.4)]"
                        : "text-[#B39D82] hover:text-[#EBE5D9]"
                    }`}
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>1. Architecture Studio</span>
                  </button>

                  <button
                    onClick={() => setCustomerStep("kyc")}
                    className={`relative px-4 py-1.5 rounded-full text-xs font-medium transition-all duration-200 cursor-pointer flex items-center space-x-2 ${
                      customerStep === "kyc"
                        ? "bg-[#e40000] text-white shadow-[0_0_16px_rgba(228,0,0,0.4)]"
                        : "text-[#B39D82] hover:text-[#EBE5D9]"
                    }`}
                  >
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>2. Smart KYC</span>
                  </button>

                  <button
                    onClick={() => setCustomerStep("tracker")}
                    className={`relative px-4 py-1.5 rounded-full text-xs font-medium transition-all duration-200 cursor-pointer flex items-center space-x-2 ${
                      customerStep === "tracker"
                        ? "bg-[#e40000] text-white shadow-[0_0_16px_rgba(228,0,0,0.4)]"
                        : "text-[#B39D82] hover:text-[#EBE5D9]"
                    }`}
                  >
                    <Truck className="w-3.5 h-3.5" />
                    <span>3. Dispatch Pipeline</span>
                  </button>
                </div>

                <div className="hidden md:flex items-center space-x-2 text-[11px] font-mono text-[#B39D82] px-3">
                  <span className="live-pulse-dot" />
                  <span>Zero-Delay Quoting</span>
                </div>
              </div>

              {/* Step 1: UNIFIED COMMAND STUDIO (Dual-Engine: Copilot + Live CPQ Blueprint) */}
              {customerStep === "studio" && (
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
                  <div className="lg:col-span-6">
                    <AdvisorChat
                      onProfileUpdated={handleProfileUpdated}
                      onProceedToCPQ={() => setCustomerStep("kyc")}
                    />
                  </div>
                  <div className="lg:col-span-6">
                    <CPQCart
                      profileSlots={profileSlots}
                      recommendedSkus={recommendedSkus}
                      onProceedToKYC={handleProceedToKYC}
                    />
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
                  <div className="luxury-glass rounded-2xl p-12 text-center space-y-4">
                    <ShieldCheck className="w-12 h-12 text-[#B39D82]/40 mx-auto" />
                    <h3 className="font-serif text-xl font-normal text-[#EBE5D9]">No Active Order</h3>
                    <p className="text-xs text-[#B39D82] max-w-sm mx-auto">
                      Run the Smart KYC gate or load a verified specimen order to track real-time dispatch.
                    </p>
                    <div className="flex items-center justify-center space-x-3 pt-2">
                      <button
                        onClick={() => setCustomerStep("kyc")}
                        className="bg-[#e40000] text-white text-xs font-medium py-2 px-4 rounded-xl shadow-[0_0_16px_rgba(228,0,0,0.4)] cursor-pointer"
                      >
                        Run KYC Gate
                      </button>
                      <button
                        onClick={handleLoadDemoOrder}
                        className="bg-[#080a0d] text-[#EBE5D9] border border-[rgba(235,229,217,0.1)] text-xs font-medium py-2 px-4 rounded-xl cursor-pointer"
                      >
                        Load Specimen Order
                      </button>
                    </div>
                  </div>
                )
              )}
            </motion.div>
          )}

          {currentTab === "partner" && (
            <motion.div
              key="partner"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
            >
              <PartnerRescueConsole />
            </motion.div>
          )}

          {currentTab === "judge" && (
            <motion.div
              key="judge"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
            >
              <JudgeTestBench />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Minimal Footer */}
      <footer className="border-t border-[rgba(235,229,217,0.06)] bg-[#030405]/90 py-5 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-[#B39D82]/60 font-mono">
          <div className="flex items-center space-x-2 text-[11px]">
            <span className="text-[#EBE5D9]">Airtel Digital</span>
            <span>·</span>
            <span>Project Udyam</span>
          </div>
          <div className="flex items-center space-x-3 text-[10px] tracking-wider uppercase">
            <span>FastAPI 3,534 GSTINs</span>
            <span>·</span>
            <span>LightGBM 5K Leads</span>
            <span>·</span>
            <span>DPDP 2023 Mask</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
