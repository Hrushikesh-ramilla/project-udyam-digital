import React, { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  ShieldCheck,
  FileText,
  AlertCircle,
  RefreshCw,
  ArrowRight,
  Upload,
  Sparkles,
  Zap,
  Check,
  Info,
  Building,
  CreditCard,
  FileCheck,
  RotateCcw,
  CheckCircle2,
  XCircle,
} from "lucide-react";
import { KYCVerificationResult, CommercialBreakdown } from "../types";
import { verifyKYC, uploadKYCDocument, verifyDigiLocker, KYCUploadResponse } from "../api";
import { validateVerhoeff, redactAadhaarInPlace, decodeGSTIN } from "../utils/verhoeff";

export interface StagedDocInfo {
  filename: string;
  badge: string;
  extractedTitle: string;
  extractedDetail: string;
  isMissing?: boolean;
  isStale?: boolean;
}

export interface SpecimenScenario {
  id: string;
  label: string;
  type: "CLEAN" | "ANOMALY" | "EXEMPT";
  desc: string;
  docs: {
    gst_certificate?: StagedDocInfo;
    udyam_certificate?: StagedDocInfo;
    signatory_id?: StagedDocInfo;
    address_proof?: StagedDocInfo;
  };
}

export const SPECIMEN_SCENARIOS: SpecimenScenario[] = [
  {
    id: "K03",
    label: "Applicant K03 (Clean Golden Path)",
    type: "CLEAN",
    desc: "Valid GSTIN + valid Udyam + fresh 46-day bill. 100% RapidFuzz score.",
    docs: {
      gst_certificate: {
        filename: "K03_gst_reg06.png",
        badge: "Valid Active",
        extractedTitle: "Ganesh Woodcraft",
        extractedDetail: "GSTIN: 27XUIXG0767D1ZP · Joseph Singh (Proprietor) · Active in Registry",
      },
      udyam_certificate: {
        filename: "K03_udyam_cert.png",
        badge: "Verified MSME",
        extractedTitle: "Ganesh Woodcraft",
        extractedDetail: "UDYAM-MH-00-9516696 · Nagpur, Maharashtra",
      },
      signatory_id: {
        filename: "K03_signatory_id.png",
        badge: "DPDP Masked",
        extractedTitle: "Joseph Singh",
        extractedDetail: "Designation: Owner · National ID Redacted: SYN-XXXX-889",
      },
      address_proof: {
        filename: "K03_electricity_bill.png",
        badge: "Fresh (46d)",
        extractedTitle: "Ganesh Woodcraft",
        extractedDetail: "Bill Date: 2026-05-30 · 46 days old (<90-day statutory limit)",
      },
    },
  },
  {
    id: "K01",
    label: "Applicant K01 (Cancelled GSTIN)",
    type: "ANOMALY",
    desc: "Planted defect: GSTIN cancelled in registry 2026-06-01 + Blank Udyam certificate.",
    docs: {
      gst_certificate: {
        filename: "K01_gst_reg06.png",
        badge: "CANCELLED",
        extractedTitle: "Vindhya Tours & Travels",
        extractedDetail: "GSTIN: 37IHKXV5167L1ZS · Cancelled in GST Registry on 2026-06-01",
        isStale: true,
      },
      udyam_certificate: {
        filename: "K01_udyam_cert.png",
        badge: "BLANK REGEX",
        extractedTitle: "Blank Udyam Certificate",
        extractedDetail: "Udyam registration number is blank string / unformatted",
        isMissing: true,
      },
      signatory_id: {
        filename: "K01_signatory_id.png",
        badge: "DPDP Masked",
        extractedTitle: "Ramesh Varma",
        extractedDetail: "Managing Partner · National ID Redacted: SYN-XXXX-190",
      },
      address_proof: {
        filename: "K01_electricity_bill.png",
        badge: "Fresh (35d)",
        extractedTitle: "Vindhya Tours & Travels",
        extractedDetail: "Bill Date: 2026-06-10 · 35 days old (<90d limit)",
      },
    },
  },
  {
    id: "K05",
    label: "Applicant K05 (Missing Udyam)",
    type: "ANOMALY",
    desc: "Planted defect: Mandatory Udyam physical certificate missing from upload folder.",
    docs: {
      gst_certificate: {
        filename: "K05_gst_reg06.png",
        badge: "Valid Active",
        extractedTitle: "Balaji Realty LLP",
        extractedDetail: "GSTIN: 29AABCB1234F1Z5 · Active in Registry",
      },
      // Udyam is intentionally undefined to show empty missing slot!
      signatory_id: {
        filename: "K05_signatory_id.png",
        badge: "DPDP Masked",
        extractedTitle: "Kiran Kumar",
        extractedDetail: "Designated Partner · National ID Redacted: SYN-XXXX-234",
      },
      address_proof: {
        filename: "K05_electricity_bill.png",
        badge: "Fresh (61d)",
        extractedTitle: "Balaji Realty LLP",
        extractedDetail: "Bill Date: 2026-05-15 · 61 days old (<90d limit)",
      },
    },
  },
  {
    id: "K07",
    label: "Applicant K07 (Name Mismatch)",
    type: "ANOMALY",
    desc: "Planted defect: Legal proprietor trade name differs from invoice (<70% RapidFuzz score).",
    docs: {
      gst_certificate: {
        filename: "K07_gst_reg06.png",
        badge: "Valid Active",
        extractedTitle: "(Prop. Shri Physio Clinic)",
        extractedDetail: "GSTIN: 36AAACB1234F1Z6 · Legal name in Registry",
      },
      udyam_certificate: {
        filename: "K07_udyam_cert.png",
        badge: "MISMATCH",
        extractedTitle: "Neelgiri Physio Clinic",
        extractedDetail: "UDYAM-TS-00-1234567 · Conflicts with legal proprietor registration",
        isStale: true,
      },
      signatory_id: {
        filename: "K07_signatory_id.png",
        badge: "DPDP Masked",
        extractedTitle: "Dr. S. Sharma",
        extractedDetail: "Proprietor · National ID Redacted: SYN-XXXX-396",
      },
      address_proof: {
        filename: "K07_electricity_bill.png",
        badge: "Fresh (44d)",
        extractedTitle: "Neelgiri Physio Clinic",
        extractedDetail: "Bill Date: 2026-06-01 · 44 days old",
      },
    },
  },
  {
    id: "K11",
    label: "Applicant K11 (Stale Utility Bill)",
    type: "ANOMALY",
    desc: "Planted defect: Utility bill dated 2025-10-31 is 257 days old (>90-day statutory limit).",
    docs: {
      gst_certificate: {
        filename: "K11_gst_reg06.png",
        badge: "Valid Active",
        extractedTitle: "Trinity Bake House Pvt Ltd",
        extractedDetail: "GSTIN: 27AAACB1234F1Z7 · Active in Registry",
      },
      udyam_certificate: {
        filename: "K11_udyam_cert.png",
        badge: "Verified MSME",
        extractedTitle: "Trinity Bake House",
        extractedDetail: "UDYAM-MH-00-7654321 · Pune, Maharashtra",
      },
      signatory_id: {
        filename: "K11_signatory_id.png",
        badge: "DPDP Masked",
        extractedTitle: "Anil Kapoor",
        extractedDetail: "Director · National ID Redacted: SYN-XXXX-312",
      },
      address_proof: {
        filename: "K11_electricity_bill.png",
        badge: "STALE 257d",
        extractedTitle: "Trinity Bake House",
        extractedDetail: "Bill Date: 2025-10-31 · 257 days old (>90-day statutory limit!)",
        isStale: true,
      },
    },
  },
  {
    id: "KIRANA_NON_GST",
    label: "Kirana Store (Non-GST Micro-Bundle)",
    type: "EXEMPT",
    desc: "Micro-bundle pathway: Valid Udyam + Bill, completely bypassing GSTIN demand.",
    docs: {
      gst_certificate: {
        filename: "Statutory_GST_Exempt_Policy.pdf",
        badge: "GST Exempt",
        extractedTitle: "Non-GST Micro Enterprise",
        extractedDetail: "Statutory exemption under ₹40L turnover threshold (Rule 4 CPQ DAG)",
      },
      udyam_certificate: {
        filename: "KIRANA_udyam_cert.png",
        badge: "Verified MSME",
        extractedTitle: "Ganesh Kirana & General Store",
        extractedDetail: "UDYAM-KL-00-1234567 · Micro-Retailer Onboarding",
      },
      signatory_id: {
        filename: "KIRANA_signatory_id.png",
        badge: "DPDP Masked",
        extractedTitle: "Ganesh Prasad",
        extractedDetail: "Proprietor · National ID Redacted: SYN-XXXX-567",
      },
      address_proof: {
        filename: "KIRANA_electricity_bill.png",
        badge: "Fresh (25d)",
        extractedTitle: "Ganesh Kirana Store",
        extractedDetail: "Bill Date: 2026-06-20 · 25 days old (<90d limit)",
      },
    },
  },
];

