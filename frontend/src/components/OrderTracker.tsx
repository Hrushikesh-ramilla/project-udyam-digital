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
    } catch (err: any) {
      alert(err.message || "Failed to advance order milestone");
    } finally {
      setAdvancing(false);
    }
  };

  const getStageIcon = (idx: number, status: string) => {
    if (status === "COMPLETED") return <CheckCircle2 className="w-5 h-5 text-emerald-400" />;
    if (status === "IN_PROGRESS") return <Clock className="w-5 h-5 text-amber-400 animate-spin" />;
    switch (idx) {
      case 0:
        return <CheckCircle2 className="w-5 h-5 text-slate-500" />;
      case 1:
        return <ShieldCheck className="w-5 h-5 text-slate-500" />;
      case 2:
        return <Wifi className="w-5 h-5 text-slate-500" />;
      case 3:
        return <Truck className="w-5 h-5 text-slate-500" />;
      case 4:
        return <Wrench className="w-5 h-5 text-slate-500" />;
      case 5:
        return <Award className="w-5 h-5 text-slate-500" />;
      default:
        return <Clock className="w-5 h-5 text-slate-500" />;
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Executive Order Header & Partner Commission Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs bg-red-600 text-white font-mono font-bold px-2.5 py-0.5 rounded-full">
              ORDER #{order.order_id}
            </span>
            <span className="text-xs text-slate-400">
              {order.is_activated ? "Status: ACTIVATED" : "Fulfillment In-Progress"}
            </span>
          </div>
          <h2 className="text-xl font-bold text-white mt-1">{order.business_name}</h2>
          <p className="text-xs text-slate-400">
            Package: <strong className="text-slate-200">{order.bundle_name}</strong> (₹
            {order.monthly_charge_inr.toLocaleString()} / mo) • Guaranteed SLA:{" "}
            <strong className="text-slate-200">{order.total_sla_days} Days</strong>
          </p>
        </div>

        {/* Partner Commission Banner */}
        <div className="bg-slate-950/80 border border-amber-500/30 rounded-xl p-3 flex items-center space-x-3">
          <Award className="w-6 h-6 text-amber-400 shrink-0" />
          <div className="text-xs">
            <span className="text-slate-400 block">Channel Partner Commission</span>
            <span className="font-bold text-amber-400 text-sm">
              ₹{order.partner_commission_inr.toLocaleString()}
            </span>
            <span className="text-[10px] text-slate-500 block">15% first-year activation share</span>
          </div>
        </div>
      </div>

      {/* 6-Stage Interactive Visual Stepper */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center space-x-2">
            <Wifi className="w-4 h-4 text-red-500" />
            <span>Deterministic 6-Stage Fulfillment Pipeline</span>
          </h3>
          <span className="text-xs text-slate-400">
            Current Stage: <strong className="text-white">{order.current_stage_idx + 1} / 6</strong>
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
                className={`p-3 rounded-xl border transition-all cursor-pointer relative ${
                  isCurrent
                    ? "border-red-500 bg-red-950/30 shadow-md shadow-red-950/40"
                    : isPassed
                    ? "border-emerald-500/40 bg-emerald-950/10 hover:border-emerald-500/60"
                    : "border-slate-800 bg-slate-950/40 opacity-60"
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono font-bold text-slate-400">
                    STAGE {idx + 1}
                  </span>
                  {getStageIcon(idx, ms.status)}
                </div>
                <h4 className="text-xs font-bold text-white truncate">{ms.stage_name}</h4>
                <p className="text-[10px] text-slate-400 mt-1 line-clamp-2">{ms.description}</p>
                <div className="mt-2 text-[10px] font-mono">
                  {ms.status === "COMPLETED" ? (
                    <span className="text-emerald-400 font-semibold">Done</span>
                  ) : ms.status === "IN_PROGRESS" ? (
                    <span className="text-amber-400 font-semibold">In Progress</span>
                  ) : (
                    <span className="text-slate-500">Pending</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Advance Stage Control */}
        <div className="mt-6 pt-5 border-t border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="text-xs text-slate-400">
            {order.is_activated ? (
              <span className="text-emerald-400 font-bold flex items-center space-x-1">
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
              className="flex items-center justify-center space-x-2 bg-red-600 hover:bg-red-500 text-white font-bold py-2.5 px-5 rounded-xl text-xs sm:text-sm shadow-lg shadow-red-600/30 transition-all disabled:opacity-50"
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
        <div className="lg:col-span-7 bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <MessageSquare className="w-4 h-4 text-emerald-400" />
              <h3 className="text-sm font-semibold text-white">
                Proactive WhatsApp Customer Updates
              </h3>
            </div>
            <span className="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded-full font-mono">
              Live Webhook Feed
            </span>
          </div>

          {selectedPreview ? (
            <div className="bg-[#0b141a] p-4 rounded-xl border border-slate-800 space-y-2">
              <div className="flex items-center space-x-2 pb-2 border-b border-slate-800/80">
                <div className="w-6 h-6 rounded-full bg-red-600 flex items-center justify-center text-[10px] font-bold text-white">
                  A
                </div>
                <div>
                  <span className="text-xs font-bold text-slate-200">Airtel Business Enterprise</span>
                  <span className="text-[10px] text-emerald-400 ml-2 font-mono">Verified Business</span>
                </div>
              </div>
              <div className="bg-[#202c33] p-3.5 rounded-xl text-xs text-slate-200 leading-relaxed font-sans shadow-sm">
                <p className="whitespace-pre-line">{selectedPreview.whatsapp_preview}</p>
                <div className="text-right text-[10px] text-slate-400 mt-2 font-mono">
                  10:14 AM • Delivered ✓✓
                </div>
              </div>
            </div>
          ) : (
            <p className="text-xs text-slate-500">Select a stage above to preview customer notifications.</p>
          )}
        </div>

        {/* Right: Field Engineer / SLA Card */}
        <div className="lg:col-span-5 bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
          <h3 className="text-sm font-semibold text-white flex items-center space-x-2">
            <User className="w-4 h-4 text-blue-400" />
            <span>Assigned Field Technician</span>
          </h3>

          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 font-bold text-sm">
                RK
              </div>
              <div>
                <h4 className="text-xs font-bold text-white">Ramesh Kumar</h4>
                <p className="text-[10px] text-slate-400">Certified Optical Fiber &amp; CPE Specialist</p>
              </div>
            </div>

            <div className="space-y-1.5 text-xs text-slate-300 pt-2 border-t border-slate-800">
              <div className="flex justify-between">
                <span className="text-slate-400">Technician Phone:</span>
                <span className="font-mono text-slate-200">+91 98110-XXXXX</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Installation OTP:</span>
                <span className="font-mono text-emerald-400 font-bold">4892</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">GPS Geo-Fence:</span>
                <span className="text-emerald-400 font-semibold">Matched to Premises</span>
              </div>
            </div>
          </div>

          <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80 text-[11px] text-slate-400 leading-relaxed">
            🚀 <strong>Funnel Impact:</strong> Automated technician allocation and real-time SLA countdown cuts the historical <strong>17.6-day activation cycle</strong> down to <strong>&lt;4 days</strong>, eliminating the 98 dropouts that occur after 21 days of waiting.
          </div>
        </div>
      </div>
    </div>
  );
};
