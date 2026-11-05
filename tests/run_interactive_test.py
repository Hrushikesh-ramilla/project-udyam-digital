import os
import sys
import time
import subprocess
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = Path(r"C:\Users\ramil\.gemini\antigravity\brain\44f68e35-74f8-4830-880f-2fb391466d88")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

def is_running(url):
    try:
        req = urllib.request.urlopen(url, timeout=1)
        return req.status in (200, 304)
    except Exception:
        return False

def wait_for_url(url, timeout=20):
    start = time.time()
    while time.time() - start < timeout:
        if is_running(url):
            return True
        time.sleep(0.5)
    return False

def main():
    print("=" * 70)
    print("STARTING END-TO-END HUMAN INTERACTION TEST WITH PLAYWRIGHT")
    print("=" * 70)

    backend_proc = None
    frontend_proc = None

    # Check if backend already running
    if not is_running("http://127.0.0.1:8000/api/health"):
        print("Starting backend...")
        env = os.environ.copy()
        env["PYTHONPATH"] = str(PROJECT_ROOT)
        backend_proc = subprocess.Popen(
            [sys.executable, str(PROJECT_ROOT / "run_server.py")],
            cwd=str(PROJECT_ROOT),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        print("Waiting for backend...")
        if not wait_for_url("http://127.0.0.1:8000/api/health", timeout=20):
            print("ERROR: Backend failed to start!")
            sys.exit(1)
    print("Backend is ready at http://127.0.0.1:8000!")

    # Check if frontend already running
    if not is_running("http://localhost:5173"):
        print("Starting frontend...")
        frontend_proc = subprocess.Popen(
            "npm run dev",
            shell=True,
            cwd=str(PROJECT_ROOT / "frontend"),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        print("Waiting for frontend...")
        if not wait_for_url("http://localhost:5173", timeout=20):
            print("ERROR: Frontend failed to start!")
            if backend_proc: backend_proc.kill()
            sys.exit(1)
    print("Frontend is ready at http://localhost:5173!")

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME_PATH, headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        print("\nNavigating to http://localhost:5173 ...")
        page.goto("http://localhost:5173", timeout=30000)
        page.wait_for_timeout(2000)

        # Shot 1: Initial Advisor Screen
        shot1 = ARTIFACT_DIR / "shot1_advisor_initial.png"
        page.screenshot(path=str(shot1))
        print(f"Captured: {shot1.name}")

        chat_input = page.locator("input[placeholder*='Hindi / Hinglish']")
        chat_input.wait_for(state="visible", timeout=10000)

        # Turn 1: Casual, ambiguous, incomplete query
        turn1_text = "arre bhai mere pass chhota sa dukaan h ... kuch internet chahiye sasta wala"
        print(f"\n[Human Turn 1] Typing: '{turn1_text}'")
        chat_input.fill(turn1_text)
        page.wait_for_timeout(600)
        chat_input.press("Enter")

        # Wait for advisor reply (should clarify missing slots without navigating away)
        page.wait_for_timeout(2500)
        shot2 = ARTIFACT_DIR / "shot2_advisor_turn1_ambiguous.png"
        page.screenshot(path=str(shot2))
        print(f"Captured: {shot2.name}")

        # Turn 2: Providing details with typos ('kanpr', '3 bnde', 'gst vst kuch nhi h', 'gpay atak jata h')
        turn2_text = "are bhaiya hum kanpr me h 3 bnde h kam krne wale ... gst vst kuch nhi h gpay atak jata h"
        print(f"\n[Human Turn 2] Typing: '{turn2_text}'")
        chat_input.fill(turn2_text)
        page.wait_for_timeout(600)
        chat_input.press("Enter")

        # Wait for advisor to resolve all slots and formulate recommendation
        page.wait_for_timeout(2000)
        shot3 = ARTIFACT_DIR / "shot3_advisor_turn2_resolved.png"
        page.screenshot(path=str(shot3))
        print(f"Captured: {shot3.name}")

        # Wait for smooth auto-transition to CPQ Cart (or click)
        page.wait_for_timeout(3000)
        if not page.locator("text=Configured Solution").is_visible():
            page.locator("button:has-text('2. Dynamic CPQ Cart')").click()
            page.wait_for_timeout(1500)

        shot4 = ARTIFACT_DIR / "shot4_cpq_cart.png"
        page.screenshot(path=str(shot4))
        print(f"Captured: {shot4.name}")

        # Step 3: Accept Quote & Start Smart KYC
        print("\n[Step 3] Clicking 'Accept Quote & Start Smart KYC'...")
        kyc_btn = page.locator("button:has-text('Accept Quote & Start Smart KYC')")
        kyc_btn.scroll_into_view_if_needed()
        kyc_btn.click()
        page.wait_for_timeout(2000)
        shot5 = ARTIFACT_DIR / "shot5_smart_kyc_gate.png"
        page.screenshot(path=str(shot5))
        print(f"Captured: {shot5.name}")

        # Run Smart KYC on Applicant K03 (Clean)
        print("\nSelecting Applicant K03 and running deterministic KYC gate...")
        page.locator("text=Applicant K03").click()
        page.wait_for_timeout(500)
        page.locator("button:has-text('Run Deterministic KYC Gate')").click()
        page.wait_for_timeout(2500)
        shot6 = ARTIFACT_DIR / "shot6_kyc_verified.png"
        page.screenshot(path=str(shot6))
        print(f"Captured: {shot6.name}")

        # Proceed to Provisioning Tracker
        print("\n[Step 4] Proceeding to Provisioning Tracker...")
        page.locator("button:has-text('Proceed to Provisioning')").click()
        page.wait_for_timeout(2000)
        shot7 = ARTIFACT_DIR / "shot7_provisioning_tracker.png"
        page.screenshot(path=str(shot7))
        print(f"Captured: {shot7.name}")

        # Advance milestone in provisioning tracker
        print("\nAdvancing SLA milestone...")
        page.locator("button:has-text('Simulate Next SLA Milestone')").click()
        page.wait_for_timeout(2000)
        shot8 = ARTIFACT_DIR / "shot8_milestone_advanced.png"
        page.screenshot(path=str(shot8))
        print(f"Captured: {shot8.name}")

        # Switch to Judge Test Bench
        print("\nSwitching to Judge Test Bench...")
        page.locator("button:has-text('Judge Test Bench')").click()
        page.wait_for_timeout(2000)
        # Click on Applicant K01 (Cancelled GSTIN Trap)
        page.locator("text=Applicant K01: Cancelled GSTIN Trap").click()
        page.wait_for_timeout(2500)
        shot9 = ARTIFACT_DIR / "shot9_judge_test_bench_k01.png"
        page.screenshot(path=str(shot9))
        print(f"Captured: {shot9.name}")

        # Switch to Partner ML Rescue Console
        print("\nSwitching to Partner ML Rescue Console...")
        page.locator("button:has-text('Partner ML Rescue')").click()
        page.wait_for_timeout(3000)
        shot10 = ARTIFACT_DIR / "shot10_partner_ml_rescue.png"
        page.screenshot(path=str(shot10))
        print(f"Captured: {shot10.name}")

        browser.close()

    if backend_proc: backend_proc.kill()
    if frontend_proc: frontend_proc.kill()
    print("\n" + "=" * 70)
    print("ALL 10 INTERACTIVE SCREENSHOTS SUCCESSFULLY CAPTURED!")
    print("=" * 70)

if __name__ == "__main__":
    main()
