import asyncio
import os
from playwright.async_api import async_playwright

async def run():
    out_dir = os.path.join("visual_audit", "zero_initial_text")
    os.makedirs(out_dir, exist_ok=True)
    print(f"Auditing zero initial text chat -> {out_dir}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("http://127.0.0.1:5173", wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # 1. Capture initial state: Zero text previously, only the clean input box
        await page.screenshot(path=os.path.join(out_dir, "01_zero_initial_text_only_input.png"))
        print("Captured 01_zero_initial_text_only_input.png")

        # 2. Type "bagunnara ela unnaru" and press Enter
        input_box = page.locator("input[type='text']").first
        await input_box.fill("bagunnara ela unnaru")
        await page.screenshot(path=os.path.join(out_dir, "02_typed_in_input.png"))
        print("Captured 02_typed_in_input.png")

        await page.keyboard.press("Enter")
        await page.wait_for_timeout(2500)
        await page.screenshot(path=os.path.join(out_dir, "03_response_generated_preserved.png"))
        print("Captured 03_response_generated_preserved.png")

        # 3. Toggle to Native Script
        native_toggle = page.locator("button:has-text('Native Script')").first
        await native_toggle.click()
        await page.wait_for_timeout(800)
        await page.screenshot(path=os.path.join(out_dir, "04_switched_to_native.png"))
        print("Captured 04_switched_to_native.png")

        # 4. Toggle back to English Words
        english_toggle = page.locator("button:has-text('English Words')").first
        await english_toggle.click()
        await page.wait_for_timeout(800)
        await page.screenshot(path=os.path.join(out_dir, "05_switched_back_to_english_words.png"))
        print("Captured 05_switched_back_to_english_words.png")

        await browser.close()
        print("Zero text verification audit finished successfully!")

if __name__ == "__main__":
    asyncio.run(run())
