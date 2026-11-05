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
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 animate-fade-in">
      {/* Left Column: Interactive Product Catalogue & Reverse Budget Solver */}
      <div className="lg:col-span-7 space-y-6">
        {/* Reverse Budget "Mera Budget ₹X Hai" Solver Banner */}
        <div className="glass-card rounded-2xl p-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-72 h-72 bg-airtel-crimson/5 rounded-full blur-3xl pointer-events-none" />
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-lg bg-airtel-crimson/15 border border-airtel-crimson/30 flex items-center justify-center text-airtel-crimson">
                <Sliders className="w-4 h-4" />
              </div>
              <h3 className="font-serif text-lg font-normal text-white">Reverse Budget Optimizer</h3>
            </div>
            <span className="text-xs font-mono bg-airtel-crimson/10 text-airtel-crimson border border-airtel-crimson/30 px-3 py-1 rounded-full font-medium">
              "Mera Budget ₹{budgetSlider.toLocaleString()}/mo Hai"
            </span>
          </div>
          <p className="text-xs text-white/60 mb-5 leading-relaxed">
            Tell us your monthly spending limit. Our Branch-and-Bound solver computes the highest-utility, DAG-legal telecom bundle within your exact budget in &lt;10ms.
          </p>

          <div className="space-y-3 bg-obsidian-surface/60 p-4 rounded-xl border border-white/[0.04]">
            <div className="flex items-center justify-between text-xs text-white/50 font-mono">
              <span>₹1,000 / mo</span>
              <span className="text-base font-serif font-medium text-airtel-crimson tracking-tight">₹{budgetSlider.toLocaleString()}</span>
              <span>₹50,000 / mo</span>
            </div>
            <input
              type="range"
              min="1000"
              max="50000"
              step="500"
              value={budgetSlider}
              onChange={(e) => setBudgetSlider(Number(e.target.value))}
              className="w-full h-2 bg-obsidian-elevated rounded-lg appearance-none cursor-pointer accent-airtel-crimson focus:outline-none"
            />
          </div>

          <div className="mt-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <button
              onClick={handleRunBudgetOptimizer}
              disabled={optimizing}
              className="flex items-center justify-center space-x-2 bg-airtel-crimson hover:bg-airtel-hover text-white px-5 py-2.5 rounded-xl text-xs sm:text-sm font-medium transition-all shadow-airtel-glow disabled:opacity-50 cursor-pointer"
            >
              <Zap className="w-4 h-4" />
              <span>{optimizing ? "Solving DAG Constraints..." : "Compute Best Bundle"}</span>
            </button>
            <span className="text-[11px] text-white/40 font-mono">
              Enforces GST Firewall &amp; Dependency Graph
            </span>
          </div>
        </div>

        {/* Product SKU Selector by Category */}
        <div className="space-y-6">
          {categories.map((cat) => {
            const catProds = products.filter((p) => p.category === cat);
            return (
              <div key={cat} className="glass-card rounded-2xl p-5">
                <div className="flex items-center justify-between mb-4 pb-2 border-b border-white/[0.06]">
                  <h4 className="font-serif text-base font-normal text-white tracking-wide">
                    {cat}
                  </h4>
                  <span className="text-[11px] font-mono text-white/40 bg-white/[0.04] px-2 py-0.5 rounded-full border border-white/[0.06]">
                    {catProds.length} SKUs
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                  {catProds.map((prod) => {
                    const isSelected = selectedProductIds.includes(prod.product_id);
                    const isGstMandatory = prod.requires_gstin;
                    const isNonGstUser = profileSlots?.has_gstin === false;
                    const isGstBlocked = isGstMandatory && isNonGstUser;

                    return (
                      <div
                        key={prod.product_id}
                        onClick={() => !isGstBlocked && toggleProduct(prod.product_id)}
                        className={`p-4 rounded-xl border transition-all cursor-pointer relative group ${
                          isGstBlocked
                            ? "border-white/[0.04] bg-obsidian-surface/40 opacity-40 cursor-not-allowed"
                            : isSelected
                            ? "border-airtel-crimson/70 bg-airtel-crimson/10 shadow-airtel-glow"
                            : "border-white/[0.06] bg-obsidian-surface/60 hover:border-white/[0.18] hover:bg-obsidian-elevated/70"
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1 pr-2">
                            <div className="flex items-center space-x-1.5">
                              <span className="font-medium text-xs sm:text-sm text-white">
                                {prod.product_name}
                              </span>
                              <span className="text-[10px] bg-white/[0.06] text-white/50 px-1.5 py-0.5 rounded font-mono">
                                {prod.product_id}
                              </span>
                            </div>
                            <p className="text-[11px] text-white/50 line-clamp-2 mt-1.5 leading-relaxed">
                              {prod.description}
                            </p>
                          </div>
                          <div
                            className={`w-5 h-5 rounded-md flex items-center justify-center border transition-all ${
                              isSelected
                                ? "bg-airtel-crimson border-airtel-crimson text-white"
                                : "border-white/[0.12] bg-obsidian-canvas/60 group-hover:border-white/30"
                            }`}
                          >
                            {isSelected && <CheckCircle2 className="w-3.5 h-3.5" />}
                          </div>
                        </div>

                        <div className="mt-3.5 pt-2.5 border-t border-white/[0.06] flex items-center justify-between text-xs">
                          <div>
                            <span className="font-serif text-sm font-medium text-white">
                              ₹{prod.price_min_inr_per_month.toLocaleString()}
                            </span>
                            <span className="text-white/40 text-[10px]"> / month</span>
                          </div>

                          <div className="flex items-center space-x-1.5">
                            {prod.requires_gstin ? (
                              <span className="text-[9px] bg-amber-500/10 text-amber-300 border border-amber-500/20 px-2 py-0.5 rounded-full font-mono">
                                GST Mandatory
                              </span>
                            ) : (
                              <span className="text-[9px] bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 px-2 py-0.5 rounded-full font-mono">
                                Non-GST Eligible
                              </span>
                            )}
                            <span className="text-[9px] text-white/40 bg-white/[0.04] px-1.5 py-0.5 rounded font-mono">
                              {prod.typical_install_days}d SLA
                            </span>
                          </div>
                        </div>

                        {isGstBlocked && (
                          <div className="mt-2.5 text-[10px] text-amber-400/90 flex items-center space-x-1 font-mono">
                            <Lock className="w-3 h-3 shrink-0" />
                            <span>GSTIN Required (Firewall Active)</span>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Right Column: Dynamic Quote Commercials & Dependency Lock State */}
      <div className="lg:col-span-5 space-y-5">
        <div className="glass-card rounded-2xl p-6 sticky top-24">
          <div className="flex items-center justify-between pb-4 border-b border-white/[0.06]">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-lg bg-airtel-crimson/15 border border-airtel-crimson/30 flex items-center justify-center text-airtel-crimson">
                <ShoppingCart className="w-4 h-4" />
              </div>
              <h3 className="font-serif text-lg font-normal text-white">Configured Solution</h3>
            </div>
            <span className="text-xs bg-white/[0.04] text-white/70 border border-white/[0.08] px-2.5 py-1 rounded-full font-mono">
              {selectedProductIds.length} SKUs Selected
            </span>
          </div>

          {/* Contract Tenure Selector */}
          <div className="mt-5 flex items-center justify-between bg-obsidian-surface/60 p-3 rounded-xl border border-white/[0.06]">
            <span className="text-xs text-white/70 font-medium">Contract Commitment:</span>
            <div className="flex space-x-1">
              {[1, 12, 24].map((months) => (
                <button
                  key={months}
                  onClick={() => setContractMonths(months)}
                  className={`px-3 py-1 rounded-lg text-xs font-mono transition-all cursor-pointer ${
                    contractMonths === months
                      ? "bg-airtel-crimson text-white shadow-airtel-glow"
                      : "text-white/50 hover:text-white bg-white/[0.04] hover:bg-white/[0.08]"
                  }`}
                >
                  {months} {months === 1 ? "Mo" : "Months"}
                </button>
              ))}
            </div>
          </div>
          {contractMonths >= 12 && (
            <p className="text-[11px] text-emerald-400 mt-2 flex items-center space-x-1.5">
              <Sparkles className="w-3.5 h-3.5 shrink-0 text-champagne-gold" />
              <span>100% One-Time Setup Fee (OTC) Waived for 12+ Months!</span>
            </p>
          )}

          {/* Dependency Locks Warning Box */}
          {(() => {
            const missingLocks = quote ? quote.dependency_locks.filter((l) => l.missing) : [];
            if (missingLocks.length === 0) return null;
            return (
              <div className="mt-4 p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200 space-y-1.5">
                <div className="flex items-center space-x-2 font-medium text-xs">
                  <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
                  <span>Prerequisite SKU Missing (CPQ DAG Lock)</span>
                </div>
                {missingLocks.map((lock) => (
                  <p key={lock.dependent_sku} className="text-[11px] leading-relaxed text-amber-300/80">
                    • <strong>{lock.dependent_name}</strong> requires an active connectivity base (
                    {lock.required_one_of.join(" or ")}).
                  </p>
                ))}
              </div>
            );
          })()}

          {/* Itemized Cart List */}
          <div className="mt-4 divide-y divide-white/[0.06] max-h-56 overflow-y-auto pr-1">
            {quote && quote.items.length > 0 ? (
              quote.items.map((item) => (
                <div key={item.product_id} className="py-2.5 flex items-center justify-between text-xs">
                  <div>
                    <span className="font-medium text-white/90">{item.product_name}</span>
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
            <div className="mt-5 pt-4 border-t border-white/[0.08] space-y-2 text-xs">
              <div className="flex justify-between text-white/60">
                <span>Gross Monthly (MRC):</span>
                <span className="font-mono">₹{quote.gross_mrc_inr.toLocaleString()}</span>
              </div>
              {quote.bundle_discount_inr > 0 && (
                <div className="flex justify-between text-champagne-gold">
                  <span>Multi-Category Bundle Discount:</span>
                  <span className="font-mono font-medium">- ₹{quote.bundle_discount_inr.toLocaleString()}</span>
                </div>
              )}
              <div className="flex justify-between text-white/60">
                <span>One-Time Setup (OTC):</span>
                <span>
                  {quote.net_otc_inr === 0 ? (
                    <span className="text-emerald-400 font-mono">
                      ₹0 <span className="text-[10px] text-emerald-400/70">(WAIVED)</span>
                    </span>
                  ) : (
                    <span className="font-mono">₹{quote.net_otc_inr.toLocaleString()}</span>
                  )}
                </span>
              </div>
              <div className="flex justify-between items-baseline pt-3 border-t border-white/[0.08]">
                <div>
                  <span className="font-serif text-base font-normal text-white">Net Monthly Total:</span>
                  <p className="text-[10px] text-white/40">Excl. applicable statutory taxes</p>
                </div>
                <div className="text-right">
                  <span className="font-serif text-3xl font-medium text-white tracking-tight">
                    ₹{quote.net_mrc_inr.toLocaleString()}
                  </span>
                  <span className="text-xs text-white/40 block">/ month</span>
                </div>
              </div>

              {/* SLA & GST-Exempt Badges */}
              <div className="grid grid-cols-2 gap-2.5 pt-3">
                <div className="bg-obsidian-surface/60 p-2.5 rounded-xl border border-white/[0.06] flex items-center space-x-2.5">
                  <Clock className="w-4 h-4 text-blue-400 shrink-0" />
                  <div>
                    <span className="text-[10px] text-white/40 block">Guaranteed SLA</span>
                    <span className="text-xs font-mono font-medium text-white">
                      {quote.guaranteed_sla_days} Business Days
                    </span>
                  </div>
                </div>
                <div className="bg-obsidian-surface/60 p-2.5 rounded-xl border border-white/[0.06] flex items-center space-x-2.5">
                  <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
                  <div>
                    <span className="text-[10px] text-white/40 block">Non-GST Pathway</span>
                    <span className="text-xs font-mono font-medium text-emerald-400">
                      {quote.gst_exempt_eligible ? "Eligible (Kirana)" : "GSTIN Mandated"}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Action Button: Proceed to Smart KYC */}
          <div className="mt-6">
            <button
              onClick={() => quote && onProceedToKYC(quote)}
              disabled={
                !quote ||
                quote.dependency_locks.filter((l) => l.missing).length > 0 ||
                loading
              }
              className="w-full flex items-center justify-center space-x-2 bg-airtel-crimson hover:bg-airtel-hover text-white font-medium py-3 px-4 rounded-xl shadow-airtel-glow transition-all disabled:opacity-40 disabled:cursor-not-allowed text-xs sm:text-sm cursor-pointer"
            >
              <span>Accept Quote &amp; Start Smart KYC</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <p className="text-[10px] text-white/40 text-center mt-2.5">
              Solves the 56% quoting drop-off by instant digital acceptance &amp; zero PDF delays.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
