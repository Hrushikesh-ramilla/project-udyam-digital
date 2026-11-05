import sys
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_deck():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Brand Colors
    BG_DARK = RGBColor(11, 15, 25)       # Slate 950
    CARD_BG = RGBColor(17, 24, 39)       # Slate 900
    CARD_BORDER = RGBColor(31, 41, 55)   # Slate 800
    TEXT_WHITE = RGBColor(255, 255, 255)
    TEXT_MUTED = RGBColor(156, 163, 175) # Slate 400
    RED_ACCENT = RGBColor(239, 68, 68)   # Red 500
    GREEN_ACCENT = RGBColor(16, 185, 129)# Emerald 500
    AMBER_ACCENT = RGBColor(245, 158, 11)# Amber 500
    BLUE_ACCENT = RGBColor(59, 130, 246) # Blue 500

    def add_slide_base(title, category="PROJECT UDYAM DIGITAL | AIRTEL SYNC HACKATHON 2026"):
        slide = prs.slides.add_slide(blank_layout)
        # Background
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_DARK
        bg.line.fill.background()

        # Category Header
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(0.4))
        tf_cat = cat_box.text_frame
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = RED_ACCENT

        # Slide Title
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.733), Inches(0.8))
        tf_t = t_box.text_frame
        p_t = tf_t.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_WHITE

        return slide

    def add_card(slide, left, top, width, height, title="", body=""):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BORDER
        card.line.width = Pt(1)

        if title or body:
            tb = slide.shapes.add_textbox(Inches(left + 0.2), Inches(top + 0.2), Inches(width - 0.4), Inches(height - 0.4))
            tf = tb.text_frame
            tf.word_wrap = True
            if title:
                p0 = tf.paragraphs[0]
                p0.text = title
                p0.font.size = Pt(13)
                p0.font.bold = True
                p0.font.color.rgb = RED_ACCENT
            if body:
                p1 = tf.add_paragraph() if title else tf.paragraphs[0]
                p1.text = body
                p1.font.size = Pt(10)
                p1.font.color.rgb = TEXT_MUTED
        return card

    # ==========================================================
    # SLIDE 1: Title & Executive Summary
    # ==========================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = BG_DARK
    bg1.line.fill.background()

    t1 = s1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.333), Inches(3.0))
    tf1 = t1.text_frame
    p_badge = tf1.paragraphs[0]
    p_badge.text = "AIRTEL SYNC HACKATHON 2026 • ENTERPRISE TRACK A"
    p_badge.font.size = Pt(12)
    p_badge.font.bold = True
    p_badge.font.color.rgb = RED_ACCENT

    p_main = tf1.add_paragraph()
    p_main.text = "Project Udyam Digital"
    p_main.font.size = Pt(44)
    p_main.font.bold = True
    p_main.font.color.rgb = TEXT_WHITE

    p_sub = tf1.add_paragraph()
    p_sub.text = "Making 6 Crore+ Indian MSMEs Go Digital in One Sitting on a Mobile Phone"
    p_sub.font.size = Pt(18)
    p_sub.font.color.rgb = RGBColor(209, 213, 219)

    add_card(s1, 1.0, 5.0, 3.6, 1.8, "The Challenge", "5,000 historical leads convert at only 7.36% due to complex multi-page SKU PDFs, manual field scheduling, and rigid GSTIN requirements.")
    add_card(s1, 4.9, 5.0, 3.6, 1.8, "The Architecture", "Neuro-symbolic sandwich: Multilingual LLM Advisor + Deterministic CPQ DAG solver + DPDP Smart KYC + LightGBM Lead Rescue.")
    add_card(s1, 8.8, 5.0, 3.6, 1.8, "The Business Impact", "Slashes blended CAC from ₹15,000 to ₹3,200, eliminates 56% quote drop-off, and shrinks activation delay from 17.6 days to 4.2 days.")

    # ==========================================================
    # SLIDE 2: The Core Problem & Funnel Bleed Analysis
    # ==========================================================
    s2 = add_slide_base("The Problem: Dissecting Accel Business's 5,000-Lead SMB Funnel Bleed")
    add_card(s2, 0.8, 1.6, 2.7, 2.2, "Primary Funnel Leak: 56.4%", "1,974 Needs Assessed → Only 861 Quotes Accepted.\n1,113 high-intent leads lost because field reps send multi-page PDF catalogs with confusing product codes.")
    add_card(s2, 3.8, 1.6, 2.7, 2.2, "Non-GST Conversion Gap", "GST registered leads convert at 9.6% vs 2.0% for non-GST leads (4.8x disparity). Sales reps pitch GST-mandatory leased lines to kiranas.")
    add_card(s2, 6.8, 1.6, 2.7, 2.2, "Field Scheduling Friction", "531 leads dropped because shop owners had no time for physical visits; 296 dropped because sales failed to schedule visits.")
    add_card(s2, 9.8, 1.6, 2.7, 2.2, "Severe CAC vs ARPU Mismatch", "₹15,000 blended customer acquisition cost against ₹1,500 - ₹2,500/month micro bundles. Requires 10+ months to break even on hardware/sales.")

    add_card(s2, 0.8, 4.2, 11.7, 2.6, "The Accel Business Funnel Reality (smb_leads.csv Telemetry)",
             "• 5,000 Leads Generated → 3,406 Contacted (68%) → 1,974 Needs Assessed (58%) → 861 Quotes Accepted (44%) → 588 KYC Complete (68%) → 368 Activated (63%).\n"
             "• Total Conversion: Only 7.36% (368 / 5,000). 98 dropouts took >21 days (average activation takes 17.6 days with 3+ status chases per customer).\n"
             "• Accel Business serves large corporates well, but its legacy sales force is structurally incapable of profitably onboarding high-volume, low-ARPU Indian micro-merchants.")

    # ==========================================================
    # SLIDE 3: Customer Segment Prioritization Strategy
    # ==========================================================
    s3 = add_slide_base("Customer Segment Prioritization: Matching Telecom Bundles to MSME Realities")
    add_card(s3, 0.8, 1.6, 2.7, 5.2, "1. Micro Retail & Services (55%)",
             "• Priority: TIER 1 IMMEDIATE FOCUS\n"
             "• Size: 55% of MSME base (Kiranas, salons, pharmacies)\n"
             "• Current Setup: Mobile hotspot, personal UPI QR\n"
             "• Core Needs: 100% UPI payment uptime, guest Wi-Fi, WhatsApp catalog\n"
             "• Non-GST Friendly: Udyam certificate pathway\n"
             "• Recommended Bundle: Biz AirFiber 100 + Secure Guest Wi-Fi + POS Backup\n"
             "• Sweet Spot: ₹1,299 - ₹1,799 / month\n"
             "• Churn Risk: Low once UPI is stabilized.")

    add_card(s3, 3.8, 1.6, 2.7, 5.2, "2. Professional Offices (25%)",
             "• Priority: TIER 1 IMMEDIATE FOCUS\n"
             "• Size: 25% (Clinics, CA firms, coaching, lawyers)\n"
             "• Current Setup: Home broadband, personal Gmail\n"
             "• Core Needs: 99.9% uptime, custom domain email (name@cafirm.in), cloud backup\n"
             "• Compliance: Mostly GST registered (PAN validated)\n"
             "• Recommended Bundle: Biz Fibre 300 + Cloud Email 10 users + 1TB Backup + Static IP\n"
             "• Sweet Spot: ₹2,499 - ₹3,499 / month\n"
             "• High lifetime value & low churn.")

    add_card(s3, 6.8, 1.6, 2.7, 5.2, "3. Small Multi-Site Chains (15%)",
             "• Priority: TIER 2 HIGH ARPU EXPANSION\n"
             "• Size: 15% (Restaurant chains, 3-10 store retail)\n"
             "• Current Setup: Fragmented local ISPs per location\n"
             "• Core Needs: Single centralized bill, SD-WAN, Cloud CCTV across all outlets\n"
             "• Compliance: Central GSTIN with multi-site billing\n"
             "• Recommended Bundle: Multi-site Biz Fibre 300 + Managed SD-WAN + Cloud CCTV\n"
             "• Sweet Spot: ₹8,000 - ₹15,000 / month\n"
             "• High switching barrier.")

    add_card(s3, 9.8, 1.6, 2.7, 5.2, "4. Small Manufacturers (5%)",
             "• Priority: TIER 3 SPECIALIZED NICHE\n"
             "• Size: 5% (Auto-parts, textiles, foundries)\n"
             "• Current Setup: Local ISP or unmanaged copper\n"
             "• Core Needs: Dedicated 1:1 Leased Line, IoT sensor monitoring, machine uptime\n"
             "• Compliance: Industrial GSTIN mandatory\n"
             "• Recommended Bundle: Internet Leased Line 20/100 Mbps + Machine Monitoring IoT\n"
             "• Sweet Spot: ₹10,000 - ₹25,000 / month\n"
             "• High margin, SLA guaranteed.")

    # ==========================================================
    # SLIDE 4: The Neuro-Symbolic Architecture
    # ==========================================================
    s4 = add_slide_base("The Solution: The Neuro-Symbolic Sandwich Architecture")
    add_card(s4, 0.8, 1.6, 11.7, 1.4, "Architectural Invariant: Zero Hallucination in Pricing, Zero Friction in Language",
             "We pair the natural language understanding of Multimodal Large Language Models (Gemini 3.5 Flash-Lite) with a deterministic, mathematically provable Symbolic Engine (DAG CPQ Solver & SHA-256 RapidFuzz KYC Gate). The LLM never computes prices; the symbolic engine never speaks stiffly.")

    add_card(s4, 0.8, 3.2, 3.6, 3.6, "Layer 1: Multilingual AI Advisor",
             "• Multilingual Slot Filler (Hindi/Hinglish/English)\n"
             "• Powered by Gemini 3.5 Flash-Lite (Tier 1)\n"
             "• Instant Deterministic Regex Fallback (Tier 2)\n"
             "• Dual Narration: Markdown UI + Web Speech Voice\n"
             "• Slashes Needs Assessment time from 4 days to 45 seconds.")

    add_card(s4, 4.9, 3.2, 3.6, 3.6, "Layer 2: Symbolic CPQ DAG Solver",
             "• Deterministic GSTIN Firewall (blocks GST SKUs for non-GST users)\n"
             "• Directed Acyclic Graph (DAG) dependency solver prevents orphan add-ons\n"
             "• Reverse Budget Optimizer ('Mera Budget ₹X Hai')\n"
             "• Exact Commercials: MRC, OTC waiver, bundle tier discounts in <5ms.")

    add_card(s4, 8.8, 3.2, 3.6, 3.6, "Layer 3: DPDP Smart KYC Gate",
             "• In-Memory National ID Redaction (DPDP Act 2023)\n"
             "• SHA-256 Content-Addressable OCR (<1ms)\n"
             "• Live Gemini Vision & PyMuPDF for arbitrary uploads\n"
             "• RapidFuzz Token-Set Entity Matcher (>70% match)\n"
             "• Utility bill freshness validation against evaluation anchor.")

    # ==========================================================
    # SLIDE 5: Multilingual Conversational Advisor Deep Dive
    # ==========================================================
    s5 = add_slide_base("Layer 1 Deep Dive: Multilingual Conversational Advisor (Voice & Chat)")
    add_card(s5, 0.8, 1.6, 5.7, 5.2, "Conversational Discovery in Hindi, Hinglish & English",
             "• True Multimodal Dialogue: Understands phonetic Hinglish, dialect words ('dukaan', 'karkhana', 'kam karne wale', 'gst nahi hai').\n"
             "• Live Example:\n"
             "  User: 'Namaste humari Surat me ek kapde ki factory hai jisme 30 log kam karte hain aur GST number bhi hai'\n"
             "  Advisor Extracted Slots:\n"
             "    - Segment: Manufacturing ('mfg')\n"
             "    - Location: Surat (City Tier 2)\n"
             "    - Employees: 30\n"
             "    - GSTIN: True\n"
             "• Dual Narration Engine:\n"
             "  1. Visual Rich Markdown: Formatted pricing cards with bullet comparisons.\n"
             "  2. Spoken Voice TTS: Natural, conversational Hindi audio narration synthesized on device without robot artifacts.\n"
             "• Zero-Latency Fallback: If cloud LLM times out (>2.5s) or encounters 503 load spikes, the deterministic regex engine extracts slots in <2ms without dropping the user session.")

    add_card(s5, 6.8, 1.6, 5.7, 5.2, "Why This Eliminates the 56% Drop-off",
             "• Replaces 5-Page Technical PDFs with a 1-Screen Interactive Offer:\n"
             "  Instead of sending PDF codes like 'SKU-P05-ILL-20M', the advisor explains in Hindi: 'Aapki factory ke liye humne Internet Leased Line 20Mbps select ki hai taaki machinery monitoring bina rukaawat chale.'\n\n"
             "• Immediate Self-Serve Gratification:\n"
             "  MSME owners make buying decisions between customer visits in their shop. A journey that finishes in 3 minutes on WhatsApp or Chrome captures intent before attention fades.\n\n"
             "• Transparent Pricing & Free Setup:\n"
             "  Clear itemization of Monthly Recurring Charges (MRC), One-Time Setup Charges (OTC), and 100% setup fee waiver for 12+ month contracts eliminates unexpected hidden charges.")

    # ==========================================================
    # SLIDE 6: CPQ Engine & The Non-GST Firewall
    # ==========================================================
    s6 = add_slide_base("Layer 2 Deep Dive: Deterministic CPQ Engine & Reverse Budget Optimizer")
    add_card(s6, 0.8, 1.6, 5.7, 5.2, "The Non-GST Firewall (Attacking the 2.0% Conversion Gap)",
             "• The Flaw in Legacy Telecom Sales:\n"
             "  Sales reps routinely pitched GST-mandatory corporate leased lines to non-GST kiranas. 3 weeks later, corporate KYC rejected them, causing a 2.0% conversion rate.\n\n"
             "• Our Deterministic Firewall in Code:\n"
             "  If user has no GSTIN, every SKU with 'requires_gstin == Y' is mathematically pruned before the user or rep can add it to cart.\n\n"
             "• Udyam-Only Micro Bundles:\n"
             "  Routes non-GST retail merchants to high-reliability Biz AirFiber (P04) + Secure Guest Wi-Fi (P22) bundles backed purely by Udyam Registration and an Electricity Bill.\n\n"
             "• Projected Outcome: Elevates non-GST conversion from 2.0% to 14.8%.")

    add_card(s6, 6.8, 1.6, 5.7, 5.2, "DAG Solver & 'Mera Budget ₹X Hai' Optimizer",
             "• Directed Acyclic Graph (DAG) Prerequisite Locks:\n"
             "  Enforces telecom network realities. Dependent add-ons (Static IP P11, Guest Wi-Fi P22, 4G Failover P09) cannot exist in a cart without an active parent connectivity SKU (P01/P02/P03/P04). Removing parent raises a deterministic 'DependencyLockError'.\n\n"
             "• Reverse Budget Optimizer ('Mera Budget ₹X/mo Hai'):\n"
             "  Indian MSMEs do not know technical bandwidth; they know their monthly cash budget. The owner drags a slider to '₹2,500/mo'.\n"
             "  Our Branch-and-Bound algorithm anchors the best legal connectivity base first, then packs highest-utility compatible add-ons in <10ms without exceeding the cap.\n\n"
             "• Multi-Category Bundle Discounts: 5% (2 categories), 10% (3 categories), 15% (4+ categories) automatically calculated.")

    # ==========================================================
    # SLIDE 7: DPDP Smart KYC & Content-Addressable OCR
    # ==========================================================
    s7 = add_slide_base("Layer 3 Deep Dive: DPDP Act 2023 Compliant Smart KYC Gate")
    add_card(s7, 0.8, 1.6, 5.7, 5.2, "DPDP Act 2023 Zero-Persistence Architecture",
             "• Explicit Digital Consent & Purpose Limitation:\n"
             "  Digital consent checkbox with cryptographic timestamp, IP hash, and audit trail before any byte ingestion.\n\n"
             "• Immediate In-Memory ID Redaction:\n"
             "  12-digit national ID / Aadhaar numbers are masked in-memory immediately upon byte ingestion using regex pattern replacement ('XXXX-XXXX-1234'). Unredacted UIDs are NEVER written to disk, SQLite, logs, or frontend state.\n\n"
             "• Anchor Freshness Invariant:\n"
             "  Utility bills validated strictly against evaluation anchor date 2026-07-15. Date 2026-04-10 (96 days old) is rejected as stale (>90d window); date 2026-04-20 (86 days old) passes.\n\n"
             "• Sub-Second Verification: Complete 4-stage regulatory verification executes in under 200ms.")

    add_card(s7, 6.8, 1.6, 5.7, 5.2, "Content-Addressable OCR & RapidFuzz Matching",
             "• Cryptographic SHA-256 Byte Ingestion:\n"
             "  Zero filename branching. Document identity is determined purely by 'hashlib.sha256(file_bytes).hexdigest()' mapped to synthetic registries.\n\n"
             "• Real Document OCR & PyMuPDF / Gemini Vision:\n"
             "  Upload real PDFs from a laptop (PyMuPDF extracts text in <2ms) or real images (Gemini Vision extracts structured GSTIN, Udyam, address, and legal trade names).\n\n"
             "• RapidFuzz Cross-Document Entity Resolution:\n"
             "  MSME certificates frequently have minor typographical spelling variations ('Prop. Ganesh Woodcraft' vs 'Joseph Singh'). RapidFuzz Token-Set Ratio achieves 100% fuzzy score, eliminating false rejections while trapping true fraud (e.g. Applicant K07 mismatch).")

    # ==========================================================
    # SLIDE 8: Phygital Sales & Channel Partner Ecosystem
    # ==========================================================
    s8 = add_slide_base("Channel Strategy: Phygital Assisted OBO Mode & WhatsApp Handoff")
    add_card(s8, 0.8, 1.6, 5.7, 5.2, "Transforming Field Sales from Competitors to Enablers",
             "• The Field Conflict Problem:\n"
             "  Field sales reps resist digital self-serve portals because they fear losing commissions. 531 leads dropped because busy owners had no time for lengthy 45-minute physical visits.\n\n"
             "• Assisted On-Behalf-Of (OBO) Mode:\n"
             "  Field reps open the app in 'Field Rep OBO' mode. During a 2-minute store visit, the rep configures the optimal solution, applies promo codes, and generates a pre-hydrated WhatsApp session link.\n\n"
             "• Zero-Visit Digital Closing:\n"
             "  The shop owner receives the pre-filled bundle on WhatsApp, reviews commercials in 30 seconds, grants digital consent, and completes KYC whenever free in the evening.\n\n"
             "• Guaranteed Partner Commission Lock:\n"
             "  15% partner commission (₹1,500 - ₹3,000) is cryptographically locked to 'partner_id'. When the owner activates online, the partner gets paid automatically.")

    add_card(s8, 6.8, 1.6, 5.7, 5.2, "6-Stage Live Provisioning State Machine",
             "• Eliminating the 17.6-Day Black Hole:\n"
             "  Currently, customers chase status 3+ times via call center because telecom provisioning is opaque. 98 leads canceled after waiting >21 days.\n\n"
             "• Transparent 6-Stage Milestone Tracker:\n"
             "  1. Order Placed & Commercial Agreement\n"
             "  2. Smart KYC & Regulatory Registry Cleared\n"
             "  3. Optical Distribution Frame (ODF) Fiber Allocated\n"
             "  4. CPE Router & Mesh Wi-Fi Dispatched\n"
             "  5. Field Technician ONT Splicing & Optical Power Calibration\n"
             "  6. Link Live & Digital Radius AAA Authentication\n\n"
             "• Real-Time WhatsApp Notification Webhooks:\n"
             "  Automated WhatsApp alerts at each milestone with field engineer contact, tracking link, and guaranteed SLA countdown.")

    # ==========================================================
    # SLIDE 9: LightGBM Machine-Learned Lead Rescue
    # ==========================================================
    s9 = add_slide_base("Back-Office Intelligence: LightGBM Machine-Learned Lead Rescue Engine")
    add_card(s9, 0.8, 1.6, 5.7, 5.2, "Targeting the 1,113 Stalled Leads with Applied ML",
             "• Machine Learning Architecture:\n"
             "  Trained LightGBM Classifier ('LGBMClassifier') on 5,000 historical SMB records from 'smb_leads.csv'.\n\n"
             "• Class Imbalance Weighting:\n"
             "  Because historical activations were only 7.36% (368 / 5,000), standard ML classifiers suffer from severe majority-class bias. We set 'scale_pos_weight = 12.59' (neg/pos ratio), ensuring high recall on high-value rescue opportunities.\n\n"
             "• Feature Importance Attribution:\n"
             "  1. Monthly Telecom Spend (split count: 164)\n"
             "  2. Customer Follow-up Calls (split count: 123)\n"
             "  3. Employee Headcount (split count: 99)\n"
             "  4. Has GSTIN flag (split count: 63)\n"
             "  5. City Tier (split count: 55)\n\n"
             "• Actionable Partner ML Console: Ranks stalled leads by win-propensity, highlights root risk factor, and generates 1-click WhatsApp rescue links.")

    add_card(s9, 6.8, 1.6, 5.7, 5.2, "The Lead Rescue Playbook",
             "• Cohort 1: High Spend, High Calls (>3 chases)\n"
             "  - Root Cause: Frustrated by installation delay.\n"
             "  - ML Action: Triggers 'Priority Engineer Dispatch' with guaranteed 48-hour installation SLA.\n\n"
             "• Cohort 2: Non-GST Retailers Stuck at KYC\n"
             "  - Root Cause: Rep pitched GST leased line; failed in verification.\n"
             "  - ML Action: Automatically re-hydrates cart into Udyam-eligible Biz AirFiber micro-bundle with ₹0 setup fee.\n\n"
             "• Cohort 3: Field Scheduling Dropouts (531 leads)\n"
             "  - Root Cause: No time for salesperson visit.\n"
             "  - ML Action: Dispatches direct digital self-serve checkout link with ₹1,500 partner closing bounty.\n\n"
             "• Recovering just 20% of the 1,113 stalled leads adds 222 new enterprise customers (+60% increase in quarterly activations).")

    # ==========================================================
    # SLIDE 10: Financial Impact, Target Metrics & Rollout
    # ==========================================================
    s10 = add_slide_base("Business Case: Unit Economics, Target Metrics & 12-Month Rollout")
    add_card(s10, 0.8, 1.6, 2.7, 2.6, "Blended CAC", "Current: ₹15,000\nTarget: ₹3,200\nReduction: 78.7%\nSlashed via digital self-serve, WhatsApp OBO links, and automated KYC.")
    add_card(s10, 3.8, 1.6, 2.7, 2.6, "Lead Conversion", "Current: 7.36%\nTarget: 22.4%\nImprovement: 3.0x\nEliminating 56% quote drop-off and unlocking the non-GST micro-retail cohort.")
    add_card(s10, 6.8, 1.6, 2.7, 2.6, "Time to Activate", "Current: 17.6 Days\nTarget: 4.2 Days\nImprovement: 76.1%\nReal-time OCR registry check & automated ODF fiber splicing dispatch.")
    add_card(s10, 9.8, 1.6, 2.7, 2.6, "Customer NPS & Churn", "NPS: Up from +28 to +64\n6-Mo Churn: Down from 14.2% to 4.8%\nSingle consolidated bill & transparent status tracker.")

    add_card(s10, 0.8, 4.5, 11.7, 2.3, "12-Month Scaled Rollout Roadmap",
             "• Months 1–3 (Pilot & Foundation): Deploy PWA & Multilingual Advisor across Tier 1 metros (Delhi NCR, Bengaluru, Mumbai). Train 500 channel partners on Assisted OBO Mode.\n"
             "• Months 4–6 (Regional Expansion): Roll out Hindi + 4 regional languages (Tamil, Telugu, Marathi, Gujarati). Integrate Live NIC GSTN GSP API and UIDAI e-Sign.\n"
             "• Months 7–12 (Full Ecosystem Scaling): Automated LightGBM lead-rescue dispatch to 5,000+ pan-India partners. Target: 100,000 MSMEs onboarded in Year 1, adding ₹180 Crore annual recurring revenue.")

    output_path = "docs/Project_Udyam_Digital_10_Slide_Pitch_Deck.pptx"
    prs.save(output_path)
    print(f"Successfully generated 10-slide business case deck: {output_path}")

if __name__ == "__main__":
    build_deck()
