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
  ArrowUpRight,
  Filter,
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
    <div className="max-w-6xl mx-auto space-y-7">
      {/* 4 Macro KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <motion.div
          whileHover={{ y: -3 }}
          className="luxury-glass p-5 rounded-2xl border border-[rgba(235,229,217,0.08)] space-y-2 shadow-sm"
        >
          <div className="flex items-center justify-between text-xs text-[#B39D82]">
            <span className="font-mono uppercase tracking-wider text-[10px]">Quote Drop-Off</span>
            <TrendingDown className="w-4 h-4 text-[#e40000]" />
          </div>
          <div className="font-serif text-4xl font-normal text-[#e40000] tracking-tight">56.4%</div>
          <p className="text-[11px] text-[#B39D82]/70 font-mono">1,113 leads lost to manual PDF delays</p>
        </motion.div>

        <motion.div
          whileHover={{ y: -3 }}
          className="luxury-glass p-5 rounded-2xl border border-[rgba(235,229,217,0.08)] space-y-2 shadow-sm"
        >
          <div className="flex items-center justify-between text-xs text-[#B39D82]">
            <span className="font-mono uppercase tracking-wider text-[10px]">Non-GST Conversion Gap</span>
            <Percent className="w-4 h-4 text-[#d9ad63]" />
          </div>
          <div className="font-serif text-4xl font-normal text-[#d9ad63] tracking-tight">2.0%</div>
          <p className="text-[11px] text-[#B39D82]/70 font-mono">Vs 9.6% GST-registered rate</p>
        </motion.div>

        <motion.div
          whileHover={{ y: -3 }}
          className="luxury-glass p-5 rounded-2xl border border-[rgba(235,229,217,0.08)] space-y-2 shadow-sm"
        >
          <div className="flex items-center justify-between text-xs text-[#B39D82]">
            <span className="font-mono uppercase tracking-wider text-[10px]">Historical Activation SLA</span>
            <Clock className="w-4 h-4 text-blue-400" />
          </div>
          <div className="font-serif text-4xl font-normal text-blue-400 tracking-tight">17.6d</div>
          <p className="text-[11px] text-[#B39D82]/70 font-mono">Compressed to 4-day SLA</p>
        </motion.div>

        <motion.div
          whileHover={{ y: -3 }}
          className="luxury-glass p-5 rounded-2xl border border-[rgba(235,229,217,0.08)] space-y-2 shadow-sm"
        >
          <div className="flex items-center justify-between text-xs text-[#B39D82]">
            <span className="font-mono uppercase tracking-wider text-[10px]">Customer Acquisition Cost</span>
            <DollarSign className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="font-serif text-4xl font-normal text-emerald-400 tracking-tight">₹15,000</div>
          <p className="text-[11px] text-[#B39D82]/70 font-mono">Target: &lt;₹3,500 digital CAC</p>
        </motion.div>
      </div>

      {/* Table Card */}
      <div className="luxury-glass rounded-3xl p-6 sm:p-7 space-y-5 border border-[rgba(235,229,217,0.08)] shadow-[0_20px_50px_rgba(0,0,0,0.7)]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-3 border-b border-[rgba(235,229,217,0.06)]">
          <div className="flex items-center space-x-2.5">
            <div className="w-7 h-7 rounded-lg bg-[#e40000]/15 flex items-center justify-center text-[#e40000]">
              <Zap className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-serif text-lg sm:text-xl font-normal text-[#EBE5D9]">
                High-Propensity Rescuable Leads
              </h3>
              <p className="text-xs text-[#B39D82]">LightGBM Gradient Boosted Pipeline (5,000 Training Leads)</p>
            </div>
          </div>

          <div className="flex items-center space-x-2.5">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-[#B39D82] absolute left-3.5 top-3" />
              <input
                type="text"
                placeholder="Search leads, cities..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-[#030405] border border-[rgba(235,229,217,0.08)] rounded-xl pl-9 pr-3.5 py-2 text-xs text-[#EBE5D9] placeholder-[#B39D82]/40 focus:outline-none focus:border-[#e40000] w-48 sm:w-56 transition-colors"
              />
            </div>
            <select
              value={filterSegment}
              onChange={(e) => setFilterSegment(e.target.value)}
              className="bg-[#030405] border border-[rgba(235,229,217,0.08)] rounded-xl px-3 py-2 text-xs text-[#EBE5D9] focus:outline-none cursor-pointer"
            >
              <option value="ALL">All Segments</option>
              <option value="Retail">Retail</option>
              <option value="Kirana">Kirana</option>
              <option value="Manufacturing">Manufacturing</option>
            </select>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-[#EBE5D9]">
            <thead className="bg-[#030405] text-[#B39D82] uppercase font-mono text-[9px] tracking-wider border-b border-[rgba(235,229,217,0.06)]">
              <tr>
                <th className="py-3 px-4">Enterprise Lead</th>
                <th className="py-3 px-4">City &amp; Monthly Spend</th>
                <th className="py-3 px-4">Drop-Off Root Cause</th>
                <th className="py-3 px-4">Rescue Propensity</th>
                <th className="py-3 px-4 text-right">Instant Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[rgba(235,229,217,0.04)]">
              {loading ? (
                <tr>
                  <td colSpan={5} className="py-10 text-center text-[#B39D82] font-mono">
                    Loading ML predictions...
                  </td>
                </tr>
              ) : filteredLeads.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-10 text-center text-[#B39D82]">
                    No leads match your search query.
                  </td>
                </tr>
              ) : (
                filteredLeads.map((lead) => {
                  const scoreVal = lead.propensity_score > 1.0 ? lead.propensity_score : lead.propensity_score * 100;
                  return (
                    <tr key={lead.lead_id} className="hover:bg-white/[0.03] transition-colors">
                      <td className="py-3.5 px-4">
                        <div className="font-medium text-[#EBE5D9] text-xs sm:text-sm">{lead.business_name}</div>
                        <div className="text-[10px] text-[#B39D82] font-mono">{lead.segment}</div>
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="font-medium">{lead.city}</div>
                        <div className="text-[10px] text-[#d9ad63] font-mono">
                          ₹{lead.monthly_spend_inr.toLocaleString()} / mo
                        </div>
                      </td>
                      <td className="py-3.5 px-4">
                        <span className="text-[#EBE5D9]">{lead.drop_reason || "Pending"}</span>
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/15 border border-emerald-500/30 font-mono text-emerald-400 font-medium">
                          <span>{scoreVal.toFixed(1)}%</span>
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <motion.a
                          whileHover={{ scale: 1.03 }}
                          whileTap={{ scale: 0.97 }}
                          href={lead.whatsapp_rescue_link}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center space-x-1.5 bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-1.5 px-3.5 rounded-xl text-xs transition-all shadow-[0_0_12px_rgba(16,185,129,0.3)]"
                        >
                          <MessageSquare className="w-3.5 h-3.5" />
                          <span>Rescue Lead</span>
                        </motion.a>
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
