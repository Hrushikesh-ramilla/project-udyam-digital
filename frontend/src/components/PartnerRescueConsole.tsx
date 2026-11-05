import React, { useState, useEffect } from "react";
import {
  BarChart3,
  TrendingDown,
  TrendingUp,
  AlertCircle,
  ExternalLink,
  MessageSquare,
  Users,
  Percent,
  Clock,
  DollarSign,
  Search,
  Filter,
  Shield,
  Zap,
} from "lucide-react";
import { LeadRescueItem } from "../types";
import { fetchRescueLeads } from "../api";

interface PartnerRescueConsoleProps {
  onLoadOBOLead?: (lead: LeadRescueItem) => void;
}

export const PartnerRescueConsole: React.FC<PartnerRescueConsoleProps> = ({ onLoadOBOLead }) => {
  const [leads, setLeads] = useState<LeadRescueItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [filterSegment, setFilterSegment] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await fetchRescueLeads();
      setLeads(data);
      setLoading(false);
    }
    load();
  }, []);

  const filteredLeads = leads.filter((lead) => {
    const matchesSegment = filterSegment === "ALL" || lead.segment.includes(filterSegment);
    const matchesSearch =
      lead.business_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      lead.lead_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      lead.city.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSegment && matchesSearch;
  });

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-fade-in">
      {/* Executive Telemetry & Funnel Diagnostic Banner */}
      <div className="glass-card rounded-2xl p-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-airtel-crimson/5 rounded-full blur-3xl pointer-events-none" />
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-white/[0.06]">
          <div>
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-lg bg-airtel-crimson/15 border border-airtel-crimson/30 flex items-center justify-center text-airtel-crimson">
                <BarChart3 className="w-4 h-4" />
              </div>
              <h2 className="font-serif text-xl font-normal text-white tracking-tight">
                Partner Console &amp; LightGBM Lead Rescue Engine
              </h2>
            </div>
            <p className="text-xs text-white/60 mt-1.5 leading-relaxed max-w-2xl">
              Real-time telemetry from 5,000 historical leads (`smb_leads.csv`). Machine-learned propensity scoring to rescue the 56% quote drop-off cohort.
            </p>
          </div>
          <span className="text-[11px] font-mono bg-airtel-crimson/10 text-airtel-crimson border border-airtel-crimson/30 px-3 py-1 rounded-full font-medium self-start md:self-auto">
            LightGBM Trained (scale_pos_weight: 12.58)
          </span>
        </div>

        {/* 4 Macro KPI Cards Targeting Hackathon Telemetry */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
          <div className="bg-obsidian-surface/60 p-4 rounded-xl border border-white/[0.06] hover:border-white/[0.14] transition-all">
            <div className="flex items-center justify-between text-xs text-white/50">
              <span>Primary Funnel Leak</span>
              <TrendingDown className="w-4 h-4 text-airtel-crimson" />
            </div>
            <div className="font-serif text-3xl font-medium text-airtel-crimson mt-2 tracking-tight">56.4% Drop-Off</div>
            <p className="text-[10px] text-white/40 mt-1">
              1,974 Needs Assessed → 861 Accepted (1,113 leads lost to PDF friction)
            </p>
          </div>

          <div className="bg-obsidian-surface/60 p-4 rounded-xl border border-white/[0.06] hover:border-white/[0.14] transition-all">
            <div className="flex items-center justify-between text-xs text-white/50">
              <span>Non-GST Conversion Gap</span>
              <Percent className="w-4 h-4 text-amber-400" />
            </div>
            <div className="font-serif text-3xl font-medium text-amber-400 mt-2 tracking-tight">2.0% vs 9.6%</div>
            <p className="text-[10px] text-white/40 mt-1">
              Non-GST leads dropped when pitched GST-mandatory corporate bundles
            </p>
          </div>

          <div className="bg-obsidian-surface/60 p-4 rounded-xl border border-white/[0.06] hover:border-white/[0.14] transition-all">
            <div className="flex items-center justify-between text-xs text-white/50">
              <span>Avg Activation Delay</span>
              <Clock className="w-4 h-4 text-blue-400" />
            </div>
            <div className="font-serif text-3xl font-medium text-blue-400 mt-2 tracking-tight">17.6 Days</div>
            <p className="text-[10px] text-white/40 mt-1">
              98 high-intent leads cancelled after waiting &gt;21 days
            </p>
          </div>

          <div className="bg-obsidian-surface/60 p-4 rounded-xl border border-white/[0.06] hover:border-white/[0.14] transition-all">
            <div className="flex items-center justify-between text-xs text-white/50">
              <span>Blended Customer CAC</span>
              <DollarSign className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="font-serif text-3xl font-medium text-emerald-400 mt-2 tracking-tight">₹15,000</div>
            <p className="text-[10px] text-white/40 mt-1">
              Target CAC: &lt;₹3,500 with zero-visit digital WhatsApp onboarding
            </p>
          </div>
        </div>
      </div>

      {/* LightGBM Rescue Leads Table */}
      <div className="glass-card rounded-2xl p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-white/[0.06]">
          <div>
            <h3 className="font-serif text-base font-normal text-white flex items-center space-x-2">
              <Zap className="w-4 h-4 text-airtel-crimson" />
              <span>High-Propensity Rescuable Leads (56% Drop-off Cohort)</span>
            </h3>
            <p className="text-xs text-white/50 mt-1">
              Ranked by LightGBM machine learning classifier trained on 5,000 historical rows with SHAP risk attribution.
            </p>
          </div>

          {/* Search & Filter Controls */}
          <div className="flex items-center space-x-2">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-white/40 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search business, city..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-obsidian-canvas/60 border border-white/[0.08] rounded-xl pl-8 pr-3 py-1.5 text-xs text-white placeholder-white/40 focus:outline-none focus:border-airtel-crimson w-44 sm:w-56"
              />
            </div>
            <select
              value={filterSegment}
              onChange={(e) => setFilterSegment(e.target.value)}
              className="bg-obsidian-canvas/60 border border-white/[0.08] rounded-xl px-3 py-1.5 text-xs text-white/80 focus:outline-none focus:border-airtel-crimson cursor-pointer"
            >
              <option value="ALL">All Segments</option>
              <option value="Retail">Retail</option>
              <option value="Kirana">Kirana</option>
              <option value="Manufacturing">Manufacturing</option>
              <option value="Services">Services</option>
            </select>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-white/70">
            <thead className="bg-obsidian-surface/60 text-white/40 uppercase font-mono text-[10px] border-b border-white/[0.06]">
              <tr>
                <th className="py-3 px-3">Lead &amp; Segment</th>
                <th className="py-3 px-3">Location &amp; Spend</th>
                <th className="py-3 px-3">Drop-Off Reason</th>
                <th className="py-3 px-3">LightGBM Propensity</th>
                <th className="py-3 px-3">Risk Factor Attribution</th>
                <th className="py-3 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.04]">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-white/40 font-mono">
                    Loading machine learning rescue cohort...
                  </td>
                </tr>
              ) : filteredLeads.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-white/40 font-mono">
                    No matching leads found.
                  </td>
                </tr>
              ) : (
                filteredLeads.map((lead) => (
                  <tr key={lead.lead_id} className="hover:bg-white/[0.02] transition-all">
                    <td className="py-3.5 px-3">
                      <div className="font-medium text-white">{lead.business_name}</div>
                      <div className="flex items-center space-x-1.5 text-[10px] text-white/40 mt-0.5">
                        <span className="font-mono">{lead.lead_id}</span>
                        <span>•</span>
                        <span>{lead.segment}</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-3">
                      <div className="text-white/80">
                        {lead.city}{" "}
                        <span className="text-[10px] text-white/40 font-mono">
                          (T{lead.city_tier})
                        </span>
                      </div>
                      <div className="text-[10px] text-white/50 font-mono mt-0.5">
                        ₹{lead.monthly_spend_inr.toLocaleString()} / mo
                      </div>
                    </td>
                    <td className="py-3.5 px-3">
                      <span className="text-[11px] text-white/80 font-medium">
                        {lead.drop_reason || "Quote Pending"}
                      </span>
                      <span className="block text-[9px] text-white/40 mt-0.5">
                        Stage: {lead.stage_reached}
                      </span>
                    </td>
                    <td className="py-3.5 px-3">
                      <div className="flex items-center space-x-2">
                        {(() => {
                          const scoreVal = lead.propensity_score > 1.0 ? lead.propensity_score : lead.propensity_score * 100;
                          return (
                            <span
                              className={`font-mono font-medium text-sm ${
                                scoreVal >= 70
                                  ? "text-emerald-400"
                                  : scoreVal >= 40
                                  ? "text-amber-400"
                                  : "text-white/40"
                              }`}
                            >
                              {scoreVal.toFixed(1)}%
                            </span>
                          );
                        })()}
                        <span
                          className={`text-[9px] px-2 py-0.5 rounded-full font-mono uppercase ${
                            lead.priority_tier === "HIGH"
                              ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                              : lead.priority_tier === "MEDIUM"
                              ? "bg-amber-500/15 text-amber-400 border border-amber-500/30"
                              : "bg-white/[0.04] text-white/40 border border-white/[0.06]"
                          }`}
                        >
                          {lead.priority_tier}
                        </span>
                      </div>
                    </td>
                    <td className="py-3.5 px-3">
                      <div className="flex flex-wrap gap-1 max-w-xs">
                        {lead.top_risk_factors.map((risk, idx) => (
                          <span
                            key={idx}
                            className="text-[9px] bg-obsidian-canvas/60 border border-white/[0.06] text-white/50 px-1.5 py-0.5 rounded font-mono"
                          >
                            {risk.replace("DROP_REASON_", "")}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="py-3.5 px-3 text-right">
                      <a
                        href={lead.whatsapp_rescue_link}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center space-x-1.5 bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-1.5 px-3 rounded-lg text-xs transition-all shadow-sm shadow-emerald-950/30 cursor-pointer"
                      >
                        <MessageSquare className="w-3.5 h-3.5" />
                        <span>Send NBA Link</span>
                      </a>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
