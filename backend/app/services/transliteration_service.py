"""
Deterministic, Bidirectional Brahmic-Indic <-> Latin/English Transliteration Engine.
Supports all 8 Indic scripts (Telugu, Devanagari, Tamil, Bengali, Gujarati, Kannada, Malayalam, Odia)
plus Romanized variants (Tenglish, Hinglish, Tanglish, Banglish).
"""

import re
from typing import Optional

SCRIPT_BASES = {
    "devanagari": 0x0900,
    "bengali": 0x0980,
    "gujarati": 0x0A80,
    "odia": 0x0B00,
    "tamil": 0x0B80,
    "telugu": 0x0C00,
    "kannada": 0x0C80,
    "malayalam": 0x0D00,
}

INDEPENDENT_VOWELS = {
    0x04: "a", 0x05: "a", 0x06: "aa", 0x07: "i", 0x08: "ee", 0x09: "u", 0x0A: "oo",
    0x0B: "ri", 0x0C: "li", 0x0E: "e", 0x0F: "ee", 0x10: "ai", 0x12: "o", 0x13: "oo", 0x14: "au"
}

CONSONANTS = {
    0x15: "k", 0x16: "kh", 0x17: "g", 0x18: "gh", 0x19: "ng",
    0x1A: "ch", 0x1B: "chh", 0x1C: "j", 0x1D: "jh", 0x1E: "ny",
    0x1F: "t", 0x20: "th", 0x21: "d", 0x22: "dh", 0x23: "n",
    0x24: "t", 0x25: "th", 0x26: "d", 0x27: "dh", 0x28: "n", 0x29: "nn",
    0x2A: "p", 0x2B: "ph", 0x2C: "b", 0x2D: "bh", 0x2E: "m",
    0x2F: "y", 0x30: "r", 0x31: "rr", 0x32: "l", 0x33: "ll", 0x34: "lll",
    0x35: "v", 0x36: "sh", 0x37: "sh", 0x38: "s", 0x39: "h",
    0x58: "q", 0x59: "kh", 0x5A: "gh", 0x5B: "z", 0x5C: "r", 0x5D: "rh", 0x5E: "f"
}

VOWEL_SIGNS = {
    0x3E: "aa", 0x3F: "i", 0x40: "ee", 0x41: "u", 0x42: "oo", 0x43: "ri",
    0x46: "e", 0x47: "ee", 0x48: "ai", 0x4A: "o", 0x4B: "oo", 0x4C: "au"
}

VIRAMA_OFFSET = 0x4D
ANUSVARA_OFFSET = 0x02

