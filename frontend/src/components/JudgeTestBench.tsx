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
      badgeColor: "bg-airtel-crimson/15 text-airtel-crimson border-airtel-crimson/30",
      desc: "GSTIN cancelled on 2026-06-01 + Blank Udyam certificate. Engine rejects immediately with actionable non-GST fallback.",
    },
    {
      id: "K05",
      title: "Applicant K05: Missing Mandatory Document",
      badge: "MISSING DOCUMENT",
      badgeColor: "bg-amber-500/15 text-amber-300 border-amber-500/30",
      desc: "Udyam certificate file omitted from ingestion payload. Engine flags UDYAM_DOC_MISSING without crashing.",
    },
    {
      id: "K07",
      title: "Applicant K07: Entity Name Discrepancy",
      badge: "FUZZY MISMATCH",
      badgeColor: "bg-amber-500/15 text-amber-300 border-amber-500/30",
      desc: "Legal trade name differs from declared name in invoice (RapidFuzz token similarity < 70%).",
    },
    {
      id: "K11",
      title: "Applicant K11: Stale Utility Bill (>90d)",
      badge: "STATUTORY EXPIRATION",
      badgeColor: "bg-airtel-crimson/15 text-airtel-crimson border-airtel-crimson/30",
      desc: "Bill dated 2025-10-31 is 257 days old relative to hackathon anchor 2026-07-15. Violates 90-day validity window.",
    },
    {
      id: "K03",
      title: "Applicant K03: Clean 100% Instant Approval",
      badge: "GOLDEN PATH",
      badgeColor: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
      desc: "Valid GSTIN, valid Udyam, fresh bill. High fuzzy match (100% proprietor title parsing). Instant APPROVAL in <200ms.",
    },
    {
      id: "NON_GST_KIRANA",
      title: "Non-GST Kirana: Micro-Bundle Pathway",
      badge: "BUSINESS IMPACT",
      badgeColor: "bg-blue-500/15 text-blue-400 border-blue-500/30",
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
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in">
      {/* Benchmark Header */}
      <div className="glass-card rounded-2xl p-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-champagne-gold/5 rounded-full blur-3xl pointer-events-none" />
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-white/[0.06]">
          <div>
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-lg bg-champagne-gold/15 border border-champagne-gold/30 flex items-center justify-center text-champagne-gold">
                <Scale className="w-4 h-4" />
              </div>
              <h2 className="font-serif text-xl font-normal text-white tracking-tight">
                Hackathon Jury Test Bench &amp; Adversarial Verification Gate
              </h2>
            </div>
            <p className="text-xs text-white/60 mt-1.5 leading-relaxed max-w-2xl">
              Test real-world regulatory compliance edge cases, document discrepancies, and statutory constraints live against the running backend.
            </p>
          </div>

          <div className="flex items-center space-x-2 bg-obsidian-surface/80 p-2.5 rounded-xl border border-white/[0.08] font-mono text-xs text-white/70 self-start md:self-auto">
            <Cpu className="w-4 h-4 text-emerald-400" />
            <span>Anchor: 2026-07-15 | DPDP: In-Memory Mask</span>
          </div>
        </div>

        {/* 6 Scenario Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5 mt-6">
          {scenarios.map((sc) => {
            const isSelected = activeScenarioId === sc.id;
            return (
              <div
                key={sc.id}
                onClick={() => handleRunScenario(sc.id)}
                className={`p-4 rounded-xl border transition-all cursor-pointer relative group ${
                  isSelected
                    ? "border-champagne-gold/70 bg-champagne-gold/10 shadow-lg shadow-black/40"
                    : "border-white/[0.06] bg-obsidian-surface/60 hover:border-white/[0.18] hover:bg-obsidian-elevated/70"
                }`}
              >
                <div className="flex items-start justify-between">
                  <span className={`text-[9px] px-2 py-0.5 rounded-full font-mono font-medium border ${sc.badgeColor}`}>
                    {sc.badge}
                  </span>
                  <Play
                    className={`w-4 h-4 transition-transform ${
                      isSelected ? "text-champagne-gold scale-110" : "text-white/40 group-hover:text-white/70"
                    }`}
                  />
                </div>
                <h4 className="text-xs font-medium text-white mt-2.5">{sc.title}</h4>
                <p className="text-[11px] text-white/50 mt-1 leading-relaxed">{sc.desc}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Execution Results & Live Telemetry Panel */}
      {scenarioData && (
        <div className="glass-card rounded-2xl p-6 space-y-5 animate-fade-in">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-white/[0.06] gap-3">
            <div>
              <span className="text-xs text-champagne-gold font-mono font-medium">
                SCENARIO: {scenarioData.scenario_id}
              </span>
              <h3 className="font-serif text-lg font-normal text-white">{scenarioData.title}</h3>
            </div>
            <div className="flex items-center space-x-3 text-xs font-mono">
              <span className="bg-obsidian-surface/80 px-3 py-1 rounded-lg border border-white/[0.08] text-white/70">
                Live End-to-End Latency: <strong className="text-emerald-400 font-medium">{executionTimeMs}ms</strong>
              </span>
              <span
                className={`px-3 py-1 rounded-lg font-mono font-medium ${
                  scenarioData.verification_result?.status === "APPROVED"
                    ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                    : scenarioData.verification_result?.status === "MANUAL_REVIEW"
                    ? "bg-amber-500/15 text-amber-300 border border-amber-500/30"
                    : "bg-airtel-crimson/15 text-airtel-crimson border border-airtel-crimson/30"
                }`}
              >
                STATUS: {scenarioData.verification_result?.status || "COMPLETED"}
              </span>
            </div>
          </div>

          {/* Expected vs Actual Behavior Comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-obsidian-surface/60 p-4 rounded-xl border border-white/[0.06] space-y-2">
              <h4 className="text-xs font-mono font-medium text-white/70 uppercase tracking-wider flex items-center space-x-1.5">
                <Layers className="w-4 h-4 text-blue-400" />
                <span>Architectural Law Enforced</span>
              </h4>
              <p className="text-xs text-white/70 leading-relaxed font-sans">
                {scenarioData.expected_behavior}
              </p>
            </div>

            <div className="bg-obsidian-surface/60 p-4 rounded-xl border border-white/[0.06] space-y-2">
              <h4 className="text-xs font-mono font-medium text-white/70 uppercase tracking-wider flex items-center space-x-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>Deterministic Verification Result</span>
              </h4>
              <p className="text-xs text-white/70 leading-relaxed font-sans">
                {scenarioData.notes}
              </p>
            </div>
          </div>

          {/* Compliance Exceptions Caught */}
          {scenarioData.verification_result?.anomalies?.length > 0 && (
            <div className="p-4 rounded-xl bg-airtel-crimson/10 border border-airtel-crimson/30 space-y-2.5">
              <h4 className="text-xs font-serif text-airtel-crimson font-medium uppercase tracking-wider flex items-center space-x-1.5">
                <AlertTriangle className="w-4 h-4" />
                <span>Compliance Exceptions Detected by Engine ({scenarioData.verification_result.anomalies.length})</span>
              </h4>
              <div className="space-y-2">
                {scenarioData.verification_result.anomalies.map((anom: KYCAnomaly, idx: number) => (
                  <div key={idx} className="text-xs text-white/80 bg-obsidian-canvas/60 p-3 rounded-lg border border-white/[0.06]">
                    <span className="font-mono text-amber-300 font-medium">{anom.code}</span>: {anom.message}
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
          <details className="bg-obsidian-surface/60 rounded-xl border border-white/[0.06] p-3 text-xs">
            <summary className="cursor-pointer font-mono text-white/50 hover:text-white flex items-center space-x-2">
              <Code className="w-4 h-4 text-white/40" />
              <span>Inspect Raw Pydantic Verification Payload &amp; DPDP Audit Log</span>
            </summary>
            <pre className="mt-3 p-4 bg-obsidian-canvas/90 rounded-lg overflow-x-auto text-[11px] font-mono text-emerald-400 leading-relaxed border border-white/[0.06]">
              {JSON.stringify(scenarioData, null, 2)}
            </pre>
          </details>
        </div>
      )}
    </div>
  );
};
