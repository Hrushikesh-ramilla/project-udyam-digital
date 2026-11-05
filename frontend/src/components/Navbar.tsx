import React from "react";
import { Shield, Sparkles, Smartphone, Users, BarChart3, Scale } from "lucide-react";

interface NavbarProps {
  currentTab: "customer" | "obo" | "partner" | "judge";
  setTab: (tab: "customer" | "obo" | "partner" | "judge") => void;
  partnerId?: string;
}

export const Navbar: React.FC<NavbarProps> = ({ currentTab, setTab, partnerId }) => {
  return (
    <header className="sticky top-0 z-50 bg-slate-900/90 backdrop-blur-md border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between py-2.5 md:py-0 md:h-16 gap-2">
          {/* Logo & Branding */}
          <div className="flex items-center space-x-2.5 cursor-pointer" onClick={() => setTab("customer")}>
            <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-xl bg-red-600 flex items-center justify-center shadow-lg shadow-red-600/30 font-bold text-white text-base sm:text-xl tracking-wider shrink-0">
              airtel
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-sm sm:text-lg font-bold text-white tracking-tight">Project Udyam Digital</span>
                <span className="text-[10px] sm:text-xs bg-red-500/20 text-red-400 border border-red-500/30 px-1.5 sm:px-2 py-0.5 rounded-full font-medium shrink-0">
                  Enterprise Track A
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">
                Making 6 Crore+ Indian MSMEs Go Digital in One Sitting
              </p>
            </div>
          </div>

          {/* Role Navigation Switcher */}
          <nav className="flex items-center space-x-1 sm:space-x-2 overflow-x-auto py-1">
            <button
              onClick={() => setTab("customer")}
              className={`flex items-center space-x-1.5 px-2.5 sm:px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all shrink-0 ${
                currentTab === "customer"
                  ? "bg-red-600 text-white shadow-md shadow-red-600/20"
                  : "text-slate-300 hover:bg-slate-800 hover:text-white"
              }`}
            >
              <Smartphone className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
              <span className="hidden md:inline">Customer Self-Serve</span>
              <span className="md:hidden">Self-Serve</span>
            </button>

            <button
              onClick={() => setTab("obo")}
              className={`flex items-center space-x-1.5 px-2.5 sm:px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all shrink-0 ${
                currentTab === "obo"
                  ? "bg-red-600 text-white shadow-md shadow-red-600/20"
                  : "text-slate-300 hover:bg-slate-800 hover:text-white"
              }`}
            >
              <Users className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
              <span className="hidden md:inline">Field Rep OBO</span>
              <span className="md:hidden">Field Rep</span>
            </button>

            <button
              onClick={() => setTab("partner")}
              className={`flex items-center space-x-1.5 px-2.5 sm:px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all shrink-0 ${
                currentTab === "partner"
                  ? "bg-red-600 text-white shadow-md shadow-red-600/20"
                  : "text-slate-300 hover:bg-slate-800 hover:text-white"
              }`}
            >
              <BarChart3 className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
              <span className="hidden md:inline">Partner ML Rescue</span>
              <span className="md:hidden">ML Rescue</span>
            </button>

            <button
              onClick={() => setTab("judge")}
              className={`flex items-center space-x-1.5 px-2.5 sm:px-3 py-1.5 rounded-lg text-xs sm:text-sm font-semibold transition-all border shrink-0 ${
                currentTab === "judge"
                  ? "bg-amber-500 text-slate-950 border-amber-400 shadow-md shadow-amber-500/20"
                  : "bg-amber-500/10 text-amber-300 border-amber-500/30 hover:bg-amber-500/20"
              }`}
            >
              <Scale className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-amber-400" />
              <span className="hidden sm:inline">Judge Test Bench</span>
              <span className="sm:hidden">Judge Bench</span>
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
};
