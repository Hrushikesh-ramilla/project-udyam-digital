import React, { useState, useEffect } from "react";
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
  Activity,
  Cpu,
  Database,
  Lock,
  Zap,
  BarChart3,
  Calendar,
} from "lucide-react";
import { fetchJudgeScenario, fetchLiveBenchmarks } from "../api";
import { JudgeScenarioResult, LiveBenchmarkResult } from "../types";

export const JudgeTestBench: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"benchmarks" | "scenarios">("benchmarks");

  // Benchmarks state
  const [benchmarksRunning, setBenchmarksRunning] = useState<boolean>(false);
  const [benchmarkData, setBenchmarkData] = useState<LiveBenchmarkResult | null>(null);

  // Scenarios state
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
      title: "Applicant K03: Clean Golden Path",
      badge: "GOLDEN PATH",
      desc: "Valid GSTIN, valid Udyam, fresh bill. 100% RapidFuzz score. Approved in <2ms.",
    },
    {
      id: "NON_GST_KIRANA",
      title: "Non-GST Kirana: Micro-Bundle",
      badge: "2.0% GAP SOLVER",
      desc: "Filters GST-only SKUs, allowing broadband + Wi-Fi to pass with Udyam.",
    },
    {
      id: "K02",
      title: "Applicant K02: Harmony Dental Care",
      badge: "ACTIVE CLINIC",
      desc: "Kolkata medical clinic with active GSTIN & Udyam registration.",
    },
    {
      id: "K04",
      title: "Applicant K04: Saffron Dental Care LLP",
      badge: "ACTIVE LLP",
      desc: "Nagpur dental hospital verified with fresh utility bill and valid credentials.",
    },
    {
      id: "K06",
      title: "Applicant K06: Saffron Unisex Salon",
      badge: "ACTIVE SALON",
      desc: "Delhi retail salon verified for high-speed fiber connectivity bundle.",
    },
    {
      id: "K08",
      title: "Applicant K08: Green Leaf Legal Associates",
      badge: "ACTIVE LAW FIRM",
      desc: "Vadodara professional law office requiring dedicated leased line & SLA.",
    },
    {
      id: "K09",
      title: "Applicant K09: Kaveri Insurance Advisors",
      badge: "ACTIVE ADVISORY",
      desc: "Visakhapatnam insurance consultancy verified with 100% statutory match.",
    },
    {
      id: "K10",
      title: "Applicant K10: Kaveri Stays LLP",
      badge: "ACTIVE HOSPITALITY",
      desc: "Mumbai multi-site boutique stay enterprise passing full KYC verification.",
    },
    {
      id: "K12",
      title: "Applicant K12: Star Electronics",
      badge: "VERIFIED RETAIL",
      desc: "Visakhapatnam multi-store retail chain approved for enterprise fiber & IoT.",
    },
  ];

  const handleRunBenchmarks = async () => {
    setBenchmarksRunning(true);
    try {
      const data = await fetchLiveBenchmarks();
      setBenchmarkData(data);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Live benchmark failed");
    } finally {
      setBenchmarksRunning(false);
    }
  };

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

  // Run benchmarks automatically on initial load
  useEffect(() => {
    handleRunBenchmarks();
  }, []);

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
              Jury Evidence &amp; System Audit Lab
            </h2>
            <p className="text-xs text-slate-300 mt-0.5">
              Live microsecond execution benchmarks, LightGBM model card, and statutory anomaly verification
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="font-mono text-xs text-amber-400 bg-slate-900/90 px-3.5 py-1.5 rounded-full border border-slate-700/80">
            Anchor Date: 2026-07-15
          </div>
        </div>
      </div>

      {/* Lab Mode Toggle Navigation */}
      <div className="flex space-x-2 border-b border-slate-800 pb-3">
        <button
          onClick={() => setActiveTab("benchmarks")}
          className={`flex items-center space-x-2 px-4 py-2.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
            activeTab === "benchmarks"
              ? "bg-[#e40000] text-white shadow-[0_0_16px_rgba(228,0,0,0.4)]"
              : "bg-slate-900 text-slate-400 hover:text-white border border-slate-800"
          }`}
        >
          <Zap className="w-3.5 h-3.5" />
          <span>Live Microsecond Benchmarks &amp; Model Card</span>
        </button>
        <button
          onClick={() => setActiveTab("scenarios")}
          className={`flex items-center space-x-2 px-4 py-2.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
            activeTab === "scenarios"
              ? "bg-[#e40000] text-white shadow-[0_0_16px_rgba(228,0,0,0.4)]"
              : "bg-slate-900 text-slate-400 hover:text-white border border-slate-800"
          }`}
        >
          <ShieldAlert className="w-3.5 h-3.5" />
          <span>Statutory KYC Edge Cases (12 Benchmark Applicants)</span>
        </button>
      </div>

      {/* TAB 1: LIVE BENCHMARKS & MODEL CARD */}
      {activeTab === "benchmarks" && (
        <div className="space-y-6">
          {/* Action Trigger Card */}
          <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-700 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Activity className="w-4 h-4 text-emerald-400" />
                Live Deterministic Microsecond Verification
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Executes live queries directly across CPQ topological DAG solver, branch-and-bound optimizer, SHA-256 byte cache KYC engine, SQLite WAL persistence, and LightGBM classifier.
              </p>
            </div>
            <motion.button
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              onClick={handleRunBenchmarks}
              disabled={benchmarksRunning}
              className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-bold rounded-xl flex items-center space-x-2 shadow-[0_0_20px_rgba(16,185,129,0.3)] cursor-pointer shrink-0"
            >
              <Zap className="w-4 h-4" />
              <span>{benchmarksRunning ? "Executing Live Benchmarks..." : "Re-Run Live Benchmarks"}</span>
            </motion.button>
          </div>

          {/* Latency Dashboard */}
          {benchmarkData && (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
              <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-700/80 space-y-1">
                <span className="text-[10px] text-slate-400 font-mono uppercase tracking-wider block">CPQ DAG Solver</span>
                <div className="text-xl sm:text-2xl font-black text-emerald-400 font-mono">
                  {benchmarkData.benchmarks.cpq_dag_solver_ms} ms
                </div>
                <span className="text-[10px] text-slate-500 font-sans block">Target: &lt;50.0ms</span>
              </div>

              <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-700/80 space-y-1">
                <span className="text-[10px] text-slate-400 font-mono uppercase tracking-wider block">Mera Budget B&amp;B</span>
                <div className="text-xl sm:text-2xl font-black text-emerald-400 font-mono">
                  {benchmarkData.benchmarks.reverse_budget_optimizer_ms} ms
                </div>
                <span className="text-[10px] text-slate-500 font-sans block">Branch-and-bound</span>
              </div>

              <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-700/80 space-y-1">
                <span className="text-[10px] text-slate-400 font-mono uppercase tracking-wider block">Smart KYC Engine</span>
                <div className="text-xl sm:text-2xl font-black text-emerald-400 font-mono">
                  {benchmarkData.benchmarks.kyc_anomaly_engine_ms} ms
                </div>
                <span className="text-[10px] text-slate-500 font-sans block">Target: &lt;250.0ms</span>
              </div>

              <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-700/80 space-y-1">
                <span className="text-[10px] text-slate-400 font-mono uppercase tracking-wider block">SQLite WAL Query</span>
                <div className="text-xl sm:text-2xl font-black text-cyan-400 font-mono">
                  {benchmarkData.benchmarks.sqlite_wal_persistence_ms} ms
                </div>
                <span className="text-[10px] text-slate-500 font-sans block">Sub-millisecond</span>
              </div>

              <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-700/80 space-y-1">
                <span className="text-[10px] text-slate-400 font-mono uppercase tracking-wider block">LightGBM Model</span>
                <div className="text-xl sm:text-2xl font-black text-amber-400 font-mono">
                  {benchmarkData.benchmarks.lightgbm_inference_ms} ms
                </div>
                <span className="text-[10px] text-slate-500 font-sans block">Batch Inference</span>
              </div>
            </div>
          )}

          {/* Model Card & Enterprise Architecture Invariants */}
          {benchmarkData && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {/* LightGBM Model Card */}
              <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-700 space-y-3.5">
                <div className="flex items-center space-x-2 text-amber-400">
                  <BarChart3 className="w-4 h-4" />
                  <h4 className="text-sm font-bold text-white uppercase tracking-wider">
                    Machine Learning Model Card (Lead Winback)
                  </h4>
                </div>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between py-1 border-b border-slate-800">
                    <span className="text-slate-400">Classifier Architecture:</span>
                    <span className="text-white font-mono font-semibold">{benchmarkData.model_card.model_type}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-800">
                    <span className="text-slate-400">Validated Test AUC:</span>
                    <span className="text-emerald-400 font-mono font-bold">{benchmarkData.model_card.test_auc}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-800">
                    <span className="text-slate-400">Dataset Size &amp; Class Imbalance:</span>
                    <span className="text-white font-mono">{benchmarkData.model_card.dataset_rows} leads ({benchmarkData.model_card.class_imbalance_ratio}x weight)</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-800">
                    <span className="text-slate-400">Top Quintile Winback Rate:</span>
                    <span className="text-emerald-400 font-mono font-semibold">{benchmarkData.model_card.top_quintile_conversion_rate}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-800">
                    <span className="text-slate-400">Marginal Customer Acquisition Cost:</span>
                    <span className="text-emerald-400 font-mono font-bold">{benchmarkData.model_card.marginal_cac}</span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span className="text-slate-400">Recoverable ARR Potential:</span>
                    <span className="text-amber-400 font-mono font-bold">{benchmarkData.model_card.recovered_arr_potential}</span>
                  </div>
                </div>
              </div>

              {/* System Invariants Card */}
              <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-700 space-y-3.5">
                <div className="flex items-center space-x-2 text-cyan-400">
                  <Lock className="w-4 h-4" />
                  <h4 className="text-sm font-bold text-white uppercase tracking-wider">
                    Statutory &amp; System Invariants
                  </h4>
                </div>
                <div className="space-y-2 text-xs">
                  <div className="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800 space-y-1">
                    <span className="text-cyan-400 font-mono text-[10.5px] uppercase font-bold block">DPDP Act 2023 Shield</span>
                    <p className="text-slate-300 text-[11px] leading-relaxed">
                      {benchmarkData.system_invariants.dpdp_act_compliance}. Zero persistence to disk or SQLite database.
                    </p>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800 space-y-1">
                    <span className="text-cyan-400 font-mono text-[10.5px] uppercase font-bold block">Anchored Freshness Clock</span>
                    <p className="text-slate-300 text-[11px] leading-relaxed">
                      Deterministic anchor: <strong className="text-white">{benchmarkData.system_invariants.evaluation_anchor_date}</strong>. Traps stale utility bills (&gt;90 days old).
                    </p>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800 space-y-1">
                    <span className="text-cyan-400 font-mono text-[10.5px] uppercase font-bold block">GSTIN Firewall &amp; Language Inertia</span>
                    <p className="text-slate-300 text-[11px] leading-relaxed">
                      {benchmarkData.system_invariants.gstin_firewall_status}. {benchmarkData.system_invariants.session_language_inertia}.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: STATUTORY KYC SCENARIOS (ALL 12 APPLICANTS) */}
      {activeTab === "scenarios" && (
        <div className="space-y-6">
          {/* Scenario Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {scenarios.map((sc) => {
              const isSelected = activeScenarioId === sc.id;
              return (
                <motion.div
                  key={sc.id}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => handleRunScenario(sc.id)}
                  className={`p-3.5 rounded-2xl border transition-all cursor-pointer ${
                    isSelected
                      ? "border-[#d9ad63] bg-[#d9ad63]/10 shadow-[0_0_24px_rgba(217,173,99,0.2)]"
                      : "border-slate-800 bg-slate-900/80 hover:border-slate-700"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[9px] px-2 py-0.5 rounded-full font-mono uppercase font-semibold border border-slate-700/80 text-white bg-white/[0.04]">
                      {sc.badge}
                    </span>
                    <Play
                      className={`w-3.5 h-3.5 transition-colors ${
                        isSelected ? "text-amber-400" : "text-slate-500"
                      }`}
                    />
                  </div>
                  <h4 className="text-xs font-semibold text-white truncate">{sc.title}</h4>
                  <p className="text-[10.5px] text-slate-400 mt-1.5 leading-relaxed line-clamp-2">{sc.desc}</p>
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
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
                <h3 className="text-lg sm:text-xl font-bold text-white tracking-tight">
                  {scenarioData.scenario_id}: {scenarioData.title}
                </h3>
                <div className="flex items-center space-x-2.5 text-xs font-mono">
                  <span className="text-slate-400">Execution Latency: {executionTimeMs}ms</span>
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
                  <span className="text-amber-400 font-mono text-[10px] uppercase tracking-wider block">Engine Diagnostic Output:</span>
                  <p className="text-white leading-relaxed">{scenarioData.notes}</p>
                </div>
              </div>

              {scenarioData.remediation && (
                <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs flex items-center gap-2 text-amber-300">
                  <Sparkles className="w-4 h-4 text-amber-400 shrink-0" />
                  <span><strong>Actionable Remediation:</strong> {scenarioData.remediation}</span>
                </div>
              )}

              <details className="text-xs bg-slate-900/90 p-4 rounded-2xl border border-slate-700">
                <summary className="cursor-pointer font-mono text-slate-400 hover:text-white select-none">
                  Inspect Raw Pydantic Payload (Strict ConfigDict Verification)
                </summary>
                <pre className="mt-3 text-[10px] font-mono text-emerald-400 overflow-x-auto p-3 bg-black/40 rounded-xl max-h-60">
                  {JSON.stringify(scenarioData, null, 2)}
                </pre>
              </details>
            </motion.div>
          )}
        </div>
      )}
    </div>
  );
};
