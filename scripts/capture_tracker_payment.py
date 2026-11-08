import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="msedge", headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        await page.goto("http://127.0.0.1:8000/", wait_until="networkidle")

        # Go to Fulfillment tab
        await page.locator("button:has-text('Fulfillment')").first.click()
        await page.wait_for_timeout(1000)

        # Click Load Specimen Order
        load_btn = page.locator("button:has-text('Load Specimen Order')").first
        if await load_btn.count() > 0:
            await load_btn.click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path="docs/verified_order_tracker_live.png", full_page=False)
            print("Captured docs/verified_order_tracker_live.png")

            # Click Pay Online
            pay_btn = page.locator("button:has-text('Pay Online')").first
            if await pay_btn.count() > 0:
                await pay_btn.click()
                await page.wait_for_timeout(2000)
                await page.screenshot(path="docs/verified_payment_modal_qr.png", full_page=False)
                print("Captured docs/verified_payment_modal_qr.png")

                # Switch to Razorpay Sandbox tab
                rzp_tab = page.locator("button:has-text('Razorpay Sandbox')").first
                if await rzp_tab.count() > 0:
                    await rzp_tab.click()
                    await page.wait_for_timeout(1000)
                    await page.screenshot(path="docs/verified_payment_modal_razorpay.png", full_page=False)
                    print("Captured docs/verified_payment_modal_razorpay.png")

        await browser.close()
        print("Done capturing tracker & payment modals!")

if __name__ == "__main__":
    asyncio.run(main())
