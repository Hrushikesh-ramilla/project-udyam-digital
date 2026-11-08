import React, { useState, useEffect } from "react";
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
  CreditCard,
  QrCode,
  Smartphone,
  ExternalLink,
  PhoneCall,
  X,
  RefreshCw,
  Lock,
} from "lucide-react";
import { ProvisioningOrder, ProvisioningMilestone } from "../types";
import {
  advanceOrderStage,
  createPaymentIntent,
  verifyUPIPayment,
  verifyRazorpayPayment,
  fetchOrderLogistics,
  triggerHardwareDispatch,
  LogisticsDispatch,
  PaymentIntent,
} from "../api";

interface OrderTrackerProps {
  order: ProvisioningOrder;
  onOrderUpdated: (updated: ProvisioningOrder) => void;
}

export const OrderTracker: React.FC<OrderTrackerProps> = ({ order, onOrderUpdated }) => {
  const [advancing, setAdvancing] = useState<boolean>(false);
  const [selectedPreview, setSelectedPreview] = useState<ProvisioningMilestone | null>(
    order.milestones[order.current_stage_idx] || order.milestones[0]
  );

  // Logistics Dispatch State
  const [logistics, setLogistics] = useState<LogisticsDispatch | null>(null);
  const [loadingLogistics, setLoadingLogistics] = useState<boolean>(false);

  // Payment State
  const [showPaymentModal, setShowPaymentModal] = useState<boolean>(false);
  const [paymentIntent, setPaymentIntent] = useState<PaymentIntent | null>(null);
  const [paymentMethodTab, setPaymentMethodTab] = useState<"upi" | "razorpay">("upi");
  const [utrInput, setUtrInput] = useState<string>("202607159841");
  const [paymentStatus, setPaymentStatus] = useState<"IDLE" | "PROCESSING" | "SUCCESS" | "FAILED">("IDLE");
  const [paymentMessage, setPaymentMessage] = useState<string>("");

  useEffect(() => {
    // Automatically load or create logistics dispatch for order
    setLoadingLogistics(true);
    fetchOrderLogistics(order.order_id)
      .then(setLogistics)
      .catch(() => {
        // Fallback or pre-dispatch trigger
        triggerHardwareDispatch(order.order_id)
          .then(setLogistics)
          .catch(() => {});
      })
      .finally(() => setLoadingLogistics(false));
  }, [order.order_id, order.current_stage_idx]);

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

  const handleOpenPayment = async () => {
    setShowPaymentModal(true);
    setPaymentStatus("IDLE");
    setPaymentMessage("");
    try {
      const intent = await createPaymentIntent(order.order_id, order.monthly_charge_inr);
      setPaymentIntent(intent);
    } catch (err: unknown) {
      setPaymentMessage(err instanceof Error ? err.message : "Failed to initialize payment gateway");
    }
  };

  const handleVerifyUPI = async () => {
    if (!paymentIntent) return;
    setPaymentStatus("PROCESSING");
    try {
      const res = await verifyUPIPayment(paymentIntent.payment_id, order.order_id, utrInput);
      if (res.status === "SUCCESS") {
        setPaymentStatus("SUCCESS");
        setPaymentMessage(res.message);
        // Advance milestone if on stage 0
        if (order.current_stage_idx === 0) {
          handleAdvance();
        }
      } else {
        setPaymentStatus("FAILED");
        setPaymentMessage(res.message);
      }
    } catch (err: unknown) {
      setPaymentStatus("FAILED");
      setPaymentMessage(err instanceof Error ? err.message : "Payment verification failed");
    }
  };

  const handleVerifyRazorpaySandbox = async () => {
    if (!paymentIntent) return;
    setPaymentStatus("PROCESSING");
    try {
      const rzpPaymentId = `pay_test_${Date.now()}`;
      // In sandbox mode, use deterministic valid sandbox token
      const res = await verifyRazorpayPayment(
        paymentIntent.payment_id,
        order.order_id,
        paymentIntent.razorpay_order_id,
        rzpPaymentId,
        "demo_sig_valid_sandbox_token"
      );
      if (res.status === "SUCCESS") {
        setPaymentStatus("SUCCESS");
        setPaymentMessage(res.message);
        if (order.current_stage_idx === 0) {
          handleAdvance();
        }
      } else {
        setPaymentStatus("FAILED");
        setPaymentMessage(res.message);
      }
    } catch (err: unknown) {
      setPaymentStatus("FAILED");
      setPaymentMessage(err instanceof Error ? err.message : "Razorpay payment verification failed");
    }
  };

  return (
    <div className="w-full space-y-7">
      {/* Order Header & Action Bar */}
      <div className="luxury-glass rounded-3xl p-6 sm:p-7 flex flex-col sm:flex-row sm:items-center justify-between gap-5 border border-slate-700/70 shadow-[0_20px_50px_rgba(0,0,0,0.7)]">
        <div>
          <div className="flex items-center space-x-2.5">
            <span className="text-[10px] font-mono bg-[#e40000] text-white px-2.5 py-0.5 rounded-full font-semibold tracking-wider">
              ORDER #{order.order_id}
            </span>
            <span
              className={`text-xs font-mono font-medium px-2 py-0.5 rounded-full border ${
                order.is_activated
                  ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                  : "bg-amber-500/15 text-amber-400 border-amber-500/30"
              }`}
            >
              {order.is_activated ? "ACTIVATED · 100% LIVE" : "IN-PROGRESS · DAY 1"}
            </span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-2">
            {order.business_name}
          </h2>
          <p className="text-xs text-slate-300 mt-1 font-sans">
            {order.bundle_name} · SLA: {order.total_sla_days} Days Guaranteed · MRC: ₹{order.monthly_charge_inr.toLocaleString()}/mo
          </p>
        </div>

        {/* Action & Partner Group */}
        <div className="flex flex-wrap items-center gap-3">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleOpenPayment}
            className="flex items-center space-x-2 bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-500 hover:to-teal-600 text-white font-medium py-2.5 px-4 rounded-2xl text-xs shadow-[0_0_20px_rgba(16,185,129,0.3)] cursor-pointer transition-all border border-emerald-400/30"
          >
            <CreditCard className="w-4 h-4 text-emerald-200" />
            <span>💳 Pay Online (UPI / Sandbox)</span>
          </motion.button>

          {/* Partner Commission Card */}
          <div className="bg-slate-900/90 border border-slate-700/70 rounded-2xl p-3.5 flex items-center space-x-3 shadow-inner">
            <div className="w-9 h-9 rounded-xl bg-[#d9ad63]/15 border border-[#d9ad63]/30 flex items-center justify-center text-amber-400">
              <Award className="w-4 h-4" />
            </div>
            <div className="text-xs">
              <span className="text-slate-300 block text-[10px] font-mono uppercase tracking-wider">
                Partner Commission
              </span>
              <span className="text-xl font-bold text-amber-400">
                ₹{order.partner_commission_inr.toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Telecommunications Logistics & Field Engineer Dispatch Card */}
      {logistics && (
        <div className="luxury-glass rounded-3xl p-6 space-y-4 border border-slate-700/70 shadow-[0_20px_50px_rgba(0,0,0,0.7)]">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-xl bg-blue-500/15 border border-blue-500/30 flex items-center justify-center text-blue-400">
                <Truck className="w-4 h-4" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h3 className="font-sans text-xs font-semibold text-white uppercase tracking-wider">
                    BlueDart Telecom Hardware Dispatch &amp; Field Engineer
                  </h3>
                  <span className="text-[9px] font-mono bg-blue-500/20 text-blue-300 border border-blue-500/30 px-2 py-0.5 rounded-full">
                    {logistics.awb_number}
                  </span>
                </div>
                <p className="text-[11px] text-slate-300 mt-0.5">
                  Courier Origin: {logistics.courier_hub}
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <a
                href={logistics.tracking_url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-white/[0.05] hover:bg-white/[0.1] text-[11px] font-medium text-white border border-slate-700/80 transition-colors"
              >
                <span>Track BlueDart</span>
                <ExternalLink className="w-3 h-3 text-slate-300" />
              </a>

              <a
                href={logistics.whatsapp_dispatch_link}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/30 text-[11px] font-medium text-emerald-300 border border-emerald-500/40 transition-colors"
              >
                <MessageSquare className="w-3 h-3 text-emerald-400" />
                <span>WhatsApp Engineer</span>
              </a>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div className="bg-slate-900/90 p-3 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-300 font-mono uppercase block">Assigned Engineer</span>
              <span className="text-white font-medium flex items-center space-x-1 mt-0.5">
                <User className="w-3.5 h-3.5 text-amber-400" />
                <span>{logistics.field_engineer_name}</span>
              </span>
            </div>
            <div className="bg-slate-900/90 p-3 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-300 font-mono uppercase block">Field Phone</span>
              <span className="text-white font-mono mt-0.5 flex items-center space-x-1">
                <PhoneCall className="w-3.5 h-3.5 text-emerald-400" />
                <span>{logistics.field_engineer_phone}</span>
              </span>
            </div>
            <div className="bg-slate-900/90 p-3 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-300 font-mono uppercase block">Dispatch Status</span>
              <span className="text-emerald-400 font-mono mt-0.5 flex items-center space-x-1">
                <Clock className="w-3.5 h-3.5 text-emerald-400" />
                <span>OUT FOR DISPATCH (SLA: ON-TRACK)</span>
              </span>
            </div>
          </div>
        </div>
      )}

      {/* 6-Stage Fulfillment Stepper */}
      <div className="luxury-glass rounded-3xl p-6 sm:p-7 space-y-6 border border-slate-700/70 shadow-[0_20px_50px_rgba(0,0,0,0.7)]">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <h3 className="font-sans text-xs font-semibold text-white uppercase tracking-widest flex items-center space-x-2">
            <Truck className="w-4 h-4 text-[#e40000]" />
            <span>6-Stage Digital Fulfillment Pipeline (SQLite WAL Engine)</span>
          </h3>
          <span className="text-xs font-mono text-amber-400 bg-white/[0.04] px-2.5 py-0.5 rounded-full border border-slate-700">
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
                    : "border-[rgba(235,229,217,0.05)] bg-slate-900/90 opacity-50"
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono text-slate-300 font-semibold">STAGE 0{idx + 1}</span>
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
                <h4 className="text-xs font-semibold text-white leading-snug">{ms.stage_name}</h4>
                <p className="text-[11px] text-slate-300 mt-1.5 line-clamp-2 leading-relaxed">
                  {ms.description}
                </p>
                <div className="mt-2.5 text-[9px] font-mono uppercase tracking-wider">
                  {isPassed ? (
                    <span className="text-emerald-400 font-medium">✓ Completed</span>
                  ) : isCurrent ? (
                    <span className="text-amber-400 font-medium">● In Progress</span>
                  ) : (
                    <span className="text-slate-300/50">○ Scheduled</span>
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
        <div className="luxury-glass rounded-3xl p-6 space-y-4 border border-slate-700/70 shadow-[0_20px_50px_rgba(0,0,0,0.7)]">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-xs font-medium text-white">
              <MessageSquare className="w-4 h-4 text-emerald-400" />
              <span>Customer WhatsApp Webhook Notification (Automated SLA Hook)</span>
            </div>
            <span className="text-[10px] font-mono text-amber-400 uppercase bg-white/[0.04] px-2 py-0.5 rounded-full">
              Meta WhatsApp API
            </span>
          </div>

          <div className="bg-[#0b141a] p-4 sm:p-5 rounded-2xl border border-slate-800 space-y-3 max-w-lg">
            <div className="flex items-center space-x-2.5 pb-2 border-b border-slate-700">
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
              <div className="flex items-center justify-end space-x-1 mt-2 text-[10px] text-slate-300/70 font-mono">
                <span>10:16 AM</span>
                <CheckCheck className="w-3.5 h-3.5 text-blue-400 inline" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Payment Gateway Modal (Native NPCI Dynamic UPI & Razorpay Sandbox) */}
      <AnimatePresence>
        {showPaymentModal && (
          <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-xl flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="luxury-glass-elevated rounded-3xl max-w-lg w-full p-6 space-y-5 border border-white/[0.12] shadow-2xl relative"
            >
              <div className="flex items-center justify-between pb-3 border-b border-slate-700/80">
                <div className="flex items-center space-x-2.5">
                  <div className="w-8 h-8 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                    <CreditCard className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="font-sans font-bold text-lg font-normal text-white">
                      Airtel Business Enterprise Checkout
                    </h3>
                    <p className="text-[11px] text-slate-300">
                      Total Payable: <strong className="text-white font-mono">₹{order.monthly_charge_inr.toLocaleString()}</strong>
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setShowPaymentModal(false)}
                  className="w-7 h-7 rounded-lg bg-white/[0.05] hover:bg-white/[0.1] flex items-center justify-center text-slate-300 hover:text-white"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Payment Method Switcher */}
              <div className="flex space-x-2 bg-slate-900/90 p-1 rounded-2xl border border-slate-700">
                <button
                  onClick={() => setPaymentMethodTab("upi")}
                  className={`flex-1 py-2 rounded-xl text-xs font-medium transition-all cursor-pointer flex items-center justify-center space-x-1.5 ${
                    paymentMethodTab === "upi"
                      ? "bg-[#e40000] text-white shadow-md"
                      : "text-slate-300 hover:text-white"
                  }`}
                >
                  <QrCode className="w-3.5 h-3.5" />
                  <span>Native NPCI UPI (QR &amp; Intent)</span>
                </button>
                <button
                  onClick={() => setPaymentMethodTab("razorpay")}
                  className={`flex-1 py-2 rounded-xl text-xs font-medium transition-all cursor-pointer flex items-center justify-center space-x-1.5 ${
                    paymentMethodTab === "razorpay"
                      ? "bg-[#e40000] text-white shadow-md"
                      : "text-slate-300 hover:text-white"
                  }`}
                >
                  <ShieldCheck className="w-3.5 h-3.5 text-blue-400" />
                  <span>Razorpay Sandbox</span>
                </button>
              </div>

              {/* TAB 1: NPCI Dynamic UPI Intent */}
              {paymentMethodTab === "upi" && (
                <div className="space-y-4">
                  {paymentIntent ? (
                    <div className="flex flex-col sm:flex-row items-center gap-4 bg-slate-900/90 p-4 rounded-2xl border border-slate-700">
                      <div className="bg-[#FAF8F5] p-2 rounded-xl shrink-0 shadow-md">
                        <img
                          src={paymentIntent.qr_data_url}
                          alt="Dynamic UPI QR"
                          className="w-36 h-36 object-contain"
                        />
                        <div className="text-[9px] font-mono text-center text-gray-800 font-bold mt-1">
                          SCAN VIA ANY UPI APP
                        </div>
                      </div>

                      <div className="space-y-2 text-xs flex-1">
                        <div className="text-[11px] text-slate-300">
                          VPA: <strong className="text-white font-mono">{paymentIntent.upi_pa}</strong>
                        </div>
                        <div className="text-[11px] text-slate-300">
                          Merchant: <strong className="text-white">{paymentIntent.upi_pn}</strong>
                        </div>

                        <a
                          href={paymentIntent.upi_uri}
                          className="mt-2 inline-flex items-center space-x-1.5 w-full justify-center bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-2 px-3 rounded-xl text-xs shadow transition-all"
                        >
                          <Smartphone className="w-3.5 h-3.5" />
                          <span>Pay via GPay / PhonePe / Paytm</span>
                        </a>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center justify-center py-6 text-xs text-slate-300">
                      <RefreshCw className="w-4 h-4 animate-spin mr-2" />
                      Generating Dynamic UPI QR...
                    </div>
                  )}

                  {/* 12-Digit Bank UTR Verification Input */}
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-white flex items-center justify-between">
                      <span>12-Digit Bank UTR / Transaction Reference</span>
                      <span className="text-[10px] text-emerald-400 font-mono">Demo: 202607159841</span>
                    </label>
                    <div className="flex space-x-2">
                      <input
                        type="text"
                        value={utrInput}
                        onChange={(e) => setUtrInput(e.target.value)}
                        placeholder="202607159841"
                        maxLength={12}
                        className="flex-1 bg-slate-900/90 border border-[rgba(235,229,217,0.12)] rounded-xl px-3 py-2 text-xs text-white font-mono focus:outline-none focus:border-emerald-500"
                      />
                      <button
                        onClick={handleVerifyUPI}
                        disabled={paymentStatus === "PROCESSING"}
                        className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-white font-medium px-4 py-2 rounded-xl text-xs cursor-pointer shadow transition-all"
                      >
                        {paymentStatus === "PROCESSING" ? "Verifying..." : "Verify UTR"}
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 2: Razorpay Developer Sandbox */}
              {paymentMethodTab === "razorpay" && (
                <div className="space-y-4">
                  <div className="bg-slate-900/90 p-4 rounded-2xl border border-slate-700 space-y-2.5 text-xs text-slate-300">
                    <div className="flex items-center justify-between text-white font-medium pb-1.5 border-b border-slate-700">
                      <span>Razorpay Developer Sandbox Mode</span>
                      <span className="text-[10px] font-mono bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded">
                        rzp_test_airtel_udyam
                      </span>
                    </div>
                    <p className="text-[11px] leading-relaxed">
                      Simulates Razorpay Standard Modal with cryptographic HMAC-SHA256 signature verification token. Zero business GSTIN or bank paperwork required.
                    </p>
                    <div className="bg-black/50 p-2.5 rounded-xl font-mono text-[10px] space-y-1 text-gray-300">
                      <div>Test Card: 4111 2222 3333 4444 (Visa)</div>
                      <div>Expiry: 12/28 · CVV: 123 · OTP: Any (123456)</div>
                    </div>
                  </div>

                  <button
                    onClick={handleVerifyRazorpaySandbox}
                    disabled={paymentStatus === "PROCESSING"}
                    className="w-full bg-[#e40000] hover:bg-[#b80000] disabled:opacity-40 text-white font-medium py-3 rounded-2xl text-xs sm:text-sm cursor-pointer shadow-[0_0_20px_rgba(228,0,0,0.3)] transition-all flex items-center justify-center space-x-2"
                  >
                    {paymentStatus === "PROCESSING" ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        <span>Verifying HMAC Signature...</span>
                      </>
                    ) : (
                      <>
                        <Lock className="w-4 h-4" />
                        <span>Simulate Razorpay Payment &amp; Verify Signature</span>
                      </>
                    )}
                  </button>
                </div>
              )}

              {/* Status Message */}
              {paymentMessage && (
                <div
                  className={`p-3 rounded-xl text-xs font-sans flex items-center space-x-2 ${
                    paymentStatus === "SUCCESS"
                      ? "bg-emerald-950/40 text-emerald-300 border border-emerald-500/30"
                      : "bg-red-950/40 text-red-300 border border-red-500/30"
                  }`}
                >
                  {paymentStatus === "SUCCESS" ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  ) : (
                    <Clock className="w-4 h-4 text-red-400 shrink-0" />
                  )}
                  <span>{paymentMessage}</span>
                </div>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};
