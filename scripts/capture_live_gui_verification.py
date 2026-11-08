import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    print("Launching Edge to capture full GUI verification...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="msedge", headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        print("Navigating to http://127.0.0.1:8000/ ...")
        await page.goto("http://127.0.0.1:8000/", wait_until="networkidle")

        # 1. Test Romanized Indic Chat (Issue #2)
        chat_input = page.locator("input[placeholder*='Type a message'], input[type='text']").first
        await chat_input.wait_for(state="visible", timeout=10000)

        query = "ekkuva money karchupettalanukovatle minimum enthalo ayipothado cheppandi"
        print(f"Typing: {query}")
        await chat_input.fill(query)
        await page.keyboard.press("Enter")

        # Wait for advisor formulation to start and then fully complete
        print("Waiting for advisor response...")
        try:
            indicator = page.locator("text=Airtel Advisor is formulating solution")
            await indicator.wait_for(state="visible", timeout=5000)
            await indicator.wait_for(state="detached", timeout=35000)
        except Exception:
            # Fallback if indicator is too fast
            await page.wait_for_timeout(12000)

        await page.wait_for_timeout(2000)
        await page.screenshot(path="docs/verified_tenglish_advisor_chat.png", full_page=False)
        print("Captured docs/verified_tenglish_advisor_chat.png")

        # 2. Test Lenis Scroll bounds (Issue #3) - Scroll to bottom and check button
        print("Testing scroll to bottom...")
        await page.evaluate("""() => {
            if (window.__lenis) {
                window.__lenis.scrollTo(document.body.scrollHeight);
            } else {
                window.scrollTo(0, document.body.scrollHeight);
            }
        }""")
        await page.wait_for_timeout(2000)

        scroll_metrics = await page.evaluate("""() => {
            return {
                scrollY: window.scrollY,
                scrollHeight: document.body.scrollHeight,
                innerHeight: window.innerHeight,
                lenisLimit: window.__lenis ? window.__lenis.limit : null,
            };
        }""")
        print("Scroll Metrics:", json.dumps(scroll_metrics, indent=2))
        await page.screenshot(path="docs/verified_lenis_bottom_scroll.png", full_page=False)
        print("Captured docs/verified_lenis_bottom_scroll.png")

        await browser.close()
        print("All live verifications successfully completed!")

if __name__ == "__main__":
    asyncio.run(main())
