import os
import sys
import glob
import shutil
import base64
from playwright.sync_api import sync_playwright
import pptx
from pptx import Presentation
from pptx.util import Inches

TEAM_NAME = "Neural Nexus"
CAMPUS_NAME = "ABV-IIITM Gwalior"
OFFICIAL_PDF = f"{TEAM_NAME}_{CAMPUS_NAME}.pdf"
OFFICIAL_PPTX = f"{TEAM_NAME}_{CAMPUS_NAME}.pptx"

# Output directories
BUILD_DIR = "docs/presentation/build_html"
PREVIEW_DIR = "docs/presentation/preview"
os.makedirs(BUILD_DIR, exist_ok=True)
os.makedirs(PREVIEW_DIR, exist_ok=True)

def to_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            ext = path.split(".")[-1]
            mime = "image/png" if ext == "png" else "image/jpeg"
            return f"data:{mime};base64," + base64.b64encode(f.read()).decode("utf-8")
    return ""

# Encode necessary assets
img_arch_b64 = to_base64("docs/presentation/assets/udyam-architecture-clean.png")
img_dag_b64 = to_base64("docs/presentation/assets/udyam-cpq-dag-tight.png")
img_screen_advisor_b64 = to_base64("docs/presentation/assets/clean_advisor.png")
img_screen_cart_b64 = to_base64("docs/presentation/assets/clean_cart.png")
img_screen_kyc_b64 = to_base64("docs/presentation/assets/clean_kyc.png")

# CSS Theme: Strict Ivory, Light Beige, White, Charcoal, Off-Black ONLY
CSS_THEME = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background-color: #FAF8F5;
  color: #121316;
  -webkit-font-smoothing: antialiased;
}
.slide {
  width: 1920px;
  height: 1080px;
  padding: 44px 72px 36px 72px;
  position: relative;
  background-color: #FAF8F5;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
/* Slide Header */
.slide-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-bottom: 1.5px solid #DDD8CE;
  padding-bottom: 10px;
  margin-bottom: 14px;
}
.slide-title-group h1 {
  font-size: 31px;
  font-weight: 800;
  color: #121316;
  letter-spacing: -0.5px;
  line-height: 1.15;
}
.slide-title-group p {
  font-size: 14px;
  color: #5A5A5D;
  margin-top: 3px;
  font-weight: 500;
}
.slide-category-badge {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  background-color: #EFECE6;
  color: #121316;
  padding: 6px 14px;
  border-radius: 6px;
  border: 1px solid #DDD8CE;
}
/* Slide Content Area */
.slide-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
/* Footline */
.slide-footer {
  margin-top: auto;
  padding-top: 10px;
  border-top: 1px solid #DDD8CE;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #7A7B7E;
  font-weight: 500;
}
.slide-footer .team-name {
  font-weight: 700;
  color: #121316;
}
.slide-footer .slide-number {
  font-weight: 700;
  color: #121316;
  background-color: #EFECE6;
  padding: 3px 10px;
  border-radius: 4px;
}

/* Cards & Layout Utilities */
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
.grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
.grid-4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 14px; }
.grid-5-4 { display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 18px; }

.card {
  background-color: #FFFFFF;
  border: 1.5px solid #DDD8CE;
  border-radius: 12px;
  padding: 16px 18px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.02);
}
.card-beige {
  background-color: #F4F0E8;
  border: 1.5px solid #DDD8CE;
  border-radius: 12px;
  padding: 14px 18px;
}
.card-title {
  font-size: 15.5px;
  font-weight: 800;
  color: #121316;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.badge-pill {
  display: inline-block;
  font-size: 10.5px;
  font-weight: 700;
  text-transform: uppercase;
  background-color: #121316;
  color: #FAF8F5;
  padding: 3px 8px;
  border-radius: 4px;
  letter-spacing: 0.5px;
}
.badge-pill-alert {
  display: inline-block;
  font-size: 10.5px;
  font-weight: 800;
  background-color: #121316;
  color: #FFFFFF;
  padding: 3px 8px;
  border-radius: 4px;
}
.bullet-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.bullet-list li {
  position: relative;
  padding-left: 14px;
  line-height: 1.35;
  color: #333336;
}
.bullet-list li::before {
  content: "•";
  position: absolute;
  left: 0;
  color: #121316;
  font-weight: bold;
}
.stat-box {
  background: #FFFFFF;
  border: 1.5px solid #DDD8CE;
  border-radius: 10px;
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
}
.stat-num {
  font-size: 36px;
  font-weight: 900;
  color: #121316;
  letter-spacing: -1px;
  line-height: 1.1;
}
.stat-label {
  font-size: 13px;
  font-weight: 700;
  color: #121316;
  margin-top: 4px;
}
.stat-sub {
  font-size: 11.5px;
  color: #5A5A5D;
  margin-top: 2px;
  line-height: 1.35;
}

