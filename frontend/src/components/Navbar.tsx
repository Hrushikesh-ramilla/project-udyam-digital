import React from "react";
import { motion } from "motion/react";
import { Zap, Sparkles, ShieldCheck, Truck, BarChart3, Scale } from "lucide-react";
import { AppPersona } from "../types";

export interface NavbarProps {
  currentTab: "studio" | "kyc" | "tracker" | "partner" | "judge";
  setTab: (tab: "studio" | "kyc" | "tracker" | "partner" | "judge") => void;
  persona: AppPersona;
  setPersona: (persona: AppPersona) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentTab, setTab, persona, setPersona }) => {
  const customerNavItems = [
    { id: "studio" as const, label: "Studio", icon: Sparkles },
    { id: "kyc" as const, label: "Smart KYC", icon: ShieldCheck },
  ];

  const partnerNavItems = [
    { id: "partner" as const, label: "Lead Rescue", icon: BarChart3 },
    { id: "tracker" as const, label: "Fulfillment", icon: Truck },
    { id: "judge" as const, label: "Jury Bench", icon: Scale },
  ];

  const navItems = persona === "CUSTOMER" ? customerNavItems : partnerNavItems;

  const handlePersonaSwitch = (newPersona: AppPersona) => {
    setPersona(newPersona);
    if (newPersona === "CUSTOMER") {
      if (currentTab !== "studio" && currentTab !== "kyc") {
        setTab("studio");
      }
    } else {
      if (currentTab !== "partner" && currentTab !== "tracker" && currentTab !== "judge") {
        setTab("partner");
      }
    }
  };

  return (
    <header className="sticky top-0 z-50 w-full bg-[#030405]/85 backdrop-blur-2xl border-b border-[rgba(235,229,217,0.06)]">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
        {/* Brand Architecture */}
        <motion.div
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
          onClick={() => {
            setPersona("CUSTOMER");
            setTab("studio");
          }}
          className="flex items-center space-x-3 cursor-pointer shrink-0"
        >
          <div className="w-8 h-8 rounded-xl bg-[#e40000] flex items-center justify-center shadow-[0_0_20px_rgba(228,0,0,0.35)]">
            <Zap className="w-4 h-4 text-white fill-white" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="font-sans text-sm font-semibold tracking-tight text-[#EBE5D9]">
              Airtel Digital
            </span>
            <span className="text-[10px] font-mono tracking-widest text-[#B39D82] uppercase hidden sm:inline">
              Udyam Studio
            </span>
          </div>
        </motion.div>

        {/* Dual-Persona Role Switcher (Issue #24) */}
        <div className="flex items-center p-1 bg-[#080a0d] border border-[rgba(235,229,217,0.08)] rounded-full shadow-[0_2px_12px_rgba(0,0,0,0.5)]">
          <button
            onClick={() => handlePersonaSwitch("CUSTOMER")}
            className={`relative px-3 py-1 rounded-full text-xs font-medium transition-all duration-200 cursor-pointer flex items-center space-x-1.5 ${
              persona === "CUSTOMER" ? "text-white" : "text-[#B39D82] hover:text-[#EBE5D9]"
            }`}
          >
            {persona === "CUSTOMER" && (
              <motion.div
                layoutId="personaPill"
                transition={{ type: "spring", stiffness: 450, damping: 32 }}
                className="absolute inset-0 bg-[#e40000] rounded-full shadow-[0_0_12px_rgba(228,0,0,0.35)]"
              />
            )}
            <span className="relative z-10">🏬 MSME Customer</span>
          </button>
          <button
            onClick={() => handlePersonaSwitch("PARTNER_OPS")}
            className={`relative px-3 py-1 rounded-full text-xs font-medium transition-all duration-200 cursor-pointer flex items-center space-x-1.5 ${
              persona === "PARTNER_OPS" ? "text-white" : "text-[#B39D82] hover:text-[#EBE5D9]"
            }`}
          >
            {persona === "PARTNER_OPS" && (
              <motion.div
                layoutId="personaPill"
                transition={{ type: "spring", stiffness: 450, damping: 32 }}
                className="absolute inset-0 bg-[#e40000] rounded-full shadow-[0_0_12px_rgba(228,0,0,0.35)]"
              />
            )}
            <span className="relative z-10">🛡️ Partner &amp; Ops</span>
          </button>
        </div>

        {/* Apple-style Unified Floating Nav */}
        <nav className="flex items-center space-x-1 bg-[#080a0d] p-1 rounded-full border border-[rgba(235,229,217,0.08)] shadow-[0_4px_24px_rgba(0,0,0,0.6)]">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setTab(item.id)}
                className={`relative px-3.5 py-1.5 rounded-full text-xs font-medium transition-colors duration-200 cursor-pointer flex items-center space-x-1.5 ${
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
                <span className="relative z-10 hidden sm:inline">{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Telemetry Pill */}
        <div className="hidden lg:flex items-center space-x-2 font-mono text-[11px] text-[#B39D82] bg-[#080a0d] border border-[rgba(235,229,217,0.06)] px-3 py-1 rounded-full">
          <span className="live-pulse-dot" />
          <span>MUMBAI · 11MS</span>
        </div>
      </div>
    </header>
  );
};
