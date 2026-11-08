import os
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto("https://airtel.hrushikeshramilla.in", wait_until="networkidle")
        
        buttons = page.locator("button").all_text_contents()
        with open("ui_buttons.txt", "w", encoding="utf-8") as f:
            for i, b in enumerate(buttons):
                f.write(f"{i}: {b.strip()}\n")
        
        # Take a full page screenshot to verify styling
        page.screenshot(path="studio_screenshot.png", full_page=True)
        print("Inspection saved to ui_buttons.txt and studio_screenshot.png")
        browser.close()

if __name__ == "__main__":
    inspect()