const APPLICANT_DISPLAY_NAMES: Record<string, string> = {
  K01: "Applicant K01 (Cancelled GSTIN) · Vindhya Tours & Travels",
  K02: "Applicant K02 · Royal Mart Supermarket",
  K03: "Applicant K03 (Clean) · Balaji Timber Traders / Ganesh Woodcraft",
  K04: "Applicant K04 · Saffron Dental Care LLP",
  K05: "Applicant K05 (Missing Udyam) · Balaji Realty LLP",
  K06: "Applicant K06 · Meenakshi Cotton Traders",
  K07: "Applicant K07 (Name Mismatch) · Neelgiri Physio",
  K08: "Applicant K08 · Green Leaf Legal Associates",
  K09: "Applicant K09 · Kaveri Insurance Advisors",
  K10: "Applicant K10 · Kaveri Stays LLP",
  K11: "Applicant K11 (Stale Utility Bill) · Trinity Bake House",
  K12: "Applicant K12 · Star Electronics",
  KIRANA_NON_GST: "Kirana Store (Non-GST Micro-Bundle) · Ganesh Kirana Store",
};

interface SmartKYCProps {
  quote: CommercialBreakdown | null;
  onKYCApproved: (result: KYCVerificationResult) => void;
  onSwitchToUdyamExempt?: () => void;
}

