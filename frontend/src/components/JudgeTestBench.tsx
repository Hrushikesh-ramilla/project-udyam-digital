import React, { useState } from "react";
import { motion } from "motion/react";
import {
  Scale,
  Play,
  CheckCircle2,
  AlertTriangle,
  Code,
  Layers,
  Sparkles,
  ShieldAlert,
  ShieldCheck,
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
    <div className="w-full space-y-7">
      {/* Header */}
      <div className="luxury-glass rounded-3xl p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border border-slate-700/70 shadow-[0_20px_50px_rgba(0,0,0,0.7)]">
        <div className="flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-2xl bg-[#d9ad63]/15 border border-[#d9ad63]/30 flex items-center justify-center text-amber-400">
            <Scale className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Jury Adversarial Test Bench
            </h2>
            <p className="text-xs text-slate-300 mt-0.5">
              Live statutory edge-case validation against running production microservices
            </p>
          </div>
        </div>

        <div className="font-mono text-xs text-amber-400 bg-slate-900/90 px-3.5 py-1.5 rounded-full border border-slate-700/80">
          Anchor Date: 2026-07-15
        </div>
      </div>

      {/* 6 Scenario Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3.5">
        {scenarios.map((sc) => {
          const isSelected = activeScenarioId === sc.id;
          return (
            <motion.div
              key={sc.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => handleRunScenario(sc.id)}
              className={`p-4 rounded-2xl border transition-all cursor-pointer ${
                isSelected
                  ? "border-[#d9ad63] bg-[#d9ad63]/10 shadow-[0_0_24px_rgba(217,173,99,0.2)]"
                  : "border-slate-800 bg-slate-900/80 hover:border-[rgba(235,229,217,0.16)]"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-[9px] px-2 py-0.5 rounded-full font-mono uppercase font-semibold border border-slate-700/80 text-white bg-white/[0.04]">
                  {sc.badge}
                </span>
                <Play
                  className={`w-3.5 h-3.5 transition-colors ${
                    isSelected ? "text-amber-400" : "text-slate-300/50"
                  }`}
                />
              </div>
              <h4 className="text-xs font-semibold text-white">{sc.title}</h4>
              <p className="text-[11px] text-slate-300 mt-1.5 leading-relaxed">{sc.desc}</p>
            </motion.div>
          );
        })}
      </div>

      {/* Results Panel */}
      {scenarioData && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
          className="luxury-glass rounded-3xl p-6 sm:p-7 space-y-5 border border-slate-700/70 shadow-[0_20px_50px_rgba(0,0,0,0.7)]"
        >
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 className="text-lg sm:text-xl font-bold text-white tracking-tight">
              {scenarioData.scenario_id}: {scenarioData.title}
            </h3>
            <div className="flex items-center space-x-2.5 text-xs font-mono">
              <span className="text-slate-300">Latency: {executionTimeMs}ms</span>
              <span
                className={`px-2.5 py-0.5 rounded-full font-semibold border ${
                  scenarioData.verification_result?.status === "APPROVED"
                    ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                    : "bg-red-500/20 text-red-400 border-red-500/30"
                }`}
              >
                {scenarioData.verification_result?.status || "DONE"}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 text-xs">
            <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-700 space-y-1.5">
              <span className="text-amber-400 font-mono text-[10px] uppercase tracking-wider block">Rule Enforced:</span>
              <p className="text-white leading-relaxed">{scenarioData.expected_behavior}</p>
            </div>
            <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-700 space-y-1.5">
              <span className="text-amber-400 font-mono text-[10px] uppercase tracking-wider block">Engine Output:</span>
              <p className="text-white leading-relaxed">{scenarioData.notes}</p>
            </div>
          </div>

          <details className="text-xs bg-slate-900/90 p-4 rounded-2xl border border-slate-700">
            <summary className="cursor-pointer font-mono text-slate-300 hover:text-white select-none">
              Inspect Raw Pydantic Payload (Strict ConfigDict Verification)
            </summary>
            <pre className="mt-3 text-[10px] font-mono text-emerald-400 overflow-x-auto p-2 bg-black/40 rounded-xl">
              {JSON.stringify(scenarioData, null, 2)}
            </pre>
          </details>
        </motion.div>
      )}
    </div>
  );
};
