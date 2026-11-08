import os
import sys
import time
import math
import random
import subprocess
from playwright.sync_api import sync_playwright, Page

def inject_visual_cursor(page: Page):
    cursor_js = """
    (() => {
        if (document.getElementById('playwright-mouse-pointer')) return;
        const cursor = document.createElement('div');
        cursor.id = 'playwright-mouse-pointer';
        cursor.style.width = '24px';
        cursor.style.height = '24px';
        cursor.style.borderRadius = '50%';
        cursor.style.position = 'fixed';
        cursor.style.left = '960px';
        cursor.style.top = '540px';
        cursor.style.zIndex = '9999999';
        cursor.style.pointerEvents = 'none';
        cursor.style.backgroundColor = 'rgba(228, 0, 0, 0.45)';
        cursor.style.border = '2px solid #ffffff';
        cursor.style.boxShadow = '0 0 14px rgba(228, 0, 0, 0.9), 0 0 4px rgba(255, 255, 255, 0.9)';
        cursor.style.transition = 'transform 0.08s ease-out, background-color 0.15s ease';
        cursor.style.transform = 'translate(-50%, -50%)';
        document.body.appendChild(cursor);
        
        window.addEventListener('mousemove', e => {
            cursor.style.left = e.clientX + 'px';
            cursor.style.top = e.clientY + 'px';
        });
        window.addEventListener('mousedown', () => {
            cursor.style.transform = 'translate(-50%, -50%) scale(0.65)';
            cursor.style.backgroundColor = 'rgba(255, 255, 255, 0.95)';
        });
        window.addEventListener('mouseup', () => {
            cursor.style.transform = 'translate(-50%, -50%) scale(1)';
            cursor.style.backgroundColor = 'rgba(228, 0, 0, 0.45)';
        });
    })();
    """
    page.evaluate(cursor_js)

def smooth_move(page: Page, target_x: float, target_y: float, steps: int = 25, delay_ms: float = 12):
    curr = page.evaluate("""() => { 
        const c = document.getElementById('playwright-mouse-pointer'); 
        return c && c.style.left ? {x: parseFloat(c.style.left), y: parseFloat(c.style.top)} : {x: 960, y: 540}; 
    }""")
    start_x, start_y = curr["x"], curr["y"]
    
    for i in range(1, steps + 1):
        t = i / steps
        ease = 0.5 - 0.5 * math.cos(t * math.pi)
        cur_x = start_x + (target_x - start_x) * ease
        cur_y = start_y + (target_y - start_y) * ease
        page.mouse.move(cur_x, cur_y)
        time.sleep(delay_ms / 1000.0)

def human_click(page: Page, locator, steps: int = 20, wait_after: float = 0.4):
    box = locator.bounding_box()
    if box:
        tx = box["x"] + box["width"] / 2
        ty = box["y"] + box["height"] / 2
        smooth_move(page, tx, ty, steps=steps)
        time.sleep(0.1)
        page.mouse.click(tx, ty)
        time.sleep(wait_after)

def human_type(page: Page, locator, text: str, min_delay: float = 0.02, max_delay: float = 0.05):
    human_click(page, locator)
    for char in text:
        page.keyboard.type(char)
        time.sleep(random.uniform(min_delay, max_delay))
    time.sleep(0.3)

