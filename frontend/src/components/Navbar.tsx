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
    <header className="sticky top-0 z-50 w-full bg-[#0B0F19]/90 backdrop-blur-2xl border-b border-slate-800/80 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
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
          <div className="w-9 h-9 rounded-xl bg-[#e40000] flex items-center justify-center shadow-[0_0_20px_rgba(228,0,0,0.4)]">
            <Zap className="w-5 h-5 text-white fill-white" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="font-sans text-base font-bold tracking-tight text-white">
              Airtel Business
            </span>
            <span className="text-xs font-mono font-medium tracking-wider text-slate-400 uppercase hidden sm:inline">
              Project Udyam
            </span>
          </div>
        </motion.div>

        {/* Dual-Persona Role Switcher (Issue #24) */}
        <div className="flex items-center p-1 bg-slate-900/90 border border-slate-700/60 rounded-full shadow-inner">
          <button
            onClick={() => handlePersonaSwitch("CUSTOMER")}
            className={`relative px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all duration-200 cursor-pointer flex items-center space-x-1.5 ${
              persona === "CUSTOMER" ? "text-white" : "text-slate-400 hover:text-white"
            }`}
          >
            {persona === "CUSTOMER" && (
              <motion.div
                layoutId="personaPill"
                transition={{ type: "spring", stiffness: 450, damping: 32 }}
                className="absolute inset-0 bg-[#e40000] rounded-full shadow-[0_0_14px_rgba(228,0,0,0.4)]"
              />
            )}
            <span className="relative z-10">🏬 MSME Customer</span>
          </button>
          <button
            onClick={() => handlePersonaSwitch("PARTNER_OPS")}
            className={`relative px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all duration-200 cursor-pointer flex items-center space-x-1.5 ${
              persona === "PARTNER_OPS" ? "text-white" : "text-slate-400 hover:text-white"
            }`}
          >
            {persona === "PARTNER_OPS" && (
              <motion.div
                layoutId="personaPill"
                transition={{ type: "spring", stiffness: 450, damping: 32 }}
                className="absolute inset-0 bg-[#e40000] rounded-full shadow-[0_0_14px_rgba(228,0,0,0.4)]"
              />
            )}
            <span className="relative z-10">🛡️ Partner &amp; Ops</span>
          </button>
        </div>

        {/* Unified Floating Nav */}
        <nav className="flex items-center space-x-1 bg-slate-900/90 p-1 rounded-full border border-slate-700/60 shadow-md">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setTab(item.id)}
                className={`relative px-4 py-1.5 rounded-full text-xs font-semibold transition-colors duration-200 cursor-pointer flex items-center space-x-1.5 ${
                  isActive ? "text-white" : "text-slate-400 hover:text-white"
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
      </div>
    </header>
  );
};
