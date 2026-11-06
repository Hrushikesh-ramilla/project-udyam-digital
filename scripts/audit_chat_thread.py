import asyncio
import os
from playwright.async_api import async_playwright

async def run():
    out_dir = os.path.join("visual_audit", "chat_threads")
    os.makedirs(out_dir, exist_ok=True)
    print(f"Starting chat thread audit -> {out_dir}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("http://127.0.0.1:5173", wait_until="networkidle")
        await page.wait_for_timeout(800)

        # 1. Initial State: Showing script format prompt & choice buttons
        await page.screenshot(path=os.path.join(out_dir, "01_chat_initial_prompt.png"))
        print("Captured 01_chat_initial_prompt.png")

        # 2. Click "English Words" choice button
        choice_btn = page.locator('button:has-text("English Words (e.g. \\"bagunnara ela unnaru\\")")').first
        if await choice_btn.is_visible():
            await choice_btn.click()
            await page.wait_for_timeout(600)
            await page.screenshot(path=os.path.join(out_dir, "02_script_choice_clicked.png"))
            print("Captured 02_script_choice_clicked.png")

        # 3. Type "bagunnara ela unnaru" into input
        input_box = page.locator('input[placeholder*="bagunnara"]').first
        if not await input_box.is_visible():
            input_box = page.locator('input[type="text"]').first

        await input_box.fill("bagunnara ela unnaru")
        await page.wait_for_timeout(300)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=os.path.join(out_dir, "03_bagunnara_sent_preserved.png"))
        print("Captured 03_bagunnara_sent_preserved.png")

        # 4. Send follow up business turn in Tenglish: "hyderabad lo 4 staff clinic undi, budget 2500"
        await input_box.fill("hyderabad lo 4 staff clinic undi, budget 2500")
        await page.wait_for_timeout(300)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=os.path.join(out_dir, "04_multi_turn_history_preserved.png"))
        print("Captured 04_multi_turn_history_preserved.png")

        # 5. Test switching back to Native Script using the toggle
        native_toggle = page.locator('button:has-text("Native Script")').first
        if await native_toggle.is_visible():
            await native_toggle.click()
            await page.wait_for_timeout(600)
            await page.screenshot(path=os.path.join(out_dir, "05_switched_to_native_toggle.png"))
            print("Captured 05_switched_to_native_toggle.png")

        await browser.close()
        print("Chat audit finished successfully.")

if __name__ == "__main__":
    asyncio.run(run())
