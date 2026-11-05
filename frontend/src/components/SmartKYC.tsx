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
} from "lucide-react";
import { KYCVerificationResult, CommercialBreakdown } from "../types";
import { verifyKYC, uploadKYCDocument, KYCUploadResponse } from "../api";

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
  const [activeTab, setActiveTab] = useState<"preset" | "upload">("preset");
  const [uploadDocType, setUploadDocType] = useState<string>("gst_certificate");
  const [uploadResponse, setUploadResponse] = useState<KYCUploadResponse | null>(null);
  const [uploadedSlots, setUploadedSlots] = useState<Record<string, { file: File; res: KYCUploadResponse }>>({});
  const [remediationNotice, setRemediationNotice] = useState<string | null>(null);

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
    setRemediationNotice("Switched to Udyam Micro Bundle (GST-Free).");
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
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Clean Header */}
      <div className="luxury-glass rounded-2xl p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border border-[rgba(235,229,217,0.06)] shadow-apple-card">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div>
            <h2 className="font-sans text-base font-medium text-[#EBE5D9]">
              Smart KYC &amp; DPDP Anomaly Gate
            </h2>
            <p className="text-xs text-[#B39D82]">
              In-memory 12-digit UID masking · RapidFuzz cross-checks under 200ms
            </p>
          </div>
        </div>

        {/* DPDP Consent */}
        <div className="flex items-center space-x-2.5 bg-[#030405] px-3.5 py-2 rounded-xl border border-[rgba(235,229,217,0.06)] text-xs text-[#B39D82]">
          <input
            type="checkbox"
            id="dpdp-consent"
            checked={consentGranted}
            onChange={(e) => setConsentGranted(e.target.checked)}
            className="w-3.5 h-3.5 accent-[#e40000] cursor-pointer"
          />
          <label htmlFor="dpdp-consent" className="cursor-pointer">
            DPDP 2023 Consent
          </label>
          <button
            onClick={() => setShowConsentModal(true)}
            className="text-[10px] text-[#d9ad63] hover:underline font-mono ml-1"
          >
            [Audit]
          </button>
        </div>
      </div>

      {remediationNotice && (
        <div className="p-3 rounded-xl bg-emerald-950/30 border border-emerald-500/30 text-emerald-300 text-xs flex items-center space-x-2">
          <Sparkles className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{remediationNotice}</span>
        </div>
      )}

      {/* Mode Switcher */}
      <div className="flex space-x-2 border-b border-[rgba(235,229,217,0.04)] pb-2">
        <button
          onClick={() => {
            setActiveTab("preset");
            setUploadResponse(null);
          }}
          className={`px-3.5 py-1.5 rounded-full text-xs font-medium transition-colors cursor-pointer ${
            activeTab === "preset"
              ? "bg-[#e40000] text-white shadow-[0_0_12px_rgba(228,0,0,0.4)]"
              : "text-[#B39D82] hover:text-[#EBE5D9]"
          }`}
        >
          Preset Specimens (K01–K12)
        </button>
        <button
          onClick={() => {
            setActiveTab("upload");
            setKycResult(null);
          }}
          className={`px-3.5 py-1.5 rounded-full text-xs font-medium transition-colors cursor-pointer ${
            activeTab === "upload"
              ? "bg-[#e40000] text-white shadow-[0_0_12px_rgba(228,0,0,0.4)]"
              : "text-[#B39D82] hover:text-[#EBE5D9]"
          }`}
        >
          Live Document Staging (4 Slots)
        </button>
      </div>

      {activeTab === "preset" ? (
        /* Presets Grid */
        <div className="luxury-glass rounded-2xl p-5 space-y-4 border border-[rgba(235,229,217,0.06)] shadow-apple-card">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
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
                  className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
                    isSelected
                      ? "border-[#e40000] bg-[#e40000]/10 shadow-[0_0_16px_rgba(228,0,0,0.2)]"
                      : "border-[rgba(235,229,217,0.04)] bg-[#030405] hover:border-[rgba(235,229,217,0.12)]"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-medium text-[#EBE5D9]">{preset.label}</span>
                    <span
                      className={`text-[9px] px-1.5 py-0.2 rounded font-mono ${
                        preset.type === "CLEAN"
                          ? "bg-emerald-500/15 text-emerald-400"
                          : preset.type === "EXEMPT"
                          ? "bg-blue-500/15 text-blue-400"
                          : "bg-amber-500/15 text-amber-400"
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
              className="flex items-center space-x-2 bg-[#e40000] hover:bg-[#b30000] text-white font-medium py-2 px-5 rounded-xl text-xs sm:text-sm shadow-[0_0_16px_rgba(228,0,0,0.4)] disabled:opacity-40 cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isVerifying ? "animate-spin" : ""}`} />
              <span>{isVerifying ? "Verifying..." : "Run KYC Gate"}</span>
            </motion.button>
          </div>
        </div>
      ) : (
        /* 4 Upload Slots */
        <div className="luxury-glass rounded-2xl p-5 space-y-4 border border-[rgba(235,229,217,0.06)] shadow-apple-card">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {[
              { id: "gst_certificate", label: "GST Certificate (REG-06)" },
              { id: "udyam_certificate", label: "Udyam Certificate" },
              { id: "signatory_id", label: "Signatory ID (Masked)" },
              { id: "address_proof", label: "Utility Bill (<90 Days)" },
            ].map((slot) => {
              const staged = uploadedSlots[slot.id];
              return (
                <div
                  key={slot.id}
                  className={`p-3.5 rounded-xl border ${
                    staged
                      ? "border-emerald-500/40 bg-emerald-950/20"
                      : "border-[rgba(235,229,217,0.04)] bg-[#030405]"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-medium text-[#EBE5D9]">{slot.label}</span>
                    <span className="text-[9px] font-mono text-[#B39D82]">
                      {staged ? "STAGED" : "EMPTY"}
                    </span>
                  </div>

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
                  <label
                    htmlFor={`file-${slot.id}`}
                    className="cursor-pointer inline-flex items-center space-x-1.5 px-3 py-1 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] text-xs text-[#EBE5D9] border border-white/[0.08] transition-colors"
                  >
                    <Upload className="w-3 h-3 text-[#B39D82]" />
                    <span>{staged ? "Replace File" : "Upload File"}</span>
                  </label>
                  {staged && (
                    <span className="text-[11px] font-mono text-[#B39D82] ml-2 truncate">
                      {staged.file.name}
                    </span>
                  )}
                </div>
              );
            })}
          </div>

          <div className="flex justify-end pt-1">
            <button
              onClick={handleVerifyCompletePackage}
              disabled={Object.keys(uploadedSlots).length === 0}
              className="bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-1.5 px-4 rounded-xl text-xs disabled:opacity-40 cursor-pointer"
            >
              Verify Staged Package
            </button>
          </div>
        </div>
      )}

      {/* Verification Result Card */}
      {kycResult && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
          className="space-y-4"
        >
          {/* Main Status */}
          <div
            className={`p-4 rounded-2xl border flex items-center justify-between luxury-glass ${
              kycResult.status === "APPROVED"
                ? "border-emerald-500/30 bg-emerald-950/20"
                : kycResult.status === "MANUAL_REVIEW"
                ? "border-amber-500/30 bg-amber-950/20"
                : "border-red-500/30 bg-red-950/20"
            }`}
          >
            <div className="flex items-center space-x-3">
              {kycResult.status === "APPROVED" ? (
                <ShieldCheck className="w-6 h-6 text-emerald-400" />
              ) : (
                <AlertCircle className="w-6 h-6 text-[#e40000]" />
              )}
              <div>
                <div className="flex items-center space-x-2">
                  <h3 className="font-sans text-sm font-semibold text-[#EBE5D9]">
                    Status: {kycResult.status}
                  </h3>
                  <span className="text-[10px] font-mono text-[#B39D82] bg-white/[0.04] px-1.5 py-0.2 rounded">
                    {kycResult.execution_latency_ms}ms
                  </span>
                </div>
                <p className="text-xs text-[#B39D82] mt-0.5">
                  {kycResult.status === "APPROVED"
                    ? "All cryptographic and RapidFuzz registry checks passed."
                    : "Remediation required for compliance pass."}
                </p>
              </div>
            </div>

            {kycResult.status === "APPROVED" && (
              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => onKYCApproved(kycResult)}
                className="bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-2 px-4 rounded-xl text-xs flex items-center space-x-1.5 cursor-pointer shadow-md"
              >
                <span>Proceed to Dispatch</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </motion.button>
            )}
          </div>

          {/* Details & Fuzzy Scores */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="luxury-glass p-3 rounded-xl border border-[rgba(235,229,217,0.06)] space-y-1">
              <span className="text-[10px] text-[#B39D82] block">DPDP Mask</span>
              <span className="font-mono text-xs text-[#EBE5D9] block truncate">
                {kycResult.redacted_signatory_id || "[Aadhaar Masked]"}
              </span>
            </div>
            <div className="luxury-glass p-3 rounded-xl border border-[rgba(235,229,217,0.06)] space-y-1">
              <span className="text-[10px] text-[#B39D82] block">GST Status</span>
              <span className="font-mono text-xs text-[#EBE5D9] block">
                {kycResult.gst_status || "N/A (Exempt)"}
              </span>
            </div>
            <div className="luxury-glass p-3 rounded-xl border border-[rgba(235,229,217,0.06)] space-y-1">
              <span className="text-[10px] text-[#B39D82] block">Utility Bill Age</span>
              <span className="font-mono text-xs text-[#EBE5D9] block">
                {kycResult.address_bill_age_days ?? "N/A"} days
              </span>
            </div>
          </div>

          {/* Anomalies List */}
          {kycResult.anomalies.length > 0 && (
            <div className="luxury-glass rounded-2xl p-4 space-y-2.5 border border-red-500/20">
              <h4 className="text-xs font-semibold text-amber-300 uppercase tracking-wider">
                Exceptions Caught ({kycResult.anomalies.length})
              </h4>
              <div className="space-y-2">
                {kycResult.anomalies.map((anom, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-[#030405] border border-white/[0.04] space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-[9px] px-1.5 py-0.2 rounded font-mono bg-red-500/20 text-red-400">
                        {anom.code}
                      </span>
                      <span className="text-xs text-[#EBE5D9]">{anom.message}</span>
                    </div>
                    {anom.remediation && (
                      <p className="text-[11px] text-emerald-400">
                        ↳ Action: {anom.remediation}
                      </p>
                    )}
                    {anom.code === "GSTIN_INACTIVE" && (
                      <button
                        onClick={handleSwitchToUdyam}
                        className="mt-1 text-xs bg-emerald-600 hover:bg-emerald-500 text-white px-2.5 py-1 rounded-lg font-medium cursor-pointer"
                      >
                        1-Click Switch to Udyam Micro Bundle
                      </button>
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
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="luxury-glass rounded-2xl max-w-md w-full p-5 space-y-3 border border-white/[0.1]">
            <div className="flex items-center justify-between pb-2 border-b border-white/[0.06]">
              <h3 className="font-sans text-sm font-semibold text-[#EBE5D9]">DPDP Act 2023 Consent</h3>
              <button
                onClick={() => setShowConsentModal(false)}
                className="text-xs text-[#B39D82] hover:text-white"
              >
                Close
              </button>
            </div>
            <div className="space-y-1.5 text-xs text-[#B39D82] font-mono bg-[#030405] p-3 rounded-xl border border-white/[0.04]">
              <p>Consent ID: CONSENT_20260715_884920</p>
              <p>Purpose: Telecom KYC Verification</p>
              <p>Storage: Zero-numeric plaintext persistence</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
