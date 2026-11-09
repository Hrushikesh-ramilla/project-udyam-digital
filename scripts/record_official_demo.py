"""
Project Udyam Digital - Official Master Demo Video Recording Script
Deterministic Playwright Automation with Smooth Visual Easing Cursor
Target Video Duration: 2m 35s - 2m 50s (strictly between 120s and 175s)
"""

import os
import sys
import time
import math
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright, Page

CUR_DIR = Path(__file__).resolve().parent
ROOT_DIR = CUR_DIR.parent
VIDEO_DIR = ROOT_DIR / "official_demo_recording"
FINAL_MP4 = ROOT_DIR / "Project_Udyam_Digital_Official_Demo.mp4"

def inject_visual_cursor(page: Page):
    """Injects a high-visibility luxury red cursor with glowing ring for professional video demo."""
    page.evaluate("""() => {
        if (window.__demo_cursor_injected) return;
        window.__demo_cursor_injected = true;
        
        const cursor = document.createElement('div');
        cursor.id = 'demo-cursor';
        cursor.style.position = 'fixed';
        cursor.style.top = '0';
        cursor.style.left = '0';
        cursor.style.width = '24px';
        cursor.style.height = '24px';
        cursor.style.borderRadius = '50%';
        cursor.style.border = '2.5px solid #ff3333';
        cursor.style.backgroundColor = 'rgba(255, 30, 30, 0.25)';
        cursor.style.boxShadow = '0 0 16px rgba(255, 0, 0, 0.8), 0 0 32px rgba(255, 0, 0, 0.4)';
        cursor.style.pointerEvents = 'none';
        cursor.style.zIndex = '999999';
        cursor.style.transform = 'translate(-50%, -50%)';
        cursor.style.transition = 'transform 0.06s ease-out, border-color 0.1s ease';
        document.body.appendChild(cursor);
        
        window.__current_cursor = { x: 960, y: 540 };
        cursor.style.left = window.__current_cursor.x + 'px';
        cursor.style.top = window.__current_cursor.y + 'px';
        
        window.addEventListener('mousemove', (e) => {
            window.__current_cursor = { x: e.clientX, y: e.clientY };
            cursor.style.left = e.clientX + 'px';
            cursor.style.top = e.clientY + 'px';
        });
        
        window.addEventListener('mousedown', () => {
            cursor.style.transform = 'translate(-50%, -50%) scale(0.75)';
            cursor.style.backgroundColor = 'rgba(255, 0, 0, 0.6)';
            cursor.style.borderColor = '#ffffff';
        });
        
        window.addEventListener('mouseup', () => {
            cursor.style.transform = 'translate(-50%, -50%) scale(1.0)';
            cursor.style.backgroundColor = 'rgba(255, 30, 30, 0.25)';
            cursor.style.borderColor = '#ff3333';
        });
    }""")

def smooth_move(page: Page, target_x: float, target_y: float, steps: int = 22, delay_ms: float = 14):
    """Moves the mouse smoothly using cosine easing for human-like fluidity."""
    curr = page.evaluate("""() => {
        return window.__current_cursor || { x: 960, y: 540 };
    }""")
    start_x, start_y = curr["x"], curr["y"]
    
    for i in range(1, steps + 1):
        t = i / steps
        ease = 0.5 - 0.5 * math.cos(t * math.pi)
        cur_x = start_x + (target_x - start_x) * ease
        cur_y = start_y + (target_y - start_y) * ease
        page.mouse.move(cur_x, cur_y)
        time.sleep(delay_ms / 1000.0)

def human_click(page: Page, locator, steps: int = 18, wait_after: float = 0.6):
    """Scrolls element into view, moves cursor smoothly, and clicks with realistic delay."""
    try:
        locator.scroll_into_view_if_needed()
        page.wait_for_timeout(250)
        inject_visual_cursor(page)
        box = locator.bounding_box()
        if box:
            tx = box["x"] + box["width"] / 2
            ty = box["y"] + box["height"] / 2
            smooth_move(page, tx, ty, steps=steps)
            time.sleep(0.12)
            page.mouse.click(tx, ty)
            time.sleep(wait_after)
        else:
            locator.click()
            time.sleep(wait_after)
    except Exception as e:
        print(f"Click fallback: {e}")
        try:
            locator.click()
            time.sleep(wait_after)
        except Exception:
            pass

