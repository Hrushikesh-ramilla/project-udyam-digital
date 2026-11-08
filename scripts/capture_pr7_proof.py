import asyncio
from playwright.async_api import async_playwright

async def main():
    print("Launching Edge to capture unconstrained multilingual UI...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="msedge", headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        await page.goto("http://127.0.0.1:8000/", wait_until="networkidle")

        # 1. Capture clean UI showing the new universal multilingual badge and removed chips
        await page.wait_for_timeout(1000)
        await page.screenshot(path="docs/verified_universal_multilingual_ui.png", full_page=False)
        print("Captured docs/verified_universal_multilingual_ui.png")

        # 2. Type 'Hello'
        chat_input = page.locator("input[placeholder*='Type or speak'], input[type='text']").first
        await chat_input.fill("Hello")
        await page.keyboard.press("Enter")

        # Wait for instant greeting response
        await page.wait_for_timeout(1000)

        # 3. Toggle to 'Native Script'
        native_btn = page.locator("button:has-text('Native Script')").first
        if await native_btn.count() > 0:
            await native_btn.click()
            await page.wait_for_timeout(1000)

        await page.screenshot(path="docs/verified_english_native_script_purity.png", full_page=False)
        print("Captured docs/verified_english_native_script_purity.png")

        await browser.close()
        print("GUI captures completed!")

if __name__ == "__main__":
    asyncio.run(main())