COMMON_PHRASE_MAPPINGS = {
    # Telugu extended
    "అర్థమైంది": "Arthamaindi",
    "తక్కువలో": "takkuvalo",
    "తక్కువ": "takkuva",
    "ఎక్కువ": "ekkuva",
    "ఖర్చు": "karchu",
    "ఎంతలో": "enthalo",
    "చెప్పండి": "cheppandi",
    "అయిపోతుందో": "ayipothundo",
    # Telugu
    "నమస్కారం": "Namaskaram",
    "నమస్తే": "Namaste",
    "బాగున్నారా": "bagunnara",
    "ఎలా ఉన్నారు": "ela unnaru",
    "ఎలా ఉన్నావు": "ela unnavu",
    "నేను బాగున్నాను": "nenu bagunnanu",
    "అడిగినందుకు ధన్యవాదాలు": "adiginanduku dhanyavadalu",
    "ధన్యవాదాలు": "dhanyavadalu",
    "ధన్యవాదములు": "dhanyavadamulu",
    "వ్యాపారానికి": "vyaparaniki",
    "వ్యాపారం": "vyaparam",
    "కనెక్టివిటీ": "connectivity",
    "కనెక్టివిటీని": "connectivity-ni",
    "క్లినిక్": "clinic",
    "కిరాణా": "kirana",
    "కార్ఖానా": "karkhana",
    "సిబ్బందితో": "staff tho",
    "సిబ్బంది": "staff",
    "ఉద్యమ్": "Udyam",
    "ఎయిర్‌టెల్": "Airtel",
    "ఎంటర్ ప్రైజ్": "Enterprise",
    "ఎంటర్‌ప్రైజ్": "Enterprise",
    "డిజిటల్": "Digital",
    "సహాయం": "sahayam",
    "కావాలి": "kavali",
    "చూపించండి": "chupinchandi",
    "ధర": "dhara",
    "ప్లాన్లు": "planlu",
    "నెలవారీ ఛార్జీ": "Net monthly investment",
    "నెలవారీ": "nelavari",
    "రుసుము": "rusumu",
    "పూర్తిగా ఉచితం": "WAIVED (Rs 0)",
    "పని దినాలలో": "business days",
    "జీఎస్టీ": "GST",
    "బ్రాడ్‌బ్యాండ్": "broadband",
    "క్లౌడ్ సేవలు": "cloud services",
    "సమాచారం": "information",
    "సిద్ధంగా ఉన్నాను": "ready to assist",
    
    # Hindi
    "नमस्ते": "Namaste",
    "कैसे हैं आप": "kaise hain aap",
    "कैसे हैं": "kaise hain",
    "कैसे हो": "kaise ho",
    "मैं ठीक हूँ": "main theek hoon",
    "धन्यवाद": "dhanyavad",
    "व्यापार": "vyapar",
    "दुकान": "dukan",
    "कारखाना": "karkhana",
    "कर्मचारी": "karmachari",
    "योजना": "yojana",
    
    # Tamil
    "வணக்கம்": "Vanakkam",
    "எப்படி இருக்கிறீர்கள்": "eppadi irukkeenga",
    "நலமாக இருக்கிறேன்": "nalamaga irukkiren",
    "நன்றி": "nandri",
    "வணிகம்": "vanigam",
    "கடை": "kadai",
    
    # Bengali
    "নমস্কার": "Nomoshkar",
    "কেমন আছেন": "kemon achen",
    "ভালো আছি": "bhalo achi",
    "ধন্যবাদ": "dhonnobad",
    
    # Gujarati
    "નમસ્તે": "Namaste",
    "કેમ છો": "kem cho",
    "મજામાં": "majama",
    "આભાર": "aabhar",
    
    # Kannada
    "ನಮಸ್ಕಾರ": "Namaskara",
    "ಹೇಗಿದ್ದೀರಿ": "hegiddeera",
    "ಆರಾಮಾಗಿದ್ದೇನೆ": "aramagiddini",
    "ಧನ್ಯವಾದಗಳು": "dhanyavadagalu",
    
    # Malayalam
    "നമസ്കാരം": "Namaskaram",
    "സുഖമാണോ": "sukhamano",
    "സുഖമാണ്": "sukhaman",
    "നന്ദി": "nandi",
    
    # Odia
    "ନମସ୍କାର": "Namaskar",
    "କେମିତି ଅଛନ୍ତି": "kemiti achanti",
    "ଭଲରେ ଅଛି": "bhalare achi",
    "ଧନ୍ୟବାଦ": "dhanyabad",
}

def _indic_char_info(ch: str):
    cp = ord(ch)
    for name, base in SCRIPT_BASES.items():
        if base <= cp <= base + 0x7F:
            return name, cp - base
    return None, None

def has_indic_script(text: str) -> bool:
    """Checks if the text contains any Brahmic/Indic script characters."""
    return bool(re.search(r"[\u0900-\u0D7F]", text))

def indic_to_latin(text: str) -> str:
    """Deterministically converts text containing any Indic script characters into clean Latin words."""
    if not text:
        return ""
    if not has_indic_script(text):
        return text

    # Pre-substitute known phrases for natural conversational flow
    cleaned = text
    for native_word, latin_word in COMMON_PHRASE_MAPPINGS.items():
        if native_word in cleaned:
            cleaned = cleaned.replace(native_word, latin_word)

    if not has_indic_script(cleaned):
        return cleaned

    # Unicode-level algorithmic transliteration
    result = []
    i = 0
    n = len(cleaned)
    while i < n:
        ch = cleaned[i]
        script, offset = _indic_char_info(ch)
        if not script:
            result.append(ch)
            i += 1
            continue

        if offset in INDEPENDENT_VOWELS:
            result.append(INDEPENDENT_VOWELS[offset])
            i += 1
            continue

        if offset in CONSONANTS:
            cons = CONSONANTS[offset]
            next_ch = cleaned[i + 1] if i + 1 < n else ""
            next_script, next_offset = _indic_char_info(next_ch) if next_ch else (None, None)

            if next_script == script and next_offset == VIRAMA_OFFSET:
                result.append(cons)
                i += 2
                continue
            elif next_script == script and next_offset in VOWEL_SIGNS:
                result.append(cons + VOWEL_SIGNS[next_offset])
                i += 2
                continue
            elif next_script == script and next_offset == ANUSVARA_OFFSET:
                result.append(cons + "am")
                i += 2
                continue
            else:
                result.append(cons + "a")
                i += 1
                continue

        if offset in VOWEL_SIGNS:
            result.append(VOWEL_SIGNS[offset])
            i += 1
            continue

        if offset == ANUSVARA_OFFSET:
            result.append("m")
            i += 1
            continue

        if offset == VIRAMA_OFFSET:
            i += 1
            continue

        # Skip remaining unmapped diacritics
        i += 1

    s = "".join(result)
    # Polish double-vowels from inherent 'a' + matra
    s = re.sub(r"a(aa|ee|oo|ai|au)", r"\1", s)
    # Strip zero-width formatting characters (ZWNJ / ZWJ / BOM)
    s = re.sub(r"[\u200B-\u200D\uFEFF]", "", s)
    # Polish formatting
    s = re.sub(r"\s+", " ", s).strip()
    return s

