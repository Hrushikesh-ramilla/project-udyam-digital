import asyncio
import os
import sys
from playwright.async_api import async_playwright

async def run_audit(cycle_name: str = "cycle_1"):
    out_dir = os.path.join("visual_audit", cycle_name)
    os.makedirs(out_dir, exist_ok=True)
    print(f"=== Starting Visual Audit for {cycle_name} -> {out_dir} ===")

    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True)
        context = await browser.new_context(
            viewport={"width": 1440, "height": 960},
            device_scale_factor=1,
        )
        page = await context.new_page()

        # 1. Studio tab
        print("Navigating to Studio tab...")
        await page.goto("http://127.0.0.1:5173", wait_until="networkidle")
        await page.wait_for_timeout(800)
        await page.screenshot(path=os.path.join(out_dir, "01_studio_default.png"))

        # Click Kirana archetype
        kirana_card = page.locator("text=Kirana & Retail").first
        if await kirana_card.is_visible():
            await kirana_card.click()
            await page.wait_for_timeout(1000)
            await page.screenshot(path=os.path.join(out_dir, "02_studio_kirana_selected.png"))

        # Click Textile archetype
        textile_card = page.locator("text=Textile Mill").first
        if await textile_card.is_visible():
            await textile_card.click()
            await page.wait_for_timeout(1000)
            await page.screenshot(path=os.path.join(out_dir, "03_studio_textile_selected.png"))

        # Scroll to view quote and CTA
        await page.evaluate("window.scrollTo({top: 500, behavior: 'smooth'})")
        await page.wait_for_timeout(800)
        await page.screenshot(path=os.path.join(out_dir, "04_studio_quote_scrolled.png"))

        # 2. Smart KYC tab
        print("Navigating to Smart KYC tab...")
        await page.click('button:has-text("Smart KYC")')
        await page.wait_for_timeout(800)
        await page.screenshot(path=os.path.join(out_dir, "05_kyc_default.png"))

        # Test Applicant K01 (Cancelled GSTIN)
        k01_card = page.locator('text=Applicant K01').first
        if await k01_card.is_visible():
            await k01_card.click()
            await page.wait_for_timeout(300)
            run_btn = page.locator('button:has-text("Run KYC Gate")').first
            await run_btn.click()
            await page.wait_for_timeout(1000)
            await page.screenshot(path=os.path.join(out_dir, "06_kyc_k01_anomaly.png"))

        # Test Applicant K03 (Clean)
        k03_card = page.locator('text=Applicant K03').first
        if await k03_card.is_visible():
            await k03_card.click()
            await page.wait_for_timeout(300)
            run_btn = page.locator('button:has-text("Run KYC Gate")').first
            await run_btn.click()
            await page.wait_for_timeout(1000)
            await page.screenshot(path=os.path.join(out_dir, "07_kyc_k03_approved.png"))

        # Test Document Staging Tab
        staging_tab = page.locator('button:has-text("Live Document Staging")').first
        if await staging_tab.is_visible():
            await staging_tab.click()
            await page.wait_for_timeout(600)
            await page.screenshot(path=os.path.join(out_dir, "08_kyc_document_staging.png"))

        # 3. Fulfillment Pipeline / Tracker
        print("Navigating to Fulfillment tab...")
        await page.click('button:has-text("Fulfillment")')
        await page.wait_for_timeout(800)
        
        # If no active order, click load specimen
        specimen_btn = page.locator('button:has-text("Load Specimen Order")').first
        if await specimen_btn.is_visible():
            await specimen_btn.click()
            await page.wait_for_timeout(600)
        
        await page.screenshot(path=os.path.join(out_dir, "09_fulfillment_initial.png"))

        # Advance stage
        advance_btn = page.locator('button:has-text("Simulate Next SLA Stage")').first
        if await advance_btn.is_visible():
            await advance_btn.click()
            await page.wait_for_timeout(800)
            await page.screenshot(path=os.path.join(out_dir, "10_fulfillment_advanced.png"))

        # 4. Lead Rescue Console
        print("Navigating to Lead Rescue tab...")
        await page.click('button:has-text("Lead Rescue")')
        await page.wait_for_timeout(800)
        await page.screenshot(path=os.path.join(out_dir, "11_lead_rescue_console.png"))

        # 5. Jury Bench
        print("Navigating to Jury Bench tab...")
        await page.click('button:has-text("Jury Bench")')
        await page.wait_for_timeout(800)
        await page.screenshot(path=os.path.join(out_dir, "12_jury_bench_initial.png"))

        # Click scenario K01
        scen_k01 = page.locator('text=Applicant K01: Cancelled GSTIN').first
        if await scen_k01.is_visible():
            await scen_k01.click()
            await page.wait_for_timeout(1000)
            await page.screenshot(path=os.path.join(out_dir, "13_jury_bench_k01_executed.png"))

        await browser.close()
        print(f"=== Visual Audit Completed: 13 captures saved in {out_dir} ===")

if __name__ == "__main__":
    c_name = sys.argv[1] if len(sys.argv) > 1 else "cycle_1"
    asyncio.run(run_audit(c_name))
