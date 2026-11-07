import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# -----------------------------------------------------------------------------
# PALETTE & TYPOGRAPHY CONSTANTS (Ivory & Charcoal Academic Standard)
# -----------------------------------------------------------------------------
BG_IVORY       = RGBColor(250, 248, 245) # #FAF8F5
CARD_BG        = RGBColor(255, 255, 255) # #FFFFFF
CARD_SOFT      = RGBColor(244, 242, 236) # #F4F2EC
TEXT_CHARCOAL  = RGBColor(18, 19, 22)    # #121316
TEXT_MUTED     = RGBColor(74, 75, 78)    # #4A4B4E
BORDER_GRAY    = RGBColor(226, 223, 216) # #E2DFD8
AIRTEL_RED     = RGBColor(200, 16, 46)   # #C8102E
SUCCESS_GREEN  = RGBColor(30, 107, 56)   # #1E6B38

FONT_HEADING = "Calibri"
FONT_BODY    = "Calibri"

def set_slide_background(slide, color):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_header(slide, title_text, subtitle_text):
    # Title & Subtitle text box
    tb = slide.shapes.add_textbox(Inches(0.6), Inches(0.35), Inches(12.133), Inches(0.75))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.name = FONT_HEADING
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = TEXT_CHARCOAL
    
    p2 = tf.add_paragraph()
    p2.text = subtitle_text
    p2.font.name = FONT_BODY
    p2.font.size = Pt(10)
    p2.font.color.rgb = TEXT_MUTED
    p2.space_before = Pt(2)
    
    # Thin divider line
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0.6), Inches(1.18), Inches(12.133), Inches(0.015)
    )
    line.fill.solid()
    line.fill.fore_color.rgb = BORDER_GRAY
    line.line.fill.background()

