import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# -------------------------------------------------------------
# PALETTE & TYPOGRAPHY CONSTANTS (Ivory & Charcoal Academic Standard)
# -------------------------------------------------------------
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

TEAM_NAME = "Neural Nexus"
CAMPUS_NAME = "ABV-IIITM Gwalior"

def set_slide_background(slide, color):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_header(slide, title_text, subtitle_text):
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

def add_footer(slide, slide_num, is_annexure=False):
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
    if is_annexure:
        p.text = f"Airtel Sync 2026 · Digital Track | Project Udyam Digital · Annexure (Reference Only)              Team {TEAM_NAME} ({CAMPUS_NAME})              Annexure"
    else:
        p.text = f"Airtel Sync 2026 · Digital Track (Enterprise Track A) | Project Udyam Digital              Team {TEAM_NAME} ({CAMPUS_NAME})              Slide {slide_num} of 7"
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

def build_editable_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 0: OFFICIAL INTRODUCTION SLIDE (Excluded from 7-Slide Count)
    # =========================================================================
    s0 = prs.slides.add_slide(blank_layout)
    set_slide_background(s0, BG_IVORY)
    
    # Tag
    tb = s0.shapes.add_textbox(Inches(0.6), Inches(0.55), Inches(12.133), Inches(0.35))
    p = tb.text_frame.paragraphs[0]
    p.text = "BHARTI AIRTEL · AIRTEL SYNC 2026 · DIGITAL TRACK (ENTERPRISE TRACK A)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = AIRTEL_RED
    p.alignment = PP_ALIGN.CENTER
    
    # Title
    tb = s0.shapes.add_textbox(Inches(0.6), Inches(0.95), Inches(12.133), Inches(1.1))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "Project Udyam Digital"
    p.font.name = FONT_HEADING
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = TEXT_CHARCOAL
    p.alignment = PP_ALIGN.CENTER
    
    p2 = tf.add_paragraph()
    p2.text = "Making 6 Crore+ Indian MSMEs Go Digital in One Sitting"
    p2.font.size = Pt(15)
    p2.font.color.rgb = TEXT_MUTED
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(3)

    p3 = tf.add_paragraph()
    p3.text = "Autonomous Neuro-Symbolic CPQ, Instant DPDP KYC & Multi-Site Orchestration for Accel Business"
    p3.font.size = Pt(10.5)
    p3.font.color.rgb = TEXT_MUTED
    p3.alignment = PP_ALIGN.CENTER
    p3.space_before = Pt(2)
    
    # Divider
    div = s0.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.5), Inches(2.3), Inches(10.333), Inches(0.015))
    div.fill.solid()
    div.fill.fore_color.rgb = BORDER_GRAY
    div.line.fill.background()

    # Left Card: Team & Registration
    add_card(s0, Inches(0.8), Inches(2.55), Inches(5.6), Inches(3.8), CARD_BG)
    c1 = s0.shapes.add_textbox(Inches(1.0), Inches(2.7), Inches(5.2), Inches(3.5))
    tf1 = c1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "Team & Institutional Registration"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = TEXT_CHARCOAL
    
    team_points = [
        ("Team Name: ", "Neural Nexus"),
        ("Campus / Institute: ", "ABV-Indian Institute of Information Technology and Management (ABV-IIITM), Gwalior"),
        ("Competition Track: ", "Airtel Sync 2026 – Digital Track (Enterprise Track A)"),
        ("Team Members: ", "Hrushikesh Ramilla (HR - Systems & ML Lead), YK (Product & Applied Research)"),
        ("Evaluation Anchor Invariant: ", "Strictly pinned to datetime.date(2026, 7, 15) for KYC freshness.")
    ]
    for b_bold, b_text in team_points:
        p = tf1.add_paragraph()
        p.space_before = Pt(7)
        r1 = p.add_run()
        r1.text = "• " + b_bold
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = TEXT_CHARCOAL
        r2 = p.add_run()
        r2.text = b_text
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = TEXT_CHARCOAL

    # Right Card: Prototype Demo Video & Cloud Links
    add_card(s0, Inches(6.933), Inches(2.55), Inches(5.6), Inches(3.8), CARD_SOFT)
    c2 = s0.shapes.add_textbox(Inches(7.133), Inches(2.7), Inches(5.2), Inches(3.5))
    tf2 = c2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "Live Production Deliverables & Demo Video"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = TEXT_CHARCOAL
    
    links = [
        ("Prototype Demo Video / Audit Proof: ", "http://65.1.112.251/audit/audit_dashboard.html (100-Case Visual Audit Proof)"),
        ("Live Production Cloud Monolith: ", "http://65.1.112.251 (FastAPI + React 18 on AWS EC2 Ubuntu 26.04)"),
        ("Interactive Swagger API Documentation: ", "http://65.1.112.251/docs (37/37 Automated Pytest Verification)"),
        ("Open-Source GitHub Repository: ", "https://github.com/Hrushikesh-ramilla/project-udyam-digital (Branch: main)"),
        ("Production Technology Stack: ", "FastAPI, React 18, TypeScript, LightGBM, RapidFuzz, DPDP SHA-256 Engine.")
    ]
    for b_bold, b_text in links:
        p = tf2.add_paragraph()
        p.space_before = Pt(7)
        r1 = p.add_run()
        r1.text = "• " + b_bold
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = AIRTEL_RED if "Demo" in b_bold or "Live" in b_bold else TEXT_CHARCOAL
        r2 = p.add_run()
        r2.text = b_text
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = TEXT_CHARCOAL

    # Intro footer note
    f_box = s0.shapes.add_textbox(Inches(0.6), Inches(6.6), Inches(12.133), Inches(0.4))
    p = f_box.text_frame.paragraphs[0]
    p.text = "Submission Note: This slide is the official Introduction Slide (excluded from 7-slide count). The following 7 slides present our technical approach, detailed competitive analysis, and quantified business impact."
    p.font.size = Pt(8.5)
    p.font.color.rgb = TEXT_MUTED
    p.alignment = PP_ALIGN.CENTER

    # Save output
    out_name = f"Neural Nexus_{CAMPUS_NAME}_Editable.pptx"
    prs.save(out_name)
    prs.save("docs/" + out_name)
    print(f"Generated editable template: {out_name}")

if __name__ == "__main__":
    build_editable_presentation()