def human_type(page: Page, locator, text: str, min_delay: float = 0.02, max_delay: float = 0.045):
    """Types text with natural keystroke cadence."""
    locator.scroll_into_view_if_needed()
    human_click(page, locator, steps=12, wait_after=0.25)
    for char in text:
        page.keyboard.type(char)
        jitter = min_delay + (hash(char) % 10) * ((max_delay - min_delay) / 10.0)
        time.sleep(jitter)
    time.sleep(0.35)

def record_master_demo():
    print("=" * 60)
    print("PROJECT UDYAM DIGITAL — OFFICIAL MASTER DEMO RECORDING")
    print("Target Duration: 2m 35s to 2m 50s (155 - 170 seconds)")
    print("=" * 60)
    
    if VIDEO_DIR.exists():
        import shutil
        shutil.rmtree(VIDEO_DIR, ignore_errors=True)
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    
    start_total_time = time.time()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="msedge",
            headless=True,
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
                "--hide-scrollbars",
            ]
        )
        
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=str(VIDEO_DIR),
            record_video_size={"width": 1920, "height": 1080},
        )
        
        page = context.new_page()
        
        # ---------------------------------------------------------
        # SCENE 1: HERO & MULTILINGUAL ADVISOR (0:00 - 1:00)
        # ---------------------------------------------------------
        print("\n[SCENE 1: HERO & MULTILINGUAL ADVISOR]")
        page.goto("https://airtel.hrushikeshramilla.in", wait_until="networkidle")
        inject_visual_cursor(page)
        page.wait_for_timeout(3500)
        
        # 1.1 Highlight Presets / Archetype cards
        presets = page.locator("div:has-text('Kirana & Retail')").first
        if presets.count() > 0:
            box = presets.bounding_box()
            if box:
                smooth_move(page, box["x"] + box["width"]/2, box["y"] + box["height"]/2, steps=18)
                time.sleep(2.5)
        
        # 1.2 Message 1: "Hola"
        print("  -> Turn 1: Typing 'Hola'...")
        chat_input = page.locator("input[placeholder*='Type a message' i], input[placeholder*='Type or speak' i]").first
        human_type(page, chat_input, "Hola")
        page.keyboard.press("Enter")
        print("  -> Waiting for Spanish response...")
        page.wait_for_timeout(6000)
        
        # Linger to let viewer read Spanish response
        page.evaluate("() => window.scrollBy({ top: 150, behavior: 'smooth' })")
        inject_visual_cursor(page)
        smooth_move(page, 960, 480, steps=15)
        time.sleep(4.5)
        
        # 1.3 Message 2: "I need some help"
        print("  -> Turn 2: Typing 'I need some help'...")
        human_type(page, chat_input, "I need some help")
        page.keyboard.press("Enter")
        print("  -> Waiting for English response...")
        page.wait_for_timeout(6000)
        
        # Linger to let viewer read English response
        inject_visual_cursor(page)
        smooth_move(page, 960, 520, steps=15)
        time.sleep(4.5)
        
        # 1.4 Message 3: Hindi Gaming Center in Ooty
        hindi_gaming_query = "Mujhe Ooty mein ek gaming center chalana hai, uske liye online shooting games khelne ke liye achha internet connection chahiye"
        print("  -> Turn 3: Typing Hindi query about Ooty gaming center...")
        human_type(page, chat_input, hindi_gaming_query, min_delay=0.015, max_delay=0.035)
        page.keyboard.press("Enter")
        print("  -> Waiting for Hinglish response...")
        page.wait_for_timeout(7500)
        
        # Linger to let viewer read Romanized Hinglish response
        inject_visual_cursor(page)
        smooth_move(page, 960, 550, steps=15)
        time.sleep(5.0)
        
        # 1.5 Click "Native Script" button
        print("  -> Toggling 'Native Script' (Devanagari)...")
        native_btn = page.locator("button:has-text('Native Script')").first
        if native_btn.count() > 0:
            human_click(page, native_btn, steps=16, wait_after=1.0)
            print("  -> Native Hindi script rendered. Linger for visual appreciation...")
            time.sleep(6.0)
            
        # 1.6 Click "English Words" button
        print("  -> Toggling back to 'English Words' (Romanized Hinglish)...")
        english_btn = page.locator("button:has-text('English Words')").first
        if english_btn.count() > 0:
            human_click(page, english_btn, steps=16, wait_after=1.0)
            time.sleep(4.0)
            
        # Highlight in-chat recommended enterprise solution card
        print("  -> Showcasing in-chat recommendation card...")
        review_cart_btn = page.locator("button:has-text('Review in Cart & Start KYC')").first
        if review_cart_btn.count() > 0 and review_cart_btn.is_visible():
            review_cart_btn.scroll_into_view_if_needed()
            page.wait_for_timeout(300)
            inject_visual_cursor(page)
            box = review_cart_btn.bounding_box()
            if box:
                smooth_move(page, box["x"] + box["width"]/2, box["y"] + box["height"]/2, steps=16)
                time.sleep(4.0)
        
        # ---------------------------------------------------------
        # SCENE 2: SOLUTION ARCHITECTURE & DYNAMIC CART (1:00 - 1:17)
        # ---------------------------------------------------------
        print("\n[SCENE 2: DYNAMIC CPQ SOLUTION ARCHITECTURE & CART]")
        # Click in-chat "Review in Cart & Start KYC" button
        if review_cart_btn.count() > 0 and review_cart_btn.is_visible():
            print("  -> Clicking in-chat 'Review in Cart & Start KYC' button...")
            human_click(page, review_cart_btn, steps=16, wait_after=2.0)
        else:
            page.evaluate("() => { const el = document.getElementById('cpq-cart-section'); if (el) el.scrollIntoView({ behavior: 'smooth' }); else window.scrollBy({ top: 500, behavior: 'smooth' }); }")
            time.sleep(2.0)
            
        inject_visual_cursor(page)
        # Highlight bundle items and contract tenure
        print("  -> Showcasing bundled architecture, contract tenure, and waived setup fees...")
        tenure_12m = page.locator("button:has-text('12 Months'), button:has-text('12-Month'), button:has-text('Annual')").first
        if tenure_12m.count() > 0 and tenure_12m.is_visible():
            human_click(page, tenure_12m, steps=15, wait_after=2.0)
            
        # Hover over budget slider / solution blueprint
        smooth_move(page, 960, 680, steps=18)
        time.sleep(5.0)
        
        # Click "Proceed to Instant KYC" button
        print("  -> Navigating to Smart KYC Gate via 'Proceed to Instant KYC'...")
        proceed_kyc_btn = page.locator("button:has-text('Proceed to Instant KYC')").first
        proceed_kyc_btn.scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        human_click(page, proceed_kyc_btn, steps=18, wait_after=2.5)
            
        # Ensure Smart KYC page has rendered
        page.wait_for_selector("text=Auto-Fill Test Specimen", timeout=6000)
        
        # ---------------------------------------------------------
        # SCENE 3: SMART KYC ANOMALY TRAPPING & SPECIMEN BENCH (1:17 - 1:40)
        # ---------------------------------------------------------
        print("\n[SCENE 3: SMART KYC ANOMALY TRAPPING & SPECIMEN BENCH]")
        inject_visual_cursor(page)
        time.sleep(2.5)
        
        # Showcase Specimen Auto-Fill Toolbar
        print("  -> Showcasing Auto-Fill Test Specimen toolbar...")
        specimen_toolbar = page.locator("div:has-text('Auto-Fill Test Specimen')").first
        if specimen_toolbar.count() > 0:
            box = specimen_toolbar.bounding_box()
            if box:
                smooth_move(page, box["x"] + 200, box["y"] + 25, steps=16)
                time.sleep(3.0)
                
        # Hover over anomaly specimen buttons (K01 Cancelled, K05 Missing Udyam) to demonstrate anomaly trap
        k01_btn = page.locator("button:has-text('K01'), button:has-text('Cancelled GSTIN')").first
        if k01_btn.count() > 0:
            box = k01_btn.bounding_box()
            if box:
                smooth_move(page, box["x"] + box["width"]/2, box["y"] + box["height"]/2, steps=12)
                time.sleep(2.0)
                
        k05_btn = page.locator("button:has-text('K05'), button:has-text('Missing Udyam')").first
        if k05_btn.count() > 0:
            box = k05_btn.bounding_box()
            if box:
                smooth_move(page, box["x"] + box["width"]/2, box["y"] + box["height"]/2, steps=12)
                time.sleep(2.0)
                
        # Click verified specimen preset (K03 Clean Golden Path)
        print("  -> Selecting verified specimen preset (K03 / Clean Golden Path)...")
        k03_btn = page.locator("button:has-text('K03'), button:has-text('Clean Golden Path')").first
        if k03_btn.count() > 0:
            human_click(page, k03_btn, steps=15, wait_after=2.5)
            
        # Scroll to inspect staged documents, Verhoeff D5 check digit, and DPDP masking
        print("  -> Showcasing live Verhoeff D5 check digit, RapidFuzz score, and DPDP Act 2023 zero-persistence masking...")
        page.evaluate("() => window.scrollBy({ top: 300, behavior: 'smooth' })")
        inject_visual_cursor(page)
        time.sleep(2.0)
        smooth_move(page, 960, 480, steps=18)
        time.sleep(5.0)
        
        # Click "Run KYC Verification on Staged Package"
        print("  -> Executing DPDP-compliant KYC verification...")
        run_kyc_btn = page.locator("button:has-text('Run KYC Verification on Staged Package')").first
        run_kyc_btn.scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        human_click(page, run_kyc_btn, steps=16, wait_after=3.0)
            
        # Wait for automatic fulfillment provisioning transition
        print("  -> Waiting for Fulfillment & Live Order Tracker transition...")
        page.wait_for_selector("button:has-text('Pay Online')", timeout=15000)
        page.wait_for_timeout(1500)
        
        # ---------------------------------------------------------
        # SCENE 4: 6-STAGE DIGITAL FULFILLMENT, WHATSAPP WEBHOOKS & PAYMENTS (1:40 - 2:16)
        # ---------------------------------------------------------
        print("\n[SCENE 4: 6-STAGE DIGITAL FULFILLMENT, WHATSAPP WEBHOOKS & PAYMENTS]")
        page.evaluate("() => window.scrollTo({ top: 0, behavior: 'instant' })")
        inject_visual_cursor(page)
        time.sleep(2.0)
        
        # Showcase Order Header and BlueDart Dispatch Card
        print("  -> Highlighting BlueDart hardware dispatch card & assigned engineer...")
        smooth_move(page, 960, 240, steps=18)
        time.sleep(4.0)
        
        # Click "Pay Online (UPI / Sandbox)" button
        print("  -> Clicking 'Pay Online (UPI / Sandbox)'...")
        pay_btn = page.locator("button:has-text('Pay Online')").first
        if pay_btn.count() > 0 and pay_btn.is_visible():
            human_click(page, pay_btn, steps=16, wait_after=2.5)
            
            # Modal is open!
            print("  -> Showcasing Native NPCI Dynamic UPI QR Code Scanner...")
            smooth_move(page, 960, 520, steps=16)
            time.sleep(5.0)
            
            # Click "Razorpay Sandbox" tab
            print("  -> Switching to Razorpay Sandbox tab...")
            rzp_tab = page.locator("button:has-text('Razorpay Sandbox')").first
            if rzp_tab.count() > 0 and rzp_tab.is_visible():
                human_click(page, rzp_tab, steps=14, wait_after=1.5)
                smooth_move(page, 960, 540, steps=14)
                time.sleep(5.0)
                
            # Close Payment Modal
            print("  -> Closing Payment Modal...")
            close_modal_btn = page.locator("button:has(svg.lucide-x), button:has(svg.lucide-x-circle)").first
            if close_modal_btn.count() > 0:
                human_click(page, close_modal_btn, steps=14, wait_after=2.0)
            else:
                page.keyboard.press("Escape")
                time.sleep(2.0)
                
        # Scroll to 6-stage fulfillment pipeline and WhatsApp webhook
        print("  -> Showcasing 6-Stage Digital Fulfillment Pipeline (SQLite WAL Engine)...")
        page.evaluate("() => window.scrollBy({ top: 380, behavior: 'smooth' })")
        inject_visual_cursor(page)
        time.sleep(2.0)
        smooth_move(page, 960, 480, steps=18)
        time.sleep(4.0)
        
        # Advance SLA stage to trigger live webhook delivery
        simulate_sla_btn = page.locator("button:has-text('Simulate Next SLA Stage')").first
        if simulate_sla_btn.count() > 0 and simulate_sla_btn.is_visible():
            print("  -> Advancing SLA Stage (Simulate Next SLA Stage)...")
            human_click(page, simulate_sla_btn, steps=16, wait_after=2.5)
            
        # Linger on Customer WhatsApp Webhook Notification
        print("  -> Showcasing Customer WhatsApp Webhook Notification drawer...")
        page.evaluate("() => window.scrollBy({ top: 320, behavior: 'smooth' })")
        inject_visual_cursor(page)
        time.sleep(2.0)
        smooth_move(page, 960, 680, steps=16)
        time.sleep(5.0)
        
        # ---------------------------------------------------------
        # SCENE 5: SELLER / PARTNER OPS CONSOLE & AUTONOMOUS LEAD RESCUE (2:16 - 2:42)
        # ---------------------------------------------------------
        print("\n[SCENE 5: SELLER / PARTNER OPS CONSOLE & AUTONOMOUS LEAD RESCUE]")
        page.evaluate("() => window.scrollTo({ top: 0, behavior: 'instant' })")
        inject_visual_cursor(page)
        time.sleep(2.0)
        
        # Switch to "Partner & Ops" persona
        print("  -> Switching to 'Partner & Ops' persona...")
        partner_pill = page.locator("button:has-text('Partner & Ops')").first
        human_click(page, partner_pill, steps=16, wait_after=2.5)
        
        # Click "Lead Rescue" tab explicitly in case another tab was active
        lead_rescue_tab = page.locator("header button:has-text('Lead Rescue'), nav button:has-text('Lead Rescue')").first
        if lead_rescue_tab.count() > 0:
            human_click(page, lead_rescue_tab, steps=14, wait_after=2.0)
            
        page.wait_for_selector("text=Recovered ARR Potential", timeout=6000)
        
        # Highlight 4 Dynamic Operational Winback KPI Cards
        print("  -> Highlighting 4 Dynamic Operational Winback KPI Cards (Recovered ARR, Winback Rate)...")
        smooth_move(page, 960, 220, steps=18)
        time.sleep(4.5)
        
        # Scroll to High-Propensity Rescuable Leads table
        print("  -> Showcasing LightGBM winback conversion propensity and TreeSHAP explainability chips...")
        page.evaluate("() => window.scrollBy({ top: 340, behavior: 'smooth' })")
        inject_visual_cursor(page)
        time.sleep(2.0)
        smooth_move(page, 960, 480, steps=18)
        time.sleep(4.5)
        
        # Open Next-Best-Action (NBA) recovery drawer for first dropped quote
        rescue_lead_btn = page.locator("button:has-text('Rescue Lead')").first
        if rescue_lead_btn.count() > 0 and rescue_lead_btn.is_visible():
            print("  -> Opening Next-Best-Action (NBA) recovery drawer for dropped quote...")
            human_click(page, rescue_lead_btn, steps=16, wait_after=2.5)
            
            # Show automated WhatsApp pitch, pre-packaged bundle, and pre-hydration
            print("  -> Showcasing automated WhatsApp pitch, pre-packaged bundle, and pre-hydration...")
            smooth_move(page, 1500, 450, steps=18)
            time.sleep(4.0)
            
            # Click "Copy Pitch"
            copy_pitch_btn = page.locator("button:has-text('Copy Pitch')").first
            if copy_pitch_btn.count() > 0:
                human_click(page, copy_pitch_btn, steps=14, wait_after=2.0)
                
            # Close NBA drawer
            close_drawer_btn = page.locator("button[aria-label='Close dialog'], button:has(svg.lucide-x)").first
            if close_drawer_btn.count() > 0:
                human_click(page, close_drawer_btn, steps=14, wait_after=2.0)
            else:
                page.keyboard.press("Escape")
                time.sleep(2.0)
                
        # ---------------------------------------------------------
        # SCENE 6: OUTRO & SYSTEM SUMMARY (2:42 - 2:47)
        # ---------------------------------------------------------
        print("\n[SCENE 6: OUTRO]")
        page.evaluate("() => window.scrollTo({ top: 0, behavior: 'smooth' })")
        inject_visual_cursor(page)
        smooth_move(page, 960, 250, steps=18)
        time.sleep(5.0)
        
        elapsed = time.time() - start_total_time
        print(f"\nRecording completed in {elapsed:.1f} seconds (~{int(elapsed // 60)}m {int(elapsed % 60)}s).")
        print("Closing browser context to finalize raw recording...")
        
        context.close()
        browser.close()
        
    # Find generated webm file
    webm_files = list(VIDEO_DIR.glob("*.webm"))
    if not webm_files:
        print("ERROR: No recorded webm file found in", VIDEO_DIR)
        sys.exit(1)
        
    raw_video = webm_files[0]
    print(f"\nTranscoding raw video {raw_video} to full HD MP4: {FINAL_MP4.name}...")
    
    # Transcode using ffmpeg with libx264 for universal compatibility
    cmd = [
        "ffmpeg",
        "-i", str(raw_video),
        "-c:v", "libx264",
        "-profile:v", "high",
        "-level", "4.0",
        "-pix_fmt", "yuv420p",
        "-crf", "20",
        "-movflags", "+faststart",
        str(FINAL_MP4),
        "-y"
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("FFmpeg error:", res.stderr)
        sys.exit(1)
        
    size_mb = FINAL_MP4.stat().st_size / (1024 * 1024)
    print(f"SUCCESS: Master Demo Video rendered: {FINAL_MP4.name} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    record_master_demo()
