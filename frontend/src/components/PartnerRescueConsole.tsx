import React, { useState, useEffect } from "react";
import { motion } from "motion/react";
import {
  BarChart3,
  TrendingDown,
  Percent,
  Clock,
  DollarSign,
  Search,
  MessageSquare,
  Zap,
} from "lucide-react";
import { LeadRescueItem } from "../types";
import { fetchRescueLeads } from "../api";

export const PartnerRescueConsole: React.FC = () => {
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
    <div className="max-w-6xl mx-auto space-y-5">
      {/* 4 Macro KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div className="luxury-glass p-4 rounded-xl border border-[rgba(235,229,217,0.06)] space-y-1">
          <div className="flex items-center justify-between text-xs text-[#B39D82]">
            <span>Quote Drop-Off</span>
            <TrendingDown className="w-3.5 h-3.5 text-[#e40000]" />
          </div>
          <div className="font-serif text-3xl font-normal text-[#e40000] tracking-tight">56.4%</div>
          <p className="text-[10px] text-[#B39D82]/60 font-mono">1,113 leads lost to PDF delays</p>
        </div>

        <div className="luxury-glass p-4 rounded-xl border border-[rgba(235,229,217,0.06)] space-y-1">
          <div className="flex items-center justify-between text-xs text-[#B39D82]">
            <span>Non-GST Gap</span>
            <Percent className="w-3.5 h-3.5 text-[#d9ad63]" />
          </div>
          <div className="font-serif text-3xl font-normal text-[#d9ad63] tracking-tight">2.0%</div>
          <p className="text-[10px] text-[#B39D82]/60 font-mono">Vs 9.6% GST-registered rate</p>
        </div>

        <div className="luxury-glass p-4 rounded-xl border border-[rgba(235,229,217,0.06)] space-y-1">
          <div className="flex items-center justify-between text-xs text-[#B39D82]">
            <span>Activation SLA</span>
            <Clock className="w-3.5 h-3.5 text-blue-400" />
          </div>
          <div className="font-serif text-3xl font-normal text-blue-400 tracking-tight">17.6d</div>
          <p className="text-[10px] text-[#B39D82]/60 font-mono">Historical manual backlog</p>
        </div>

        <div className="luxury-glass p-4 rounded-xl border border-[rgba(235,229,217,0.06)] space-y-1">
          <div className="flex items-center justify-between text-xs text-[#B39D82]">
            <span>Customer CAC</span>
            <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
          </div>
          <div className="font-serif text-3xl font-normal text-emerald-400 tracking-tight">₹15,000</div>
          <p className="text-[10px] text-[#B39D82]/60 font-mono">Target: &lt;₹3,500 digital CAC</p>
        </div>
      </div>

      {/* Table Card */}
      <div className="luxury-glass rounded-2xl p-5 space-y-4 border border-[rgba(235,229,217,0.06)] shadow-apple-card">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-[rgba(235,229,217,0.06)]">
          <div className="flex items-center space-x-2">
            <Zap className="w-4 h-4 text-[#e40000]" />
            <h3 className="font-sans text-sm font-semibold text-[#EBE5D9]">
              High-Propensity Rescuable Leads (LightGBM)
            </h3>
          </div>

          <div className="flex items-center space-x-2">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-[#B39D82] absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-[#030405] border border-[rgba(235,229,217,0.06)] rounded-xl pl-8 pr-3 py-1 text-xs text-[#EBE5D9] placeholder-[#B39D82]/40 focus:outline-none focus:border-[#e40000] w-40 sm:w-48"
              />
            </div>
            <select
              value={filterSegment}
              onChange={(e) => setFilterSegment(e.target.value)}
              className="bg-[#030405] border border-[rgba(235,229,217,0.06)] rounded-xl px-2.5 py-1 text-xs text-[#EBE5D9] focus:outline-none cursor-pointer"
            >
              <option value="ALL">All</option>
              <option value="Retail">Retail</option>
              <option value="Kirana">Kirana</option>
              <option value="Manufacturing">Manufacturing</option>
            </select>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-[#EBE5D9]">
            <thead className="bg-[#030405] text-[#B39D82] uppercase font-mono text-[9px] border-b border-[rgba(235,229,217,0.04)]">
              <tr>
                <th className="py-2.5 px-3">Lead</th>
                <th className="py-2.5 px-3">City &amp; Spend</th>
                <th className="py-2.5 px-3">Drop-Off Reason</th>
                <th className="py-2.5 px-3">Propensity</th>
                <th className="py-2.5 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[rgba(235,229,217,0.04)]">
              {loading ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-[#B39D82] font-mono">
                    Loading ML predictions...
                  </td>
                </tr>
              ) : filteredLeads.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-[#B39D82]">
                    No leads found.
                  </td>
                </tr>
              ) : (
                filteredLeads.map((lead) => {
                  const scoreVal = lead.propensity_score > 1.0 ? lead.propensity_score : lead.propensity_score * 100;
                  return (
                    <tr key={lead.lead_id} className="hover:bg-white/[0.02] transition-colors">
                      <td className="py-2.5 px-3">
                        <div className="font-medium text-[#EBE5D9]">{lead.business_name}</div>
                        <div className="text-[10px] text-[#B39D82] font-mono">{lead.segment}</div>
                      </td>
                      <td className="py-2.5 px-3">
                        <div>{lead.city}</div>
                        <div className="text-[10px] text-[#B39D82] font-mono">
                          ₹{lead.monthly_spend_inr.toLocaleString()} / mo
                        </div>
                      </td>
                      <td className="py-2.5 px-3">
                        <span className="text-[#EBE5D9]">{lead.drop_reason || "Pending"}</span>
                      </td>
                      <td className="py-2.5 px-3">
                        <span
                          className={`font-mono font-medium ${
                            scoreVal >= 70
                              ? "text-emerald-400"
                              : scoreVal >= 40
                              ? "text-[#d9ad63]"
                              : "text-[#B39D82]"
                          }`}
                        >
                          {scoreVal.toFixed(1)}%
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-right">
                        <a
                          href={lead.whatsapp_rescue_link}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center space-x-1.5 bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-1 px-3 rounded-lg text-xs transition-colors shadow-sm"
                        >
                          <MessageSquare className="w-3 h-3" />
                          <span>Rescue</span>
                        </a>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
