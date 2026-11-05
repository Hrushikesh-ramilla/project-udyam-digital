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
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Executive Telemetry & Funnel Diagnostic Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800">
          <div>
            <div className="flex items-center space-x-2">
              <BarChart3 className="w-6 h-6 text-red-500" />
              <h2 className="text-xl font-bold text-white tracking-tight">
                Partner Console &amp; LightGBM Lead Rescue Engine
              </h2>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Real-time telemetry from 5,000 historical leads (`smb_leads.csv`). Machine-learned propensity scoring to rescue the 56% quote drop-off cohort.
            </p>
          </div>
          <span className="text-xs bg-red-500/20 text-red-400 border border-red-500/30 px-3 py-1 rounded-full font-mono font-bold self-start md:self-auto">
            LightGBM Trained (scale_pos_weight: 12.58)
          </span>
        </div>

        {/* 4 Macro KPI Cards Targeting Hackathon Telemetry */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
          <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Primary Funnel Leak</span>
              <TrendingDown className="w-4 h-4 text-red-400" />
            </div>
            <div className="text-2xl font-black text-red-500 mt-1">56.4% Drop-Off</div>
            <p className="text-[10px] text-slate-500 mt-0.5">
              1,974 Needs Assessed → 861 Accepted (1,113 leads lost to PDF friction)
            </p>
          </div>

          <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Non-GST Conversion Gap</span>
              <Percent className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-2xl font-black text-amber-400 mt-1">2.0% vs 9.6%</div>
            <p className="text-[10px] text-slate-500 mt-0.5">
              Non-GST leads dropped when pitched GST-mandatory corporate bundles
            </p>
          </div>

          <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Avg Activation Delay</span>
              <Clock className="w-4 h-4 text-blue-400" />
            </div>
            <div className="text-2xl font-black text-blue-400 mt-1">17.6 Days</div>
            <p className="text-[10px] text-slate-500 mt-0.5">
              98 high-intent leads cancelled after waiting &gt;21 days
            </p>
          </div>

          <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Blended Customer CAC</span>
              <DollarSign className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-black text-emerald-400 mt-1">₹15,000</div>
            <p className="text-[10px] text-slate-500 mt-0.5">
              Target CAC: &lt;₹3,500 with zero-visit digital WhatsApp onboarding
            </p>
          </div>
        </div>
      </div>

      {/* LightGBM Rescue Leads Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2">
              <Zap className="w-4 h-4 text-red-500" />
              <span>High-Propensity Rescuable Leads (56% Drop-off Cohort)</span>
            </h3>
            <p className="text-xs text-slate-400">
              Ranked by LightGBM machine learning classifier trained on 5,000 historical rows with SHAP risk attribution.
            </p>
          </div>

          {/* Search & Filter Controls */}
          <div className="flex items-center space-x-2">
            <div className="relative">
              <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search business, city..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-red-500 w-44 sm:w-56"
              />
            </div>
            <select
              value={filterSegment}
              onChange={(e) => setFilterSegment(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none focus:border-red-500"
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
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950/80 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-3 px-3">Lead &amp; Segment</th>
                <th className="py-3 px-3">Location &amp; Spend</th>
                <th className="py-3 px-3">Drop-Off Reason</th>
                <th className="py-3 px-3">LightGBM Propensity</th>
                <th className="py-3 px-3">Risk Factor Attribution</th>
                <th className="py-3 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-500">
                    Loading machine learning rescue cohort...
                  </td>
                </tr>
              ) : filteredLeads.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-500">
                    No matching leads found.
                  </td>
                </tr>
              ) : (
                filteredLeads.map((lead) => (
                  <tr key={lead.lead_id} className="hover:bg-slate-800/30 transition-all">
                    <td className="py-3 px-3">
                      <div className="font-bold text-white">{lead.business_name}</div>
                      <div className="flex items-center space-x-1.5 text-[10px] text-slate-400">
                        <span className="font-mono">{lead.lead_id}</span>
                        <span>•</span>
                        <span>{lead.segment}</span>
                      </div>
                    </td>
                    <td className="py-3 px-3">
                      <div>
                        {lead.city}{" "}
                        <span className="text-[10px] text-slate-500 font-mono">
                          (T{lead.city_tier})
                        </span>
                      </div>
                      <div className="text-[10px] text-slate-400 font-mono">
                        ₹{lead.monthly_spend_inr.toLocaleString()} / mo
                      </div>
                    </td>
                    <td className="py-3 px-3">
                      <span className="text-[11px] text-slate-300">
                        {lead.drop_reason || "Quote Pending"}
                      </span>
                      <span className="block text-[9px] text-slate-500">
                        Stage: {lead.stage_reached}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      <div className="flex items-center space-x-2">
                        {(() => {
                          const scoreVal = lead.propensity_score > 1.0 ? lead.propensity_score : lead.propensity_score * 100;
                          return (
                            <span
                              className={`font-mono font-bold text-sm ${
                                scoreVal >= 70
                                  ? "text-emerald-400"
                                  : scoreVal >= 40
                                  ? "text-amber-400"
                                  : "text-slate-400"
                              }`}
                            >
                              {scoreVal.toFixed(1)}%
                            </span>
                          );
                        })()}
                        <span
                          className={`text-[9px] px-1.5 py-0.5 rounded font-bold uppercase ${
                            lead.priority_tier === "HIGH"
                              ? "bg-emerald-500/20 text-emerald-400"
                              : lead.priority_tier === "MEDIUM"
                              ? "bg-amber-500/20 text-amber-400"
                              : "bg-slate-800 text-slate-400"
                          }`}
                        >
                          {lead.priority_tier}
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-3">
                      <div className="flex flex-wrap gap-1 max-w-xs">
                        {lead.top_risk_factors.map((risk, idx) => (
                          <span
                            key={idx}
                            className="text-[9px] bg-slate-950 border border-slate-800 text-slate-400 px-1.5 py-0.5 rounded"
                          >
                            {risk.replace("DROP_REASON_", "")}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="py-3 px-3 text-right">
                      <a
                        href={lead.whatsapp_rescue_link}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center space-x-1.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-1.5 px-3 rounded-lg text-xs transition-all shadow-sm shadow-emerald-600/30"
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
