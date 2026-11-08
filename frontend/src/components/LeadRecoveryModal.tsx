import React, { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { X, Copy, Check, MessageSquare, ShoppingCart, Sparkles, Building2, MapPin, IndianRupee, AlertCircle } from "lucide-react";
import { LeadRescueItem } from "../types";

export interface LeadRecoveryModalProps {
  lead: LeadRescueItem | null;
  isOpen: boolean;
  onClose: () => void;
  onPreHydrateCart?: (lead: LeadRescueItem, skus: string[]) => void;
}

export function getRecoveryPitchDetails(lead: LeadRescueItem): {
  pitch: string;
  recommendedSkus: string[];
  bundleName: string;
} {
  const normDrop = (lead.drop_reason || "").toLowerCase();
  const cleanId = lead.lead_id.replace(/[^A-Za-z0-9_-]/g, "");

  if (normDrop.includes("site not feasible") || normDrop.includes("fibre") || normDrop.includes("fiber")) {
    return {
      pitch: `Namaste ${lead.business_name}, we noticed optical fiber lines couldn't reach your premises in ${lead.city}. We have reserved our new Biz 5G AirFiber 100 wireless antenna for your office with a 100% waived setup fee (₹0 upfront). Your wireless circuit is pre-allocated with 48-hour delivery. Confirm your setup here: https://airtel.hrushikeshramilla.in/?lead=${cleanId}&bundle=P04`,
      recommendedSkus: ["P04"],
      bundleName: "Biz 5G AirFiber 100 (Zero Trenching)",
    };
  }

  if (normDrop.includes("payment") || normDrop.includes("price") || normDrop.includes("cheaper")) {
    return {
      pitch: `Namaste ${lead.business_name}, we understand pricing and cash-flow flexibility are vital for your operations in ${lead.city}. We have approved a 100% OTC installation waiver plus an instant 10% monthly rebate voucher with AutoPay for your business bundle. Complete your frictionless activation here: https://airtel.hrushikeshramilla.in/?lead=${cleanId}&discount=10`,
      recommendedSkus: ["P01", "P08"],
      bundleName: "Biz Fiber 100M + Static IPv4 (10% Rebate & ₹0 OTC)",
    };
  }

  if (normDrop.includes("document") || normDrop.includes("missing gst") || normDrop.includes("gstin") || !lead.has_gstin) {
    return {
      pitch: `Namaste ${lead.business_name}, no GST number? No problem! Under Airtel Udyam Digital, you can fast-track your enterprise broadband using only your Udyam Certificate with zero-touch DigiLocker approval in 10 seconds. Claim your verified connection here: https://airtel.hrushikeshramilla.in/?lead=${cleanId}&channel=udyam`,
      recommendedSkus: ["P01"],
      bundleName: "Udyam-Only Smart KYC Fast-Track (GST-Exempt)",
    };
  }

  if (normDrop.includes("delayed") || normDrop.includes("delay") || normDrop.includes("21 days")) {
    return {
      pitch: `Namaste ${lead.business_name}, we apologize for the previous installation delay in ${lead.city}. We have escalated your order to Priority Red-Carpet Dispatch with a dedicated field engineer and a complimentary 1st-month service credit. Track your priority dispatch here: https://airtel.hrushikeshramilla.in/?lead=${cleanId}&priority=true`,
      recommendedSkus: ["P02"],
      bundleName: "Biz Fiber 300M (Priority 48-Hr Dispatch + Credit)",
    };
  }

  return {
    pitch: `Namaste ${lead.business_name}, skip legacy PDF delays! We have prepared a 1-click interactive mobile CPQ quote tailored to your business needs in ${lead.city} with instant discount locking. Review and lock your quote here: https://airtel.hrushikeshramilla.in/?lead=${cleanId}&view=instant`,
    recommendedSkus: ["P01"],
    bundleName: "1-Click Interactive Mobile CPQ Bundle",
  };
}

export const LeadRecoveryModal: React.FC<LeadRecoveryModalProps> = ({
  lead,
  isOpen,
  onClose,
  onPreHydrateCart,
}) => {
  const [copied, setCopied] = useState<boolean>(false);

  if (!isOpen || !lead) return null;

  const { pitch, recommendedSkus, bundleName } = getRecoveryPitchDetails(lead);
  const waLink = `https://wa.me/?text=${encodeURIComponent(pitch)}`;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(pitch);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch {
      // Fallback
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    }
  };

  const handlePreHydrate = () => {
    if (onPreHydrateCart) {
      onPreHydrateCart(lead, recommendedSkus);
      onClose();
    }
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="fixed inset-0 bg-black/80 backdrop-blur-md"
        />

        {/* Modal Window / Drawer */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 15 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 15 }}
          transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
          className="relative w-full max-w-2xl bg-[#090b0e] border border-[rgba(235,229,217,0.12)] rounded-3xl p-6 sm:p-7 shadow-[0_25px_60px_rgba(0,0,0,0.85)] z-10 space-y-5 overflow-hidden"
        >
          {/* Header */}
          <div className="flex items-start justify-between gap-4 pb-4 border-b border-[rgba(235,229,217,0.08)]">
            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-mono tracking-wider bg-[#e40000]/15 text-[#e40000] border border-[#e40000]/30 font-semibold uppercase">
                  Next-Best-Action (NBA)
                </span>
                <span className="text-xs text-[#B39D82] font-mono">Lead ID: {lead.lead_id}</span>
              </div>
              <h2 className="font-serif text-xl sm:text-2xl font-normal text-[#EBE5D9]">
                Automated Recovery Pitch — <span className="text-[#d9ad63]">{lead.business_name}</span> ({lead.city})
              </h2>
            </div>
            <button
              onClick={onClose}
              className="p-2 text-[#B39D82] hover:text-[#EBE5D9] hover:bg-white/5 rounded-xl transition-colors"
              aria-label="Close dialog"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Lead Context Chips */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 p-3.5 bg-[#030405] border border-[rgba(235,229,217,0.06)] rounded-2xl text-xs">
            <div className="space-y-0.5">
              <span className="text-[10px] text-[#B39D82] uppercase font-mono">Segment</span>
              <div className="text-[#EBE5D9] font-medium flex items-center space-x-1">
                <Building2 className="w-3.5 h-3.5 text-[#B39D82]" />
                <span className="truncate">{lead.segment}</span>
              </div>
            </div>
            <div className="space-y-0.5">
              <span className="text-[10px] text-[#B39D82] uppercase font-mono">Location</span>
              <div className="text-[#EBE5D9] font-medium flex items-center space-x-1">
                <MapPin className="w-3.5 h-3.5 text-blue-400" />
                <span>{lead.city} (Tier {lead.city_tier})</span>
              </div>
            </div>
            <div className="space-y-0.5">
              <span className="text-[10px] text-[#B39D82] uppercase font-mono">Monthly Budget</span>
              <div className="text-[#d9ad63] font-medium font-mono flex items-center">
                <IndianRupee className="w-3 h-3" />
                <span>{lead.monthly_spend_inr.toLocaleString()}</span>
              </div>
            </div>
            <div className="space-y-0.5">
              <span className="text-[10px] text-[#B39D82] uppercase font-mono">Winback Score</span>
              <div className="text-emerald-400 font-medium font-mono">
                {lead.propensity_score > 1.0 ? lead.propensity_score.toFixed(1) : (lead.propensity_score * 100).toFixed(1)}% ({lead.priority_tier})
              </div>
            </div>
          </div>

          {/* Drop-Off Root Cause Callout */}
          <div className="flex items-start space-x-2.5 p-3 bg-red-950/20 border border-red-800/30 rounded-xl text-xs">
            <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
            <div className="space-y-0.5">
              <span className="text-red-300 font-medium">Drop-Off Root Cause Identified:</span>
              <p className="text-[#EBE5D9]/80 font-mono text-[11px]">{lead.drop_reason || "Quoting funnel timeout"}</p>
            </div>
          </div>

          {/* Personalized Recovery Pitch Box */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-[#d9ad63]" />
                <span className="text-xs font-mono uppercase text-[#B39D82] tracking-wider">
                  Tailored WhatsApp Pitch ({bundleName})
                </span>
              </div>
              {copied && (
                <span className="text-[11px] font-mono text-emerald-400 flex items-center space-x-1 animate-pulse">
                  <Check className="w-3.5 h-3.5" />
                  <span>Copied pitch to clipboard!</span>
                </span>
              )}
            </div>
            <div className="relative p-4 bg-[#030405] border border-[rgba(235,229,217,0.08)] rounded-2xl">
              <p className="text-xs sm:text-sm text-[#EBE5D9] leading-relaxed whitespace-pre-line font-sans">
                {pitch}
              </p>
            </div>
          </div>

          {/* Functional Actions */}
          <div className="pt-2 flex flex-col sm:flex-row items-center gap-3">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleCopy}
              className="w-full sm:w-auto flex-1 inline-flex items-center justify-center space-x-2 px-4 py-2.5 bg-white/5 hover:bg-white/10 border border-[rgba(235,229,217,0.12)] text-[#EBE5D9] rounded-xl text-xs font-medium transition-all"
            >
              {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4 text-[#B39D82]" />}
              <span>{copied ? "Copied to Clipboard" : "Copy Recovery Pitch"}</span>
            </motion.button>

            <motion.a
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              href={waLink}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full sm:w-auto flex-1 inline-flex items-center justify-center space-x-2 px-4 py-2.5 bg-[#25D366] hover:bg-[#20ba59] text-black font-semibold rounded-xl text-xs transition-all shadow-[0_0_18px_rgba(37,211,102,0.3)]"
            >
              <MessageSquare className="w-4 h-4" />
              <span>Open in WhatsApp</span>
            </motion.a>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handlePreHydrate}
              className="w-full sm:w-auto flex-1 inline-flex items-center justify-center space-x-2 px-4 py-2.5 bg-[#e40000] hover:bg-[#c00000] text-white font-medium rounded-xl text-xs transition-all shadow-[0_0_18px_rgba(228,0,0,0.35)]"
            >
              <ShoppingCart className="w-4 h-4" />
              <span>Pre-Hydrate into Cart</span>
            </motion.button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
