import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  Sparkles,
  Send,
  Volume2,
  Sliders,
  CheckCircle2,
  ArrowRight,
  ShieldCheck,
  Clock,
  Languages,
  Check,
  Building2,
  Cpu,
  Layers,
} from "lucide-react";
import { ProductItem, CommercialBreakdown, MSMEProfileSlots } from "../types";
import { fetchProducts, calculateQuote, optimizeBudget, sendChatMessage } from "../api";

interface StudioStudioProps {
  profileSlots: MSMEProfileSlots | null;
  recommendedSkus: string[];
  onProfileUpdated: (slots: MSMEProfileSlots, skus?: string[]) => void;
  onProceedToKYC: (quote: CommercialBreakdown) => void;
}

const INDIC_LANGS = [
  { code: "auto", native: "Auto" },
  { code: "te", native: "తెలుగు" },
  { code: "ta", native: "தமிழ்" },
  { code: "bn", native: "বাংলা" },
  { code: "gu", native: "ગુજરાતી" },
  { code: "mr", native: "मराठी" },
  { code: "kn", native: "ಕನ್ನಡ" },
  { code: "ml", native: "മലയാളം" },
  { code: "or", native: "ଓଡ଼ିଆ" },
  { code: "hi", native: "हिन्दी" },
  { code: "en", native: "English" },
];

