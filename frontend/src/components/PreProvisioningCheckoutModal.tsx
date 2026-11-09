import React from "react";
import { motion, AnimatePresence } from "motion/react";
import { Zap, ShieldCheck, CreditCard, Banknote, Sparkles, Check, ArrowRight, X, Clock, IndianRupee } from "lucide-react";
import { CommercialBreakdown } from "../types";

export interface PreProvisioningCheckoutModalProps {
  isOpen: boolean;
  onClose: () => void;
  quote: CommercialBreakdown | null;
  businessName: string;
  onConfirmSettlement: (mode: "DIGITAL_PAY" | "POSTPAID_COD") => void;
}

export const PreProvisioningCheckoutModal: React.FC<PreProvisioningCheckoutModalProps> = ({
  isOpen,
  onClose,
  quote,
  businessName,
  onConfirmSettlement,
}) => {
  if (!isOpen) return null;

  const monthlyPrice = quote?.net_mrc_inr || 2499;
  const slaDays = quote?.guaranteed_sla_days || 4;

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

        {/* Modal Window */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 15 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 15 }}
          transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
          className="relative w-full max-w-2xl bg-[#090b0e] border border-[rgba(235,229,217,0.12)] rounded-3xl p-6 sm:p-7 shadow-[0_25px_60px_rgba(0,0,0,0.85)] z-10 space-y-6 overflow-hidden"
        >
          {/* Header */}
          <div className="flex items-start justify-between gap-4 pb-4 border-b border-[rgba(235,229,217,0.08)]">
            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-mono tracking-wider bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 font-semibold uppercase">
                  KYC Verified · Commercial Gate
                </span>
                <span className="text-xs text-[#B39D82] font-mono">Stage 3 of 4</span>
              </div>
              <h2 className="font-serif text-xl sm:text-2xl font-normal text-[#EBE5D9]">
                Commercial Settlement Choice — <span className="text-[#d9ad63]">{businessName}</span>
              </h2>
              <p className="text-xs text-[#B39D82]">
                Select your billing &amp; provisioning preference before hardware dispatch and field technician assignment.
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-2 text-[#B39D82] hover:text-[#EBE5D9] hover:bg-white/5 rounded-xl transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Plan Summary Ribbon */}
          <div className="flex items-center justify-between p-3.5 bg-[#030405] border border-[rgba(235,229,217,0.08)] rounded-2xl text-xs font-mono">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-[#d9ad63]" />
              <span className="text-[#EBE5D9]">Contract Value:</span>
              <strong className="text-[#d9ad63]">₹{monthlyPrice.toLocaleString()}/mo</strong>
            </div>
            <div className="flex items-center space-x-2 text-[#B39D82]">
              <Clock className="w-3.5 h-3.5 text-blue-400" />
              <span>SLA: {slaDays} Business Days</span>
            </div>
          </div>

          {/* 2 Distinct Settlement Options (Issue #37) */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Option A: Instant Digital Pay */}
            <motion.div
              whileHover={{ y: -3 }}
              onClick={() => onConfirmSettlement("DIGITAL_PAY")}
              className="p-5 rounded-2xl bg-gradient-to-b from-[#e40000]/10 via-[#030405] to-[#030405] border-2 border-[#e40000] space-y-4 cursor-pointer relative shadow-[0_0_24px_rgba(228,0,0,0.2)]"
            >
              <div className="flex items-center justify-between">
                <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-mono uppercase bg-[#e40000] text-white font-semibold shadow-sm">
                  <Zap className="w-3 h-3" />
                  <span>Recommended</span>
                </span>
                <span className="text-[10px] font-mono text-emerald-400 font-semibold">Save ₹1,500 OTC</span>
              </div>

              <div>
                <h3 className="text-base font-semibold text-white flex items-center space-x-2">
                  <CreditCard className="w-4 h-4 text-[#e40000]" />
                  <span>Instant Digital Pay</span>
                </h3>
                <p className="text-xs text-[#B39D82] mt-1 leading-relaxed">
                  UPI / Cards / AutoPay with 100% One-Time Setup Fee Waiver.
                </p>
              </div>

              <ul className="text-[11px] text-[#EBE5D9] space-y-2 font-mono">
                <li className="flex items-center space-x-2 text-emerald-300">
                  <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  <span>₹0 Setup Fee (100% OTC Waived)</span>
                </li>
                <li className="flex items-center space-x-2">
                  <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  <span>Priority OLT Port Fast-Track</span>
                </li>
                <li className="flex items-center space-x-2">
                  <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  <span>Immediate Advance Paid Status</span>
                </li>
              </ul>

              <button
                type="button"
                className="w-full py-2.5 px-4 bg-[#e40000] hover:bg-[#b30000] text-white text-xs font-semibold rounded-xl flex items-center justify-center space-x-1.5 transition-colors shadow-md cursor-pointer"
              >
                <span>Select Instant Pay</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </motion.div>

            {/* Option B: Pay Post-Installation (COD) */}
            <motion.div
              whileHover={{ y: -3 }}
              onClick={() => onConfirmSettlement("POSTPAID_COD")}
              className="p-5 rounded-2xl bg-[#030405] border border-[rgba(235,229,217,0.12)] hover:border-[rgba(235,229,217,0.25)] space-y-4 cursor-pointer relative"
            >
              <div className="flex items-center justify-between">
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-mono uppercase bg-white/5 text-[#B39D82] border border-white/10 font-semibold">
                  Post-Installation
                </span>
                <span className="text-[10px] font-mono text-[#B39D82]">Standard Terms</span>
              </div>

              <div>
                <h3 className="text-base font-semibold text-white flex items-center space-x-2">
                  <Banknote className="w-4 h-4 text-[#d9ad63]" />
                  <span>Pay Post-Installation (COD)</span>
                </h3>
                <p className="text-xs text-[#B39D82] mt-1 leading-relaxed">
                  Pay only after physical fiber loop testing &amp; line handover.
                </p>
              </div>

              <ul className="text-[11px] text-[#EBE5D9] space-y-2 font-mono">
                <li className="flex items-center space-x-2">
                  <Check className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                  <span>₹0 Upfront Payment Today</span>
                </li>
                <li className="flex items-center space-x-2">
                  <Check className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                  <span>Line Handover &amp; Speed Verified First</span>
                </li>
                <li className="flex items-center space-x-2 text-[#d9ad63]">
                  <Check className="w-3.5 h-3.5 text-[#d9ad63] shrink-0" />
                  <span>Standard OTC applies on 1st bill</span>
                </li>
              </ul>

              <button
                type="button"
                className="w-full py-2.5 px-4 bg-white/5 hover:bg-white/10 text-[#EBE5D9] border border-[rgba(235,229,217,0.12)] text-xs font-semibold rounded-xl flex items-center justify-center space-x-1.5 transition-colors cursor-pointer"
              >
                <span>Select Postpaid COD</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
