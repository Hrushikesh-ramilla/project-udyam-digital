import React, { useState, useEffect } from "react";
import {
  ShoppingCart,
  Zap,
  Sliders,
  CheckCircle2,
  AlertTriangle,
  Lock,
  ArrowRight,
  ShieldCheck,
  Clock,
  Sparkles,
  Layers,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { ProductItem, CommercialBreakdown, MSMEProfileSlots } from "../types";
import { fetchProducts, calculateQuote, optimizeBudget } from "../api";

interface CPQCartProps {
  profileSlots?: MSMEProfileSlots | null;
  recommendedSkus?: string[];
  onProceedToKYC: (quote: CommercialBreakdown) => void;
}

export const CPQCart: React.FC<CPQCartProps> = ({
  profileSlots,
  recommendedSkus = [],
  onProceedToKYC,
}) => {
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [selectedProductIds, setSelectedProductIds] = useState<string[]>([]);
  const [contractMonths, setContractMonths] = useState<number>(12);
  const [budgetSlider, setBudgetSlider] = useState<number>(2500);
  const [quote, setQuote] = useState<CommercialBreakdown | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [optimizing, setOptimizing] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"blueprint" | "catalogue">("blueprint");

  const initializedRef = React.useRef(false);

  // Initial products fetch
  useEffect(() => {
    async function load() {
      const prods = await fetchProducts();
      setProducts(prods);

      if (!initializedRef.current) {
        if (recommendedSkus.length > 0) {
          setSelectedProductIds(recommendedSkus);
        } else if (profileSlots?.has_gstin === false) {
          setSelectedProductIds(["P02", "P17", "P22"]); // Kirana bundle (GST-free)
        } else {
          setSelectedProductIds(["P01", "P11", "P16", "P22"]); // Smart Office standard
        }
        initializedRef.current = true;
      }
    }
    load();
  }, [recommendedSkus, profileSlots]);

  // Update selection if advisor recommendations arrive
  useEffect(() => {
    if (recommendedSkus.length > 0) {
      setSelectedProductIds(recommendedSkus);
    }
  }, [recommendedSkus]);

  // Recalculate quote whenever cart or contract changes
  useEffect(() => {
    if (selectedProductIds.length === 0) {
      setQuote(null);
      return;
    }

    async function recalc() {
      setLoading(true);
      setErrorMessage(null);
      try {
        const cartItems = selectedProductIds.map((id) => ({ product_id: id, quantity: 1 }));
        const res = await calculateQuote(cartItems, contractMonths);
        setQuote(res);
      } catch (err: unknown) {
        setErrorMessage(err instanceof Error ? err.message : "Failed to calculate quote");
      } finally {
        setLoading(false);
      }
    }
    recalc();
  }, [selectedProductIds, contractMonths]);

  const toggleProduct = (productId: string) => {
    setSelectedProductIds((prev) =>
      prev.includes(productId) ? prev.filter((id) => id !== productId) : [...prev, productId]
    );
  };

  const handleRunBudgetOptimizer = async () => {
    setOptimizing(true);
    setErrorMessage(null);
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
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : "Budget optimization failed");
    } finally {
      setOptimizing(false);
    }
  };

  // Group products by category
  const categories = Array.from(new Set(products.map((p) => p.category)));

  return (
    <div className="space-y-4">
      {/* Studio Header & View Switcher */}
      <div className="flex items-center justify-between pb-1 border-b border-white/[0.06]">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-[#e40000] shadow-[0_0_8px_rgba(228,0,0,0.8)]" />
          <h3 className="font-serif text-base font-medium text-white tracking-tight">
            Live Telecom Solution Blueprint
          </h3>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center space-x-1 bg-[#121210] p-1 rounded-full border border-white/[0.08]">
          <button
            onClick={() => setActiveTab("blueprint")}
            className={`px-3 py-1 rounded-full text-[11px] font-medium transition-all cursor-pointer ${
              activeTab === "blueprint"
                ? "bg-[#e40000] text-white shadow-[0_0_12px_rgba(228,0,0,0.4)]"
                : "text-white/50 hover:text-white"
            }`}
          >
            Active Solution ({selectedProductIds.length})
          </button>
          <button
            onClick={() => setActiveTab("catalogue")}
            className={`px-3 py-1 rounded-full text-[11px] font-medium transition-all cursor-pointer ${
              activeTab === "catalogue"
                ? "bg-[#e40000] text-white shadow-[0_0_12px_rgba(228,0,0,0.4)]"
                : "text-white/50 hover:text-white"
            }`}
          >
            Explore 25 SKUs
          </button>
        </div>
      </div>

      {activeTab === "blueprint" ? (
        /* TAB 1: ACTIVE SOLUTION BLUEPRINT & REVERSE BUDGET SOLVER */
        <div className="space-y-5 animate-in fade-in duration-200">
          {/* Reverse Budget "Mera Budget ₹X Hai" Solver Banner */}
          <div className="glass-card rounded-2xl p-5 relative overflow-hidden border border-white/[0.08]">
            <div className="flex items-center justify-between mb-2.5">
              <div className="flex items-center space-x-2">
                <Sliders className="w-4 h-4 text-[#e40000]" />
                <h4 className="font-serif text-base font-normal text-white">Reverse Budget Optimizer</h4>
              </div>
              <span className="text-[11px] font-mono bg-[#e40000]/10 text-[#e40000] border border-[#e40000]/30 px-2.5 py-0.5 rounded-full font-medium">
                Mera Budget ₹{budgetSlider.toLocaleString()}/mo
              </span>
            </div>
            <p className="text-[11px] text-white/50 mb-3 leading-relaxed">
              Branch-and-Bound algorithm computes the highest-utility, DAG-legal telecom bundle within your budget in &lt;10ms.
            </p>

            <div className="space-y-2.5 bg-[#0a0a09]/80 p-3.5 rounded-xl border border-white/[0.05]">
              <div className="flex items-center justify-between text-[11px] text-white/40 font-mono">
                <span>₹1,000 / mo</span>
                <span className="text-sm font-serif font-medium text-[#e40000] tracking-tight">
                  ₹{budgetSlider.toLocaleString()}
                </span>
                <span>₹50,000 / mo</span>
              </div>
              <input
                type="range"
                min="1000"
                max="50000"
                step="500"
                value={budgetSlider}
                onChange={(e) => setBudgetSlider(Number(e.target.value))}
                className="w-full h-1.5 bg-[#1a1a18] rounded-lg appearance-none cursor-pointer accent-[#e40000]"
              />
            </div>

            <div className="mt-3.5 flex items-center justify-between">
              <button
                onClick={handleRunBudgetOptimizer}
                disabled={optimizing}
                className="flex items-center space-x-1.5 bg-[#e40000] hover:bg-[#b30000] text-white px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all shadow-[0_0_12px_rgba(228,0,0,0.3)] disabled:opacity-50 cursor-pointer"
              >
                <Zap className="w-3.5 h-3.5" />
                <span>{optimizing ? "Solving..." : "Compute Best Bundle"}</span>
              </button>
              <span className="text-[10px] text-white/40 font-mono">
                DAG &amp; Firewall Enforced
              </span>
            </div>
          </div>

          {/* Configured Commercials Card */}
          <div className="glass-card rounded-2xl p-5 space-y-4 border border-white/[0.08]">
            {/* Contract Commitment Selector */}
            <div className="flex items-center justify-between bg-[#0a0a09]/70 p-2.5 rounded-xl border border-white/[0.05]">
              <span className="text-xs text-white/60 font-medium">Contract Commitment:</span>
              <div className="flex space-x-1">
                {[1, 12, 24].map((months) => (
                  <button
                    key={months}
                    onClick={() => setContractMonths(months)}
                    className={`px-2.5 py-0.5 rounded-lg text-xs font-mono transition-all cursor-pointer ${
                      contractMonths === months
                        ? "bg-[#e40000] text-white shadow-[0_0_10px_rgba(228,0,0,0.4)]"
                        : "text-white/40 hover:text-white bg-white/[0.04]"
                    }`}
                  >
                    {months} {months === 1 ? "Mo" : "Months"}
                  </button>
                ))}
              </div>
            </div>

            {contractMonths >= 12 && (
              <p className="text-[11px] text-emerald-400 flex items-center space-x-1.5">
                <Sparkles className="w-3.5 h-3.5 text-[#d9ad63] shrink-0" />
                <span>100% One-Time Setup Fee (OTC) Waived for 12+ Months!</span>
              </p>
            )}

            {/* Dependency Locks Warning Box */}
            {(() => {
              const missingLocks = quote ? quote.dependency_locks.filter((l) => l.missing) : [];
              if (missingLocks.length === 0) return null;
              return (
                <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200 space-y-1">
                  <div className="flex items-center space-x-1.5 font-medium text-xs">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                    <span>Prerequisite SKU Missing (CPQ DAG Lock)</span>
                  </div>
                  {missingLocks.map((lock) => (
                    <p key={lock.dependent_sku} className="text-[10px] leading-relaxed text-amber-300/80">
                      • <strong>{lock.dependent_name}</strong> requires an active connectivity base (
                      {lock.required_one_of.join(" or ")}).
                    </p>
                  ))}
                </div>
              );
            })()}

            {/* Itemized Cart List */}
            <div className="divide-y divide-white/[0.05] max-h-52 overflow-y-auto pr-1">
              {quote && quote.items.length > 0 ? (
                quote.items.map((item) => (
                  <div key={item.product_id} className="py-2.5 flex items-center justify-between text-xs">
                    <div>
                      <div className="flex items-center space-x-1.5">
                        <span className="font-medium text-white/90">{item.product_name}</span>
                        <span className="text-[9px] font-mono text-white/40 bg-white/[0.04] px-1.5 py-0.2 rounded">
                          {item.product_id}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2 text-[10px] text-white/40 mt-0.5">
                        <span>{item.category}</span>
                        <span>•</span>
                        <span className="font-mono">{item.install_days}d SLA</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="font-serif font-medium text-white text-sm">
                        ₹{item.total_mrc_inr.toLocaleString()}
                      </span>
                      <span className="text-[10px] text-white/40 block">/ mo</span>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-xs text-white/40 py-6 text-center">No products selected.</p>
              )}
            </div>

            {/* Commercial Math Breakdown */}
            {quote && (
              <div className="pt-3 border-t border-white/[0.06] space-y-2 text-xs">
                <div className="flex justify-between text-white/50">
                  <span>Gross Monthly (MRC):</span>
                  <span className="font-mono">₹{quote.gross_mrc_inr.toLocaleString()}</span>
                </div>
                {quote.bundle_discount_inr > 0 && (
                  <div className="flex justify-between text-[#d9ad63]">
                    <span>Multi-Category Bundle Discount:</span>
                    <span className="font-mono font-medium">- ₹{quote.bundle_discount_inr.toLocaleString()}</span>
                  </div>
                )}
                <div className="flex justify-between text-white/50">
                  <span>One-Time Setup (OTC):</span>
                  <span>
                    {quote.net_otc_inr === 0 ? (
                      <span className="text-emerald-400 font-mono">
                        ₹0 <span className="text-[9px] text-emerald-400/70">(WAIVED)</span>
                      </span>
                    ) : (
                      <span className="font-mono">₹{quote.net_otc_inr.toLocaleString()}</span>
                    )}
                  </span>
                </div>

                <div className="flex justify-between items-baseline pt-2.5 border-t border-white/[0.06]">
                  <div>
                    <span className="font-serif text-sm font-normal text-white">Net Monthly Total:</span>
                    <p className="text-[9px] text-white/40 font-mono">Excl. applicable GST</p>
                  </div>
                  <div className="text-right">
                    <span className="font-serif text-2xl font-medium text-white tracking-tight">
                      ₹{quote.net_mrc_inr.toLocaleString()}
                    </span>
                    <span className="text-[10px] text-white/40 block">/ month</span>
                  </div>
                </div>

                {/* SLA & GST-Exempt Badges */}
                <div className="grid grid-cols-2 gap-2 pt-2">
                  <div className="bg-[#0a0a09]/70 p-2 rounded-xl border border-white/[0.05] flex items-center space-x-2">
                    <Clock className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                    <div>
                      <span className="text-[9px] text-white/40 block">Guaranteed SLA</span>
                      <span className="text-xs font-mono font-medium text-white">
                        {quote.guaranteed_sla_days} Days
                      </span>
                    </div>
                  </div>
                  <div className="bg-[#0a0a09]/70 p-2 rounded-xl border border-white/[0.05] flex items-center space-x-2">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                    <div>
                      <span className="text-[9px] text-white/40 block">Non-GST Pathway</span>
                      <span className="text-xs font-mono font-medium text-emerald-400">
                        {quote.gst_exempt_eligible ? "Eligible (Kirana)" : "GSTIN Mandated"}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Action Button: Proceed to Smart KYC */}
            <div className="pt-2">
              <button
                onClick={() => quote && onProceedToKYC(quote)}
                disabled={
                  !quote ||
                  quote.dependency_locks.filter((l) => l.missing).length > 0 ||
                  loading
                }
                className="w-full flex items-center justify-center space-x-2 bg-[#e40000] hover:bg-[#b30000] text-white font-medium py-3 px-4 rounded-xl shadow-[0_0_16px_rgba(228,0,0,0.4)] transition-all disabled:opacity-40 disabled:cursor-not-allowed text-xs sm:text-sm cursor-pointer"
              >
                <span>Accept Quote &amp; Start Smart KYC</span>
                <ArrowRight className="w-4 h-4" />
              </button>
              <p className="text-[10px] text-white/40 text-center mt-2 font-mono">
                Zero-delay digital sign-off • Solves 56% PDF quote dropout
              </p>
            </div>
          </div>
        </div>
      ) : (
        /* TAB 2: EXPLORE ALL 25 SKUs */
        <div className="space-y-4 max-h-[600px] overflow-y-auto pr-1">
          {categories.map((cat) => {
            const catProds = products.filter((p) => p.category === cat);
            return (
              <div key={cat} className="glass-card rounded-xl p-4 space-y-3 border border-white/[0.06]">
                <div className="flex items-center justify-between pb-1.5 border-b border-white/[0.05]">
                  <h4 className="font-serif text-sm font-normal text-white tracking-wide">{cat}</h4>
                  <span className="text-[10px] font-mono text-white/40">{catProds.length} SKUs</span>
                </div>

                <div className="space-y-2">
                  {catProds.map((prod) => {
                    const isSelected = selectedProductIds.includes(prod.product_id);
                    const isGstMandatory = prod.requires_gstin;
                    const isNonGstUser = profileSlots?.has_gstin === false;
                    const isGstBlocked = isGstMandatory && isNonGstUser;

                    return (
                      <div
                        key={prod.product_id}
                        onClick={() => !isGstBlocked && toggleProduct(prod.product_id)}
                        className={`p-3 rounded-lg border transition-all cursor-pointer ${
                          isGstBlocked
                            ? "border-white/[0.03] bg-black/40 opacity-40 cursor-not-allowed"
                            : isSelected
                            ? "border-[#e40000]/70 bg-[#e40000]/10 shadow-[0_0_12px_rgba(228,0,0,0.2)]"
                            : "border-white/[0.05] bg-[#0c0c0b] hover:border-white/[0.14]"
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div>
                            <div className="flex items-center space-x-1.5">
                              <span className="font-medium text-xs text-white">{prod.product_name}</span>
                              <span className="text-[9px] font-mono text-white/40 bg-white/[0.04] px-1 py-0.2 rounded">
                                {prod.product_id}
                              </span>
                            </div>
                            <p className="text-[10px] text-white/50 line-clamp-1 mt-0.5">{prod.description}</p>
                          </div>
                          <div
                            className={`w-4 h-4 rounded flex items-center justify-center border transition-all ${
                              isSelected ? "bg-[#e40000] border-[#e40000] text-white" : "border-white/20"
                            }`}
                          >
                            {isSelected && <CheckCircle2 className="w-3 h-3" />}
                          </div>
                        </div>

                        <div className="mt-2 pt-1.5 border-t border-white/[0.04] flex items-center justify-between text-[11px]">
                          <span className="font-serif font-medium text-white">
                            ₹{prod.price_min_inr_per_month.toLocaleString()} / mo
                          </span>
                          <span className="text-[9px] font-mono text-white/40">{prod.typical_install_days}d SLA</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
