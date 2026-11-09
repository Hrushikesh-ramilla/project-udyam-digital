import os
import sys
import base64
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
from pptx import Presentation
from pptx.util import Inches

BUILD_DIR = "docs/presentation/build"
PREVIEW_DIR = "docs/presentation/preview"
OFFICIAL_PDF = "Neural_Nexus_ABV_IIITM_Gwalior.pdf"
OFFICIAL_PPTX = "Neural_Nexus_ABV_IIITM_Gwalior.pptx"
TEAM_NAME = "Neural Nexus"

os.makedirs(BUILD_DIR, exist_ok=True)
os.makedirs(PREVIEW_DIR, exist_ok=True)

def to_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            ext = path.split(".")[-1]
            mime = "image/png" if ext == "png" else "image/jpeg"
            return f"data:{mime};base64," + base64.b64encode(f.read()).decode("utf-8")
    return ""

img_template_cover_b64 = to_base64("docs/presentation/template_extracted/slide_1_img_0.jpg")
img_template_slide_b64 = to_base64("docs/presentation/template_extracted/slide_2_img_0.jpg")
img_arch_b64 = to_base64("docs/presentation/assets/udyam-architecture-tight.png")
img_screen_advisor_b64 = to_base64("docs/presentation/assets/clean_advisor.png")
img_screen_cart_b64 = to_base64("docs/presentation/assets/clean_cart.png")
img_screen_kyc_b64 = to_base64("docs/presentation/assets/clean_kyc.png")
img_screen_fulfillment_b64 = to_base64("docs/presentation/assets/clean_fulfillment.png")
img_screen_tracker_b64 = to_base64("docs/presentation/assets/screen_tracker.png")

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
  position: relative;
  background-size: 1920px 1080px;
  background-position: center;
  background-repeat: no-repeat;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.slide-cover-bg {
  background-color: #0A0B0E;
  padding: 0 72px 28px 72px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}
.slide-template-bg {
  background-color: #FFFFFF;
  padding: 24px 72px 18px 72px;
}
.slide-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-left: 175px;
  margin-right: 175px;
  border-bottom: 2px solid #EFECE6;
  padding-bottom: 10px;
  margin-bottom: 14px;
  min-height: 82px;
}
.slide-title-group h1 {
  font-size: 32px;
  font-weight: 850;
  color: #121316;
  letter-spacing: -0.6px;
  line-height: 1.15;
}
.slide-title-group p {
  font-size: 15px;
  color: #5A5A5D;
  margin-top: 3px;
  font-weight: 500;
}
.slide-category-badge {
  font-size: 12px;
  font-weight: 750;
  text-transform: uppercase;
  letter-spacing: 1px;
  background-color: #F4F1EA;
  color: #E40000;
  padding: 6px 14px;
  border-radius: 6px;
  border: 1.5px solid #DDD8CE;
  white-space: nowrap;
}
.slide-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 6px;
}
.slide-footer {
  margin-top: auto;
  padding-top: 6px;
  margin-right: 340px;
  border-top: 1.5px solid #EFECE6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #6A6D75;
  font-weight: 500;
}
.slide-footer .team-name {
  font-weight: 750;
  color: #121316;
}
.slide-footer .slide-number {
  font-weight: 800;
  color: #121316;
  background-color: #EFECE6;
  padding: 3px 12px;
  border-radius: 4px;
}

.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
.grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.grid-5-4 { display: grid; grid-template-columns: 1.05fr 0.95fr; gap: 20px; }

.card {
  background-color: #FFFFFF;
  border: 1.5px solid #DDD8CE;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.02);
}
.card-beige {
  background-color: #F7F5F0;
  border: 1.5px solid #DDD8CE;
  border-radius: 8px;
}
.badge-pill {
  font-size: 11px;
  font-weight: 750;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background-color: #EFECE6;
  color: #121316;
  padding: 3px 9px;
  border-radius: 4px;
  border: 1px solid #DDD8CE;
}
.bullet-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.bullet-list li {
  position: relative;
  padding-left: 13px;
  line-height: 1.35;
  color: #2D2E32;
  font-size: 12.5px;
}
.bullet-list li::before {
  content: "•";
  position: absolute;
  left: 0;
  color: #E40000;
  font-weight: bold;
}
.stat-box {
  background: #FFFFFF;
  border: 1.5px solid #DDD8CE;
  border-radius: 8px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
}
.stat-num {
  font-size: 42px;
  font-weight: 900;
  color: #121316;
  letter-spacing: -1px;
  line-height: 1.1;
}
.stat-label {
  font-size: 14px;
  font-weight: 750;
  color: #121316;
  margin-top: 4px;
}
.stat-sub {
  font-size: 12.5px;
  color: #5A5A5D;
  margin-top: 3px;
  line-height: 1.35;
}