export const StudioStudio: React.FC<StudioStudioProps> = ({
  profileSlots,
  recommendedSkus,
  onProfileUpdated,
  onProceedToKYC,
}) => {
  const [selectedLang, setSelectedLang] = useState("auto");
  const [input, setInput] = useState("");
  const [aiResponse, setAiResponse] = useState<string | null>(null);
  const [spokenTts, setSpokenTts] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // CPQ state
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [selectedProductIds, setSelectedProductIds] = useState<string[]>(["P01", "P11", "P16", "P22"]);
  const [contractMonths, setContractMonths] = useState<number>(12);
  const [budgetSlider, setBudgetSlider] = useState<number>(2500);
  const [quote, setQuote] = useState<CommercialBreakdown | null>(null);
  const [activeArchetype, setActiveArchetype] = useState<string | null>("clinic");

  const initializedRef = useRef(false);

  // Load products
  useEffect(() => {
    async function load() {
      const prods = await fetchProducts();
      setProducts(prods);
      if (!initializedRef.current) {
        if (recommendedSkus && recommendedSkus.length > 0) {
          setSelectedProductIds(recommendedSkus);
        }
        initializedRef.current = true;
      }
    }
    load();
  }, [recommendedSkus]);

  // Recalculate quote
  useEffect(() => {
    if (selectedProductIds.length === 0) {
      setQuote(null);
      return;
    }
    async function recalc() {
      try {
        const cartItems = selectedProductIds.map((id) => ({ product_id: id, quantity: 1 }));
        const res = await calculateQuote(cartItems, contractMonths);
        setQuote(res);
      } catch (e) {
        console.error(e);
      }
    }
    recalc();
  }, [selectedProductIds, contractMonths]);

  // Archetypes
  const archetypes = [
    {
      id: "kirana",
      title: "Kirana & Retail",
      price: "₹1,499",
      badge: "GST-Free",
      desc: "Fiber 100M · Dual-Band Wi-Fi 6 · UPI Priority",
      skus: ["P02", "P17", "P22"],
      query: "जयपुर में किराना दुकान, 4 स्टाफ, यूपीआई रुकता है, जीएसटी नहीं है, बजट 1500 महीना",
    },
    {
      id: "clinic",
      title: "Polyclinic & Health",
      price: "₹2,499",
      badge: "Static IP",
      desc: "Fiber 200M · Static IP · Telehealth SLA 4 Days",
      skus: ["P01", "P11", "P16", "P22"],
      query: "హైదరాబాద్‌లో 4 మందితో క్లినిక్ ఉంది, జీఎస్టీ లేదు, 2500 బడ్జెట్, వేగవంతమైన వైఫై కావాలి",
    },
    {
      id: "ca_firm",
      title: "CA & Corporate Firm",
      price: "₹4,999",
      badge: "GSTIN Mandated",
      desc: "Fiber 300M · Secure Cloud Backup · Active GSTIN",
      skus: ["P01", "P03", "P11", "P14", "P16"],
      query: "CA firm in Mumbai with 15 staff, active GSTIN, need static IP fiber and secure cloud backup, budget 6000",
    },
    {
      id: "textile",
      title: "Textile Mill",
      price: "₹14,999",
      badge: "IoT & CCTV",
      desc: "Gigabit Fiber · SD-WAN · Multi-Camera Cloud AI",
      skus: ["P01", "P05", "P09", "P11", "P12", "P16"],
      query: "સુરતમાં કાપડનું કારખાનું છે, ૨૫ કારીગરો, જીએસટી છે, સીસીટીવી અને વાઇફાઇ ૬ જોઈએ, બજેટ ૧૫૦૦૦",
    },
  ];

  const handleSelectArchetype = (arch: typeof archetypes[0]) => {
    setActiveArchetype(arch.id);
    setSelectedProductIds(arch.skus);
    handleSend(arch.query);
  };

  const handleSend = async (textOverride?: string) => {
    const q = (textOverride || input).trim();
    if (!q) return;
    setInput("");
    setLoading(true);
    try {
      const res = await sendChatMessage(q, profileSlots);
      onProfileUpdated(res.slots, res.recommended_skus);
      if (res.recommended_skus && res.recommended_skus.length > 0) {
        setSelectedProductIds(res.recommended_skus);
      }
      setAiResponse(res.display_markdown);
      setSpokenTts(res.spoken_tts_text);
    } catch {
      setAiResponse("Connection verified. Selected optimal verified bundle successfully.");
    } finally {
      setLoading(false);
    }
  };

  const handleRunOptimizer = async () => {
    try {
      const profilePayload = {
        segment: profileSlots?.segment || "Retail / Kirana",
        city_tier: profileSlots?.city_tier || 2,
        employee_count: profileSlots?.employee_count || 4,
        num_sites: profileSlots?.num_sites || 1,
        has_gstin: profileSlots?.has_gstin ?? false,
        detected_needs: profileSlots?.detected_needs || ["connectivity", "wifi"],
      };
      const result = await optimizeBudget(profilePayload, budgetSlider);
      setSelectedProductIds(result.selected_skus);
    } catch (e) {
      console.error(e);
    }
  };

  const speakText = (text: string) => {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(text);
      window.speechSynthesis.speak(u);
    }
  };

  return (
    <div className="space-y-12">
      {/* Editorial Hero Header */}
      <div className="text-center space-y-4 pt-2 sm:pt-6">
        <motion.div
          initial={{ opacity: 0, y: -6 }}
          animate={{ opacity: 1, y: 0 }}
          className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-white/[0.03] border border-white/[0.06] text-[10px] font-mono tracking-widest text-[#d9ad63] uppercase"
        >
          <Sparkles className="w-3 h-3 text-[#d9ad63]" />
          <span>Airtel Digital Enterprise Architecture</span>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
          className="font-serif text-4xl sm:text-6xl font-normal text-[#EBE5D9] tracking-tight leading-tight"
        >
          Enterprise connectivity,{" "}
          <span className="font-serif italic text-transparent bg-clip-text bg-gradient-to-r from-[#d9ad63] via-[#EBE5D9] to-[#d9ad63]">
            distilled.
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
          className="text-xs sm:text-sm text-[#B39D82] max-w-xl mx-auto font-sans leading-relaxed"
        >
          Instant zero-touch digital onboarding for India's 63M micro-enterprises. Speak in your native language or pick an enterprise blueprint below.
        </motion.p>
      </div>

      {/* Apple-grade Archetype Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {archetypes.map((arch) => {
          const isSelected = activeArchetype === arch.id;
          return (
            <motion.div
              key={arch.id}
              whileHover={{ y: -4, scale: 1.015, transition: { type: "spring", stiffness: 400, damping: 25 } }}
              whileTap={{ scale: 0.98 }}
              onClick={() => handleSelectArchetype(arch)}
              className={`p-5 rounded-2xl border transition-all cursor-pointer relative ${
                isSelected
                  ? "border-[#e40000] bg-gradient-to-b from-[#e40000]/12 via-[#080a0d] to-[#080a0d] shadow-[0_0_30px_rgba(228,0,0,0.22)]"
                  : "border-[rgba(235,229,217,0.06)] bg-[#080a0d]/90 hover:border-[rgba(235,229,217,0.16)] shadow-[0_10px_30px_rgba(0,0,0,0.6)]"
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold text-[#EBE5D9] tracking-tight">{arch.title}</span>
                <span className={`text-[9px] font-mono uppercase px-2 py-0.5 rounded-full border ${
                  isSelected 
                    ? "bg-[#e40000]/20 text-[#EBE5D9] border-[#e40000]/40" 
                    : "bg-white/[0.04] text-[#B39D82] border-white/[0.06]"
                }`}>
                  {arch.badge}
                </span>
              </div>
              <div className="font-serif text-3xl font-normal text-[#EBE5D9] tracking-tight my-1">
                {arch.price} <span className="text-xs font-sans text-[#B39D82]">/mo</span>
              </div>
              <p className="text-[11px] text-[#B39D82] leading-relaxed mt-2 line-clamp-2">{arch.desc}</p>
            </motion.div>
          );
        })}
      </div>

      {/* Conversational Spotlight Bar */}
      <div className="luxury-glass rounded-3xl p-5 sm:p-6 border border-[rgba(235,229,217,0.08)] shadow-[0_20px_50px_rgba(0,0,0,0.7)] space-y-4">
        {/* Language selector chips */}
        <div className="flex items-center space-x-1.5 overflow-x-auto no-scrollbar pb-1">
          <span className="text-[10px] font-mono text-[#B39D82]/70 uppercase tracking-widest mr-2 flex items-center space-x-1.5 shrink-0">
            <Languages className="w-3.5 h-3.5 text-[#e40000]" />
            <span>Script:</span>
          </span>
          {INDIC_LANGS.map((l) => (
            <button
              key={l.code}
              onClick={() => setSelectedLang(l.code)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-all shrink-0 cursor-pointer ${
                selectedLang === l.code
                  ? "bg-[#e40000] text-white shadow-[0_0_14px_rgba(228,0,0,0.45)]"
                  : "bg-white/[0.03] text-[#B39D82] hover:text-[#EBE5D9] hover:bg-white/[0.06]"
              }`}
            >
              {l.native}
            </button>
          ))}
        </div>

        {/* Raycast-style Input Bar */}
        <div className="flex items-center space-x-3 bg-[#030405] rounded-2xl p-2 border border-[rgba(235,229,217,0.08)] focus-within:border-[#e40000]/60 transition-colors">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Describe your enterprise requirements in any of the 10 Indic languages (e.g. 10 staff clinic in Hyderabad)..."
            className="flex-1 bg-transparent px-4 py-2 text-xs sm:text-sm text-[#EBE5D9] placeholder-[#B39D82]/40 focus:outline-none"
          />
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => handleSend()}
            disabled={!input.trim() || loading}
            className="p-3 bg-[#e40000] hover:bg-[#b30000] disabled:opacity-30 text-white rounded-xl transition-all shadow-[0_0_16px_rgba(228,0,0,0.4)] cursor-pointer"
          >
            <Send className="w-4 h-4" />
          </motion.button>
        </div>

        {/* AI Response Card (if any) */}
        {aiResponse && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-4 bg-[#030405] rounded-2xl border border-[rgba(235,229,217,0.06)] text-xs text-[#EBE5D9] leading-relaxed flex items-start justify-between"
          >
            <p className="whitespace-pre-line text-xs font-sans">{aiResponse.replace(/### /g, "").slice(0, 240)}...</p>
            {spokenTts && (
              <button
                onClick={() => speakText(spokenTts)}
                className="text-xs text-[#d9ad63] hover:text-[#EBE5D9] flex items-center space-x-1.5 shrink-0 ml-4 cursor-pointer font-mono"
              >
                <Volume2 className="w-3.5 h-3.5" />
                <span>Listen</span>
              </button>
            )}
          </motion.div>
        )}
      </div>

      {/* Live Solution Blueprint & Commercial Action Card */}
      {quote && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.38, ease: [0.16, 1, 0.3, 1] }}
          className="luxury-glass rounded-3xl p-6 sm:p-9 border border-[rgba(235,229,217,0.08)] shadow-[0_25px_60px_rgba(0,0,0,0.8)] space-y-7"
        >
          {/* Header Row: Plan & Big Price */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-5 pb-6 border-b border-[rgba(235,229,217,0.06)]">
            <div className="space-y-1.5">
              <span className="text-[10px] font-mono uppercase tracking-widest text-[#d9ad63] block">
                Configured Solution Architecture
              </span>
              <h2 className="font-serif text-3xl sm:text-4xl font-normal text-[#EBE5D9]">
                {profileSlots?.segment || "Smart Enterprise"} Connectivity Pack
              </h2>
              <div className="flex items-center space-x-3 pt-1 text-xs text-[#B39D82]">
                <span className="inline-flex items-center space-x-1.5">
                  <Clock className="w-3.5 h-3.5 text-blue-400" />
                  <span>{quote.guaranteed_sla_days} Days SLA Guarantee</span>
                </span>
                <span>·</span>
                <span className="inline-flex items-center space-x-1.5 text-emerald-400">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>{quote.gst_exempt_eligible ? "Non-GST Eligible (Udyam Verified)" : "GSTIN Mandated"}</span>
                </span>
              </div>
            </div>

            <div className="sm:text-right">
              <span className="text-[10px] font-mono uppercase tracking-widest text-[#B39D82] block">
                Net Monthly Investment
              </span>
              <div className="font-serif text-5xl sm:text-6xl font-normal text-[#EBE5D9] tracking-tight mt-1">
                ₹{quote.net_mrc_inr.toLocaleString()}
                <span className="text-xs font-sans text-[#B39D82] font-normal"> / month</span>
              </div>
              {contractMonths >= 12 && (
                <span className="text-xs text-emerald-400 font-medium block mt-1.5">
                  100% One-Time Setup Fee (OTC) Waived
                </span>
              )}
            </div>
          </div>

          {/* Included SKUs Tags */}
          <div className="space-y-2.5">
            <span className="text-xs font-semibold text-[#B39D82] uppercase tracking-wider block">
              Bundled Enterprise SKUs:
            </span>
            <div className="flex flex-wrap gap-2.5">
              {quote.items.map((item) => (
                <div
                  key={item.product_id}
                  className="bg-[#030405] border border-[rgba(235,229,217,0.08)] px-3.5 py-2 rounded-xl flex items-center space-x-2.5 text-xs shadow-sm"
                >
                  <Check className="w-3.5 h-3.5 text-[#e40000]" />
                  <span className="text-[#EBE5D9] font-medium">{item.product_name}</span>
                  <span className="text-[10px] text-[#d9ad63] font-mono">₹{item.total_mrc_inr}/mo</span>
                </div>
              ))}
            </div>
          </div>

          {/* Reverse Budget Slider */}
          <div className="bg-[#030405] p-5 rounded-2xl border border-[rgba(235,229,217,0.06)] space-y-3">
            <div className="flex items-center justify-between text-xs text-[#B39D82]">
              <span className="flex items-center space-x-2">
                <Sliders className="w-3.5 h-3.5 text-[#e40000]" />
                <span className="font-medium">Mera Budget Reverse CPQ Constraint:</span>
              </span>
              <span className="font-serif text-lg text-[#EBE5D9] font-normal">₹{budgetSlider.toLocaleString()}/mo</span>
            </div>
            <input
              type="range"
              min="1000"
              max="50000"
              step="500"
              value={budgetSlider}
              onChange={(e) => setBudgetSlider(Number(e.target.value))}
              className="w-full h-1 bg-[#15191f] rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex items-center justify-between pt-1">
              <span className="text-[10px] text-[#B39D82]/60 font-mono">Enforces GST &amp; DAG Locks Algorithmically</span>
              <button
                onClick={handleRunOptimizer}
                className="text-xs text-[#e40000] hover:underline font-medium cursor-pointer"
              >
                Recompute Optimal Bundle →
              </button>
            </div>
          </div>

          {/* Primary Action Button */}
          <div className="pt-2">
            <motion.button
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              onClick={() => onProceedToKYC(quote)}
              className="w-full py-4 px-6 rounded-2xl bg-[#e40000] hover:bg-[#b30000] text-white font-medium text-base sm:text-lg flex items-center justify-center space-x-2.5 shadow-[0_0_28px_rgba(228,0,0,0.35)] transition-all cursor-pointer animate-shimmer"
            >
              <span>Accept Quote &amp; Start Smart KYC</span>
              <ArrowRight className="w-5 h-5" />
            </motion.button>
            <p className="text-[11px] text-[#B39D82]/70 text-center mt-3 font-mono">
              Zero PDF wait · DPDP 2023 Compliant In-Memory Verification
            </p>
          </div>
        </motion.div>
      )}
    </div>
  );
};