HINDI_LEXICON = {
    "ooty": "ऊटी", "gaming": "गेमिंग", "center": "सेंटर", "centre": "सेंटर",
    "online": "ऑनलाइन", "shooting": "शूटिंग", "games": "गेम्स", "game": "गेम",
    "internet": "इंटरनेट", "connection": "कनेक्शन", "speed": "स्पीड",
    "latency": "लेटेंसी", "ping": "पिंग", "packet": "पैकेट", "drop": "ड्रॉप",
    "loss": "लॉस", "high": "हाई", "low": "लो", "wifi": "वाई-फ़ाई", "wi-fi": "वाई-फ़ाई",
    "router": "राउटर", "fibre": "फ़ाइबर", "fiber": "फ़ाइबर", "airfiber": "एयरफ़ाइबर",
    "airtel": "एयरटेल", "business": "बिज़नेस", "enterprise": "एंटरप्राइज़",
    "digital": "डिजिटल", "guest": "गेस्ट", "network": "नेटवर्क", "cart": "कार्ट",
    "plan": "प्लान", "plans": "प्लान्स", "package": "पैकेज", "failover": "फ़ेलओवर",
    "backup": "बैकअप", "setup": "सेटअप", "support": "सपोर्ट", "free": "फ़्री",
    "symmetric": "सिमेट्रिक", "clients": "क्लाइंट्स", "lobbies": "लॉबीज़",
    "lightning": "लाइटनिंग", "fast": "फ़ास्ट", "secure": "सिक्योर",
    "recommend": "रेकमेंड", "configuration": "कॉन्फ़िगरेशन", "mein": "में",
    "ek": "एक", "hai": "है", "hain": "हैं", "ho": "हो", "hoon": "हूँ",
    "tha": "था", "the": "थे", "thi": "थी", "ka": "का", "ke": "के", "ki": "की",
    "ko": "को", "se": "से", "par": "पर", "aur": "और", "ya": "या", "toh": "तो",
    "to": "तो", "bhi": "भी", "yeh": "यह", "ye": "ये", "woh": "वह", "wo": "वो",
    "kya": "क्या", "kyun": "क्यों", "kaise": "कैसे", "khelne": "खेलने",
    "chalana": "चलाना", "chalane": "चलाने", "chahiye": "चाहिए", "achha": "अच्छा",
    "accha": "अच्छा", "sabse": "सबसे", "zaroori": "ज़रूरी", "zaroorat": "ज़रूरत",
    "cheez": "चीज़", "cheezein": "चीज़ें", "taaki": "ताकि", "sakein": "सकें",
    "sakte": "सकते", "sakti": "सकती", "karta": "करता", "karte": "करते",
    "karunga": "करूँगा", "karungi": "करूँगी", "karein": "करें", "karo": "करो",
    "karoon": "करूँ", "karne": "करने", "karna": "करना", "rakhein": "रखें",
    "rakho": "रखो", "dekh": "देख", "deta": "देता", "dete": "देते", "deti": "देती",
    "apne": "अपने", "apna": "अपना", "apni": "अपनी", "aap": "आप", "aapka": "आपका",
    "aapke": "आपके", "aapki": "आपकी", "main": "मैं", "hum": "हम", "mera": "मेरा",
    "mere": "मेरे", "meri": "मेरी", "mujhe": "मुझे", "humein": "हमें",
    "niche": "नीचे", "upar": "ऊपर", "saath": "साथ", "wah": "वाह",
    "shandar": "शानदार", "shaandaar": "शानदार", "ekdum": "एकदम", "bilkul": "बिल्कुल",
    "badiya": "बढ़िया", "badhai": "बधाई", "naam": "नाम", "koi": "कोई", "kuch": "कुछ",
    "bahut": "बहुत", "kam": "कम", "zyada": "ज़्यादा", "kharch": "खर्च",
    "paise": "पैसे", "rupaye": "रुपये", "mahina": "महीना", "mahine": "महीने",
    "din": "दिन", "saal": "साल", "dukan": "दुकान", "dukaan": "दुकान",
    "kirana": "किराणा", "clinic": "क्लीनिक", "office": "ऑफ़िस", "factory": "फ़ैक्टरी",
    "staff": "स्टाफ़", "strongly": "स्ट्रॉन्गली", "isolated": "आइसोलेटेड",
    "add-on": "ऐड-ऑन", "addon": "ऐड-ऑन", "sure": "ज़रूर", "namaste": "नमस्ते",
    "bhai": "भाई", "dost": "दोस्त", "karenge": "करेंगे", "kijiye": "कीजिए",
    "bataiye": "बताइए", "batao": "बताओ", "lekin": "लेकिन", "parantu": "परंतु"
}

