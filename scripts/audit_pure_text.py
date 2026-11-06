import asyncio
import os
from playwright.async_api import async_playwright

async def run():
    out_dir = os.path.join("visual_audit", "pure_text_messages")
    os.makedirs(out_dir, exist_ok=True)
    print(f"Auditing pure text message chat -> {out_dir}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("http://127.0.0.1:5173", wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # 1. Initial State: Two simple side-by-side text bubbles, zero badges/labels/buttons
        await page.screenshot(path=os.path.join(out_dir, "01_pure_text_side_by_side.png"))
        print("Captured 01_pure_text_side_by_side.png")

        # 2. Click Left Message (English Words)
        left_msg = page.locator("text=Namaste! Mee business ki Airtel Enterprise").first
        await left_msg.click()
        await page.wait_for_timeout(600)
        await page.screenshot(path=os.path.join(out_dir, "02_left_bubble_activated.png"))
        print("Captured 02_left_bubble_activated.png")

        # 3. Type user message "bagunnara ela unnaru"
        input_box = page.locator("input[type='text']").first
        await input_box.fill("bagunnara ela unnaru")
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(2500)
        await page.screenshot(path=os.path.join(out_dir, "03_user_message_pure_text.png"))
        print("Captured 03_user_message_pure_text.png")

        # 4. Toggle Script to Native Script
        native_toggle = page.locator("button:has-text('Native Script')").first
        await native_toggle.click()
        await page.wait_for_timeout(800)
        await page.screenshot(path=os.path.join(out_dir, "04_switched_to_native_pure_text.png"))
        print("Captured 04_switched_to_native_pure_text.png")

        await browser.close()
        print("Audit completed successfully!")

if __name__ == "__main__":
    asyncio.run(run())