def add_footer(slide, slide_num, total_slides=7):
    # Top rule
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0.6), Inches(7.0), Inches(12.133), Inches(0.015)
    )
    line.fill.solid()
    line.fill.fore_color.rgb = BORDER_GRAY
    line.line.fill.background()
    
    tb = slide.shapes.add_textbox(Inches(0.6), Inches(7.08), Inches(12.133), Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p = tf.paragraphs[0]
    p.text = f"Airtel Sync 2026 · Digital Track (Enterprise Track A) | Project Udyam Digital              Team Neural Nexus (YK, HR)              Slide {slide_num} of {total_slides}"
    p.font.name = FONT_BODY
    p.font.size = Pt(8.5)
    p.font.color.rgb = TEXT_MUTED

def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=BORDER_GRAY):
    card = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        left, top, width, height
    )
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(0.75)
    return card

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # blank layout

    # =========================================================================
    # SLIDE 1: TITLE & EXECUTIVE VISION (The Single-Sitting Paradigm)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, BG_IVORY)
    
    # Title Tag
    tag_box = s1.shapes.add_textbox(Inches(0.6), Inches(0.65), Inches(12.133), Inches(0.35))
    tf = tag_box.text_frame
    p = tf.paragraphs[0]
    p.text = "AIRTEL SYNC 2026 · DIGITAL TRACK (ENTERPRISE TRACK A)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = AIRTEL_RED
    p.alignment = PP_ALIGN.CENTER
    
    # Main Title
    t_box = s1.shapes.add_textbox(Inches(0.6), Inches(1.05), Inches(12.133), Inches(1.1))
    tf = t_box.text_frame
    p = tf.paragraphs[0]
    p.text = "Project Udyam Digital"
    p.font.name = FONT_HEADING
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = TEXT_CHARCOAL
    p.alignment = PP_ALIGN.CENTER
    
    p2 = tf.add_paragraph()
    p2.text = "Making 6 Crore+ Indian MSMEs Go Digital in One Sitting"
    p2.font.name = FONT_BODY
    p2.font.size = Pt(16)
    p2.font.color.rgb = TEXT_MUTED
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(3)

    p3 = tf.add_paragraph()
    p3.text = "Autonomous Neuro-Symbolic CPQ, Instant DPDP KYC & Multi-Site Orchestration"
    p3.font.name = FONT_BODY
    p3.font.size = Pt(11)
    p3.font.color.rgb = TEXT_MUTED
    p3.alignment = PP_ALIGN.CENTER
    p3.space_before = Pt(2)
    
    # Divider line
    div = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.5), Inches(2.4), Inches(10.333), Inches(0.015))
    div.fill.solid()
    div.fill.fore_color.rgb = BORDER_GRAY
    div.line.fill.background()

    # Left Card: Problem
    add_card(s1, Inches(0.8), Inches(2.65), Inches(5.6), Inches(3.7), CARD_BG)
    c1_box = s1.shapes.add_textbox(Inches(1.0), Inches(2.8), Inches(5.2), Inches(3.4))
    tf1 = c1_box.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "The Enterprise MSME Acquisition Bottleneck"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = TEXT_CHARCOAL
    
    bullets_left = [
        ("Massive TAM with Low Penetration: ", "Accel Business leads enterprise corporates but captures <10% of India's 63M MSMEs (Kiranas, clinics, CA firms, workshops)."),
        ("17.6-Day Manual Sales Ordeal: ", "Legacy journey relies on field sales visits, 3–5 day manual PDF quoting lags, and 3.2 customer status chase calls."),
        ("The 56.4% Quoting Abyss: ", "Prospective owners drop off while awaiting cryptic enterprise quotes, defecting to fragmented local unmanaged ISPs."),
        ("Crippling CAC Burden: ", "Blended acquisition cost of ₹15,000 against a median monthly ARPU of ₹6,900 (and ₹2,500 for micro-retail).")
    ]
    for b_bold, b_text in bullets_left:
        p = tf1.add_paragraph()
        p.space_before = Pt(8)
        run_b = p.add_run()
        run_b.text = "• " + b_bold
        run_b.font.bold = True
        run_b.font.size = Pt(10)
        run_b.font.color.rgb = TEXT_CHARCOAL
        run_t = p.add_run()
        run_t.text = b_text
        run_t.font.size = Pt(10)
        run_t.font.color.rgb = TEXT_CHARCOAL

    # Right Card: Breakthrough Solution
    add_card(s1, Inches(6.933), Inches(2.65), Inches(5.6), Inches(3.7), CARD_SOFT)
    c2_box = s1.shapes.add_textbox(Inches(7.133), Inches(2.8), Inches(5.2), Inches(3.4))
    tf2 = c2_box.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "The Single-Sitting Breakthrough Solution"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = TEXT_CHARCOAL
    
    bullets_right = [
        ("<15-Minute Mobile Self-Serve: ", "Multi-turn conversational advisor in 10 Indic languages translating ambiguous merchant needs into deterministic quotes."),
        ("GST-Free Udyam Onboarding: ", "Unlocks 3.5 Crore unregistered MSMEs (historically 2.0% conversion) via composite declaration rules."),
        ("DPDP Act 2023 Compliant: ", "Zero-persistence in-memory PII masking, cryptographic SHA-256 byte caching, and tamper-evident audit trails."),
        ("Production Monolith Live on EC2: ", "Fully functional on AWS EC2 (http://65.1.112.251) with 37/37 Pytest test suite verified.")
    ]
    for b_bold, b_text in bullets_right:
        p = tf2.add_paragraph()
        p.space_before = Pt(8)
        run_b = p.add_run()
        run_b.text = "• " + b_bold
        run_b.font.bold = True
        run_b.font.size = Pt(10)
        run_b.font.color.rgb = TEXT_CHARCOAL
        run_t = p.add_run()
        run_t.text = b_text
        run_t.font.size = Pt(10)
        run_t.font.color.rgb = TEXT_CHARCOAL

    # Title slide footer
    f_box = s1.shapes.add_textbox(Inches(0.6), Inches(6.6), Inches(12.133), Inches(0.4))
    tf = f_box.text_frame
    p = tf.paragraphs[0]
    p.text = "Team Neural Nexus: YK · HR (Hrushikesh Ramilla)     |     Live Deployment: http://65.1.112.251     |     GitHub: Hrushikesh-ramilla/project-udyam-digital"
    p.font.name = FONT_BODY
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_CHARCOAL
    p.alignment = PP_ALIGN.CENTER

    # =========================================================================
    # SLIDE 2: PROBLEM & 5,000-LEAD SMB FUNNEL BLEED DISSECTION
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, BG_IVORY)
    add_header(s2, "Problem Statement & Funnel Bleed Dissection", "Empirical Analysis of 5,000 SMB Leads (smb_leads.csv, Apr–Jun 2026)")
    add_footer(s2, 2)

    # Left Column: Funnel Table & Chart
    add_card(s2, Inches(0.6), Inches(1.35), Inches(6.3), Inches(5.45), CARD_BG)
    t_title = s2.shapes.add_textbox(Inches(0.8), Inches(1.45), Inches(5.9), Inches(0.35))
    t_title.text_frame.paragraphs[0].text = "SMB Acquisition Funnel Degradation (N = 5,000)"
    t_title.text_frame.paragraphs[0].font.bold = True
    t_title.text_frame.paragraphs[0].font.size = Pt(11)
    t_title.text_frame.paragraphs[0].font.color.rgb = TEXT_CHARCOAL

    # Table
    rows = [
        ["Funnel Stage", "Leads", "Stage %", "Cumulative %"],
        ["Leads Generated", "5,000", "100.0%", "100.0%"],
        ["Contacted Outreach", "3,406", "68.1%", "68.1%"],
        ["Needs Assessed (Field Visit)", "1,974", "58.0%", "39.5%"],
        ["Quote Accepted (Steepest Cliff)", "861", "43.6%", "17.2%"],
        ["KYC Completed", "588", "68.3%", "11.8%"],
        ["Activated Customers", "368", "62.6%", "7.36%"]
    ]
    table_shape = s2.shapes.add_table(7, 4, Inches(0.8), Inches(1.85), Inches(5.9), Inches(2.0))
    table = table_shape.table
    table.columns[0].width = Inches(2.7)
    table.columns[1].width = Inches(1.0)
    table.columns[2].width = Inches(1.1)
    table.columns[3].width = Inches(1.1)
    
    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.text = val
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.font.name = FONT_BODY
            p.font.size = Pt(9)
            if r_idx == 0:
                p.font.bold = True
                p.font.color.rgb = TEXT_CHARCOAL
                cell.fill.solid()
                cell.fill.fore_color.rgb = CARD_SOFT
            elif r_idx == 4:
                p.font.bold = True
                p.font.color.rgb = AIRTEL_RED
            else:
                p.font.color.rgb = TEXT_CHARCOAL
            if c_idx > 0:
                p.alignment = PP_ALIGN.RIGHT

    # Funnel Image
    funnel_img_path = "docs/presentation/assets/udyam-funnel-economics.png"
    if os.path.exists(funnel_img_path):
        s2.shapes.add_picture(funnel_img_path, Inches(0.8), Inches(4.0), Inches(5.9), Inches(2.6))

    # Right Column: The 3 Failure Modes
    add_card(s2, Inches(7.1), Inches(1.35), Inches(5.6), Inches(4.1), CARD_BG)
    f_box = s2.shapes.add_textbox(Inches(7.3), Inches(1.45), Inches(5.2), Inches(3.9))
    tf = f_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "The Three Structural Failure Modes"
    p.font.name = FONT_HEADING
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = TEXT_CHARCOAL

    failures = [
        ("1. The 3–5 Day Quoting Abyss (56.4% Drop)", 
         "Manual pricing and complex product codes create an intolerable latency gap. 1,113 of 1,974 assessed prospects abandon the pipeline while awaiting quotes, buying piecemeal from local unmanaged ISPs."),
        ("2. The Non-GST Regulatory Wall (4.8x Penalty)", 
         "Leads with active GSTIN activate at 9.6%; leads without GSTIN drop to 2.0%. 55% of India's micro-enterprises operate below GST thresholds and are systematically discarded by legacy KYC."),
        ("3. Crippling Unit Economics (₹15,000 CAC)", 
         "A 17.6-day lead-to-activation cycle and 3.2 manual follow-up calls consume ₹15,000 in direct sales acquisition costs against a ₹6,900 median monthly revenue, yielding a crippling 6.0-month payback period.")
    ]
    for title, desc in failures:
        p = tf.add_paragraph()
        p.space_before = Pt(8)
        r = p.add_run()
        r.text = title
        r.font.bold = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = TEXT_CHARCOAL
        
        p2 = tf.add_paragraph()
        p2.space_before = Pt(2)
        r2 = p2.add_run()
        r2.text = desc
        r2.font.size = Pt(9)
        r2.font.color.rgb = TEXT_MUTED

    # Bottom Right Accent Card: Target Mandate
    add_card(s2, Inches(7.1), Inches(5.6), Inches(5.6), Inches(1.2), CARD_SOFT)
    m_box = s2.shapes.add_textbox(Inches(7.3), Inches(5.7), Inches(5.2), Inches(1.0))
    tf = m_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = "Target Strategic Mandate: "
    r.font.bold = True
    r.font.size = Pt(9.5)
    r.font.color.rgb = AIRTEL_RED
    r2 = p.add_run()
    r2.text = "Compress quoting latency from 5 days to <60 seconds, eliminate the 2.0% non-GST penalty via instant Udyam lookup & composite declaration, and deploy self-serve status tracking to eliminate 87.5% of status chase calls."
    r2.font.size = Pt(9)
    r2.font.color.rgb = TEXT_CHARCOAL

    # =========================================================================
    # SLIDE 3: CUSTOMER SEGMENTATION & BUNDLE MATRIX
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, BG_IVORY)
    add_header(s3, "Customer Segmentation & CPQ Bundle Synthesis", "Synthesizing 25 Catalogue Products into 4 High-Conversion MSME Bundles")
    add_footer(s3, 3)

    bundles = [
        {
            "num": "1. Kirana & Retail",
            "share": "55% Base · Very High Price Sens.",
            "setup": "Mobile hotspot + QR on counter",
            "name": "Udyam Vyapar Pack",
            "price": "₹1,499 / month",
            "bullets": [
                "100 Mbps Fixed Broadband Fiber",
                "Dual-Band Wi-Fi 6 Router Included",
                "UPI Merchant Priority SLA",
                "2x Business SIMs (100GB Pool)"
            ],
            "reg": "GST-Free Onboarding:\nUdyam Reg + PAN Declaration"
        },
        {
            "num": "2. Clinics & Labs",
            "share": "25% Base · Medium Price Sens.",
            "setup": "Home ISP + Personal Gmail",
            "name": "Udyam Professional",
            "price": "₹2,499 / month",
            "bullets": [
                "300 Mbps Dedicated Fiber",
                "Static IP for EMR/ABHA Compliance",
                "5x Google Workspace Enterprise",
                "500GB Airtel Cloud Storage Backup"
            ],
            "reg": "Key Value Driver:\nABHA regulatory compliance & 99.9% SLA"
        },
        {
            "num": "3. Multi-Site Chains",
            "share": "15% Base · Med–Low Price Sens.",
            "setup": "3–10 branch retail / dining hubs",
            "name": "Udyam Multi-Site",
            "price": "₹4,999 / mo / hub",
            "bullets": [
                "500 Mbps Fiber + 4G Backup",
                "Automated Failover Gateway",
                "4-Cam Cloud CCTV (30-day buffer)",
                "Centralized Single-Invoice Portal"
            ],
            "reg": "Key Value Driver:\nZero POS outage + unified multi-store NOC"
        },
        {
            "num": "4. Manufacturing",
            "share": "5% Base · Low Price Sens.",
            "setup": "Leased line / local fragmented ISP",
            "name": "Udyam Industrial",
            "price": "₹14,999 / month",
            "bullets": [
                "1 Gbps Leased Line (1:1 Symmetrical)",
                "Industrial IoT Gateway for Machines",
                "Perimeter Cloud Security Firewall",
                "Dedicated Enterprise RM Support"
            ],
            "reg": "Key Value Driver:\nDeterministic CNC latency & ERP cloud sync"
        }
    ]

    card_w = Inches(2.88)
    card_gap = Inches(0.2)
    left_start = Inches(0.6)

    for i, b in enumerate(bundles):
        c_left = left_start + i * (card_w + card_gap)
        add_card(s3, c_left, Inches(1.35), card_w, Inches(4.3), CARD_BG)
        
        tb = s3.shapes.add_textbox(c_left + Inches(0.15), Inches(1.45), card_w - Inches(0.3), Inches(4.1))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = b["num"]
        p.font.name = FONT_HEADING
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_CHARCOAL
        
        p = tf.add_paragraph()
        p.text = b["share"]
        p.font.size = Pt(7.5)
        p.font.color.rgb = TEXT_MUTED
        
        p = tf.add_paragraph()
        p.text = "Setup: " + b["setup"]
        p.font.size = Pt(7.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(4)
        
        p = tf.add_paragraph()
        p.text = b["name"]
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = AIRTEL_RED
        
        p = tf.add_paragraph()
        p.text = b["price"]
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = TEXT_CHARCOAL
        p.space_after = Pt(4)
        
        for item in b["bullets"]:
            p = tf.add_paragraph()
            p.text = "• " + item
            p.font.size = Pt(7.5)
            p.font.color.rgb = TEXT_CHARCOAL
            p.space_before = Pt(1.5)
            
        p = tf.add_paragraph()
        p.text = b["reg"]
        p.font.size = Pt(7.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(6)

    # Bottom Full-Width Card: Reverse Budget Solver
    add_card(s3, Inches(0.6), Inches(5.8), Inches(12.133), Inches(1.05), CARD_SOFT)
    b_box = s3.shapes.add_textbox(Inches(0.8), Inches(5.85), Inches(8.5), Inches(0.95))
    tf = b_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Symbolic Reverse Budget Solver (\"Mera Budget ₹X Hai\"):"
    p.font.name = FONT_HEADING
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = TEXT_CHARCOAL
    
    p2 = tf.add_paragraph()
    p2.text = "When an owner specifies a ceiling budget, our Branch-and-Bound DAG solver calculates: max Σ v_i x_i  s.t. Σ p_i x_i ≤ B_target, Prerequisites(x) = 1. Dynamic pruning guarantees valid, optimal bundles in <0.5ms with zero LLM hallucination."
    p2.font.size = Pt(8.5)
    p2.font.color.rgb = TEXT_CHARCOAL
    p2.space_before = Pt(2)

    # Mini DAG preview on the right
    dag_img_path = "docs/presentation/assets/udyam-cpq-dag.png"
    if os.path.exists(dag_img_path):
        s3.shapes.add_picture(dag_img_path, Inches(9.5), Inches(5.85), Inches(3.0), Inches(0.9))

    # =========================================================================
    # SLIDE 4: SYSTEM ARCHITECTURE — 4-STAGE PIPELINE
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, BG_IVORY)
    add_header(s4, "System Architecture: 4-Stage Neuro-Symbolic Pipeline", "Autonomous Acquisition Topology: From Ambient Natural Language to Fulfilled Order")
    add_footer(s4, 4)

    # Big Architecture Diagram
    arch_img_path = "docs/presentation/assets/udyam-architecture.png"
    if os.path.exists(arch_img_path):
        s4.shapes.add_picture(arch_img_path, Inches(0.6), Inches(1.35), Inches(12.133), Inches(3.0))

    # 4 Stage Cards Below
    stages = [
        ("Stage 1: Conversational Advisor", [
            ("Dual-Engine Architecture: ", "Gemini 2.5 Flash for natural intent understanding + deterministic Pydantic v2 extraction."),
            ("10 Indic Languages: ", "In-place script toggle across Hindi, Tamil, Telugu, Kannada, etc. with zero latency."),
            ("Zero Hallucination: ", "Strictly bounds recommendations to validated catalogue IDs.")
        ]),
        ("Stage 2: CPQ DAG Solver", [
            ("Prerequisite Engine: ", "Enforces topological validity (e.g., Static IP requires Fixed Fiber line)."),
            ("Hard GSTIN Firewall: ", "Traps illegal SKU requests by non-GST merchants, diverting to composite options."),
            ("Dynamic Knapsack: ", "Instantaneous bundle recalculation with contract length discounts in <0.5ms.")
        ]),
        ("Stage 3: DPDP Smart KYC Gate", [
            ("Zero-Persistence Privacy: ", "12-digit national IDs redacted in-memory upon byte ingestion ([ID Redacted])."),
            ("SHA-256 Byte Caching: ", "Cryptographic hashing prevents replay attacks and redundant OCR processing."),
            ("RapidFuzz Entity Match: ", "Robust token-sort ratio (>85% threshold) tolerates phonetic spelling drifts.")
        ]),
        ("Stage 4: Tracker & Rescue", [
            ("6-Stage Status View: ", "Transparent customer portal eliminates 3.2 follow-up calls per lead."),
            ("LightGBM Model (AUC 0.84): ", "Decision tree predicts drop probability based on hesitation signals."),
            ("Automated Rescue: ", "Dispatches targeted WhatsApp links with pre-filled state tokens to revive stalled leads.")
        ])
    ]

    card_w4 = Inches(2.88)
    gap4 = Inches(0.2)
    for i, (title, points) in enumerate(stages):
        c_left = Inches(0.6) + i * (card_w4 + gap4)
        add_card(s4, c_left, Inches(4.55), card_w4, Inches(2.25), CARD_BG)
        
        tb = s4.shapes.add_textbox(c_left + Inches(0.12), Inches(4.65), card_w4 - Inches(0.24), Inches(2.05))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_HEADING
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = TEXT_CHARCOAL
        
        for b_bold, b_text in points:
            p = tf.add_paragraph()
            p.space_before = Pt(3)
            r = p.add_run()
            r.text = "• " + b_bold
            r.font.bold = True
            r.font.size = Pt(7.5)
            r.font.color.rgb = TEXT_CHARCOAL
            r2 = p.add_run()
            r2.text = b_text
            r2.font.size = Pt(7.5)
            r2.font.color.rgb = TEXT_CHARCOAL

    # =========================================================================
    # SLIDE 5: COMPREHENSIVE COMPETITIVE LANDSCAPE & ACCEL MOAT
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, BG_IVORY)
    add_header(s5, "Comprehensive Competitive Landscape & Accel Strategic Moat", "Rigorous Comparison Against Incumbents, Telco Peers, and SaaS Aggregators")
    add_footer(s5, 5)

    add_card(s5, Inches(0.6), Inches(1.35), Inches(12.133), Inches(4.3), CARD_BG)
    
    comp_rows = [
        ["Strategic Dimension", "Accel Business (Project Udyam)", "Jio Business", "Unmanaged Local ISPs", "Digital SaaS Aggregators"],
        ["Acquisition Velocity & Time-to-Quote", "<15 Mins (Self-serve mobile)\nDeterministic instant quoting", "24–48 Hours\nManual callback & sales visit", "2–3 Days\nUnscheduled technician visit", "Immediate\nSingle-product SaaS only"],
        ["Non-GST MSME Access (60% Market)", "Native Udyam / Composite Engine\nZero-drop onboarding", "Strict GSTIN Mandate\nNon-GST leads dropped", "Unregulated Cash\nZero legal protection / SLA", "Strict GSTIN Mandate\nB2B tax invoices required"],
        ["DPDP Act 2023 Privacy Compliance", "Zero-Persistence In-Memory Redaction\nPurpose-limited consent", "Standard Cloud Storage\nPII stored on disk", "Zero Privacy\nPaper copies, raw WhatsApp", "Third-Party Analytics\nCross-domain ad cookies"],
        ["Indic Multilingual Support", "10 Indic Languages\nReal-time script toggle", "English + Hindi only\nStatic portal forms", "Verbal local dialect only\nZero digital interface", "English-only interfaces"],
        ["Channel Partner Coexistence", "Partner Assisted OBO Mode\n15% protected recurring commission", "Direct Sales Focus\nDisintermediates dealers", "Fragmented Resellers\nNo technology integration", "100% Direct Online\nCompetes with channel"],
        ["Unified Billing & SLA Accountability", "Single Invoice, Single NOC\n99.5% unified telecom + cloud SLA", "Separate Invoices\nTelecom vs Cloud split", "Cash Receipts\nNo SLA, untracked outages", "4–6 Separate Subscriptions\nMultiple credit card charges"]
    ]

    t5_shape = s5.shapes.add_table(7, 5, Inches(0.8), Inches(1.45), Inches(11.733), Inches(4.1))
    t5 = t5_shape.table
    t5.columns[0].width = Inches(2.3)
    t5.columns[1].width = Inches(2.6)
    t5.columns[2].width = Inches(2.2)
    t5.columns[3].width = Inches(2.2)
    t5.columns[4].width = Inches(2.4)

    for r_idx, row in enumerate(comp_rows):
        for c_idx, val in enumerate(row):
            cell = t5.cell(r_idx, c_idx)
            cell.text = val
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.font.name = FONT_BODY
            p.font.size = Pt(8)
            if r_idx == 0:
                p.font.bold = True
                p.font.color.rgb = TEXT_CHARCOAL
                cell.fill.solid()
                cell.fill.fore_color.rgb = CARD_SOFT
            elif c_idx == 1:
                p.font.bold = True
                p.font.color.rgb = AIRTEL_RED
            else:
                p.font.color.rgb = TEXT_CHARCOAL

    # Bottom Summary Callout
    add_card(s5, Inches(0.6), Inches(5.8), Inches(12.133), Inches(1.05), CARD_SOFT)
    sum_box = s5.shapes.add_textbox(Inches(0.8), Inches(5.85), Inches(11.733), Inches(0.95))
    tf = sum_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = "The Accel Strategic Moat: "
    r.font.bold = True
    r.font.size = Pt(10)
    r.font.color.rgb = TEXT_CHARCOAL
    r2 = p.add_run()
    r2.text = "By unlocking the 3.5 Crore Non-GST MSME base and preserving dealer incentives through dynamic QR attribution, Project Udyam Digital achieves unprecedented acquisition velocity without triggering channel friction or regulatory non-compliance. Accel becomes Bharat's default digital operating system for small enterprises."
    r2.font.size = Pt(9)
    r2.font.color.rgb = TEXT_CHARCOAL

    # =========================================================================
    # SLIDE 6: HOSTILE AUDIT & PLANTED DEFECT TRAPPING
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, BG_IVORY)
    add_header(s6, "Adversarial Verification: Trapping Planted KYC Defects & Edge Cases", "Empirical Validation Against Benchmark Anomaly Suite (kyc_documents/ K01–K12)")
    add_footer(s6, 6)

    # Left Column: Benchmark Anomaly Trapping
    add_card(s6, Inches(0.6), Inches(1.35), Inches(5.9), Inches(3.6), CARD_BG)
    tb = s6.shapes.add_textbox(Inches(0.8), Inches(1.45), Inches(5.5), Inches(0.35))
    tb.text_frame.paragraphs[0].text = "Benchmark Anomaly Trapping Matrix"
    tb.text_frame.paragraphs[0].font.bold = True
    tb.text_frame.paragraphs[0].font.size = Pt(11)
    tb.text_frame.paragraphs[0].font.color.rgb = TEXT_CHARCOAL

    k_rows = [
        ["Case ID", "Planted Anomaly", "Deterministic Trapping Result"],
        ["K01", "Cancelled GSTIN\n(27AABCU9603R1ZM)", "Trapped in 12ms. Seamless 1-click fallback to Udyam / Composite declaration."],
        ["K05", "Schema Violation\n(Missing Signatory POA)", "API catches missing payload; returns localized, actionable re-upload prompt."],
        ["K07", "Entity Name Inconsistency\n(Prop. Ramesh vs Neelgiri)", "RapidFuzz token-sort ratio (91.4%) validates legal proprietorship link."],
        ["K11", "Stale Utility Bill\n(257 days old vs 2026-07-15)", "Trapped immediately (>90-day statutory threshold); requests fresh utility bill."]
    ]
    t6_shape = s6.shapes.add_table(5, 3, Inches(0.8), Inches(1.85), Inches(5.5), Inches(2.9))
    t6 = t6_shape.table
    t6.columns[0].width = Inches(0.9)
    t6.columns[1].width = Inches(1.8)
    t6.columns[2].width = Inches(2.8)

    for r_idx, row in enumerate(k_rows):
        for c_idx, val in enumerate(row):
            cell = t6.cell(r_idx, c_idx)
            cell.text = val
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.font.name = FONT_BODY
            p.font.size = Pt(8)
            if r_idx == 0:
                p.font.bold = True
                p.font.color.rgb = TEXT_CHARCOAL
                cell.fill.solid()
                cell.fill.fore_color.rgb = CARD_SOFT
            elif c_idx == 0:
                p.font.bold = True
                p.font.color.rgb = AIRTEL_RED
            else:
                p.font.color.rgb = TEXT_CHARCOAL

    # Left Bottom Card: Adversarial Security Hardening
    add_card(s6, Inches(0.6), Inches(5.1), Inches(5.9), Inches(1.75), CARD_SOFT)
    sec_box = s6.shapes.add_textbox(Inches(0.8), Inches(5.2), Inches(5.5), Inches(1.55))
    tf = sec_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Adversarial Security Hardening"
    p.font.name = FONT_HEADING
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = TEXT_CHARCOAL

    sec_bullets = [
        ("100/100 Multi-Dialect Jailbreaks Neutralized: ", "Defeated prompt injections, price override tampering, and system prompt exfiltration across Hindi, Hinglish & English."),
        ("Pydantic v2 Type Safety: ", "Strict schema validation prevents malformed JSON injections or parameter tampering.")
    ]
    for b_bold, b_text in sec_bullets:
        p = tf.add_paragraph()
        p.space_before = Pt(3)
        r = p.add_run()
        r.text = "• " + b_bold
        r.font.bold = True
        r.font.size = Pt(8)
        r.font.color.rgb = TEXT_CHARCOAL
        r2 = p.add_run()
        r2.text = b_text
        r2.font.size = Pt(8)
        r2.font.color.rgb = TEXT_CHARCOAL

    # Right Column: KYC Architecture Diagram & Test Suite Status
    add_card(s6, Inches(6.8), Inches(1.35), Inches(5.9), Inches(4.3), CARD_BG)
    kyc_title = s6.shapes.add_textbox(Inches(7.0), Inches(1.45), Inches(5.5), Inches(0.35))
    kyc_title.text_frame.paragraphs[0].text = "Smart KYC Verification Architecture"
    kyc_title.text_frame.paragraphs[0].font.bold = True
    kyc_title.text_frame.paragraphs[0].font.size = Pt(11)
    kyc_title.text_frame.paragraphs[0].font.color.rgb = TEXT_CHARCOAL

    kyc_img_path = "docs/presentation/assets/udyam-kyc-gate.png"
    if os.path.exists(kyc_img_path):
        s6.shapes.add_picture(kyc_img_path, Inches(7.0), Inches(1.85), Inches(5.5), Inches(2.9))

    guar_box = s6.shapes.add_textbox(Inches(7.0), Inches(4.85), Inches(5.5), Inches(0.7))
    tf = guar_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Zero-Persistence DPDP Guarantee: Signatory IDs are stripped of 12-digit numbers in-memory prior to logging, caching, or database storage."
    p.font.size = Pt(8.5)
    p.font.color.rgb = TEXT_MUTED

    # Right Bottom Card: Automated Test Suite Status
    add_card(s6, Inches(6.8), Inches(5.8), Inches(5.9), Inches(1.05), CARD_BG)
    ts_box = s6.shapes.add_textbox(Inches(7.0), Inches(5.9), Inches(5.5), Inches(0.85))
    tf = ts_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = "Automated Test Suite Status: "
    r.font.bold = True
    r.font.size = Pt(10)
    r.font.color.rgb = TEXT_CHARCOAL
    r2 = p.add_run()
    r2.text = "37 / 37 Pytest Tests Passing (100% Pass Rate)\n"
    r2.font.bold = True
    r2.font.size = Pt(10)
    r2.font.color.rgb = SUCCESS_GREEN
    r3 = p.add_run()
    r3.text = "Verified against symbolic CPQ solver, GSTIN firewall, RapidFuzz entity matcher, anchor invariant (2026-07-15), and LightGBM model."
    r3.font.size = Pt(8)
    r3.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 7: QUANTIFIED UNIT ECONOMICS & PHYGITAL ROLLOUT
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, BG_IVORY)
    add_header(s7, "Unit Economics Transformation, Business Impact & Strategic Rollout", "Quantified Before vs. After Funnel Economics and 12-Month National Scale Strategy")
    add_footer(s7, 7)

    # Left Column: Funnel Transformation Table
    add_card(s7, Inches(0.6), Inches(1.35), Inches(6.2), Inches(3.6), CARD_BG)
    t_box = s7.shapes.add_textbox(Inches(0.8), Inches(1.45), Inches(5.8), Inches(0.35))
    t_box.text_frame.paragraphs[0].text = "Funnel Unit Economic Transformation"
    t_box.text_frame.paragraphs[0].font.bold = True
    t_box.text_frame.paragraphs[0].font.size = Pt(11)
    t_box.text_frame.paragraphs[0].font.color.rgb = TEXT_CHARCOAL

    econ_rows = [
        ["Core Metric", "Baseline (smb_leads)", "With Project Udyam", "Net Impact"],
        ["Quoting Acceptance Rate", "43.6%", "82.4%", "+38.8% Lift"],
        ["Non-GST Conversion Rate", "2.0%", "8.5%", "+4.25x Gain"],
        ["Lead-to-Activation SLA", "17.6 Days", "3.8 Days", "−78.4% Faster"],
        ["Blended CAC per SMB", "₹15,000", "₹3,250", "−78.3% Cost"],
        ["Customer Status Chases", "3.2 calls", "0.4 calls", "−87.5% Load"],
        ["Projected 6-Month Churn", "14.2%", "6.8%", "−52.1% Churn"]
    ]
    t7_shape = s7.shapes.add_table(7, 4, Inches(0.8), Inches(1.85), Inches(5.8), Inches(2.9))
    t7 = t7_shape.table
    t7.columns[0].width = Inches(2.3)
    t7.columns[1].width = Inches(1.2)
    t7.columns[2].width = Inches(1.2)
    t7.columns[3].width = Inches(1.1)

    for r_idx, row in enumerate(econ_rows):
        for c_idx, val in enumerate(row):
            cell = t7.cell(r_idx, c_idx)
            cell.text = val
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.font.name = FONT_BODY
            p.font.size = Pt(8.5)
            if r_idx == 0:
                p.font.bold = True
                p.font.color.rgb = TEXT_CHARCOAL
                cell.fill.solid()
                cell.fill.fore_color.rgb = CARD_SOFT
            elif c_idx == 3:
                p.font.bold = True
                p.font.color.rgb = SUCCESS_GREEN
                p.alignment = PP_ALIGN.RIGHT
            elif c_idx > 0:
                p.font.color.rgb = TEXT_CHARCOAL
                p.alignment = PP_ALIGN.RIGHT
            else:
                p.font.bold = True
                p.font.color.rgb = TEXT_CHARCOAL

    # Left Bottom Card: Phygital Partner Assisted Ingress (OBO Mode)
    add_card(s7, Inches(0.6), Inches(5.1), Inches(6.2), Inches(1.75), CARD_SOFT)
    obo_box = s7.shapes.add_textbox(Inches(0.8), Inches(5.2), Inches(5.8), Inches(1.55))
    tf = obo_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Phygital Partner Assisted Ingress (OBO Mode)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = TEXT_CHARCOAL

    p2 = tf.add_paragraph()
    p2.space_before = Pt(3)
    r = p2.add_run()
    r.text = "Coexistence over Cannibalization: "
    r.font.bold = True
    r.font.size = Pt(8.5)
    r.font.color.rgb = TEXT_CHARCOAL
    r2 = p2.add_run()
    r2.text = "Field sales executives and 120,000+ local Airtel retailers utilize the same platform in \"On Behalf Of\" (OBO) mode. Dynamic QR token handoffs guarantee 15% recurring dealer commission, converting channel friction into grassroots distribution velocity."
    r2.font.size = Pt(8.5)
    r2.font.color.rgb = TEXT_CHARCOAL

    # Right Column: 12-Month Phased National Rollout
    add_card(s7, Inches(7.1), Inches(1.35), Inches(5.6), Inches(4.2), CARD_BG)
    ro_box = s7.shapes.add_textbox(Inches(7.3), Inches(1.45), Inches(5.2), Inches(4.0))
    tf = ro_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "12-Month Phased National Rollout Strategy"
    p.font.name = FONT_HEADING
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = TEXT_CHARCOAL

    phases = [
        ("Phase 1: Metros & Kirana Hubs (Months 1–3)", [
            "Target: 8 Tier-1 Metros (Delhi NCR, Mumbai, Bengaluru, Chennai, Hyderabad, Kolkata, Pune, Ahmedabad).",
            "Focus: Kirana Vyapar Pack & Clinic Bundles via retail store QR codes.",
            "Target: 25,000 active MSMEs, ₹50 Cr annualized ARR."
        ]),
        ("Phase 2: Industrial Clusters (Months 4–6)", [
            "Target: 40 Tier-2 manufacturing hubs (Surat, Coimbatore, Ludhiana, Indore).",
            "Focus: Industrial Edge Leased Line & Cloud CCTV multi-site bundles.",
            "Target: 100,000 active MSMEs, ₹280 Cr annualized ARR."
        ]),
        ("Phase 3: Pan-India Bharat Scale (Months 7–12)", [
            "Target: 500+ Tier-3/4 districts across 10 Indic languages.",
            "Target: 500,000 active MSMEs, ₹1,200 Cr annualized ARR."
        ])
    ]
    for ph_title, ph_bullets in phases:
        p = tf.add_paragraph()
        p.space_before = Pt(8)
        r = p.add_run()
        r.text = ph_title
        r.font.bold = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = AIRTEL_RED
        for b_item in ph_bullets:
            p = tf.add_paragraph()
            p.space_before = Pt(1.5)
            r = p.add_run()
            r.text = "• " + b_item
            r.font.size = Pt(8.5)
            r.font.color.rgb = TEXT_CHARCOAL

    # Right Bottom Card: Executive Summary Box
    add_card(s7, Inches(7.1), Inches(5.7), Inches(5.6), Inches(1.15), CARD_BG)
    sum_box = s7.shapes.add_textbox(Inches(7.3), Inches(5.75), Inches(5.2), Inches(1.05))
    tf = sum_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = "Executive Summary: "
    r.font.bold = True
    r.font.size = Pt(9.5)
    r.font.color.rgb = TEXT_CHARCOAL
    r2 = p.add_run()
    r2.text = "Project Udyam Digital transforms Accel Business from a slow, paper-bound enterprise carrier into Bharat's default digital operating system for small enterprises—compressing 17.6 days into 15 minutes."
    r2.font.size = Pt(8.5)
    r2.font.color.rgb = TEXT_MUTED

    # Save output
    out_pptx = "docs/Neural_Nexus_Airtel_Sync_2026_Digital_Track.pptx"
    prs.save(out_pptx)
    print(f"Generated official PPTX: {out_pptx} ({os.path.getsize(out_pptx)} bytes)")

if __name__ == "__main__":
    build_presentation()