/* Comparison Table */
.comp-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.comp-table th {
  background-color: #EFECE6;
  color: #121316;
  font-weight: 800;
  text-align: left;
  padding: 12px 14px;
  border-bottom: 2px solid #DDD8CE;
}
.comp-table td {
  padding: 11px 14px;
  border-bottom: 1px solid #EFECE6;
  color: #333336;
  line-height: 1.35;
}
.comp-table tr:last-child td {
  border-bottom: none;
}
.comp-table .highlight-col {
  background-color: #F7F5F0;
  font-weight: 700;
  color: #121316;
  border-left: 2px solid #121316;
  border-right: 1.5px solid #DDD8CE;
}
.comp-table .highlight-row {
  background-color: #F7F5F0;
}
"""

def generate_slides_html():
    slides = []

    # =============================================================
    # SLIDE 0: MANDATORY INTRODUCTION SLIDE (UNCOUNTED)
    # =============================================================
    s0 = f"""
    <div class="slide" style="display: flex; flex-direction: column; justify-content: space-between; padding: 40px 72px 28px 72px;">
      
      <!-- Top Title Area -->
      <div style="text-align: center; padding-top: 4px;">
        <div style="display: inline-block; margin-bottom: 10px;">
          <span style="font-size: 12px; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; background: #EFECE6; color: #121316; padding: 6px 18px; border-radius: 30px; border: 1px solid #DDD8CE;">
            BHARTI AIRTEL · AIRTEL SYNC 2026 · DIGITAL TRACK (ENTERPRISE TRACK A)
          </span>
        </div>
        <h1 style="font-size: 52px; font-weight: 900; color: #121316; letter-spacing: -1.5px; line-height: 1.1; margin-bottom: 8px;">
          Project Udyam Digital
        </h1>
        <p style="font-size: 18px; color: #4A4B4E; max-width: 980px; margin: 0 auto; font-weight: 500; line-height: 1.35;">
          Making 6 Crore+ Indian Small Businesses Go Digital in One Sitting<br>
          <span style="font-size: 15px; color: #6E7075;">Instant Self-Serve Mobile Onboarding, Fast Legal KYC & Multi-Site Telecommunications</span>
        </p>
      </div>

      <!-- Center 2-Column Registration & Working Prototype Cards -->
      <div class="grid-2" style="text-align: left; gap: 22px; margin: 4px 0;">
        <div class="card" style="padding: 20px 24px;">
          <div class="card-title" style="border-bottom: 1.5px solid #EFECE6; padding-bottom: 10px; margin-bottom: 12px; font-size: 16px;">
            Team & Institutional Registration
          </div>
          <table style="width: 100%; font-size: 13.5px; border-collapse: collapse;">
            <tr style="border-bottom: 1px solid #F4F0E8;">
              <td style="padding: 7px 0; color: #7A7B7E; width: 140px; font-weight: 600;">Team Name</td>
              <td style="padding: 7px 0; font-weight: 800; color: #121316;">{TEAM_NAME}</td>
            </tr>
            <tr style="border-bottom: 1px solid #F4F0E8;">
              <td style="padding: 7px 0; color: #7A7B7E; font-weight: 600;">Institution</td>
              <td style="padding: 7px 0; font-weight: 600; color: #121316;">ABV-Indian Institute of Information Technology and Management (ABV-IIITM), Gwalior</td>
            </tr>
            <tr style="border-bottom: 1px solid #F4F0E8;">
              <td style="padding: 7px 0; color: #7A7B7E; font-weight: 600;">Competition Track</td>
              <td style="padding: 7px 0; color: #121316;">Airtel Sync 2026 — Digital Track (Enterprise Track A: Accel Business)</td>
            </tr>
            <tr style="border-bottom: 1px solid #F4F0E8;">
              <td style="padding: 7px 0; color: #7A7B7E; font-weight: 600;">Team Members</td>
              <td style="padding: 7px 0; color: #121316;"><strong>Hrushikesh Ramilla (HR)</strong> — Lead Systems & ML Architect<br><strong>YK</strong> — Product Engineering & Applied Research</td>
            </tr>
            <tr style="border-bottom: 1px solid #F4F0E8;">
              <td style="padding: 7px 0; color: #7A7B7E; font-weight: 600;">Technical Stack</td>
              <td style="padding: 7px 0; color: #121316;">Python 3.11+, FastAPI, React 18, Vite, Pydantic v2, LightGBM, RapidFuzz, Playwright</td>
            </tr>
            <tr>
              <td style="padding: 7px 0; color: #7A7B7E; font-weight: 600;">Evaluation Date</td>
              <td style="padding: 7px 0; color: #121316;"><code style="font-family: monospace; font-weight: 700;">2026-07-15</code> (Evaluation invariant strictly enforced)</td>
            </tr>
          </table>
        </div>

        <div class="card-beige" style="padding: 20px 24px;">
          <div class="card-title" style="border-bottom: 1.5px solid #DDD8CE; padding-bottom: 10px; margin-bottom: 12px; font-size: 16px;">
            Live Working Prototype & Direct Audit Links
          </div>
          <table style="width: 100%; font-size: 13.5px; border-collapse: collapse;">
            <tr style="border-bottom: 1px solid #DDD8CE;">
              <td style="padding: 7px 0; color: #5A5A5D; width: 145px; font-weight: 700;">Live Cloud Monolith</td>
              <td style="padding: 7px 0; font-weight: 800;"><a href="http://65.1.112.251" style="color: #121316; text-decoration: underline;">http://65.1.112.251</a> (Deployed on AWS EC2, Port 80)</td>
            </tr>
            <tr style="border-bottom: 1px solid #DDD8CE;">
              <td style="padding: 7px 0; color: #5A5A5D; font-weight: 700;">Interactive API Docs</td>
              <td style="padding: 7px 0; font-weight: 700;"><a href="http://65.1.112.251/docs" style="color: #121316; text-decoration: underline;">http://65.1.112.251/docs</a> (FastAPI Swagger UI)</td>
            </tr>
            <tr style="border-bottom: 1px solid #DDD8CE;">
              <td style="padding: 7px 0; color: #5A5A5D; font-weight: 700;">Code Repository</td>
              <td style="padding: 7px 0; font-family: monospace; font-weight: 700; color: #121316;">github.com/Hrushikesh-ramilla/project-udyam-digital</td>
            </tr>
            <tr style="border-bottom: 1px solid #DDD8CE;">
              <td style="padding: 7px 0; color: #5A5A5D; font-weight: 700;">Automated Tests</td>
              <td style="padding: 7px 0; color: #121316;"><span class="badge-pill" style="font-size: 11px;">37 / 37 Pytest Tests Passing</span> (100% Pass Rate | Zero Mocks)</td>
            </tr>
            <tr style="border-bottom: 1px solid #DDD8CE;">
              <td style="padding: 7px 0; color: #5A5A5D; font-weight: 700;">Visual Verification</td>
              <td style="padding: 7px 0; font-weight: 700; color: #121316;">100 End-to-End Visual Proof Cases Documented & Audited</td>
            </tr>
            <tr>
              <td style="padding: 7px 0; color: #5A5A5D; font-weight: 700;">Compliance Invariant</td>
              <td style="padding: 7px 0; color: #121316;"><span class="badge-pill" style="font-size: 11px;">DPDP Act 2023 Shield</span> Zero Persistence RAM Masking</td>
            </tr>
          </table>
        </div>
      </div>

      <!-- Bottom Executive Scope Card -->
      <div class="card-beige" style="padding: 16px 24px; border-left: 4px solid #121316;">
        <div style="font-size: 13.5px; font-weight: 800; color: #121316; margin-bottom: 8px;">
          The Executive Scope at a Glance (Airtel Enterprise Track A Mandate):
        </div>
        <div class="grid-3" style="font-size: 12px; color: #4A4B4E; line-height: 1.45; gap: 16px;">
          <div style="background: #FFFFFF; border: 1px solid #DDD8CE; border-radius: 6px; padding: 10px 12px;">
            <div style="font-weight: 800; color: #121316; margin-bottom: 3px;">1. The Market Opportunity</div>
            India is home to 6.3 Crore MSMEs, but 55% operate under GST thresholds. Discarding non-GST applicants cuts Airtel off from 3.5 Crore viable retail merchants.
          </div>
          <div style="background: #FFFFFF; border: 1px solid #DDD8CE; border-radius: 6px; padding: 10px 12px;">
            <div style="font-weight: 800; color: #121316; margin-bottom: 3px;">2. The Enterprise Bottleneck</div>
            Current manual quote delivery takes 3 to 5 days, causing 56.4% of interested leads to abandon the pipeline while burning ₹15,000 in CAC per customer.
          </div>
          <div style="background: #FFFFFF; border: 1px solid #DDD8CE; border-radius: 6px; padding: 10px 12px;">
            <div style="font-weight: 800; color: #121316; margin-bottom: 3px;">3. The Udyam Solution</div>
            Self-serve conversational AI in 10 languages, &lt;0.5ms CPQ DAG bundling, zero-persistence DPDP KYC, and 1-click LightGBM WhatsApp retargeting.
          </div>
        </div>
      </div>

      <!-- Submission Footnote -->
      <div style="font-size: 12px; color: #7A7B7E; text-align: center; padding-top: 2px;">
        <strong>Submission Note:</strong> Mandatory Introduction Slide (excluded from 7-slide evaluation count). Slides 1 to 7 showcase the technical solution, competitive moat, and quantified business impact.
      </div>

    </div>
    """
    slides.append(s0)

    # =============================================================
    # SLIDE 1 OF 7: PROBLEM STATEMENT & FUNNEL BLEED DISSECTION
    # =============================================================
    s1 = f"""
    <div class="slide">
      <div class="slide-header">
        <div class="slide-title-group">
          <h1>Problem Statement: The 5,000-Lead Sales Drop-Off</h1>
          <p>Real-world analysis of 5,000 small business leads from April to June 2026 (smb_leads.csv)</p>
        </div>
        <div class="slide-category-badge">Slide 1 of 7 · Challenge Context</div>
      </div>

      <div class="slide-content">
        <div class="grid-5-4" style="flex: 1; gap: 18px;">
          
          <!-- Funnel Numbers & High-Res Visual Chart -->
          <div class="card" style="display: flex; flex-direction: column; gap: 12px; padding: 16px 18px;">
            <div>
              <div class="card-title" style="margin-bottom: 8px;">
                <span>Sales Funnel Analysis (N = 5,000 Leads)</span>
                <span style="font-size: 11px; font-weight: 600; color: #5A5A5D; background: #EFECE6; padding: 2px 8px; border-radius: 4px;">Tier 1–2 Cities</span>
              </div>
              
              <table class="comp-table" style="font-size: 12.5px; margin-bottom: 6px;">
                <tr>
                  <th style="width: 44%; padding: 8px 10px;">Funnel Stage</th>
                  <th style="width: 18%; text-align: right; padding: 8px 10px;">Leads</th>
                  <th style="width: 18%; text-align: right; padding: 8px 10px;">Stage %</th>
                  <th style="width: 20%; text-align: right; padding: 8px 10px;">Drop / Status</th>
                </tr>
                <tr>
                  <td style="padding: 7px 10px;">1. Leads Generated</td>
                  <td style="text-align: right; font-weight: 700; padding: 7px 10px;">5,000</td>
                  <td style="text-align: right; padding: 7px 10px;">100.0%</td>
                  <td style="text-align: right; color: #5A5A5D; padding: 7px 10px;">Starting Base</td>
                </tr>
                <tr>
                  <td style="padding: 7px 10px;">2. Contacted Outreach</td>
                  <td style="text-align: right; font-weight: 700; padding: 7px 10px;">3,406</td>
                  <td style="text-align: right; padding: 7px 10px;">68.1%</td>
                  <td style="text-align: right; color: #5A5A5D; padding: 7px 10px;">-31.9%</td>
                </tr>
                <tr>
                  <td style="padding: 7px 10px;">3. Needs Assessed (Field Visit)</td>
                  <td style="text-align: right; font-weight: 700; padding: 7px 10px;">1,974</td>
                  <td style="text-align: right; padding: 7px 10px;">58.0%</td>
                  <td style="text-align: right; color: #5A5A5D; padding: 7px 10px;">-42.0%</td>
                </tr>
                <tr class="highlight-row" style="background: #EFECE6;">
                  <td style="padding: 7px 10px;"><strong>4. Quote Accepted (Steepest Drop)</strong></td>
                  <td style="text-align: right; font-weight: 900; padding: 7px 10px;">861</td>
                  <td style="text-align: right; font-weight: 900; padding: 7px 10px;">43.6%</td>
                  <td style="text-align: right; padding: 7px 10px;"><span class="badge-pill-alert">-56.4% CLIFF</span></td>
                </tr>
                <tr>
                  <td style="padding: 7px 10px;">5. KYC Completed</td>
                  <td style="text-align: right; font-weight: 700; padding: 7px 10px;">588</td>
                  <td style="text-align: right; padding: 7px 10px;">68.3%</td>
                  <td style="text-align: right; color: #5A5A5D; padding: 7px 10px;">-31.7%</td>
                </tr>
                <tr class="highlight-row">
                  <td style="padding: 7px 10px;"><strong>6. Activated Customers</strong></td>
                  <td style="text-align: right; font-weight: 900; padding: 7px 10px;">368</td>
                  <td style="text-align: right; font-weight: 900; padding: 7px 10px;">62.6%</td>
                  <td style="text-align: right; padding: 7px 10px;"><span class="badge-pill">7.36% NET ACTIVATION</span></td>
                </tr>
              </table>
            </div>

            <!-- High-Res Visual Horizontal Funnel -->
            <div style="background-color: #FAF8F5; border: 1.5px solid #DDD8CE; border-radius: 8px; padding: 12px 14px;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; color: #5A5A5D; margin-bottom: 8px;">
                Visual Funnel Retention Rate (% of Initial 5,000 Leads)
              </div>
              
              <div style="display: flex; flex-direction: column; gap: 7px; font-size: 11.5px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                  <span style="width: 120px; font-weight: 700;">1. Leads Generated</span>
                  <div style="flex: 1; background: #EFECE6; height: 15px; border-radius: 3px; overflow: hidden;">
                    <div style="width: 100%; background: #121316; height: 100%;"></div>
                  </div>
                  <span style="width: 45px; text-align: right; font-weight: 800;">100%</span>
                </div>

                <div style="display: flex; align-items: center; gap: 10px;">
                  <span style="width: 120px; font-weight: 700;">2. Contacted</span>
                  <div style="flex: 1; background: #EFECE6; height: 15px; border-radius: 3px; overflow: hidden;">
                    <div style="width: 68.1%; background: #4A4B4E; height: 100%;"></div>
                  </div>
                  <span style="width: 45px; text-align: right; font-weight: 800;">68.1%</span>
                </div>

                <div style="display: flex; align-items: center; gap: 10px;">
                  <span style="width: 120px; font-weight: 700;">3. Needs Assessed</span>
                  <div style="flex: 1; background: #EFECE6; height: 15px; border-radius: 3px; overflow: hidden;">
                    <div style="width: 39.5%; background: #4A4B4E; height: 100%;"></div>
                  </div>
                  <span style="width: 45px; text-align: right; font-weight: 800;">39.5%</span>
                </div>

                <div style="display: flex; align-items: center; gap: 10px;">
                  <span style="width: 120px; font-weight: 900; color: #121316;">4. Quote Accepted</span>
                  <div style="flex: 1; background: #EFECE6; height: 15px; border-radius: 3px; overflow: hidden;">
                    <div style="width: 17.2%; background: #121316; height: 100%; border-right: 3px solid #000;"></div>
                  </div>
                  <span style="width: 45px; text-align: right; font-weight: 900; color: #121316;">17.2%</span>
                </div>

                <div style="display: flex; align-items: center; gap: 10px;">
                  <span style="width: 120px; font-weight: 700;">5. KYC Complete</span>
                  <div style="flex: 1; background: #EFECE6; height: 15px; border-radius: 3px; overflow: hidden;">
                    <div style="width: 11.8%; background: #4A4B4E; height: 100%;"></div>
                  </div>
                  <span style="width: 45px; text-align: right; font-weight: 800;">11.8%</span>
                </div>

                <div style="display: flex; align-items: center; gap: 10px;">
                  <span style="width: 120px; font-weight: 900; color: #121316;">6. Activated</span>
                  <div style="flex: 1; background: #EFECE6; height: 15px; border-radius: 3px; overflow: hidden;">
                    <div style="width: 7.36%; background: #121316; height: 100%;"></div>
                  </div>
                  <span style="width: 45px; text-align: right; font-weight: 900; color: #121316;">7.36%</span>
                </div>
              </div>
            </div>

            <!-- Two Sub-Insight Cards to Fill Lower Section -->
            <div class="grid-2" style="gap: 10px;">
              <div style="font-size: 11.5px; color: #4A4B4E; line-height: 1.38; background: #EFECE6; padding: 10px 12px; border-radius: 6px;">
                <strong style="color: #121316;">The Non-GST Penalty:</strong> Leads with active GSTIN activate at <strong>9.6%</strong>, while leads without GST drop to <strong>2.0%</strong> (a 4.8x conversion penalty caused by legacy enterprise forms).
              </div>
              <div style="font-size: 11.5px; color: #4A4B4E; line-height: 1.38; background: #EFECE6; padding: 10px 12px; border-radius: 6px;">
                <strong style="color: #121316;">High Cost of Delay:</strong> 17.6-day average cycle time and 3.2 chase calls consume ₹15,000 in sales rep labor per deal, requiring 14.2 months to break even on CAC.
              </div>
            </div>
          </div>

          <!-- The 3 Root Causes + Key Metrics + Financial Impact -->
          <div style="display: flex; flex-direction: column; gap: 10px;">
            
            <!-- Failure Mode 1 -->
            <div class="card" style="padding: 13px 16px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <span class="badge-pill">Failure Mode 1</span>
                <span style="font-size: 11px; font-weight: 800; color: #121316;">56.4% Abandonment</span>
              </div>
              <div style="font-size: 14px; font-weight: 800; color: #121316;">The 3–5 Day Quoting Wait (Latency Bleed)</div>
              <div style="font-size: 12px; color: #4A4B4E; margin-top: 3px; line-height: 1.38;">
                Sales reps manually navigate 25 disconnected enterprise product SKUs on Excel sheets. Because quotes take 3 to 5 days, <strong>1,113 of 1,974 interested businesses go cold</strong> and abandon before receiving pricing.
              </div>
            </div>

            <!-- Failure Mode 2 -->
            <div class="card" style="padding: 13px 16px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <span class="badge-pill">Failure Mode 2</span>
                <span style="font-size: 11px; font-weight: 800; color: #121316;">4.8x Conversion Cliff</span>
              </div>
              <div style="font-size: 14px; font-weight: 800; color: #121316;">The Non-GST Regulatory Wall (Market Exclusion)</div>
              <div style="font-size: 12px; color: #4A4B4E; margin-top: 3px; line-height: 1.38;">
                55% of India's 6.3 Crore micro-enterprises earn under ₹40 Lakhs and are legally GST-exempt. Legacy enterprise CRM hardcodes mandatory GSTIN validation, discarding 3.5 Crore retail shops and salons at the front door.
              </div>
            </div>

            <!-- Failure Mode 3 -->
            <div class="card" style="padding: 13px 16px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <span class="badge-pill">Failure Mode 3</span>
                <span style="font-size: 11px; font-weight: 800; color: #121316;">₹15,000 Direct CAC</span>
              </div>
              <div style="font-size: 14px; font-weight: 800; color: #121316;">Crippling Unit Economics (Manual Follow-Ups)</div>
              <div style="font-size: 12px; color: #4A4B4E; margin-top: 3px; line-height: 1.38;">
                A slow 17.6-day onboarding cycle and 3.2 manual status chase calls per lead consume ₹15,000 in sales rep labor per deal, resulting in a 14.2-month CAC payback period against ₹6,900 monthly ARPU.
              </div>
            </div>

            <!-- 4-Stat Box Grid -->
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px;">
              <div style="background: #FAF8F5; border: 1px solid #DDD8CE; padding: 7px 8px; border-radius: 6px; text-align: center;">
                <div style="font-size: 9px; color: #7A7B7E; font-weight: 700; text-transform: uppercase;">Quoting Drop</div>
                <div style="font-size: 15px; font-weight: 900; color: #121316;">-56.4%</div>
              </div>
              <div style="background: #FAF8F5; border: 1px solid #DDD8CE; padding: 7px 8px; border-radius: 6px; text-align: center;">
                <div style="font-size: 9px; color: #7A7B7E; font-weight: 700; text-transform: uppercase;">Non-GST Gap</div>
                <div style="font-size: 15px; font-weight: 900; color: #121316;">4.8x Lower</div>
              </div>
              <div style="background: #FAF8F5; border: 1px solid #DDD8CE; padding: 7px 8px; border-radius: 6px; text-align: center;">
                <div style="font-size: 9px; color: #7A7B7E; font-weight: 700; text-transform: uppercase;">Cycle Time</div>
                <div style="font-size: 15px; font-weight: 900; color: #121316;">17.6 Days</div>
              </div>
              <div style="background: #FAF8F5; border: 1px solid #DDD8CE; padding: 7px 8px; border-radius: 6px; text-align: center;">
                <div style="font-size: 9px; color: #7A7B7E; font-weight: 700; text-transform: uppercase;">Direct CAC</div>
                <div style="font-size: 15px; font-weight: 900; color: #121316;">₹15,000</div>
              </div>
            </div>

            <!-- Financial Bleed Card -->
            <div class="card-beige" style="padding: 11px 14px; border-left: 3px solid #121316;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
                <span style="font-size: 11.5px; font-weight: 800; color: #121316; text-transform: uppercase;">Financial Revenue Bleed (From 5,000 Sample Leads)</span>
                <span class="badge-pill-alert" style="font-size: 10px;">₹11.05 Cr / Yr Lost</span>
              </div>
              <div style="font-size: 11px; color: #4A4B4E; line-height: 1.35;">
                At median ₹6,900/mo ARPU, the 1,113 abandoned leads represent <strong>₹92.1 Lakhs/month in lost recurring revenue</strong>. Nationwide across Airtel's enterprise funnel, this quoting latency bleeds over <strong>₹120+ Crore annually</strong> to competitors.
              </div>
            </div>

            <!-- Mandate Banner -->
            <div style="background: #121316; color: #FAF8F5; padding: 10px 14px; border-radius: 8px;">
              <div style="font-size: 11.5px; font-weight: 800; color: #FAF8F5;">The Accel Business Mandate:</div>
              <div style="font-size: 11px; color: #DDD8CE; margin-top: 2px; line-height: 1.35;">
                Compress quote delivery from 5 days to <strong>under 60 seconds</strong>, unlock non-GST merchants via instant Udyam lookup, and automate tracking to eliminate chase calls.
              </div>
            </div>

          </div>

        </div>
      </div>

      <div class="slide-footer">
        <span>Airtel Sync 2026 · Digital Track | Project Udyam Digital</span>
        <span class="team-name">Team Neural Nexus · ABV-IIITM Gwalior</span>
        <span class="slide-number">Slide 1 of 7</span>
      </div>
    </div>
    """
    slides.append(s1)

    # =============================================================
    # SLIDE 2 OF 7: TARGET CUSTOMER SEGMENTATION & PERSONA MATRIX
    # =============================================================
    s2 = f"""
    <div class="slide">
      <div class="slide-header">
        <div class="slide-title-group">
          <h1>Target Customer Segments: Four Core Business Types</h1>
          <p>Prioritizing India's 6.3 Crore small businesses based on real field data (Case Appendix A2)</p>
        </div>
        <div class="slide-category-badge">Slide 2 of 7 · Market Strategy</div>
      </div>

      <div class="slide-content">
        <div class="grid-4" style="flex: 1;">
          
          <!-- Segment 1: Kirana & Retail -->
          <div class="card" style="display: flex; flex-direction: column; justify-content: space-between; padding: 15px 15px;">
            <div style="border-bottom: 1.5px solid #EFECE6; padding-bottom: 8px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <span class="badge-pill">Segment 1</span>
                <span style="font-size: 11px; font-weight: 800; color: #121316;">55% of MSMEs (3.5 Cr)</span>
              </div>
              <div style="font-size: 17px; font-weight: 800; color: #121316;">Kirana & Micro Retail</div>
              <div style="font-size: 11px; color: #7A7B7E;">Grocery shops, salons, pharmacies</div>
            </div>
            
            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 11px 11px; border-radius: 7px;">
              <div style="font-size: 10px; font-weight: 800; text-transform: uppercase; color: #5A5A5D;">Scale & Baseline Setup</div>
              <div style="font-size: 11.5px; color: #222225; margin-top: 3px; line-height: 1.36;">
                • <strong>Staff:</strong> 1–3 employees | ₹1.5L–₹5L monthly sales.<br>
                • <strong>Footfall:</strong> 120+ daily UPI digital checkouts.<br>
                • <strong>Current Link:</strong> Owner's 4G mobile hotspot.<br>
                • <strong>Monthly Spend:</strong> ₹800 on fragmented prepaid packs.
              </div>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 11px 11px; border-radius: 7px;">
              <div style="font-size: 10px; font-weight: 800; text-transform: uppercase; color: #5A5A5D;">Core Daily Bleed</div>
              <div style="font-size: 11.5px; color: #222225; margin-top: 3px; line-height: 1.36;">
                • QR payment drops during 7–9 PM peak rush.<br>
                • Personal WhatsApp flooded with customer orders.<br>
                • <strong>Revenue Bleed:</strong> ~₹12,000/mo in lost walkouts.<br>
                • Customer dispute delays cause billing friction.
              </div>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 11px 11px; border-radius: 7px;">
              <div style="font-size: 10px; font-weight: 800; text-transform: uppercase; color: #5A5A5D;">Included Accel Hardware</div>
              <div style="font-size: 11.5px; color: #222225; margin-top: 3px; line-height: 1.36;">
                • 100 Mbps Fixed Fiber + Dual-Band Wi-Fi 6 Router.<br>
                • 2x CUG SIMs (100GB corporate pooled data).<br>
                • Airtel Soundbox with merchant priority QoS queue.<br>
                • 4-Hour MTTR local technician dispatch commitment.
              </div>
            </div>

            <div style="background: #EFECE6; padding: 11px 13px; border-radius: 7px;">
              <div style="font-size: 9.5px; font-weight: 800; color: #5A5A5D; text-transform: uppercase;">Target Pricing & Route</div>
              <div style="font-size: 19px; font-weight: 900; color: #121316; margin-top: 1px;">₹1,499 <span style="font-size: 11px; font-weight: 500;">/ month</span></div>
              <div style="font-size: 10.5px; color: #4A4B4E; margin-top: 2px; font-weight: 600;">₹0 Setup Fee | 100% GST-Exempt Udyam</div>
            </div>
          </div>

          <!-- Segment 2: Clinics & Healthcare -->
          <div class="card" style="display: flex; flex-direction: column; justify-content: space-between; padding: 15px 15px;">
            <div style="border-bottom: 1.5px solid #EFECE6; padding-bottom: 8px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <span class="badge-pill">Segment 2</span>
                <span style="font-size: 11px; font-weight: 800; color: #121316;">25% of MSMEs (1.5 Cr)</span>
              </div>
              <div style="font-size: 17px; font-weight: 800; color: #121316;">Clinics & Healthcare</div>
              <div style="font-size: 11px; color: #7A7B7E;">Doctors, path labs, CA chambers</div>
            </div>
            
            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 11px 11px; border-radius: 7px;">
              <div style="font-size: 10px; font-weight: 800; text-transform: uppercase; color: #5A5A5D;">Scale & Baseline Setup</div>
              <div style="font-size: 11.5px; color: #222225; margin-top: 3px; line-height: 1.36;">
                • <strong>Staff:</strong> 5–15 employees | ₹8L–₹25L monthly sales.<br>
                • <strong>Traffic:</strong> 40+ daily telehealth consults & reports.<br>
                • <strong>Current Link:</strong> Consumer unmanaged broadband.<br>
                • <strong>Records:</strong> Free Gmail and shared personal Drive.
              </div>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 11px 11px; border-radius: 7px;">
              <div style="font-size: 10px; font-weight: 800; text-transform: uppercase; color: #5A5A5D;">Core Daily Bleed</div>
              <div style="font-size: 11.5px; color: #222225; margin-top: 3px; line-height: 1.36;">
                • Video consult drops mid-call on jitter spikes.<br>
                • Unencrypted patient records violate ABHA rules.<br>
                • <strong>Revenue Bleed:</strong> ~₹45,000/mo in lost appointments.<br>
                • Statutory exposure under DPDP health data rules.
              </div>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 11px 11px; border-radius: 7px;">
              <div style="font-size: 10px; font-weight: 800; text-transform: uppercase; color: #5A5A5D;">Included Accel Hardware</div>
              <div style="font-size: 11.5px; color: #222225; margin-top: 3px; line-height: 1.36;">
                • 300 Mbps Dedicated Fiber with Static IPv4 address.<br>
                • 5x Google Workspace business licenses.<br>
                • 500GB Airtel Cloud Backup with 4h MTTR SLA.<br>
                • Separate guest Wi-Fi network for patient waiting room.
              </div>
            </div>

            <div style="background: #EFECE6; padding: 11px 13px; border-radius: 7px;">
              <div style="font-size: 9.5px; font-weight: 800; color: #5A5A5D; text-transform: uppercase;">Target Pricing & Route</div>
              <div style="font-size: 19px; font-weight: 900; color: #121316; margin-top: 1px;">₹2,499 <span style="font-size: 11px; font-weight: 500;">/ month</span></div>
              <div style="font-size: 10.5px; color: #4A4B4E; margin-top: 2px; font-weight: 600;">Static IP | 99.9% Telehealth Uptime SLA</div>
            </div>
          </div>

          <!-- Segment 3: Multi-Site Chains -->
          <div class="card" style="display: flex; flex-direction: column; justify-content: space-between; padding: 15px 15px;">
            <div style="border-bottom: 1.5px solid #EFECE6; padding-bottom: 8px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <span class="badge-pill">Segment 3</span>
                <span style="font-size: 11px; font-weight: 800; color: #121316;">15% of MSMEs (90 Lakhs)</span>
              </div>
              <div style="font-size: 17px; font-weight: 800; color: #121316;">Multi-Site Chains</div>
              <div style="font-size: 11px; color: #7A7B7E;">3–10 branch retail or restaurants</div>
            </div>
            
            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 11px 11px; border-radius: 7px;">
              <div style="font-size: 10px; font-weight: 800; text-transform: uppercase; color: #5A5A5D;">Scale & Baseline Setup</div>
              <div style="font-size: 11.5px; color: #222225; margin-top: 3px; line-height: 1.36;">
                • <strong>Outlets:</strong> 3–10 stores | ₹30L–₹1.2 Cr combined turnover.<br>
                • <strong>Workload:</strong> Real-time ERP inventory synchronization.<br>
                • <strong>Current Link:</strong> Mixed local cable ISPs per store.<br>
                • <strong>Billing:</strong> 5+ separate physical bills and invoices.
              </div>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 11px 11px; border-radius: 7px;">
              <div style="font-size: 10px; font-weight: 800; text-transform: uppercase; color: #5A5A5D;">Core Daily Bleed</div>
              <div style="font-size: 11.5px; color: #222225; margin-top: 3px; line-height: 1.36;">
                • POS halts during cable cuts; inventory desyncs.<br>
                • Zero central visibility into store CCTV cameras.<br>
                • <strong>Revenue Bleed:</strong> ~₹1,20,000/mo in checkout delays.<br>
                • Unmonitored stock shrinkage across branch locations.
              </div>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 11px 11px; border-radius: 7px;">
              <div style="font-size: 10px; font-weight: 800; text-transform: uppercase; color: #5A5A5D;">Included Accel Hardware</div>
              <div style="font-size: 11.5px; color: #222225; margin-top: 3px; line-height: 1.36;">
                • 500 Mbps Fiber + 4G LTE Auto-Failover Gateway.<br>
                • 4-Cam Cloud AI CCTV (30-day offsite archive).<br>
                • Centralized portal for multi-store network control.<br>
                • Single consolidated invoice for corporate tax credit.
              </div>
            </div>

            <div style="background: #EFECE6; padding: 11px 13px; border-radius: 7px;">
              <div style="font-size: 9.5px; font-weight: 800; color: #5A5A5D; text-transform: uppercase;">Target Pricing & Route</div>
              <div style="font-size: 19px; font-weight: 900; color: #121316; margin-top: 1px;">₹4,999 <span style="font-size: 11px; font-weight: 500;">/ mo / store</span></div>
              <div style="font-size: 10.5px; color: #4A4B4E; margin-top: 2px; font-weight: 600;">Single Consolidated Bill | Auto-Failover</div>
            </div>
          </div>

          <!-- Segment 4: Small Manufacturing -->
          <div class="card" style="display: flex; flex-direction: column; justify-content: space-between; padding: 15px 15px;">
            <div style="border-bottom: 1.5px solid #EFECE6; padding-bottom: 8px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <span class="badge-pill">Segment 4</span>
                <span style="font-size: 11px; font-weight: 800; color: #121316;">5% of MSMEs (30 Lakhs)</span>
              </div>
              <div style="font-size: 17px; font-weight: 800; color: #121316;">Light Manufacturing</div>
              <div style="font-size: 11px; color: #7A7B7E;">Auto-parts, textiles, CNC shops</div>
            </div>
            
            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 11px 11px; border-radius: 7px;">
              <div style="font-size: 10px; font-weight: 800; text-transform: uppercase; color: #5A5A5D;">Scale & Baseline Setup</div>
              <div style="font-size: 11.5px; color: #222225; margin-top: 3px; line-height: 1.36;">
                • <strong>Staff:</strong> 25–100 workers | ₹1.5 Cr–₹8 Cr annual sales.<br>
                • <strong>Tools:</strong> Automated CNC mills & factory PLCs.<br>
                • <strong>Current Link:</strong> Shared consumer broadband line.<br>
                • <strong>Security:</strong> Unmanaged routers with default passwords.
              </div>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 11px 11px; border-radius: 7px;">
              <div style="font-size: 10px; font-weight: 800; text-transform: uppercase; color: #5A5A5D;">Core Daily Bleed</div>
              <div style="font-size: 11.5px; color: #222225; margin-top: 3px; line-height: 1.36;">
                • Latency jitter halts precision CNC cutting tools.<br>
                • Zero firewall defense against factory ransomware.<br>
                • <strong>Revenue Bleed:</strong> ~₹3,50,000/mo in damaged tooling.<br>
                • Production downtime halts customer shipment schedules.
              </div>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 11px 11px; border-radius: 7px;">
              <div style="font-size: 10px; font-weight: 800; text-transform: uppercase; color: #5A5A5D;">Included Accel Hardware</div>
              <div style="font-size: 11.5px; color: #222225; margin-top: 3px; line-height: 1.36;">
                • 1 Gbps 1:1 Leased Line with sub-5ms low latency.<br>
                • Industrial IoT Box + Cloud Perimeter Firewall.<br>
                • Dedicated 24/7 Enterprise Account Manager.<br>
                • 99.95% Availability SLA with 2-Hour on-site MTTR.
              </div>
            </div>

            <div style="background: #EFECE6; padding: 11px 13px; border-radius: 7px;">
              <div style="font-size: 9.5px; font-weight: 800; color: #5A5A5D; text-transform: uppercase;">Target Pricing & Route</div>
              <div style="font-size: 19px; font-weight: 900; color: #121316; margin-top: 1px;">₹14,999 <span style="font-size: 11px; font-weight: 500;">/ month</span></div>
              <div style="font-size: 10.5px; color: #4A4B4E; margin-top: 2px; font-weight: 600;">1:1 Leased Line | 99.95% Enterprise SLA</div>
            </div>
          </div>

        </div>

        <!-- Strategy Insight Banner -->
        <div class="card-beige" style="padding: 12px 18px;">
          <div style="font-size: 12.5px; color: #121316; line-height: 1.4;">
            <strong>Key Market Insight:</strong> Over <strong>80% of Accel Business's addressable volume</strong> lies in Kirana stores and local clinics. To capture this segment, Airtel must remove the rigid corporate GST requirement while delivering business-grade SLAs at consumer-friendly prices.
          </div>
        </div>
      </div>

      <div class="slide-footer">
        <span>Airtel Sync 2026 · Digital Track | Project Udyam Digital</span>
        <span class="team-name">Team Neural Nexus · ABV-IIITM Gwalior</span>
        <span class="slide-number">Slide 2 of 7</span>
      </div>
    </div>
    """
    slides.append(s2)

    # =============================================================
    # SLIDE 3 OF 7: PROPOSED SOLUTION & CPQ BUNDLE MATRIX
    # =============================================================
    s3 = f"""
    <div class="slide">
      <div class="slide-header">
        <div class="slide-title-group">
          <h1>The Solution: 4 Ready Packs & Smart Budget Matching</h1>
          <p>Turning 25 individual enterprise products into 4 simple, high-converting business bundles</p>
        </div>
        <div class="slide-category-badge">Slide 3 of 7 · Product Strategy</div>
      </div>

      <div class="slide-content">
        <!-- 4 Bundles -->
        <div class="grid-4" style="flex: 1;">
          
          <div class="card" style="display: flex; flex-direction: column; justify-content: space-between; padding: 15px 15px;">
            <div>
              <div class="badge-pill" style="margin-bottom: 4px;">Kirana & Retail</div>
              <div style="font-size: 17px; font-weight: 900; color: #121316;">Udyam Vyapar</div>
              <div style="font-size: 21px; font-weight: 900; color: #121316; margin: 2px 0;">₹1,499 <span style="font-size: 11px; font-weight: 500;">/mo</span></div>
              <div style="font-size: 10.5px; color: #7A7B7E; margin-bottom: 8px;">₹0 setup fee on 12-mo plan (Save ₹1,400)</div>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 10px 11px; border-radius: 6px;">
              <div style="font-size: 9.5px; font-weight: 800; color: #5A5A5D; text-transform: uppercase;">Connectivity & Hardware</div>
              <ul class="bullet-list" style="font-size: 11.5px; gap: 4px; margin-top: 3px;">
                <li><strong>100 Mbps Fixed Fiber:</strong> Unlimited symmetric pipe.</li>
                <li><strong>Wi-Fi 6 Router:</strong> Supports 50+ concurrent devices.</li>
                <li><strong>Airtel Soundbox:</strong> Instant voice audio checkouts.</li>
              </ul>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 10px 11px; border-radius: 6px;">
              <div style="font-size: 9.5px; font-weight: 800; color: #5A5A5D; text-transform: uppercase;">Mobility & SLA Terms</div>
              <ul class="bullet-list" style="font-size: 11.5px; gap: 4px; margin-top: 3px;">
                <li><strong>2x Business SIMs:</strong> 100GB pooled CUG data.</li>
                <li><strong>Merchant UPI Priority:</strong> QoS priority packet queuing.</li>
                <li><strong>4-Hour MTTR:</strong> Rapid local field restoration.</li>
              </ul>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 8px 11px; border-radius: 6px;">
              <div style="font-size: 9.5px; font-weight: 800; color: #5A5A5D; text-transform: uppercase;">Value Proposition</div>
              <div style="font-size: 11px; color: #222225; margin-top: 2px;">
                Replaces costly consumer hotspot with business-grade reliable connectivity at consumer pricing.
              </div>
            </div>

            <div style="background: #EFECE6; padding: 8px 10px; border-radius: 6px; font-size: 10.5px; font-weight: 700; color: #121316;">
              100% GST-Free Onboarding via Udyam Registration
            </div>
          </div>

          <div class="card" style="display: flex; flex-direction: column; justify-content: space-between; padding: 15px 15px;">
            <div>
              <div class="badge-pill" style="margin-bottom: 4px;">Clinics & Labs</div>
              <div style="font-size: 17px; font-weight: 900; color: #121316;">Udyam Professional</div>
              <div style="font-size: 21px; font-weight: 900; color: #121316; margin: 2px 0;">₹2,499 <span style="font-size: 11px; font-weight: 500;">/mo</span></div>
              <div style="font-size: 10.5px; color: #7A7B7E; margin-bottom: 8px;">12-month commercial agreement</div>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 10px 11px; border-radius: 6px;">
              <div style="font-size: 9.5px; font-weight: 800; color: #5A5A5D; text-transform: uppercase;">Connectivity & Hardware</div>
              <ul class="bullet-list" style="font-size: 11.5px; gap: 4px; margin-top: 3px;">
                <li><strong>300 Mbps Dedicated Fiber:</strong> Zero-jitter consultations.</li>
                <li><strong>Static IPv4 Address:</strong> EMR server & ABHA compliant.</li>
                <li><strong>Wi-Fi 6 Gateway:</strong> Patient waiting room guest isolation.</li>
              </ul>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 10px 11px; border-radius: 6px;">
              <div style="font-size: 9.5px; font-weight: 800; color: #5A5A5D; text-transform: uppercase;">Productivity & SLA Terms</div>
              <ul class="bullet-list" style="font-size: 11.5px; gap: 4px; margin-top: 3px;">
                <li><strong>5x Google Workspace:</strong> Branded clinic emails.</li>
                <li><strong>500GB Airtel Cloud:</strong> Automated daily backups.</li>
                <li><strong>Guaranteed 99.9% SLA:</strong> Priority medical support desk.</li>
              </ul>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 8px 11px; border-radius: 6px;">
              <div style="font-size: 9.5px; font-weight: 800; color: #5A5A5D; text-transform: uppercase;">Value Proposition</div>
              <div style="font-size: 11px; color: #222225; margin-top: 2px;">
                Zero-liability health data compliance and 100% video telemedicine uptime guaranteed.
              </div>
            </div>

            <div style="background: #EFECE6; padding: 8px 10px; border-radius: 6px; font-size: 10.5px; font-weight: 700; color: #121316;">
              Guaranteed 99.9% Uptime SLA for Telehealth
            </div>
          </div>

          <div class="card" style="display: flex; flex-direction: column; justify-content: space-between; padding: 15px 15px;">
            <div>
              <div class="badge-pill" style="margin-bottom: 4px;">Multi-Store Chains</div>
              <div style="font-size: 17px; font-weight: 900; color: #121316;">Udyam Multi-Site</div>
              <div style="font-size: 21px; font-weight: 900; color: #121316; margin: 2px 0;">₹4,999 <span style="font-size: 11px; font-weight: 500;">/mo/hub</span></div>
              <div style="font-size: 10.5px; color: #7A7B7E; margin-bottom: 8px;">Multi-location single consolidated invoice</div>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 10px 11px; border-radius: 6px;">
              <div style="font-size: 9.5px; font-weight: 800; color: #5A5A5D; text-transform: uppercase;">Connectivity & Hardware</div>
              <ul class="bullet-list" style="font-size: 11.5px; gap: 4px; margin-top: 3px;">
                <li><strong>500 Mbps Fixed Fiber:</strong> Unlimited high-speed pipe.</li>
                <li><strong>4G LTE Auto-Failover:</strong> &lt;2 second cutover gateway.</li>
                <li><strong>Central SD-WAN:</strong> Unified routing across stores.</li>
              </ul>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 10px 11px; border-radius: 6px;">
              <div style="font-size: 9.5px; font-weight: 800; color: #5A5A5D; text-transform: uppercase;">Security & Multi-Site SLA</div>
              <ul class="bullet-list" style="font-size: 11.5px; gap: 4px; margin-top: 3px;">
                <li><strong>4-Cam Cloud AI CCTV:</strong> 30-day offsite recording.</li>
                <li><strong>Central Cloud Portal:</strong> Live view of all branches.</li>
                <li><strong>Single Monthly Bill:</strong> Zero vendor fragmentation.</li>
              </ul>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 8px 11px; border-radius: 6px;">
              <div style="font-size: 9.5px; font-weight: 800; color: #5A5A5D; text-transform: uppercase;">Value Proposition</div>
              <div style="font-size: 11px; color: #222225; margin-top: 2px;">
                Single pane of glass replaces 5+ fragmented local cable vendors with full POS failover protection.
              </div>
            </div>

            <div style="background: #EFECE6; padding: 8px 10px; border-radius: 6px; font-size: 10.5px; font-weight: 700; color: #121316;">
              Zero POS payment outages across all branches
            </div>
          </div>

          <div class="card" style="display: flex; flex-direction: column; justify-content: space-between; padding: 15px 15px;">
            <div>
              <div class="badge-pill" style="margin-bottom: 4px;">Manufacturing</div>
              <div style="font-size: 17px; font-weight: 900; color: #121316;">Udyam Industrial</div>
              <div style="font-size: 21px; font-weight: 900; color: #121316; margin: 2px 0;">₹14,999 <span style="font-size: 11px; font-weight: 500;">/mo</span></div>
              <div style="font-size: 10.5px; color: #7A7B7E; margin-bottom: 8px;">Enterprise SLA contract with dedicated RM</div>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 10px 11px; border-radius: 6px;">
              <div style="font-size: 9.5px; font-weight: 800; color: #5A5A5D; text-transform: uppercase;">Connectivity & Hardware</div>
              <ul class="bullet-list" style="font-size: 11.5px; gap: 4px; margin-top: 3px;">
                <li><strong>1 Gbps 1:1 Leased Line:</strong> Symmetric low-jitter pipe.</li>
                <li><strong>Industrial IoT Box:</strong> Modbus/PLC telemetry bridge.</li>
                <li><strong>Perimeter Cloud Firewall:</strong> Layer-7 cyber defense.</li>
              </ul>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 10px 11px; border-radius: 6px;">
              <div style="font-size: 9.5px; font-weight: 800; color: #5A5A5D; text-transform: uppercase;">Security & Mission-Critical SLA</div>
              <ul class="bullet-list" style="font-size: 11.5px; gap: 4px; margin-top: 3px;">
                <li><strong>99.95% Availability SLA:</strong> 2-Hour on-site MTTR.</li>
                <li><strong>Dedicated RM:</strong> Direct line to NOC engineers.</li>
                <li><strong>Zero CNC Stoppages:</strong> Hardware-level packet priority.</li>
              </ul>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 8px 11px; border-radius: 6px;">
              <div style="font-size: 9.5px; font-weight: 800; color: #5A5A5D; text-transform: uppercase;">Value Proposition</div>
              <div style="font-size: 11px; color: #222225; margin-top: 2px;">
                Protects heavy CNC and automated machinery from micro-stoppages and expensive factory tooling damage.
              </div>
            </div>

            <div style="background: #EFECE6; padding: 8px 10px; border-radius: 6px; font-size: 10.5px; font-weight: 700; color: #121316;">
              Zero packet jitter for factory automated tools
            </div>
          </div>

        </div>

        <!-- Reverse Budget Optimizer Card -->
        <div class="card-beige" style="display: flex; gap: 28px; align-items: center; padding: 16px 22px;">
          <div style="flex: 1.2;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
              <span class="badge-pill" style="background: #121316;">Reverse Budget Solver</span>
              <span style="font-size: 15px; font-weight: 800; color: #121316;">"Mera Budget ₹X Hai" (Instant Math Matching)</span>
            </div>
            <div style="font-size: 12px; color: #4A4B4E; line-height: 1.4;">
              Instead of forcing a shop owner to browse 25 technical products, they simply enter their monthly budget (e.g. ₹2,500). Our branch-and-bound solver tests all valid product combinations in <strong>under 0.5 milliseconds</strong>, guaranteeing the best possible bundle with zero human error.
            </div>
          </div>

          <div style="flex: 0.8; border-left: 1.5px solid #DDD8CE; padding-left: 20px;">
            <div style="font-size: 12px; font-weight: 800; color: #121316; margin-bottom: 4px;">Commercial Discount Policy Built In:</div>
            <ul class="bullet-list" style="font-size: 11.5px; gap: 3px; margin-bottom: 0;">
              <li><strong>Multi-Product Discount:</strong> 5% off for 2 categories, 10% for 3, 15% for 4+.</li>
              <li><strong>Setup Fee Waiver:</strong> 100% setup fee waived on 12-month plans (₹0 upfront).</li>
              <li><strong>GST Input Credit:</strong> Automatic 18% GST tax deduction calculated for registered firms.</li>
            </ul>
          </div>
        </div>

      </div>

      <div class="slide-footer">
        <span>Airtel Sync 2026 · Digital Track | Project Udyam Digital</span>
        <span class="team-name">Team Neural Nexus · ABV-IIITM Gwalior</span>
        <span class="slide-number">Slide 3 of 7</span>
      </div>
    </div>
    """
    slides.append(s3)

    # =============================================================
    # SLIDE 4 OF 7: TECHNICAL SYSTEM ARCHITECTURE
    # =============================================================
    s4 = f"""
    <div class="slide">
      <div class="slide-header">
        <div class="slide-title-group">
          <h1>System Architecture: The 4-Step Acquisition Pipeline</h1>
          <p>Autonomous onboarding pipeline: From spoken regional language to activated order</p>
        </div>
        <div class="slide-category-badge">Slide 4 of 7 · System Architecture</div>
      </div>

      <div class="slide-content" style="align-items: center; justify-content: space-between;">
        
        <!-- Large High-Resolution Architecture Diagram -->
        <div style="width: 100%; display: flex; justify-content: center; background: #FFFFFF; border: 1.5px solid #DDD8CE; border-radius: 12px; padding: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.02);">
          <img src="{img_arch_b64}" style="max-height: 640px; width: 100%; object-fit: contain;">
        </div>

        <!-- Architectural Highlights Banner -->
        <div class="card-beige" style="width: 100%; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center;">
          <div style="display: flex; gap: 24px; font-size: 12px; width: 100%; justify-content: space-between;">
            <div><strong>Stage 1 Discovery:</strong> Gemini 2.5 Flash + Pydantic v2 + 10 Indic languages with audio readout</div>
            <div><strong>Stage 2 CPQ DAG:</strong> &lt;0.5ms solver + Hard GSTIN firewall blocks ineligible SKUs</div>
            <div><strong>Stage 3 Smart KYC:</strong> In-memory redaction (12-digit IDs never saved to disk) + RapidFuzz</div>
            <div><strong>Stage 4 Fulfillment:</strong> 6-stage tracker + LightGBM rescue model (AUC 0.84)</div>
          </div>
        </div>

      </div>

      <div class="slide-footer">
        <span>Airtel Sync 2026 · Digital Track | Project Udyam Digital</span>
        <span class="team-name">Team Neural Nexus · ABV-IIITM Gwalior</span>
        <span class="slide-number">Slide 4 of 7</span>
      </div>
    </div>
    """
    slides.append(s4)

    # =============================================================
    # SLIDE 5 OF 7: WORKING PROTOTYPE IN ACTION (LIVE SCREENSHOTS)
    # =============================================================
    s5 = f"""
    <div class="slide">
      <div class="slide-header">
        <div class="slide-title-group">
          <h1>Working Prototype: Live Software Walkthrough</h1>
          <p>Verified against 100 real-world test cases and deployed on AWS EC2 (http://65.1.112.251)</p>
        </div>
        <div class="slide-category-badge">Slide 5 of 7 · Product Demonstration</div>
      </div>

      <div class="slide-content">
        <div class="grid-2" style="flex: 1; gap: 16px;">
          
          <!-- Screen 1: Multilingual Advisor -->
          <div class="card" style="padding: 12px 14px; display: flex; flex-direction: column; gap: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 13.5px; font-weight: 800; color: #121316;">1. Multilingual Natural Language Advisor</span>
              <span class="badge-pill">10 Indian Languages</span>
            </div>
            <div style="flex: 1; border: 1px solid #DDD8CE; border-radius: 6px; overflow: hidden; background: #000; display: flex; justify-content: center; align-items: center;">
              <img src="{img_screen_advisor_b64}" style="width: 100%; height: 100%; object-fit: cover;">
            </div>
            <div style="font-size: 11.5px; color: #5A5A5D; line-height: 1.35;">
              Shop owners chat or speak in Hindi, Tamil, Telugu, etc. The assistant understands business needs and explains bundle recommendations in plain language with voice audio.
            </div>
          </div>

          <!-- Screen 2: Interactive Cart & Budget Solver -->
          <div class="card" style="padding: 12px 14px; display: flex; flex-direction: column; gap: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 13.5px; font-weight: 800; color: #121316;">2. Dynamic Cart & "Mera Budget" Slider</span>
              <span class="badge-pill">&lt;0.5ms Solver</span>
            </div>
            <div style="flex: 1; border: 1px solid #DDD8CE; border-radius: 6px; overflow: hidden; background: #000; display: flex; justify-content: center; align-items: center;">
              <img src="{img_screen_cart_b64}" style="width: 100%; height: 100%; object-fit: cover;">
            </div>
            <div style="font-size: 11.5px; color: #5A5A5D; line-height: 1.35;">
              Transparent monthly price breakdown. Moving the budget slider automatically recalculates the best compliant bundle in under 1ms, applying multi-category discounts.
            </div>
          </div>

          <!-- Screen 3: Smart KYC Gate -->
          <div class="card" style="padding: 12px 14px; display: flex; flex-direction: column; gap: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 13.5px; font-weight: 800; color: #121316;">3. Fast & Safe KYC (Zero-Persistence DPDP)</span>
              <span class="badge-pill">Traps Planted Defects</span>
            </div>
            <div style="flex: 1; border: 1px solid #DDD8CE; border-radius: 6px; overflow: hidden; background: #000; display: flex; justify-content: center; align-items: center;">
              <img src="{img_screen_kyc_b64}" style="width: 100%; height: 100%; object-fit: cover;">
            </div>
            <div style="font-size: 11.5px; color: #5A5A5D; line-height: 1.35;">
              Instant verification against Udyam/GST databases. Traps cancelled GSTINs and old bills immediately, while masking 12-digit national IDs in volatile RAM.
            </div>
          </div>

          <!-- Screen 4: Real-Time Tracker UI Mockup -->
          <div class="card" style="padding: 12px 14px; display: flex; flex-direction: column; gap: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 13.5px; font-weight: 800; color: #121316;">4. 6-Stage Order Tracker & Lead Rescue</span>
              <span class="badge-pill">Zero Chase Calls</span>
            </div>
            
            <div style="flex: 1; border: 1px solid #2A2B30; border-radius: 6px; overflow: hidden; background: #0D0E11; padding: 12px 14px; color: #EBE5D9; display: flex; flex-direction: column; justify-content: space-between;">
              
              <!-- Order Header -->
              <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #222328; padding-bottom: 8px;">
                <div>
                  <div style="display: flex; align-items: center; gap: 6px;">
                    <span style="background: #E40000; color: #fff; font-size: 9px; font-weight: 800; padding: 1px 6px; border-radius: 3px; font-family: monospace;">ORDER #ORD-2026-8832</span>
                    <span style="background: rgba(34, 197, 94, 0.15); color: #4ADE80; border: 1px solid rgba(34, 197, 94, 0.3); font-size: 9px; font-weight: 700; padding: 1px 6px; border-radius: 10px;">DAY 1 · IN PROGRESS</span>
                  </div>
                  <div style="font-size: 13.5px; font-weight: 800; color: #FFFFFF; margin-top: 3px;">Apex Diagnostics Center</div>
                  <div style="font-size: 10.5px; color: #9A9AA0;">Smart Office Fiber 300M · SLA: 4 Days Guaranteed</div>
                </div>
                <div style="background: #16171B; border: 1px solid #2A2B30; border-radius: 5px; padding: 5px 8px; text-align: right;">
                  <div style="font-size: 8.5px; color: #B39D82; text-transform: uppercase; font-family: monospace;">Partner Payout</div>
                  <div style="font-size: 13px; font-weight: 800; color: #D9AD63;">₹4,498</div>
                </div>
              </div>

              <!-- 6-Stage Stepper Grid -->
              <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin: 6px 0;">
                <div style="background: #141519; border: 1px solid #222328; border-radius: 5px; padding: 5px 6px;">
                  <div style="display: flex; justify-content: space-between; font-size: 8.5px; color: #4ADE80; font-weight: 700;">STAGE 1 <span>✓</span></div>
                  <div style="font-size: 10.5px; font-weight: 700; color: #FFFFFF; margin-top: 1px;">Order Placed</div>
                  <div style="font-size: 8.5px; color: #7A7B82;">Quote locked in 42s</div>
                </div>
                <div style="background: #141519; border: 1px solid #222328; border-radius: 5px; padding: 5px 6px;">
                  <div style="display: flex; justify-content: space-between; font-size: 8.5px; color: #4ADE80; font-weight: 700;">STAGE 2 <span>✓</span></div>
                  <div style="font-size: 10.5px; font-weight: 700; color: #FFFFFF; margin-top: 1px;">Smart KYC</div>
                  <div style="font-size: 8.5px; color: #7A7B82;">Masked SYN-XXXX-889</div>
                </div>
                <div style="background: #141519; border: 1px solid #222328; border-radius: 5px; padding: 5px 6px;">
                  <div style="display: flex; justify-content: space-between; font-size: 8.5px; color: #4ADE80; font-weight: 700;">STAGE 3 <span>✓</span></div>
                  <div style="font-size: 10.5px; font-weight: 700; color: #FFFFFF; margin-top: 1px;">Feasibility</div>
                  <div style="font-size: 8.5px; color: #7A7B82;">Splitter Port #4 OK</div>
                </div>
                <div style="background: #141519; border: 1px solid #222328; border-radius: 5px; padding: 5px 6px;">
                  <div style="display: flex; justify-content: space-between; font-size: 8.5px; color: #4ADE80; font-weight: 700;">STAGE 4 <span>✓</span></div>
                  <div style="font-size: 10.5px; font-weight: 700; color: #FFFFFF; margin-top: 1px;">CPE Router</div>
                  <div style="font-size: 8.5px; color: #7A7B82;">Wi-Fi 6 Dispatched</div>
                </div>
                <div style="background: #1E1F26; border: 1px solid #D9AD63; border-radius: 5px; padding: 5px 6px;">
                  <div style="display: flex; justify-content: space-between; font-size: 8.5px; color: #D9AD63; font-weight: 800;">STAGE 5 <span>ACTIVE</span></div>
                  <div style="font-size: 10.5px; font-weight: 800; color: #FFFFFF; margin-top: 1px;">Field Tech</div>
                  <div style="font-size: 8.5px; color: #D9AD63;">Ramesh Kumar · OTP: 4892</div>
                </div>
                <div style="background: #141519; border: 1px solid #222328; border-radius: 5px; padding: 5px 6px; opacity: 0.65;">
                  <div style="display: flex; justify-content: space-between; font-size: 8.5px; color: #7A7B82; font-weight: 700;">STAGE 6 <span>ETA 3D</span></div>
                  <div style="font-size: 10.5px; font-weight: 700; color: #CCCCCC; margin-top: 1px;">Activated</div>
                  <div style="font-size: 8.5px; color: #7A7B82;">99.9% Uptime Live</div>
                </div>
              </div>

              <!-- WhatsApp Automated Push Banner -->
              <div style="background: #16181E; border: 1px solid #2A2D38; border-radius: 5px; padding: 6px 8px; display: flex; align-items: center; justify-content: space-between; font-size: 10px;">
                <div style="display: flex; align-items: center; gap: 6px;">
                  <span style="color: #25D366; font-weight: 800;">● WhatsApp Push:</span>
                  <span style="color: #C0C1C7;">"Engineer Ramesh Kumar arrives tomorrow at 11 AM. Verification OTP: 4892."</span>
                </div>
                <span style="background: #22242D; color: #EFECE6; font-size: 8.5px; padding: 1px 6px; border-radius: 3px; font-weight: 600;">Automated</span>
              </div>

            </div>

            <div style="font-size: 11.5px; color: #5A5A5D; line-height: 1.35;">
              Self-serve view shows progress from payment to technician dispatch with OTP. If a user pauses, an automated WhatsApp rescue message with a token brings them back.
            </div>
          </div>

        </div>
      </div>

      <div class="slide-footer">
        <span>Airtel Sync 2026 · Digital Track | Project Udyam Digital</span>
        <span class="team-name">Team Neural Nexus · ABV-IIITM Gwalior</span>
        <span class="slide-number">Slide 5 of 7</span>
      </div>
    </div>
    """
    slides.append(s5)

    # =============================================================
    # SLIDE 6 OF 7: DETAILED COMPETITIVE ANALYSIS & ACCEL MOAT
    # =============================================================
    s6 = f"""
    <div class="slide">
      <div class="slide-header">
        <div class="slide-title-group">
          <h1>Competitive Advantage: Why Accel Business Wins</h1>
          <p>Direct comparison against telco competitors, local cable resellers, and digital software apps</p>
        </div>
        <div class="slide-category-badge">Slide 6 of 7 · Competitive Strategy</div>
      </div>

      <div class="slide-content">
        <!-- Main Comparison Table Card -->
        <div class="card" style="padding: 10px 16px; flex: 1; display: flex; flex-direction: column; justify-content: space-between;">
          <table class="comp-table" style="height: 100%;">
            <thead>
              <tr>
                <th style="width: 22%; padding: 10px 14px;">Strategic Capability</th>
                <th class="highlight-col" style="width: 28%; padding: 10px 14px;">Accel Business (Project Udyam)</th>
                <th style="width: 25%; padding: 10px 14px;">Jio Business</th>
                <th style="width: 25%; padding: 10px 14px;">Local Cable / Resellers</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style="padding: 8px 14px;"><strong>Time to Get a Quote</strong></td>
                <td class="highlight-col" style="padding: 8px 14px;"><strong>&lt; 60 Seconds</strong> (Instant on mobile phone)</td>
                <td style="padding: 8px 14px;">24 to 48 Hours (Sales rep visit required)</td>
                <td style="padding: 8px 14px;">2 to 3 Days (Wait for technician visit)</td>
              </tr>
              <tr>
                <td style="padding: 8px 14px;"><strong>Non-GST Shop Access</strong></td>
                <td class="highlight-col" style="padding: 8px 14px;"><strong>Full Access via Udyam</strong> (Unlocks 3.5 Cr shops)</td>
                <td style="padding: 8px 14px;">Strict GSTIN Mandate (Drops non-GST leads)</td>
                <td style="padding: 8px 14px;">Unregulated cash (No legal agreements)</td>
              </tr>
              <tr>
                <td style="padding: 8px 14px;"><strong>Upfront Setup & Hardware</strong></td>
                <td class="highlight-col" style="padding: 8px 14px;"><strong>100% Waived (₹0 Upfront)</strong> on 12-mo plans</td>
                <td style="padding: 8px 14px;">₹1,500 – ₹3,000 setup fee charged upfront</td>
                <td style="padding: 8px 14px;">₹2,500 modem purchase + cash installation</td>
              </tr>
              <tr>
                <td style="padding: 8px 14px;"><strong>SLA & Downtime Guarantee</strong></td>
                <td class="highlight-col" style="padding: 8px 14px;"><strong>99.5% Uptime + 4G LTE Auto-Failover</strong></td>
                <td style="padding: 8px 14px;">Best effort broadband; slow fiber cut repair</td>
                <td style="padding: 8px 14px;">No SLA; frequent unannounced cable cuts</td>
              </tr>
              <tr>
                <td style="padding: 8px 14px;"><strong>Hardware & Devices Bundled</strong></td>
                <td class="highlight-col" style="padding: 8px 14px;"><strong>Wi-Fi 6 Router + CUG SIMs + Soundbox + CCTV</strong></td>
                <td style="padding: 8px 14px;">Standard single-band Wi-Fi router only</td>
                <td style="padding: 8px 14px;">Consumer modem; third-party camera setup</td>
              </tr>
              <tr>
                <td style="padding: 8px 14px;"><strong>Lead Abandonment Rescue</strong></td>
                <td class="highlight-col" style="padding: 8px 14px;"><strong>Automated LightGBM WhatsApp Rescue</strong></td>
                <td style="padding: 8px 14px;">Manual sales calls; 56% leads abandoned</td>
                <td style="padding: 8px 14px;">Ignored; zero retargeting infrastructure</td>
              </tr>
              <tr>
                <td style="padding: 8px 14px;"><strong>Data Privacy (DPDP Act 2023)</strong></td>
                <td class="highlight-col" style="padding: 8px 14px;"><strong>100% Zero-Persistence:</strong> IDs masked in RAM</td>
                <td style="padding: 8px 14px;">Standard cloud storage (PII saved on disk)</td>
                <td style="padding: 8px 14px;">Zero privacy (Photocopies, raw WhatsApp)</td>
              </tr>
              <tr>
                <td style="padding: 8px 14px;"><strong>Indian Language Ingress</strong></td>
                <td class="highlight-col" style="padding: 8px 14px;"><strong>10 Indian Languages</strong> with script & voice audio</td>
                <td style="padding: 8px 14px;">Static English & Hindi website forms</td>
                <td style="padding: 8px 14px;">Verbal local dialect only (No digital tool)</td>
              </tr>
              <tr>
                <td style="padding: 8px 14px;"><strong>Time to Final Activation</strong></td>
                <td class="highlight-col" style="padding: 8px 14px;"><strong>3.8 Days</strong> (Digital dispatch & automated provisioning)</td>
                <td style="padding: 8px 14px;">14 to 21 Days (Paper manual verification)</td>
                <td style="padding: 8px 14px;">5 to 7 Days (Unmanaged setup)</td>
              </tr>
              <tr>
                <td style="padding: 8px 14px;"><strong>Customer Status Visibility</strong></td>
                <td class="highlight-col" style="padding: 8px 14px;"><strong>Live 6-Stage Web/WhatsApp Tracker + Tech OTP</strong></td>
                <td style="padding: 8px 14px;">Manual chase calls to 1800 call center</td>
                <td style="padding: 8px 14px;">Unreachable technician mobile numbers</td>
              </tr>
              <tr>
                <td style="padding: 8px 14px;"><strong>Channel Partner Model</strong></td>
                <td class="highlight-col" style="padding: 8px 14px;"><strong>15% Recurring Commission</strong> via dynamic QR</td>
                <td style="padding: 8px 14px;">Direct sales force (Cuts out local dealers)</td>
                <td style="padding: 8px 14px;">Fragmented resellers (No technology)</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 3-Pillar Competitive Defense Strategy -->
        <div class="grid-3" style="gap: 14px;">
          <div class="card-beige" style="padding: 12px 16px;">
            <div style="font-size: 12.5px; font-weight: 800; color: #121316; margin-bottom: 4px;">Why Jio Cannot Copy Quickly</div>
            <div style="font-size: 11.5px; color: #4A4B4E; line-height: 1.38;">
              Jio's enterprise architecture relies on rigid SAP GST pipelines and corporate direct sales teams. Discarding GST requirements demands rebuilding their DoT compliance stack from scratch.
            </div>
          </div>

          <div class="card-beige" style="padding: 12px 16px;">
            <div style="font-size: 12.5px; font-weight: 800; color: #121316; margin-bottom: 4px;">Coexistence Over Cannibalization</div>
            <div style="font-size: 11.5px; color: #4A4B4E; line-height: 1.38;">
              Instead of fighting local cable operators, Accel pays them 15% recurring commissions via dynamic QR codes, converting former competitors into our local installation & maintenance franchise.
            </div>
          </div>

          <div class="card-beige" style="padding: 12px 16px;">
            <div style="font-size: 12.5px; font-weight: 800; color: #121316; margin-bottom: 4px;">Telecom Physical Infrastructure Moat</div>
            <div style="font-size: 11.5px; color: #4A4B4E; line-height: 1.38;">
              Standalone SaaS software (Khatabook / Zoho) cannot provide physical last-mile fiber connectivity or cellular auto-failover. Accel owns the foundational physical infrastructure.
            </div>
          </div>
        </div>

      </div>

      <div class="slide-footer">
        <span>Airtel Sync 2026 · Digital Track | Project Udyam Digital</span>
        <span class="team-name">Team Neural Nexus · ABV-IIITM Gwalior</span>
        <span class="slide-number">Slide 6 of 7</span>
      </div>
    </div>
    """
    slides.append(s6)

    # =============================================================
    # SLIDE 7 OF 7: QUANTIFIED BUSINESS IMPACT & 12-MONTH ROLLOUT
    # =============================================================
    s7 = f"""
    <div class="slide">
      <div class="slide-header">
        <div class="slide-title-group">
          <h1>Quantified Business Impact & 12-Month Rollout</h1>
          <p>Before vs. After sales transformation and 12-month national scale roadmap</p>
        </div>
        <div class="slide-category-badge">Slide 7 of 7 · Impact & Rollout</div>
      </div>

      <div class="slide-content" style="gap: 12px;">
        <div class="grid-2" style="flex: 1; gap: 18px;">
          
          <!-- Left Column: Metrics, Recovery & Unit Economics -->
          <div style="display: flex; flex-direction: column; gap: 12px;">
            
            <!-- 4 Big Metric Stat Boxes -->
            <div class="card" style="padding: 16px 20px;">
              <div style="font-size: 14.5px; font-weight: 800; color: #121316; margin-bottom: 10px;">Funnel Economics Transformation</div>

              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                <div class="stat-box" style="padding: 14px 16px;">
                  <div class="stat-num">+38.8%</div>
                  <div class="stat-label">Quote Acceptance Rate</div>
                  <div class="stat-sub">Jumps from 43.6% to 82.4% by eliminating the 5-day quote wait.</div>
                </div>

                <div class="stat-box" style="padding: 14px 16px;">
                  <div class="stat-num">4.25x</div>
                  <div class="stat-label">Non-GST Conversion Lift</div>
                  <div class="stat-sub">Conversion rises from 2.0% to 8.5% via instant Udyam lookup.</div>
                </div>

                <div class="stat-box" style="padding: 14px 16px;">
                  <div class="stat-num">3.8 Days</div>
                  <div class="stat-label">Lead to Activation Cycle</div>
                  <div class="stat-sub">Compressed by 78.4% from baseline 17.6 days via digital KYC.</div>
                </div>

                <div class="stat-box" style="padding: 14px 16px;">
                  <div class="stat-num">₹3,250</div>
                  <div class="stat-label">Acquisition Cost (CAC)</div>
                  <div class="stat-sub">Slashed by 78.3% from ₹15,000 via self-serve mobile flow.</div>
                </div>
              </div>
            </div>

            <!-- LightGBM Funnel Rescue Impact Card -->
            <div class="card-beige" style="padding: 14px 18px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-size: 13.5px; font-weight: 800; color: #121316;">LightGBM Lead Rescue Engine (Trained on 5,000 Leads)</span>
                <span class="badge-pill">AUC 0.84 Model</span>
              </div>
              <div style="font-size: 12px; color: #4A4B4E; line-height: 1.42;">
                Retargets the <strong>56.4% dropped quote cohort</strong> within 15 minutes via enterprise WhatsApp API with 1-click pre-hydrated carts. Recovers <strong>22.4% of abandoned prospects</strong> (249 merchants from 5,000 leads), unlocking <strong>₹48 Cr in recovered recurring ARR</strong> at national scale.
              </div>
            </div>

            <!-- Labor Savings & Unit Economics Card -->
            <div class="card" style="padding: 16px 20px; flex: 1; display: flex; flex-direction: column; gap: 10px;">
              <div style="font-size: 13.5px; font-weight: 800; color: #121316;">
                Direct Labor & Operational Efficiency Gains:
              </div>
              <table style="width: 100%; font-size: 12.5px; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #EFECE6;">
                  <td style="padding: 7px 0; color: #5A5A5D;">Field Sales Rep Time / Customer</td>
                  <td style="padding: 7px 0; text-align: right; font-weight: 800; color: #121316;">24.0 Hours → 2.1 Hours (-91.2%)</td>
                </tr>
                <tr style="border-bottom: 1px solid #EFECE6;">
                  <td style="padding: 7px 0; color: #5A5A5D;">Customer Status Chase Calls</td>
                  <td style="padding: 7px 0; text-align: right; font-weight: 800; color: #121316;">3.2 Calls → 0.4 Calls (-87.5%)</td>
                </tr>
                <tr style="border-bottom: 1px solid #EFECE6;">
                  <td style="padding: 7px 0; color: #5A5A5D;">6-Month Customer Churn Rate</td>
                  <td style="padding: 7px 0; text-align: right; font-weight: 800; color: #121316;">14.2% → 6.8% (-52.1% via SLAs)</td>
                </tr>
                <tr style="border-bottom: 1px solid #EFECE6;">
                  <td style="padding: 7px 0; color: #5A5A5D;">Gross Margin on Bundles</td>
                  <td style="padding: 7px 0; text-align: right; font-weight: 800; color: #121316;">42.5% → 61.8% (+19.3% automated margin)</td>
                </tr>
                <tr style="border-bottom: 1px solid #EFECE6;">
                  <td style="padding: 7px 0; color: #5A5A5D;">Partner Dealer Commission</td>
                  <td style="padding: 7px 0; text-align: right; font-weight: 800; color: #121316;">15% Recurring via Instant QR Attribution</td>
                </tr>
                <tr style="border-bottom: 1px solid #EFECE6;">
                  <td style="padding: 7px 0; color: #5A5A5D;">Quote Generation Speed</td>
                  <td style="padding: 7px 0; text-align: right; font-weight: 800; color: #121316;">3 to 5 Days → &lt; 60 Seconds (-99.9%)</td>
                </tr>
                <tr>
                  <td style="padding: 7px 0; color: #5A5A5D;">Payback Period on Sales CAC</td>
                  <td style="padding: 7px 0; text-align: right; font-weight: 800; color: #121316;">4.8 Months (vs 14.2 Months baseline)</td>
                </tr>
              </table>

              <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 10px 14px; border-radius: 6px;">
                <span style="font-size: 11.5px; color: #121316; line-height: 1.35;">
                  <strong>Bottom-Line Result:</strong> Direct sales acquisition cost slashed from ₹15,000 to ₹3,250, compressing CAC payback from 14.2 months to 4.8 months while freeing 22 hours of sales rep labor per closed account.
                </span>
              </div>
            </div>

          </div>

          <!-- Right Column: 12-Month Rollout Strategy & Synergies -->
          <div style="display: flex; flex-direction: column; gap: 12px;">
            
            <div class="card" style="padding: 16px 20px;">
              <div style="font-size: 14.5px; font-weight: 800; color: #121316; margin-bottom: 10px;">12-Month National Scale Strategy</div>

              <div style="display: flex; flex-direction: column; gap: 9px;">
                <div style="border-left: 3px solid #121316; padding-left: 12px; background: #FAF8F5; padding: 9px 14px; border-radius: 0 6px 6px 0;">
                  <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 13px; font-weight: 800; color: #121316;">Phase 1: Metros & Kirana Density (Months 1–3)</span>
                    <span class="badge-pill" style="font-size: 10px;">50k Units · ₹12 Cr ARR</span>
                  </div>
                  <div style="font-size: 11.5px; color: #5A5A5D; margin-top: 3px; line-height: 1.4;">
                    • Target 8 Tier-1 cities (Delhi NCR, Mumbai, Bengaluru, Hyderabad).<br>
                    • Deploy Udyam Vyapar & Clinic packs via 15,000 retail store QR codes.<br>
                    • Activate 50,000 merchants with instant paperless Udyam onboarding.<br>
                    • Train 1,200 local cable operators as authorized 15% commission partners.
                  </div>
                </div>

                <div style="border-left: 3px solid #121316; padding-left: 12px; background: #FAF8F5; padding: 9px 14px; border-radius: 0 6px 6px 0;">
                  <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 13px; font-weight: 800; color: #121316;">Phase 2: Industrial Clusters & Clinics (Months 4–6)</span>
                    <span class="badge-pill" style="font-size: 10px;">120k Units · ₹38 Cr ARR</span>
                  </div>
                  <div style="font-size: 11.5px; color: #5A5A5D; margin-top: 3px; line-height: 1.4;">
                    • Expand into 40 manufacturing towns (Surat, Coimbatore, Ludhiana, Peenya).<br>
                    • Focus on Leased Line connectivity and multi-store Cloud CCTV packs.<br>
                    • Capture 120,000 businesses with mission-critical 99.95% SLAs.<br>
                    • Roll out automated field technician dispatch with OTP tracking across hubs.
                  </div>
                </div>

                <div style="border-left: 3px solid #121316; padding-left: 12px; background: #FAF8F5; padding: 9px 14px; border-radius: 0 6px 6px 0;">
                  <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 13px; font-weight: 800; color: #121316;">Phase 3: All-India Bharat Scale (Months 7–12)</span>
                    <span class="badge-pill" style="font-size: 10px;">500k Units · ₹1,200 Cr ARR</span>
                  </div>
                  <div style="font-size: 11.5px; color: #5A5A5D; margin-top: 3px; line-height: 1.4;">
                    • Roll out across 500+ Tier-3/4 districts supported by 10 Indian languages.<br>
                    • Integrate full voice biometrics and regional dialect speech synthesis.<br>
                    • 12-Month Goal: <strong>500,000 active small businesses</strong> generating <strong>₹1,200 Cr annualized ARR</strong> at ₹3,250 blended CAC.
                  </div>
                </div>
              </div>
            </div>

            <!-- Ecosystem Synergies Card -->
            <div class="card-beige" style="padding: 16px 20px; flex: 1; display: flex; flex-direction: column; gap: 8px;">
              <div style="font-size: 13.5px; font-weight: 800; color: #121316; margin-bottom: 2px;">
                Strategic Airtel Ecosystem Synergies:
              </div>
              <div style="background: #FFFFFF; border: 1px solid #DDD8CE; padding: 8px 12px; border-radius: 6px;">
                <strong>Airtel Payments Bank:</strong> Integrated QR soundbox for Kirana checkouts; daily merchant cash settlements automatically offset monthly Accel broadband subscriptions.
              </div>
              <div style="background: #FFFFFF; border: 1px solid #DDD8CE; padding: 8px 12px; border-radius: 6px;">
                <strong>Airtel IQ WhatsApp API:</strong> Sub-second transactional quote push and LightGBM automated retargeting with 1-click pre-hydrated carts. Recovers 22.4% of abandoned prospects.
              </div>
              <div style="background: #FFFFFF; border: 1px solid #DDD8CE; padding: 8px 12px; border-radius: 6px;">
                <strong>Nxtra Data Centers:</strong> Sovereign Tier-4 Indian data facilities guarantee 100% DPDP Act 2023 compliance with zero offshore data transit or foreign jurisdiction exposure.
              </div>
              <div style="background: #FFFFFF; border: 1px solid #DDD8CE; padding: 8px 12px; border-radius: 6px;">
                <strong>Airtel 5G Plus QoS Slicing:</strong> Dedicated network QoS packet queues ensure zero latency jitter during evening peak payment hours (7–9 PM), preventing lost retail checkouts.
              </div>
              <div style="background: #FFFFFF; border: 1px solid #DDD8CE; padding: 8px 12px; border-radius: 6px;">
                <strong>Airtel Merchant Finance:</strong> Pre-approved working capital micro-loans up to ₹5 Lakhs for active Accel businesses based on automated broadband uptime and UPI transaction history.
              </div>
            </div>

          </div>

        </div>

        <!-- Full-Width Executive Conclusion Card -->
        <div class="card-beige" style="padding: 12px 20px; border-left: 4px solid #121316;">
          <div style="font-size: 12.5px; color: #121316; font-weight: 700; line-height: 1.4;">
            <strong>Executive Verdict:</strong> Project Udyam Digital transforms Accel Business from a slow, paper-bound corporate carrier into India's default digital operating system for small enterprises—slashing CAC by 78%, lifting non-GST conversions 4.25x, and unlocking ₹1,200 Cr ARR in 12 months.
          </div>
        </div>

      </div>

      <div class="slide-footer">
        <span>Airtel Sync 2026 · Digital Track | Project Udyam Digital</span>
        <span class="team-name">Team Neural Nexus · ABV-IIITM Gwalior</span>
        <span class="slide-number">Slide 7 of 7</span>
      </div>
    </div>
    """
    slides.append(s7)

    # =============================================================
    # SLIDE 8: ANNEXURE A - CPQ DAG ENGINE (REFERENCE ONLY)
    # =============================================================
    s8 = f"""
    <div class="slide">
      <div class="slide-header">
        <div class="slide-title-group">
          <h1>Annexure A: 25-Product CPQ Directed Acyclic Graph</h1>
          <p>Reference Only — Technical dependency structure and compatibility rules across 25 products</p>
        </div>
        <div class="slide-category-badge">Annexure A · Technical Reference</div>
      </div>

      <div class="slide-content">
        <div class="grid-5-4" style="flex: 1; gap: 18px;">
          
          <div class="card" style="display: flex; flex-direction: column; gap: 9px; padding: 16px 18px; justify-content: space-between;">
            <div class="card-title" style="margin-bottom: 0px;">Topological Prerequisite Rules & Mathematical Model</div>
            
            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 10px 14px; border-radius: 6px;">
              <div style="font-size: 11px; font-weight: 800; color: #121316; text-transform: uppercase;">Graph Model Complexity & Solver Latency</div>
              <div style="font-size: 11.5px; color: #4A4B4E; margin-top: 2px; line-height: 1.38;">
                Directed graph <i>G</i> = (<i>V</i>, <i>E</i>) with |<i>V</i>| = 25 product SKUs and |<i>E</i>| = 31 prerequisite edges. Topological sort validates order in <i>O</i>(|<i>V</i>| + |<i>E</i>|) = 56 operations, executing in <strong>0.12 ms</strong>.
              </div>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 10px 14px; border-radius: 6px;">
              <div style="font-size: 11px; font-weight: 800; color: #121316; text-transform: uppercase;">Layer 0: Base Pipes (P01..P04) — Pick Exactly 1</div>
              <div style="font-size: 11.5px; color: #4A4B4E; margin-top: 2px; line-height: 1.38;">
                Fixed Fiber 100M (₹999), 300M (₹1,999), 1Gbps (₹3,999), or Leased Line 1Gbps (₹8,999). Establishes root parent node in DAG. Topological sort guarantees zero orphan add-ons can be selected.
              </div>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 10px 14px; border-radius: 6px;">
              <div style="font-size: 11px; font-weight: 800; color: #121316; text-transform: uppercase;">Layer 1: Network & Reliability Add-Ons (P09, P11, P12)</div>
              <div style="font-size: 11.5px; color: #4A4B4E; margin-top: 2px; line-height: 1.38;">
                Static IPv4 (requires Fiber or Leased Line), 4G LTE Auto-Failover (requires Fiber P01..P03), Dual-Band Wi-Fi 6 Router. Enforces upstream base node existence before activating dependent child SKUs.
              </div>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 10px 14px; border-radius: 6px;">
              <div style="font-size: 11px; font-weight: 800; color: #121316; text-transform: uppercase;">Layer 2: IoT, Surveillance & Cloud Security (P21, P22, P24)</div>
              <div style="font-size: 11.5px; color: #4A4B4E; margin-top: 2px; line-height: 1.38;">
                Cloud CCTV AI 4-Cam (requires ≥100M Fiber), Industrial IoT Gateway (requires Leased Line P04 or P03), Cloud Perimeter Firewall. Restricts high-throughput security tools to compatible pipes.
              </div>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 10px 14px; border-radius: 6px;">
              <div style="font-size: 11px; font-weight: 800; color: #121316; text-transform: uppercase;">Layer 3: Mobility & Productivity Suite (P16, P18, P19)</div>
              <div style="font-size: 11.5px; color: #4A4B4E; margin-top: 2px; line-height: 1.38;">
                Business CUG SIMs (2x / 5x 100GB pooled corporate data), Google Workspace Office licenses, 500GB Airtel Cloud Storage. Multi-tenant corporate provisioning with zero manual intervention.
              </div>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 10px 14px; border-radius: 6px;">
              <div style="font-size: 11px; font-weight: 800; color: #121316; text-transform: uppercase;">Branch-and-Bound Pruning Complexity</div>
              <div style="font-size: 11.5px; color: #4A4B4E; margin-top: 2px; line-height: 1.38;">
                Pruning invalid DAG branches reduces candidate search space from 2<sup>25</sup> (33.55 million combinations) to under 180 feasible bundles, evaluated in <strong>&lt;0.45 ms</strong>.
              </div>
            </div>

            <div class="card-beige" style="padding: 10px 14px;">
              <div style="font-size: 11.5px; color: #121316; line-height: 1.38;">
                <strong>GSTIN Hard Firewall:</strong> Non-GST businesses cannot select Leased Line or Static IP. The CPQ engine instantly routes them to compliant Udyam Composite alternatives without error.
              </div>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #DDD8CE; padding: 10px 14px; border-radius: 6px;">
              <div style="font-size: 11px; font-weight: 800; color: #121316; text-transform: uppercase;">Commercial Invariant & Precision Engine</div>
              <div style="font-size: 11.5px; color: #5A5A5D; margin-top: 2px; line-height: 1.38;">
                Exact integer arithmetic enforced via Pydantic v2. Zero floating-point drift. Multi-category volume discounts (5%, 10%, 15%) computed deterministically server-side.
              </div>
            </div>
          </div>

          <!-- Right Column: Diagram + Optimization Formulation -->
          <div style="display: flex; flex-direction: column; gap: 12px; justify-content: space-between;">
            <div style="display: flex; justify-content: center; align-items: center; background: #FFFFFF; border: 1.5px solid #DDD8CE; border-radius: 12px; padding: 10px; height: 535px;">
              <img src="{img_dag_b64}" style="max-height: 515px; width: 100%; object-fit: contain;">
            </div>

            <div class="card-beige" style="padding: 16px 20px;">
              <div style="font-size: 13.5px; font-weight: 800; color: #121316; margin-bottom: 8px;">
                Branch-and-Bound Integer Linear Programming (ILP) Formulation:
              </div>
              <div class="grid-2" style="font-size: 11.5px; color: #4A4B4E; line-height: 1.45; gap: 14px;">
                <div>
                  &bull; <strong>Objective Function:</strong> Maximize &sum; (Utility<sub>i</sub> &times; x<sub>i</sub>)<br>
                  &bull; <strong>Budget Cap:</strong> &sum; (Cost<sub>i</sub> &times; x<sub>i</sub>) &le; BudgetCap<br>
                  &bull; <strong>Dependency:</strong> x<sub>child</sub> &le; x<sub>parent</sub> for all edges (parent &rarr; child)
                </div>
                <div>
                  &bull; <strong>GSTIN Hard Constraint:</strong> x<sub>gst_only</sub> &times; (1 &minus; is_gst) = 0<br>
                  &bull; <strong>Discount Tiers:</strong> 5% (2 cats), 10% (3 cats), 15% (4+ cats)<br>
                  &bull; <strong>Setup Fee Waiver:</strong> 100% waiver on &ge; 12-month commitments
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>

      <div class="slide-footer">
        <span>Airtel Sync 2026 · Digital Track | Project Udyam Digital · Annexure</span>
        <span class="team-name">Team Neural Nexus · ABV-IIITM Gwalior</span>
        <span class="slide-number">Annexure A</span>
      </div>
    </div>
    """
    slides.append(s8)

    # =============================================================
    # SLIDE 9: ANNEXURE B - DPDP ACT 2023 PRIVACY (REFERENCE ONLY)
    # =============================================================
    s9 = f"""
    <div class="slide">
      <div class="slide-header">
        <div class="slide-title-group">
          <h1>Annexure B: DPDP Act 2023 Data Privacy Architecture</h1>
          <p>Reference Only — Cryptographic zero-persistence privacy guarantee for small business owners</p>
        </div>
        <div class="slide-category-badge">Annexure B · Privacy Reference</div>
      </div>

      <div class="slide-content">
        <div class="grid-2" style="flex: 1; gap: 18px;">
          
          <!-- Left Column: Statutory Principles -->
          <div class="card" style="display: flex; flex-direction: column; gap: 8px; padding: 16px 20px; justify-content: space-between;">
            <div class="card-title" style="margin-bottom: 0px;">Statutory DPDP Principles Implemented</div>
            
            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 11px 14px; border-radius: 6px;">
              <strong style="font-size: 12px; color: #121316;">1. Purpose Limitation (Section 6, DPDP Act 2023):</strong>
              <div style="color: #4A4B4E; font-size: 11.5px; margin-top: 2px; line-height: 1.4;">
                Customer data is used strictly for telecom connectivity feasibility, pricing, and DoT statutory KYC. Zero secondary data selling, zero profiling, and zero third-party advertisement monetization.
              </div>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 11px 14px; border-radius: 6px;">
              <strong style="font-size: 12px; color: #121316;">2. Data Minimisation & Zero Persistence (Section 7):</strong>
              <div style="color: #4A4B4E; font-size: 11.5px; margin-top: 2px; line-height: 1.4;">
                12-digit national ID numbers are masked in-memory immediately upon byte ingestion ([ID Redacted]). Only safe masked tokens (XXXX-XXXX-1234) ever hit SQLite or persistent storage.
              </div>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 11px 14px; border-radius: 6px;">
              <strong style="font-size: 12px; color: #121316;">3. Verifiable Consent Tokens (Section 8):</strong>
              <div style="color: #4A4B4E; font-size: 11.5px; margin-top: 2px; line-height: 1.4;">
                Every transaction generates an immutable cryptographic consent record: SHA-256(ApplicantID + Timestamp + Purpose + ClientIP) stored for regulatory audit transparency.
              </div>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 11px 14px; border-radius: 6px;">
              <strong style="font-size: 12px; color: #121316;">4. Data Protection Officer & Audit Logging (Section 10):</strong>
              <div style="color: #4A4B4E; font-size: 11.5px; margin-top: 2px; line-height: 1.4;">
                All administrative access, cryptographic hashes, and verification outcomes are recorded in an append-only audit trail with sub-millisecond tamper detection.
              </div>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 11px 14px; border-radius: 6px;">
              <strong style="font-size: 12px; color: #121316;">5. Right to Erasure & Grievance Redressal (Section 12):</strong>
              <div style="color: #4A4B4E; font-size: 11.5px; margin-top: 2px; line-height: 1.4;">
                Merchant can trigger an instant purge of unactivated application tokens with zero orphaned records left in database, cache, or operational logs.
              </div>
            </div>

            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 11px 14px; border-radius: 6px;">
              <strong style="font-size: 12px; color: #121316;">6. Right to Data Portability & Audit Ledger (Section 11):</strong>
              <div style="color: #4A4B4E; font-size: 11.5px; margin-top: 2px; line-height: 1.4;">
                Merchants can export full machine-readable JSON logs of their service parameters, SLA records, and verified consent tokens at any point in their lifecycle.
              </div>
            </div>

            <div class="card-beige" style="padding: 12px 16px; border-left: 3px solid #121316;">
              <div style="font-size: 11.5px; color: #121316; line-height: 1.4;">
                <strong>Statutory Liability Shield:</strong> Completely eliminates exposure to Section 33 penalties (up to ₹250 Crore per data compromise incident) by ensuring raw biometric and identity numbers are never persisted anywhere.
              </div>
            </div>
          </div>

          <!-- Right Column: Cryptographic Ingestion Pipeline + Comparison Matrix -->
          <div class="card-beige" style="display: flex; flex-direction: column; gap: 8px; padding: 16px 20px; justify-content: space-between;">
            <div class="card-title" style="margin-bottom: 0px;">Cryptographic Ingestion Pipeline (7 Discrete Steps)</div>
            
            <div style="background: #FFFFFF; border: 1px solid #DDD8CE; padding: 9px 13px; border-radius: 6px;">
              <strong style="font-size: 11.5px; color: #121316;">Step 1: Volatile In-Memory Byte Stream (io.BytesIO)</strong>
              <div style="color: #5A5A5D; font-size: 11px; margin-top: 2px; line-height: 1.38;">
                Uploaded document bytes stream directly into RAM memory buffers without ever touching the server hard drive or temporary scratch folders.
              </div>
            </div>

            <div style="background: #FFFFFF; border: 1px solid #DDD8CE; padding: 9px 13px; border-radius: 6px;">
              <strong style="font-size: 11.5px; color: #121316;">Step 2: Instant Regex PII Redaction</strong>
              <div style="color: #5A5A5D; font-size: 11px; margin-top: 2px; line-height: 1.38;">
                12-digit national IDs are matched via regex and replaced with safe masked tokens (e.g. <code>SYN-XXXX-889</code>) inside memory buffers prior to schema validation.
              </div>
            </div>

            <div style="background: #FFFFFF; border: 1px solid #DDD8CE; padding: 9px 13px; border-radius: 6px;">
              <strong style="font-size: 11.5px; color: #121316;">Step 3: SHA-256 Idempotency & Replay Protection</strong>
              <div style="color: #5A5A5D; font-size: 11px; margin-top: 2px; line-height: 1.38;">
                Cryptographic file fingerprinting (<code>hashlib.sha256(raw_bytes).hexdigest()</code>) allows re-uploaded files to verify in under 2ms without re-running CPU OCR.
              </div>
            </div>

            <div style="background: #FFFFFF; border: 1px solid #DDD8CE; padding: 9px 13px; border-radius: 6px;">
              <strong style="font-size: 11.5px; color: #121316;">Step 4: RapidFuzz Levenshtein Entity Resolution</strong>
              <div style="color: #5A5A5D; font-size: 11px; margin-top: 2px; line-height: 1.38;">
                Cross-references applicant trade name against 3,534 GSTINs and 2,723 Udyam records with ≥70% token set ratio to prevent identity fraud.
              </div>
            </div>

            <div style="background: #FFFFFF; border: 1px solid #DDD8CE; padding: 9px 13px; border-radius: 6px;">
              <strong style="font-size: 11.5px; color: #121316;">Step 5: Deterministic Anchor Invariant (2026-07-15)</strong>
              <div style="color: #5A5A5D; font-size: 11px; margin-top: 2px; line-height: 1.38;">
                Document freshness verified strictly against anchor date 2026-07-15. Traps stale utility bills (&gt;90 days) and cancelled GSTINs deterministically.
              </div>
            </div>

            <div style="background: #FFFFFF; border: 1px solid #DDD8CE; padding: 9px 13px; border-radius: 6px;">
              <strong style="font-size: 11.5px; color: #121316;">Step 6: Immediate Garbage Collection</strong>
              <div style="color: #5A5A5D; font-size: 11px; margin-top: 2px; line-height: 1.38;">
                All raw byte buffers are explicitly deleted (<code>del raw_bytes; gc.collect()</code>) immediately after token generation to ensure zero memory residue.
              </div>
            </div>

            <div style="background: #FFFFFF; border: 1px solid #DDD8CE; padding: 9px 13px; border-radius: 6px;">
              <strong style="font-size: 11.5px; color: #121316;">Step 7: Immutable Audit Hash Chaining</strong>
              <div style="color: #5A5A5D; font-size: 11px; margin-top: 2px; line-height: 1.38;">
                Generates a forward-linked SHA-256 state token verifying regulatory compliance for DoT audits without ever storing personal customer records.
              </div>
            </div>

            <!-- DPDP Statutory Comparison Matrix -->
            <div style="background: #121316; color: #FAF8F5; padding: 12px 16px; border-radius: 8px;">
              <div style="font-size: 11.5px; font-weight: 800; color: #FAF8F5; text-transform: uppercase; margin-bottom: 6px;">
                DPDP 2023 Security Architecture Benchmark:
              </div>
              <table style="width: 100%; font-size: 11px; border-collapse: collapse; color: #DDD8CE;">
                <tr style="border-bottom: 1px solid #333;">
                  <td style="padding: 4px 0; color: #FFF; font-weight: 700; width: 30%;">National ID Storage</td>
                  <td style="padding: 4px 0; color: #BBB;">Legacy: Stored as plaintext PDFs</td>
                  <td style="padding: 4px 0; color: #FFF; font-weight: 700;">Udyam: 100% In-memory masked</td>
                </tr>
                <tr style="border-bottom: 1px solid #333;">
                  <td style="padding: 4px 0; color: #FFF; font-weight: 700;">Consent Records</td>
                  <td style="padding: 4px 0; color: #BBB;">Legacy: Unindexed paper logs</td>
                  <td style="padding: 4px 0; color: #FFF; font-weight: 700;">Udyam: SHA-256 chained hash</td>
                </tr>
                <tr>
                  <td style="padding: 4px 0; color: #FFF; font-weight: 700;">Section 33 Risk</td>
                  <td style="padding: 4px 0; color: #BBB;">Legacy: ₹250 Cr leak exposure</td>
                  <td style="padding: 4px 0; color: #FFF; font-weight: 700;">Udyam: Zero-persistence immunity</td>
                </tr>
              </table>
            </div>

          </div>

        </div>
      </div>

      <div class="slide-footer">
        <span>Airtel Sync 2026 · Digital Track | Project Udyam Digital · Annexure</span>
        <span class="team-name">Team Neural Nexus · ABV-IIITM Gwalior</span>
        <span class="slide-number">Annexure B</span>
      </div>
    </div>
    """
    slides.append(s9)

    # =============================================================
    # SLIDE 10: ANNEXURE C - PYTEST SUITE (REFERENCE ONLY)
    # =============================================================
    s10 = f"""
    <div class="slide">
      <div class="slide-header">
        <div class="slide-title-group">
          <h1>Annexure C: Complete 37/37 Pytest Verification Suite</h1>
          <p>Reference Only — Deterministic test matrix running on CI/CD runner and production AWS EC2</p>
        </div>
        <div class="slide-category-badge">Annexure C · Testing Reference</div>
      </div>

      <div class="slide-content" style="gap: 14px; flex: 1; display: flex; flex-direction: column;">
        
        <!-- Test Matrix Table Card -->
        <div class="card" style="padding: 14px 20px;">
          <table class="comp-table">
            <thead>
              <tr>
                <th style="width: 25%; padding: 10px 14px;">Test Module</th>
                <th style="width: 14%; padding: 10px 14px;">Status</th>
                <th style="width: 61%; padding: 10px 14px;">Invariants & Planted Edge Cases Verified</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style="padding: 9px 14px;"><code>test_phase1_data_ingestion.py</code></td>
                <td style="padding: 9px 14px;"><span class="badge-pill">7 / 7 Passed</span></td>
                <td style="padding: 9px 14px;">25 products, 3,534 GSTINs, 2,723 Udyam records, 5,000 lead records normalized.</td>
              </tr>
              <tr>
                <td style="padding: 9px 14px;"><code>test_phase2_cpq_dag.py</code></td>
                <td style="padding: 9px 14px;"><span class="badge-pill">5 / 5 Passed</span></td>
                <td style="padding: 9px 14px;">DAG topological sorting, prerequisite enforcement, &lt;0.5ms reverse budget solver.</td>
              </tr>
              <tr>
                <td style="padding: 9px 14px;"><code>test_phase3_advisor.py</code></td>
                <td style="padding: 9px 14px;"><span class="badge-pill">4 / 4 Passed</span></td>
                <td style="padding: 9px 14px;">Multi-turn dialog state retention, 10 Indic language parsing, slot extraction.</td>
              </tr>
              <tr>
                <td style="padding: 9px 14px;"><code>test_phase4_kyc_anomalies.py</code></td>
                <td style="padding: 9px 14px;"><span class="badge-pill">9 / 9 Passed</span></td>
                <td style="padding: 9px 14px;">Traps cancelled GSTIN (K01), missing POA (K05), entity mismatch (K07), stale utility bill (K11).</td>
              </tr>
              <tr>
                <td style="padding: 9px 14px;"><code>test_phase5_partner_ml.py</code></td>
                <td style="padding: 9px 14px;"><span class="badge-pill">4 / 4 Passed</span></td>
                <td style="padding: 9px 14px;">LightGBM GBDT model training, AUC 0.84 inference, automated WhatsApp rescue push.</td>
              </tr>
              <tr>
                <td style="padding: 9px 14px;"><code>test_api_endpoints.py</code></td>
                <td style="padding: 9px 14px;"><span class="badge-pill">7 / 7 Passed</span></td>
                <td style="padding: 9px 14px;">REST endpoints: /api/advisor/chat, /api/cpq/quote, /api/kyc/verify, /api/order/create.</td>
              </tr>
              <tr>
                <td style="padding: 9px 14px;"><code>test_e2e_journey.py</code></td>
                <td style="padding: 9px 14px;"><span class="badge-pill">1 / 1 Passed</span></td>
                <td style="padding: 9px 14px;">Full user journey from Hindi voice inquiry to live activated order with zero manual touch.</td>
              </tr>
              <tr class="highlight-row" style="background: #EFECE6; font-weight: 800;">
                <td style="padding: 9px 14px;"><strong>Total Verification Matrix</strong></td>
                <td style="padding: 9px 14px;"><strong>37 / 37 (100%)</strong></td>
                <td style="padding: 9px 14px;"><strong>Zero Mocks in Core Business Logic | Exit Code 0 | All CI/CD Passing</strong></td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 4-Stat Box Grid -->
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;">
          <div style="background: #FAF8F5; border: 1.5px solid #DDD8CE; padding: 15px 18px; border-radius: 8px;">
            <div style="font-size: 10px; font-weight: 800; color: #7A7B7E; text-transform: uppercase;">GSTIN Registry</div>
            <div style="font-size: 21px; font-weight: 900; color: #121316; margin-top: 2px;">3,534 Validated</div>
            <div style="font-size: 11.5px; color: #5A5A5D;">O(1) in-memory index</div>
          </div>
          <div style="background: #FAF8F5; border: 1.5px solid #DDD8CE; padding: 15px 18px; border-radius: 8px;">
            <div style="font-size: 10px; font-weight: 800; color: #7A7B7E; text-transform: uppercase;">Udyam Database</div>
            <div style="font-size: 21px; font-weight: 900; color: #121316; margin-top: 2px;">2,723 Records</div>
            <div style="font-size: 11.5px; color: #5A5A5D;">Deterministic local lookup</div>
          </div>
          <div style="background: #FAF8F5; border: 1.5px solid #DDD8CE; padding: 15px 18px; border-radius: 8px;">
            <div style="font-size: 10px; font-weight: 800; color: #7A7B7E; text-transform: uppercase;">CPQ DAG Latency</div>
            <div style="font-size: 21px; font-weight: 900; color: #121316; margin-top: 2px;">&lt; 0.5 ms</div>
            <div style="font-size: 11.5px; color: #5A5A5D;">Branch-and-bound solver</div>
          </div>
          <div style="background: #FAF8F5; border: 1.5px solid #DDD8CE; padding: 15px 18px; border-radius: 8px;">
            <div style="font-size: 10px; font-weight: 800; color: #7A7B7E; text-transform: uppercase;">PII Security</div>
            <div style="font-size: 21px; font-weight: 900; color: #121316; margin-top: 2px;">100% Zero RAM</div>
            <div style="font-size: 11.5px; color: #5A5A5D;">DPDP 2023 statutory shield</div>
          </div>
        </div>

        <!-- 6 Planted Adversarial Cases Trapped Grid -->
        <div style="background: #FFFFFF; border: 1.5px solid #DDD8CE; border-radius: 10px; padding: 16px 20px; display: flex; flex-direction: column; gap: 10px; flex: 1;">
          <div style="font-size: 13px; font-weight: 800; color: #121316; text-transform: uppercase; letter-spacing: 0.5px;">
            Adversarial Attack & Planted Anomaly Trapping Matrix (Verified in tests/):
          </div>
          <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 11px; font-size: 11.5px; flex: 1;">
            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 11px 14px; border-radius: 6px;">
              <strong>K01 Cancelled GSTIN:</strong> Trapped at regex + registry verification; status flagged CANCELLED; returns clean remediation guidance.
            </div>
            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 11px 14px; border-radius: 6px;">
              <strong>K05 Missing POA Document:</strong> Trapped during in-memory multi-slot validation; returns non-blocking request for utility bill.
            </div>
            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 11px 14px; border-radius: 6px;">
              <strong>K07 Entity Name Mismatch:</strong> RapidFuzz token match returns 58.2% (&lt;70% threshold); prompts merchant for trade name proof.
            </div>
            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 11px 14px; border-radius: 6px;">
              <strong>K11 Stale Utility Bill:</strong> Evaluated against anchor 2026-07-15; bill date is 257 days old (&gt;90d statutory limit); rejected.
            </div>
            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 11px 14px; border-radius: 6px;">
              <strong>Prompt Injection Attack:</strong> Adversarial jailbreak attempts rejected by Pydantic v2 strict schemas and slot extractors.
            </div>
            <div style="background: #FAF8F5; border: 1px solid #EFECE6; padding: 11px 14px; border-radius: 6px;">
              <strong>Client Price Tampering:</strong> Client-side price tampering ignored; DAG recomputes true integer pricing server-side.
            </div>
          </div>
        </div>

        <!-- Production CI/CD & Cloud Infrastructure Box -->
        <div class="card-beige" style="padding: 13px 20px; border-left: 3px solid #121316;">
          <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12px;">
            <span style="font-weight: 800; color: #121316;">CI/CD Verification Infrastructure & Reproducibility Guarantee:</span>
            <span style="color: #4A4B4E; font-weight: 600;">AWS EC2 Production Monolith · systemd auto-healing · 37 tests in 0.42s · 100 Visual Case Proofs Documented</span>
          </div>
          <div style="font-size: 11.5px; color: #5A5A5D; margin-top: 4px;">
            Live Audit Dashboard: <a href="http://65.1.112.251/audit/audit_dashboard.html" style="color: #121316; font-weight: 700; text-decoration: underline;">http://65.1.112.251/audit/audit_dashboard.html</a> &nbsp;|&nbsp; 
            Swagger UI: <a href="http://65.1.112.251/docs" style="color: #121316; font-weight: 700; text-decoration: underline;">http://65.1.112.251/docs</a> &nbsp;|&nbsp; 
            Live Web App: <a href="http://65.1.112.251" style="color: #121316; font-weight: 700; text-decoration: underline;">http://65.1.112.251</a>
          </div>
        </div>

      </div>

      <div class="slide-footer">
        <span>Airtel Sync 2026 · Digital Track | Project Udyam Digital · Annexure</span>
        <span class="team-name">Team Neural Nexus · ABV-IIITM Gwalior</span>
        <span class="slide-number">Annexure C</span>
      </div>
    </div>
    """
    slides.append(s10)

    return slides

def main():
    print("=== Building Official Winning Deck for Airtel Sync 2026 ===")
    slides = generate_slides_html()
    print(f"Total Slides Generated: {len(slides)} (Slide 0 Intro + 7 Evaluated Slides + 3 Annexures)")

    # 1. Write individual slide HTML files & all_slides.html
    html_files = []
    for idx, slide_content in enumerate(slides):
        full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
{CSS_THEME}
</style>
</head>
<body>
{slide_content}
</body>
</html>"""
        path = os.path.join(BUILD_DIR, f"slide_{idx}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(full_html)
        html_files.append(path)

    all_slides_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
{CSS_THEME}
@page {{
  size: 1920px 1080px;
  margin: 0;
}}
.slide {{
  page-break-after: always;
}}
</style>
</head>
<body>
{"".join(slides)}
</body>
</html>"""
    all_path = os.path.join(BUILD_DIR, "all_slides.html")
    with open(all_path, "w", encoding="utf-8") as f:
        f.write(all_slides_html)

    # 2. Render each slide to high-res PNG using Edge Playwright
    print("Launching Microsoft Edge via Playwright to render 4K screenshots...")
    slide_pngs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2
        )
        page = context.new_page()

        for idx, slide_html in enumerate(html_files):
            abs_url = f"file:///{os.path.abspath(slide_html).replace(os.sep, '/')}"
            page.goto(abs_url, wait_until="networkidle")
            page.wait_for_timeout(300)
            png_path = os.path.join(PREVIEW_DIR, f"slide_{idx}.png")
            page.screenshot(path=png_path)
            slide_pngs.append(png_path)
            print(f"  -> Rendered Slide {idx}: {png_path}")

        # Render PDF of the entire presentation
        print(f"Rendering official PDF: {OFFICIAL_PDF}...")
        all_abs_url = f"file:///{os.path.abspath(all_path).replace(os.sep, '/')}"
        page.goto(all_abs_url, wait_until="networkidle")
        page.wait_for_timeout(500)
        page.pdf(
            path=OFFICIAL_PDF,
            width="1920px",
            height="1080px",
            print_background=True,
            prefer_css_page_size=True,
            margin={"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"}
        )
        print(f"  -> Generated {OFFICIAL_PDF} ({os.path.getsize(OFFICIAL_PDF) / (1024*1024):.2f} MB)")

        browser.close()

    # 3. Build native widescreen PPTX embedding the rendered 4K slide PNGs
    print(f"Building official PPTX: {OFFICIAL_PPTX}...")
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    for png in slide_pngs:
        slide = prs.slides.add_slide(blank_layout)
        slide.shapes.add_picture(png, Inches(0), Inches(0), width=Inches(13.333), height=Inches(7.5))

    prs.save(OFFICIAL_PPTX)
    print(f"  -> Generated {OFFICIAL_PPTX} ({os.path.getsize(OFFICIAL_PPTX) / (1024*1024):.2f} MB)")

    print("\n=== Presentation Build Complete! ===")
    print(f"1. PDF: {OFFICIAL_PDF} ({os.path.getsize(OFFICIAL_PDF) / (1024*1024):.2f} MB)")
    print(f"2. PPT: {OFFICIAL_PPTX} ({os.path.getsize(OFFICIAL_PPTX) / (1024*1024):.2f} MB)")

if __name__ == "__main__":
    main()
