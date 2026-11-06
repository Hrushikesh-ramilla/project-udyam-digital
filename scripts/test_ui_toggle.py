import sys
import io
from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    page = browser.new_page(viewport={'width': 1400, 'height': 900})
    page.goto('http://127.0.0.1:5173')
    page.wait_for_timeout(1000)

    target_input = page.locator('input[placeholder*="enterprise"], input[placeholder*="message"]').first
    print("Found target input. Typing 'ela unnaru'...")
    target_input.fill('ela unnaru')
    page.keyboard.press('Enter')
    page.wait_for_timeout(2500)

    # Check the chat messages
    messages = page.locator('div.max-h-\\[380px\\]').inner_text()
    print("\n--- INITIAL RESPONSE (Default Latin) ---")
    print(messages[:250])

    has_indic_init = any(0x0900 <= ord(c) <= 0x0D7F for c in messages)
    print(f"Has Indic characters in Latin mode: {has_indic_init}")

    # Click Native Script button
    print("\n--- TOGGLING TO NATIVE SCRIPT ---")
    page.locator('button:has-text("Native Script")').click()
    page.wait_for_timeout(500)
    native_messages = page.locator('div.max-h-\\[380px\\]').inner_text()
    print(native_messages[:250])
    has_indic_native = any(0x0900 <= ord(c) <= 0x0D7F for c in native_messages)
    print(f"Has Indic characters in Native mode: {has_indic_native}")

    # Click English Words button
    print("\n--- TOGGLING BACK TO ENGLISH WORDS ---")
    page.locator('button:has-text("English Words")').click()
    page.wait_for_timeout(500)
    latin_messages = page.locator('div.max-h-\\[380px\\]').inner_text()
    print(latin_messages[:250])
    has_indic_latin = any(0x0900 <= ord(c) <= 0x0D7F for c in latin_messages)
    print(f"Has Indic characters in English Words mode: {has_indic_latin}")

    page.screenshot(path='visual_audit/test_toggle_verification.png', full_page=True)
    print("\nSaved verification screenshot to visual_audit/test_toggle_verification.png")
    browser.close()
