import React from "react";
import { Sparkles, Smartphone, Users, BarChart3, Scale, Activity } from "lucide-react";

interface NavbarProps {
  currentTab: "customer" | "obo" | "partner" | "judge";
  setTab: (tab: "customer" | "obo" | "partner" | "judge") => void;
  partnerId?: string;
}

export const Navbar: React.FC<NavbarProps> = ({ currentTab, setTab }) => {
  return (
    <header className="sticky top-0 z-50 bg-[#0c0c0b]/85 backdrop-blur-xl border-b border-white/[0.08] shadow-2xl">
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between py-2.5 md:py-0 md:h-16 gap-2">
          {/* Logo & Branding */}
          <div className="flex items-center space-x-3 cursor-pointer group" onClick={() => setTab("customer")}>
            <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-br from-red-600 to-rose-700 flex items-center justify-center shadow-lg shadow-red-600/30 font-black text-white text-base sm:text-xl tracking-tighter shrink-0 border border-red-500/30 group-hover:scale-105 transition-transform">
              airtel
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-sm sm:text-lg font-bold text-white tracking-tight font-sans">Project Udyam Digital</span>
                <span className="text-[10px] sm:text-xs bg-red-500/15 text-red-400 border border-red-500/25 px-2 py-0.5 rounded-full font-mono font-medium shrink-0">
                  Track A
                </span>
                <div className="hidden lg:flex items-center space-x-1.5 text-[10px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  <span>TELEMETRY ONLINE</span>
                </div>
              </div>
              <p className="text-[11px] text-[#a3a19b] hidden sm:block font-sans">
                Airtel Business Enterprise MSME Onboarding Engine
              </p>
            </div>
          </div>

          {/* Role Navigation Switcher */}
          <nav className="flex items-center space-x-1 sm:space-x-1.5 bg-[#141413]/90 border border-white/[0.06] p-1 rounded-xl overflow-x-auto no-scrollbar shadow-inner">
            <button
              onClick={() => setTab("customer")}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all shrink-0 cursor-pointer ${
                currentTab === "customer"
                  ? "bg-red-600 text-white shadow-md shadow-red-600/30 font-semibold"
                  : "text-[#a3a19b] hover:text-white hover:bg-white/[0.04]"
              }`}
            >
              <Smartphone className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
              <span className="hidden md:inline">Customer Self-Serve</span>
              <span className="md:hidden">Self-Serve</span>
            </button>

            <button
              onClick={() => setTab("obo")}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all shrink-0 cursor-pointer ${
                currentTab === "obo"
                  ? "bg-red-600 text-white shadow-md shadow-red-600/30 font-semibold"
                  : "text-[#a3a19b] hover:text-white hover:bg-white/[0.04]"
              }`}
            >
              <Users className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
              <span className="hidden md:inline">Field Rep OBO</span>
              <span className="md:hidden">Field Rep</span>
            </button>

            <button
              onClick={() => setTab("partner")}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all shrink-0 cursor-pointer ${
                currentTab === "partner"
                  ? "bg-red-600 text-white shadow-md shadow-red-600/30 font-semibold"
                  : "text-[#a3a19b] hover:text-white hover:bg-white/[0.04]"
              }`}
            >
              <BarChart3 className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
              <span className="hidden md:inline">Partner ML Rescue</span>
              <span className="md:hidden">ML Rescue</span>
            </button>

            <button
              onClick={() => setTab("judge")}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs sm:text-sm font-semibold transition-all shrink-0 border cursor-pointer ${
                currentTab === "judge"
                  ? "bg-gradient-to-r from-amber-500 to-amber-600 text-slate-950 border-amber-400 shadow-md shadow-amber-500/30"
                  : "bg-amber-500/10 text-amber-300 border-amber-500/30 hover:bg-amber-500/20"
              }`}
            >
              <Scale className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
              <span className="hidden sm:inline">Judge Test Bench</span>
              <span className="sm:hidden">Judge</span>
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
};
