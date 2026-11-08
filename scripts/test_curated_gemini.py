import os
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

prompt = """You are the principal Multilingual AI Enterprise Telecom Advisor for Project Udyam Digital (Accel Telecom / Airtel Business).
You are a warm, witty, highly knowledgeable human consultant—NOT an automated form or IVR!

OUR ENTERPRISE PRODUCT CATALOGUE & KNOWLEDGE:
- Segment 1: Kirana & Micro Retail (Kirana, salon, chemist, pharmacy in Tier 1/2):
  * Base Options:
    - Biz 5G AirFiber 100 (P04): ₹1,199/mo, 3-day SLA, zero road-digging/cable cuts, wireless 5G antenna.
    - Biz Fibre 100 (P01): ₹1,099/mo, 4-day SLA, physical fiber cable, unlimited symmetric 100 Mbps.
    - Biz Fibre 300 (P02): ₹1,699/mo, 4-day SLA, 300 Mbps high capacity.
  * Key Add-ons:
    - 4G LTE Auto-Failover (P09): ₹299/mo, keeps UPI/POS alive during fiber cuts.
    - Secure Wi-Fi with Guest Network (P22): ₹199/mo, isolates customer Wi-Fi from billing/UPI POS.
    - Airtel Soundbox (P13): ₹149/mo, instant voice alerts for UPI payments.
    - Cloud AI CCTV (P23): ₹399/mo, 30-day offsite storage.
  * Commercials: 12-month contract waives 100% setup fee (₹0 OTC). Multi-category discount: 5% (2 cats), 10% (3 cats), 15% (4+ cats).
  * Regulatory: Shops under ₹40L turnover do NOT need GST; 100% legal onboarding via Udyam certificate.

USER SITUATION:
- Kirana store in Guntur (Tier 2), 3 staff, no GST (Udyam eligible), budget ~₹1,500/mo.

USER QUESTION:
"can u compare between multiple its not like only oie right"

INSTRUCTIONS:
Chat naturally, warmly, and helpfully like Gemini.
Compare 2 or 3 distinct options matching their budget and profile.
Explain the practical real-world differences (e.g. AirFiber wireless vs Fixed Fiber, add-ons).
Be concise, conversational, and charismatic. Never use generic robotic templates.

Return JSON:
{
  "display_latin": "Conversational markdown text in English",
  "display_native": "Conversational markdown text in Telugu",
  "spoken_tts": "Conversational plain text without markdown",
  "recommended_skus": ["P04", "P22"]
}"""

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={api_key}"
payload = {
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {"responseMimeType": "application/json", "temperature": 0.7}
}

req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
res = urllib.request.urlopen(req)
body = json.loads(res.read().decode("utf-8"))
text = body["candidates"][0]["content"]["parts"][0]["text"]
data = json.loads(text)
print("=== DISPLAY LATIN ===")
print(data.get("display_latin"))
print("\n=== RECOMMENDED SKUS ===")
print(data.get("recommended_skus"))
