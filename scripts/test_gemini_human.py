import os
import json
from google import genai

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

queries = [
    "hola",
    "how do I make Hyderabadi biryani",
    "internet",
    "bgunnara ela unaru",
    "bagunnara ela unnaru nenu kotha business start chesthunna",
    "clnic hydrbad 10 staff"
]

for q in queries:
    prompt = f"""You are a warm, charismatic, sharp, highly intelligent human-like AI Enterprise Advisor for Airtel Business (Project Udyam Digital).
User query: "{q}"

Task:
1. Understand the intent, language, and cultural tone.
2. If it's a greeting in another language (e.g. Spanish "hola"), warmly acknowledge it in that language or English and pivot to business telecom.
3. If it's unrelated or whimsical (e.g. biryani recipe, weather), respond with wit, personality, and charm, then playfully check if they run a restaurant, cafe, or business that needs rock-solid fiber connectivity.
4. If it's terse (e.g. "internet", "plans"), be proactive, energetic, and ask a single natural qualifying question.
5. If it's Romanized Indic (e.g. Tenglish, Hinglish), reply authentically in that EXACT conversational Romanized style (NOT robotic textbook translation).
6. Extract slots if mentioned (business type, city, staff, etc.).
7. Keep the response concise, punchy (2-4 lines), human, and helpful. Never dump a robotic 3-bullet checklist!

Output valid JSON:
{{
  "reply_latin": "Natural conversational response in English alphabet (matching Romanized Indic if applicable)",
  "reply_native": "Same natural response rendered in authentic native Indic script (or English if foreign/unrelated)",
  "segment": "micro" | "prof" | "multi" | "mfg" | null,
  "city_tier": 1 | 2 | 3 | null,
  "employee_count": integer or null,
  "detected_needs": []
}}
"""
    try:
        resp = client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        data = json.loads(resp.text)
        print(f"QUERY: {q}")
        print(f"LATIN: {data.get('reply_latin')}")
        print(f"NATIVE: {data.get('reply_native')}")
        print("-" * 50)
    except Exception as e:
        print(f"ERROR for '{q}': {e}")
