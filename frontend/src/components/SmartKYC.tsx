import React, { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  Shield,
  ShieldCheck,
  ShieldAlert,
  FileText,
  Lock,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  ArrowRight,
  Upload,
  FileUp,
  Sparkles,
  Zap,
  Check,
  Info,
  Building,
  CreditCard,
  FileCheck,
  Smartphone,
  KeyRound,
} from "lucide-react";
import { KYCVerificationResult, CommercialBreakdown } from "../types";
import { verifyKYC, uploadKYCDocument, verifyDigiLocker, KYCUploadResponse } from "../api";
import { validateVerhoeff, redactAadhaarInPlace, decodeGSTIN } from "../utils/verhoeff";

interface SmartKYCProps {
  quote: CommercialBreakdown | null;
  onKYCApproved: (result: KYCVerificationResult) => void;
  onSwitchToUdyamExempt?: () => void;
}

export const SmartKYC: React.FC<SmartKYCProps> = ({ quote, onKYCApproved, onSwitchToUdyamExempt }) => {
  const [consentGranted, setConsentGranted] = useState<boolean>(true);
  const [selectedPreset, setSelectedPreset] = useState<string>("K03");
  const [isVerifying, setIsVerifying] = useState<boolean>(false);
  const [kycResult, setKycResult] = useState<KYCVerificationResult | null>(null);
  const [showConsentModal, setShowConsentModal] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<"preset" | "upload" | "digilocker">("preset");
  const [uploadDocType, setUploadDocType] = useState<string>("gst_certificate");
  const [uploadResponse, setUploadResponse] = useState<KYCUploadResponse | null>(null);
  const [uploadedSlots, setUploadedSlots] = useState<Record<string, { file: File; res: KYCUploadResponse }>>({});
  const [remediationNotice, setRemediationNotice] = useState<string | null>(null);

  // DigiLocker Fast-Track State
  const [digiAadhaar, setDigiAadhaar] = useState<string>("2345 6789 0124");
  const [digiOtp, setDigiOtp] = useState<string>("1234");
  const [digiGstin, setDigiGstin] = useState<string>("32TTNXB7384T1ZW");
  const [digiUdyam, setDigiUdyam] = useState<string>("UDYAM-KL-00-1234567");

  // Live Verhoeff & GSTIN decoding (Issue #27)
  const cleanAadhaar = digiAadhaar.replace(/\D/g, "");
  const isAadhaarValidVerhoeff = cleanAadhaar.length === 12 && validateVerhoeff(cleanAadhaar);
  const aadhaarRedactionPreview = redactAadhaarInPlace(digiAadhaar);
  const gstinDecoded = decodeGSTIN(digiGstin);

  const handleDigiLockerVerify = async () => {
    if (!consentGranted) {
      alert("DPDP Act 2023 requires explicit digital consent before DigiLocker verification.");
      return;
    }
    setIsVerifying(true);
    try {
      const cartRequiresGstin = quote ? !quote.gst_exempt_eligible : false;
      const res = await verifyDigiLocker({
        aadhaarNumber: digiAadhaar,
        otp: digiOtp,
        declaredGstin: digiGstin,
        declaredUdyam: digiUdyam,
        applicantId: "DIGI_MERCHANT",
        cartRequiresGstin: cartRequiresGstin,
      });
      setKycResult(res);
      if (res.status === "APPROVED") {
        onKYCApproved(res);
      }
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "DigiLocker verification failed.");
    } finally {
      setIsVerifying(false);
    }
  };

  const handleFileUpload = async (file: File, docTypeOverride?: string) => {
    if (!consentGranted) {
      alert("DPDP Act 2023 requires explicit digital consent before document processing.");
      return;
    }
    const targetType = docTypeOverride || uploadDocType;
    setIsVerifying(true);
    try {
      const cartRequiresGstin = quote ? !quote.gst_exempt_eligible : true;
      const res = await uploadKYCDocument(file, targetType, cartRequiresGstin);
      setUploadResponse(res);
      setUploadedSlots((prev) => ({
        ...prev,
        [targetType]: { file, res },
      }));
      setKycResult(res.single_doc_result || res.verification_result);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "File OCR failed.");
    } finally {
      setIsVerifying(false);
    }
  };

  const handleVerifyCompletePackage = () => {
    if (Object.keys(uploadedSlots).length === 0) {
      alert("Please upload at least one document first.");
      return;
    }
    if (uploadResponse?.verification_result) {
      setKycResult(uploadResponse.verification_result);
    }
  };

  const handleSwitchToUdyam = async () => {
    if (onSwitchToUdyamExempt) {
      onSwitchToUdyamExempt();
    }
    setSelectedPreset("KIRANA_NON_GST");
    setRemediationNotice("Switched to Udyam Micro Bundle (GST-Free). All GST-only SKUs removed.");
    try {
      const res = await verifyKYC("KIRANA_NON_GST", false);
      setKycResult(res);
    } catch {
      // fallback
    }
  };

  const presets = [
    {
      id: "K03",
      label: "Applicant K03 (Clean)",
      type: "CLEAN",
      desc: "Valid GST + Udyam + Utility Bill. 100% RapidFuzz score.",
    },
    {
      id: "K01",
      label: "Applicant K01 (Cancelled GSTIN)",
      type: "ANOMALY",
      desc: "GSTIN cancelled on 2026-06-01 + Blank Udyam certificate.",
    },
    {
      id: "K05",
      label: "Applicant K05 (Missing Udyam)",
      type: "ANOMALY",
      desc: "Udyam physical certificate missing from package.",
    },
    {
      id: "K07",
      label: "Applicant K07 (Name Mismatch)",
      type: "ANOMALY",
      desc: "Legal trade name differs from invoice (<70% similarity).",
    },
    {
      id: "K11",
      label: "Applicant K11 (Stale Utility Bill)",
      type: "ANOMALY",
      desc: "Bill dated 2025-10-31 is 257 days old (>90-day statutory limit).",
    },
    {
      id: "KIRANA_NON_GST",
      label: "Kirana Store (Non-GST)",
      type: "EXEMPT",
      desc: "Valid Udyam + Bill, bypassing GSTIN requirement.",
    },
  ];

  const handleVerify = async () => {
    if (!consentGranted) {
      alert("DPDP Act 2023 requires consent.");
      return;
    }
    setIsVerifying(true);
    try {
      const cartRequiresGstin = quote ? !quote.gst_exempt_eligible : true;
      const res = await verifyKYC(selectedPreset, cartRequiresGstin);
      setKycResult(res);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "KYC failed.");
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-7">
      {/* Editorial Header */}
      <div className="luxury-glass rounded-3xl p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-5 border border-[rgba(235,229,217,0.08)] shadow-[0_20px_50px_rgba(0,0,0,0.7)]">
        <div className="flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-2xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shrink-0">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h2 className="font-serif text-xl sm:text-2xl font-normal text-[#EBE5D9]">
              Smart KYC &amp; DPDP Anomaly Gate
            </h2>
            <p className="text-xs text-[#B39D82] mt-0.5">
              In-memory 12-digit UID masking · RapidFuzz cross-checks under 200ms
            </p>
          </div>
        </div>

        {/* DPDP Consent Switch */}
        <div className="flex items-center space-x-3 bg-[#030405] px-4 py-2.5 rounded-2xl border border-[rgba(235,229,217,0.08)] text-xs text-[#B39D82] shrink-0">
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              id="dpdp-consent"
              checked={consentGranted}
              onChange={(e) => setConsentGranted(e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-8 h-4 bg-gray-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-[#EBE5D9] after:border-gray-300 after:border after:rounded-full after:h-3 after:w-3 after:transition-all peer-checked:bg-[#e40000]"></div>
          </label>
          <label htmlFor="dpdp-consent" className="cursor-pointer font-medium text-[#EBE5D9]">
            DPDP 2023 Consent
          </label>
          <button
            onClick={() => setShowConsentModal(true)}
            className="text-[10px] text-[#d9ad63] hover:underline font-mono"
          >
            [Audit]
          </button>
        </div>
      </div>

      {remediationNotice && (
        <motion.div
          initial={{ opacity: 0, y: -6 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 rounded-2xl bg-emerald-950/30 border border-emerald-500/30 text-emerald-300 text-xs flex items-center space-x-2.5"
        >
          <Sparkles className="w-4 h-4 text-emerald-400 shrink-0" />
          <span className="font-sans">{remediationNotice}</span>
        </motion.div>
      )}

      {/* Mode Switcher */}
      <div className="flex flex-wrap gap-2 border-b border-[rgba(235,229,217,0.06)] pb-3">
        <button
          onClick={() => {
            setActiveTab("preset");
            setUploadResponse(null);
          }}
          className={`px-4 py-2 rounded-full text-xs font-medium transition-all cursor-pointer ${
            activeTab === "preset"
              ? "bg-[#e40000] text-white shadow-[0_0_16px_rgba(228,0,0,0.4)]"
              : "text-[#B39D82] hover:text-[#EBE5D9] hover:bg-white/[0.03]"
          }`}
        >
          Preset Specimens (K01–K12)
        </button>
        <button
          onClick={() => {
            setActiveTab("upload");
            setKycResult(null);
          }}
          className={`px-4 py-2 rounded-full text-xs font-medium transition-all cursor-pointer ${
            activeTab === "upload"
              ? "bg-[#e40000] text-white shadow-[0_0_16px_rgba(228,0,0,0.4)]"
              : "text-[#B39D82] hover:text-[#EBE5D9] hover:bg-white/[0.03]"
          }`}
        >
          Live Document Staging (4 Slots)
        </button>
        <button
          onClick={() => {
            setActiveTab("digilocker");
            setKycResult(null);
            setUploadResponse(null);
          }}
          className={`px-4 py-2 rounded-full text-xs font-medium transition-all cursor-pointer flex items-center space-x-1.5 ${
            activeTab === "digilocker"
              ? "bg-[#e40000] text-white shadow-[0_0_16px_rgba(228,0,0,0.4)]"
              : "text-[#d9ad63] hover:text-[#EBE5D9] hover:bg-white/[0.03] border border-[#d9ad63]/30"
          }`}
        >
          <Zap className="w-3.5 h-3.5 text-[#d9ad63]" />
          <span>⚡ DigiLocker Fast-Track (10s)</span>
        </button>
      </div>

      {activeTab === "preset" ? (
        /* Presets Grid */
        <div className="luxury-glass rounded-3xl p-6 sm:p-7 space-y-5 border border-[rgba(235,229,217,0.08)] shadow-[0_20px_50px_rgba(0,0,0,0.7)]">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3.5">
            {presets.map((preset) => {
              const isSelected = selectedPreset === preset.id;
              return (
                <motion.div
                  key={preset.id}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => {
                    setSelectedPreset(preset.id);
                    setKycResult(null);
                  }}
                  className={`p-4 rounded-2xl border transition-all cursor-pointer ${
                    isSelected
                      ? "border-[#e40000] bg-gradient-to-b from-[#e40000]/15 to-transparent shadow-[0_0_20px_rgba(228,0,0,0.25)]"
                      : "border-[rgba(235,229,217,0.06)] bg-[#030405] hover:border-[rgba(235,229,217,0.16)]"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold text-[#EBE5D9]">{preset.label}</span>
                    <span
                      className={`text-[9px] px-2 py-0.5 rounded-full font-mono uppercase border ${
                        preset.type === "CLEAN"
                          ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30"
                          : preset.type === "EXEMPT"
                          ? "bg-[#d9ad63]/15 text-[#d9ad63] border-[#d9ad63]/30"
                          : "bg-red-500/15 text-red-400 border-red-500/30"
                      }`}
                    >
                      {preset.type}
                    </span>
                  </div>
                  <p className="text-[11px] text-[#B39D82] leading-relaxed">{preset.desc}</p>
                </motion.div>
              );
            })}
          </div>

          <div className="flex justify-end pt-2">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleVerify}
              disabled={isVerifying || !consentGranted}
              className="flex items-center space-x-2 bg-[#e40000] hover:bg-[#b30000] text-white font-medium py-3 px-6 rounded-2xl text-xs sm:text-sm shadow-[0_0_20px_rgba(228,0,0,0.4)] disabled:opacity-40 cursor-pointer animate-shimmer"
            >
              <RefreshCw className={`w-4 h-4 ${isVerifying ? "animate-spin" : ""}`} />
              <span>{isVerifying ? "Verifying Registry..." : "Run KYC Gate"}</span>
            </motion.button>
          </div>
        </div>
      ) : activeTab === "upload" ? (
        /* 4 Upload Slots */
        <div className="luxury-glass rounded-3xl p-6 sm:p-7 space-y-6 border border-[rgba(235,229,217,0.08)] shadow-[0_20px_50px_rgba(0,0,0,0.7)]">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {[
              { id: "gst_certificate", label: "GST Certificate (REG-06)", icon: Building, desc: "Form GST REG-06 Certificate" },
              { id: "udyam_certificate", label: "Udyam Certificate", icon: FileCheck, desc: "MSME Registration Certificate" },
              { id: "signatory_id", label: "Signatory ID (Masked)", icon: CreditCard, desc: "DPDP Zero-Numeric In-Memory ID" },
              { id: "address_proof", label: "Utility Bill (<90 Days)", icon: FileText, desc: "Electricity or Municipal Bill" },
            ].map((slot) => {
              const staged = uploadedSlots[slot.id];
              const SlotIcon = slot.icon;
              return (
                <div
                  key={slot.id}
                  className={`p-5 rounded-2xl border transition-all ${
                    staged
                      ? "border-emerald-500/40 bg-emerald-950/20"
                      : "border-dashed border-[rgba(235,229,217,0.12)] bg-[#030405] hover:border-[rgba(235,229,217,0.25)]"
                  }`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-2.5">
                      <div className="w-7 h-7 rounded-lg bg-white/[0.04] flex items-center justify-center text-[#B39D82]">
                        <SlotIcon className="w-3.5 h-3.5" />
                      </div>
                      <span className="text-xs font-semibold text-[#EBE5D9]">{slot.label}</span>
                    </div>
                    <span className={`text-[9px] font-mono px-2 py-0.5 rounded-full uppercase border ${
                      staged 
                        ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" 
                        : "bg-white/[0.04] text-[#B39D82]/60 border-white/[0.06]"
                    }`}>
                      {staged ? "STAGED" : "EMPTY"}
                    </span>
                  </div>

                  <p className="text-[11px] text-[#B39D82] mb-3">{slot.desc}</p>

                  <input
                    type="file"
                    id={`file-${slot.id}`}
                    accept=".pdf,.png,.jpg,.jpeg"
                    onChange={(e) => {
                      const f = e.target.files?.[0];
                      if (f) handleFileUpload(f, slot.id);
                    }}
                    className="hidden"
                  />
                  <div className="flex items-center space-x-2">
                    <label
                      htmlFor={`file-${slot.id}`}
                      className="cursor-pointer inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl bg-white/[0.05] hover:bg-white/[0.1] text-xs font-medium text-[#EBE5D9] border border-white/[0.08] transition-colors"
                    >
                      <Upload className="w-3 h-3 text-[#B39D82]" />
                      <span>{staged ? "Replace File" : "Upload Document"}</span>
                    </label>
                    {staged && (
                      <span className="text-[11px] font-mono text-emerald-400 truncate">
                        ✓ {staged.file.name}
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          <div className="flex justify-end pt-2">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleVerifyCompletePackage}
              disabled={Object.keys(uploadedSlots).length === 0}
              className="bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-2.5 px-6 rounded-2xl text-xs sm:text-sm disabled:opacity-40 cursor-pointer shadow-lg transition-all"
            >
              Verify Staged Package
            </motion.button>
          </div>
        </div>
      ) : (
        /* DigiLocker Fast-Track Gateway */
        <div className="luxury-glass rounded-3xl p-6 sm:p-7 space-y-6 border border-[rgba(235,229,217,0.08)] shadow-[0_20px_50px_rgba(0,0,0,0.7)]">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[rgba(235,229,217,0.06)]">
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-amber-500/20 to-red-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400">
                <Zap className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-[#EBE5D9]">
                  DigiLocker 1-Tap Fast-Track (National e-KYC Gateway)
                </h3>
                <p className="text-[11px] text-[#B39D82]">
                  Pulls verified GSTIN &amp; Udyam directly from issuer registries · Verhoeff D₅ dihedral checksum validation
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-[10px] px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
                DPDP Zero-Persistence Active
              </span>
            </div>
          </div>

          {/* UIDAI Sandbox Simulation Architecture Callout (Issue #27) */}
          <div className="p-3.5 bg-blue-950/20 border border-blue-500/25 rounded-2xl flex items-start space-x-2.5 text-xs">
            <Info className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
            <p className="text-[11px] leading-relaxed text-[#B39D82]">
              <strong className="text-blue-300">UIDAI Sandbox Simulation:</strong> Telecom operators connect to UIDAI CIDR via DigiLocker e-KYC API. In this offline evaluation suite, OTP <code className="text-emerald-400 font-mono bg-white/5 px-1 py-0.5 rounded border border-white/10">1234</code> authenticates the session while in-memory redaction preserves <strong className="text-[#EBE5D9]">DPDP Act 2023 zero-persistence privacy</strong>.
            </p>
          </div>

          {/* Quick Demo Preset Chips */}
          <div className="space-y-2">
            <label className="text-[11px] font-mono uppercase tracking-wider text-[#B39D82]">
              Jury Test Bench · 1-Click Simulation Presets
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2">
              <button
                type="button"
                onClick={() => {
                  setDigiAadhaar("2345 6789 0124");
                  setDigiOtp("1234");
                  setDigiGstin("32TTNXB7384T1ZW");
                  setDigiUdyam("UDYAM-KL-00-1234567");
                  setKycResult(null);
                }}
                className="text-left p-2.5 rounded-xl border border-emerald-500/30 bg-emerald-950/10 hover:bg-emerald-950/20 transition-all cursor-pointer"
              >
                <div className="text-[11px] font-semibold text-emerald-300">🌟 Golden Merchant</div>
                <div className="text-[9px] text-[#B39D82] font-mono mt-0.5">Valid UID + Active GST</div>
              </button>

              <button
                type="button"
                onClick={() => {
                  setDigiAadhaar("2345 6789 0120");
                  setDigiOtp("1234");
                  setDigiGstin("32TTNXB7384T1ZW");
                  setDigiUdyam("UDYAM-KL-00-1234567");
                  setKycResult(null);
                }}
                className="text-left p-2.5 rounded-xl border border-red-500/30 bg-red-950/10 hover:bg-red-950/20 transition-all cursor-pointer"
              >
                <div className="text-[11px] font-semibold text-red-300">❌ Verhoeff UID Trap</div>
                <div className="text-[9px] text-[#B39D82] font-mono mt-0.5">Invalid Checksum (0120)</div>
              </button>

              <button
                type="button"
                onClick={() => {
                  setDigiAadhaar("2345 6789 0124");
                  setDigiOtp("9999");
                  setDigiGstin("32TTNXB7384T1ZW");
                  setDigiUdyam("UDYAM-KL-00-1234567");
                  setKycResult(null);
                }}
                className="text-left p-2.5 rounded-xl border border-red-500/30 bg-red-950/10 hover:bg-red-950/20 transition-all cursor-pointer"
              >
                <div className="text-[11px] font-semibold text-red-300">❌ Invalid OTP Trap</div>
                <div className="text-[9px] text-[#B39D82] font-mono mt-0.5">OTP &quot;9999&quot; Rejected</div>
              </button>

              <button
                type="button"
                onClick={() => {
                  setDigiAadhaar("2345 6789 0124");
                  setDigiOtp("1234");
                  setDigiGstin("37IHKXV5167L1ZS");
                  setDigiUdyam("UDYAM-AP-00-1234567");
                  setKycResult(null);
                }}
                className="text-left p-2.5 rounded-xl border border-amber-500/30 bg-amber-950/10 hover:bg-amber-950/20 transition-all cursor-pointer"
              >
                <div className="text-[11px] font-semibold text-amber-300">❌ Inactive GSTIN</div>
                <div className="text-[9px] text-[#B39D82] font-mono mt-0.5">Cancelled in Registry</div>
              </button>
            </div>
          </div>

          {/* Form Fields */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-[#EBE5D9] flex items-center justify-between">
                <span>Signatory 12-digit Aadhaar UID</span>
                {cleanAadhaar.length < 12 ? (
                  <span className="text-[10px] text-[#B39D82] font-mono">
                    12 digits required ({cleanAadhaar.length}/12)
                  </span>
                ) : isAadhaarValidVerhoeff ? (
                  <span className="text-[10px] text-emerald-400 font-mono flex items-center space-x-1">
                    <span>✓ Valid Verhoeff D₅ (UIDAI Standard)</span>
                  </span>
                ) : (
                  <span className="text-[10px] text-red-400 font-mono flex items-center space-x-1">
                    <span>✗ Invalid Checksum (Failed Dihedral D₅)</span>
                  </span>
                )}
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={digiAadhaar}
                  onChange={(e) => setDigiAadhaar(e.target.value)}
                  placeholder="2345 6789 0124"
                  className={`w-full bg-[#030405] border rounded-2xl px-4 py-2.5 text-xs text-[#EBE5D9] font-mono focus:outline-none transition-colors ${
                    cleanAadhaar.length === 12
                      ? isAadhaarValidVerhoeff
                        ? "border-emerald-500/50 focus:border-emerald-400"
                        : "border-red-500/50 focus:border-red-400"
                      : "border-[rgba(235,229,217,0.12)] focus:border-[#e40000]"
                  }`}
                />
              </div>
              <div className="flex items-center justify-between text-[10px] text-[#B39D82] font-mono">
                <span>DPDP Mask:</span>
                <span className="text-emerald-400">{aadhaarRedactionPreview}</span>
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-[#EBE5D9] flex items-center justify-between">
                <span>Authentication OTP</span>
                <span className="text-[10px] text-emerald-400 font-mono">Demo: 1234</span>
              </label>
              <input
                type="text"
                value={digiOtp}
                onChange={(e) => setDigiOtp(e.target.value)}
                placeholder="1234"
                className="w-full bg-[#030405] border border-[rgba(235,229,217,0.12)] rounded-2xl px-4 py-2.5 text-xs text-[#EBE5D9] font-mono focus:outline-none focus:border-[#e40000]"
              />
              <p className="text-[10px] text-[#B39D82]">Simulated DigiLocker mobile OTP authorization.</p>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-[#EBE5D9] flex items-center justify-between">
                <span>Declared GSTIN (Optional / Bundle Dependent)</span>
                {gstinDecoded && (
                  <span className="text-[10px] font-mono text-[#d9ad63]">
                    {gstinDecoded.stateName}
                  </span>
                )}
              </label>
              <input
                type="text"
                value={digiGstin}
                onChange={(e) => setDigiGstin(e.target.value)}
                placeholder="32TTNXB7384T1ZW"
                className="w-full bg-[#030405] border border-[rgba(235,229,217,0.12)] rounded-2xl px-4 py-2.5 text-xs text-[#EBE5D9] font-mono focus:outline-none focus:border-[#e40000]"
              />
              {gstinDecoded && (
                <div className="flex items-center justify-between text-[10px] font-mono text-[#B39D82]">
                  <span>Entity Type: <strong className="text-[#EBE5D9]">{gstinDecoded.entityType}</strong></span>
                  {gstinDecoded.isValidFormat && <span className="text-emerald-400">✓ Valid Structure</span>}
                </div>
              )}
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-[#EBE5D9]">
                Declared Udyam Number (Optional)
              </label>
              <input
                type="text"
                value={digiUdyam}
                onChange={(e) => setDigiUdyam(e.target.value)}
                placeholder="UDYAM-KL-00-1234567"
                className="w-full bg-[#030405] border border-[rgba(235,229,217,0.12)] rounded-2xl px-4 py-2.5 text-xs text-[#EBE5D9] font-mono focus:outline-none focus:border-[#e40000]"
              />
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2 border-t border-[rgba(235,229,217,0.06)]">
            <div className="text-[11px] text-[#B39D82]">
              ⚡ Fast-tracks onboarding from 17.6 days to <strong className="text-emerald-400">&lt; 10 seconds</strong>.
            </div>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleDigiLockerVerify}
              disabled={isVerifying || !consentGranted}
              className="w-full sm:w-auto bg-[#e40000] hover:bg-[#b80000] text-white font-medium py-2.5 px-6 rounded-2xl text-xs sm:text-sm disabled:opacity-40 cursor-pointer shadow-[0_0_20px_rgba(228,0,0,0.3)] transition-all flex items-center justify-center space-x-2"
            >
              {isVerifying ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Connecting DigiLocker...</span>
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4" />
                  <span>Authenticate &amp; Pull from DigiLocker</span>
                </>
              )}
            </motion.button>
          </div>
        </div>
      )}

      {/* Verification Result Card */}
      {kycResult && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
          className="space-y-4"
        >
          {/* Main Status Banner */}
          <div
            className={`p-5 rounded-3xl border flex flex-col sm:flex-row sm:items-center justify-between gap-4 luxury-glass ${
              kycResult.status === "APPROVED"
                ? "border-emerald-500/40 bg-gradient-to-r from-emerald-950/20 via-[#080a0d] to-transparent shadow-[0_0_24px_rgba(16,185,129,0.15)]"
                : kycResult.status === "MANUAL_REVIEW"
                ? "border-amber-500/40 bg-amber-950/20"
                : "border-red-500/40 bg-gradient-to-r from-red-950/20 via-[#080a0d] to-transparent"
            }`}
          >
            <div className="flex items-center space-x-3.5">
              {kycResult.status === "APPROVED" ? (
                <div className="w-10 h-10 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 shrink-0">
                  <ShieldCheck className="w-6 h-6" />
                </div>
              ) : (
                <div className="w-10 h-10 rounded-2xl bg-red-500/20 border border-red-500/40 flex items-center justify-center text-red-400 shrink-0">
                  <AlertCircle className="w-6 h-6" />
                </div>
              )}
              <div>
                <div className="flex items-center space-x-2.5">
                  <h3 className="font-serif text-xl sm:text-2xl font-normal text-[#EBE5D9]">
                    Status: {kycResult.status}
                  </h3>
                  <span className="text-[10px] font-mono text-[#d9ad63] bg-white/[0.04] border border-white/[0.06] px-2 py-0.5 rounded-full">
                    {kycResult.execution_latency_ms}ms
                  </span>
                </div>
                <p className="text-xs text-[#B39D82] mt-0.5">
                  {kycResult.status === "APPROVED"
                    ? "All cryptographic and RapidFuzz registry checks passed."
                    : "Remediation required for statutory compliance pass."}
                </p>
              </div>
            </div>

            {kycResult.status === "APPROVED" && (
              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => onKYCApproved(kycResult)}
                className="bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-3 px-6 rounded-2xl text-xs sm:text-sm flex items-center space-x-2 cursor-pointer shadow-[0_0_20px_rgba(16,185,129,0.35)] shrink-0"
              >
                <span>Proceed to Dispatch</span>
                <ArrowRight className="w-4 h-4" />
              </motion.button>
            )}
          </div>

          {/* Details & Fuzzy Scores */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
            <div className="luxury-glass p-4 rounded-2xl border border-[rgba(235,229,217,0.06)] space-y-1">
              <span className="text-[10px] font-mono uppercase tracking-wider text-[#B39D82] block">DPDP Mask</span>
              <span className="font-mono text-xs text-[#EBE5D9] block truncate font-medium">
                {kycResult.redacted_signatory_id || "[Aadhaar Masked]"}
              </span>
            </div>
            <div className="luxury-glass p-4 rounded-2xl border border-[rgba(235,229,217,0.06)] space-y-1">
              <span className="text-[10px] font-mono uppercase tracking-wider text-[#B39D82] block">GST Status</span>
              <span className="font-mono text-xs text-[#EBE5D9] block font-medium">
                {kycResult.gst_status || "N/A (Exempt)"}
              </span>
            </div>
            <div className="luxury-glass p-4 rounded-2xl border border-[rgba(235,229,217,0.06)] space-y-1">
              <span className="text-[10px] font-mono uppercase tracking-wider text-[#B39D82] block">Utility Bill Age</span>
              <span className="font-mono text-xs text-[#EBE5D9] block font-medium">
                {kycResult.address_bill_age_days ?? "N/A"} days
              </span>
            </div>
          </div>

          {/* Anomalies List */}
          {kycResult.anomalies.length > 0 && (
            <div className="luxury-glass rounded-3xl p-5 sm:p-6 space-y-3 border border-red-500/25">
              <h4 className="text-xs font-semibold text-amber-300 uppercase tracking-wider flex items-center space-x-2">
                <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
                <span>Statutory Exceptions Caught ({kycResult.anomalies.length})</span>
              </h4>
              <div className="space-y-3">
                {kycResult.anomalies.map((anom, idx) => (
                  <div key={idx} className="p-4 rounded-2xl bg-[#030405] border border-white/[0.06] space-y-2">
                    <div className="flex items-center space-x-2.5">
                      <span className="text-[9px] px-2 py-0.5 rounded-full font-mono bg-red-500/20 text-red-400 border border-red-500/30">
                        {anom.code}
                      </span>
                      <span className="text-xs font-medium text-[#EBE5D9]">{anom.message}</span>
                    </div>
                    {anom.remediation && (
                      <p className="text-[11px] text-[#B39D82]">
                        ↳ <span className="text-emerald-400">Action:</span> {anom.remediation}
                      </p>
                    )}
                    {anom.code === "GSTIN_INACTIVE" && (
                      <div className="pt-1">
                        <motion.button
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={handleSwitchToUdyam}
                          className="text-xs bg-[#d9ad63] hover:bg-[#b8914d] text-[#030405] font-semibold px-3.5 py-1.5 rounded-xl cursor-pointer shadow-[0_0_12px_rgba(217,173,99,0.3)] transition-all"
                        >
                          1-Click Switch to Udyam Micro Bundle
                        </motion.button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      )}

      {/* Consent Modal */}
      {showConsentModal && (
        <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-xl flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="luxury-glass-elevated rounded-3xl max-w-md w-full p-6 space-y-4 border border-white/[0.12] shadow-2xl"
          >
            <div className="flex items-center justify-between pb-3 border-b border-white/[0.06]">
              <div className="flex items-center space-x-2">
                <ShieldCheck className="w-4 h-4 text-[#d9ad63]" />
                <h3 className="font-serif text-lg font-normal text-[#EBE5D9]">DPDP Act 2023 Consent Audit</h3>
              </div>
              <button
                onClick={() => setShowConsentModal(false)}
                className="text-xs text-[#B39D82] hover:text-[#EBE5D9] px-2 py-1 rounded-lg bg-white/[0.04]"
              >
                Close
              </button>
            </div>
            <div className="space-y-2 text-xs text-[#B39D82] font-mono bg-[#030405] p-4 rounded-2xl border border-white/[0.06]">
              <p className="text-white">Consent ID: CONSENT_20260715_884920</p>
              <p>Section 6 Notice: Telecom KYC Verification</p>
              <p>In-Memory Hashing: SHA-256 + Immediate ID Masking</p>
              <p className="text-emerald-400">Zero Numeric ID Plaintext Stored on Disk</p>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};
