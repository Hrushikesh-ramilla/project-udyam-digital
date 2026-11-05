import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel='chrome')
        page = await browser.new_page(viewport={'width': 1440, 'height': 900})
        await page.goto('http://127.0.0.1:5173')
        await page.click('button:has-text("Smart KYC")')
        await page.wait_for_timeout(600)
        await page.click('button:has-text("Run KYC Gate")')
        await page.wait_for_timeout(1000)
        await page.click('button:has-text("Proceed to Dispatch")')
        await page.wait_for_timeout(1000)
        await page.screenshot(path='crawl_dispatch_active.png')
        print("Captured crawl_dispatch_active.png")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())
