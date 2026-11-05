import React from "react";
import {
  Sparkles,
  ShieldCheck,
  BarChart3,
  Scale,
  Zap,
  Activity,
  Layers,
} from "lucide-react";

interface NavbarProps {
  currentTab: "customer" | "obo" | "partner" | "judge";
  setTab: (tab: "customer" | "obo" | "partner" | "judge") => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentTab, setTab }) => {
  return (
    <header className="sticky top-0 z-50 w-full bg-[#080808]/85 backdrop-blur-2xl border-b border-white/[0.07]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Architecture */}
        <div className="flex items-center space-x-3.5 cursor-pointer" onClick={() => setTab("customer")}>
          <div className="relative flex items-center justify-center">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#e40000] to-[#8b0000] flex items-center justify-center shadow-[0_0_16px_rgba(228,0,0,0.4)] border border-white/20">
              <Zap className="w-4 h-4 text-white fill-white" />
            </div>
            <span className="absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full bg-emerald-400 border border-[#080808]" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-serif text-lg tracking-tight font-medium text-[#f2efea]">
                Airtel Digital
              </span>
              <span className="text-[9px] font-mono uppercase tracking-[0.2em] bg-white/[0.05] border border-white/[0.08] text-[#d9ad63] px-2 py-0.5 rounded-full">
                Udyam OS v2.6
              </span>
            </div>
            <p className="text-[10px] font-mono tracking-wider text-white/40 uppercase hidden sm:block">
              63M MSME Instant Zero-Touch Onboarding
            </p>
          </div>
        </div>

        {/* Studio Navigation Pills */}
        <nav className="flex items-center space-x-1 sm:space-x-1.5 bg-[#121210]/90 p-1 rounded-full border border-white/[0.08] shadow-[inset_0_1px_1px_rgba(255,255,255,0.06)]">
          <button
            onClick={() => setTab("customer")}
            className={`flex items-center space-x-1.5 px-3.5 py-1.5 rounded-full text-xs font-medium transition-all duration-200 cursor-pointer ${
              currentTab === "customer"
                ? "bg-[#e40000] text-white shadow-[0_0_16px_rgba(228,0,0,0.4)]"
                : "text-white/60 hover:text-white hover:bg-white/[0.04]"
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Command Studio</span>
            <span className="sm:hidden">Studio</span>
          </button>

          <button
            onClick={() => setTab("partner")}
            className={`flex items-center space-x-1.5 px-3.5 py-1.5 rounded-full text-xs font-medium transition-all duration-200 cursor-pointer ${
              currentTab === "partner"
                ? "bg-[#e40000] text-white shadow-[0_0_16px_rgba(228,0,0,0.4)]"
                : "text-white/60 hover:text-white hover:bg-white/[0.04]"
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Lead Rescue (56% Cohort)</span>
            <span className="sm:hidden">Rescue</span>
          </button>

          <button
            onClick={() => setTab("judge")}
            className={`flex items-center space-x-1.5 px-3.5 py-1.5 rounded-full text-xs font-medium transition-all duration-200 cursor-pointer ${
              currentTab === "judge"
                ? "bg-[#e40000] text-white shadow-[0_0_16px_rgba(228,0,0,0.4)]"
                : "text-white/60 hover:text-white hover:bg-white/[0.04]"
            }`}
          >
            <Scale className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Jury Test Bench</span>
            <span className="sm:hidden">Jury</span>
          </button>
        </nav>

        {/* Live POP Telemetry Indicator */}
        <div className="hidden lg:flex items-center space-x-3 text-xs font-mono">
          <div className="flex items-center space-x-2 bg-[#121210] border border-white/[0.07] px-3 py-1.5 rounded-full">
            <span className="live-pulse-dot" />
            <span className="text-[11px] text-white/70">MUMBAI POP · 11MS</span>
          </div>
          <span className="text-[9px] uppercase tracking-[0.2em] font-mono px-2.5 py-1 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-emerald-400">
            DPDP In-Memory
          </span>
        </div>
      </div>
    </header>
  );
};
