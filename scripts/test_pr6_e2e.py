import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    print("Launching Edge to test PR #6...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="msedge", headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        print("Navigating to http://127.0.0.1:8000/ ...")
        await page.goto("http://127.0.0.1:8000/", wait_until="networkidle")

        # 1. Test Chat with Romanized Telugu query (Issue #2)
        print("Finding chat input...")
        chat_input = page.locator("textarea, input[type='text']").first
        await chat_input.wait_for(state="visible", timeout=10000)

        query = "ekkuva money karchupettalanukovatle minimum enthalo ayipothado cheppandi"
        print(f"Typing Romanized Telugu query: '{query}'...")
        await chat_input.fill(query)
        await page.keyboard.press("Enter")

        # Wait for advisor response
        print("Waiting for advisor response...")
        await page.wait_for_timeout(4000)

        # Take screenshot of chat
        await page.screenshot(path="docs/audit_pr6_tenglish_chat.png", full_page=False)
        print("Saved docs/audit_pr6_tenglish_chat.png")

        # Extract message texts
        messages = await page.locator(".whitespace-pre-line, .prose, .chat-bubble").all_text_contents()
        print("\n--- Extracted Messages in DOM ---")
        for m in messages:
            print("Message snippet:", m[:120].strip())

        # 2. Test Lenis Scroll bounds (Issue #3)
        # Send another query to expand chat
        await chat_input.fill("Gwalior lo maaku clinic undi, 3 doctors unnaru. Best plan cheppandi.")
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(4000)

        # Scroll to bottom
        print("\nTesting scroll to bottom...")
        scroll_info_before = await page.evaluate("""() => {
            return {
                scrollY: window.scrollY,
                scrollHeight: document.body.scrollHeight,
                innerHeight: window.innerHeight,
                lenisLimit: window.lenis ? window.lenis.limit : null,
                lenisScroll: window.lenis ? window.lenis.scroll : null,
            };
        }""")
        print("Scroll info before scroll:", json.dumps(scroll_info_before, indent=2))

        # Scroll to bottom using window.scrollTo and Lenis scrollTo if present
        await page.evaluate("""() => {
            if (window.lenis) {
                window.lenis.scrollTo(document.body.scrollHeight);
            } else {
                window.scrollTo(0, document.body.scrollHeight);
            }
        }""")
        await page.wait_for_timeout(1500)

        scroll_info_after = await page.evaluate("""() => {
            return {
                scrollY: window.scrollY,
                scrollHeight: document.body.scrollHeight,
                innerHeight: window.innerHeight,
                lenisLimit: window.lenis ? window.lenis.limit : null,
                lenisScroll: window.lenis ? window.lenis.scroll : null,
            };
        }""")
        print("Scroll info after scroll:", json.dumps(scroll_info_after, indent=2))

        # Capture bottom screenshot
        await page.screenshot(path="docs/audit_pr6_bottom_scroll.png", full_page=False)
        print("Saved docs/audit_pr6_bottom_scroll.png")

        await browser.close()
        print("\nE2E Verification Complete!")

if __name__ == "__main__":
    asyncio.run(main())
