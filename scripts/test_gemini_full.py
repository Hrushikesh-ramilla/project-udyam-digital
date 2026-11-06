import os
import json
from google import genai

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def test_query(text: str, script_mode: str = "latin"):
    prompt = f"""You are the principal Multilingual AI Enterprise Telecom Advisor for Project Udyam Digital (Accel Telecom / Airtel Business).
You are a warm, witty, charismatic, and highly intelligent human advisor—NOT a robotic form filler or IVR!

User message: "{text}"
Preferred Script mode: {script_mode}

GUIDELINES FOR YOUR CONVERSATIONAL RESPONSE:
1. NEVER dump a generic, canned, bullet-point questionnaire or repetitive template.
2. If the user greets in any language (e.g. "hola", "bonjour", "namaste", "bagunnara"), warmly acknowledge their greeting in that language or cultural style with genuine hospitality.
3. If the user asks something off-topic (e.g. recipe, weather, movie, joke, poetry, coding), respond with witty charm, playful personality, and a natural chuckle, then seamlessly ask if they run a business (like a cafe, studio, tech firm) that needs blazing fiber broadband.
4. If the user gives terse or ambiguous input (e.g. "internet", "price", "speed"), respond with high energy and ask 1 single natural, friendly question about their setup.
5. If the user writes in Romanized Indic (e.g. Tenglish, Hinglish, Tanglish like "bagunnara ela unnaru nenu kotha business start chesthunna"), respond naturally in that EXACT conversational style!
6. Generate both:
   - "display_latin": Natural conversational markdown reply in pure English alphabet (Latin characters only, zero Indic script characters).
   - "display_native": The corresponding natural response in authentic native Indic script (or English if foreign/unrelated).
   - "spoken_tts": A short, friendly 1-2 sentence voice TTS version without markdown symbols.
7. Extract business slots if mentioned (segment, city_tier, employee_count, num_sites, has_gstin, detected_needs, monthly_budget_cap).

Return STRICTLY valid JSON:
{{
  "segment": "micro" | "prof" | "multi" | "mfg" | null,
  "city_tier": 1 | 2 | 3 | null,
  "employee_count": integer or null,
  "num_sites": integer or null,
  "has_gstin": true | false | null,
  "detected_needs": ["broadband", "wifi", "calling", "cloud", "security", "cctv", "iot"],
  "monthly_budget_cap": integer or null,
  "display_latin": "Conversational markdown response in English alphabet",
  "display_native": "Conversational markdown response in native Indic script",
  "spoken_tts": "Natural plain text voice response"
}}"""

    for mod in ["gemini-flash-lite-latest", "gemini-flash-latest"]:
        try:
            res = client.models.generate_content(
                model=mod,
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            return json.loads(res.text)
        except Exception as e:
            print(f"Model {mod} failed: {e}")
            continue
    return None

queries = [
    "hola",
    "how do I make Hyderabadi biryani",
    "internet",
    "bagunnara ela unnaru",
    "bagunnara ela unnaru nenu kotha business start chesthunna"
]

for q in queries:
    res = test_query(q)
    print("=" * 60)
    print("USER:", q)
    if res:
        print("LATIN:", res.get("display_latin"))
        print("SLOTS:", {k: v for k, v in res.items() if k in ["segment", "city_tier", "employee_count", "has_gstin"] and v is not None})
    else:
        print("FAILED TO GET RESPONSE")