export const SmartKYC: React.FC<SmartKYCProps> = ({ quote, onKYCApproved, onSwitchToUdyamExempt }) => {
  const [consentGranted, setConsentGranted] = useState<boolean>(true);
  const [selectedPreset, setSelectedPreset] = useState<string>("K03");
  const [stagedDocs, setStagedDocs] = useState<Record<string, StagedDocInfo | undefined>>(
    SPECIMEN_SCENARIOS[0].docs
  );
  const [isVerifying, setIsVerifying] = useState<boolean>(false);
  const [kycResult, setKycResult] = useState<KYCVerificationResult | null>(null);
  const [showConsentModal, setShowConsentModal] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<"staging" | "digilocker">("staging");
  const [uploadedCustomFiles, setUploadedCustomFiles] = useState<Record<string, { file: File; res: KYCUploadResponse }>>({});
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

  // Handle Specimen Auto-Fill (Populates slots without auto-verifying!)
  const handleSelectSpecimen = (specimenId: string) => {
    setSelectedPreset(specimenId);
    setKycResult(null); // Clear previous result so user must explicitly verify!
    const scenario = SPECIMEN_SCENARIOS.find((s) => s.id === specimenId);
    if (scenario) {
      setStagedDocs(scenario.docs);
    }
  };

  // Clear slots back to empty for custom drag-and-drop
  const handleClearSlots = () => {
    setSelectedPreset("CUSTOM");
    setStagedDocs({});
    setUploadedCustomFiles({});
    setKycResult(null);
  };

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

  const handleCustomFileUpload = async (file: File, docType: string) => {
    if (!consentGranted) {
      alert("DPDP Act 2023 requires explicit digital consent before document processing.");
      return;
    }
    setIsVerifying(true);
    try {
      const cartRequiresGstin = quote ? !quote.gst_exempt_eligible : true;
      const res = await uploadKYCDocument(file, docType, cartRequiresGstin);
      setUploadedCustomFiles((prev) => ({
        ...prev,
        [docType]: { file, res },
      }));
      // Auto-fill this slot with real extracted file data
      setStagedDocs((prev) => ({
        ...prev,
        [docType]: {
          filename: file.name,
          badge: "Uploaded File",
          extractedTitle: res.extracted_fields?.trade_name || res.extracted_fields?.consumer_name || res.extracted_fields?.signatory_name || "Extracted Document",
          extractedDetail: `SHA-256: ${res.file_sha256.slice(0, 16)}... · ${Math.round(file.size / 1024)} KB`,
        },
      }));
      setKycResult(null); // Keep result null until user hits verify package!
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "File OCR extraction failed.");
    } finally {
      setIsVerifying(false);
    }
  };

  const handleVerifyStagedPackage = async () => {
    if (!consentGranted) {
      alert("DPDP Act 2023 requires explicit digital consent before verification.");
      return;
    }

    const stagedKeys = Object.keys(stagedDocs).filter((k) => stagedDocs[k] !== undefined);
    if (stagedKeys.length === 0) {
      alert("Please auto-fill a test specimen or upload documents before verifying.");
      return;
    }

    setIsVerifying(true);
    try {
      const cartRequiresGstin = quote ? !quote.gst_exempt_eligible : true;
      let res: KYCVerificationResult;

      // If user uploaded custom files, use package upload verification
      if (Object.keys(uploadedCustomFiles).length > 0) {
        const lastUpload = Object.values(uploadedCustomFiles)[0].res;
        res = lastUpload.verification_result;
      } else {
        // Run verification on the staged specimen (e.g. K03, K01, K11)
        res = await verifyKYC(selectedPreset, cartRequiresGstin);
      }

      setKycResult(res);
      if (res.status === "APPROVED") {
        onKYCApproved(res);
      }
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "KYC verification failed.");
    } finally {
      setIsVerifying(false);
    }
  };

  const handleSwitchToUdyam = async () => {
    if (onSwitchToUdyamExempt) {
      onSwitchToUdyamExempt();
    }
    handleSelectSpecimen("KIRANA_NON_GST");
    setRemediationNotice("Switched to Udyam Micro-Bundle (GST-Free). All GST-only SKUs removed.");
    try {
      const res = await verifyKYC("KIRANA_NON_GST", false);
      setKycResult(res);
    } catch {
      // fallback
    }
  };

  const currentScenario = SPECIMEN_SCENARIOS.find((s) => s.id === selectedPreset);

  return (
    <div className="w-full space-y-7">
      {/* Editorial Header */}
      <div className="luxury-glass rounded-3xl p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-5 border border-slate-700/70 shadow-[0_20px_50px_rgba(0,0,0,0.7)]">
        <div className="flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-2xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shrink-0">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Smart KYC &amp; DPDP Anomaly Gate
            </h2>
            <p className="text-xs text-slate-300 mt-0.5">
              In-memory 12-digit UID masking · RapidFuzz cross-checks under 200ms
            </p>
          </div>
        </div>

        {/* DPDP Consent Switch */}
        <div className="flex items-center space-x-3 bg-slate-900/90 px-4 py-2.5 rounded-2xl border border-slate-700/70 text-xs text-slate-300 shrink-0">
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
          <label htmlFor="dpdp-consent" className="cursor-pointer font-medium text-white">
            DPDP 2023 Consent
          </label>
          <button
            onClick={() => setShowConsentModal(true)}
            className="text-[10px] text-amber-400 hover:underline font-mono"
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

      {/* Mode Switcher Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-slate-800 pb-3">
        <button
          onClick={() => {
            setActiveTab("staging");
            setKycResult(null);
          }}
          className={`px-4 py-2 rounded-full text-xs font-medium transition-all cursor-pointer flex items-center space-x-1.5 ${
            activeTab === "staging"
              ? "bg-[#e40000] text-white shadow-[0_0_16px_rgba(228,0,0,0.4)]"
              : "text-slate-300 hover:text-white hover:bg-white/[0.03]"
          }`}
        >
          <FileCheck className="w-3.5 h-3.5" />
          <span>Live Document Staging (4 Slots)</span>
        </button>

        <button
          onClick={() => {
            setActiveTab("digilocker");
            setKycResult(null);
          }}
          className={`px-4 py-2 rounded-full text-xs font-medium transition-all cursor-pointer flex items-center space-x-1.5 ${
            activeTab === "digilocker"
              ? "bg-[#e40000] text-white shadow-[0_0_16px_rgba(228,0,0,0.4)]"
              : "text-amber-400 hover:text-white hover:bg-white/[0.03] border border-[#d9ad63]/30"
          }`}
        >
          <Zap className="w-3.5 h-3.5 text-amber-400" />
          <span>⚡ DigiLocker Fast-Track (10s)</span>
        </button>
      </div>

      {activeTab === "staging" ? (
        /* Unified Document Staging & Specimen Auto-Fill View */
        <div className="space-y-6">
          {/* ⚡ Specimen Auto-Fill Bench Toolbar */}
          <div className="luxury-glass rounded-3xl p-5 border border-slate-700/70 shadow-[0_15px_40px_rgba(0,0,0,0.6)] space-y-3.5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2.5 border-b border-slate-800">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                <span className="text-xs font-semibold text-white">
                  Auto-Fill Test Specimen (Simulated Dataset)
                </span>
                <span className="text-[9px] font-mono text-amber-400 bg-[#d9ad63]/10 border border-[#d9ad63]/20 px-2 py-0.5 rounded-full">
                  Click to Stage Slots
                </span>
              </div>
              <button
                onClick={handleClearSlots}
                className="text-[11px] font-mono text-slate-300 hover:text-white flex items-center space-x-1 cursor-pointer self-start sm:self-auto"
              >
                <RotateCcw className="w-3 h-3" />
                <span>Reset to Empty Slots</span>
              </button>
            </div>

            {/* Specimen Buttons Row */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
              {SPECIMEN_SCENARIOS.map((scenario) => {
                const isSelected = selectedPreset === scenario.id;
                return (
                  <button
                    key={scenario.id}
                    onClick={() => handleSelectSpecimen(scenario.id)}
                    className={`p-2.5 rounded-xl border text-left transition-all cursor-pointer ${
                      isSelected
                        ? "border-[#e40000] bg-gradient-to-b from-[#e40000]/20 to-transparent shadow-[0_0_15px_rgba(228,0,0,0.3)] ring-1 ring-[#e40000]"
                        : "border-slate-700 bg-slate-900/90 hover:border-white/[0.15]"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[10px] font-mono font-bold text-white">
                        {scenario.id}
                      </span>
                      <span
                        className={`text-[8px] font-mono px-1.5 py-0.5 rounded-full uppercase border ${
                          scenario.type === "CLEAN"
                            ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                            : scenario.type === "EXEMPT"
                            ? "bg-[#d9ad63]/20 text-amber-400 border-[#d9ad63]/30"
                            : "bg-red-500/20 text-red-400 border-red-500/30"
                        }`}
                      >
                        {scenario.type}
                      </span>
                    </div>
                    <div className="text-[10px] font-medium text-white truncate">
                      {scenario.label.split("(")[1]?.replace(")", "") || scenario.label}
                    </div>
                  </button>
                );
              })}
            </div>

            {currentScenario && (
              <p className="text-[11px] text-slate-300 bg-white/[0.02] p-2 rounded-xl border border-white/[0.04]">
                ↳ <strong className="text-white">{currentScenario.label}:</strong> {currentScenario.desc}
              </p>
            )}
          </div>

          {/* 4 Staging Slots (Visible and Hydrated) */}
          <div className="luxury-glass rounded-3xl p-6 sm:p-7 space-y-6 border border-slate-700/70 shadow-[0_20px_50px_rgba(0,0,0,0.7)]">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div>
                <h3 className="text-xs font-semibold text-white">
                  Staged Document Package (4 Statutory Checklist Slots)
                </h3>
                <p className="text-[11px] text-slate-300 mt-0.5">
                  Inspect staged documents below before executing the Smart KYC Anomaly Gate.
                </p>
              </div>
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-full">
                {Object.keys(stagedDocs).filter((k) => stagedDocs[k] !== undefined).length}/4 Slots Ready
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {[
                { id: "gst_certificate", label: "1. GST Certificate (REG-06)", icon: Building, desc: "Form GST REG-06 Registration" },
                { id: "udyam_certificate", label: "2. Udyam Certificate", icon: FileCheck, desc: "MSME Registration Certificate" },
                { id: "signatory_id", label: "3. Signatory National ID", icon: CreditCard, desc: "DPDP In-Memory Masked ID" },
                { id: "address_proof", label: "4. Utility Bill (<90 Days)", icon: FileText, desc: "Electricity or Municipal Bill" },
              ].map((slot) => {
                const staged = stagedDocs[slot.id];
                const SlotIcon = slot.icon;
                return (
                  <div
                    key={slot.id}
                    className={`p-5 rounded-2xl border transition-all ${
                      staged && !staged.isMissing
                        ? staged.isStale
                          ? "border-red-500/40 bg-red-950/15"
                          : "border-emerald-500/40 bg-emerald-950/15"
                        : "border-dashed border-slate-700 bg-slate-900/90"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2.5">
                      <div className="flex items-center space-x-2.5">
                        <div className="w-7 h-7 rounded-lg bg-white/[0.04] flex items-center justify-center text-slate-300">
                          <SlotIcon className="w-3.5 h-3.5" />
                        </div>
                        <span className="text-xs font-semibold text-white">{slot.label}</span>
                      </div>
                      <span
                        className={`text-[9px] font-mono px-2 py-0.5 rounded-full uppercase border ${
                          staged && !staged.isMissing
                            ? staged.isStale
                              ? "bg-red-500/20 text-red-400 border-red-500/30"
                              : "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                            : "bg-red-500/20 text-red-400 border-red-500/30"
                        }`}
                      >
                        {staged && !staged.isMissing ? staged.badge : "EMPTY (MISSING)"}
                      </span>
                    </div>

                    {staged && !staged.isMissing ? (
                      <div className="space-y-1.5 mb-3 bg-slate-900/90 p-3 rounded-xl border border-white/[0.04]">
                        <div className="text-xs font-medium text-white truncate">
                          📄 {staged.extractedTitle}
                        </div>
                        <div className="text-[10px] font-mono text-slate-300 truncate">
                          {staged.extractedDetail}
                        </div>
                        <div className="text-[9px] font-mono text-amber-400">
                          File: {staged.filename}
                        </div>
                      </div>
                    ) : (
                      <p className="text-[11px] text-slate-300 mb-3">{slot.desc}</p>
                    )}

                    <div className="flex items-center justify-between pt-1">
                      <input
                        type="file"
                        id={`custom-file-${slot.id}`}
                        accept=".pdf,.png,.jpg,.jpeg"
                        onChange={(e) => {
                          const f = e.target.files?.[0];
                          if (f) handleCustomFileUpload(f, slot.id);
                        }}
                        className="hidden"
                      />
                      <label
                        htmlFor={`custom-file-${slot.id}`}
                        className="cursor-pointer inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-white/[0.05] hover:bg-white/[0.1] text-xs font-medium text-white border border-slate-700/80 transition-colors"
                      >
                        <Upload className="w-3 h-3 text-slate-300" />
                        <span>{staged ? "Replace File" : "Upload File"}</span>
                      </label>
                      {staged && (
                        <span className="text-[10px] font-mono text-emerald-400">
                          ✓ Staged in-memory
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Explicit Submission Action Bar */}
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-3 border-t border-slate-800">
              <div className="text-xs text-slate-300">
                Ready to verify: <strong className="text-white">{currentScenario?.label || "Custom Staged Package"}</strong>
              </div>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleVerifyStagedPackage}
                disabled={isVerifying || !consentGranted}
                className="w-full sm:w-auto flex items-center justify-center space-x-2 bg-[#e40000] hover:bg-[#b30000] text-white font-medium py-3 px-8 rounded-2xl text-xs sm:text-sm shadow-[0_0_20px_rgba(228,0,0,0.4)] disabled:opacity-40 cursor-pointer animate-shimmer"
              >
                <RefreshCw className={`w-4 h-4 ${isVerifying ? "animate-spin" : ""}`} />
                <span>
                  {isVerifying
                    ? "Verifying Cryptographic Hashes & Registries..."
                    : `Run KYC Verification on Staged Package`}
                </span>
              </motion.button>
            </div>
          </div>
        </div>
      ) : (
        /* DigiLocker Fast-Track Gateway */
        <div className="luxury-glass rounded-3xl p-6 sm:p-7 space-y-6 border border-slate-700/70 shadow-[0_20px_50px_rgba(0,0,0,0.7)]">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-amber-500/20 to-red-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400">
                <Zap className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-serif text-lg font-normal text-white">
                  Aadhaar DigiLocker Gateway
                </h3>
                <p className="text-xs text-slate-300 mt-0.5">
                  UIDAI Verhoeff $D_5$ Checksum · OTP Authentication · Registry Pull
                </p>
              </div>
            </div>

          {/* UIDAI Sandbox Simulation Architecture Callout (Issue #27) */}
          <div className="p-3.5 bg-blue-950/20 border border-blue-500/25 rounded-2xl flex items-start space-x-2.5 text-xs">
            <Info className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
            <p className="text-[11px] leading-relaxed text-slate-300">
              <strong className="text-blue-300">UIDAI Sandbox Simulation:</strong> Telecom operators connect to UIDAI CIDR via DigiLocker e-KYC API. In this offline evaluation suite, OTP <code className="text-emerald-400 font-mono bg-white/5 px-1 py-0.5 rounded border border-white/10">1234</code> authenticates the session while in-memory redaction preserves <strong className="text-white">DPDP Act 2023 zero-persistence privacy</strong>.
            </p>
          </div>

          {/* Quick-fill Scenario Buttons for DigiLocker */}
          <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => {
                  setDigiAadhaar("2345 6789 0124");
                  setDigiOtp("1234");
                  setDigiGstin("32TTNXB7384T1ZW");
                  setDigiUdyam("UDYAM-KL-00-1234567");
                  setKycResult(null);
                }}
                className="px-2.5 py-1 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[10px] font-mono cursor-pointer"
              >
                Auto-fill Clean Merchant
              </button>
              <button
                type="button"
                onClick={() => {
                  setDigiAadhaar("2345 6789 0120");
                  setDigiOtp("1234");
                  setKycResult(null);
                }}
                className="px-2.5 py-1 rounded-xl bg-red-500/10 hover:bg-red-500/20 text-red-300 border border-red-500/30 text-[10px] font-mono cursor-pointer"
              >
                Invalid UID (0120)
              </button>
            </div>
          </div>

          {/* Form Fields */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-white flex items-center justify-between">
                <span>Signatory 12-digit Aadhaar UID</span>
                {cleanAadhaar.length < 12 ? (
                  <span className="text-[10px] text-slate-300 font-mono">
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
                  className={`w-full bg-slate-900/90 border rounded-2xl px-4 py-2.5 text-xs text-white font-mono focus:outline-none transition-colors ${
                    cleanAadhaar.length === 12
                      ? isAadhaarValidVerhoeff
                        ? "border-emerald-500/50 focus:border-emerald-400"
                        : "border-red-500/50 focus:border-red-400"
                      : "border-slate-700 focus:border-[#e40000]"
                  }`}
                />
              </div>
              <div className="flex items-center justify-between text-[10px] text-slate-300 font-mono">
                <span>DPDP Mask:</span>
                <span className="text-emerald-400">{aadhaarRedactionPreview}</span>
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-white flex items-center justify-between">
                <span>Authentication OTP</span>
                <span className="text-[10px] text-emerald-400 font-mono">Demo: 1234</span>
              </label>
              <input
                type="text"
                value={digiOtp}
                onChange={(e) => setDigiOtp(e.target.value)}
                placeholder="1234"
                className="w-full bg-slate-900/90 border border-slate-700 rounded-2xl px-4 py-2.5 text-xs text-white font-mono focus:outline-none focus:border-[#e40000]"
              />
              <p className="text-[10px] text-slate-300">Simulated DigiLocker mobile OTP authorization.</p>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-white flex items-center justify-between">
                <span>Declared GSTIN (Optional / Bundle Dependent)</span>
                {gstinDecoded && (
                  <span className="text-[10px] font-mono text-amber-400">
                    {gstinDecoded.stateName}
                  </span>
                )}
              </label>
              <input
                type="text"
                value={digiGstin}
                onChange={(e) => setDigiGstin(e.target.value)}
                placeholder="32TTNXB7384T1ZW"
                className="w-full bg-slate-900/90 border border-slate-700 rounded-2xl px-4 py-2.5 text-xs text-white font-mono focus:outline-none focus:border-[#e40000]"
              />
              {gstinDecoded && (
                <div className="flex items-center justify-between text-[10px] font-mono text-slate-300">
                  <span>Entity Type: <strong className="text-white">{gstinDecoded.entityType}</strong></span>
                  {gstinDecoded.isValidFormat && <span className="text-emerald-400">✓ Valid Structure</span>}
                </div>
              )}
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-white">
                Declared Udyam Number (Optional)
              </label>
              <input
                type="text"
                value={digiUdyam}
                onChange={(e) => setDigiUdyam(e.target.value)}
                placeholder="UDYAM-KL-00-1234567"
                className="w-full bg-slate-900/90 border border-slate-700 rounded-2xl px-4 py-2.5 text-xs text-white font-mono focus:outline-none focus:border-[#e40000]"
              />
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2 border-t border-slate-800">
            <div className="text-[11px] text-slate-300">
              ⚡ Fast-tracks onboarding from 17.6 days to <strong className="text-emerald-400">&lt; 10 seconds</strong>.
            </div>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleDigiLockerVerify}
              disabled={isVerifying || !consentGranted}
              className="w-full sm:w-auto bg-[#e40000] hover:bg-[#b80000] text-white font-medium py-2.5 px-6 rounded-2xl text-xs sm:text-sm disabled:opacity-40 cursor-pointer shadow-[0_0_20px_rgba(228,0,0,0.3)] transition-all flex items-center justify-center space-x-2"
            >
              <Zap className="w-4 h-4" />
              <span>{isVerifying ? "Connecting DigiLocker..." : "Authenticate & Pull from DigiLocker"}</span>
            </motion.button>
          </div>
        </div>
      )}

      {/* Verification Result Card (Only rendered after user clicks Verify!) */}
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
                  <h3 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                    Status: {kycResult.status}
                  </h3>
                  <span className="text-[10px] font-mono text-amber-400 bg-white/[0.04] border border-slate-700 px-2 py-0.5 rounded-full">
                    {kycResult.execution_latency_ms}ms
                  </span>
                </div>
                <div className="text-[11px] font-mono text-amber-400 mt-1 flex flex-wrap items-center gap-1.5">
                  <span>Verified Subject:</span>
                  <span className="text-white font-sans font-medium">
                    {kycResult.applicant_id && APPLICANT_DISPLAY_NAMES[kycResult.applicant_id]
                      ? APPLICANT_DISPLAY_NAMES[kycResult.applicant_id]
                      : activeTab === "digilocker"
                      ? "DigiLocker Authenticated Signatory"
                      : "Staged Document Package"}
                  </span>
                </div>
                <p className="text-xs text-slate-300 mt-0.5">
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
            <div className="luxury-glass p-4 rounded-2xl border border-slate-800 space-y-1">
              <span className="text-[10px] font-mono uppercase tracking-wider text-slate-300 block">DPDP Mask</span>
              <span className="font-mono text-xs text-white block truncate font-medium">
                {kycResult.redacted_signatory_id || "[Aadhaar Masked]"}
              </span>
            </div>
            <div className="luxury-glass p-4 rounded-2xl border border-slate-800 space-y-1">
              <span className="text-[10px] font-mono uppercase tracking-wider text-slate-300 block">GST Status</span>
              <span className="font-mono text-xs text-white block font-medium">
                {kycResult.gst_status || "N/A (Exempt)"}
              </span>
            </div>
            <div className="luxury-glass p-4 rounded-2xl border border-slate-800 space-y-1">
              <span className="text-[10px] font-mono uppercase tracking-wider text-slate-300 block">Utility Bill Age</span>
              <span className="font-mono text-xs text-white block font-medium">
                {kycResult.address_bill_age_days ?? "N/A"} days
              </span>
            </div>
          </div>

          {/* Anomalies List with 1-click Remediation */}
          {kycResult.anomalies.length > 0 && (
            <div className="luxury-glass rounded-3xl p-5 sm:p-6 space-y-3 border border-red-500/25">
              <h4 className="text-xs font-semibold text-amber-300 uppercase tracking-wider flex items-center space-x-2">
                <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
                <span>Statutory Exceptions Caught ({kycResult.anomalies.length})</span>
              </h4>
              <div className="space-y-3">
                {kycResult.anomalies.map((anom, idx) => (
                  <div key={idx} className="p-4 rounded-2xl bg-slate-900/90 border border-slate-700 space-y-2">
                    <div className="flex items-center space-x-2.5">
                      <span className="text-[9px] px-2 py-0.5 rounded-full font-mono bg-red-500/20 text-red-400 border border-red-500/30">
                        {anom.code}
                      </span>
                      <span className="text-xs font-medium text-white">{anom.message}</span>
                    </div>
                    {anom.remediation && (
                      <p className="text-[11px] text-slate-300">
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
                          Switch to Udyam Micro-Bundle (GST-Free)
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
    </div>
  );
};
