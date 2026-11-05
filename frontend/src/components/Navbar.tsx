import React from "react";
import { motion } from "motion/react";
import { Zap, Sparkles, BarChart3, Scale, Layers } from "lucide-react";

interface NavbarProps {
  currentTab: "customer" | "obo" | "partner" | "judge";
  setTab: (tab: "customer" | "obo" | "partner" | "judge") => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentTab, setTab }) => {
  const tabs = [
    { id: "customer", label: "Command Studio", icon: Sparkles },
    { id: "partner", label: "Lead Rescue", icon: BarChart3 },
    { id: "judge", label: "Jury Bench", icon: Scale },
  ] as const;

  return (
    <header className="sticky top-0 z-50 w-full bg-[#030405]/80 backdrop-blur-2xl border-b border-[rgba(235,229,217,0.06)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Architecture */}
        <motion.div
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
          onClick={() => setTab("customer")}
          className="flex items-center space-x-3 cursor-pointer"
        >
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-[#e40000] to-[#b30000] flex items-center justify-center shadow-[0_0_20px_rgba(228,0,0,0.35)] border border-white/20">
            <Zap className="w-4 h-4 text-white fill-white" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="font-sans text-base font-semibold tracking-tight text-[#EBE5D9]">
              Airtel Digital
            </span>
            <span className="text-[10px] font-mono tracking-widest text-[#B39D82] uppercase">
              Udyam Studio
            </span>
          </div>
        </motion.div>

        {/* Inertial Floating Nav Tabs */}
        <nav className="flex items-center space-x-1 bg-[#080a0d]/90 p-1 rounded-full border border-[rgba(235,229,217,0.08)] shadow-[0_4px_20px_rgba(0,0,0,0.5)]">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = currentTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setTab(tab.id)}
                className={`relative px-4 py-1.5 rounded-full text-xs font-medium transition-colors duration-200 cursor-pointer flex items-center space-x-1.5 ${
                  isActive ? "text-[#EBE5D9]" : "text-[#B39D82]/70 hover:text-[#EBE5D9]"
                }`}
              >
                {isActive && (
                  <motion.div
                    layoutId="activeNavPill"
                    transition={{ type: "spring", stiffness: 450, damping: 32 }}
                    className="absolute inset-0 bg-[#e40000] rounded-full shadow-[0_0_16px_rgba(228,0,0,0.4)]"
                  />
                )}
                <Icon className="w-3.5 h-3.5 relative z-10" />
                <span className="relative z-10">{tab.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Telemetry Pill */}
        <div className="hidden sm:flex items-center space-x-3 font-mono text-[11px]">
          <div className="flex items-center space-x-2 bg-[#080a0d] border border-[rgba(235,229,217,0.06)] px-3 py-1 rounded-full text-[#B39D82]">
            <span className="live-pulse-dot" />
            <span>MUMBAI HUB · 11MS</span>
          </div>
        </div>
      </div>
    </header>
  );
};
