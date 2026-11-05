# Project Udyam Digital — 10-Slide Business Case & Pitch Deck

**Competition:** Airtel SYNC Hackathon 2026 (Enterprise Track A)  
**Operator Context:** Accel Telecom / Accel Business  
**Submission Package Artifact:** `docs/Project_Udyam_Digital_10_Slide_Pitch_Deck.pptx` (Generated via `python-pptx`)

---

## Slide 1: Title & Executive Summary
- **Main Heading:** Project Udyam Digital
- **Sub-heading:** Making 6 Crore+ Indian MSMEs Go Digital in One Sitting on a Mobile Phone
- **The Core Problem:** 5,000 historical leads convert at only 7.36% due to complex multi-page SKU PDFs, manual field scheduling delays, and rigid GSTIN requirements.
- **The Solution:** A Neuro-Symbolic Sandwich combining a Multilingual Conversational Advisor (Hindi/Hinglish/English via Gemini 3.5 Flash-Lite), a deterministic DAG CPQ solver with a Non-GST Firewall, DPDP Act 2023 Smart KYC (<200ms), and a LightGBM Lead Rescue Engine (`scale_pos_weight: 12.59`).
- **The Financial ROI:** Slashes blended customer acquisition cost (CAC) from ₹15,000 to ₹3,200, triples conversion from 7.36% to 22.4%, and compresses activation delay from 17.6 days to 4.2 days.

---

## Slide 2: The Core Problem & Funnel Bleed Analysis
*Telemetry Source: `smb_leads.csv` (5,000 historical enterprise leads, Apr–Jun 2026)*

- **The Funnel Bleed:**
  - Leads Generated: 5,000 (100%)
  - Contacted: 3,406 (68.1%)
  - Needs Assessed: 1,974 (58.0%)
  - **Quote Accepted: 861 (43.6% — 56.4% Drop-Off / 1,113 Leads Lost!)**
  - KYC Complete: 588 (68.3%)
  - Activated: 368 (62.6%)
- **The 4 Root Friction Vectors:**
  1. **Primary Funnel Leak (56.4% Drop-off):** 1,113 high-intent merchants walk away between Needs Assessed and Quote Accepted because sales reps send multi-page PDF catalogs filled with technical SKU codes.
  2. **Non-GST Conversion Gap (4.8x Disparity):** Leads with GSTIN convert at 9.6% vs 2.0% for non-GST leads because reps pitch GST-mandatory leased lines to kiranas, which fail weeks later in KYC.
  3. **Field Scheduling Failure:** 531 leads dropped because shop owners had no time for 45-minute physical visits; 296 dropped because reps failed to schedule visits.
  4. **CAC vs ARPU Inversion:** Accel spends ₹15,000 in blended CAC to acquire customers for ₹1,500–₹2,500/mo micro bundles, taking >10 months to break even.

---

## Slide 3: Customer Segment Prioritization Strategy
*Matching Telecom Products to MSME Operating Realities*

| Priority Tier | Segment & Share | Typical Profile | Core Unmet Need | Tailored Telecom Bundle | Sweet Spot Price Point |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Tier 1 (Focus)** | **Micro Retail & Services (55%)** | Kirana, salon, pharmacy | 100% UPI payment uptime, guest Wi-Fi, WhatsApp catalog | Biz AirFiber 100 (P04) + Secure Guest Wi-Fi (P22) + 4G Failover (P09) | ₹1,299 – ₹1,799 / mo |
| **Tier 1 (Focus)** | **Professional Offices (25%)** | Clinic, CA firm, coaching | High uptime, domain email (name@firm.in), secure cloud backup | Biz Fibre 300 (P02) + Cloud Email (P16) + 1TB Backup (P17) + Static IP (P11) | ₹2,499 – ₹3,499 / mo |
| **Tier 2 (Expansion)**| **Multi-Site Chains (15%)** | Restaurant chains, 3–10 outlets | Centralized single bill, SD-WAN, multi-store Cloud CCTV | Biz Fibre 300 per site + Managed SD-WAN (P10) + Cloud CCTV (P23) | ₹8,000 – ₹15,000 / mo |
| **Tier 3 (Niche)** | **Small Manufacturers (5%)** | Auto-parts, textile units | Dedicated 1:1 bandwidth, IoT sensor monitoring, ERP uptime | Internet Leased Line 20/100 (P05/P06) + Machine Monitoring IoT (P24) | ₹10,000 – ₹25,000 / mo |

---