def record_full_demo():
    output_dir = "official_demo_recording"
    os.makedirs(output_dir, exist_ok=True)
    
    print("[1/7] Launching Chromium browser with 1920x1080 viewport...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",
            headless=True,
            args=["--start-maximized", "--no-sandbox", "--disable-infobars"]
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=output_dir,
            record_video_size={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        
        print("[2/7] Navigating to https://airtel.hrushikeshramilla.in...")
        page.goto("https://airtel.hrushikeshramilla.in", wait_until="networkidle")
        inject_visual_cursor(page)
        page.wait_for_timeout(2000)
        
        # ---------------------------------------------------------
        # SCENE 1: STUDIO HERO & PRESET ARCHETYPES
        # ---------------------------------------------------------
        print("[SCENE 1] Studio Hero & Archetypes Exploration...")
        # Hover over Navbar MSME vs Partner & Ops
        customer_pill = page.locator("button:has-text('MSME Customer')")
        if customer_pill.count() > 0:
            human_click(page, customer_pill, steps=15, wait_after=0.5)
            
        partner_pill = page.locator("button:has-text('Partner & Ops')")
        if partner_pill.count() > 0:
            # Hover over partner pill to showcase dual persona
            box = partner_pill.bounding_box()
            if box:
                smooth_move(page, box["x"] + box["width"]/2, box["y"] + box["height"]/2, steps=18)
                time.sleep(1.0)
            # Hover back to customer
            if customer_pill.count() > 0:
                box_c = customer_pill.bounding_box()
                if box_c:
                    smooth_move(page, box_c["x"] + box_c["width"]/2, box_c["y"] + box_c["height"]/2, steps=18)
                    time.sleep(0.5)
        
        # Hover over Presets
        presets = page.locator(".grid.grid-cols-2 > div, .grid.grid-cols-4 > div, div:has-text('Kirana & Retail')")
        print(f"  Found {presets.count()} presets/cards")
        for i in range(min(4, presets.count())):
            p_card = presets.nth(i)
            box = p_card.bounding_box()
            if box:
                smooth_move(page, box["x"] + box["width"]/2, box["y"] + box["height"]/2, steps=15)
                time.sleep(0.6)
                
        # ---------------------------------------------------------
        # SCENE 2: CONVERSATIONAL MULTILINGUAL AI ADVISOR
        # ---------------------------------------------------------
        print("[SCENE 2] Conversational Multilingual AI Enterprise Advisor...")
        chat_input = page.locator("input[placeholder*='Type a message' i], textarea[placeholder*='Type a message' i]").first
        
        query_text = (
            "Namaste bhaiya, hamari Lucknow mein ek polyclinic aur diagnostic health center hai "
            "with 4 doctors and 10 staff. Patients ke online MRI reports aur digital billing ke liye "
            "fast fiber internet chahiye, plus static IP aur cloud backup. Mera budget 2500 se 3000 "
            "per month hai. Best plan suggest kijiye."
        )
        
        human_type(page, chat_input, query_text, min_delay=0.015, max_delay=0.035)
        page.wait_for_timeout(500)
        
        # Click Send
        send_btn = page.locator("button:has(svg.lucide-send)").first
        human_click(page, send_btn, steps=15, wait_after=1.0)
        
        # Wait for advisor response
        print("  Waiting for AI Advisor response stream...")
        page.wait_for_timeout(6000)
        
        # Demonstrate Bidirectional Transliteration (Issue #23)
        print("  Toggling Native Script (Devanagari)...")
        native_btn = page.locator("button:has-text('Native Script')").first
        if native_btn.count() > 0:
            human_click(page, native_btn, steps=15, wait_after=2.0)
            
        print("  Toggling back to English Words (Romanized Hinglish)...")
        latin_btn = page.locator("button:has-text('English Words')").first
        if latin_btn.count() > 0:
            human_click(page, latin_btn, steps=15, wait_after=1.5)
            
        # Scroll down to Configured Solution Architecture
        print("  Scrolling smoothly to Configured Solution Architecture...")
        page.evaluate("() => window.scrollBy({ top: 480, behavior: 'smooth' })")
        page.wait_for_timeout(2000)
        
        # Hover over tenure / agreement options
        tenure_btns = page.locator("button:has-text('12 Months'), button:has-text('Annual'), button:has-text('1 Year')")
        if tenure_btns.count() > 0:
            human_click(page, tenure_btns.first, steps=15, wait_after=1.0)
            
        # Click 'Proceed to Instant KYC'
        print("  Clicking 'Proceed to Instant KYC'...")
        kyc_proceed_btn = page.locator("button:has-text('Proceed to Instant KYC'), button:has-text('Accept Quote')").first
        if kyc_proceed_btn.count() > 0:
            human_click(page, kyc_proceed_btn, steps=20, wait_after=2.0)
            
        # ---------------------------------------------------------
        # SCENE 3: SMART KYC ANOMALY TRAPPING & LIVE VERHOEFF
        # ---------------------------------------------------------
        print("[SCENE 3] Smart KYC Anomaly Trapping & Live Verhoeff D5 Checksum...")
        inject_visual_cursor(page)
        page.wait_for_timeout(1000)
        
        # 3A: Test Planted Defect K01 (Cancelled GSTIN)
        k01_specimen = page.locator("button:has-text('K01')").first
        if k01_specimen.count() > 0:
            print("  Staging Applicant K01 (Cancelled GSTIN)...")
            human_click(page, k01_specimen, steps=15, wait_after=1.0)
            
            # Click Verify
            verify_staged_btn = page.locator("button:has-text('Run KYC Verification'), button:has-text('Verify Staged')").first
            if verify_staged_btn.count() > 0:
                print("  Executing adversarial verification on K01...")
                human_click(page, verify_staged_btn, steps=15, wait_after=2.5)
                
            # Demonstrate 2.0% Non-GST Gap Solver Recovery
            udyam_fallback_btn = page.locator("button:has-text('Switch to Udyam Micro-Bundle')").first
            if udyam_fallback_btn.count() > 0:
                print("  Demonstrating Algorithmic Fallback to Udyam Micro-Bundle...")
                human_click(page, udyam_fallback_btn, steps=18, wait_after=2.0)
                
        # 3B: Switch to DigiLocker Fast-Track
        print("  Switching to DigiLocker Fast-Track...")
        digilocker_tab = page.locator("button:has-text('DigiLocker Fast-Track'), button:has-text('DigiLocker Gateway')").first
        if digilocker_tab.count() > 0:
            human_click(page, digilocker_tab, steps=15, wait_after=1.5)
            
        # Demonstrate Live Verhoeff Checksum Typing
        aadhaar_input = page.locator("input[value*='2345'], input[placeholder*='Aadhaar' i]").first
        if aadhaar_input.count() > 0:
            print("  Demonstrating live Verhoeff D5 dihedral check digit validation...")
            box = aadhaar_input.bounding_box()
            if box:
                smooth_move(page, box["x"] + box["width"] - 20, box["y"] + box["height"]/2, steps=15)
                page.mouse.click(box["x"] + box["width"] - 20, box["y"] + box["height"]/2)
                time.sleep(0.3)
                
                # Backspace last digit '4' and type '0' (invalid)
                page.keyboard.press("Backspace")
                page.keyboard.type("0")
                time.sleep(1.8) # Show red error badge
                
                # Correct back to '4' (valid)
                page.keyboard.press("Backspace")
                page.keyboard.type("4")
                time.sleep(1.5) # Show green valid badge
                
        # Click Authenticate & Pull from DigiLocker
        digi_verify_btn = page.locator("button:has-text('Authenticate & Pull from DigiLocker')").first
        if digi_verify_btn.count() > 0:
            print("  Authenticating DigiLocker with zero-persistence DPDP Act 2023 consent...")
            human_click(page, digi_verify_btn, steps=18, wait_after=3.0)
            
        # ---------------------------------------------------------
        # SCENE 4: 6-STAGE TELECOMMUNICATIONS FULFILLMENT
        # ---------------------------------------------------------
        print("[SCENE 4] 6-Stage Telecommunications Fulfillment & Field Tracking...")
        inject_visual_cursor(page)
        page.wait_for_timeout(2000)
        
        # Hover over BlueDart tracking & stage timeline
        bluedart_chip = page.locator("span:has-text('BD-'), div:has-text('BlueDart'), span:has-text('BlueDart')").first
        if bluedart_chip.count() > 0:
            box = bluedart_chip.bounding_box()
            if box:
                smooth_move(page, box["x"] + box["width"]/2, box["y"] + box["height"]/2, steps=15)
                time.sleep(1.5)
                
        # Advance stage
        advance_stage_btn = page.locator("button:has-text('Simulate Next SLA Stage')").first
        if advance_stage_btn.count() > 0:
            print("  Simulating Next SLA Stage progression...")
            human_click(page, advance_stage_btn, steps=18, wait_after=2.5)
            
        # ---------------------------------------------------------
        # SCENE 5: PARTNER OPS AUTONOMOUS WINBACK & WHATSAPP DRAWER
        # ---------------------------------------------------------
        print("[SCENE 5] Partner Ops Autonomous Winback Engine & WhatsApp Recovery...")
        # Switch persona to Partner & Ops
        partner_btn = page.locator("button:has-text('Partner & Ops')").first
        if partner_btn.count() > 0:
            human_click(page, partner_btn, steps=18, wait_after=1.5)
            
        lead_rescue_tab = page.locator("button:has-text('Lead Rescue')").first
        if lead_rescue_tab.count() > 0:
            human_click(page, lead_rescue_tab, steps=15, wait_after=1.5)
            
        # Highlight calibrated KPIs & propensity distribution
        kpi_cards = page.locator(".grid.grid-cols-1.sm\\:grid-cols-3 > div, div:has-text('Recovered ARR Potential')")
        print(f"  Highlighting {kpi_cards.count()} dynamic Winback KPIs...")
        page.wait_for_timeout(1500)
        
        # Click [ 💬 Rescue Lead ] on Amrit & Associates
        rescue_btn = page.locator("button:has-text('Rescue Lead')").first
        if rescue_btn.count() > 0:
            print("  Clicking [ 💬 Rescue Lead ] on Amrit & Associates...")
            human_click(page, rescue_btn, steps=18, wait_after=2.0)
            
            # Modal / Drawer is now open!
            # Click Copy Pitch
            copy_btn = page.locator("button:has-text('Copy Pitch')").first
            if copy_btn.count() > 0:
                print("  Clicking [ 📋 Copy Pitch ]...")
                human_click(page, copy_btn, steps=15, wait_after=1.5)
                
            # Hover over WhatsApp button
            wa_btn = page.locator("a:has-text('Open in WhatsApp'), button:has-text('Open in WhatsApp')").first
            if wa_btn.count() > 0:
                box = wa_btn.bounding_box()
                if box:
                    smooth_move(page, box["x"] + box["width"]/2, box["y"] + box["height"]/2, steps=15)
                    time.sleep(1.0)
                    
            # Click Pre-Hydrate into Cart
            prehydrate_btn = page.locator("button:has-text('Pre-Hydrate into Cart')").first
            if prehydrate_btn.count() > 0:
                print("  Clicking [ ⚡ Pre-Hydrate into Cart ]...")
                human_click(page, prehydrate_btn, steps=18, wait_after=2.5)
                
        # ---------------------------------------------------------
        # SCENE 6: JURY ADVERSARIAL TEST BENCH & OUTRO
        # ---------------------------------------------------------
        print("[SCENE 6] Jury Adversarial Test Bench...")
        # Switch back to Partner persona if needed
        partner_btn = page.locator("button:has-text('Partner & Ops')").first
        if partner_btn.count() > 0:
            human_click(page, partner_btn, steps=15, wait_after=1.0)
            
        jury_tab = page.locator("button:has-text('Jury Bench')").first
        if jury_tab.count() > 0:
            human_click(page, jury_tab, steps=18, wait_after=2.0)
            
            # Click on test cases (e.g. K03 Clean Approval, K07 Name Mismatch)
            k03_bench = page.locator("button:has-text('Applicant K03'), div:has-text('Applicant K03: Clean Approval')").first
            if k03_bench.count() > 0:
                print("  Running Jury Golden Path K03 validation (<200ms)...")
                human_click(page, k03_bench, steps=15, wait_after=2.0)
                
            k07_bench = page.locator("button:has-text('Applicant K07'), div:has-text('Applicant K07: Name Mismatch')").first
            if k07_bench.count() > 0:
                print("  Running Jury RapidFuzz Name Mismatch K07 validation...")
                human_click(page, k07_bench, steps=15, wait_after=2.0)
                
        # Final outro pause on Jury Bench
        page.wait_for_timeout(3000)
        
        print("[7/7] Closing browser context and finalizing recording...")
        context.close()
        browser.close()
        
    # Check recorded video
    recorded_files = [f for f in os.listdir(output_dir) if f.endswith(".webm")]
    if not recorded_files:
        raise RuntimeError("No recorded video found in output directory!")
        
    raw_video = os.path.join(output_dir, recorded_files[0])
    final_mp4 = "Project_Udyam_Digital_Official_Demo.mp4"
    
    print(f"Transcoding {raw_video} to high-definition MP4: {final_mp4}...")
    cmd = [
        "ffmpeg", "-y",
        "-i", raw_video,
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        final_mp4
    ]
    subprocess.run(cmd, check=True)
    size_mb = os.path.getsize(final_mp4) / (1024 * 1024)
    print(f"SUCCESS! Final Official Demo Video rendered: {final_mp4} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    record_full_demo()
