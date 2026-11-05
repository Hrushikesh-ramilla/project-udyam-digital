import React, { useState } from "react";
import { motion } from "motion/react";
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
    <div className="max-w-4xl mx-auto space-y-5">
      {/* Order Header */}
      <div className="luxury-glass rounded-2xl p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border border-[rgba(235,229,217,0.06)] shadow-apple-card">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-[10px] font-mono bg-[#e40000] text-white px-2 py-0.5 rounded-full font-medium">
              ORDER #{order.order_id}
            </span>
            <span className="text-xs font-mono text-[#B39D82]">
              {order.is_activated ? "ACTIVATED" : "IN-PROGRESS"}
            </span>
          </div>
          <h2 className="font-serif text-xl font-normal text-[#EBE5D9] mt-1.5">{order.business_name}</h2>
          <p className="text-xs text-[#B39D82] mt-0.5">
            {order.bundle_name} · SLA: {order.total_sla_days} Days
          </p>
        </div>

        {/* Commission */}
        <div className="bg-[#030405] border border-[rgba(235,229,217,0.06)] rounded-xl p-3 flex items-center space-x-3 shrink-0">
          <Award className="w-5 h-5 text-[#d9ad63]" />
          <div className="text-xs">
            <span className="text-[#B39D82] block">Partner Commission</span>
            <span className="font-serif text-base text-[#d9ad63]">
              ₹{order.partner_commission_inr.toLocaleString()}
            </span>
          </div>
        </div>
      </div>

      {/* 6-Stage Stepper */}
      <div className="luxury-glass rounded-2xl p-5 space-y-4 border border-[rgba(235,229,217,0.06)] shadow-apple-card">
        <div className="flex items-center justify-between pb-2 border-b border-[rgba(235,229,217,0.04)]">
          <h3 className="font-sans text-xs font-semibold text-[#EBE5D9] uppercase tracking-wider">
            6-Stage Fulfillment Pipeline
          </h3>
          <span className="text-xs font-mono text-[#B39D82]">
            Stage {order.current_stage_idx + 1} of 6
          </span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-6 gap-2.5">
          {order.milestones.map((ms, idx) => {
            const isCurrent = idx === order.current_stage_idx;
            const isPassed = ms.status === "COMPLETED";

            return (
              <motion.div
                key={ms.stage_id}
                whileHover={{ scale: 1.02 }}
                onClick={() => setSelectedPreview(ms)}
                className={`p-3 rounded-xl border transition-all cursor-pointer ${
                  isCurrent
                    ? "border-[#e40000] bg-[#e40000]/10 shadow-[0_0_12px_rgba(228,0,0,0.3)]"
                    : isPassed
                    ? "border-emerald-500/30 bg-emerald-950/15"
                    : "border-[rgba(235,229,217,0.04)] bg-[#030405] opacity-50"
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[9px] font-mono text-[#B39D82]">0{idx + 1}</span>
                  {isPassed ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  ) : isCurrent ? (
                    <Clock className="w-3.5 h-3.5 text-amber-400 animate-spin" />
                  ) : (
                    <span className="w-1.5 h-1.5 rounded-full bg-white/20" />
                  )}
                </div>
                <h4 className="text-xs font-medium text-[#EBE5D9] truncate">{ms.stage_name}</h4>
                <div className="mt-1.5 text-[9px] font-mono">
                  {isPassed ? (
                    <span className="text-emerald-400">Done</span>
                  ) : isCurrent ? (
                    <span className="text-amber-400">In Progress</span>
                  ) : (
                    <span className="text-[#B39D82]/50">Pending</span>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>

        {!order.is_activated && (
          <div className="pt-2 flex justify-end">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleAdvance}
              disabled={advancing}
              className="flex items-center space-x-1.5 bg-[#e40000] hover:bg-[#b30000] text-white font-medium py-2 px-4 rounded-xl text-xs shadow-apple-glow disabled:opacity-40 cursor-pointer"
            >
              <span>{advancing ? "Advancing..." : "Simulate Next SLA Stage"}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </motion.button>
          </div>
        )}
      </div>

      {/* WhatsApp Preview Drawer */}
      {selectedPreview && (
        <div className="luxury-glass rounded-2xl p-4 space-y-3 border border-[rgba(235,229,217,0.06)] shadow-apple-card">
          <div className="flex items-center space-x-2 text-xs font-medium text-[#EBE5D9]">
            <MessageSquare className="w-3.5 h-3.5 text-emerald-400" />
            <span>WhatsApp Customer Webhook Feed</span>
          </div>

          <div className="bg-[#0b141a] p-3.5 rounded-xl border border-[rgba(235,229,217,0.04)] space-y-2">
            <div className="flex items-center space-x-2 pb-1.5 border-b border-white/[0.06]">
              <div className="w-5 h-5 rounded-full bg-[#e40000] flex items-center justify-center text-[10px] font-bold text-white">
                A
              </div>
              <span className="text-xs font-medium text-white">Airtel Enterprise</span>
              <span className="text-[9px] text-emerald-400 font-mono">Verified</span>
            </div>
            <div className="bg-[#202c33] p-3 rounded-lg text-xs text-white/90 font-sans">
              <p className="whitespace-pre-line">{selectedPreview.whatsapp_preview}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
