import os
from playwright.sync_api import sync_playwright

def test_record():
    os.makedirs("test_video", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir="test_video/",
            record_video_size={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        page.goto("https://airtel.hrushikeshramilla.in", wait_until="networkidle")
        page.wait_for_timeout(2000)
        context.close()
        browser.close()
        
    videos = os.listdir("test_video")
    print("Videos recorded:", videos)

if __name__ == "__main__":
    test_record()
