from playwright.sync_api import sync_playwright

def test_studio():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto("https://airtel.hrushikeshramilla.in", wait_until="networkidle")
        
        print("Page title:", page.title())
        
        # 1. Type Hinglish message into chat
        chat_input = page.locator("input[placeholder*='Type a message' i], textarea[placeholder*='Type a message' i]")
        print("Chat input count:", chat_input.count())
        
        msg = "Namaste bhaiya, hamari Lucknow mein ek polyclinic aur diagnostic health center hai with 4 doctors and 10 staff. Patients ke online MRI reports aur digital billing ke liye fast fiber internet chahiye, plus static IP aur cloud backup. Mera budget 2500 se 3000 per month hai. Best plan suggest kijiye."
        
        chat_input.first.fill(msg)
        print("Filled input")
        
        # Send button
        send_btn = page.locator("button:has(svg.lucide-send)")
        print("Send btn count:", send_btn.count())
        send_btn.first.click()
        print("Clicked send. Waiting for advisor response...")
        
        page.wait_for_timeout(6000)
        
        # Check messages
        advisor_msgs = page.locator(".bg-slate-900\\/90, .bg-\\[\\#111827\\]").all_text_contents()
        print("Found messages:", len(advisor_msgs))
        
        # Check script toggle
        native_btn = page.locator("button:has-text('Native Script')")
        print("Native Script btn count:", native_btn.count())
        if native_btn.count() > 0:
            native_btn.first.click()
            print("Switched to Native Script")
            page.wait_for_timeout(1000)
            
        latin_btn = page.locator("button:has-text('English Words')")
        if latin_btn.count() > 0:
            latin_btn.first.click()
            print("Switched back to English Words")
            page.wait_for_timeout(1000)
            
        # Check Cart
        kyc_btn = page.locator("button:has-text('Proceed to Instant KYC')")
        print("Proceed to Instant KYC count:", kyc_btn.count())
        
        # Take screenshot
        page.screenshot(path="studio_chat_verified.png")
        print("Screenshot saved to studio_chat_verified.png")
        browser.close()

if __name__ == "__main__":
    test_studio()
