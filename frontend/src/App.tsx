import React, { useState, useEffect } from "react";
import Lenis from "lenis";
import { motion, AnimatePresence } from "motion/react";
import { Navbar } from "./components/Navbar";
import { StudioStudio } from "./components/StudioStudio";
import { SmartKYC } from "./components/SmartKYC";
import { OrderTracker } from "./components/OrderTracker";
import { PartnerRescueConsole } from "./components/PartnerRescueConsole";
import { JudgeTestBench } from "./components/JudgeTestBench";
import {
  MSMEProfileSlots,
  CommercialBreakdown,
  KYCVerificationResult,
  ProvisioningOrder,
  AppPersona,
} from "./types";
import { createProvisioningOrder, calculateQuote } from "./api";
import { ShieldCheck, Sparkles, ArrowRight } from "lucide-react";

declare global {
  interface Window {
    __lenis?: Lenis;
  }
}

export const App: React.FC = () => {
  const [persona, setPersona] = useState<AppPersona>("CUSTOMER");
  const [currentTab, setTab] = useState<"studio" | "kyc" | "tracker" | "partner" | "judge">("studio");

  // Global Session State
  const [profileSlots, setProfileSlots] = useState<MSMEProfileSlots | null>(null);
  const [recommendedSkus, setRecommendedSkus] = useState<string[]>([]);
  const [quote, setQuote] = useState<CommercialBreakdown | null>(null);
  const [kycResult, setKycResult] = useState<KYCVerificationResult | null>(null);
  const [order, setOrder] = useState<ProvisioningOrder | null>(null);

  // Initialize Lenis smooth inertial scroll with nested scroll protection
  useEffect(() => {
    const lenis = new Lenis({
      duration: 1.0,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      autoResize: true,
      allowNestedScroll: true,
      prevent: (node) => {
        if (!(node instanceof HTMLElement)) return false;
        if (node.hasAttribute("data-lenis-prevent") || Boolean(node.closest("[data-lenis-prevent]"))) {
          return true;
        }
        // Seamless nested scroll chaining: only prevent while container has scroll room
        const scrollable = node.closest(".overflow-y-auto") as HTMLElement | null;
        if (scrollable && scrollable.scrollHeight > scrollable.clientHeight) {
          const atTop = scrollable.scrollTop <= 2;
          const atBottom = scrollable.scrollTop + scrollable.clientHeight >= scrollable.scrollHeight - 2;
          if (atTop || atBottom) {
            return false;
          }
          return true;
        }
        return false;
      },
    });

    // Dynamically recalculate document bounds on DOM mutations and container expansions
    const resizeObserver = new ResizeObserver(() => {
      lenis.resize();
    });
    if (document.body) {
      resizeObserver.observe(document.body);
    }
    const rootEl = document.getElementById("root");
    if (rootEl) {
      resizeObserver.observe(rootEl);
    }

    window.__lenis = lenis;

    function raf(time: number) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }
    const reqId = requestAnimationFrame(raf);
    return () => {
      cancelAnimationFrame(reqId);
      resizeObserver.disconnect();
      lenis.destroy();
      delete window.__lenis;
    };
  }, []);

  const handleProfileUpdated = (slots: MSMEProfileSlots, skus?: string[]) => {
    setProfileSlots(slots);
    if (skus && skus.length > 0) setRecommendedSkus(skus);
  };

  const handleProceedToKYC = (calculatedQuote: CommercialBreakdown) => {
    setQuote(calculatedQuote);
    setTab("kyc");
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
      setTab("tracker");
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
            stage_name: "Order Placed & Quote Locked",
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
            whatsapp_preview: "KYC Approved instantly. National ID masked to SYN-XXXX-889.",
          },
          {
            stage_id: "FEASIBILITY",
            stage_name: "Fiber Feasibility & Port Allocation",
            status: "IN_PROGRESS",
            timestamp: null,
            eta_days: 1,
            description: "Checking local splitter port and OLT port capacity.",
            whatsapp_preview: "Fiber feasibility check in progress.",
          },
          {
            stage_id: "CPE_DISPATCH",
            stage_name: "CPE Wi-Fi 6 Router Dispatched",
            status: "PENDING",
            timestamp: null,
            eta_days: 2,
            description: "Airtel Wi-Fi 6 Dual-Band Gateway dispatched from regional hub.",
            whatsapp_preview: "Hardware dispatched with tracking ID #AT-8841-DL.",
          },
          {
            stage_id: "ENGINEER_ASSIGNED",
            stage_name: "Field Engineer Assigned",
            status: "PENDING",
            timestamp: null,
            eta_days: 3,
            description: "Senior field technician allocated with digital OTP check-in.",
            whatsapp_preview: "Engineer Rajesh Kumar (+91 98765 43210) assigned for installation.",
          },
          {
            stage_id: "ACTIVATION",
            stage_name: "Service Activated & Live",
            status: "PENDING",
            timestamp: null,
            eta_days: 4,
            description: "End-to-end fiber loop active with 99.9% uptime SLA.",
            whatsapp_preview: "Congratulations! Your Airtel enterprise broadband is live.",
          },
        ],
        is_activated: false,
      });
      setTab("tracker");
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
          stage_name: "Order Placed & Quote Locked",
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
          stage_name: "Fiber Feasibility & Port Allocation",
          status: "IN_PROGRESS",
          timestamp: null,
          eta_days: 1,
          description: "Splitter port #4 allocated at Main Street Junction.",
          whatsapp_preview: "Fiber loop feasibility passed with 1.2dB loss margin.",
        },
        {
          stage_id: "CPE_DISPATCH",
          stage_name: "CPE Wi-Fi 6 Router Dispatched",
          status: "PENDING",
          timestamp: null,
          eta_days: 2,
          description: "Dual-Band Wi-Fi 6 Airtel Business Gateway dispatched from warehouse.",
          whatsapp_preview: "Hardware in transit with bluedart air courier #BD-9912.",
        },
        {
          stage_id: "ENGINEER_ASSIGNED",
          stage_name: "Field Engineer Assigned",
          status: "PENDING",
          timestamp: null,
          eta_days: 3,
          description: "Technician Rajesh Kumar allocated with OTP: 8492.",
          whatsapp_preview: "Field engineer scheduled for slot 11:00 AM tomorrow.",
        },
        {
          stage_id: "ACTIVATION",
          stage_name: "Service Activated & Live",
          status: "PENDING",
          timestamp: null,
          eta_days: 4,
          description: "Line testing verified at 200 Mbps symmetric. Billing initialized.",
          whatsapp_preview: "Your Airtel Business Fiber is officially active! Enjoy seamless connectivity.",
        },
      ],
      is_activated: false,
    });
  };

  return (
    <div className="min-h-screen bg-[#030405] text-[#EBE5D9] flex flex-col font-sans selection:bg-[#e40000]/30 selection:text-white relative">
      <Navbar currentTab={currentTab} setTab={setTab} persona={persona} setPersona={setPersona} />

      <main className="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 py-10 sm:py-14">
        <AnimatePresence mode="wait">
          {currentTab === "studio" && (
            <motion.div
              key="studio"
              initial={{ opacity: 0, y: 16, filter: "blur(4px)" }}
              animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
              exit={{ opacity: 0, y: -12, filter: "blur(4px)" }}
              transition={{ duration: 0.38, ease: [0.16, 1, 0.3, 1] }}
            >
              <StudioStudio
                profileSlots={profileSlots}
                recommendedSkus={recommendedSkus}
                onProfileUpdated={handleProfileUpdated}
                onProceedToKYC={handleProceedToKYC}
              />
            </motion.div>
          )}

          {currentTab === "kyc" && (
            <motion.div
              key="kyc"
              initial={{ opacity: 0, y: 16, filter: "blur(4px)" }}
              animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
              exit={{ opacity: 0, y: -12, filter: "blur(4px)" }}
              transition={{ duration: 0.38, ease: [0.16, 1, 0.3, 1] }}
            >
              <SmartKYC
                quote={quote}
                onKYCApproved={handleKYCApproved}
                onSwitchToUdyamExempt={handleSwitchToUdyamExempt}
              />
            </motion.div>
          )}

          {currentTab === "tracker" && (
            <motion.div
              key="tracker"
              initial={{ opacity: 0, y: 16, filter: "blur(4px)" }}
              animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
              exit={{ opacity: 0, y: -12, filter: "blur(4px)" }}
              transition={{ duration: 0.38, ease: [0.16, 1, 0.3, 1] }}
            >
              {order ? (
                <OrderTracker order={order} onOrderUpdated={(up) => setOrder(up)} />
              ) : (
                <div className="luxury-glass rounded-3xl p-12 text-center space-y-5 max-w-md mx-auto border border-[rgba(235,229,217,0.08)] shadow-[0_20px_50px_rgba(0,0,0,0.7)]">
                  <div className="w-16 h-16 rounded-2xl bg-white/[0.03] border border-white/[0.06] flex items-center justify-center mx-auto text-[#B39D82]">
                    <ShieldCheck className="w-8 h-8" />
                  </div>
                  <div className="space-y-2">
                    <h3 className="font-serif text-2xl font-normal text-[#EBE5D9]">No Active Order</h3>
                    <p className="text-xs text-[#B39D82] max-w-sm mx-auto leading-relaxed">
                      Complete the Smart KYC gate or load a verified specimen order to observe live 6-stage SLA dispatch telemetry.
                    </p>
                  </div>
                  <div className="flex items-center justify-center space-x-3 pt-3">
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => setTab("kyc")}
                      className="bg-[#e40000] hover:bg-[#b30000] text-white text-xs font-medium py-2.5 px-5 rounded-xl shadow-[0_0_20px_rgba(228,0,0,0.4)] cursor-pointer"
                    >
                      Run Smart KYC
                    </motion.button>
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={handleLoadDemoOrder}
                      className="bg-[#080a0d] hover:bg-[#12161c] text-[#EBE5D9] border border-[rgba(235,229,217,0.1)] text-xs font-medium py-2.5 px-5 rounded-xl cursor-pointer"
                    >
                      Load Specimen Order
                    </motion.button>
                  </div>
                </div>
              )}
            </motion.div>
          )}

          {currentTab === "partner" && (
            <motion.div
              key="partner"
              initial={{ opacity: 0, y: 16, filter: "blur(4px)" }}
              animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
              exit={{ opacity: 0, y: -12, filter: "blur(4px)" }}
              transition={{ duration: 0.38, ease: [0.16, 1, 0.3, 1] }}
            >
              <PartnerRescueConsole />
            </motion.div>
          )}

          {currentTab === "judge" && (
            <motion.div
              key="judge"
              initial={{ opacity: 0, y: 16, filter: "blur(4px)" }}
              animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
              exit={{ opacity: 0, y: -12, filter: "blur(4px)" }}
              transition={{ duration: 0.38, ease: [0.16, 1, 0.3, 1] }}
            >
              <JudgeTestBench />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Minimal Luxury Footer */}
      <footer className="border-t border-[rgba(235,229,217,0.06)] bg-[#030405]/90 py-8 mt-20">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-[#B39D82]/60 font-mono">
          <div className="flex items-center space-x-2 text-[11px]">
            <span className="text-[#EBE5D9] font-medium tracking-wide">Airtel Digital</span>
            <span>·</span>
            <span>Project Udyam Enterprise</span>
          </div>
          <div className="flex items-center space-x-3 text-[10px] tracking-widest uppercase">
            <span>FastAPI 3,534 GSTINs</span>
            <span>·</span>
            <span>LightGBM 5K Leads</span>
            <span>·</span>
            <span className="text-[#d9ad63]">DPDP 2023 Compliant</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