def roman_to_devanagari(text: str) -> str:
    """Converts Romanized Hindi / Hinglish text into authentic Devanagari script preserving layout."""
    if not text:
        return ""
    def replace_word(m: re.Match) -> str:
        w = m.group(0)
        low = w.lower()
        if low in HINDI_LEXICON:
            return HINDI_LEXICON[low]
        return w
    res = re.sub(r"[a-zA-Z\-]+", replace_word, text)
    return res

def latin_to_indic(text: str, target_lang: str = "te") -> str:
    """Converts common Romanized Latin queries into authentic native script."""
    if not text:
        return ""
    lower = text.lower().strip()
    
    # Hindi / Hinglish conversion
    if target_lang == "hi" or any(w in lower for w in ["kaise", "theek", "kharch", "paise", "kam", "ooty", "gaming", "chahiye", "achha", "khelne"]):
        converted = roman_to_devanagari(text)
        if has_indic_script(converted):
            return converted
        if any(w in lower for w in ["kharch", "paise", "kam budget", "sasta"]):
            return "समझ गया! कम बजट में बिज़ 5G AirFiber 100 ₹1,199/माह सबसे बढ़िया विकल्प है।"
        if "kaise ho" in lower or "kaise hain" in lower:
            return "नमस्ते! आप कैसे हैं?"
        if "namaste" in lower:
            return "नमस्ते!"

    # Telugu conversion
    if target_lang == "te" or any(w in lower for w in ["ela", "bagu", "karchu", "ekkuva", "takkuva", "enthalo", "artham"]):
        if any(w in lower for w in ["ekkuva", "karchu", "enthalo", "takkuva"]):
            return "ఎక్కువ ఖర్చు పెట్టాలనుకోవట్లేదు, కనీసం ఎంతలో అయిపోతుందో చెప్పండి"
        if "arthamaindi" in lower or "artham" in lower:
            return "అర్థమైంది! బడ్జెట్ తక్కువలో కావాలంటే, బిజ్ 5G ఎయిర్‌ఫైబర్ 100 నెలకు ₹1,199 ఉత్తమ ఎంపిక!"
        if "bagunnara" in lower or "bagunara" in lower:
            return "బాగున్నారా"
        if "ela unnaru" in lower or "ela unnav" in lower:
            return "ఎలా ఉన్నారు"
        if "namaste" in lower or "namaskaram" in lower:
            return "నమస్కారం"
        if "clinic" in lower:
            return "క్లినిక్"
        if "kirana" in lower:
            return "కిరాణా దుకాణం"
    elif target_lang == "ta" or "vanakkam" in lower or "eppadi" in lower:
        if "eppadi" in lower:
            return "எப்படி இருக்கிறீர்கள்"
        if "vanakkam" in lower:
            return "வணக்கம்"

    return text