## Slide 4: The Neuro-Symbolic Sandwich Architecture
- **Design Philosophy:** Never allow an LLM to hallucinate commercial prices; never allow a static form to talk stiffly to a rural shopkeeper.
- **Layer 1 (Neuro): Multilingual AI Conversational Advisor**
  - Powered by Gemini 3.5 Flash-Lite with zero-latency (<10ms) deterministic regex fallback.
  - Understands colloquial Hindi, Hinglish, and English with phonetic typo tolerance.
  - Dual-channel narration: Interactive Markdown cards + Web Speech Voice narration.
- **Layer 2 (Symbolic): Deterministic CPQ DAG Engine**
  - Hard Eligibility Gate & Non-GST Firewall.
  - Directed Acyclic Graph (DAG) dependency solver over 25 SKUs (`requires_one_of`).
  - Branch-and-bound reverse budget optimizer ("Mera Budget ₹X Hai").
- **Layer 3 (Symbolic & Neuro): DPDP Smart KYC Gate**
  - Immediate in-memory national ID masking (`XXXX-XXXX-1234`).
  - SHA-256 content-addressable OCR (<1ms) + native PyMuPDF & Gemini Vision for arbitrary file uploads.
  - RapidFuzz token matching (>70% match) and evaluation anchor freshness validation (`2026-07-15`).
- **Layer 4 (Neuro): LightGBM Lead Rescue Machine Learning**
  - Trained on 5,000 historical leads with `scale_pos_weight: 12.59` to rescue stalled quotes.

---

## Slide 5: Layer 1 Deep Dive — Multilingual AI Advisor
- **Natural Language Slot Extraction:** Automatically extracts `segment`, `city_tier`, `employee_count`, `num_sites`, `has_gstin`, `detected_needs`, and `monthly_budget_cap`.
- **Live Multilingual Example:**
  - *Merchant:* *"Namaste humara Surat me ek kapde ka manufacturing karkhana hai jisme 30 workers hain aur active GST number bhi hai"*
  - *Advisor Extracted:* `segment: mfg`, `city_tier: 2`, `employee_count: 30`, `has_gstin: True`.
  - *Recommendation:* Internet Leased Line 20 Mbps with 0 setup fee.
- **Dual-Channel Narration:**
  - *Visual Markdown:* Clear commercial math breakdown, guaranteed SLA turnaround days.
  - *Spoken Voice Audio:* Natural, clean Hindi voice speech synthesized directly in browser.
- **Resilience:** If network drops or cloud API hits 503 load, the deterministic regex engine takes over instantly in <2ms.

---

## Slide 6: Layer 2 Deep Dive — CPQ Engine & The Non-GST Firewall
- **The Non-GST Firewall:**
  - In legacy sales, reps pitched GST-mandatory leased lines to kiranas, leading to a 2.0% conversion rate.
  - Our code prunes all `requires_gstin == Y` SKUs when `has_gstin == False`.
  - Automatically routes non-GST retail to Udyam-eligible Biz AirFiber bundles, boosting non-GST conversion to 14.8%.
- **DAG Prerequisite Solver:**
  - Enforces telecom physical realities: add-ons (Static IP P11, Guest Wi-Fi P22, 4G Failover P09) require base connectivity (P01/P02/P03/P04). Removing base raises a deterministic `DependencyLockError`.
- **"Mera Budget ₹X Hai" Reverse Budget Optimizer:**
  - MSMEs drag a budget slider (e.g. ₹2,500/mo).
  - Branch-and-bound solver anchors the legal base connection, then packs highest-utility dependent add-ons in <5ms.
- **Commercial Discounts:**
  - Multi-category bundle discounts: 5% (2 categories), 10% (3 categories), 15% (4+ categories).
  - 100% One-Time Setup Fee (OTC) waived for 12+ month contracts.

---

## Slide 7: Layer 3 Deep Dive — DPDP Act 2023 Compliant Smart KYC
- **DPDP Act 2023 Zero-Persistence Guarantee:**
  - Explicit digital consent recorded with timestamp and IP hash before processing.
  - 12-digit national IDs are redacted in-memory immediately upon byte ingestion (`XXXX-XXXX-1234`). Unmasked digits are NEVER stored, logged, or sent to frontend state.
- **Content-Addressable Verification (<1ms):**
  - Keyed by `hashlib.sha256(file_bytes).hexdigest()`. Zero filename cheats.
- **Arbitrary File Upload Support:**
  - Upload real PDFs (parsed via native PyMuPDF) or images (parsed via Gemini Vision).
