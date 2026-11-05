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
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Branding */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setTab("customer")}>
            <div className="w-10 h-10 rounded-xl bg-red-600 flex items-center justify-center shadow-lg shadow-red-600/30 font-bold text-white text-xl tracking-wider">
              airtel
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-lg font-bold text-white tracking-tight">Project Udyam Digital</span>
                <span className="text-xs bg-red-500/20 text-red-400 border border-red-500/30 px-2 py-0.5 rounded-full font-medium">
                  Enterprise Track A
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">
                Making 6 Crore+ Indian MSMEs Go Digital in One Sitting
              </p>
            </div>
          </div>

          {/* Role Navigation Switcher */}
          <nav className="flex items-center space-x-1 sm:space-x-2">
            <button
              onClick={() => setTab("customer")}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all ${
                currentTab === "customer"
                  ? "bg-red-600 text-white shadow-md shadow-red-600/20"
                  : "text-slate-300 hover:bg-slate-800 hover:text-white"
              }`}
            >
              <Smartphone className="w-4 h-4" />
              <span className="hidden md:inline">Customer Self-Serve</span>
              <span className="md:hidden">Self-Serve</span>
            </button>

            <button
              onClick={() => setTab("obo")}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all ${
                currentTab === "obo"
                  ? "bg-red-600 text-white shadow-md shadow-red-600/20"
                  : "text-slate-300 hover:bg-slate-800 hover:text-white"
              }`}
            >
              <Users className="w-4 h-4" />
              <span className="hidden md:inline">Field Rep OBO</span>
              <span className="md:hidden">Field Rep</span>
            </button>

            <button
              onClick={() => setTab("partner")}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all ${
                currentTab === "partner"
                  ? "bg-red-600 text-white shadow-md shadow-red-600/20"
                  : "text-slate-300 hover:bg-slate-800 hover:text-white"
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              <span className="hidden md:inline">Partner ML Rescue</span>
              <span className="md:hidden">ML Rescue</span>
            </button>

            <button
              onClick={() => setTab("judge")}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs sm:text-sm font-semibold transition-all border ${
                currentTab === "judge"
                  ? "bg-amber-500 text-slate-950 border-amber-400 shadow-md shadow-amber-500/20"
                  : "bg-amber-500/10 text-amber-300 border-amber-500/30 hover:bg-amber-500/20"
              }`}
            >
              <Scale className="w-4 h-4 text-amber-400" />
              <span>Judge Test Bench</span>
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
};
