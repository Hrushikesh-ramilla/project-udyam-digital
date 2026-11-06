import asyncio
import os
from playwright.async_api import async_playwright

async def run():
    out_dir = os.path.join("visual_audit", "dual_script_pure")
    os.makedirs(out_dir, exist_ok=True)
    print(f"Auditing clean minimal dual-script chat -> {out_dir}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("http://127.0.0.1:5173", wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # 1. Capture initial side-by-side cards
        await page.screenshot(path=os.path.join(out_dir, "01_initial_left_right_cards.png"))
        print("Captured 01_initial_left_right_cards.png")

        # 2. Click Left Card (English Words)
        left_card = page.locator("text=English Words").first
        await left_card.click()
        await page.wait_for_timeout(600)
        await page.screenshot(path=os.path.join(out_dir, "02_selected_english_words.png"))
        print("Captured 02_selected_english_words.png")

        # 3. Type "bagunnara ela unnaru"
        input_box = page.locator("input[type='text']").first
        await input_box.fill("bagunnara ela unnaru")
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(2500)
        await page.screenshot(path=os.path.join(out_dir, "03_bagunnara_latin_preserved.png"))
        print("Captured 03_bagunnara_latin_preserved.png")

        # 4. Click Native Script toggle at the top
        native_toggle = page.locator("button:has-text('Native Script')").first
        await native_toggle.click()
        await page.wait_for_timeout(800)
        await page.screenshot(path=os.path.join(out_dir, "04_toggled_to_native_history_switched.png"))
        print("Captured 04_toggled_to_native_history_switched.png")

        # 5. Click English Words toggle at the top
        english_toggle = page.locator("button:has-text('English Words')").first
        await english_toggle.click()
        await page.wait_for_timeout(800)
        await page.screenshot(path=os.path.join(out_dir, "05_toggled_back_to_english_words.png"))
        print("Captured 05_toggled_back_to_english_words.png")

        # 6. Click archetype "Polyclinic & Health"
        poly_card = page.locator("text=Polyclinic & Health").first
        await poly_card.click()
        await page.wait_for_timeout(3000)
        await page.screenshot(path=os.path.join(out_dir, "06_archetype_quote_and_chat_preserved.png"))
        print("Captured 06_archetype_quote_and_chat_preserved.png")

        # 7. Switch toggle again to Native Script on full conversation
        await native_toggle.click()
        await page.wait_for_timeout(800)
        await page.screenshot(path=os.path.join(out_dir, "07_full_conversation_switched_to_native.png"))
        print("Captured 07_full_conversation_switched_to_native.png")

        await browser.close()
        print("All verification screenshots captured successfully!")

if __name__ == "__main__":
    asyncio.run(run())
