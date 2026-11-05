import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  Sliders,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  ShieldCheck,
  Clock,
  Sparkles,
  Zap,
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
  const [activeTab, setActiveTab] = useState<"blueprint" | "catalogue">("blueprint");

  const initializedRef = React.useRef(false);

  useEffect(() => {
    async function load() {
      const prods = await fetchProducts();
      setProducts(prods);

      if (!initializedRef.current) {
        if (recommendedSkus.length > 0) {
          setSelectedProductIds(recommendedSkus);
        } else if (profileSlots?.has_gstin === false) {
          setSelectedProductIds(["P02", "P17", "P22"]);
        } else {
          setSelectedProductIds(["P01", "P11", "P16", "P22"]);
        }
        initializedRef.current = true;
      }
    }
    load();
  }, [recommendedSkus, profileSlots]);

  useEffect(() => {
    if (recommendedSkus.length > 0) {
      setSelectedProductIds(recommendedSkus);
    }
  }, [recommendedSkus]);

  useEffect(() => {
    if (selectedProductIds.length === 0) {
      setQuote(null);
      return;
    }

    async function recalc() {
      setLoading(true);
      try {
        const cartItems = selectedProductIds.map((id) => ({ product_id: id, quantity: 1 }));
        const res = await calculateQuote(cartItems, contractMonths);
        setQuote(res);
      } catch (err: unknown) {
        console.error(err);
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
      console.error(err);
    } finally {
      setOptimizing(false);
    }
  };

  const categories = Array.from(new Set(products.map((p) => p.category)));

  return (
    <div className="space-y-4">
      {/* Blueprint Header */}
      <div className="flex items-center justify-between pb-1 border-b border-[rgba(235,229,217,0.06)]">
        <div className="flex items-center space-x-2">
          <div className="w-1.5 h-1.5 rounded-full bg-[#e40000]" />
          <h3 className="font-sans text-sm font-medium text-[#EBE5D9]">
            Live Solution Blueprint
          </h3>
        </div>

        {/* View Switcher */}
        <div className="flex items-center space-x-1 bg-[#080a0d] p-1 rounded-full border border-[rgba(235,229,217,0.06)]">
          <button
            onClick={() => setActiveTab("blueprint")}
            className={`px-3 py-0.5 rounded-full text-[11px] font-medium transition-colors cursor-pointer ${
              activeTab === "blueprint"
                ? "bg-[#e40000] text-white shadow-[0_0_12px_rgba(228,0,0,0.4)]"
                : "text-[#B39D82] hover:text-[#EBE5D9]"
            }`}
          >
            Active ({selectedProductIds.length})
          </button>
          <button
            onClick={() => setActiveTab("catalogue")}
            className={`px-3 py-0.5 rounded-full text-[11px] font-medium transition-colors cursor-pointer ${
              activeTab === "catalogue"
                ? "bg-[#e40000] text-white shadow-[0_0_12px_rgba(228,0,0,0.4)]"
                : "text-[#B39D82] hover:text-[#EBE5D9]"
            }`}
          >
            Catalogue (25)
          </button>
        </div>
      </div>

      <AnimatePresence mode="wait">
        {activeTab === "blueprint" ? (
          <motion.div
            key="blueprint"
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
            className="space-y-4"
          >
            {/* Reverse Budget Solver Card */}
            <div className="luxury-glass rounded-2xl p-4 space-y-3 border border-[rgba(235,229,217,0.06)] shadow-apple-card">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2 text-xs font-medium text-[#EBE5D9]">
                  <Sliders className="w-3.5 h-3.5 text-[#e40000]" />
                  <span>Reverse Budget Solver</span>
                </div>
                <span className="font-mono text-xs text-[#EBE5D9] bg-[#030405] px-2.5 py-0.5 rounded-full border border-white/[0.06]">
                  ₹{budgetSlider.toLocaleString()}/mo
                </span>
              </div>

              <div className="space-y-2 bg-[#030405]/80 p-3 rounded-xl border border-[rgba(235,229,217,0.04)]">
                <div className="flex items-center justify-between text-[10px] text-[#B39D82] font-mono">
                  <span>₹1,000</span>
                  <span className="font-serif text-sm font-normal text-[#EBE5D9]">₹{budgetSlider.toLocaleString()}</span>
                  <span>₹50,000</span>
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
              </div>

              <div className="flex items-center justify-between">
                <motion.button
                  whileHover={{ scale: 1.03 }}
                  whileTap={{ scale: 0.97 }}
                  onClick={handleRunBudgetOptimizer}
                  disabled={optimizing}
                  className="flex items-center space-x-1.5 bg-[#e40000] hover:bg-[#b30000] text-white px-3 py-1.5 rounded-xl text-xs font-medium shadow-[0_0_12px_rgba(228,0,0,0.3)] disabled:opacity-40 cursor-pointer"
                >
                  <Zap className="w-3.5 h-3.5" />
                  <span>{optimizing ? "Solving..." : "Optimize Bundle"}</span>
                </motion.button>
                <span className="text-[10px] text-[#B39D82] font-mono">
                  DAG &amp; Firewall Validated
                </span>
              </div>
            </div>

            {/* Commercials Card */}
            <div className="luxury-glass rounded-2xl p-5 space-y-4 border border-[rgba(235,229,217,0.06)] shadow-apple-card">
              {/* Commitment Pill Selector */}
              <div className="flex items-center justify-between bg-[#030405]/80 p-2 rounded-xl border border-[rgba(235,229,217,0.04)]">
                <span className="text-xs text-[#B39D82]">Contract Tenure:</span>
                <div className="flex space-x-1">
                  {[1, 12, 24].map((m) => (
                    <button
                      key={m}
                      onClick={() => setContractMonths(m)}
                      className={`px-2.5 py-0.5 rounded-lg text-xs font-mono transition-colors cursor-pointer ${
                        contractMonths === m
                          ? "bg-[#e40000] text-white"
                          : "text-[#B39D82] hover:text-[#EBE5D9]"
                      }`}
                    >
                      {m}M
                    </button>
                  ))}
                </div>
              </div>

              {contractMonths >= 12 && (
                <p className="text-[11px] text-emerald-400 flex items-center space-x-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-[#d9ad63] shrink-0" />
                  <span>100% Setup Fee (OTC) Waived for 12+ Months!</span>
                </p>
              )}

              {/* Dependency Warning */}
              {(() => {
                const missing = quote ? quote.dependency_locks.filter((l) => l.missing) : [];
                if (missing.length === 0) return null;
                return (
                  <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/25 text-amber-200 text-xs space-y-1">
                    <div className="flex items-center space-x-1.5 font-medium">
                      <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                      <span>Missing Base SKU</span>
                    </div>
                    {missing.map((l) => (
                      <p key={l.dependent_sku} className="text-[10px] text-amber-300/80">
                        • {l.dependent_name} requires {l.required_one_of.join(" or ")}.
                      </p>
                    ))}
                  </div>
                );
              })()}

              {/* Itemized SKUs */}
              <div className="divide-y divide-[rgba(235,229,217,0.04)] max-h-48 overflow-y-auto pr-1">
                {quote && quote.items.length > 0 ? (
                  quote.items.map((item) => (
                    <div key={item.product_id} className="py-2 flex items-center justify-between text-xs">
                      <div>
                        <span className="font-medium text-[#EBE5D9]">{item.product_name}</span>
                        <div className="flex items-center space-x-2 text-[10px] text-[#B39D82]">
                          <span>{item.category}</span>
                          <span>•</span>
                          <span className="font-mono">{item.install_days}d SLA</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="font-serif font-medium text-[#EBE5D9]">
                          ₹{item.total_mrc_inr.toLocaleString()}
                        </span>
                        <span className="text-[10px] text-[#B39D82] block">/mo</span>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-[#B39D82] py-4 text-center">No products selected.</p>
                )}
              </div>

              {/* Price Breakdown */}
              {quote && (
                <div className="pt-3 border-t border-[rgba(235,229,217,0.06)] space-y-1.5 text-xs">
                  <div className="flex justify-between text-[#B39D82]">
                    <span>Monthly Gross:</span>
                    <span className="font-mono">₹{quote.gross_mrc_inr.toLocaleString()}</span>
                  </div>
                  {quote.bundle_discount_inr > 0 && (
                    <div className="flex justify-between text-[#d9ad63]">
                      <span>Bundle Discount:</span>
                      <span className="font-mono font-medium">- ₹{quote.bundle_discount_inr.toLocaleString()}</span>
                    </div>
                  )}

                  <div className="flex justify-between items-baseline pt-2 border-t border-[rgba(235,229,217,0.06)]">
                    <div>
                      <span className="text-xs text-[#B39D82] block">Net Monthly:</span>
                      <span className="text-[9px] text-[#B39D82]/60 font-mono">Excl. GST</span>
                    </div>
                    <div className="text-right">
                      <span className="font-serif text-3xl font-normal text-[#EBE5D9] tracking-tight">
                        ₹{quote.net_mrc_inr.toLocaleString()}
                      </span>
                      <span className="text-[10px] text-[#B39D82] block">/ month</span>
                    </div>
                  </div>

                  {/* Badges */}
                  <div className="grid grid-cols-2 gap-2 pt-2">
                    <div className="bg-[#030405] p-2 rounded-xl border border-[rgba(235,229,217,0.04)] flex items-center space-x-2">
                      <Clock className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                      <div>
                        <span className="text-[9px] text-[#B39D82] block">SLA</span>
                        <span className="text-xs font-mono font-medium text-[#EBE5D9]">
                          {quote.guaranteed_sla_days} Days
                        </span>
                      </div>
                    </div>
                    <div className="bg-[#030405] p-2 rounded-xl border border-[rgba(235,229,217,0.04)] flex items-center space-x-2">
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      <div>
                        <span className="text-[9px] text-[#B39D82] block">Compliance</span>
                        <span className="text-xs font-mono font-medium text-emerald-400">
                          {quote.gst_exempt_eligible ? "Non-GST Ready" : "GSTIN Mandated"}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Action Button */}
              <div className="pt-2">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => quote && onProceedToKYC(quote)}
                  disabled={
                    !quote ||
                    quote.dependency_locks.filter((l) => l.missing).length > 0 ||
                    loading
                  }
                  className="w-full flex items-center justify-center space-x-2 bg-[#e40000] hover:bg-[#b30000] text-white font-medium py-3 px-4 rounded-xl shadow-[0_0_16px_rgba(228,0,0,0.4)] transition-all disabled:opacity-30 disabled:cursor-not-allowed text-xs sm:text-sm cursor-pointer"
                >
                  <span>Start Smart KYC Gate</span>
                  <ArrowRight className="w-4 h-4" />
                </motion.button>
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="catalogue"
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
            className="space-y-3 max-h-[580px] overflow-y-auto pr-1"
          >
            {categories.map((cat) => {
              const catProds = products.filter((p) => p.category === cat);
              return (
                <div key={cat} className="luxury-glass rounded-xl p-3 space-y-2 border border-[rgba(235,229,217,0.06)]">
                  <div className="flex items-center justify-between pb-1 border-b border-[rgba(235,229,217,0.04)]">
                    <h4 className="font-sans text-xs font-medium text-[#EBE5D9]">{cat}</h4>
                    <span className="text-[9px] font-mono text-[#B39D82]">{catProds.length} SKUs</span>
                  </div>

                  <div className="space-y-1.5">
                    {catProds.map((prod) => {
                      const isSelected = selectedProductIds.includes(prod.product_id);
                      const isGstMandatory = prod.requires_gstin;
                      const isNonGstUser = profileSlots?.has_gstin === false;
                      const isGstBlocked = isGstMandatory && isNonGstUser;

                      return (
                        <motion.div
                          key={prod.product_id}
                          whileHover={{ scale: 1.01 }}
                          whileTap={{ scale: 0.99 }}
                          onClick={() => !isGstBlocked && toggleProduct(prod.product_id)}
                          className={`p-2.5 rounded-lg border transition-all cursor-pointer ${
                            isGstBlocked
                              ? "border-white/[0.03] bg-black/40 opacity-40 cursor-not-allowed"
                              : isSelected
                              ? "border-[#e40000] bg-[#e40000]/10 shadow-[0_0_12px_rgba(228,0,0,0.2)]"
                              : "border-[rgba(235,229,217,0.04)] bg-[#080a0d] hover:border-[rgba(235,229,217,0.12)]"
                          }`}
                        >
                          <div className="flex items-start justify-between">
                            <div>
                              <div className="flex items-center space-x-1.5">
                                <span className="font-medium text-xs text-[#EBE5D9]">{prod.product_name}</span>
                                <span className="text-[9px] font-mono text-[#B39D82] bg-white/[0.04] px-1 py-0.2 rounded">
                                  {prod.product_id}
                                </span>
                              </div>
                              <p className="text-[10px] text-[#B39D82] line-clamp-1 mt-0.5">{prod.description}</p>
                            </div>
                            <div
                              className={`w-4 h-4 rounded flex items-center justify-center border transition-all ${
                                isSelected ? "bg-[#e40000] border-[#e40000] text-white" : "border-white/20"
                              }`}
                            >
                              {isSelected && <CheckCircle2 className="w-3 h-3" />}
                            </div>
                          </div>

                          <div className="mt-1.5 pt-1 border-t border-[rgba(235,229,217,0.04)] flex items-center justify-between text-[11px]">
                            <span className="font-serif font-medium text-[#EBE5D9]">
                              ₹{prod.price_min_inr_per_month.toLocaleString()} / mo
                            </span>
                            <span className="text-[9px] font-mono text-[#B39D82]">{prod.typical_install_days}d SLA</span>
                          </div>
                        </motion.div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
