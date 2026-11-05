import React, { useState } from "react";
import {
  CheckCircle2,
  Clock,
  Truck,
  Wrench,
  Wifi,
  ShieldCheck,
  ChevronRight,
  MessageSquare,
  Award,
  Phone,
  User,
  ArrowRight,
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
      alert(err instanceof Error ? err.message : "Failed to advance order milestone");
    } finally {
      setAdvancing(false);
    }
  };

  const getStageIcon = (idx: number, status: string) => {
    if (status === "COMPLETED") return <CheckCircle2 className="w-5 h-5 text-emerald-400" />;
    if (status === "IN_PROGRESS") return <Clock className="w-5 h-5 text-amber-400 animate-spin" />;
    switch (idx) {
      case 0:
        return <CheckCircle2 className="w-5 h-5 text-white/30" />;
      case 1:
        return <ShieldCheck className="w-5 h-5 text-white/30" />;
      case 2:
        return <Wifi className="w-5 h-5 text-white/30" />;
      case 3:
        return <Truck className="w-5 h-5 text-white/30" />;
      case 4:
        return <Wrench className="w-5 h-5 text-white/30" />;
      case 5:
        return <Award className="w-5 h-5 text-white/30" />;
      default:
        return <Clock className="w-5 h-5 text-white/30" />;
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6 animate-fade-in">
      {/* Executive Order Header & Partner Commission Banner */}
      <div className="glass-card rounded-2xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-5 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-airtel-crimson/5 rounded-full blur-3xl pointer-events-none" />
        <div>
          <div className="flex items-center space-x-2.5">
            <span className="text-xs font-mono font-medium bg-airtel-crimson text-white px-2.5 py-0.5 rounded-full shadow-airtel-glow">
              ORDER #{order.order_id}
            </span>
            <span className="text-xs font-mono text-white/50">
              {order.is_activated ? "Status: ACTIVATED" : "Fulfillment In-Progress"}
            </span>
          </div>
          <h2 className="font-serif text-2xl font-normal text-white mt-2">{order.business_name}</h2>
          <p className="text-xs text-white/60 mt-1">
            Package: <strong className="text-white/90 font-medium">{order.bundle_name}</strong> (₹
            {order.monthly_charge_inr.toLocaleString()} / mo) • Guaranteed SLA:{" "}
            <strong className="text-white/90 font-mono font-medium">{order.total_sla_days} Days</strong>
          </p>
        </div>

        {/* Partner Commission Banner */}
        <div className="bg-obsidian-surface/80 border border-champagne-gold/30 rounded-xl p-3.5 flex items-center space-x-3.5 shrink-0">
          <div className="w-10 h-10 rounded-lg bg-champagne-gold/10 border border-champagne-gold/30 flex items-center justify-center text-champagne-gold">
            <Award className="w-5 h-5" />
          </div>
          <div className="text-xs">
            <span className="text-white/50 block">Channel Partner Commission</span>
            <span className="font-serif text-xl font-medium text-champagne-gold">
              ₹{order.partner_commission_inr.toLocaleString()}
            </span>
            <span className="text-[10px] text-white/40 block">15% first-year activation share</span>
          </div>
        </div>
      </div>

      {/* 6-Stage Interactive Visual Stepper */}
      <div className="glass-card rounded-2xl p-6">
        <div className="flex items-center justify-between mb-6 pb-2 border-b border-white/[0.06]">
          <h3 className="font-serif text-base font-normal text-white flex items-center space-x-2">
            <Wifi className="w-4 h-4 text-airtel-crimson" />
            <span>Deterministic 6-Stage Fulfillment Pipeline</span>
          </h3>
          <span className="text-xs font-mono text-white/50">
            Current Stage: <strong className="text-white font-medium">{order.current_stage_idx + 1} / 6</strong>
          </span>
        </div>

        {/* Stepper bar */}
        <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
          {order.milestones.map((ms, idx) => {
            const isCurrent = idx === order.current_stage_idx;
            const isPassed = ms.status === "COMPLETED";

            return (
              <div
                key={ms.stage_id}
                onClick={() => setSelectedPreview(ms)}
                className={`p-3.5 rounded-xl border transition-all cursor-pointer relative ${
                  isCurrent
                    ? "border-airtel-crimson/70 bg-airtel-crimson/10 shadow-airtel-glow"
                    : isPassed
                    ? "border-emerald-500/40 bg-emerald-950/20 hover:border-emerald-500/60"
                    : "border-white/[0.06] bg-obsidian-surface/60 opacity-50"
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono text-white/40">
                    STAGE {idx + 1}
                  </span>
                  {getStageIcon(idx, ms.status)}
                </div>
                <h4 className="text-xs font-medium text-white truncate">{ms.stage_name}</h4>
                <p className="text-[10px] text-white/50 mt-1 line-clamp-2 leading-relaxed">{ms.description}</p>
                <div className="mt-2 text-[10px] font-mono">
                  {ms.status === "COMPLETED" ? (
                    <span className="text-emerald-400 font-medium">Done</span>
                  ) : ms.status === "IN_PROGRESS" ? (
                    <span className="text-amber-400 font-medium">In Progress</span>
                  ) : (
                    <span className="text-white/40">Pending</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Advance Stage Control */}
        <div className="mt-6 pt-5 border-t border-white/[0.06] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="text-xs text-white/50">
            {order.is_activated ? (
              <span className="text-emerald-400 font-medium flex items-center space-x-1.5">
                <CheckCircle2 className="w-4 h-4" />
                <span>Service 100% Provisioned &amp; Online. Zero back-office delays!</span>
              </span>
            ) : (
              <span>
                Simulate post-sales operational transitions across OSS/BSS, field inventory, and engineer dispatch.
              </span>
            )}
          </div>

          {!order.is_activated && (
            <button
              onClick={handleAdvance}
              disabled={advancing}
              className="flex items-center justify-center space-x-2 bg-airtel-crimson hover:bg-airtel-hover text-white font-medium py-2.5 px-5 rounded-xl text-xs sm:text-sm shadow-airtel-glow transition-all disabled:opacity-50 cursor-pointer"
            >
              <span>{advancing ? "Transitioning..." : "Simulate Next SLA Milestone"}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* WhatsApp Proactive Notification Drawer & Technician Card */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: WhatsApp Push Notification Preview */}
        <div className="lg:col-span-7 glass-card rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4 pb-2 border-b border-white/[0.06]">
            <div className="flex items-center space-x-2">
              <MessageSquare className="w-4 h-4 text-emerald-400" />
              <h3 className="font-serif text-base font-normal text-white">
                Proactive WhatsApp Customer Updates
              </h3>
            </div>
            <span className="text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-2.5 py-0.5 rounded-full">
              Live Webhook Feed
            </span>
          </div>

          {selectedPreview ? (
            <div className="bg-[#0b141a] p-4 rounded-xl border border-white/[0.08] space-y-2.5">
              <div className="flex items-center space-x-2 pb-2.5 border-b border-white/[0.08]">
                <div className="w-7 h-7 rounded-full bg-airtel-crimson flex items-center justify-center text-xs font-bold text-white shadow-airtel-glow">
                  A
                </div>
                <div>
                  <span className="text-xs font-medium text-white">Airtel Business Enterprise</span>
                  <span className="text-[10px] text-emerald-400 ml-2 font-mono">Verified Business</span>
                </div>
              </div>
              <div className="bg-[#202c33] p-4 rounded-xl text-xs text-white/90 leading-relaxed font-sans shadow-sm border border-white/[0.04]">
                <p className="whitespace-pre-line">{selectedPreview.whatsapp_preview}</p>
                <div className="text-right text-[10px] text-white/40 mt-2 font-mono">
                  10:14 AM • Delivered ✓✓
                </div>
              </div>
            </div>
          ) : (
            <p className="text-xs text-white/40">Select a stage above to preview customer notifications.</p>
          )}
        </div>

        {/* Right: Field Engineer / SLA Card */}
        <div className="lg:col-span-5 glass-card rounded-2xl p-6 space-y-4">
          <h3 className="font-serif text-base font-normal text-white flex items-center space-x-2">
            <User className="w-4 h-4 text-blue-400" />
            <span>Assigned Field Technician</span>
          </h3>

          <div className="bg-obsidian-surface/60 p-4 rounded-xl border border-white/[0.06] space-y-3">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-blue-500/15 border border-blue-500/30 flex items-center justify-center text-blue-400 font-serif font-medium text-sm">
                RK
              </div>
              <div>
                <h4 className="text-xs font-medium text-white">Ramesh Kumar</h4>
                <p className="text-[10px] text-white/50">Certified Optical Fiber &amp; CPE Specialist</p>
              </div>
            </div>

            <div className="space-y-2 text-xs text-white/70 pt-3 border-t border-white/[0.06]">
              <div className="flex justify-between">
                <span className="text-white/50">Technician Phone:</span>
                <span className="font-mono text-white/90">+91 98110-XXXXX</span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/50">Installation OTP:</span>
                <span className="font-mono text-emerald-400 font-medium">4892</span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/50">GPS Geo-Fence:</span>
                <span className="text-emerald-400 font-medium">Matched to Premises</span>
              </div>
            </div>
          </div>

          <div className="bg-obsidian-surface/40 p-3 rounded-xl border border-white/[0.04] text-[11px] text-white/50 leading-relaxed">
            🚀 <strong>Funnel Impact:</strong> Automated technician allocation and real-time SLA countdown cuts the historical <strong>17.6-day activation cycle</strong> down to <strong>&lt;4 days</strong>, eliminating the 98 dropouts that occur after 21 days of waiting.
          </div>
        </div>
      </div>
    </div>
  );
};