.comp-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14.5px;
}
.comp-table th {
  background-color: #F4F1EA;
  color: #121316;
  font-weight: 800;
  text-align: left;
  padding: 11px 14px;
  border: 1px solid #DDD8CE;
}
.comp-table td {
  padding: 10px 14px;
  border: 1px solid #DDD8CE;
  color: #2D2E32;
}
.comp-table tr:nth-child(even) {
  background-color: #FCFBF9;
}
.comp-table .highlight-row {
  background-color: #FAF4F4;
  font-weight: 750;
  border-left: 3px solid #E40000;
}
"""

def generate_deck():
    print("=== Building Official Winning Deck for Airtel Sync 2026 ===")
    
    # SLIDE 0: TITLE & REGISTRATION COVER
    s0 = f"""
    <div class="slide slide-cover-bg" style="background-image: url('{img_template_cover_b64}');">
      <div style="position: absolute; top: 505px; left: 72px; right: 72px; bottom: 30px; display: flex; flex-direction: column; justify-content: space-between;">
        <div>
          <div style="display: inline-block; font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: 1.2px; color: #E40000; background: rgba(228,0,0,0.12); padding: 5px 14px; border-radius: 4px; margin-bottom: 8px; border: 1px solid rgba(228,0,0,0.3);">
            BHARTI AIRTEL · AIRTEL SYNC 2026 · DIGITAL TRACK (ENTERPRISE TRACK A)
          </div>
          <h1 style="font-size: 46px; font-weight: 900; color: #FFFFFF; letter-spacing: -1.2px; line-height: 1.1; margin-bottom: 6px;">
            Project Udyam Digital
          </h1>
          <p style="font-size: 19px; color: #DDD8CE; font-weight: 500; max-width: 1300px; line-height: 1.35;">
            Instant Self-Serve Mobile Onboarding, Fast Legal KYC & Multi-Site Connectivity for 6 Cr+ MSMEs
          </p>
        </div>

        <div class="grid-2" style="gap: 20px;">
          <div style="background: rgba(18, 19, 22, 0.85); border: 1.5px solid rgba(255,255,255,0.15); border-radius: 8px; padding: 18px 22px; backdrop-filter: blur(8px);">
            <div style="font-size: 14px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; color: #FFFFFF; margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 6px;">
              Team & Institutional Registration
            </div>
            <table style="width: 100%; font-size: 14px; color: #C5C6C9; border-collapse: collapse;">
              <tr><td style="padding: 5px 0; width: 34%; font-weight: 600; color: #8F9094;">Team Name</td><td style="font-weight: 800; color: #FFFFFF;">Neural Nexus</td></tr>
              <tr><td style="padding: 5px 0; font-weight: 600; color: #8F9094;">Institution</td><td style="font-weight: 750; color: #FFFFFF;">ABV-IIITM Gwalior</td></tr>
              <tr><td style="padding: 5px 0; font-weight: 600; color: #8F9094;">Track</td><td style="font-weight: 700; color: #FFFFFF;">Digital Track (Enterprise Track A: Accel Business)</td></tr>
              <tr><td style="padding: 5px 0; font-weight: 600; color: #8F9094;">Team Members</td><td style="font-weight: 700; color: #FFFFFF;">Hrushikesh Ramilla &nbsp;&nbsp;|&nbsp;&nbsp; G Yaswanth Kumar</td></tr>
              <tr><td style="padding: 5px 0; font-weight: 600; color: #8F9094;">Technical Stack</td><td style="font-weight: 600; color: #FFFFFF; font-size: 13px;">Python 3.11+, FastAPI, React 18, Vite, LightGBM, RapidFuzz, SQLite WAL</td></tr>
            </table>
          </div>

          <div style="background: rgba(18, 19, 22, 0.85); border: 1.5px solid rgba(255,255,255,0.15); border-radius: 8px; padding: 18px 22px; backdrop-filter: blur(8px);">
            <div style="font-size: 14px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; color: #FFFFFF; margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 6px;">
              Live Working Prototype & Direct Audit Links
            </div>
            <table style="width: 100%; font-size: 14px; color: #C5C6C9; border-collapse: collapse;">
              <tr><td style="padding: 6px 0; width: 34%; font-weight: 600; color: #8F9094;">Live Platform</td><td><a href="https://airtel.hrushikeshramilla.in" style="color: #FF5252; text-decoration: underline; font-weight: 800;">airtel.hrushikeshramilla.in</a></td></tr>
              <tr><td style="padding: 6px 0; font-weight: 600; color: #8F9094;">Demo Video</td><td><a href="https://airtel.hrushikeshramilla.in/demoVideo" style="color: #FF5252; text-decoration: underline; font-weight: 850;">https://airtel.hrushikeshramilla.in/demoVideo</a></td></tr>
              <tr><td style="padding: 6px 0; font-weight: 600; color: #8F9094;">Repository</td><td style="font-family: monospace; font-size: 13px; color: #FFFFFF;">github.com/hrushikesh-ramilla/project-udyam-digital</td></tr>
              <tr><td style="padding: 6px 0; font-weight: 600; color: #8F9094;">Compliance</td><td><span style="background: rgba(0, 114, 255, 0.25); color: #64b5f6; font-size: 11.5px; font-weight: 800; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(0, 114, 255, 0.4);">DPDP ACT 2023</span> <span style="color: #FFFFFF; font-weight: 600; font-size: 13px;">Zero-Persistence Privacy</span></td></tr>
            </table>
          </div>
        </div>

        <div style="background: rgba(18, 19, 22, 0.9); border-left: 4px solid #E40000; border-radius: 6px; padding: 12px 18px; width: 100%;">
          <div style="font-size: 13.5px; font-weight: 800; color: #FFFFFF; margin-bottom: 4px;">
            The Executive Scope at a Glance (Airtel Enterprise Track A Mandate):
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1.1fr 1.2fr; gap: 14px; font-size: 12.5px; color: #C5C6C9; line-height: 1.35;">
            <div><strong style="color: #FFFFFF;">1. Market:</strong> 6.3 Cr MSMEs; 55% under GST threshold. Discarding non-GST loses 3.5 Cr merchants.</div>
            <div><strong style="color: #FFFFFF;">2. Bottleneck:</strong> 3–5 day manual quotes cause 56.4% abandonment and ₹15,000 CAC bleed.</div>
            <div><strong style="color: #FFFFFF;">3. Udyam:</strong> Multilingual AI (100+ langs, Session Inertia), &lt;0.5ms CPQ DAG, zero-persistence KYC, NPCI UPI.</div>
          </div>
        </div>

        <div style="font-size: 11px; color: #7A7B7E; width: 100%;">
          Submission Note: Mandatory Introduction Slide (excluded from 7-slide evaluation count). Slides 1 to 7 showcase the technical solution, competitive moat, and quantified business impact.
        </div>
      </div>
    </div>
    """

    # SLIDE 1: PROBLEM STATEMENT & 5,000-LEAD SALES DROP-OFF
    s1 = f"""
    <div class="slide slide-template-bg" style="background-image: url('{img_template_slide_b64}');">
      <div class="slide-header">
        <div class="slide-title-group">
          <h1>Problem Statement: The 5,000-Lead Sales Drop-Off</h1>
          <p>Real-world analysis of 5,000 small business leads from April to June 2026 (smb_leads.csv)</p>
        </div>
        <div class="slide-category-badge">Slide 1 of 7 · Challenge Context</div>
      </div>

      <div class="slide-content">
        <div class="grid-5-4" style="flex: 1; gap: 18px;">
          
          <div class="card" style="display: flex; flex-direction: column; gap: 12px; padding: 18px 20px;">
            <div>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 18px; font-weight: 850; color: #121316;">Sales Funnel Analysis (N = 5,000 Leads)</span>
                <span style="font-size: 12.5px; font-weight: 600; color: #5A5A5D; background: #EFECE6; padding: 3px 10px; border-radius: 4px;">Tier 1–2 Cities</span>
              </div>
              
              <table class="comp-table" style="font-size: 14.5px;">
                <tr>
                  <th style="width: 44%; padding: 11px 14px;">Funnel Stage</th>
                  <th style="width: 18%; text-align: right; padding: 11px 14px;">Leads</th>
                  <th style="width: 18%; text-align: right; padding: 11px 14px;">Stage %</th>
                  <th style="width: 20%; text-align: right; padding: 11px 14px;">Drop / Status</th>
                </tr>
                <tr>
                  <td style="padding: 11px 14px;">1. Leads Generated</td>
                  <td style="text-align: right; font-weight: 800; padding: 11px 14px;">5,000</td>
                  <td style="text-align: right; padding: 11px 14px;">100.0%</td>
                  <td style="text-align: right; color: #5A5A5D; padding: 11px 14px;">Starting Base</td>
                </tr>
                <tr>
                  <td style="padding: 11px 14px;">2. Contacted Outreach</td>
                  <td style="text-align: right; font-weight: 800; padding: 11px 14px;">3,406</td>
                  <td style="text-align: right; padding: 11px 14px;">68.1%</td>
                  <td style="text-align: right; color: #5A5A5D; padding: 11px 14px;">-31.9%</td>
                </tr>
                <tr>
                  <td style="padding: 11px 14px;">3. Needs Assessed (Field Visit)</td>
                  <td style="text-align: right; font-weight: 800; padding: 11px 14px;">1,974</td>
                  <td style="text-align: right; padding: 11px 14px;">58.0%</td>
                  <td style="text-align: right; color: #5A5A5D; padding: 11px 14px;">-42.0%</td>
                </tr>
                <tr style="background-color: #FFF3F3; border-left: 3px solid #E40000;">
                  <td style="padding: 11px 14px; font-weight: 850; color: #E40000;">4. Quote Accepted (Steepest Drop)</td>
                  <td style="text-align: right; font-weight: 900; color: #E40000; padding: 11px 14px;">861</td>
                  <td style="text-align: right; font-weight: 900; color: #E40000; padding: 11px 14px;">43.6%</td>
                  <td style="text-align: right; padding: 11px 14px;"><span class="badge-pill" style="background: #E40000; color: #fff; border-color: #E40000; font-weight: 800;">-56.4% CLIFF</span></td>
                </tr>
                <tr>
                  <td style="padding: 11px 14px;">5. KYC Completed</td>
                  <td style="text-align: right; font-weight: 800; padding: 11px 14px;">588</td>
                  <td style="text-align: right; padding: 11px 14px;">68.3%</td>
                  <td style="text-align: right; color: #5A5A5D; padding: 11px 14px;">-31.7%</td>
                </tr>
                <tr class="highlight-row">
                  <td style="padding: 11px 14px;"><strong>6. Activated Customers</strong></td>
                  <td style="text-align: right; font-weight: 900; padding: 11px 14px;">368</td>
                  <td style="text-align: right; font-weight: 900; padding: 11px 14px;">62.6%</td>
                  <td style="text-align: right; padding: 11px 14px;"><span class="badge-pill" style="background: #121316; color: #fff; font-weight: 800;">7.36% NET ACTIVATION</span></td>
                </tr>
              </table>
            </div>

            <div style="background-color: #FAF8F5; border: 1.5px solid #DDD8CE; border-radius: 8px; padding: 14px 18px;">
              <div style="font-size: 13.5px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; color: #5A5A5D; margin-bottom: 10px;">
                Visual Funnel Retention Rate (% of Initial 5,000 Leads)
              </div>
              <div style="display: flex; flex-direction: column; gap: 9px; font-size: 14px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                  <span style="width: 155px; font-weight: 700;">1. Leads Generated</span>
                  <div style="flex: 1; background: #EFECE6; height: 26px; border-radius: 4px; overflow: hidden;">
                    <div style="width: 100%; background: #121316; height: 100%;"></div>
                  </div>
                  <span style="width: 55px; text-align: right; font-weight: 850;">100%</span>
                </div>
                <div style="display: flex; align-items: center; gap: 12px;">
                  <span style="width: 155px; font-weight: 700;">2. Contacted</span>
                  <div style="flex: 1; background: #EFECE6; height: 26px; border-radius: 4px; overflow: hidden;">
                    <div style="width: 68.1%; background: #4A4B4E; height: 100%;"></div>
                  </div>
                  <span style="width: 55px; text-align: right; font-weight: 850;">68.1%</span>
                </div>
                <div style="display: flex; align-items: center; gap: 12px;">
                  <span style="width: 155px; font-weight: 700;">3. Needs Assessed</span>
                  <div style="flex: 1; background: #EFECE6; height: 26px; border-radius: 4px; overflow: hidden;">
                    <div style="width: 39.5%; background: #4A4B4E; height: 100%;"></div>
                  </div>
                  <span style="width: 55px; text-align: right; font-weight: 850;">39.5%</span>
                </div>
                <div style="display: flex; align-items: center; gap: 12px;">
                  <span style="width: 155px; font-weight: 900; color: #E40000;">4. Quote Accepted</span>
                  <div style="flex: 1; background: #EFECE6; height: 26px; border-radius: 4px; overflow: hidden;">
                    <div style="width: 17.2%; background: #E40000; height: 100%;"></div>
                  </div>
                  <span style="width: 55px; text-align: right; font-weight: 900; color: #E40000;">17.2%</span>
                </div>
                <div style="display: flex; align-items: center; gap: 12px;">
                  <span style="width: 155px; font-weight: 700;">5. KYC Complete</span>
                  <div style="flex: 1; background: #EFECE6; height: 26px; border-radius: 4px; overflow: hidden;">
                    <div style="width: 11.8%; background: #4A4B4E; height: 100%;"></div>
                  </div>
                  <span style="width: 55px; text-align: right; font-weight: 850;">11.8%</span>
                </div>
                <div style="display: flex; align-items: center; gap: 12px;">
                  <span style="width: 155px; font-weight: 900; color: #121316;">6. Activated</span>
                  <div style="flex: 1; background: #EFECE6; height: 26px; border-radius: 4px; overflow: hidden;">
                    <div style="width: 7.36%; background: #121316; height: 100%;"></div>
                  </div>
                  <span style="width: 55px; text-align: right; font-weight: 900; color: #121316;">7.36%</span>
                </div>
              </div>
            </div>

            <div class="grid-2" style="gap: 12px;">
              <div style="font-size: 13.5px; color: #333336; line-height: 1.45; background: #EFECE6; padding: 14px 16px; border-radius: 6px;">
                <strong style="color: #121316;">The Non-GST Penalty:</strong> Leads with active GSTIN activate at <strong>9.6%</strong>, while leads without GST drop to <strong>2.0%</strong> (a 4.8x conversion penalty caused by legacy enterprise forms).
              </div>
              <div style="font-size: 13.5px; color: #333336; line-height: 1.45; background: #EFECE6; padding: 14px 16px; border-radius: 6px;">
                <strong style="color: #121316;">High Cost of Delay:</strong> 17.6-day average cycle time and 3.2 chase calls consume ₹15,000 in sales rep labor per deal, requiring 14.2 months to break even on CAC.
              </div>
            </div>

            <div style="font-size: 13.5px; color: #4A4B4E; line-height: 1.45; background: #FAF0F0; border-left: 3.5px solid #E40000; padding: 14px 16px; border-radius: 6px;">
              <strong style="color: #900;">15.2% Mis-Selling Discovery:</strong> Data audit reveals <strong>56 of 368 activated bundles (15.2%) violated catalogue rules</strong> (wrong tier, size, inactive GSTIN, missing dependencies). Udyam Digital's CPQ DAG mathematically guarantees a <strong>0% violation rate</strong>.
            </div>
          </div>

          <div style="display: flex; flex-direction: column; gap: 12px;">
            <div class="card" style="padding: 16px 18px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 3px;">
                <span class="badge-pill" style="background: #E40000; color: #fff; border-color: #E40000;">Failure Mode 1</span>
                <span style="font-size: 13px; font-weight: 850; color: #E40000;">56.4% Abandonment</span>
              </div>
              <div style="font-size: 16.5px; font-weight: 850; color: #121316;">The 3–5 Day Quoting Wait (Latency Bleed)</div>
              <ul class="bullet-list" style="margin-top: 5px; gap: 4px;">
                <li style="font-size: 13.5px;">Sales reps manually cross-check 25 disconnected enterprise SKUs on static Excel rate-cards.</li>
                <li style="font-size: 13.5px;"><strong>Quoting Delay Bleed:</strong> 1,113 of 1,974 interested businesses abandon before receiving pricing.</li>
                <li style="font-size: 13.5px;">Local cable resellers win deals on the spot with verbal, instant cash commitments.</li>
              </ul>
            </div>

            <div class="card" style="padding: 16px 18px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 3px;">
                <span class="badge-pill" style="background: #E40000; color: #fff; border-color: #E40000;">Failure Mode 2</span>
                <span style="font-size: 13px; font-weight: 850; color: #E40000;">4.8x Conversion Cliff</span>
              </div>
              <div style="font-size: 16.5px; font-weight: 850; color: #121316;">The Non-GST Regulatory Wall (Market Exclusion)</div>
              <ul class="bullet-list" style="margin-top: 5px; gap: 4px;">
                <li style="font-size: 13.5px;">55% of India's 6.3 Crore micro-enterprises earn under ₹40 Lakhs and are legally GST-exempt.</li>
                <li style="font-size: 13.5px;">Legacy enterprise CRM hardcodes mandatory 15-character GSTIN input validation fields.</li>
                <li style="font-size: 13.5px;">Discards 3.5 Crore retail shops and clinics at the front door; non-GST conversion drops to 2.0%.</li>
              </ul>
            </div>

            <div class="card" style="padding: 16px 18px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 3px;">
                <span class="badge-pill" style="background: #E40000; color: #fff; border-color: #E40000;">Failure Mode 3</span>
                <span style="font-size: 13px; font-weight: 850; color: #E40000;">₹15,000 Direct CAC</span>
              </div>
              <div style="font-size: 16.5px; font-weight: 850; color: #121316;">Crippling Unit Economics (Manual Follow-Ups)</div>
              <ul class="bullet-list" style="margin-top: 5px; gap: 4px;">
                <li style="font-size: 13.5px;">A slow 17.6-day onboarding cycle requires 3.2 manual status chase calls per lead.</li>
                <li style="font-size: 13.5px;">Consumes ₹15,000 in sales rep field labor per closed account.</li>
                <li style="font-size: 13.5px;">Requires 14.2 months to break even on CAC against ₹6,900 monthly ARPU.</li>
              </ul>
            </div>

            <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px;">
              <div style="background: #FAF8F5; border: 1.5px solid #DDD8CE; padding: 12px 4px; border-radius: 6px; text-align: center;">
                <div style="font-size: 11px; color: #7A7B7E; font-weight: 750; text-transform: uppercase;">Quoting Drop</div>
                <div style="font-size: 22px; font-weight: 900; color: #E40000; margin-top: 2px;">-56.4%</div>
              </div>
              <div style="background: #FAF8F5; border: 1.5px solid #DDD8CE; padding: 12px 4px; border-radius: 6px; text-align: center;">
                <div style="font-size: 11px; color: #7A7B7E; font-weight: 750; text-transform: uppercase;">Non-GST Gap</div>
                <div style="font-size: 22px; font-weight: 900; color: #121316; margin-top: 2px;">4.8x Lower</div>
              </div>
              <div style="background: #FAF8F5; border: 1.5px solid #E40000; padding: 12px 4px; border-radius: 6px; text-align: center;">
                <div style="font-size: 11px; color: #E40000; font-weight: 750; text-transform: uppercase;">Mis-Sell Rate</div>
                <div style="font-size: 22px; font-weight: 900; color: #E40000; margin-top: 2px;">15.2% (56)</div>
              </div>
              <div style="background: #FAF8F5; border: 1.5px solid #DDD8CE; padding: 12px 4px; border-radius: 6px; text-align: center;">
                <div style="font-size: 11px; color: #7A7B7E; font-weight: 750; text-transform: uppercase;">Cycle Time</div>
                <div style="font-size: 22px; font-weight: 900; color: #121316; margin-top: 2px;">17.6 Days</div>
              </div>
              <div style="background: #FAF8F5; border: 1.5px solid #DDD8CE; padding: 12px 4px; border-radius: 6px; text-align: center;">
                <div style="font-size: 11px; color: #7A7B7E; font-weight: 750; text-transform: uppercase;">Direct CAC</div>
                <div style="font-size: 22px; font-weight: 900; color: #121316; margin-top: 2px;">₹15,000</div>
              </div>
            </div>

            <div class="card-beige" style="padding: 14px 18px;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-size: 13.5px; font-weight: 850; color: #121316; text-transform: uppercase; letter-spacing: 0.5px;">Financial Revenue Bleed (5,000 Sample Leads)</div>
                <span class="badge-pill" style="background: #121316; color: #fff; font-weight: 850;">₹11.05 Cr / Yr Lost</span>
              </div>
              <div style="font-size: 13px; color: #4A4B4E; margin-top: 4px; line-height: 1.4;">
                At median ₹6,900/mo ARPU, the 1,113 abandoned leads represent <strong>₹92.1 Lakhs/month in lost recurring revenue</strong>. Nationwide across Airtel's enterprise funnel, this quoting latency bleeds over <strong>₹120+ Crore annually</strong> to competitors.
              </div>
            </div>

            <div style="background: #121316; color: #FFFFFF; border-radius: 6px; padding: 13px 18px;">
              <div style="font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; color: #E40000;">The Accel Business Mandate:</div>
              <div style="font-size: 13.5px; margin-top: 3px; line-height: 1.4; color: #EFECE6;">
                Compress quote delivery from 5 days to <strong>under 60 seconds</strong>, unlock non-GST merchants via instant Udyam lookup, and automate tracking to eliminate chase calls.
              </div>
            </div>
          </div>

        </div>
      </div>

      <div class="slide-footer">
        <div>Airtel Sync 2026 · Digital Track | Project Udyam Digital</div>
        <div class="team-name">Team Neural Nexus · ABV-IIITM Gwalior</div>
        <div class="slide-number">Slide 1 of 7</div>
      </div>
    </div>
    """

    # -------------------------------------------------------------
    # SLIDE 2: TARGET CUSTOMER SEGMENTS (FOUR CORE BUSINESS TYPES)
    # RICH 5-SECTION CARDS FILLING THE FULL CANVAS (NO GAPS)
    # -------------------------------------------------------------
    s2 = f"""
    <div class="slide slide-template-bg" style="background-image: url('{img_template_slide_b64}');">
      <div class="slide-header">
        <div class="slide-title-group">
          <h1>Target Customer Segments: Four Core Business Types</h1>
          <p>Prioritizing India's 6.3 Crore small businesses based on real field data (Case Appendix A2)</p>
        </div>
        <div class="slide-category-badge">Slide 2 of 7 · Market Strategy</div>
      </div>

      <div class="slide-content">
        <div class="grid-4" style="flex: 1;">
          
          <!-- Segment 1 -->
          <div class="card" style="display: flex; flex-direction: column; justify-content: space-between; padding: 16px 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span class="badge-pill">Segment 1</span>
              <span style="font-size: 12px; font-weight: 800; color: #121316;">55% of MSMEs (3.5 Cr)</span>
            </div>
            <div>
              <div style="font-size: 19px; font-weight: 850; color: #121316; line-height: 1.15;">Kirana & Micro Retail</div>
              <div style="font-size: 12px; color: #5A5A5D; margin-top: 1px;">Grocery shops, salons, pharmacies</div>
            </div>

            <div style="background: #F7F5F0; border-radius: 6px; padding: 9px 10px;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #7A7B7E; letter-spacing: 0.5px; margin-bottom: 3px;">1. Scale & Baseline Setup</div>
              <ul class="bullet-list">
                <li><strong>Staff:</strong> 1–3 employees | ₹1.5L–₹5L monthly sales.</li>
                <li><strong>Footfall:</strong> 120+ daily UPI checkouts & POS taps.</li>
                <li><strong>Current Link:</strong> Owner's 4G mobile hotspot.</li>
                <li><strong>Monthly Spend:</strong> ₹800 on fragmented prepaid SIMs.</li>
              </ul>
            </div>

            <div style="background: #FFF5F5; border-radius: 6px; padding: 9px 10px; border-left: 2.5px solid #E40000;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #E40000; letter-spacing: 0.5px; margin-bottom: 3px;">2. Daily Operational Bleed</div>
              <ul class="bullet-list">
                <li>QR payment timeouts during 7–9 PM peak rush.</li>
                <li>Personal phone flooded with incoming orders.</li>
                <li><strong>Revenue Bleed:</strong> ~₹12,000/mo in lost walkouts.</li>
                <li>Customer dispute delays stall evening billing lines.</li>
              </ul>
            </div>

            <div style="background: #F0F4F8; border-radius: 6px; padding: 9px 10px;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #121316; letter-spacing: 0.5px; margin-bottom: 3px;">3. Included Accel Hardware</div>
              <ul class="bullet-list">
                <li>100 Mbps Fixed Fiber + Dual-Band Wi-Fi 6 Router.</li>
                <li>2x Business CUG SIMs (100GB pooled corporate data).</li>
                <li>Airtel Soundbox with merchant priority QoS queue.</li>
                <li>4-Hour MTTR local technician dispatch commitment.</li>
              </ul>
            </div>

            <div style="background: #FAF8F5; border-radius: 6px; padding: 9px 10px; border: 1px dashed #DDD8CE;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #5A5A5D; margin-bottom: 3px;">4. Regulatory & Onboarding Route</div>
              <ul class="bullet-list">
                <li><strong>100% GST-Exempt:</strong> Annual revenue &lt;₹40 Lakhs.</li>
                <li><strong>Instant Verification:</strong> Udyam certificate auto-match.</li>
                <li><strong>Zero Physical Paperwork:</strong> Mobile Aadhaar KYC.</li>
              </ul>
            </div>

            <div style="background-color: #FAF4F4; border: 1.5px solid #DDD8CE; border-radius: 6px; padding: 10px 12px;">
              <div style="display: flex; justify-content: space-between; align-items: baseline;">
                <span style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #7A7B7E;">Pricing & Terms</span>
                <span style="font-size: 24px; font-weight: 900; color: #121316;">₹1,499 <span style="font-size: 13px; font-weight: 600; color: #5A5A5D;">/mo</span></span>
              </div>
              <div style="font-size: 11.5px; color: #2D2E32; margin-top: 2px;">₹0 Setup Fee Waived · 4h Field MTTR SLA</div>
            </div>
          </div>

          <!-- Segment 2 -->
          <div class="card" style="display: flex; flex-direction: column; justify-content: space-between; padding: 16px 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span class="badge-pill">Segment 2</span>
              <span style="font-size: 12px; font-weight: 800; color: #121316;">25% of MSMEs (1.5 Cr)</span>
            </div>
            <div>
              <div style="font-size: 19px; font-weight: 850; color: #121316; line-height: 1.15;">Clinics & Healthcare</div>
              <div style="font-size: 12px; color: #5A5A5D; margin-top: 1px;">Doctors, path labs, CA chambers</div>
            </div>

            <div style="background: #F7F5F0; border-radius: 6px; padding: 9px 10px;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #7A7B7E; letter-spacing: 0.5px; margin-bottom: 3px;">1. Scale & Baseline Setup</div>
              <ul class="bullet-list">
                <li><strong>Staff:</strong> 5–15 employees | ₹8L–₹25L monthly sales.</li>
                <li><strong>Traffic:</strong> 40+ daily telehealth consults & reports.</li>
                <li><strong>Current Link:</strong> Consumer unmanaged broadband.</li>
                <li><strong>Records:</strong> Free Gmail and shared personal Drive.</li>
              </ul>
            </div>

            <div style="background: #FFF5F5; border-radius: 6px; padding: 9px 10px; border-left: 2.5px solid #E40000;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #E40000; letter-spacing: 0.5px; margin-bottom: 3px;">2. Daily Operational Bleed</div>
              <ul class="bullet-list">
                <li>Video consult drops mid-call on jitter spikes.</li>
                <li>Unencrypted patient records violate ABHA rules.</li>
                <li><strong>Revenue Bleed:</strong> ~₹45,000/mo in lost consults.</li>
                <li>Statutory liability exposure under DPDP health rules.</li>
              </ul>
            </div>

            <div style="background: #F0F4F8; border-radius: 6px; padding: 9px 10px;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #121316; letter-spacing: 0.5px; margin-bottom: 3px;">3. Included Accel Hardware</div>
              <ul class="bullet-list">
                <li>300 Mbps Dedicated Fiber with Static IPv4 address.</li>
                <li>5x Google Workspace business email licenses.</li>
                <li>500GB Airtel Cloud Backup with 4h MTTR SLA.</li>
                <li>Separate guest Wi-Fi network for patient lounge.</li>
              </ul>
            </div>

            <div style="background: #FAF8F5; border-radius: 6px; padding: 9px 10px; border: 1px dashed #DDD8CE;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #5A5A5D; margin-bottom: 3px;">4. Regulatory & Onboarding Route</div>
              <ul class="bullet-list">
                <li><strong>ABHA Compliant:</strong> Static IP for statutory health APIs.</li>
                <li><strong>Data Protection:</strong> DPDP 2023 certified in-memory RAM.</li>
                <li><strong>Single B2B Invoice:</strong> Valid for IT tax depreciation.</li>
              </ul>
            </div>

            <div style="background-color: #FAF4F4; border: 1.5px solid #DDD8CE; border-radius: 6px; padding: 10px 12px;">
              <div style="display: flex; justify-content: space-between; align-items: baseline;">
                <span style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #7A7B7E;">Pricing & Terms</span>
                <span style="font-size: 24px; font-weight: 900; color: #121316;">₹2,499 <span style="font-size: 13px; font-weight: 600; color: #5A5A5D;">/mo</span></span>
              </div>
              <div style="font-size: 11.5px; color: #2D2E32; margin-top: 2px;">Static IP · 99.9% Telehealth Uptime SLA Contract</div>
            </div>
          </div>

          <!-- Segment 3 -->
          <div class="card" style="display: flex; flex-direction: column; justify-content: space-between; padding: 16px 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span class="badge-pill">Segment 3</span>
              <span style="font-size: 12px; font-weight: 800; color: #121316;">15% of MSMEs (90 Lakhs)</span>
            </div>
            <div>
              <div style="font-size: 19px; font-weight: 850; color: #121316; line-height: 1.15;">Multi-Site Chains</div>
              <div style="font-size: 12px; color: #5A5A5D; margin-top: 1px;">3–10 branch retail or restaurants</div>
            </div>

            <div style="background: #F7F5F0; border-radius: 6px; padding: 9px 10px;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #7A7B7E; letter-spacing: 0.5px; margin-bottom: 3px;">1. Scale & Baseline Setup</div>
              <ul class="bullet-list">
                <li><strong>Outlets:</strong> 3–10 stores | ₹30L–₹1.2 Cr combined turnover.</li>
                <li><strong>Workload:</strong> Real-time ERP inventory synchronization.</li>
                <li><strong>Current Link:</strong> Mixed local cable ISPs per store.</li>
                <li><strong>Billing:</strong> 5+ separate physical bills and invoices.</li>
              </ul>
            </div>

            <div style="background: #FFF5F5; border-radius: 6px; padding: 9px 10px; border-left: 2.5px solid #E40000;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #E40000; letter-spacing: 0.5px; margin-bottom: 3px;">2. Daily Operational Bleed</div>
              <ul class="bullet-list">
                <li>POS halts during cable cuts; inventory desyncs.</li>
                <li>Zero central visibility into branch CCTV cameras.</li>
                <li><strong>Revenue Bleed:</strong> ~₹1,20,000/mo in checkout delays.</li>
                <li>Unmonitored stock shrinkage across branch locations.</li>
              </ul>
            </div>

            <div style="background: #F0F4F8; border-radius: 6px; padding: 9px 10px;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #121316; letter-spacing: 0.5px; margin-bottom: 3px;">3. Included Accel Hardware</div>
              <ul class="bullet-list">
                <li>500 Mbps Fiber + 4G LTE Auto-Failover Gateway.</li>
                <li>4-Cam Cloud AI CCTV (30-day offsite archive).</li>
                <li>Centralized SD-WAN portal for multi-store network.</li>
                <li>Single consolidated invoice for corporate tax credit.</li>
              </ul>
            </div>

            <div style="background: #FAF8F5; border-radius: 6px; padding: 9px 10px; border: 1px dashed #DDD8CE;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #5A5A5D; margin-bottom: 3px;">4. Regulatory & Onboarding Route</div>
              <ul class="bullet-list">
                <li><strong>Unified GSTIN Billing:</strong> Multi-branch consolidated input credit.</li>
                <li><strong>Automated Provisioning:</strong> Push-button site deployment.</li>
                <li><strong>HQ Dashboard:</strong> Real-time bandwidth & POS status.</li>
              </ul>
            </div>

            <div style="background-color: #FAF4F4; border: 1.5px solid #DDD8CE; border-radius: 6px; padding: 10px 12px;">
              <div style="display: flex; justify-content: space-between; align-items: baseline;">
                <span style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #7A7B7E;">Pricing & Terms</span>
                <span style="font-size: 24px; font-weight: 900; color: #121316;">₹4,999 <span style="font-size: 13px; font-weight: 600; color: #5A5A5D;">/mo/hub</span></span>
              </div>
              <div style="font-size: 11.5px; color: #2D2E32; margin-top: 2px;">Single Consolidated Bill · Automatic 4G Failover</div>
            </div>
          </div>

          <!-- Segment 4 -->
          <div class="card" style="display: flex; flex-direction: column; justify-content: space-between; padding: 16px 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span class="badge-pill">Segment 4</span>
              <span style="font-size: 12px; font-weight: 800; color: #121316;">5% of MSMEs (30 Lakhs)</span>
            </div>
            <div>
              <div style="font-size: 19px; font-weight: 850; color: #121316; line-height: 1.15;">Light Manufacturing</div>
              <div style="font-size: 12px; color: #5A5A5D; margin-top: 1px;">Auto-parts, textiles, CNC shops</div>
            </div>

            <div style="background: #F7F5F0; border-radius: 6px; padding: 9px 10px;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #7A7B7E; letter-spacing: 0.5px; margin-bottom: 3px;">1. Scale & Baseline Setup</div>
              <ul class="bullet-list">
                <li><strong>Staff:</strong> 25–100 workers | ₹1.5 Cr–₹8 Cr annual sales.</li>
                <li><strong>Tools:</strong> Automated CNC mills & factory PLCs.</li>
                <li><strong>Current Link:</strong> Shared consumer broadband line.</li>
                <li><strong>Security:</strong> Unmanaged routers with default passwords.</li>
              </ul>
            </div>

            <div style="background: #FFF5F5; border-radius: 6px; padding: 9px 10px; border-left: 2.5px solid #E40000;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #E40000; letter-spacing: 0.5px; margin-bottom: 3px;">2. Daily Operational Bleed</div>
              <ul class="bullet-list">
                <li>Latency jitter halts precision CNC cutting tools.</li>
                <li>Zero firewall defense against factory ransomware.</li>
                <li><strong>Revenue Bleed:</strong> ~₹3,50,000/mo in damaged tooling.</li>
                <li>Production downtime halts customer shipment schedules.</li>
              </ul>
            </div>

            <div style="background: #F0F4F8; border-radius: 6px; padding: 9px 10px;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #121316; letter-spacing: 0.5px; margin-bottom: 3px;">3. Included Accel Hardware</div>
              <ul class="bullet-list">
                <li>1 Gbps 1:1 Leased Line with sub-5ms low latency.</li>
                <li>Industrial IoT Box + Cloud Perimeter Firewall.</li>
                <li>Dedicated 24/7 Enterprise Account Manager.</li>
                <li>99.95% Availability SLA with 2-Hour on-site MTTR.</li>
              </ul>
            </div>

            <div style="background: #FAF8F5; border-radius: 6px; padding: 9px 10px; border: 1px dashed #DDD8CE;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #5A5A5D; margin-bottom: 3px;">4. Regulatory & Onboarding Route</div>
              <ul class="bullet-list">
                <li><strong>Mission-Critical SLA:</strong> Financial penalty credit if SLA &lt;99.95%.</li>
                <li><strong>Direct NOC Escalation:</strong> Priority circuit monitoring.</li>
                <li><strong>DoT Security Compliance:</strong> Certified clean-pipe perimeter.</li>
              </ul>
            </div>

            <div style="background-color: #FAF4F4; border: 1.5px solid #DDD8CE; border-radius: 6px; padding: 10px 12px;">
              <div style="display: flex; justify-content: space-between; align-items: baseline;">
                <span style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #7A7B7E;">Pricing & Terms</span>
                <span style="font-size: 24px; font-weight: 900; color: #121316;">₹14,999 <span style="font-size: 13px; font-weight: 600; color: #5A5A5D;">/mo</span></span>
              </div>
              <div style="font-size: 11.5px; color: #2D2E32; margin-top: 2px;">1:1 Leased Line · 99.95% Enterprise SLA with 2h MTTR</div>
            </div>
          </div>

        </div>

        <div class="card-beige" style="padding: 13px 18px; margin-top: 12px; margin-right: 340px;">
          <div style="font-size: 14px; color: #121316; font-weight: 600; line-height: 1.4;">
            <strong style="color: #121316;">Key Market Insight:</strong> Over 80% of Accel Business's addressable volume lies in Kirana stores and local clinics. To capture this segment, Airtel must remove the rigid corporate GST requirement while delivering business-grade SLAs at consumer-friendly prices.
          </div>
        </div>
      </div>

      <div class="slide-footer">
        <div>Airtel Sync 2026 · Digital Track | Project Udyam Digital</div>
        <div class="team-name">Team Neural Nexus · ABV-IIITM Gwalior</div>
        <div class="slide-number">Slide 2 of 7</div>
      </div>
    </div>
    """

    # -------------------------------------------------------------
    # SLIDE 3: THE SOLUTION: 4 READY PACKS & SMART BUDGET MATCHING
    # RICH 5-SECTION PACK CARDS FILLING THE FULL CANVAS (NO GAPS)
    # -------------------------------------------------------------
    s3 = f"""
    <div class="slide slide-template-bg" style="background-image: url('{img_template_slide_b64}');">
      <div class="slide-header">
        <div class="slide-title-group">
          <h1>The Solution: 4 Ready Packs & Smart Budget Matching</h1>
          <p>Turning 25 individual enterprise products into 4 simple, high-converting business bundles</p>
        </div>
        <div class="slide-category-badge">Slide 3 of 7 · Product Strategy</div>
      </div>

      <div class="slide-content">
        <div class="grid-4" style="flex: 1;">
          
          <!-- Pack 1 -->
          <div class="card" style="display: flex; flex-direction: column; justify-content: space-between; padding: 16px 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span class="badge-pill" style="background: #121316; color: #fff;">Kirana & Retail</span>
              <span style="font-size: 11.5px; font-weight: 750; color: #E40000;">Save ₹1,400 Setup</span>
            </div>
            <div>
              <div style="font-size: 20px; font-weight: 900; color: #121316;">Udyam Vyapar</div>
              <div style="font-size: 28px; font-weight: 900; color: #121316; margin-top: 1px;">₹1,499 <span style="font-size: 14px; font-weight: 600; color: #5A5A5D;">/mo</span></div>
              <div style="font-size: 11.5px; color: #5A5A5D;">100% Waived Setup Fee on 12-month plan</div>
            </div>

            <div style="background: #F7F5F0; border-radius: 6px; padding: 9px 10px;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #7A7B7E; letter-spacing: 0.5px; margin-bottom: 3px;">1. Connectivity & Routing</div>
              <ul class="bullet-list">
                <li><strong>100 Mbps Fixed Fiber:</strong> Unlimited symmetric pipe.</li>
                <li><strong>Wi-Fi 6 Router:</strong> Supports 50+ concurrent devices.</li>
                <li><strong>1:1 Contention:</strong> High-priority merchant packet queue.</li>
              </ul>
            </div>

            <div style="background: #F0F4F8; border-radius: 6px; padding: 9px 10px;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #7A7B7E; letter-spacing: 0.5px; margin-bottom: 3px;">2. Mobility & Devices</div>
              <ul class="bullet-list">
                <li><strong>2x Business SIMs:</strong> 100GB pooled corporate CUG data.</li>
                <li><strong>Airtel Soundbox:</strong> Instant voice audio checkouts.</li>
                <li><strong>Auto-Failover Ready:</strong> Optional 4G LTE backup card.</li>
              </ul>
            </div>

            <div style="background: #FFF5F5; border-radius: 6px; padding: 9px 10px; border-left: 2.5px solid #E40000;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #E40000; letter-spacing: 0.5px; margin-bottom: 3px;">3. SLA & Local MTTR</div>
              <ul class="bullet-list">
                <li><strong>4-Hour MTTR:</strong> Rapid local field restoration.</li>
                <li><strong>99.5% Uptime SLA:</strong> Priority merchant support line.</li>
                <li><strong>Dedicated Dispatch:</strong> Nearby field technician hub.</li>
              </ul>
            </div>

            <div style="background: #FAF8F5; border-radius: 6px; padding: 9px 10px; border: 1px dashed #DDD8CE;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #5A5A5D; margin-bottom: 3px;">4. Regulatory & Commercial Terms</div>
              <ul class="bullet-list">
                <li><strong>100% GST-Free:</strong> Legally exempt via Udyam lookup.</li>
                <li><strong>Zero Setup Fee:</strong> ₹1,400 OTC waived on 12-mo plan.</li>
                <li><strong>Digital Mandate:</strong> NPCI AutoPay with single-tap cancel.</li>
              </ul>
            </div>

            <div style="background-color: #FAF4F4; border: 1.5px solid #E40000; border-radius: 6px; padding: 8px 10px; text-align: center; font-size: 11.5px; font-weight: 800; color: #900;">
              ✓ Replaces costly hotspot with business fiber at ₹1,499/mo
            </div>
          </div>

          <!-- Pack 2 -->
          <div class="card" style="display: flex; flex-direction: column; justify-content: space-between; padding: 16px 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span class="badge-pill" style="background: #121316; color: #fff;">Clinics & Labs</span>
              <span style="font-size: 11.5px; font-weight: 750; color: #121316;">ABHA Compliant</span>
            </div>
            <div>
              <div style="font-size: 20px; font-weight: 900; color: #121316;">Udyam Professional</div>
              <div style="font-size: 28px; font-weight: 900; color: #121316; margin-top: 1px;">₹2,499 <span style="font-size: 14px; font-weight: 600; color: #5A5A5D;">/mo</span></div>
              <div style="font-size: 11.5px; color: #5A5A5D;">12-month commercial agreement</div>
            </div>

            <div style="background: #F7F5F0; border-radius: 6px; padding: 9px 10px;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #7A7B7E; letter-spacing: 0.5px; margin-bottom: 3px;">1. Connectivity & Routing</div>
              <ul class="bullet-list">
                <li><strong>300 Mbps Dedicated Fiber:</strong> Zero-jitter consultations.</li>
                <li><strong>Static IPv4 Address:</strong> EMR server & ABHA compliant.</li>
                <li><strong>Wi-Fi 6 Gateway:</strong> Isolated patient waiting lounge SSID.</li>
              </ul>
            </div>

            <div style="background: #F0F4F8; border-radius: 6px; padding: 9px 10px;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #7A7B7E; letter-spacing: 0.5px; margin-bottom: 3px;">2. Productivity & Backup</div>
              <ul class="bullet-list">
                <li><strong>5x Google Workspace:</strong> Branded clinic emails & Drive.</li>
                <li><strong>500GB Airtel Cloud:</strong> Automated encrypted backups.</li>
                <li><strong>Sub-5ms Telehealth SLA:</strong> Lag-free HD video feeds.</li>
              </ul>
            </div>

            <div style="background: #FFF5F5; border-radius: 6px; padding: 9px 10px; border-left: 2.5px solid #E40000;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #E40000; letter-spacing: 0.5px; margin-bottom: 3px;">3. SLA & Local MTTR</div>
              <ul class="bullet-list">
                <li><strong>4-Hour MTTR SLA:</strong> Dedicated medical escalation desk.</li>
                <li><strong>99.9% Availability:</strong> Contractual uptime SLA.</li>
                <li><strong>Active Circuit Monitoring:</strong> Proactive fiber cut alerts.</li>
              </ul>
            </div>

            <div style="background: #FAF8F5; border-radius: 6px; padding: 9px 10px; border: 1px dashed #DDD8CE;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #5A5A5D; margin-bottom: 3px;">4. Regulatory & Commercial Terms</div>
              <ul class="bullet-list">
                <li><strong>ABHA & DPDP 2023:</strong> Full statutory patient data defense.</li>
                <li><strong>Tax Invoice:</strong> 18% GST input credit deduction.</li>
                <li><strong>Zero Setup Fee:</strong> ₹2,500 OTC waived on annual agreement.</li>
              </ul>
            </div>

            <div style="background-color: #FAF4F4; border: 1.5px solid #E40000; border-radius: 6px; padding: 8px 10px; text-align: center; font-size: 11.5px; font-weight: 800; color: #900;">
              ✓ Guaranteed 99.9% SLA & static IP for ABHA compliance
            </div>
          </div>

          <!-- Pack 3 -->
          <div class="card" style="display: flex; flex-direction: column; justify-content: space-between; padding: 16px 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span class="badge-pill" style="background: #121316; color: #fff;">Multi-Store Chains</span>
              <span style="font-size: 11.5px; font-weight: 750; color: #121316;">SD-WAN Managed</span>
            </div>
            <div>
              <div style="font-size: 20px; font-weight: 900; color: #121316;">Udyam Multi-Site</div>
              <div style="font-size: 28px; font-weight: 900; color: #121316; margin-top: 1px;">₹4,999 <span style="font-size: 14px; font-weight: 600; color: #5A5A5D;">/mo/hub</span></div>
              <div style="font-size: 11.5px; color: #5A5A5D;">Multi-location single consolidated invoice</div>
            </div>

            <div style="background: #F7F5F0; border-radius: 6px; padding: 9px 10px;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #7A7B7E; letter-spacing: 0.5px; margin-bottom: 3px;">1. Connectivity & Routing</div>
              <ul class="bullet-list">
                <li><strong>500 Mbps Fixed Fiber:</strong> Unlimited high-speed pipe.</li>
                <li><strong>4G LTE Auto-Failover:</strong> &lt;2 second cutover gateway.</li>
                <li><strong>Central SD-WAN:</strong> Unified routing across stores.</li>
              </ul>
            </div>

            <div style="background: #F0F4F8; border-radius: 6px; padding: 9px 10px;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #7A7B7E; letter-spacing: 0.5px; margin-bottom: 3px;">2. Security & Surveillance</div>
              <ul class="bullet-list">
                <li><strong>4-Cam Cloud AI CCTV:</strong> 30-day offsite archive.</li>
                <li><strong>Central Cloud Portal:</strong> Live view of all branches.</li>
                <li><strong>Shrinkage Alerts:</strong> Motion AI alerts after store close.</li>
              </ul>
            </div>

            <div style="background: #FFF5F5; border-radius: 6px; padding: 9px 10px; border-left: 2.5px solid #E40000;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #E40000; letter-spacing: 0.5px; margin-bottom: 3px;">3. SLA & Local MTTR</div>
              <ul class="bullet-list">
                <li><strong>2-Hour MTTR SLA:</strong> Fast on-site technician response.</li>
                <li><strong>99.9% Network Uptime:</strong> High-availability failover.</li>
                <li><strong>Zero POS Outages:</strong> Unbroken card checkout flow.</li>
              </ul>
            </div>

            <div style="background: #FAF8F5; border-radius: 6px; padding: 9px 10px; border: 1px dashed #DDD8CE;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #5A5A5D; margin-bottom: 3px;">4. Regulatory & Commercial Terms</div>
              <ul class="bullet-list">
                <li><strong>Single B2B Bill:</strong> Replaces 5+ fragmented local ISPs.</li>
                <li><strong>10% Multi-Site Discount:</strong> Automatically applied in CPQ.</li>
                <li><strong>Full GST Credit:</strong> Automated corporate tax deduction.</li>
              </ul>
            </div>

            <div style="background-color: #FAF4F4; border: 1.5px solid #E40000; border-radius: 6px; padding: 8px 10px; text-align: center; font-size: 11.5px; font-weight: 800; color: #900;">
              ✓ Replaces 5+ local ISPs with 4G failover & single bill
            </div>
          </div>

          <!-- Pack 4 -->
          <div class="card" style="display: flex; flex-direction: column; justify-content: space-between; padding: 16px 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span class="badge-pill" style="background: #121316; color: #fff;">Manufacturing</span>
              <span style="font-size: 11.5px; font-weight: 750; color: #121316;">Mission-Critical</span>
            </div>
            <div>
              <div style="font-size: 20px; font-weight: 900; color: #121316;">Udyam Industrial</div>
              <div style="font-size: 28px; font-weight: 900; color: #121316; margin-top: 1px;">₹14,999 <span style="font-size: 14px; font-weight: 600; color: #5A5A5D;">/mo</span></div>
              <div style="font-size: 11.5px; color: #5A5A5D;">Enterprise SLA contract with dedicated RM</div>
            </div>

            <div style="background: #F7F5F0; border-radius: 6px; padding: 9px 10px;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #7A7B7E; letter-spacing: 0.5px; margin-bottom: 3px;">1. Connectivity & Routing</div>
              <ul class="bullet-list">
                <li><strong>1 Gbps 1:1 Leased Line:</strong> Symmetric low-jitter pipe.</li>
                <li><strong>Sub-5ms Latency:</strong> Hardware-level packet priority.</li>
                <li><strong>Industrial IoT Box:</strong> Modbus/PLC telemetry bridge.</li>
              </ul>
            </div>

            <div style="background: #F0F4F8; border-radius: 6px; padding: 9px 10px;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #7A7B7E; letter-spacing: 0.5px; margin-bottom: 3px;">2. Security & Cyber Defense</div>
              <ul class="bullet-list">
                <li><strong>Perimeter Cloud Firewall:</strong> Layer-7 cyber protection.</li>
                <li><strong>Anti-DDoS Shield:</strong> Real-time automated scrubbing.</li>
                <li><strong>Dedicated NOC Team:</strong> Direct line to senior engineers.</li>
              </ul>
            </div>

            <div style="background: #FFF5F5; border-radius: 6px; padding: 9px 10px; border-left: 2.5px solid #E40000;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #E40000; letter-spacing: 0.5px; margin-bottom: 3px;">3. SLA & Local MTTR</div>
              <ul class="bullet-list">
                <li><strong>99.95% Availability SLA:</strong> Financial penalty credit.</li>
                <li><strong>2-Hour MTTR SLA:</strong> Priority on-site technician dispatch.</li>
                <li><strong>Zero CNC Halts:</strong> Rock-solid automated production.</li>
              </ul>
            </div>

            <div style="background: #FAF8F5; border-radius: 6px; padding: 9px 10px; border: 1px dashed #DDD8CE;">
              <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #5A5A5D; margin-bottom: 3px;">4. Regulatory & Commercial Terms</div>
              <ul class="bullet-list">
                <li><strong>Custom SLA Contract:</strong> DoT enterprise leased line rules.</li>
                <li><strong>Dedicated RM:</strong> Single point of contact for billing.</li>
                <li><strong>15% Volume Discount:</strong> Built into 12-month CPQ solver.</li>
              </ul>
            </div>

            <div style="background-color: #FAF4F4; border: 1.5px solid #E40000; border-radius: 6px; padding: 8px 10px; text-align: center; font-size: 11.5px; font-weight: 800; color: #900;">
              ✓ 1:1 Leased Line with sub-5ms low latency for CNC mills
            </div>
          </div>

        </div>

        <div class="card-beige" style="padding: 13px 18px; margin-top: 12px; margin-right: 340px;">
          <div style="display: grid; grid-template-columns: 1.2fr 1fr; gap: 18px; align-items: center;">
            <div>
              <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 3px;">
                <span class="badge-pill" style="background: #121316; color: #fff;">Reverse Budget Solver</span>
                <span style="font-size: 14.5px; font-weight: 850; color: #121316;">"Mera Budget ₹X Hai" (Instant Math Matching)</span>
              </div>
              <div style="font-size: 13px; color: #4A4B4E; line-height: 1.4;">
                Instead of forcing a shop owner to browse 25 technical products, they simply enter their monthly budget (e.g. ₹2,500). Our branch-and-bound solver tests all valid product combinations in <strong>under 0.5 milliseconds</strong>, guaranteeing the best possible bundle with zero human error.
              </div>
            </div>

            <div style="font-size: 12.5px; color: #2D2E32; line-height: 1.4; border-left: 2px solid #DDD8CE; padding-left: 16px;">
              <strong style="color: #121316;">Commercial Discount Policy Built In:</strong>
              <div style="margin-top: 2px;">• <strong>Multi-Product Discount:</strong> 5% off for 2 categories, 10% for 3, 15% for 4+.</div>
              <div>• <strong>Setup Fee Waiver:</strong> 100% setup fee waived on 12-month plans (₹0 upfront).</div>
              <div>• <strong>GST Input Credit:</strong> Automatic 18% GST tax deduction calculated for registered firms.</div>
              <div>• <strong>0% Mis-Sell Guarantee:</strong> CPQ DAG solver eliminates the 15.2% legacy rule violations.</div>
            </div>
          </div>
        </div>

      </div>

      <div class="slide-footer">
        <div>Airtel Sync 2026 · Digital Track | Project Udyam Digital</div>
        <div class="team-name">Team Neural Nexus · ABV-IIITM Gwalior</div>
        <div class="slide-number">Slide 3 of 7</div>
      </div>
    </div>
    """

    # -------------------------------------------------------------
        # -------------------------------------------------------------
        # -------------------------------------------------------------
        # -------------------------------------------------------------
        # -------------------------------------------------------------
    # SLIDE 4: SYSTEM ARCHITECTURE
    # -------------------------------------------------------------
    s4 = f"""
    <div class="slide slide-template-bg" style="background-image: url('{img_template_slide_b64}');">
      <div class="slide-header" style="margin-left: 175px; margin-right: 175px; border-bottom: 2px solid #EFECE6; padding-bottom: 8px; margin-bottom: 10px; min-height: 80px;">
        <div class="slide-title-group">
          <h1>System Architecture: The 4-Step Acquisition Pipeline</h1>
          <p>Four-stage deterministic acquisition, pricing, verification &amp; fulfillment topology</p>
        </div>
        <div class="slide-category-badge">Slide 4 of 7 · System Architecture</div>
      </div>

      <div class="slide-content" style="display: flex; flex-direction: column; justify-content: space-between; flex: 1; gap: 8px;">
        
        <!-- PIPELINE FLOW INDICATOR -->
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; width: 100%;">
          <div style="background: #E40000; color: #FFFFFF; padding: 5px 12px; border-radius: 4px; font-size: 11.5px; font-weight: 850; text-align: center; text-transform: uppercase; letter-spacing: 0.5px;">
            Stage 1: Discovery &amp; Ingress ➔
          </div>
          <div style="background: #121316; color: #FFFFFF; padding: 5px 12px; border-radius: 4px; font-size: 11.5px; font-weight: 850; text-align: center; text-transform: uppercase; letter-spacing: 0.5px;">
            Stage 2: CPQ Constraint Engine ➔
          </div>
          <div style="background: #E40000; color: #FFFFFF; padding: 5px 12px; border-radius: 4px; font-size: 11.5px; font-weight: 850; text-align: center; text-transform: uppercase; letter-spacing: 0.5px;">
            Stage 3: DPDP KYC Gate ➔
          </div>
          <div style="background: #121316; color: #FFFFFF; padding: 5px 12px; border-radius: 4px; font-size: 11.5px; font-weight: 850; text-align: center; text-transform: uppercase; letter-spacing: 0.5px;">
            Stage 4: Fulfillment &amp; Active SLA ✔
          </div>
        </div>

        <!-- 4-STAGE ARCHITECTURE CARDS (PACKED EDGE-TO-EDGE, EQUAL-FLEX BLOCKS) -->
        <div class="grid-4" style="gap: 14px; flex: 1; width: 100%; align-items: stretch;">
          
          <!-- STAGE 1: DISCOVERY & ADVISOR -->
          <div class="card" style="display: flex; flex-direction: column; justify-content: space-between; padding: 14px 14px; border-top: 4px solid #E40000; background: #FFFFFF; height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
              <span style="background: #E40000; color: #FFFFFF; font-size: 11px; font-weight: 850; padding: 2px 7px; border-radius: 4px;">STAGE 1</span>
              <span style="font-size: 11px; font-weight: 750; color: #E40000; background: rgba(228,0,0,0.08); padding: 2px 6px; border-radius: 4px;">&lt;50ms Fast-Path</span>
            </div>
            <div style="margin-bottom: 6px;">
              <div style="font-size: 16px; font-weight: 850; color: #121316; line-height: 1.2;">Discovery &amp; Advisor</div>
              <div style="font-size: 11.5px; color: #6E6F73; font-weight: 600;">Universal Indic Ingress &amp; Slot Extraction</div>
            </div>

            <div style="display: flex; flex-direction: column; flex: 1; justify-content: space-between; gap: 8px;">
              <!-- Block 1 -->
              <div style="background: #FAF8F5; border: 1.5px solid #EFECE6; border-radius: 6px; padding: 10px 12px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 12px; font-weight: 850; color: #E40000; text-transform: uppercase; margin-bottom: 3px;">1. Ingress Channels &amp; Voice</div>
                <div style="font-size: 12px; color: #2C2D30; line-height: 1.4;">
                  • <strong>Mobile PWA &amp; Phygital QR:</strong> Zero-friction camera scan entry.<br>
                  • <strong>Indic Web Speech:</strong> Low-latency voice-to-text input stream.<br>
                  • <strong>Dual Narration:</strong> Markdown text + browser TTS audio.
                </div>
              </div>

              <!-- Block 2 -->
              <div style="background: #FAF8F5; border: 1.5px solid #EFECE6; border-radius: 6px; padding: 10px 12px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 12px; font-weight: 850; color: #121316; text-transform: uppercase; margin-bottom: 3px;">2. Multilingual NLP Engine</div>
                <div style="font-size: 12px; color: #2C2D30; line-height: 1.4;">
                  • <strong>10+ Languages:</strong> Native te, ta, bn, gu, mr, kn, ml, or, hi, en.<br>
                  • <strong>Session Inertia:</strong> User-turn isolation traps language flip.<br>
                  • <strong>Script Toggle:</strong> Romanized English &lt;-&gt; Native script switch.
                </div>
              </div>

              <!-- Block 3 -->
              <div style="background: #FAF8F5; border: 1.5px solid #EFECE6; border-radius: 6px; padding: 10px 12px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 12px; font-weight: 850; color: #121316; text-transform: uppercase; margin-bottom: 3px;">3. Cascaded Entity Extractor</div>
                <div style="font-size: 12px; color: #2C2D30; line-height: 1.4;">
                  • <strong>Slot Parser:</strong> Extracts business segment, city tier, headcount.<br>
                  • <strong>Budget Isolation:</strong> Detects spending limits &amp; site count.<br>
                  • <strong>Zero Cold-Start:</strong> Instant query bar response in &lt;50ms.
                </div>
              </div>

              <!-- Block 4 -->
              <div style="background: #FAF8F5; border: 1.5px solid #EFECE6; border-radius: 6px; padding: 10px 12px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 12px; font-weight: 850; color: #121316; text-transform: uppercase; margin-bottom: 3px;">4. Interface Hand-off &amp; State</div>
                <div style="font-size: 12px; color: #2C2D30; line-height: 1.4;">
                  • <strong>Pydantic v2 Schema:</strong> Strict JSON tool-call validation.<br>
                  • <strong>FastAPI Async Bus:</strong> Non-blocking state pipeline sync.<br>
                  • <strong>Telemetry:</strong> Live session tracking &amp; drop-off triggers.
                </div>
              </div>
            </div>

            <!-- Footer Badge -->
            <div style="margin-top: 8px; background: rgba(228,0,0,0.06); border: 1px solid rgba(228,0,0,0.2); border-radius: 4px; padding: 7px 10px; font-size: 11.5px; color: #E40000; font-weight: 750; text-align: center;">
              Zero initial delay · &lt;50ms fast-path greeting
            </div>
          </div>

          <!-- STAGE 2: CPQ DAG CONSTRAINT ENGINE -->
          <div class="card" style="display: flex; flex-direction: column; justify-content: space-between; padding: 14px 14px; border-top: 4px solid #121316; background: #FFFFFF; height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
              <span style="background: #121316; color: #FFFFFF; font-size: 11px; font-weight: 850; padding: 2px 7px; border-radius: 4px;">STAGE 2</span>
              <span style="font-size: 11px; font-weight: 750; color: #121316; background: rgba(0,0,0,0.06); padding: 2px 6px; border-radius: 4px;">&lt;0.5ms Solver</span>
            </div>
            <div style="margin-bottom: 6px;">
              <div style="font-size: 16px; font-weight: 850; color: #121316; line-height: 1.2;">Deterministic CPQ DAG</div>
              <div style="font-size: 11.5px; color: #6E6F73; font-weight: 600;">Constraint Solver &amp; Reverse Optimizer</div>
            </div>

            <div style="display: flex; flex-direction: column; flex: 1; justify-content: space-between; gap: 8px;">
              <!-- Block 1 -->
              <div style="background: #FAF8F5; border: 1.5px solid #EFECE6; border-radius: 6px; padding: 10px 12px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 12px; font-weight: 850; color: #121316; text-transform: uppercase; margin-bottom: 3px;">1. Symbolic DAG Engine</div>
                <div style="font-size: 12px; color: #2C2D30; line-height: 1.4;">
                  • <strong>DAG Validator:</strong> Checks <code>requires_one_of</code> in microsecond.<br>
                  • <strong>Hard GST Firewall:</strong> Blocks GST SKUs for non-GST firms.<br>
                  • <strong>Zero Mis-Sell:</strong> Mathematical compatibility guarantee.
                </div>
              </div>

              <!-- Block 2 -->
              <div style="background: #FAF8F5; border: 1.5px solid #EFECE6; border-radius: 6px; padding: 10px 12px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 12px; font-weight: 850; color: #121316; text-transform: uppercase; margin-bottom: 3px;">2. Multi-Tier Bundling</div>
                <div style="font-size: 12px; color: #2C2D30; line-height: 1.4;">
                  • <strong>Commercial Tiers:</strong> 5% (2 cats), 10% (3 cats), 15% (4+ cats).<br>
                  • <strong>Setup Waiver:</strong> 100% OTC fee waiver on &gt;=12mo tenure.<br>
                  • <strong>Gross Margin:</strong> Automated discount keeps &gt;60% margin.
                </div>
              </div>

              <!-- Block 3 -->
              <div style="background: #FAF8F5; border: 1.5px solid #EFECE6; border-radius: 6px; padding: 10px 12px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 12px; font-weight: 850; color: #121316; text-transform: uppercase; margin-bottom: 3px;">3. "Mera Budget" Optimizer</div>
                <div style="font-size: 12px; color: #2C2D30; line-height: 1.4;">
                  • <strong>Branch-and-Bound:</strong> Max bandwidth under spend cap.<br>
                  • <strong>Dynamic Recalculation:</strong> Updates cart in &lt;1ms on slide.<br>
                  • <strong>SLA Guarantee:</strong> Real-time delivery timeline calculation.
                </div>
              </div>

              <!-- Block 4 -->
              <div style="background: #FAF8F5; border: 1.5px solid #EFECE6; border-radius: 6px; padding: 10px 12px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 12px; font-weight: 850; color: #121316; text-transform: uppercase; margin-bottom: 3px;">4. Catalogue Engine</div>
                <div style="font-size: 12px; color: #2C2D30; line-height: 1.4;">
                  • <strong>25 Enterprise SKUs:</strong> Fiber, Leased Line, 4G, CCTV, Wi-Fi.<br>
                  • <strong>Zero Stubs:</strong> 100% mathematical constraint graph.<br>
                  • <strong>Locking:</strong> Cryptographic quote hash locks terms for 30d.
                </div>
              </div>
            </div>

            <!-- Footer Badge -->
            <div style="margin-top: 8px; background: #FAF8F5; border: 1px solid #EFECE6; border-radius: 4px; padding: 7px 10px; font-size: 11.5px; color: #5A5A5D; font-weight: 750; text-align: center;">
              Mathematical optimality · Zero manual sales delay
            </div>
          </div>

          <!-- STAGE 3: DPDP SMART KYC GATE -->
          <div class="card" style="display: flex; flex-direction: column; justify-content: space-between; padding: 14px 14px; border-top: 4px solid #E40000; background: #FFFFFF; height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
              <span style="background: #E40000; color: #FFFFFF; font-size: 11px; font-weight: 850; padding: 2px 7px; border-radius: 4px;">STAGE 3</span>
              <span style="font-size: 11px; font-weight: 750; color: #0072FF; background: rgba(0,114,255,0.08); padding: 2px 6px; border-radius: 4px;">DPDP Compliant</span>
            </div>
            <div style="margin-bottom: 6px;">
              <div style="font-size: 16px; font-weight: 850; color: #121316; line-height: 1.2;">DPDP Smart KYC Gate</div>
              <div style="font-size: 11.5px; color: #6E6F73; font-weight: 600;">In-Memory Privacy &amp; Anomaly Trapping</div>
            </div>

            <div style="display: flex; flex-direction: column; flex: 1; justify-content: space-between; gap: 8px;">
              <!-- Block 1 -->
              <div style="background: #FAF8F5; border: 1.5px solid #EFECE6; border-radius: 6px; padding: 10px 12px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 12px; font-weight: 850; color: #E40000; text-transform: uppercase; margin-bottom: 3px;">1. DPDP Privacy Shield</div>
                <div style="font-size: 12px; color: #2C2D30; line-height: 1.4;">
                  • <strong>Section 6 Consent:</strong> Explicit digital consent + SHA-256.<br>
                  • <strong>In-Memory Masking:</strong> 12-digit UID masked in RAM.<br>
                  • <strong>Zero Persistence:</strong> Unredacted UID never hits disk/DB.
                </div>
              </div>

              <!-- Block 2 -->
              <div style="background: #FAF8F5; border: 1.5px solid #EFECE6; border-radius: 6px; padding: 10px 12px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 12px; font-weight: 850; color: #121316; text-transform: uppercase; margin-bottom: 3px;">2. Registry Verification</div>
                <div style="font-size: 12px; color: #2C2D30; line-height: 1.4;">
                  • <strong>GSTIN Registry:</strong> O(1) lookup across 3,534 records.<br>
                  • <strong>Udyam Registry:</strong> Instant lookup across 2,723 records.<br>
                  • <strong>Non-GST Bridge:</strong> Onboards micro-firms with Udyam.
                </div>
              </div>

              <!-- Block 3 -->
              <div style="background: #FAF8F5; border: 1.5px solid #EFECE6; border-radius: 6px; padding: 10px 12px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 12px; font-weight: 850; color: #121316; text-transform: uppercase; margin-bottom: 3px;">3. Adversarial Anomaly Traps</div>
                <div style="font-size: 12px; color: #2C2D30; line-height: 1.4;">
                  • <strong>RapidFuzz Match:</strong> Traps planted name defects (K07).<br>
                  • <strong>Status Verifier:</strong> Rejects Cancelled GSTINs (K01).<br>
                  • <strong>Doc Completeness:</strong> Traps Missing Udyam (K05).
                </div>
              </div>

              <!-- Block 4 -->
              <div style="background: #FAF8F5; border: 1.5px solid #EFECE6; border-radius: 6px; padding: 10px 12px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 12px; font-weight: 850; color: #121316; text-transform: uppercase; margin-bottom: 3px;">4. Freshness Validation</div>
                <div style="font-size: 12px; color: #2C2D30; line-height: 1.4;">
                  • <strong>Evaluation Anchor:</strong> Anchored to 2026-07-15.<br>
                  • <strong>Stale Bill Trap:</strong> Rejects bills &gt;90 days old (K11).<br>
                  • <strong>Audit Ledger:</strong> Tamper-evident verification logs.
                </div>
              </div>
            </div>

            <!-- Footer Badge -->
            <div style="margin-top: 8px; background: rgba(0,114,255,0.06); border: 1px solid rgba(0,114,255,0.25); border-radius: 4px; padding: 7px 10px; font-size: 11.5px; color: #0072FF; font-weight: 750; text-align: center;">
              DPDP Act 2023 Zero-Persistence Architecture
            </div>
          </div>

          <!-- STAGE 4: FULFILLMENT & RESCUE -->
          <div class="card" style="display: flex; flex-direction: column; justify-content: space-between; padding: 14px 14px; border-top: 4px solid #121316; background: #FFFFFF; height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
              <span style="background: #121316; color: #FFFFFF; font-size: 11px; font-weight: 850; padding: 2px 7px; border-radius: 4px;">STAGE 4</span>
              <span style="font-size: 11px; font-weight: 750; color: #121316; background: rgba(0,0,0,0.06); padding: 2px 6px; border-radius: 4px;">17.6d -&gt; 3.8d</span>
            </div>
            <div style="margin-bottom: 6px;">
              <div style="font-size: 16px; font-weight: 850; color: #121316; line-height: 1.2;">Fulfillment &amp; Rescue</div>
              <div style="font-size: 11.5px; color: #6E6F73; font-weight: 600;">6-Stage Tracker &amp; Machine Learning</div>
            </div>

            <div style="display: flex; flex-direction: column; flex: 1; justify-content: space-between; gap: 8px;">
              <!-- Block 1 -->
              <div style="background: #FAF8F5; border: 1.5px solid #EFECE6; border-radius: 6px; padding: 10px 12px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 12px; font-weight: 850; color: #121316; text-transform: uppercase; margin-bottom: 3px;">1. 6-Stage Lifecycle</div>
                <div style="font-size: 12px; color: #2C2D30; line-height: 1.4;">
                  • <strong>Sequential Stages:</strong> Order ➔ KYC ➔ Feas ➔ CPE ➔ Tech ➔ Live.<br>
                  • <strong>SLA Compression:</strong> Shrinks 17.6-day delay to 3.8 days.<br>
                  • <strong>Digital Stamping:</strong> Instant agreement counter-signing.
                </div>
              </div>

              <!-- Block 2 -->
              <div style="background: #FAF8F5; border: 1.5px solid #EFECE6; border-radius: 6px; padding: 10px 12px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 12px; font-weight: 850; color: #121316; text-transform: uppercase; margin-bottom: 3px;">2. Logistics &amp; Field Tech</div>
                <div style="font-size: 12px; color: #2C2D30; line-height: 1.4;">
                  • <strong>BlueDart AWB Sync:</strong> Live CPE hardware tracking.<br>
                  • <strong>Field Tech Dispatch:</strong> Real-time tech assignment + OTP.<br>
                  • <strong>Zero Chase Calls:</strong> Status transparency ends inbound calls.
                </div>
              </div>

              <!-- Block 3 -->
              <div style="background: #FAF8F5; border: 1.5px solid #EFECE6; border-radius: 6px; padding: 10px 12px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 12px; font-weight: 850; color: #121316; text-transform: uppercase; margin-bottom: 3px;">3. Instant NPCI UPI QR</div>
                <div style="font-size: 12px; color: #2C2D30; line-height: 1.4;">
                  • <strong>Dynamic QR:</strong> Exact quote amount locked with UTR sync.<br>
                  • <strong>Razorpay Webhooks:</strong> Auto-advances order to Stage 2.<br>
                  • <strong>Partner Split:</strong> 15% instant commission allocation.
                </div>
              </div>

              <!-- Block 4 -->
              <div style="background: #FAF8F5; border: 1.5px solid #EFECE6; border-radius: 6px; padding: 10px 12px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 12px; font-weight: 850; color: #121316; text-transform: uppercase; margin-bottom: 3px;">4. Meta WhatsApp API</div>
                <div style="font-size: 12px; color: #2C2D30; line-height: 1.4;">
                  • <strong>Proactive Push:</strong> Milestones delivered to phone directly.<br>
                  • <strong>Security OTP:</strong> Automated installation code dispatch.<br>
                  • <strong>Live Link:</strong> One-tap live order tracking URL.
                </div>
              </div>
            </div>

            <!-- Footer Badge -->
            <div style="margin-top: 8px; background: #FAF8F5; border: 1px solid #EFECE6; border-radius: 4px; padding: 7px 10px; font-size: 11.5px; color: #5A5A5D; font-weight: 750; text-align: center;">
              Zero inbound chase calls · Proactive SLA delivery
            </div>
          </div>

        </div>

        <!-- FULL-WIDTH CLOSED-LOOP RECOVERY BANNER (AT THE BOTTOM OF ARCHITECTURE) -->
        <div style="background: rgba(228,0,0,0.06); border: 1.5px dashed #E40000; border-radius: 6px; padding: 10px 16px; display: flex; align-items: center; justify-content: space-between; width: 100%;">
          <div style="display: flex; align-items: center; gap: 12px;">
            <span style="background: #E40000; color: #FFFFFF; font-size: 11px; font-weight: 850; padding: 3px 8px; border-radius: 4px; text-transform: uppercase; white-space: nowrap;">Closed-Loop ML Recovery</span>
            <span style="font-size: 12.5px; color: #121316; font-weight: 750; line-height: 1.3;">
              <strong>LightGBM NBA Rescue Loop:</strong> Automatically identifies the 56.4% quote drop-off cohort and triggers personalized WhatsApp recovery drawers with 1-click pre-hydrated carts.
            </span>
          </div>
          <span style="font-size: 11.5px; font-weight: 850; color: #E40000; background: #FFFFFF; padding: 4px 10px; border-radius: 4px; border: 1px solid rgba(228,0,0,0.25); white-space: nowrap; margin-left: 12px;">
            Stops ₹15,000 CAC Bleed
          </span>
        </div>

      </div>

      <div class="slide-footer">
        <div>Airtel Sync 2026 · Digital Track | Project Udyam Digital</div>
        <div class="team-name">Team Neural Nexus · ABV-IIITM Gwalior</div>
        <div class="slide-number">Slide 4 of 7</div>
      </div>
    </div>
    """

    # -------------------------------------------------------------
    # SLIDE 5: WORKING PROTOTYPE: LIVE SOFTWARE WALKTHROUGH
    # -------------------------------------------------------------
    s5 = f"""
    <div class="slide slide-template-bg" style="background-image: url('{img_template_slide_b64}');">
      <div class="slide-header">
        <div class="slide-title-group">
          <h1>Working Prototype: Live Software Walkthrough</h1>
          <p>Live software walkthrough across all 4 production modules on airtel.hrushikeshramilla.in</p>
        </div>
        <div class="slide-category-badge">Slide 5 of 7 · Product Demonstration</div>
      </div>

            <div class="slide-content">
        <div class="grid-2" style="flex: 1; gap: 14px;">
          
          <!-- BOX 1: ADVISOR -->
          <div class="card" style="display: flex; flex-direction: column; justify-content: space-between; padding: 14px 16px;">
            <div>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-size: 15px; font-weight: 850; color: #121316;">1. Multilingual Natural Language Advisor</span>
                <span class="badge-pill">Universal Multilingual AI</span>
              </div>
              <div style="background: #0D0E12; border-radius: 6px; overflow: hidden; height: 285px; display: flex; align-items: center; justify-content: center; border: 1px solid #DDD8CE;">
                <img src="{img_screen_advisor_b64}" style="max-height: 100%; max-width: 100%; object-fit: contain;" alt="Multilingual Advisor">
              </div>
            </div>
            <div style="font-size: 13px; color: #4A4B4E; margin-top: 6px; line-height: 1.35;">
              Shop owners converse in any language (English, Hindi, Telugu, Tamil, etc.). Session Language Inertia preserves conversation continuity without false language flipping.
            </div>
          </div>

          <!-- BOX 2: SMART KYC GATE -->
          <div class="card" style="display: flex; flex-direction: column; justify-content: space-between; padding: 14px 16px;">
            <div>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-size: 15px; font-weight: 850; color: #121316;">2. DPDP Smart KYC Verification Gate</span>
                <span class="badge-pill">DPDP Act 2023 · In-Memory</span>
              </div>
              <div style="background: #0D0E12; border-radius: 6px; overflow: hidden; height: 285px; display: flex; align-items: center; justify-content: center; border: 1px solid #DDD8CE;">
                <img src="{img_screen_kyc_b64}" style="max-height: 100%; max-width: 100%; object-fit: contain;" alt="DPDP Smart KYC Verification Gate">
              </div>
            </div>
            <div style="font-size: 13px; color: #4A4B4E; margin-top: 6px; line-height: 1.35;">
              Instant 4-slot statutory verification against GST and Udyam registries. Redacts 12-digit national IDs to XXXX-XXXX-1234 in volatile RAM with zero disk persistence.
            </div>
          </div>

          <!-- BOX 3: 6-STAGE FULFILLMENT & WHATSAPP HOOKS -->
          <div class="card" style="display: flex; flex-direction: column; justify-content: space-between; padding: 14px 16px;">
            <div>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-size: 15px; font-weight: 850; color: #121316;">3. 6-Stage SLA Fulfillment &amp; WhatsApp Hooks</span>
                <span class="badge-pill">Zero Chase Calls · Meta API</span>
              </div>
              <div style="background: #0D0E12; border-radius: 6px; overflow: hidden; height: 285px; display: flex; align-items: center; justify-content: center; border: 1px solid #DDD8CE;">
                <img src="{img_screen_fulfillment_b64}" style="max-height: 100%; max-width: 100%; object-fit: contain;" alt="6-Stage SLA Fulfillment">
              </div>
            </div>
            <div style="font-size: 13px; color: #4A4B4E; margin-top: 6px; line-height: 1.35;">
              End-to-end transparency compresses 17.6-day delays to 3.8 days. Proactive Meta WhatsApp API hooks push real-time technician assignment and OTP tracking directly to merchants.
            </div>
          </div>

          <!-- BOX 4: PARTNER CONSOLE & RESCUE -->
          <div class="card" style="display: flex; flex-direction: column; justify-content: space-between; padding: 14px 16px;">
            <div>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-size: 15px; font-weight: 850; color: #121316;">4. Partner Console &amp; Autonomous Lead Rescue</span>
                <span class="badge-pill">LightGBM ML · ₹21.8L ARR</span>
              </div>
              <div style="background: #0D0E12; border-radius: 6px; overflow: hidden; height: 285px; display: flex; align-items: center; justify-content: center; border: 1px solid #DDD8CE;">
                <img src="{img_screen_tracker_b64}" style="max-height: 100%; max-width: 100%; object-fit: contain;" alt="Partner Lead Rescue Console">
              </div>
            </div>
            <div style="font-size: 13px; color: #4A4B4E; margin-top: 6px; line-height: 1.35;">
              Partner ops console powered by LightGBM calibrated propensity scoring across 5,000 leads. Recovers the 56.4% quote drop-off cohort via 1-click WhatsApp winback at ₹350 marginal CAC.
            </div>
          </div>

        </div>

        <div class="card-beige" style="padding: 10px 18px; margin-top: 12px; width: 100%;">
          <div style="font-size: 13.5px; color: #121316; font-weight: 750; display: flex; justify-content: space-between; align-items: center;">
            <span><strong style="color: #E40000;">Live Prototype Access:</strong> Deployed and accessible live at <a href="https://airtel.hrushikeshramilla.in" style="color: #E40000; text-decoration: underline;">airtel.hrushikeshramilla.in</a></span>
            <span style="color: #5A5A5D; font-weight: 600;">Official Demo Video: <a href="https://airtel.hrushikeshramilla.in/demoVideo" style="color: #121316; text-decoration: underline; font-weight: 800;">airtel.hrushikeshramilla.in/demoVideo</a></span>
          </div>
        </div>
      </div>

      <div class="slide-footer">
        <div>Airtel Sync 2026 · Digital Track | Project Udyam Digital</div>
        <div class="team-name">Team Neural Nexus · ABV-IIITM Gwalior</div>
        <div class="slide-number">Slide 5 of 7</div>
      </div>
    </div>
    """

    # -------------------------------------------------------------
    # SLIDE 6: COMPETITIVE ADVANTAGE: WHY ACCEL BUSINESS WINS
    # -------------------------------------------------------------
    s6 = f"""
    <div class="slide slide-template-bg" style="background-image: url('{img_template_slide_b64}');">
      <div class="slide-header">
        <div class="slide-title-group">
          <h1>Competitive Advantage: Why Accel Business Wins</h1>
          <p>Direct comparison against telco competitors, local cable resellers, and digital software apps</p>
        </div>
        <div class="slide-category-badge">Slide 6 of 7 · Competitive Strategy</div>
      </div>

      <div class="slide-content">
        <table class="comp-table" style="font-size: 14.5px;">
          <tr>
            <th style="width: 22%;">Strategic Capability</th>
            <th style="width: 28%; background-color: #FAF0F0; color: #900; border-left: 2px solid #E40000;">Accel Business (Project Udyam)</th>
            <th style="width: 25%;">Jio Business</th>
            <th style="width: 25%;">Local Cable / Resellers</th>
          </tr>
          <tr>
            <td><strong>Time to Get a Quote</strong></td>
            <td style="background-color: #FAF4F4; font-weight: 800; color: #121316; border-left: 2px solid #E40000;">&lt; 60 Seconds (Instant on mobile phone)</td>
            <td>24 to 48 Hours (Sales rep visit required)</td>
            <td>2 to 3 Days (Wait for technician visit)</td>
          </tr>
          <tr>
            <td><strong>Non-GST Shop Access</strong></td>
            <td style="background-color: #FAF4F4; font-weight: 800; color: #121316; border-left: 2px solid #E40000;">Full Access via Udyam (Unlocks 3.5 Cr shops)</td>
            <td>Strict GSTIN Mandate (Drops non-GST leads)</td>
            <td>Unregulated cash (No legal agreements)</td>
          </tr>
          <tr>
            <td><strong>Upfront Setup & Hardware</strong></td>
            <td style="background-color: #FAF4F4; font-weight: 800; color: #121316; border-left: 2px solid #E40000;">100% Waived (₹0 Upfront) on 12-mo plans</td>
            <td>₹1,500 – ₹3,000 setup fee charged upfront</td>
            <td>₹2,500 modem purchase + cash installation</td>
          </tr>
          <tr>
            <td><strong>SLA & Downtime Guarantee</strong></td>
            <td style="background-color: #FAF4F4; font-weight: 800; color: #121316; border-left: 2px solid #E40000;">99.5% Uptime + 4G LTE Auto-Failover</td>
            <td>Best effort broadband; slow fiber cut repair</td>
            <td>No SLA; frequent unannounced cable cuts</td>
          </tr>
          <tr>
            <td><strong>Hardware & Devices Bundled</strong></td>
            <td style="background-color: #FAF4F4; font-weight: 800; color: #121316; border-left: 2px solid #E40000;">Wi-Fi 6 Router + CUG SIMs + Soundbox + CCTV</td>
            <td>Standard single-band Wi-Fi router only</td>
            <td>Consumer modem; third-party camera setup</td>
          </tr>
          <tr>
            <td><strong>Lead Abandonment Rescue</strong></td>
            <td style="background-color: #FAF4F4; font-weight: 800; color: #121316; border-left: 2px solid #E40000;">Automated LightGBM WhatsApp Rescue</td>
            <td>Manual sales calls; 56% leads abandoned</td>
            <td>Ignored; zero retargeting infrastructure</td>
          </tr>
          <tr>
            <td><strong>Data Privacy (DPDP Act 2023)</strong></td>
            <td style="background-color: #FAF4F4; font-weight: 800; color: #121316; border-left: 2px solid #E40000;">100% Zero-Persistence: IDs masked in RAM</td>
            <td>Standard cloud storage (PII saved on disk)</td>
            <td>Zero privacy (Photocopies, raw WhatsApp)</td>
          </tr>
          <tr>
            <td><strong>Indian Language Ingress</strong></td>
            <td style="background-color: #FAF4F4; font-weight: 800; color: #121316; border-left: 2px solid #E40000;">10 Indian Languages with script & voice audio</td>
            <td>Static English & Hindi website forms</td>
            <td>Verbal local dialect only (No digital tool)</td>
          </tr>
          <tr>
            <td><strong>Time to Final Activation</strong></td>
            <td style="background-color: #FAF4F4; font-weight: 800; color: #121316; border-left: 2px solid #E40000;">3.8 Days (Digital dispatch & automated provisioning)</td>
            <td>14 to 21 Days (Paper manual verification)</td>
            <td>5 to 7 Days (Unmanaged setup)</td>
          </tr>
          <tr>
            <td><strong>Customer Status Visibility</strong></td>
            <td style="background-color: #FAF4F4; font-weight: 800; color: #121316; border-left: 2px solid #E40000;">Live 6-Stage Web/WhatsApp Tracker + Tech OTP</td>
            <td>Manual chase calls to 1800 call center</td>
            <td>Unreachable technician mobile numbers</td>
          </tr>
          <tr>
            <td><strong>Channel Partner Model</strong></td>
            <td style="background-color: #FAF4F4; font-weight: 800; color: #121316; border-left: 2px solid #E40000;">15% Recurring Commission via dynamic QR</td>
            <td>Direct sales force (Cuts out local dealers)</td>
            <td>Fragmented resellers (No technology)</td>
          </tr>
        </table>

        <div class="grid-3" style="gap: 14px;">
          <div class="card-beige" style="padding: 16px 18px;">
            <div style="font-size: 15px; font-weight: 850; color: #121316; margin-bottom: 4px;">Why Jio Cannot Copy Quickly</div>
            <div style="font-size: 13.5px; color: #4A4B4E; line-height: 1.45;">
              Jio's enterprise architecture relies on rigid SAP GST pipelines and corporate direct sales teams. Discarding GST requirements demands rebuilding their DoT compliance stack from scratch.
            </div>
          </div>

          <div class="card-beige" style="padding: 16px 18px;">
            <div style="font-size: 15px; font-weight: 850; color: #121316; margin-bottom: 4px;">Coexistence Over Cannibalization</div>
            <div style="font-size: 13.5px; color: #4A4B4E; line-height: 1.45;">
              Instead of fighting local cable operators, Accel pays them 15% recurring commissions via dynamic QR codes, converting former competitors into our local installation & maintenance franchise.
            </div>
          </div>

          <div class="card-beige" style="padding: 16px 18px;">
            <div style="font-size: 15px; font-weight: 850; color: #121316; margin-bottom: 4px;">Telecom Physical Infrastructure Moat</div>
            <div style="font-size: 13.5px; color: #4A4B4E; line-height: 1.45;">
              Standalone SaaS software (Khatabook / Zoho) cannot provide physical last-mile fiber connectivity or cellular auto-failover. Accel owns the foundational physical infrastructure.
            </div>
          </div>
        </div>

        <div class="card" style="padding: 14px 20px; border-left: 4px solid #E40000; background: #FAF8F5; margin-top: 14px; margin-right: 340px;">
          <div style="font-size: 14px; color: #121316; font-weight: 600; line-height: 1.45;">
            <strong style="color: #900;">Defensibility Summary:</strong> Accel's physical last-mile fiber + automated DoT-compliant Udyam engine creates an insurmountable 18-month moat against both legacy telcos and pure SaaS players.
          </div>
        </div>
      </div>

      <div class="slide-footer">
        <div>Airtel Sync 2026 · Digital Track | Project Udyam Digital</div>
        <div class="team-name">Team Neural Nexus · ABV-IIITM Gwalior</div>
        <div class="slide-number">Slide 6 of 7</div>
      </div>
    </div>
    """

    # -------------------------------------------------------------
    # SLIDE 7: QUANTIFIED BUSINESS IMPACT & 12-MONTH ROLLOUT

    # -------------------------------------------------------------

    s7 = f"""

    <div class="slide slide-template-bg" style="background-image: url('{img_template_slide_b64}');">

      <div class="slide-header">

        <div class="slide-title-group">

          <h1>Quantified Business Impact & 12-Month Rollout</h1>

          <p>Before vs. After sales transformation and 12-month national scale roadmap</p>

        </div>

        <div class="slide-category-badge">Slide 7 of 7 · Impact & Rollout</div>

      </div>



      <div class="slide-content">

        <div class="grid-2" style="flex: 1; gap: 18px;">

          

          <div style="display: flex; flex-direction: column; gap: 10px;">

            <div class="card" style="padding: 16px 18px;">

              <div style="font-size: 14.5px; font-weight: 850; color: #121316; margin-bottom: 10px;">Funnel Economics Transformation</div>

              <div class="grid-2" style="gap: 12px;">

                <div class="stat-box">

                  <div class="stat-num" style="color: #E40000;">+38.8%</div>

                  <div class="stat-label">Quote Acceptance Rate</div>

                  <div class="stat-sub">Jumps from 43.6% to 82.4% by eliminating the 5-day quote wait.</div>

                </div>

                <div class="stat-box">

                  <div class="stat-num">4.25x</div>

                  <div class="stat-label">Non-GST Conversion Lift</div>

                  <div class="stat-sub">Conversion rises from 2.0% to 8.5% via instant Udyam lookup.</div>

                </div>

                <div class="stat-box">

                  <div class="stat-num">3.8 Days</div>

                  <div class="stat-label">Lead to Activation Cycle</div>

                  <div class="stat-sub">Compressed by 78.4% from baseline 17.6 days via digital KYC.</div>

                </div>

                <div class="stat-box">

                  <div class="stat-num">₹3,250</div>

                  <div class="stat-label">Acquisition Cost (CAC)</div>

                  <div class="stat-sub">Slashed by 78.3% from ₹15,000 via self-serve mobile flow.</div>

                </div>

              </div>

            </div>



            <div class="card" style="padding: 14px 18px; border-left: 3.5px solid #121316;">

              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 3px;">

                <div style="font-size: 14px; font-weight: 850; color: #121316;">LightGBM Lead Rescue Engine (Trained on 5,000 Leads)</div>

                <span class="badge-pill" style="background: #121316; color: #fff; font-weight: 800;">AUC 0.84 MODEL</span>

              </div>

              <div style="font-size: 13px; color: #4A4B4E; line-height: 1.4;">

                Retargets the 56.4% dropped quote cohort within 15 minutes via enterprise WhatsApp API with 1-click pre-hydrated carts. <strong>Recovers 22.4% of abandoned prospects</strong> (249 merchants from 5,000 leads), unlocking <strong>₹48 Cr in recovered recurring ARR</strong> at national scale.

              </div>

            </div>



            <div class="card" style="padding: 14px 18px;">

              <div style="font-size: 13.5px; font-weight: 850; color: #121316; margin-bottom: 6px;">Direct Labor & Operational Efficiency Gains:</div>

              <table style="width: 100%; font-size: 12.5px; border-collapse: collapse;">

                <tr style="border-bottom: 1px solid #EFECE6;"><td style="padding: 4px 0; color: #5A5A5D;">Field Sales Rep Time / Customer</td><td style="text-align: right; font-weight: 800;">24.0 Hours → 2.1 Hours (-91.2%)</td></tr>

                <tr style="border-bottom: 1px solid #EFECE6;"><td style="padding: 4px 0; color: #5A5A5D;">Customer Status Chase Calls</td><td style="text-align: right; font-weight: 800;">3.2 Calls → 0.4 Calls (-87.5%)</td></tr>

                <tr style="border-bottom: 1px solid #EFECE6;"><td style="padding: 4px 0; color: #5A5A5D;">6-Month Customer Churn Rate</td><td style="text-align: right; font-weight: 800;">14.2% → 6.8% (-52.1% via SLAs)</td></tr>

                <tr style="border-bottom: 1px solid #EFECE6;"><td style="padding: 4px 0; color: #5A5A5D;">Catalogue Rule Violation / Mis-Sell Rate</td><td style="text-align: right; font-weight: 850; color: #E40000;">15.2% (56/368) → 0.0% (-100% via CPQ DAG)</td></tr>

                <tr style="border-bottom: 1px solid #EFECE6;"><td style="padding: 4px 0; color: #5A5A5D;">Gross Margin on Bundles</td><td style="text-align: right; font-weight: 800;">42.5% → 61.8% (+19.3% automated margin)</td></tr>

                <tr style="border-bottom: 1px solid #EFECE6;"><td style="padding: 4px 0; color: #5A5A5D;">Partner Dealer Commission</td><td style="text-align: right; font-weight: 800;">15% Recurring via Instant QR Attribution</td></tr>

                <tr style="border-bottom: 1px solid #EFECE6;"><td style="padding: 4px 0; color: #5A5A5D;">Quote Generation Speed</td><td style="text-align: right; font-weight: 800;">3 to 5 Days → &lt; 60 Seconds (-99.9%)</td></tr>

                <tr><td style="padding: 4px 0; color: #5A5A5D;">Payback Period on Sales CAC</td><td style="text-align: right; font-weight: 850; color: #121316;">4.8 Months (vs 14.2 Months baseline)</td></tr>

              </table>

              <div style="font-size: 11.5px; color: #7A7B7E; margin-top: 6px; border-top: 1px solid #EFECE6; padding-top: 4px;">

                <strong>Bottom-Line Result:</strong> Direct sales acquisition cost slashed from ₹15,000 to ₹3,250, compressing CAC payback from 14.2 months to 4.8 months while freeing 22 hours of sales rep labor per closed account.

              </div>

            </div>

          </div>



          <div style="display: flex; flex-direction: column; gap: 10px;">

            <div class="card" style="padding: 16px 18px;">

              <div style="font-size: 14.5px; font-weight: 850; color: #121316; margin-bottom: 8px;">12-Month National Scale Strategy</div>

              

              <div style="border-left: 3px solid #E40000; padding-left: 10px; margin-bottom: 10px;">

                <div style="display: flex; justify-content: space-between;">

                  <strong style="font-size: 13.5px; color: #121316;">Phase 1: Metros & Kirana Density (Months 1–3)</strong>

                  <span class="badge-pill" style="background: #E40000; color: #fff; border-color: #E40000;">50K Units · ₹12 Cr ARR</span>

                </div>

                <div style="font-size: 12.5px; color: #4A4B4E; margin-top: 2px; line-height: 1.35;">

                  • Target 8 Tier-1 cities (Delhi NCR, Mumbai, Bengaluru, Hyderabad).<br>

                  • Deploy Udyam Vyapar & Clinic packs via 15,000 retail store QR codes.<br>

                  • Activate 50,000 merchants with instant paperless Udyam onboarding.<br>

                  • Train 1,200 local cable operators as authorized 15% commission partners.

                </div>

              </div>



              <div style="border-left: 3px solid #121316; padding-left: 10px; margin-bottom: 10px;">

                <div style="display: flex; justify-content: space-between;">

                  <strong style="font-size: 13.5px; color: #121316;">Phase 2: Industrial Clusters & Clinics (Months 4–6)</strong>

                  <span class="badge-pill">120K Units · ₹38 Cr ARR</span>

                </div>

                <div style="font-size: 12.5px; color: #4A4B4E; margin-top: 2px; line-height: 1.35;">

                  • Expand into 40 manufacturing towns (Surat, Coimbatore, Ludhiana, Peenya).<br>

                  • Focus on Leased Line connectivity and multi-store Cloud CCTV packs.<br>

                  • Capture 120,000 businesses with mission-critical 99.95% SLAs.<br>

                  • Roll out automated field technician dispatch with OTP tracking across hubs.

                </div>

              </div>



              <div style="border-left: 3px solid #121316; padding-left: 10px;">

                <div style="display: flex; justify-content: space-between;">

                  <strong style="font-size: 13.5px; color: #121316;">Phase 3: All-India Bharat Scale (Months 7–12)</strong>

                  <span class="badge-pill" style="background: #121316; color: #fff;">500K Units · ₹1,200 Cr ARR</span>

                </div>

                <div style="font-size: 12.5px; color: #4A4B4E; margin-top: 2px; line-height: 1.35;">

                  • Roll out across 500+ Tier-3/4 districts supported by 10 Indian languages.<br>

                  • Integrate full voice biometrics and regional dialect speech synthesis.<br>

                  • 12-Month Goal: 500,000 active small businesses generating ₹1,200 Cr annualized ARR at ₹3,250 blended CAC.

                </div>

              </div>

            </div>



            <div class="card-beige" style="padding: 14px 18px;">

              <div style="font-size: 14px; font-weight: 850; color: #121316; margin-bottom: 6px;">Strategic Airtel Ecosystem Synergies:</div>

              <div style="display: flex; flex-direction: column; gap: 5px; font-size: 12.5px; color: #333336;">

                <div style="background: #FFFFFF; padding: 6px 10px; border-radius: 4px; border: 1px solid #DDD8CE;">

                  <strong>Airtel Payments Bank:</strong> Integrated QR soundbox for Kirana checkouts; daily merchant cash settlements automatically offset monthly Accel broadband subscriptions.

                </div>

                <div style="background: #FFFFFF; padding: 6px 10px; border-radius: 4px; border: 1px solid #DDD8CE;">

                  <strong>Airtel IQ WhatsApp API:</strong> Sub-second transactional quote push and LightGBM automated retargeting with 1-click pre-hydrated carts. Recovers 22.4% of abandoned prospects.

                </div>

                <div style="background: #FFFFFF; padding: 6px 10px; border-radius: 4px; border: 1px solid #DDD8CE;">

                  <strong>Nxtra Data Centers:</strong> Sovereign Tier-4 Indian data facilities guarantee 100% DPDP Act 2023 compliance with zero offshore data transit or foreign jurisdiction exposure.

                </div>

                <div style="background: #FFFFFF; padding: 6px 10px; border-radius: 4px; border: 1px solid #DDD8CE;">

                  <strong>Airtel 5G Plus QoS Slicing:</strong> Dedicated network QoS packet queues ensure zero latency jitter during evening peak payment hours (7–9 PM), preventing lost retail checkouts.

                </div>

                <div style="background: #FFFFFF; padding: 6px 10px; border-radius: 4px; border: 1px solid #DDD8CE;">

                  <strong>Airtel Merchant Finance:</strong> Pre-approved working capital micro-loans up to ₹5 Lakhs for active Accel businesses based on automated broadband uptime and UPI transaction history.

                </div>

              </div>

            </div>

          </div>



        </div>



        <div style="background: #FFFFFF; border-left: 4px solid #E40000; border-top: 1.5px solid #DDD8CE; border-right: 1.5px solid #DDD8CE; border-bottom: 1.5px solid #DDD8CE; border-radius: 6px; padding: 12px 18px; width: 100%;">

          <div style="font-size: 13.5px; font-weight: 750; color: #121316; line-height: 1.4;">

            <strong style="color: #E40000;">Executive Verdict:</strong> Project Udyam Digital transforms Accel Business from a slow, paper-bound corporate carrier into India's default digital operating system for small enterprises—slashing CAC by 78%, lifting non-GST conversions 4.25x, and unlocking ₹1,200 Cr ARR in 12 months.<br><span style="font-size: 12px; color: #4A4B4E; margin-top: 4px; display: inline-block;">Official HD Video Walkthrough & Interactive Demo: <a href="https://airtel.hrushikeshramilla.in/demoVideo" style="color: #E40000; font-weight: 800; text-decoration: underline;">https://airtel.hrushikeshramilla.in/demoVideo</a></span>

          </div>

        </div>

      </div>



      <div class="slide-footer">

        <div>Airtel Sync 2026 · Digital Track | Project Udyam Digital</div>

        <div class="team-name">Team Neural Nexus · ABV-IIITM Gwalior</div>

        <div class="slide-number">Slide 7 of 7</div>

      </div>

    </div>

    """

    slides_html = [s0, s1, s2, s3, s4, s5, s6, s7]
    print(f"Total Slides Generated: {len(slides_html)} (Slide 0 Intro + 7 Evaluated Slides = Exactly 8 Slides Total)")

    slide_files = []
    for idx, s_html in enumerate(slides_html):
        full_page = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>{CSS_THEME}</style>
</head>
<body>
{s_html}
</body>
</html>"""
        path = os.path.join(BUILD_DIR, f"slide_{idx}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(full_page)
        slide_files.append(path)

    slide_pngs = []
    print("Launching Microsoft Edge via Playwright to render 4K screenshots...")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=2)
        
        for idx, slide_html in enumerate(slide_files):
            abs_url = f"file:///{os.path.abspath(slide_html).replace(os.sep, '/')}"
            page.goto(abs_url, wait_until="networkidle")
            page.wait_for_timeout(400)
            png_path = os.path.join(PREVIEW_DIR, f"slide_{idx}.png")
            page.screenshot(path=png_path, full_page=True)
            print(f"  -> Rendered Slide {idx}: {png_path}")
            slide_pngs.append(png_path)
            
        browser.close()

    print(f"Rendering official PDF: {OFFICIAL_PDF}...")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        pdf_pages_html = ""
        for s_html in slides_html:
            pdf_pages_html += f'<div style="page-break-after: always; width: 1920px; height: 1080px; overflow: hidden;">{s_html}</div>\n'
            
        full_pdf_doc = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@page {{
  size: 1920px 1080px;
  margin: 0;
}}
{CSS_THEME}
body {{ margin: 0; padding: 0; background-color: #FFFFFF; }}
</style>
</head>
<body>
{pdf_pages_html}
</body>
</html>"""
        pdf_html_path = os.path.join(BUILD_DIR, "full_deck.html")
        with open(pdf_html_path, "w", encoding="utf-8") as f:
            f.write(full_pdf_doc)
            
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        abs_pdf_url = f"file:///{os.path.abspath(pdf_html_path).replace(os.sep, '/')}"
        page.goto(abs_pdf_url, wait_until="networkidle")
        page.wait_for_timeout(600)
        page.pdf(
            path=OFFICIAL_PDF,
            width="1920px",
            height="1080px",
            print_background=True,
            margin={"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"}
        )
        browser.close()
        print(f"  -> Generated {OFFICIAL_PDF} ({os.path.getsize(OFFICIAL_PDF)/1024/1024:.2f} MB)")

    print(f"Building official PPTX: {OFFICIAL_PPTX}...")
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    for png_path in slide_pngs:
        slide = prs.slides.add_slide(blank_layout)
        slide.shapes.add_picture(png_path, 0, 0, width=prs.slide_width, height=prs.slide_height)

    prs.save(OFFICIAL_PPTX)
    print(f"  -> Generated {OFFICIAL_PPTX} ({os.path.getsize(OFFICIAL_PPTX)/1024/1024:.2f} MB)")

    if OFFICIAL_PDF != "Neural_Nexus_ABV_IIITM_Gwalior.pdf": shutil.copyfile(OFFICIAL_PDF, "Neural_Nexus_ABV_IIITM_Gwalior.pdf")
    if OFFICIAL_PPTX != "Neural_Nexus_ABV_IIITM_Gwalior.pptx": shutil.copyfile(OFFICIAL_PPTX, "Neural_Nexus_ABV_IIITM_Gwalior.pptx")
    print("  -> Mirrored to Neural_Nexus_ABV_IIITM_Gwalior.pdf and Neural_Nexus_ABV_IIITM_Gwalior.pptx")

    print("\n=== Presentation Build Complete! ===")
    print(f"1. PDF: {OFFICIAL_PDF} ({os.path.getsize(OFFICIAL_PDF)/1024/1024:.2f} MB)")
    print(f"2. PPT: {OFFICIAL_PPTX} ({os.path.getsize(OFFICIAL_PPTX)/1024/1024:.2f} MB)")

if __name__ == "__main__":
    generate_deck()
