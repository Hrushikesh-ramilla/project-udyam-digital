import React, { useState } from "react";
import {
  Scale,
  Play,
  CheckCircle2,
  AlertTriangle,
  Code,
  Clock,
  ShieldCheck,
  Cpu,
  Layers,
  ArrowRight,
  Database,
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
      title: "Applicant K01: Cancelled GSTIN Verification",
      badge: "REGULATORY BLOCKER",
      badgeColor: "bg-red-500/20 text-red-400 border-red-500/30",
      desc: "GSTIN cancelled on 2026-06-01 + Blank Udyam certificate. Engine rejects immediately with actionable non-GST fallback.",
    },
    {
      id: "K05",
      title: "Applicant K05: Missing Mandatory Document",
      badge: "MISSING DOCUMENT",
      badgeColor: "bg-amber-500/20 text-amber-400 border-amber-500/30",
      desc: "Udyam certificate file omitted from ingestion payload. Engine flags UDYAM_DOC_MISSING without crashing.",
    },
    {
      id: "K07",
      title: "Applicant K07: Entity Name Discrepancy",
      badge: "FUZZY MISMATCH",
      badgeColor: "bg-amber-500/20 text-amber-400 border-amber-500/30",
      desc: "Legal trade name differs from declared name in invoice (RapidFuzz token similarity < 70%).",
    },
    {
      id: "K11",
      title: "Applicant K11: Stale Utility Bill (>90d)",
      badge: "STATUTORY EXPIRATION",
      badgeColor: "bg-red-500/20 text-red-400 border-red-500/30",
      desc: "Bill dated 2025-10-31 is 257 days old relative to hackathon anchor 2026-07-15. Violates 90-day validity window.",
    },
    {
      id: "K03",
      title: "Applicant K03: Clean 100% Instant Approval",
      badge: "GOLDEN PATH",
      badgeColor: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
      desc: "Valid GSTIN, valid Udyam, fresh bill. High fuzzy match (100% proprietor title parsing). Instant APPROVAL in <200ms.",
    },
    {
      id: "NON_GST_KIRANA",
      title: "Non-GST Kirana: Micro-Bundle Pathway",
      badge: "BUSINESS IMPACT",
      badgeColor: "bg-blue-500/20 text-blue-400 border-blue-500/30",
      desc: "Attacks the 2.0% non-GST conversion gap. CPQ filters GST-only SKUs while allowing broadband + Wi-Fi to pass with Udyam.",
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
      alert(err instanceof Error ? err.message : "Failed to execute scenario");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Benchmark Header */}
      <div className="bg-slate-900 border border-amber-500/30 rounded-2xl p-6 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <Scale className="w-6 h-6 text-amber-400" />
              <h2 className="text-xl font-bold text-white tracking-tight">
                Hackathon Jury Test Bench &amp; Adversarial Verification Gate
              </h2>
            </div>
            <p className="text-xs text-slate-300 mt-1">
              Test real-world regulatory compliance edge cases, document discrepancies, and statutory constraints live against the running backend.
            </p>
          </div>
          <div className="flex items-center space-x-2 bg-slate-950 p-2.5 rounded-xl border border-slate-800 font-mono text-xs text-slate-300">
            <Cpu className="w-4 h-4 text-emerald-400" />
            <span>Anchor: 2026-07-15 | DPDP: In-Memory Mask</span>
          </div>
        </div>

        {/* 6 Scenario Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mt-6">
          {scenarios.map((sc) => {
            const isSelected = activeScenarioId === sc.id;
            return (
              <div
                key={sc.id}
                onClick={() => handleRunScenario(sc.id)}
                className={`p-4 rounded-xl border transition-all cursor-pointer relative ${
                  isSelected
                    ? "border-amber-400 bg-amber-950/20 shadow-lg shadow-amber-950/40"
                    : "border-slate-800 bg-slate-950/50 hover:border-slate-700"
                }`}
              >
                <div className="flex items-start justify-between">
                  <span className={`text-[9px] px-2 py-0.5 rounded-full font-bold border ${sc.badgeColor}`}>
                    {sc.badge}
                  </span>
                  <Play
                    className={`w-4 h-4 transition-transform ${
                      isSelected ? "text-amber-400 scale-110" : "text-slate-500"
                    }`}
                  />
                </div>
                <h4 className="text-xs font-bold text-white mt-2">{sc.title}</h4>
                <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">{sc.desc}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Execution Results & Live Telemetry Panel */}
      {scenarioData && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5 animate-in fade-in duration-200">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-2">
            <div>
              <span className="text-xs text-amber-400 font-mono font-bold">
                SCENARIO: {scenarioData.scenario_id}
              </span>
              <h3 className="text-base font-bold text-white">{scenarioData.title}</h3>
            </div>
            <div className="flex items-center space-x-3 text-xs font-mono">
              <span className="bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800 text-slate-300">
                Live End-to-End Latency: <strong className="text-emerald-400">{executionTimeMs}ms</strong>
              </span>
              <span
                className={`px-2.5 py-1 rounded-lg font-bold ${
                  scenarioData.verification_result?.status === "APPROVED"
                    ? "bg-emerald-500/20 text-emerald-400"
                    : scenarioData.verification_result?.status === "MANUAL_REVIEW"
                    ? "bg-amber-500/20 text-amber-400"
                    : "bg-red-500/20 text-red-400"
                }`}
              >
                STATUS: {scenarioData.verification_result?.status || "COMPLETED"}
              </span>
            </div>
          </div>

          {/* Expected vs Actual Behavior Comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800 space-y-2">
              <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
                <Layers className="w-4 h-4 text-blue-400" />
                <span>Architectural Law Enforced</span>
              </h4>
              <p className="text-xs text-slate-300 leading-relaxed font-sans">
                {scenarioData.expected_behavior}
              </p>
            </div>

            <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800 space-y-2">
              <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>Deterministic Verification Result</span>
              </h4>
              <p className="text-xs text-slate-300 leading-relaxed font-sans">
                {scenarioData.notes}
              </p>
            </div>
          </div>

          {/* Compliance Exceptions Caught */}
          {scenarioData.verification_result?.anomalies?.length > 0 && (
            <div className="p-4 rounded-xl bg-red-950/20 border border-red-500/30 space-y-2">
              <h4 className="text-xs font-bold text-red-400 uppercase tracking-wider flex items-center space-x-1.5">
                <AlertTriangle className="w-4 h-4" />
                <span>Compliance Exceptions Detected by Engine ({scenarioData.verification_result.anomalies.length})</span>
              </h4>
              <div className="space-y-1.5">
                {scenarioData.verification_result.anomalies.map((anom: KYCAnomaly, idx: number) => (
                  <div key={idx} className="text-xs text-slate-300 bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                    <span className="font-mono text-amber-400 font-bold">{anom.code}</span>: {anom.message}
                    {anom.remediation && (
                      <p className="text-[11px] text-emerald-400 mt-1">
                        ↳ Actionable UI Remediation: {anom.remediation}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Live JSON Payload Inspector for Judges */}
          <details className="bg-slate-950 rounded-xl border border-slate-800 p-3 text-xs">
            <summary className="cursor-pointer font-mono text-slate-400 hover:text-white flex items-center space-x-2">
              <Code className="w-4 h-4 text-slate-500" />
              <span>Inspect Raw Pydantic Verification Payload &amp; DPDP Audit Log</span>
            </summary>
            <pre className="mt-3 p-3 bg-slate-900 rounded-lg overflow-x-auto text-[11px] font-mono text-emerald-400 leading-relaxed border border-slate-800">
              {JSON.stringify(scenarioData, null, 2)}
            </pre>
          </details>
        </div>
      )}
    </div>
  );
};