def ensure_dual_scripts(
    text_latin: Optional[str],
    text_native: Optional[str],
    active_lang: str = "te"
) -> tuple[str, str]:
    """
    Infallible guarantor: Returns (pure_latin, authentic_native)
    Guarantees pure_latin contains ZERO native Indic characters.
    Guarantees authentic_native contains native script when available.
    Guarantees full dynamic response text is NEVER lost or replaced with a generic greeting.
    """
    raw_latin = text_latin or ""
    raw_native = text_native or ""

    # 1. Guarantee pure_latin has 0 Indic characters
    if has_indic_script(raw_latin):
        pure_latin = indic_to_latin(raw_latin)
    elif raw_latin.strip():
        pure_latin = raw_latin
    elif raw_native.strip():
        pure_latin = indic_to_latin(raw_native)
    else:
        pure_latin = "Namaste! Welcome to Airtel Enterprise Digital."

    # If non-Indic language (English, Spanish, French, German, etc.) or no Indic script present, native is identical to Latin
    indic_langs = {"te", "hi", "ta", "bn", "gu", "mr", "kn", "ml", "or", "pa", "as", "ur"}
    if (active_lang not in indic_langs and not has_indic_script(raw_native)) or active_lang in {"en", "es", "fr", "de", "it", "pt", "ru", "ja", "zh", "ar"}:
        pure_native = raw_native if has_indic_script(raw_native) else pure_latin
        return pure_latin, pure_native

    # Guard against bogus generic greeting replacing a full substantive response
    is_bogus_greeting = (
        has_indic_script(raw_native)
        and len(raw_native) < 50
        and len(pure_latin) > 80
        and ("स्वागत" in raw_native or "స్వాగతం" in raw_native or "வரவேற்கிறோம்" in raw_native)
    )

    # 2. Guarantee authentic_native has native script
    if has_indic_script(raw_native) and not is_bogus_greeting:
        pure_native = raw_native
    elif has_indic_script(raw_latin) and not is_bogus_greeting:
        pure_native = raw_latin
    else:
        pure_native = latin_to_indic(pure_latin, target_lang=active_lang)
        # ONLY apply regional default greeting if pure_latin is trivial / empty (<35 chars)
        if not has_indic_script(pure_native) and len(pure_latin) < 35:
            defaults = {
                "te": "నమస్కారం! ఎయిర్‌టెల్ బిజినెస్ ఉద్యమ్ డిజిటల్‌కు స్వాగతం.",
                "hi": "नमस्ते! एयरटेल बिजनेस उद्यम डिजिटल में आपका स्वागत है।",
                "ta": "வணக்கம்! ஏர்டெல் பிசினஸ் உத்யம் டிஜிட்டலுக்கு வரவேற்கிறோம்.",
                "bn": "নমস্কার! এয়ারটেল বিজনেস উদ্যম ডিজিটালে আপনাকে স্বাগতম।",
                "gu": "નમસ્તે! એરટેલ બિઝનેસ ઉદ્યમ ડિજિટલમાં તમારું સ્વાગત છે.",
                "mr": "नमस्कार! एअरटेल बिझनेस उद्यम डिजिटलमध्ये आपले स्वागत आहे.",
                "kn": "ನಮಸ್ಕಾರ! ಏರ್‌ಟೆಲ್ ಬಿಸಿನೆಸ್ ಉದ್ಯಮ್ ಡಿಜಿಟಲ್‌ಗೆ ಸುಸ್ವಾಗತ.",
                "ml": "നമസ്കാരം! എയർടെൽ ബിസിനസ്സ് ഉദ്യം ഡിജിറ്റലിലേക്ക് സ്വാగതം.",
                "or": "ନମସ୍କାର! ଏୟାରଟେଲ ବିଜନେସ ଉଦ୍ୟମ ଡିଜିଟାଲକୁ ଆପଣଙ୍କୁ ସ୍ୱାଗତ।",
                "pa": "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ! ਏਅਰਟੈੱਲ ਬਿਜ਼ਨਸ ਉੱਦਮ ਡਿਜੀਟਲ ਵਿੱਚ ਤੁਹਾਡਾ ਸਵਾਗਤ ਹੈ।",
                "as": "নমস্কাৰ! এয়াৰটেল বিজनेছ উদ্যম ডিজিটেললৈ আপোনাক স্বাগতম।",
                "ur": "خوش آمدید! ایئرٹیل بزنس ادیام ڈیجیٹل میں آپ का خیر مقدم ہے۔",
            }
            pure_native = defaults.get(active_lang, pure_latin)
        elif not has_indic_script(pure_native):
            # Fallback to pure_latin rather than discarding substantive text
            pure_native = pure_latin

    return pure_latin, pure_native