- **Evaluation Anchor Freshness:**
  - Utility bills validated against anchor `2026-07-15`. A bill dated `2026-04-10` (96 days old) is blocked as stale; `2026-04-20` (86 days old) passes.
- **RapidFuzz Cross-Document Entity Resolution:**
  - Resolves Indian proprietor syntax (*"Joseph Singh (Prop. Ganesh Woodcraft)"* vs *"Ganesh Woodcraft"*) with >70% token-set ratio.

---

## Slide 8: Phygital Sales & Channel Partner Ecosystem
- **The Field Sales Paradox:**
  - Field reps fear losing commissions to digital self-serve tools.
- **Assisted On-Behalf-Of (OBO) Mode:**
  - Rep opens the app in "Field Rep OBO" mode during a 2-minute store visit, configures the optimal solution, and generates a pre-hydrated WhatsApp session link.
- **Commission Lock:**
  - The partner ID is cryptographically attached to the checkout URL. When the merchant completes KYC and activates online at night, the partner's 15% commission (₹1,500–₹3,000) is automatically locked and paid.
- **Transparent 6-Stage Milestone Tracker:**
  - Replaces customer status chases with automated WhatsApp milestone updates:
    1. Order Placed & Agreement Sealed
    2. Smart KYC & Regulatory Registry Cleared
    3. ODF Fiber Allocated & VLAN Configured
    4. CPE Router & Mesh Wi-Fi Dispatched
    5. Field Splicing & Optical Power Calibration
    6. Link Live & Digital Radius AAA Provisioned.

---

## Slide 9: Back-Office Intelligence — LightGBM Lead Rescue
- **Targeting the 1,113 Stalled Quote Leads:**
  - LightGBM Classifier (`LGBMClassifier`) trained on 5,000 leads from `smb_leads.csv`.
- **Handling Severe Class Imbalance:**
  - Historical activations were only 7.36%. We set `scale_pos_weight = 12.59` (negative/positive ratio) to maximize recall on high-value rescue opportunities.
- **Key Feature Importances:**
  1. `monthly_telecom_spend_inr` (Importance: 164)
  2. `customer_follow_up_calls` (Importance: 123)
  3. `employee_count` (Importance: 99)
  4. `has_gstin_int` (Importance: 63)
  5. `city_tier` (Importance: 55)
- **Automated Next Best Actions:**
  - *High Spend + High Calls (>3 chases):* Priority engineer dispatch with guaranteed 48-hour SLA.
  - *Non-GST Stuck Leads:* Automatic re-routing to Udyam-eligible Biz AirFiber micro-bundles.
  - *Unscheduled Field Leads (531 leads):* 1-click WhatsApp checkout link with ₹1,500 partner closing bounty.
- **Business Upside:** Rescuing just 20% of stalled leads adds 222 new enterprise activations (+60% quarterly surge).

---

## Slide 10: Unit Economics, Target Metrics & 12-Month Rollout
- **Core Business KPI Targets:**

| Metric | Historical Baseline (`smb_leads.csv`) | Project Udyam Digital Target | Strategic Impact |
| :--- | :--- | :--- | :--- |
| **Lead-to-Activation Conversion** | 7.36% (368 / 5,000) | **22.4%** | **3.0x Surge** via instant quoting & non-GST routing |
| **Blended Customer Acquisition Cost** | ₹15,000 | **₹3,200** | **78.7% Reduction** via digital self-serve & WhatsApp OBO |
| **Average Time to Activation** | 17.6 Days (98 dropouts >21d) | **4.2 Days** | **76.1% Compression** via automated Smart KYC |
| **Customer Status Chases** | 3+ calls per customer | **0 calls** | Eliminated via 6-stage WhatsApp tracker |
| **6-Month Churn Rate** | 14.2% | **4.8%** | Decreased via single consolidated billing |
| **Customer Net Promoter Score (NPS)** | +28 | **+64** | Driven by instant digital onboarding |

- **12-Month Phased Rollout Plan:**
  - **Months 1–3 (Pilot):** Deploy in Tier 1 metros (Delhi NCR, Bengaluru, Mumbai). Train 500 top-performing channel partners on Assisted OBO Mode.
  - **Months 4–6 (Regional Expansion):** Roll out regional language packs (Tamil, Telugu, Marathi, Gujarati). Integrate Live NIC GSTN GSP API and Aadhaar UIDAI e-Sign.
  - **Months 7–12 (Ecosystem Scale):** Pan-India rollout across 5,000+ partners. Target: 100,000 new MSMEs onboarded in Year 1, contributing **₹180 Crore in annual recurring revenue**.
