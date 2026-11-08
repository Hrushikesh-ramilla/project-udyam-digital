import urllib.request
import json
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

test_cases = [
    {
        "lang": "en",
        "name": "English",
        "script_mode": "latin",
        "query": "Hello, I run a retail store with 5 employees and need reliable broadband under 2000 rupees."
    },
    {
        "lang": "te",
        "name": "Telugu (Romanized / Tenglish)",
        "script_mode": "latin",
        "query": "ekkuva money karchupettalanukovatle minimum enthalo ayipothado cheppandi"
    },
    {
        "lang": "te",
        "name": "Telugu (Native Script)",
        "script_mode": "native",
        "query": "మాకు 5గురు ఉద్యోగులు ఉన్నారు, తక్కువ బడ్జెట్‌లో మంచి ఇంటర్నెట్ కావాలి"
    },
    {
        "lang": "hi",
        "name": "Hindi (Romanized / Hinglish)",
        "script_mode": "latin",
        "query": "zyada paise kharch nahi karna chahte minimum kitne me ho jayega bataiye"
    },
    {
        "lang": "hi",
        "name": "Hindi (Native Devanagari)",
        "script_mode": "native",
        "query": "नमस्ते, हमारी 10 लोगों की टीम है और हमें कॉलिंग और इंटरनेट चाहिए"
    },
    {
        "lang": "ta",
        "name": "Tamil (Romanized / Tanglish)",
        "script_mode": "latin",
        "query": "vanakkam, enga kadai ku nalla internet connection venum budget kulla sollunga"
    },
    {
        "lang": "ta",
        "name": "Tamil (Native Script)",
        "script_mode": "native",
        "query": "வணக்கம், எங்கள் கடைக்கு நல்ல இணைய இணைப்பு மற்றும் காலிங் தேவை"
    },
    {
        "lang": "bn",
        "name": "Bengali (Romanized / Banglish)",
        "script_mode": "latin",
        "query": "nomoshkar, amader choto dokaner jonno bhalo internet lagbe kom damer moddhe"
    },
    {
        "lang": "bn",
        "name": "Bengali (Native Script)",
        "script_mode": "native",
        "query": "নমস্কার, আমাদের ব্যবসার জন্য ভালো ইন্টারনেট সংযোগ প্রয়োজন"
    },
    {
        "lang": "gu",
        "name": "Gujarati (Romanized)",
        "script_mode": "latin",
        "query": "kem cho, amari dukan mate sasto ane saro internet plan batavo"
    },
    {
        "lang": "gu",
        "name": "Gujarati (Native Script)",
        "script_mode": "native",
        "query": "નમસ્તે, અમારે નાની દુકાન માટે સારો ઇન્ટરનેટ પ્લાન જોઈએ છે"
    },
    {
        "lang": "kn",
        "name": "Kannada (Romanized)",
        "script_mode": "latin",
        "query": "namaskara, namma angadige olle internet connection beku kammi dharayalli"
    },
    {
        "lang": "kn",
        "name": "Kannada (Native Script)",
        "script_mode": "native",
        "query": "ನಮಸ್ಕಾರ, ನಮ್ಮ ವ್ಯಾಪಾರಕ್ಕೆ ಕಡಿಮೆ ವೆಚ್ಚದಲ್ಲಿ ಇಂಟರ್ನೆಟ್ ಸಂಪರ್ಕ ಬೇಕು"
    },
    {
        "lang": "mr",
        "name": "Marathi (Romanized)",
        "script_mode": "latin",
        "query": "namaskar, aamchya dukanasathi kami kharchat changla internet plan sanga"
    },
    {
        "lang": "mr",
        "name": "Marathi (Native Devanagari)",
        "script_mode": "native",
        "query": "नमस्कार, आमच्या दुकानासाठी कमी खर्चात चांगला इंटरनेट प्लॅन सांगा"
    },
    {
        "lang": "ml",
        "name": "Malayalam (Romanized)",
        "script_mode": "latin",
        "query": "namaskaram, njangalude kadaykk nalla internet connection venam kuranja chilavil"
    },
    {
        "lang": "ml",
        "name": "Malayalam (Native Script)",
        "script_mode": "native",
        "query": "നമസ്കാരം, ഞങ്ങളുടെ സ്ഥാപനത്തിന് മികച്ച ഇന്റർനെറ്റ് കണക്ഷൻ വേണം"
    },
    {
        "lang": "or",
        "name": "Odia (Romanized)",
        "script_mode": "latin",
        "query": "namaskar, aama dokan pain bhal internet connection darkar kam poisa re"
    },
    {
        "lang": "or",
        "name": "Odia (Native Script)",
        "script_mode": "native",
        "query": "ନମସ୍କାର, ଆମ ଦୋକାନ ପାଇଁ ଭଲ ଇଣ୍ଟରନେଟ୍ ସଂଯୋଗ ଦରକାର"
    },
    {
        "lang": "auto",
        "name": "Auto Detect (Hinglish)",
        "script_mode": "latin",
        "query": "dukan ke liye sasta broadband plan batao bhai jaldi se"
    }
]

print(f"=== TESTING ADVISOR ACROSS ALL {len(test_cases)} LANGUAGE & SCRIPT CONFIGURATIONS ===")

passed = 0
failed = 0

for i, tc in enumerate(test_cases, 1):
    payload = json.dumps({
        "user_message": tc["query"],
        "language_code": tc["lang"],
        "script_mode": tc["script_mode"],
        "history": []
    }).encode("utf-8")
    
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/advisor/chat",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            display_md = data.get("display_markdown", "")
            display_latin = data.get("display_latin", "")
            display_native = data.get("display_native", "")
            skus = data.get("recommended_skus", [])
            tts = data.get("spoken_tts_text", "")
            slots = data.get("extracted_slots", {})
            
            print(f"\n[{i}/{len(test_cases)}] {tc['name']} (lang={tc['lang']}, script={tc['script_mode']})")
            print(f"  User Query : {tc['query']}")
            print(f"  Active Mode: {tc['script_mode']}")
            print(f"  Display MD : {display_md[:95]}...")
            print(f"  Latin Text : {display_latin[:95]}...")
            print(f"  Native Text: {display_native[:95]}...")
            print(f"  Voice TTS  : {tts[:85]}...")
            print(f"  SKUs       : {skus}")
            if slots:
                print(f"  Slots      : {slots}")
            
            # Validation assertions
            assert len(display_md) > 0, "Empty markdown display"
            assert len(tts) > 0, "Empty TTS readout"
            
            passed += 1
    except Exception as e:
        print(f"\n[{i}/{len(test_cases)}] FAILED: {tc['name']} -> {e}")
        failed += 1

print("\n" + "=" * 70)
print(f"SUMMARY: {passed} passed, {failed} failed out of {len(test_cases)} tests.")
print("=" * 70)
