import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  CreditCard,
  QrCode,
  Smartphone,
  ShieldCheck,
  Check,
  CheckCircle2,
  Clock,
  ArrowRight,
  Lock,
  RefreshCw,
  X,
  Sparkles,
  KeyRound,
  Building2,
  AlertCircle,
  Eye,
  EyeOff,
  ChevronRight,
  IndianRupee,
  ShieldAlert,
} from "lucide-react";
import { ProvisioningOrder } from "../types";
import {
  createPaymentIntent,
  verifyUPIPayment,
  verifyRazorpayPayment,
  PaymentIntent,
} from "../api";

export interface PaymentSandboxModalProps {
  isOpen: boolean;
  onClose: () => void;
  order: ProvisioningOrder;
  onPaymentSuccess: (message: string) => void;
}

export const PaymentSandboxModal: React.FC<PaymentSandboxModalProps> = ({
  isOpen,
  onClose,
  order,
  onPaymentSuccess,
}) => {
  const [activeTab, setActiveTab] = useState<"upi" | "card">("upi");
  const [loadingIntent, setLoadingIntent] = useState<boolean>(true);
  const [paymentIntent, setPaymentIntent] = useState<PaymentIntent | null>(null);
  const [paymentStatus, setPaymentStatus] = useState<"IDLE" | "PROCESSING" | "SUCCESS" | "FAILED">("IDLE");
  const [statusMessage, setStatusMessage] = useState<string>("");

  // ==========================================
  // UPI SIMULATOR STATE
  // ==========================================
  const [selectedUpiApp, setSelectedUpiApp] = useState<"PhonePe" | "Google Pay" | "Paytm">("PhonePe");
  const [bankBalance, setBankBalance] = useState<number>(50000.0);
  const [upiStage, setUpiStage] = useState<"APP_VIEW" | "ENTER_PIN" | "SUCCESS">("APP_VIEW");
  const [upiPin, setUpiPin] = useState<string>("");
  const [manualUtr, setManualUtr] = useState<string>("202607159841");
  const [lastGeneratedUtr, setLastGeneratedUtr] = useState<string>("");

  // ==========================================
  // CARD TERMINAL & 3D-SECURE STATE
  // ==========================================
  const [cardNumber, setCardNumber] = useState<string>("4111 2222 3333 4444");
  const [cardHolder, setCardHolder] = useState<string>("Rajesh Kumar");
  const [cardExpiry, setCardExpiry] = useState<string>("12/28");
  const [cardCvv, setCardCvv] = useState<string>("842");
  const [showCvv, setShowCvv] = useState<boolean>(false);
  const [cardErrors, setCardErrors] = useState<{ number?: string; expiry?: string; cvv?: string }>({});

  // 3D-Secure Modal
  const [showOtpModal, setShowOtpModal] = useState<boolean>(false);
  const [otpValue, setOtpValue] = useState<string>("");
  const [otpTimer, setOtpTimer] = useState<number>(180);
  const [selectedBank, setSelectedBank] = useState<"SBI" | "HDFC">("HDFC");

  // Load Payment Intent on Open
  useEffect(() => {
    if (isOpen) {
      setLoadingIntent(true);
      setPaymentStatus("IDLE");
      setStatusMessage("");
      setUpiStage("APP_VIEW");
      setUpiPin("");
      setShowOtpModal(false);

      createPaymentIntent(order.order_id, order.monthly_charge_inr)
        .then((intent) => {
          setPaymentIntent(intent);
        })
        .catch((err: unknown) => {
          setStatusMessage(err instanceof Error ? err.message : "Failed to initialize payment gateway");
        })
        .finally(() => setLoadingIntent(false));
    }
  }, [isOpen, order.order_id, order.monthly_charge_inr]);

  // 3D-Secure Countdown Timer
  useEffect(() => {
    let interval: ReturnType<typeof setInterval> | null = null;
    if (showOtpModal && otpTimer > 0) {
      interval = setInterval(() => {
        setOtpTimer((prev) => (prev > 0 ? prev - 1 : 0));
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [showOtpModal, otpTimer]);

  if (!isOpen) return null;

  // Format Card Number (adds space every 4 digits)
  const handleCardNumberChange = (raw: string) => {
    const digitsOnly = raw.replace(/\D/g, "").slice(0, 16);
    const parts = digitsOnly.match(/.{1,4}/g) || [];
    setCardNumber(parts.join(" "));
  };

  // Format Expiry (MM/YY)
  const handleExpiryChange = (raw: string) => {
    const digits = raw.replace(/\D/g, "").slice(0, 4);
    if (digits.length >= 3) {
      setCardExpiry(`${digits.slice(0, 2)}/${digits.slice(2)}`);
    } else {
      setCardExpiry(digits);
    }
  };

  // Card Preset Selectors
  const applyCardPreset = (type: "VISA" | "MASTERCARD") => {
    if (type === "VISA") {
      setCardNumber("4111 2222 3333 4444");
      setCardHolder("Rajesh Kumar");
      setCardExpiry("12/28");
      setCardCvv("842");
      setSelectedBank("HDFC");
    } else {
      setCardNumber("5123 4567 8901 2345");
      setCardHolder("Priya Sharma");
      setCardExpiry("09/27");
      setCardCvv("314");
      setSelectedBank("SBI");
    }
    setCardErrors({});
  };

  // Trigger 3D-Secure Modal
  const handleProceedToOtp = () => {
    const errors: { number?: string; expiry?: string; cvv?: string } = {};
    const cleanNum = cardNumber.replace(/\s/g, "");
    if (cleanNum.length < 16) {
      errors.number = "Please enter a valid 16-digit card number";
    }
    if (!/^\d{2}\/\d{2}$/.test(cardExpiry)) {
      errors.expiry = "Use MM/YY format";
    }
    if (cardCvv.length < 3) {
      errors.cvv = "3 digits required";
    }

    if (Object.keys(errors).length > 0) {
      setCardErrors(errors);
      return;
    }

    setCardErrors({});
    setOtpValue("");
    setOtpTimer(180);
    setShowOtpModal(true);
  };

  // Submit 3D-Secure OTP
  const handleSubmitOtp = async () => {
    if (!paymentIntent) return;
    setPaymentStatus("PROCESSING");
    try {
      const rzpPaymentId = `pay_rzp_${Date.now()}`;
      const sigToken = `demo_sig_valid_rzp_${Date.now()}`;

      const res = await verifyRazorpayPayment(
        paymentIntent.payment_id,
        order.order_id,
        paymentIntent.razorpay_order_id,
        rzpPaymentId,
        sigToken
      );

      if (res.status === "SUCCESS") {
        setPaymentStatus("SUCCESS");
        setStatusMessage(res.message);
        setShowOtpModal(false);
        onPaymentSuccess(res.message);
      } else {
        setPaymentStatus("FAILED");
        setStatusMessage(res.message);
      }
    } catch (err: unknown) {
      setPaymentStatus("FAILED");
      setStatusMessage(err instanceof Error ? err.message : "Razorpay payment verification failed");
    }
  };

  // Smartphone Simulator: Submit PIN & Complete UPI Payment
  const handleConfirmUpiPin = async () => {
    if (!paymentIntent) return;
    if (upiPin.length !== 4) return;

    setPaymentStatus("PROCESSING");
    try {
      // 1. Generate 12-digit numeric bank UTR
      const generatedUtr = `2026${Math.floor(10000000 + Math.random() * 90000000)}`;
      setLastGeneratedUtr(generatedUtr);

      // 2. Execute verification against backend
      const res = await verifyUPIPayment(
        paymentIntent.payment_id,
        order.order_id,
        generatedUtr
      );

      if (res.status === "SUCCESS") {
        // 3. Deduct balance in simulated bank wallet
        setBankBalance((prev) => Math.max(0, prev - order.monthly_charge_inr));
        setUpiStage("SUCCESS");
        setPaymentStatus("SUCCESS");
        setStatusMessage(res.message);
        onPaymentSuccess(res.message);
      } else {
        setPaymentStatus("FAILED");
        setStatusMessage(res.message);
      }
    } catch (err: unknown) {
      setPaymentStatus("FAILED");
      setStatusMessage(err instanceof Error ? err.message : "UPI payment verification failed");
    }
  };

  // Manual UTR Verification
  const handleManualUtrVerify = async () => {
    if (!paymentIntent) return;
    setPaymentStatus("PROCESSING");
    try {
      const res = await verifyUPIPayment(
        paymentIntent.payment_id,
        order.order_id,
        manualUtr
      );
      if (res.status === "SUCCESS") {
        setPaymentStatus("SUCCESS");
        setStatusMessage(res.message);
        onPaymentSuccess(res.message);
      } else {
        setPaymentStatus("FAILED");
        setStatusMessage(res.message);
      }
    } catch (err: unknown) {
      setPaymentStatus("FAILED");
      setStatusMessage(err instanceof Error ? err.message : "Manual UTR verification failed");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 overflow-y-auto">
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="fixed inset-0 bg-black/85 backdrop-blur-md"
      />

      {/* Main Dialog */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 15 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 15 }}
        transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
        className="relative w-full max-w-4xl bg-[#090b0e] border border-[rgba(235,229,217,0.12)] rounded-3xl p-5 sm:p-7 shadow-[0_25px_60px_rgba(0,0,0,0.85)] z-10 space-y-6 overflow-hidden my-auto"
      >
        {/* Header */}
        <div className="flex items-start justify-between gap-4 pb-4 border-b border-[rgba(235,229,217,0.08)]">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-mono tracking-wider bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 font-semibold uppercase">
                <ShieldCheck className="w-3 h-3 text-emerald-400" />
                <span>NPCI UPI 2.0 &amp; Razorpay Developer Sandbox</span>
              </span>
              <span className="text-xs text-[#B39D82] font-mono">ORDER #{order.order_id}</span>
            </div>
            <h2 className="font-serif text-xl sm:text-2xl font-normal text-[#EBE5D9]">
              Telecom Payment Gateway — <span className="text-[#d9ad63]">{order.business_name}</span>
            </h2>
            <p className="text-xs text-[#B39D82]">
              Simulate enterprise pre-provisioning payments with full 3D-Secure card authorization or mobile bank wallet balance deduction.
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-[#B39D82] hover:text-[#EBE5D9] hover:bg-white/5 rounded-xl transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Amount Ribbon & Mode Switcher */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-[#030405] p-3 rounded-2xl border border-[rgba(235,229,217,0.08)]">
          <div className="flex items-center space-x-3 text-xs font-mono">
            <span className="text-[#B39D82]">Total Amount Due:</span>
            <span className="text-base font-bold text-white flex items-center text-[#d9ad63]">
              ₹{order.monthly_charge_inr.toLocaleString()}
            </span>
            <span className="text-[10px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
              Advance 1st Month + ₹0 OTC
            </span>
          </div>

          <div className="flex space-x-1.5 bg-[#090b0e] p-1 rounded-xl border border-[rgba(235,229,217,0.08)]">
            <button
              onClick={() => setActiveTab("upi")}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                activeTab === "upi"
                  ? "bg-[#e40000] text-white shadow-sm"
                  : "text-[#B39D82] hover:text-[#EBE5D9]"
              }`}
            >
              <Smartphone className="w-3.5 h-3.5" />
              <span>📱 Smartphone UPI Simulator</span>
            </button>
            <button
              onClick={() => setActiveTab("card")}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                activeTab === "card"
                  ? "bg-[#e40000] text-white shadow-sm"
                  : "text-[#B39D82] hover:text-[#EBE5D9]"
              }`}
            >
              <CreditCard className="w-3.5 h-3.5" />
              <span>💳 Card Terminal &amp; 3D-Secure</span>
            </button>
          </div>
        </div>

        {/* TAB 1: INTERACTIVE SMARTPHONE UPI SIMULATOR */}
        {activeTab === "upi" && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
            {/* Left: Dynamic QR & Manual UTR Check (5 cols) */}
            <div className="lg:col-span-5 bg-[#030405] p-5 rounded-2xl border border-[rgba(235,229,217,0.08)] space-y-4">
              <div className="text-center space-y-2">
                <span className="text-[10px] font-mono uppercase tracking-wider text-[#B39D82] block">
                  NPCI Dynamic UPI QR
                </span>
                {paymentIntent ? (
                  <div className="bg-white p-3 rounded-2xl inline-block shadow-lg border-2 border-[#d9ad63]">
                    <img
                      src={paymentIntent.qr_data_url}
                      alt="Dynamic UPI QR"
                      className="w-36 h-36 mx-auto object-contain"
                    />
                    <div className="text-[9px] font-mono text-center text-gray-900 font-bold mt-1">
                      SCAN VIA ANY BANK APP
                    </div>
                  </div>
                ) : (
                  <div className="h-36 flex items-center justify-center text-xs text-[#B39D82]">
                    <RefreshCw className="w-5 h-5 animate-spin mr-2" />
                    Generating QR...
                  </div>
                )}
              </div>

              <div className="text-[11px] font-mono space-y-1 bg-[#090b0e] p-3 rounded-xl border border-[rgba(235,229,217,0.08)]">
                <div className="text-[#B39D82]">
                  VPA: <span className="text-white">{paymentIntent?.upi_pa || "airtel.enterprise@icici"}</span>
                </div>
                <div className="text-[#B39D82]">
                  Payee: <span className="text-white">{paymentIntent?.upi_pn || "Bharti Airtel Limited"}</span>
                </div>
              </div>

              {/* Manual Bank UTR Option */}
              <div className="space-y-2 pt-2 border-t border-[rgba(235,229,217,0.08)]">
                <label className="text-xs text-white font-medium flex items-center justify-between">
                  <span>Manual 12-Digit Bank UTR</span>
                  <button
                    onClick={() => setManualUtr("202607159841")}
                    className="text-[10px] text-emerald-400 font-mono hover:underline cursor-pointer"
                  >
                    Demo: 202607159841
                  </button>
                </label>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={manualUtr}
                    onChange={(e) => setManualUtr(e.target.value)}
                    maxLength={12}
                    className="flex-1 bg-[#090b0e] border border-[rgba(235,229,217,0.12)] rounded-xl px-3 py-2 text-xs text-white font-mono focus:outline-none focus:border-emerald-500"
                  />
                  <button
                    onClick={handleManualUtrVerify}
                    disabled={paymentStatus === "PROCESSING"}
                    className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-white font-medium px-3.5 py-2 rounded-xl text-xs cursor-pointer transition-colors"
                  >
                    Verify
                  </button>
                </div>
              </div>
            </div>

            {/* Right: Interactive Smartphone Simulator Frame (7 cols) */}
            <div className="lg:col-span-7 bg-gradient-to-b from-[#141822] to-[#0c0f16] p-4 sm:p-5 rounded-3xl border-2 border-slate-700 shadow-2xl relative">
              {/* Phone Speaker & Camera Notch */}
              <div className="flex items-center justify-between pb-3 px-2 border-b border-white/10 text-[10px] text-slate-400 font-mono">
                <span className="font-semibold text-white">9:41 AM</span>
                <div className="w-16 h-3.5 bg-black/60 rounded-full mx-auto" />
                <span className="text-emerald-400 font-bold">5G · 100%</span>
              </div>

              <div className="pt-3 space-y-4">
                {/* App Selector Pills */}
                <div className="flex items-center justify-between bg-black/40 p-1.5 rounded-2xl border border-white/5">
                  {(["PhonePe", "Google Pay", "Paytm"] as const).map((app) => (
                    <button
                      key={app}
                      onClick={() => {
                        setSelectedUpiApp(app);
                        setUpiStage("APP_VIEW");
                      }}
                      className={`flex-1 py-1.5 rounded-xl text-[11px] font-semibold transition-all cursor-pointer ${
                        selectedUpiApp === app
                          ? app === "PhonePe"
                            ? "bg-[#5f259f] text-white shadow-md"
                            : app === "Google Pay"
                            ? "bg-[#1a73e8] text-white shadow-md"
                            : "bg-[#00b9f5] text-gray-900 shadow-md"
                          : "text-slate-400 hover:text-white"
                      }`}
                    >
                      {app}
                    </button>
                  ))}
                </div>

                {/* Simulated Bank Balance Card */}
                <div className="bg-black/60 p-3.5 rounded-2xl border border-white/10 flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-9 h-9 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
                      <Building2 className="w-4 h-4" />
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-mono">
                        Primary Linked Account
                      </span>
                      <span className="text-xs font-semibold text-white">
                        HDFC Bank · A/C **4921
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-mono">
                      Simulated Balance
                    </span>
                    <span className="text-sm font-bold font-mono text-emerald-400">
                      ₹{bankBalance.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                </div>

                {/* Smartphone Flow Views */}
                {upiStage === "APP_VIEW" && (
                  <motion.div
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-[#090b0e] p-4 rounded-2xl border border-white/10 space-y-4"
                  >
                    <div className="flex items-center justify-between pb-3 border-b border-white/5">
                      <div>
                        <span className="text-[10px] text-slate-400 font-mono">Transfer To</span>
                        <h4 className="text-sm font-semibold text-white">Bharti Airtel Limited</h4>
                        <span className="text-[10px] text-emerald-400 font-mono">airtel.enterprise@icici · Verified Merchant</span>
                      </div>
                      <span className="text-lg font-bold font-mono text-white">
                        ₹{order.monthly_charge_inr.toLocaleString()}
                      </span>
                    </div>

                    <button
                      onClick={() => setUpiStage("ENTER_PIN")}
                      className={`w-full py-3 rounded-2xl text-xs font-bold uppercase tracking-wider transition-all shadow-lg flex items-center justify-center space-x-2 cursor-pointer ${
                        selectedUpiApp === "PhonePe"
                          ? "bg-[#5f259f] hover:bg-[#4d1d82] text-white"
                          : selectedUpiApp === "Google Pay"
                          ? "bg-[#1a73e8] hover:bg-[#1557b0] text-white"
                          : "bg-[#00b9f5] hover:bg-[#009fd4] text-gray-900"
                      }`}
                    >
                      <span>Pay ₹{order.monthly_charge_inr.toLocaleString()} via {selectedUpiApp}</span>
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  </motion.div>
                )}

                {upiStage === "ENTER_PIN" && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="bg-[#090b0e] p-4 rounded-2xl border border-purple-500/30 space-y-4"
                  >
                    <div className="text-center space-y-1">
                      <div className="w-8 h-8 rounded-full bg-purple-500/20 text-purple-400 mx-auto flex items-center justify-center">
                        <KeyRound className="w-4 h-4" />
                      </div>
                      <h4 className="text-xs font-semibold text-white uppercase tracking-wider">
                        Enter 4-Digit UPI PIN
                      </h4>
                      <p className="text-[11px] text-slate-400">
                        Authorizing ₹{order.monthly_charge_inr.toLocaleString()} from HDFC Bank **4921
                      </p>
                    </div>

                    {/* PIN Helper Chip */}
                    <div className="text-center">
                      <button
                        onClick={() => setUpiPin("8492")}
                        className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-[10px] font-mono bg-purple-500/20 text-purple-300 border border-purple-500/40 hover:bg-purple-500/30 transition-colors cursor-pointer"
                      >
                        <Sparkles className="w-3 h-3 text-purple-400" />
                        <span>Click to auto-fill Test PIN: <strong>8492</strong></span>
                      </button>
                    </div>

                    {/* PIN Input */}
                    <div className="flex justify-center space-x-3">
                      <input
                        type="password"
                        maxLength={4}
                        value={upiPin}
                        onChange={(e) => setUpiPin(e.target.value.replace(/\D/g, ""))}
                        placeholder="••••"
                        className="w-36 text-center tracking-[1em] text-lg font-bold bg-black/60 border-2 border-purple-500/50 rounded-xl px-3 py-2 text-white font-mono focus:outline-none focus:border-purple-400"
                      />
                    </div>

                    <div className="flex space-x-2 pt-2">
                      <button
                        onClick={() => setUpiStage("APP_VIEW")}
                        className="flex-1 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-xs text-slate-300 cursor-pointer"
                      >
                        Back
                      </button>
                      <button
                        onClick={handleConfirmUpiPin}
                        disabled={upiPin.length !== 4 || paymentStatus === "PROCESSING"}
                        className="flex-2 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 disabled:opacity-40 text-white font-bold text-xs uppercase tracking-wider shadow-lg flex items-center justify-center space-x-2 cursor-pointer transition-all"
                      >
                        {paymentStatus === "PROCESSING" ? (
                          <>
                            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                            <span>Authorizing NPCI...</span>
                          </>
                        ) : (
                          <>
                            <Check className="w-3.5 h-3.5" />
                            <span>Confirm &amp; Debit Bank</span>
                          </>
                        )}
                      </button>
                    </div>
                  </motion.div>
                )}

                {upiStage === "SUCCESS" && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="bg-emerald-950/40 border border-emerald-500/40 p-4 rounded-2xl text-center space-y-3"
                  >
                    <div className="w-10 h-10 rounded-full bg-emerald-500/20 text-emerald-400 mx-auto flex items-center justify-center">
                      <CheckCircle2 className="w-6 h-6" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-white">Payment Authorized!</h4>
                      <p className="text-xs text-emerald-300 mt-0.5">
                        ₹{order.monthly_charge_inr.toLocaleString()} debited from HDFC Bank **4921
                      </p>
                    </div>
                    <div className="bg-black/40 p-2.5 rounded-xl text-[10px] font-mono text-slate-300 space-y-1">
                      <div>Bank Ref (UTR): <strong className="text-emerald-400">{lastGeneratedUtr}</strong></div>
                      <div>Updated Account Balance: <strong className="text-white">₹{bankBalance.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</strong></div>
                    </div>
                  </motion.div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: RAZORPAY CARD TERMINAL & 3D-SECURE */}
        {activeTab === "card" && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
            {/* Left: Interactive Card Graphic & Presets (5 cols) */}
            <div className="lg:col-span-5 space-y-4">
              {/* Luxury CSS Credit Card */}
              <div className="relative h-48 rounded-2xl bg-gradient-to-tr from-slate-950 via-slate-900 to-indigo-950 p-5 border border-indigo-500/30 shadow-[0_15px_35px_rgba(0,0,0,0.7)] flex flex-col justify-between overflow-hidden">
                {/* Background watermarks */}
                <div className="absolute -right-8 -top-8 w-32 h-32 rounded-full bg-indigo-500/10 blur-xl pointer-events-none" />
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-1.5">
                    <div className="w-8 h-6 bg-gradient-to-r from-amber-400 to-amber-200 rounded-md border border-amber-300 shadow-inner flex items-center justify-center">
                      <div className="w-4 h-3 border border-amber-800/40 rounded-sm" />
                    </div>
                    <span className="text-[10px] font-mono text-slate-400 uppercase tracking-widest">
                      Corporate
                    </span>
                  </div>
                  <span className="text-sm font-bold font-mono tracking-widest text-white">
                    {cardNumber.startsWith("4") ? "VISA" : "Mastercard"}
                  </span>
                </div>

                <div className="font-mono text-lg tracking-[0.2em] text-white font-bold drop-shadow-md">
                  {cardNumber || "•••• •••• •••• ••••"}
                </div>

                <div className="flex items-end justify-between text-xs font-mono">
                  <div>
                    <span className="text-[9px] text-slate-400 uppercase block">Cardholder</span>
                    <span className="text-white font-medium uppercase tracking-wider">
                      {cardHolder || "CORPORATE CLIENT"}
                    </span>
                  </div>
                  <div>
                    <span className="text-[9px] text-slate-400 uppercase block">Expires</span>
                    <span className="text-white font-medium">{cardExpiry || "MM/YY"}</span>
                  </div>
                </div>
              </div>

              {/* Test Card Presets */}
              <div className="bg-[#030405] p-3 rounded-2xl border border-[rgba(235,229,217,0.08)] space-y-2">
                <span className="text-[10px] font-mono uppercase tracking-wider text-[#B39D82] block">
                  Clickable Test Card Presets
                </span>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => applyCardPreset("VISA")}
                    className="p-2.5 rounded-xl bg-[#090b0e] hover:bg-white/5 border border-white/10 text-left transition-colors cursor-pointer"
                  >
                    <span className="text-xs font-bold text-white block">Visa Business</span>
                    <span className="text-[10px] font-mono text-[#d9ad63] block">4111 2222 •••• 4444</span>
                    <span className="text-[9px] text-slate-400 block">Exp: 12/28 · HDFC Bank</span>
                  </button>
                  <button
                    onClick={() => applyCardPreset("MASTERCARD")}
                    className="p-2.5 rounded-xl bg-[#090b0e] hover:bg-white/5 border border-white/10 text-left transition-colors cursor-pointer"
                  >
                    <span className="text-xs font-bold text-white block">Mastercard Corp</span>
                    <span className="text-[10px] font-mono text-amber-400 block">5123 4567 •••• 2345</span>
                    <span className="text-[9px] text-slate-400 block">Exp: 09/27 · SBI Bank</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Right: Card Input Form (7 cols) */}
            <div className="lg:col-span-7 bg-[#030405] p-5 rounded-2xl border border-[rgba(235,229,217,0.08)] space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-[rgba(235,229,217,0.08)]">
                <h3 className="text-sm font-semibold text-white flex items-center space-x-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <span>Razorpay Terminal Payment Form</span>
                </h3>
                <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/30">
                  3D-Secure 2.0 Ready
                </span>
              </div>

              {/* Card Number Input */}
              <div className="space-y-1">
                <label className="text-xs text-white font-medium flex justify-between">
                  <span>Card Number (16-Digit)</span>
                  {cardErrors.number && <span className="text-[10px] text-red-400">{cardErrors.number}</span>}
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={cardNumber}
                    onChange={(e) => handleCardNumberChange(e.target.value)}
                    placeholder="4111 2222 3333 4444"
                    maxLength={19}
                    className="w-full bg-[#090b0e] border border-[rgba(235,229,217,0.12)] rounded-xl px-3.5 py-2.5 text-xs text-white font-mono focus:outline-none focus:border-indigo-500"
                  />
                  <div className="absolute right-3 top-2.5 text-[10px] font-mono text-slate-400">
                    {cardNumber.startsWith("4") ? "VISA" : "MC"}
                  </div>
                </div>
              </div>

              {/* Cardholder Name */}
              <div className="space-y-1">
                <label className="text-xs text-white font-medium">Cardholder Name</label>
                <input
                  type="text"
                  value={cardHolder}
                  onChange={(e) => setCardHolder(e.target.value)}
                  placeholder="Rajesh Kumar"
                  className="w-full bg-[#090b0e] border border-[rgba(235,229,217,0.12)] rounded-xl px-3.5 py-2.5 text-xs text-white font-sans focus:outline-none focus:border-indigo-500"
                />
              </div>

              {/* Expiry & CVV */}
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-xs text-white font-medium flex justify-between">
                    <span>Expiry (MM/YY)</span>
                    {cardErrors.expiry && <span className="text-[10px] text-red-400">{cardErrors.expiry}</span>}
                  </label>
                  <input
                    type="text"
                    value={cardExpiry}
                    onChange={(e) => handleExpiryChange(e.target.value)}
                    placeholder="12/28"
                    maxLength={5}
                    className="w-full bg-[#090b0e] border border-[rgba(235,229,217,0.12)] rounded-xl px-3.5 py-2.5 text-xs text-white font-mono focus:outline-none focus:border-indigo-500"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-xs text-white font-medium flex justify-between">
                    <span>CVV</span>
                    {cardErrors.cvv && <span className="text-[10px] text-red-400">{cardErrors.cvv}</span>}
                  </label>
                  <div className="relative">
                    <input
                      type={showCvv ? "text" : "password"}
                      value={cardCvv}
                      onChange={(e) => setCardCvv(e.target.value.replace(/\D/g, "").slice(0, 3))}
                      placeholder="•••"
                      maxLength={3}
                      className="w-full bg-[#090b0e] border border-[rgba(235,229,217,0.12)] rounded-xl px-3.5 py-2.5 text-xs text-white font-mono focus:outline-none focus:border-indigo-500"
                    />
                    <button
                      type="button"
                      onClick={() => setShowCvv(!showCvv)}
                      className="absolute right-3 top-2.5 text-slate-400 hover:text-white cursor-pointer"
                    >
                      {showCvv ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                </div>
              </div>

              {/* Submit to 3D-Secure */}
              <button
                type="button"
                onClick={handleProceedToOtp}
                className="w-full mt-2 py-3 bg-[#e40000] hover:bg-[#b30000] text-white font-semibold text-xs rounded-xl flex items-center justify-center space-x-2 transition-all shadow-[0_0_20px_rgba(228,0,0,0.3)] cursor-pointer"
              >
                <Lock className="w-4 h-4" />
                <span>Proceed to 3D-Secure Bank Verification (₹{order.monthly_charge_inr.toLocaleString()})</span>
              </button>
            </div>
          </div>
        )}

        {/* Global Status Message */}
        {statusMessage && (
          <div
            className={`p-3.5 rounded-xl text-xs flex items-center space-x-2 ${
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
            <span>{statusMessage}</span>
          </div>
        )}
      </motion.div>

      {/* ========================================================= */}
      {/* 3D-SECURE BANK AUTHENTICATION MODAL (SBI / HDFC BRANDED) */}
      {/* ========================================================= */}
      <AnimatePresence>
        {showOtpModal && (
          <div className="fixed inset-0 z-60 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/85 backdrop-blur-md"
              onClick={() => setShowOtpModal(false)}
            />

            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="relative w-full max-w-md bg-white text-gray-900 rounded-3xl p-6 shadow-2xl z-20 space-y-5"
            >
              {/* Bank Header */}
              <div className="flex items-center justify-between pb-3 border-b border-gray-200">
                <div className="flex items-center space-x-2">
                  <div
                    className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-white text-xs ${
                      selectedBank === "HDFC" ? "bg-[#004c8f]" : "bg-[#280071]"
                    }`}
                  >
                    {selectedBank}
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-gray-900 leading-tight">
                      {selectedBank === "HDFC" ? "HDFC Bank SafePay" : "State Bank of India 3D-Secure"}
                    </h4>
                    <span className="text-[10px] text-gray-500 font-mono">
                      Verified by Visa · Mastercard ID Check
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => setShowOtpModal(false)}
                  className="p-1.5 text-gray-400 hover:text-gray-700 rounded-lg hover:bg-gray-100 cursor-pointer"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Transaction Metadata Table */}
              <div className="bg-gray-50 p-3.5 rounded-2xl border border-gray-200 text-xs space-y-1.5 font-mono">
                <div className="flex justify-between text-gray-600">
                  <span>Merchant:</span>
                  <strong className="text-gray-900">Bharti Airtel Limited</strong>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Amount:</span>
                  <strong className="text-gray-900">₹{order.monthly_charge_inr.toLocaleString()}</strong>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Card Number:</span>
                  <strong className="text-gray-900">XXXX XXXX XXXX {cardNumber.replace(/\s/g, "").slice(-4)}</strong>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Registered Mobile:</span>
                  <strong className="text-gray-900">+91 98••••••10</strong>
                </div>
              </div>

              {/* OTP Prompt */}
              <div className="space-y-3">
                <div className="text-center space-y-1">
                  <span className="text-xs font-semibold text-gray-800">
                    Enter the 6-digit OTP sent to your registered mobile number
                  </span>
                  <div className="flex items-center justify-center space-x-2 text-[11px] text-gray-500">
                    <Clock className="w-3.5 h-3.5 text-red-500" />
                    <span>Time remaining: <strong>{Math.floor(otpTimer / 60)}:{String(otpTimer % 60).padStart(2, "0")}</strong></span>
                  </div>
                </div>

                {/* Clickable Test OTP Chip */}
                <div className="text-center">
                  <button
                    type="button"
                    onClick={() => setOtpValue("123456")}
                    className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-[11px] font-mono bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 transition-colors cursor-pointer"
                  >
                    <Sparkles className="w-3 h-3 text-blue-600" />
                    <span>Click to auto-fill Test OTP: <strong>123456</strong></span>
                  </button>
                </div>

                {/* OTP Input */}
                <div className="flex justify-center">
                  <input
                    type="text"
                    maxLength={6}
                    value={otpValue}
                    onChange={(e) => setOtpValue(e.target.value.replace(/\D/g, ""))}
                    placeholder="123456"
                    className="w-48 text-center tracking-[0.5em] text-xl font-bold bg-white border-2 border-gray-300 rounded-xl px-3 py-2 text-gray-900 font-mono focus:outline-none focus:border-blue-600 shadow-inner"
                  />
                </div>
              </div>

              {/* Action Buttons */}
              <div className="space-y-2 pt-2">
                <button
                  type="button"
                  onClick={handleSubmitOtp}
                  disabled={otpValue.length !== 6 || paymentStatus === "PROCESSING"}
                  className="w-full py-3 bg-[#e40000] hover:bg-[#b30000] disabled:opacity-40 text-white font-bold text-xs uppercase tracking-wider rounded-xl shadow-lg flex items-center justify-center space-x-2 cursor-pointer transition-all"
                >
                  {paymentStatus === "PROCESSING" ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>Authenticating with Bank...</span>
                    </>
                  ) : (
                    <>
                      <ShieldCheck className="w-4 h-4" />
                      <span>Submit OTP &amp; Authorize Payment</span>
                    </>
                  )}
                </button>

                <div className="flex items-center justify-between text-[11px] text-gray-500 px-1">
                  <button
                    type="button"
                    onClick={() => setOtpTimer(180)}
                    className="hover:underline text-blue-600 cursor-pointer"
                  >
                    Resend OTP
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowOtpModal(false)}
                    className="hover:underline text-gray-600 cursor-pointer"
                  >
                    Cancel Transaction
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};