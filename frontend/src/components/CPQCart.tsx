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

  // Initial products fetch
  useEffect(() => {
    async function load() {
      const prods = await fetchProducts();
      setProducts(prods);

      // Default selection from recommendations or baseline
      if (recommendedSkus.length > 0) {
        setSelectedProductIds(recommendedSkus);
      } else if (profileSlots?.has_gstin === false) {
        setSelectedProductIds(["P02", "P17", "P22"]); // Kirana bundle (GST-free)
      } else {
        setSelectedProductIds(["P01", "P11", "P16", "P22"]); // Smart Office standard
      }
    }
    load();
  }, [recommendedSkus, profileSlots]);

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
      } catch (err: any) {
        setErrorMessage(err.message || "Failed to calculate quote");
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
    } catch (err: any) {
      setErrorMessage(err.message || "Budget optimization failed");
    } finally {
      setOptimizing(false);
    }
  };

  // Group products by category
  const categories = Array.from(new Set(products.map((p) => p.category)));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
      {/* Left Column: Interactive Product Catalogue & Reverse Budget Solver */}
      <div className="lg:col-span-7 space-y-6">
        {/* Reverse Budget "Mera Budget ₹X Hai" Solver Banner */}
        <div className="bg-gradient-to-r from-red-950/80 via-slate-900 to-slate-900 border border-red-500/30 rounded-2xl p-5 shadow-xl">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <Sliders className="w-5 h-5 text-red-400" />
              <h3 className="text-base font-bold text-white">Reverse Budget Optimizer</h3>
            </div>
            <span className="text-xs bg-red-500/20 text-red-300 border border-red-500/40 px-2.5 py-1 rounded-full font-semibold">
              "Mera Budget ₹{budgetSlider.toLocaleString()}/mo Hai"
            </span>
          </div>
          <p className="text-xs text-slate-300 mb-4">
            Tell us your monthly spending limit. Our Branch-and-Bound solver computes the highest-utility, DAG-legal telecom bundle within your exact budget in &lt;10ms.
          </p>

          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>₹1,000 / mo</span>
              <span className="text-sm font-bold text-red-400">₹{budgetSlider.toLocaleString()}</span>
              <span>₹25,000 / mo</span>
            </div>
            <input
              type="range"
              min="1000"
              max="15000"
              step="500"
              value={budgetSlider}
              onChange={(e) => setBudgetSlider(Number(e.target.value))}
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-red-500"
            />
          </div>

          <div className="mt-4 flex items-center justify-between">
            <button
              onClick={handleRunBudgetOptimizer}
              disabled={optimizing}
              className="flex items-center space-x-2 bg-red-600 hover:bg-red-500 text-white px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all shadow-md shadow-red-600/30 disabled:opacity-50"
            >
              <Zap className="w-4 h-4" />
              <span>{optimizing ? "Solving DAG Constraints..." : "Compute Best Bundle"}</span>
            </button>
            <span className="text-xs text-slate-400">
              Enforces GST Firewall &amp; Dependency Graph
            </span>
          </div>
        </div>

        {/* Product SKU Selector by Category */}
        <div className="space-y-6">
          {categories.map((cat) => {
            const catProds = products.filter((p) => p.category === cat);
            return (
              <div key={cat} className="bg-slate-900 border border-slate-800 rounded-2xl p-4">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-sm font-semibold text-slate-200 tracking-wide uppercase">
                    {cat}
                  </h4>
                  <span className="text-xs text-slate-500">{catProds.length} SKUs</span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {catProds.map((prod) => {
                    const isSelected = selectedProductIds.includes(prod.product_id);
                    const isGstMandatory = prod.requires_gstin;
                    const isNonGstUser = profileSlots?.has_gstin === false;
                    const isGstBlocked = isGstMandatory && isNonGstUser;

                    return (
                      <div
                        key={prod.product_id}
                        onClick={() => !isGstBlocked && toggleProduct(prod.product_id)}
                        className={`p-3.5 rounded-xl border transition-all cursor-pointer relative ${
                          isGstBlocked
                            ? "border-slate-800 bg-slate-950/60 opacity-50 cursor-not-allowed"
                            : isSelected
                            ? "border-red-500/70 bg-red-950/20 shadow-md shadow-red-950/30"
                            : "border-slate-800 bg-slate-800/40 hover:border-slate-700 hover:bg-slate-800/70"
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1 pr-2">
                            <div className="flex items-center space-x-1.5">
                              <span className="font-semibold text-xs sm:text-sm text-white">
                                {prod.product_name}
                              </span>
                              <span className="text-[10px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded font-mono">
                                {prod.product_id}
                              </span>
                            </div>
                            <p className="text-[11px] text-slate-400 line-clamp-2 mt-1">
                              {prod.description}
                            </p>
                          </div>
                          <div
                            className={`w-5 h-5 rounded-md flex items-center justify-center border transition-all ${
                              isSelected
                                ? "bg-red-600 border-red-500 text-white"
                                : "border-slate-700 bg-slate-800"
                            }`}
                          >
                            {isSelected && <CheckCircle2 className="w-3.5 h-3.5" />}
                          </div>
                        </div>

                        <div className="mt-3 pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs">
                          <div>
                            <span className="font-bold text-white">
                              ₹{prod.price_min_inr_per_month.toLocaleString()}
                            </span>
                            <span className="text-slate-400 text-[10px]"> / month</span>
                          </div>

                          <div className="flex items-center space-x-1.5">
                            {prod.requires_gstin ? (
                              <span className="text-[9px] bg-amber-500/10 text-amber-300 border border-amber-500/20 px-1.5 py-0.5 rounded">
                                GST Mandatory
                              </span>
                            ) : (
                              <span className="text-[9px] bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 px-1.5 py-0.5 rounded">
                                Non-GST Eligible
                              </span>
                            )}
                            <span className="text-[9px] text-slate-400 bg-slate-800 px-1.5 py-0.5 rounded">
                              {prod.typical_install_days}d SLA
                            </span>
                          </div>
                        </div>

                        {isGstBlocked && (
                          <div className="mt-2 text-[10px] text-amber-400 flex items-center space-x-1">
                            <Lock className="w-3 h-3" />
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
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl sticky top-20">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <div className="flex items-center space-x-2">
              <ShoppingCart className="w-5 h-5 text-red-500" />
              <h3 className="text-base font-bold text-white">Configured Solution</h3>
            </div>
            <span className="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded-full font-mono">
              {selectedProductIds.length} SKUs Selected
            </span>
          </div>

          {/* Contract Tenure Selector */}
          <div className="mt-4 flex items-center justify-between bg-slate-950/60 p-2.5 rounded-xl border border-slate-800">
            <span className="text-xs text-slate-300 font-medium">Contract Commitment:</span>
            <div className="flex space-x-1">
              {[1, 12, 24].map((months) => (
                <button
                  key={months}
                  onClick={() => setContractMonths(months)}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                    contractMonths === months
                      ? "bg-red-600 text-white shadow-sm"
                      : "text-slate-400 hover:text-white bg-slate-800/60"
                  }`}
                >
                  {months} {months === 1 ? "Mo" : "Months"}
                </button>
              ))}
            </div>
          </div>
          {contractMonths >= 12 && (
            <p className="text-[11px] text-emerald-400 mt-1 flex items-center space-x-1">
              <Sparkles className="w-3 h-3" />
              <span>100% One-Time Setup Fee (OTC) Waived for 12+ Months!</span>
            </p>
          )}

          {/* Dependency Locks Warning Box */}
          {quote && quote.dependency_locks.length > 0 && (
            <div className="mt-4 p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 space-y-1.5">
              <div className="flex items-center space-x-1.5 font-bold text-xs">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <span>Prerequisite SKU Missing (CPQ DAG Lock)</span>
              </div>
              {quote.dependency_locks.map((lock) => (
                <p key={lock.dependent_sku} className="text-[11px] leading-relaxed">
                  • <strong>{lock.dependent_name}</strong> requires an active connectivity base (
                  {lock.required_one_of.join(" or ")}).
                </p>
              ))}
            </div>
          )}

          {/* Itemized Cart List */}
          <div className="mt-4 divide-y divide-slate-800 max-h-56 overflow-y-auto pr-1">
            {quote && quote.items.length > 0 ? (
              quote.items.map((item) => (
                <div key={item.product_id} className="py-2.5 flex items-center justify-between text-xs">
                  <div>
                    <span className="font-medium text-slate-200">{item.product_name}</span>
                    <div className="flex items-center space-x-2 text-[10px] text-slate-400">
                      <span>{item.category}</span>
                      <span>•</span>
                      <span>{item.install_days}d SLA</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="font-semibold text-white">
                      ₹{item.total_mrc_inr.toLocaleString()}
                    </span>
                    <span className="text-[10px] text-slate-400 block">/ mo</span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-500 py-4 text-center">No products selected.</p>
            )}
          </div>

          {/* Commercial Math Breakdown */}
          {quote && (
            <div className="mt-4 pt-4 border-t border-slate-800 space-y-2 text-xs">
              <div className="flex justify-between text-slate-400">
                <span>Gross Monthly (MRC):</span>
                <span>₹{quote.gross_mrc_inr.toLocaleString()}</span>
              </div>
              {quote.bundle_discount_inr > 0 && (
                <div className="flex justify-between text-emerald-400">
                  <span>Multi-Category Bundle Discount:</span>
                  <span>- ₹{quote.bundle_discount_inr.toLocaleString()}</span>
                </div>
              )}
              <div className="flex justify-between text-slate-400">
                <span>One-Time Setup (OTC):</span>
                <span>
                  {quote.net_otc_inr === 0 ? (
                    <span className="text-emerald-400 line-through">
                      ₹{quote.total_otc_inr.toLocaleString()} (WAIVED)
                    </span>
                  ) : (
                    `₹${quote.net_otc_inr.toLocaleString()}`
                  )}
                </span>
              </div>
              <div className="flex justify-between items-baseline pt-2 border-t border-slate-800">
                <div>
                  <span className="text-sm font-bold text-white">Net Monthly Total:</span>
                  <p className="text-[10px] text-slate-400">Excl. applicable statutory taxes</p>
                </div>
                <div className="text-right">
                  <span className="text-2xl font-black text-red-500">
                    ₹{quote.net_mrc_inr.toLocaleString()}
                  </span>
                  <span className="text-xs text-slate-400 block">/ month</span>
                </div>
              </div>

              {/* SLA & GST-Exempt Badges */}
              <div className="grid grid-cols-2 gap-2 pt-2">
                <div className="bg-slate-950/70 p-2 rounded-xl border border-slate-800 flex items-center space-x-2">
                  <Clock className="w-4 h-4 text-blue-400" />
                  <div>
                    <span className="text-[10px] text-slate-400 block">Guaranteed SLA</span>
                    <span className="text-xs font-bold text-white">
                      {quote.guaranteed_sla_days} Business Days
                    </span>
                  </div>
                </div>
                <div className="bg-slate-950/70 p-2 rounded-xl border border-slate-800 flex items-center space-x-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <div>
                    <span className="text-[10px] text-slate-400 block">Non-GST Pathway</span>
                    <span className="text-xs font-bold text-emerald-400">
                      {quote.gst_exempt_eligible ? "Eligible (Kirana)" : "GSTIN Mandated"}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Action Button: Proceed to Smart KYC */}
          <div className="mt-5">
            <button
              onClick={() => quote && onProceedToKYC(quote)}
              disabled={!quote || quote.dependency_locks.length > 0 || loading}
              className="w-full flex items-center justify-center space-x-2 bg-red-600 hover:bg-red-500 text-white font-bold py-3 px-4 rounded-xl shadow-lg shadow-red-600/30 transition-all disabled:opacity-40 disabled:cursor-not-allowed text-sm"
            >
              <span>Accept Quote &amp; Start Smart KYC</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <p className="text-[10px] text-slate-500 text-center mt-2">
              Solves the 56% quoting drop-off by instant digital acceptance &amp; zero PDF delays.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
