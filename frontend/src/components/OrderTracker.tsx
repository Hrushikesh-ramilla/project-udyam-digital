import React, { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  CheckCircle2,
  Clock,
  Truck,
  Wrench,
  Wifi,
  ShieldCheck,
  Award,
  ArrowRight,
  MessageSquare,
  User,
  Check,
  CheckCheck,
  Sparkles,
} from "lucide-react";
import { ProvisioningOrder, ProvisioningMilestone } from "../types";
import { advanceOrderStage } from "../api";

interface OrderTrackerProps {
  order: ProvisioningOrder;
  onOrderUpdated: (updated: ProvisioningOrder) => void;
}

export const OrderTracker: React.FC<OrderTrackerProps> = ({ order, onOrderUpdated }) => {
  const [advancing, setAdvancing] = useState<boolean>(false);
  const [selectedPreview, setSelectedPreview] = useState<ProvisioningMilestone | null>(
    order.milestones[order.current_stage_idx] || order.milestones[0]
  );

  const handleAdvance = async () => {
    if (order.is_activated) return;
    setAdvancing(true);
    try {
      const updated = await advanceOrderStage(order.order_id);
      onOrderUpdated(updated);
      setSelectedPreview(updated.milestones[updated.current_stage_idx] || updated.milestones[updated.milestones.length - 1]);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Milestone advance failed");
    } finally {
      setAdvancing(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-7">
      {/* Order Header */}
      <div className="luxury-glass rounded-3xl p-6 sm:p-7 flex flex-col sm:flex-row sm:items-center justify-between gap-5 border border-[rgba(235,229,217,0.08)] shadow-[0_20px_50px_rgba(0,0,0,0.7)]">
        <div>
          <div className="flex items-center space-x-2.5">
            <span className="text-[10px] font-mono bg-[#e40000] text-white px-2.5 py-0.5 rounded-full font-semibold tracking-wider">
              ORDER #{order.order_id}
            </span>
            <span className={`text-xs font-mono font-medium px-2 py-0.5 rounded-full border ${
              order.is_activated 
                ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" 
                : "bg-amber-500/15 text-amber-400 border-amber-500/30"
            }`}>
              {order.is_activated ? "ACTIVATED · 100% LIVE" : "IN-PROGRESS · DAY 1"}
            </span>
          </div>
          <h2 className="font-serif text-2xl sm:text-3xl font-normal text-[#EBE5D9] mt-2">{order.business_name}</h2>
          <p className="text-xs text-[#B39D82] mt-1 font-sans">
            {order.bundle_name} · SLA: {order.total_sla_days} Days Guaranteed
          </p>
        </div>

        {/* Partner Commission Card */}
        <div className="bg-[#030405] border border-[rgba(235,229,217,0.08)] rounded-2xl p-4 flex items-center space-x-3.5 shrink-0 shadow-inner">
          <div className="w-10 h-10 rounded-xl bg-[#d9ad63]/15 border border-[#d9ad63]/30 flex items-center justify-center text-[#d9ad63]">
            <Award className="w-5 h-5" />
          </div>
          <div className="text-xs">
            <span className="text-[#B39D82] block text-[11px] font-mono uppercase tracking-wider">Partner Commission</span>
            <span className="font-serif text-2xl text-[#d9ad63] font-normal">
              ₹{order.partner_commission_inr.toLocaleString()}
            </span>
          </div>
        </div>
      </div>

      {/* 6-Stage Fulfillment Stepper */}
      <div className="luxury-glass rounded-3xl p-6 sm:p-7 space-y-6 border border-[rgba(235,229,217,0.08)] shadow-[0_20px_50px_rgba(0,0,0,0.7)]">
        <div className="flex items-center justify-between pb-3 border-b border-[rgba(235,229,217,0.06)]">
          <h3 className="font-sans text-xs font-semibold text-[#EBE5D9] uppercase tracking-widest flex items-center space-x-2">
            <Truck className="w-4 h-4 text-[#e40000]" />
            <span>6-Stage Digital Fulfillment Pipeline</span>
          </h3>
          <span className="text-xs font-mono text-[#d9ad63] bg-white/[0.04] px-2.5 py-0.5 rounded-full border border-white/[0.06]">
            Stage {Math.min(order.current_stage_idx + 1, 6)} of 6
          </span>
        </div>

        {/* Pipeline Stepper Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
          {order.milestones.map((ms, idx) => {
            const isCurrent = idx === order.current_stage_idx && !order.is_activated;
            const isPassed = ms.status === "COMPLETED" || (order.is_activated && idx <= order.current_stage_idx);
            const isSelected = selectedPreview?.stage_id === ms.stage_id;

            return (
              <motion.div
                key={ms.stage_id}
                whileHover={{ scale: 1.015 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setSelectedPreview(ms)}
                className={`p-4 rounded-2xl border transition-all cursor-pointer relative ${
                  isSelected
                    ? "border-[#d9ad63] shadow-[0_0_20px_rgba(217,173,99,0.2)]"
                    : isCurrent
                    ? "border-[#e40000] bg-gradient-to-b from-[#e40000]/15 to-transparent shadow-[0_0_20px_rgba(228,0,0,0.25)]"
                    : isPassed
                    ? "border-emerald-500/30 bg-emerald-950/15"
                    : "border-[rgba(235,229,217,0.05)] bg-[#030405] opacity-50"
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono text-[#B39D82] font-semibold">STAGE 0{idx + 1}</span>
                  {isPassed ? (
                    <div className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                      <Check className="w-3 h-3" />
                    </div>
                  ) : isCurrent ? (
                    <Clock className="w-4 h-4 text-amber-400 animate-spin" />
                  ) : (
                    <span className="w-2 h-2 rounded-full bg-white/20" />
                  )}
                </div>
                <h4 className="text-xs font-semibold text-[#EBE5D9] leading-snug">{ms.stage_name}</h4>
                <p className="text-[11px] text-[#B39D82] mt-1.5 line-clamp-2 leading-relaxed">
                  {ms.description}
                </p>
                <div className="mt-2.5 text-[9px] font-mono uppercase tracking-wider">
                  {isPassed ? (
                    <span className="text-emerald-400 font-medium">✓ Completed</span>
                  ) : isCurrent ? (
                    <span className="text-amber-400 font-medium">● In Progress</span>
                  ) : (
                    <span className="text-[#B39D82]/50">○ Scheduled</span>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Action Button */}
        {!order.is_activated && (
          <div className="pt-2 flex justify-end">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleAdvance}
              disabled={advancing}
              className="flex items-center space-x-2 bg-[#e40000] hover:bg-[#b30000] text-white font-medium py-3 px-6 rounded-2xl text-xs sm:text-sm shadow-[0_0_24px_rgba(228,0,0,0.4)] disabled:opacity-40 cursor-pointer animate-shimmer"
            >
              <span>{advancing ? "Advancing Engine..." : "Simulate Next SLA Stage"}</span>
              <ArrowRight className="w-4 h-4" />
            </motion.button>
          </div>
        )}
      </div>

      {/* WhatsApp Preview Drawer */}
      {selectedPreview && (
        <div className="luxury-glass rounded-3xl p-6 space-y-4 border border-[rgba(235,229,217,0.08)] shadow-[0_20px_50px_rgba(0,0,0,0.7)]">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-xs font-medium text-[#EBE5D9]">
              <MessageSquare className="w-4 h-4 text-emerald-400" />
              <span>Customer WhatsApp Webhook Notification (Automated SLA Hook)</span>
            </div>
            <span className="text-[10px] font-mono text-[#d9ad63] uppercase bg-white/[0.04] px-2 py-0.5 rounded-full">
              Meta WhatsApp API
            </span>
          </div>

          <div className="bg-[#0b141a] p-4 sm:p-5 rounded-2xl border border-[rgba(235,229,217,0.06)] space-y-3 max-w-lg">
            <div className="flex items-center space-x-2.5 pb-2 border-b border-white/[0.06]">
              <div className="w-6 h-6 rounded-full bg-[#e40000] flex items-center justify-center text-[10px] font-bold text-white shadow-sm">
                A
              </div>
              <span className="text-xs font-semibold text-white">Airtel Enterprise Care</span>
              <span className="text-[9px] bg-emerald-500/20 text-emerald-400 px-1.5 py-0.2 rounded font-mono">
                Verified
              </span>
            </div>
            <div className="bg-[#202c33] p-3.5 rounded-xl text-xs text-white/95 font-sans leading-relaxed shadow-sm">
              <p className="whitespace-pre-line">{selectedPreview.whatsapp_preview}</p>
              <div className="flex items-center justify-end space-x-1 mt-2 text-[10px] text-[#B39D82]/70 font-mono">
                <span>10:16 AM</span>
                <CheckCheck className="w-3.5 h-3.5 text-blue-400 inline" />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
