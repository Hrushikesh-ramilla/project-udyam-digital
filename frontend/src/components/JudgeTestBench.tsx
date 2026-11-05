import React, { useState } from "react";
import { motion } from "motion/react";
import {
  Scale,
  Play,
  CheckCircle2,
  AlertTriangle,
  Code,
  Layers,
} from "lucide-react";
import { fetchJudgeScenario } from "../api";
import { JudgeScenarioResult, KYCAnomaly } from "../types";

export const JudgeTestBench: React.FC = () => {
  const [activeScenarioId, setActiveScenarioId] = useState<string>("K01");
  const [running, setRunning] = useState<boolean>(false);
  const [scenarioData, setScenarioData] = useState<JudgeScenarioResult | null>(null);
  const [executionTimeMs, setExecutionTimeMs] = useState<number | null>(null);

  const scenarios = [
    {
      id: "K01",
      title: "Applicant K01: Cancelled GSTIN",
      badge: "BLOCKER",
      desc: "Cancelled GSTIN on 2026-06-01 + Blank Udyam certificate. Rejects with non-GST fallback.",
    },
    {
      id: "K05",
      title: "Applicant K05: Missing Udyam",
      badge: "MISSING DOC",
      desc: "Udyam certificate file omitted. Flags UDYAM_DOC_MISSING without crashing.",
    },
    {
      id: "K07",
      title: "Applicant K07: Name Mismatch",
      badge: "FUZZY MISMATCH",
      desc: "Legal trade name differs from declared invoice (<70% RapidFuzz score).",
    },
    {
      id: "K11",
      title: "Applicant K11: Stale Utility Bill",
      badge: "EXPIRED (>90D)",
      desc: "Bill dated 2025-10-31 is 257 days old relative to 2026-07-15 anchor.",
    },
    {
      id: "K03",
      title: "Applicant K03: Clean Approval",
      badge: "GOLDEN PATH",
      desc: "Valid GSTIN, valid Udyam, fresh bill. 100% RapidFuzz score. Approved in <200ms.",
    },
    {
      id: "NON_GST_KIRANA",
      title: "Non-GST Kirana: Micro-Bundle",
      badge: "2.0% GAP SOLVER",
      desc: "Filters GST-only SKUs, allowing broadband + Wi-Fi to pass with Udyam.",
    },
  ];

  const handleRunScenario = async (id: string) => {
    setActiveScenarioId(id);
    setRunning(true);
    const start = performance.now();
    try {
      const data = await fetchJudgeScenario(id);
      const elapsed = Math.round(performance.now() - start);
      setScenarioData(data);
      setExecutionTimeMs(elapsed);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Scenario failed");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-5">
      {/* Header */}
      <div className="luxury-glass rounded-2xl p-5 flex items-center justify-between border border-[rgba(235,229,217,0.06)] shadow-apple-card">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-xl bg-[#d9ad63]/15 border border-[#d9ad63]/30 flex items-center justify-center text-[#d9ad63]">
            <Scale className="w-4 h-4" />
          </div>
          <div>
            <h2 className="font-sans text-base font-semibold text-[#EBE5D9]">
              Jury Adversarial Test Bench
            </h2>
            <p className="text-xs text-[#B39D82]">
              Live statutory edge-case validation against the running engine
            </p>
          </div>
        </div>

        <div className="font-mono text-xs text-[#B39D82] bg-[#030405] px-3 py-1.5 rounded-full border border-white/[0.06]">
          Anchor: 2026-07-15
        </div>
      </div>

      {/* 6 Scenario Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
        {scenarios.map((sc) => {
          const isSelected = activeScenarioId === sc.id;
          return (
            <motion.div
              key={sc.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => handleRunScenario(sc.id)}
              className={`p-4 rounded-xl border transition-all cursor-pointer ${
                isSelected
                  ? "border-[#d9ad63] bg-[#d9ad63]/10 shadow-[0_0_16px_rgba(217,173,99,0.25)]"
                  : "border-[rgba(235,229,217,0.06)] bg-[#080a0d] hover:border-[rgba(235,229,217,0.14)]"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-[9px] px-2 py-0.5 rounded-full font-mono font-medium border border-white/[0.08] text-[#EBE5D9]">
                  {sc.badge}
                </span>
                <Play
                  className={`w-3.5 h-3.5 ${
                    isSelected ? "text-[#d9ad63]" : "text-[#B39D82]/50"
                  }`}
                />
              </div>
              <h4 className="text-xs font-medium text-[#EBE5D9]">{sc.title}</h4>
              <p className="text-[11px] text-[#B39D82] mt-1 leading-relaxed">{sc.desc}</p>
            </motion.div>
          );
        })}
      </div>

      {/* Results Panel */}
      {scenarioData && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
          className="luxury-glass rounded-2xl p-5 space-y-4 border border-[rgba(235,229,217,0.06)] shadow-apple-card"
        >
          <div className="flex items-center justify-between pb-2 border-b border-[rgba(235,229,217,0.04)]">
            <h3 className="font-sans text-sm font-semibold text-[#EBE5D9]">
              {scenarioData.scenario_id}: {scenarioData.title}
            </h3>
            <div className="flex items-center space-x-2 text-xs font-mono">
              <span className="text-[#B39D82]">Latency: {executionTimeMs}ms</span>
              <span
                className={`px-2 py-0.5 rounded-full ${
                  scenarioData.verification_result?.status === "APPROVED"
                    ? "bg-emerald-500/20 text-emerald-400"
                    : "bg-red-500/20 text-red-400"
                }`}
              >
                {scenarioData.verification_result?.status || "DONE"}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            <div className="p-3 rounded-xl bg-[#030405] border border-white/[0.04] space-y-1">
              <span className="text-[#B39D82] font-mono text-[10px] uppercase block">Rule Enforced:</span>
              <p className="text-[#EBE5D9] leading-relaxed">{scenarioData.expected_behavior}</p>
            </div>
            <div className="p-3 rounded-xl bg-[#030405] border border-white/[0.04] space-y-1">
              <span className="text-[#B39D82] font-mono text-[10px] uppercase block">Engine Output:</span>
              <p className="text-[#EBE5D9] leading-relaxed">{scenarioData.notes}</p>
            </div>
          </div>

          <details className="text-xs bg-[#030405] p-3 rounded-xl border border-white/[0.04]">
            <summary className="cursor-pointer font-mono text-[#B39D82] hover:text-[#EBE5D9]">
              Inspect Raw Pydantic Payload
            </summary>
            <pre className="mt-2 text-[10px] font-mono text-emerald-400 overflow-x-auto">
              {JSON.stringify(scenarioData, null, 2)}
            </pre>
          </details>
        </motion.div>
      )}
    </div>
  );
};
