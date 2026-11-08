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
        chat_input = page.locator("textarea, input[type='text']").first
        await chat_input.wait_for(state="visible", timeout=10000)

        query = "ekkuva money karchupettalanukovatle minimum enthalo ayipothado cheppandi"
        print(f"Typing: {query}")
        await chat_input.fill(query)
        await page.keyboard.press("Enter")

        # Wait for advisor reply to render
        await page.wait_for_timeout(6000)
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

        # 3. Test Navigation to Fulfillment Tracker & Logistics / Payments
        print("Navigating to Fulfillment Tracker...")
        tracker_tab = page.locator("button:has-text('Fulfillment')").first
        if await tracker_tab.count() > 0:
            await tracker_tab.click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path="docs/verified_tracker_logistics.png", full_page=False)
            print("Captured docs/verified_tracker_logistics.png")

            # Click Pay Online button to open payment drawer
            pay_btn = page.locator("button:has-text('Pay Online')").first
            if await pay_btn.count() > 0:
                await pay_btn.click()
                await page.wait_for_timeout(1500)
                await page.screenshot(path="docs/verified_payment_modal_npci_upi.png", full_page=False)
                print("Captured docs/verified_payment_modal_npci_upi.png")

        await browser.close()
        print("GUI Verification Complete!")

if __name__ == "__main__":
    asyncio.run(main())
