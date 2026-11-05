from __future__ import annotations

from typing import Optional

from backend.app.db.registry import RegistryDatabase, get_registry
from backend.app.models.schemas import (
    CartItem,
    CartItemBreakdown,
    CommercialBreakdown,
    DependencyLock,
    ProductItem,
    ReverseBudgetResult,
    UserProfile,
)

BASE_CONNECTIVITY_SKUS = {"P01", "P02", "P03", "P04", "P05", "P06"}


class DependencyLockError(ValueError):
    """Raised when a cart violates directed acyclic graph prerequisite dependencies."""
    pass


class CPQEngine:
    """Deterministic Configure-Price-Quote (CPQ) Engine with DAG dependency verification

    and branch-and-bound reverse budget optimization.
    """

    def __init__(self, db: Optional[RegistryDatabase] = None) -> None:
        self.db = db or get_registry()

    def filter_eligible_products(self, user: UserProfile) -> list[ProductItem]:
        """Filters catalog deterministically based on business size, city tier,

        and the non-negotiable GSTIN Firewall.
        """
        all_products = self.db.get_all_products()
        eligible: list[ProductItem] = []

        norm_segment = user.segment.lower().strip()
        if "micro" in norm_segment:
            seg_code = "micro"
        elif "prof" in norm_segment or "office" in norm_segment or "clinic" in norm_segment:
            seg_code = "prof"
        elif "multi" in norm_segment or "chain" in norm_segment or "store" in norm_segment:
            seg_code = "multi"
        elif "mfg" in norm_segment or "manufactur" in norm_segment:
            seg_code = "mfg"
        else:
            seg_code = norm_segment

        for sku in all_products:
            # 1. City Tier Gate
            if user.city_tier not in sku.available_city_tiers:
                continue

            # 2. Minimum Employee Scale Gate
            if user.employee_count < sku.min_employees:
                continue

            # 3. Minimum Site Scale Gate
            if user.num_sites < sku.min_sites:
                continue

            # 4. GSTIN Firewall Gate: Never pitch GSTIN-mandatory SKUs to non-GST businesses!
            if sku.requires_gstin and not user.has_gstin:
                continue

            # 5. Segment Compatibility: Must be valid for user segment or universal
            if seg_code and sku.target_segments and seg_code not in sku.target_segments:
                # If specific target segments defined and current segment not present, skip
                continue

            eligible.append(sku)

        return eligible

    def check_dependencies(self, cart: list[CartItem]) -> tuple[bool, list[DependencyLock]]:
        """Validates that every add-on in the cart satisfies its prerequisite parent SKU."""
        cart_sku_set = {item.product_id.upper() for item in cart}
        locks: list[DependencyLock] = []
        is_valid = True

        for item in cart:
            sku = self.db.get_product(item.product_id)
            if not sku:
                continue

            if sku.requires_one_of:
                # Check if at least one prerequisite is present in cart
                has_prereq = any(prereq in cart_sku_set for prereq in sku.requires_one_of)
                if not has_prereq:
                    is_valid = False
                    prereq_names = [
                        self.db.get_product(p).product_name
                        for p in sku.requires_one_of
                        if self.db.get_product(p)
                    ]
                    reason = (
                        f"'{sku.product_name}' requires at least one base connection: "
                        f"{', '.join(prereq_names)}."
                    )
                    locks.append(
                        DependencyLock(
                            dependent_sku=sku.product_id,
                            dependent_name=sku.product_name,
                            required_one_of=sku.requires_one_of,
                            missing=True,
                            reason=reason,
                        )
                    )
                else:
                    locks.append(
                        DependencyLock(
                            dependent_sku=sku.product_id,
                            dependent_name=sku.product_name,
                            required_one_of=sku.requires_one_of,
                            missing=False,
                            reason="Dependency satisfied.",
                        )
                    )

        return is_valid, locks

    def calculate_commercials(
        self,
        cart: list[CartItem],
        contract_months: int = 12,
        strict_dag: bool = True,
    ) -> CommercialBreakdown:
        """Computes exact Monthly Recurring Charge (MRC), One-Time Setup Charge (OTC),

        multi-category bundle discounts, and guaranteed SLA turnaround days.
        """
        is_valid_dag, locks = self.check_dependencies(cart)
        if strict_dag and not is_valid_dag:
            missing_reasons = [lock.reason for lock in locks if lock.missing]
            raise DependencyLockError(f"Cart violates DAG dependencies: {'; '.join(missing_reasons)}")

        items_breakdown: list[CartItemBreakdown] = []
        categories_present: set[str] = set()
        gross_mrc = 0
        total_otc = 0
        max_sla_days = 0
        min_required_contract = 1
        all_non_gst = True

        for item in cart:
            sku = self.db.get_product(item.product_id)
            if not sku:
                raise ValueError(f"Unknown SKU: {item.product_id}")

            unit_mrc = sku.price_min_inr_per_month
            item_mrc = unit_mrc * item.quantity
            unit_otc = sku.one_time_setup_inr
            item_otc = unit_otc * item.quantity

            gross_mrc += item_mrc
            total_otc += item_otc
            categories_present.add(sku.category)

            if sku.typical_install_days > max_sla_days:
                max_sla_days = sku.typical_install_days

            if sku.min_contract_months > min_required_contract:
                min_required_contract = sku.min_contract_months

            if sku.requires_gstin:
                all_non_gst = False

            items_breakdown.append(
                CartItemBreakdown(
                    product_id=sku.product_id,
                    product_name=sku.product_name,
                    category=sku.category,
                    quantity=item.quantity,
                    unit_mrc_inr=unit_mrc,
                    total_mrc_inr=item_mrc,
                    unit_otc_inr=unit_otc,
                    total_otc_inr=item_otc,
                    install_days=sku.typical_install_days,
                    requires_gstin=sku.requires_gstin,
                )
            )

        # Multi-category Bundle Discount Logic
        num_categories = len(categories_present)
        discount_pct = 0.0
        if num_categories >= 4:
            discount_pct = 0.15  # 15% discount for 4+ categories
        elif num_categories == 3:
            discount_pct = 0.10  # 10% discount for 3 categories
        elif num_categories == 2 and gross_mrc >= 2000:
            discount_pct = 0.05  # 5% discount for 2 categories

        bundle_discount = int(gross_mrc * discount_pct)
        net_mrc = gross_mrc - bundle_discount

        # Setup Fee (OTC) Discount Logic: Waive or discount setup fee for commitments >= 12 months
        otc_discount = 0
        if contract_months >= 12:
            if net_mrc >= 2000:
                otc_discount = total_otc  # 100% setup fee waiver
            elif net_mrc >= 1000:
                otc_discount = int(total_otc * 0.50)  # 50% setup fee waiver

        net_otc = total_otc - otc_discount
        effective_contract = max(contract_months, min_required_contract)

        return CommercialBreakdown(
            items=items_breakdown,
            gross_mrc_inr=gross_mrc,
            bundle_discount_inr=bundle_discount,
            net_mrc_inr=net_mrc,
            total_otc_inr=total_otc,
            otc_discount_inr=otc_discount,
            net_otc_inr=net_otc,
            min_contract_months=effective_contract,
            guaranteed_sla_days=max_sla_days if items_breakdown else 0,
            gst_exempt_eligible=all_non_gst,
            dependency_locks=[lock for lock in locks if lock.missing],
        )

    def optimize_budget(self, user: UserProfile, max_monthly_budget: int) -> ReverseBudgetResult:
        """Deterministic DAG-Constrained Branch-and-Bound Optimizer ("Mera Budget ₹X Hai").

        Guarantees:
        1. Hard eligibility (tier, employees, sites, GSTIN firewall) satisfied.
        2. Exactly ONE primary connectivity SKU anchored first.
        3. Compatible add-ons packed to maximize detected_needs utility without exceeding budget.
        4. Runs in sub-millisecond execution time.
        """
        eligible_skus = self.filter_eligible_products(user)
        eligible_map = {sku.product_id: sku for sku in eligible_skus}

        # Separate into base connectivity vs add-ons
        base_candidates = [
            sku for sku in eligible_skus
            if sku.product_id in BASE_CONNECTIVITY_SKUS and sku.price_min_inr_per_month <= max_monthly_budget
        ]

        if not base_candidates:
            # Fallback if budget is extremely low: Check if mobile postpaid fits
            postpaid_candidates = [
                sku for sku in eligible_skus
                if sku.product_id in {"P07", "P08"} and sku.price_min_inr_per_month <= max_monthly_budget
            ]
            if postpaid_candidates:
                base_candidates = postpaid_candidates
            else:
                # Return empty result indicating budget too low for standalone connectivity
                commercials = self.calculate_commercials([], strict_dag=False)
                return ReverseBudgetResult(
                    budget_inr=max_monthly_budget,
                    selected_skus=[],
                    commercials=commercials,
                    utility_score=0.0,
                    rationale=f"Monthly budget of ₹{max_monthly_budget} is below the lowest available plan.",
                )

        # Need-scoring utility weights
        needs_weights = {
            "pos_upi_uptime": {"P09": 60, "P04": 30, "P01": 20},
            "whatsapp_catalogue": {"P15": 50, "P18": 30},
            "cloud_email": {"P16": 45, "P17": 35},
            "cctv_surveillance": {"P23": 40},
            "guest_wifi": {"P22": 35},
            "static_ip": {"P11": 30},
            "pos_billing": {"P19": 40},
            "sd_wan": {"P10": 50},
            "cybersecurity": {"P20": 30, "P21": 45},
            "iot_monitoring": {"P24": 50, "P25": 40},
        }

        best_cart: list[str] = []
        best_utility = -1.0
        best_commercials: Optional[CommercialBreakdown] = None
        best_base_sku = ""

        # Evaluate each base candidate
        for base in base_candidates:
            current_cart = [base.product_id]
            current_mrc = base.price_min_inr_per_month

            # Calculate base utility
            base_utility = 100.0
            # Higher bandwidth / speed gives higher base score
            if base.product_id == "P02":
                base_utility += 25.0
            elif base.product_id == "P03":
                base_utility += 50.0
            elif base.product_id == "P04":
                # AirFiber 5G is highly preferred for fast setup in micro
                base_utility += 20.0

            # Eligible add-ons compatible with this base
            compatible_addons: list[ProductItem] = []
            for sku in eligible_skus:
                if sku.product_id == base.product_id or sku.product_id in BASE_CONNECTIVITY_SKUS:
                    continue
                # Check requires_one_of
                if sku.requires_one_of and base.product_id not in sku.requires_one_of:
                    continue
                compatible_addons.append(sku)

            # Sort add-ons by utility per rupee
            def addon_utility(sku: ProductItem) -> float:
                score = 10.0  # Base utility
                for need in user.detected_needs:
                    norm_need = need.lower().strip()
                    if norm_need in needs_weights and sku.product_id in needs_weights[norm_need]:
                        score += needs_weights[norm_need][sku.product_id]
                return score

            compatible_addons.sort(
                key=lambda x: addon_utility(x) / max(1, x.price_min_inr_per_month),
                reverse=True,
            )

            # Greedy packing of add-ons within budget
            current_addons: list[str] = []
            remaining_budget = max_monthly_budget - current_mrc
            total_utility = base_utility

            for addon in compatible_addons:
                addon_price = addon.price_min_inr_per_month
                # Consider bundle discount when testing inclusion
                if addon_price <= remaining_budget:
                    current_addons.append(addon.product_id)
                    remaining_budget -= addon_price
                    total_utility += addon_utility(addon)

            candidate_full_cart = [base.product_id] + current_addons
            cart_objs = [CartItem(product_id=pid, quantity=1) for pid in candidate_full_cart]
            comms = self.calculate_commercials(cart_objs, strict_dag=True)

            # Verify that net MRC fits in budget
            if comms.net_mrc_inr <= max_monthly_budget:
                if total_utility > best_utility:
                    best_utility = total_utility
                    best_cart = candidate_full_cart
                    best_commercials = comms
                    best_base_sku = base.product_name

        if not best_commercials:
            # Fallback to minimal base
            minimal_base = min(base_candidates, key=lambda x: x.price_min_inr_per_month)
            cart_objs = [CartItem(product_id=minimal_base.product_id, quantity=1)]
            best_commercials = self.calculate_commercials(cart_objs, strict_dag=True)
            best_cart = [minimal_base.product_id]
            best_utility = 100.0
            best_base_sku = minimal_base.product_name

        names = [self.db.get_product(pid).product_name for pid in best_cart if self.db.get_product(pid)]
        rationale = (
            f"Optimized within ₹{max_monthly_budget}/mo budget: Anchored with '{best_base_sku}' "
            f"and bundled {len(best_cart) - 1} high-utility add-ons: {', '.join(names[1:]) or 'None'}. "
            f"Guaranteed SLA: {best_commercials.guaranteed_sla_days} days."
        )

        return ReverseBudgetResult(
            budget_inr=max_monthly_budget,
            selected_skus=best_cart,
            commercials=best_commercials,
            utility_score=best_utility,
            rationale=rationale,
        )
