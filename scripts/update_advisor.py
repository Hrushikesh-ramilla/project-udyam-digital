import re

with open("backend/app/services/advisor_agent.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update _extract_slots_with_gemini signature and prompt
old_func_sig = """    def _extract_slots_with_gemini(
        self, text: str, existing_slots: Optional[MSMEProfileSlots] = None
    ) -> Optional[tuple[MSMEProfileSlots, Optional[str], Optional[str]]]:"""

new_func_sig = """    def _extract_slots_with_gemini(
        self,
        text: str,
        existing_slots: Optional[MSMEProfileSlots] = None,
        language_code: Optional[str] = None,
        script_mode: Optional[str] = None,
    ) -> Optional[tuple[MSMEProfileSlots, Optional[str], Optional[str]]]:"""

if old_func_sig in code:
    code = code.replace(old_func_sig, new_func_sig, 1)
    print("Replaced _extract_slots_with_gemini signature.")
else:
    print("Warning: old_func_sig not found")

# Add script instruction into prompt inside _extract_slots_with_gemini
old_prompt_block = '''        prompt = f"""You are the principal Multilingual AI Enterprise Telecom Advisor for Project Udyam Digital (Accel Telecom / Airtel Business).
Analyze this user query in any Indian language: Telugu, Tamil, Bengali, Gujarati, Marathi, Kannada, Malayalam, Odia, Hindi, Hinglish, or English:
\\"{text}\\"

Extract MSME business slots and generate a natural, culturally attuned response IN THE EXACT SAME REGIONAL LANGUAGE AND SCRIPT that the user used (e.g. Telugu script for Telugu, Tamil script for Tamil, Bengali script for Bengali, etc.).'''

new_prompt_block = '''        script_instruction = ""
        if script_mode == "latin":
            script_instruction = (
                "\\nCRITICAL SCRIPT INSTRUCTION: The user prefers ROMANIZED / LATIN SCRIPT (using ONLY standard English alphabet phonetically for the regional language, "
                "e.g. Tenglish 'bagunnara ela unnaru' for Telugu, Hinglish for Hindi, Tanglish for Tamil). "
                "DO NOT use Devanagari or any native Indic characters. Write display_markdown and spoken_tts entirely in English alphabet."
            )
        elif script_mode == "native":
            script_instruction = (
                "\\nCRITICAL SCRIPT INSTRUCTION: The user prefers AUTHENTIC NATIVE SCRIPT "
                "(e.g. Telugu script for Telugu, Tamil script for Tamil, Devanagari for Hindi). Write display_markdown in the native script."
            )
        elif re.search(r"\\b(bagunnara|ela\\s*unnaru|ela\\s*unnav|kavali|cheppandi|kaise\\s*ho|kya\\s*haal|theek\\s*hai|vanakkam|eppadi\\s*iruk|kemon\\s*acho|kem\\s*cho|kase\\s*ahat|hegidd|sukhamano)\\b", text.lower()):
            script_instruction = (
                "\\nCRITICAL SCRIPT INSTRUCTION: The user is writing in ROMANIZED / LATIN SCRIPT (regional language written using English alphabet). "
                "Respond in the SAME regional language using English alphabet (e.g. Tenglish, Hinglish, Tanglish). DO NOT switch to native Indic script."
            )

        prompt = f"""You are the principal Multilingual AI Enterprise Telecom Advisor for Project Udyam Digital (Accel Telecom / Airtel Business).
Analyze this user query in any Indian language: Telugu, Tamil, Bengali, Gujarati, Marathi, Kannada, Malayalam, Odia, Hindi, Hinglish, or English:
\\"{text}\\"
{script_instruction}

Extract MSME business slots and generate a natural, culturally attuned response in the user's requested regional language and script mode.'''

if old_prompt_block in code:
    code = code.replace(old_prompt_block, new_prompt_block, 1)
    print("Replaced prompt block in _extract_slots_with_gemini.")
else:
    print("Warning: old_prompt_block not found")

# 2. Update process_turn signature and greeting handling
old_process_sig = """    def process_turn(self, user_message: str, previous_slots: Optional[MSMEProfileSlots] = None) -> AdvisorResponse:"""
new_process_sig = """    def process_turn(
        self,
        user_message: str,
        previous_slots: Optional[MSMEProfileSlots] = None,
        language_code: Optional[str] = None,
        script_mode: Optional[str] = None,
    ) -> AdvisorResponse:"""

if old_process_sig in code:
    code = code.replace(old_process_sig, new_process_sig, 1)
    print("Replaced process_turn signature.")
else:
    print("Warning: old_process_sig not found")

# Replace the gemini call in process_turn:
old_gemini_call = """        # Attempt Gemini LLM enhancement for conversational nuances
        gemini_result = self._extract_slots_with_gemini(user_message, slots)"""

new_gemini_call = """        # Attempt Gemini LLM enhancement for conversational nuances
        gemini_result = self._extract_slots_with_gemini(
            user_message, slots, language_code=language_code, script_mode=script_mode
        )"""

if old_gemini_call in code:
    code = code.replace(old_gemini_call, new_gemini_call, 1)
    print("Replaced gemini_result call in process_turn.")
else:
    print("Warning: old_gemini_call not found")

# Replace greeting block with multi-script Romanized and Native handling
old_greeting_block = """        # Friendly casual greeting handling across 8 Regional Indic Languages
        clean_msg = user_message.strip().lower()
        regional_greetings = [
            "నమస్కారం", "నమస్తే", "బాగున్నారా", # Telugu
            "வணக்கம்", "ஹலோ", "நலமா", # Tamil
            "নমস্কার", "নমস্তে", "কেমন আছেন", # Bengali
            "નમસ્તે", "કેમ છો", "નમસ્કાર", # Gujarati
            "नमस्कार", "कसे आहात", # Marathi
            "ನಮಸ್ಕಾರ", "ಹೇಗಿದ್ದೀರಿ", # Kannada
            "നമസ്കാരം", "സുഖമാണോ", # Malayalam
            "ନମସ୍କାର", "କେମିତି ଅଛନ୍ତି" # Odia
        ]
        is_greeting = bool(re.search(r"^(hey|hi|hello|whats\\s*up|what\\'s\\s*up|namaste|kem\\s*cho|kaise\\s*ho|kya\\s*haal|good\\s*(morning|evening|afternoon)|yo|sup|bhai|bhaiya)\\b", clean_msg)) or any(g in clean_msg for g in regional_greetings)
        has_business_info = bool(slots.segment or slots.city_tier or slots.has_gstin is not None or slots.detected_needs)

        if is_greeting and not has_business_info:
            welcome_md = gemini_md or (
                "### Namaste! Welcome to Airtel Business Udyam Digital 🙏\\n\\n"
                "I am doing great! I am your AI Enterprise Telecom Advisor. Tell me a bit about your business:\\n"
                "* What kind of business do you run (e.g. retail shop, clinic, CA office, factory)?\\n"
                "* Which city and approximately how many staff?\\n"
                "* Do you have a registered GSTIN or Udyam certificate?"
            )
            welcome_tts = gemini_tts or "Namaste! Airtel Business Udyam Digital mein aapka swagat hai. Kripya batayein ki aap kis sheher mein hain aur aapka business kis type ka hai."
            return AdvisorResponse(
                slots=slots,
                quote=None,
                recommended_skus=[],
                display_markdown=welcome_md,
                spoken_tts_text=welcome_tts,
                next_suggested_prompts=[
                    "I run a Kirana store in Tier 2 with no GST",
                    "We are a CA office in Mumbai with GST",
                    "We have a factory in Surat with 30 staff",
                ],
            )"""

new_greeting_block = """        # Friendly casual greeting handling across 8 Regional Indic Languages (Native Script + English/Latin Romanized)
        clean_msg = user_message.strip().lower()
        has_indic_script = bool(re.search(r"[\u0900-\u0D7F]", user_message))
        effective_script = script_mode or ("native" if has_indic_script else "latin")

        # Detect active language
        active_lang = language_code or "en"
        if re.search(r"[\\u0C00-\\u0C7F]", user_message) or re.search(r"\\b(bagunnara|bagunara|ela\\s*unnaru|ela\\s*unnav|namaskaram|namasthe|kavali|kavala|enti|eppudu|undi|ledu|meeru)\\b", clean_msg):
            active_lang = "te"
        elif re.search(r"[\\u0B80-\\u0BFF]", user_message) or re.search(r"\\b(vanakkam|eppadi\\s*iruk|nalama|sollunga|irukku|illa|venum|ungalukku)\\b", clean_msg):
            active_lang = "ta"
        elif re.search(r"[\\u0980-\\u09FF]", user_message) or re.search(r"\\b(nomoshkar|kemon\\s*ac|bhalo|lagbe|nei|apnar)\\b", clean_msg):
            active_lang = "bn"
        elif re.search(r"[\\u0A80-\\u0AFF]", user_message) or re.search(r"\\b(kem\\s*cho|majama|tamare|joie|nathi)\\b", clean_msg):
            active_lang = "gu"
        elif re.search(r"\\b(kase\\s*ahat|pahije|ahe|nahi|tumhi)\\b", clean_msg):
            active_lang = "mr"
        elif re.search(r"[\\u0C80-\\u0CFF]", user_message) or re.search(r"\\b(namaskara|hegidd|hegiddira|beku|illa|nimma)\\b", clean_msg):
            active_lang = "kn"
        elif re.search(r"[\\u0D00-\\u0D7F]", user_message) or re.search(r"\\b(namaskaram|sukhamano|sukham\\s*anu|venam|illa|ningal)\\b", clean_msg):
            active_lang = "ml"
        elif re.search(r"[\\u0B00-\\u0B7F]", user_message) or re.search(r"\\b(kemiti\\s*ach|bhalare|darkar|nahin|apana)\\b", clean_msg):
            active_lang = "or"
        elif re.search(r"[\\u0900-\\u097F]", user_message) or re.search(r"\\b(kaise\\s*ho|kya\\s*haal|sab\\s*theek|bhai|bhaiya|chahiye|aapka)\\b", clean_msg):
            active_lang = "hi"

        regional_greetings_native = [
            "నమస్కారం", "నమస్తే", "బాగున్నారా", "ఎలా ఉన్నారు", # Telugu
            "வணக்கம்", "ஹலோ", "நலமா", "எப்படி இருக்கிறீர்கள்", # Tamil
            "নমস্কার", "নমস্তে", "কেমন আছেন", # Bengali
            "નમસ્તે", "કેમ છો", "નમસ્કાર", # Gujarati
            "नमस्कार", "कसे आहात", # Marathi
            "ನಮಸ್ಕಾರ", "ಹೇಗಿದ್ದೀರಿ", # Kannada
            "നമസ്കാരം", "സുഖമാണോ", # Malayalam
            "ନମସ୍କାର", "କେମିତି ଅଛନ୍ତି" # Odia
        ]
        regional_greetings_latin = [
            "bagunnara", "bagunara", "ela unnaru", "ela unnav", "namaskaram", "namasthe",
            "vanakkam", "eppadi irukkeenga", "eppadi irukinga", "nalama",
            "nomoshkar", "kemon acho", "kemon achen",
            "kem cho", "majama",
            "kase ahat",
            "hegiddeera", "hegiddiri", "namaskara",
            "sukhamano", "sukham anu",
            "kemiti achanti",
            "kaise ho", "kya haal", "sab theek", "namaste"
        ]

        is_greeting = (
            bool(re.search(r"^(hey|hi|hello|whats\\s*up|what\\'s\\s*up|good\\s*(morning|evening|afternoon)|yo|sup|bhai|bhaiya)\\b", clean_msg))
            or any(g in clean_msg for g in regional_greetings_native)
            or any(g in clean_msg for g in regional_greetings_latin)
        )
        has_business_info = bool(slots.segment or slots.city_tier or slots.has_gstin is not None or slots.detected_needs)

        if is_greeting and not has_business_info:
            # Script-aware, culturally attuned regional responses
            greetings_map = {
                "te": {
                    "native": (
                        "### నమస్కారం! నేను బాగున్నాను, ధన్యవాదాలు 🙏\\n\\n"
                        "మీరు ఎలా ఉన్నారు? ఎయిర్‌టెల్ బిజినెస్ ఉద్యమ్ డిజిటల్‌కు స్వాగతం.\\n"
                        "మీ వ్యాపారానికి సరిపోయే ఉత్తమమైన కనెక్టివిటీ ప్లాన్ కోసం వివరాలు తెలపండి:\\n"
                        "* మీ వ్యాపారం ఏ రకమైనది (ఉదా. కిరాణా షాప్, క్లినిక్, సిఏ ఆఫీస్, ఫ్యాక్టరీ)?\\n"
                        "* ఏ ఊరు మరియు ఎంతమంది సిబ్బంది?\\n"
                        "* మీకు జిఎస్టీ (GSTIN) లేదా ఉద్యమ్ సర్టిఫికేట్ ఉందా?",
                        "నమస్కారం! నేను బాగున్నాను ధన్యవాదాలు. మీరు ఎలా ఉన్నారు? ఎయిర్‌టెల్ బిజినెస్ ఉద్యమ్ డిజిటల్‌కు స్వాగతం. మీ వ్యాపారానికి ఎలాంటి కనెక్టివిటీ కావాలి?"
                    ),
                    "latin": (
                        "### Namaskaram! Nenu bagunnanu, dhanyavadalu 🙏\\n\\n"
                        "Meeru ela unnaru? Welcome to Airtel Business Udyam Digital.\\n"
                        "Mee business ki saripoye best plan kosam ee details cheppandi:\\n"
                        "* Mee business elantidi (e.g. Kirana store, Clinic, CA office, Factory)?\\n"
                        "* Ee oori lo undi mariyu entha mandi staff unnaru?\\n"
                        "* Meeku GST number unda leda sirf Udyam certificate matrame unda?",
                        "Namaskaram! Nenu bagunnanu, dhanyavadalu. Meeru ela unnaru? Welcome to Airtel Business Udyam Digital. Mee business ki elanti internet connectivity kavali?"
                    ),
                },
                "ta": {
                    "native": (
                        "### வணக்கம்! நான் நலமாக இருக்கிறேன், நன்றி 🙏\\n\\n"
                        "நீங்கள் எப்படி இருக்கிறீர்கள்? ஏர்டெல் பிசினஸ் உத்யம் டிஜிட்டலுக்கு வரவேற்கிறோம்.\\n"
                        "உங்கள் வணிகத்திற்கு சிறந்த திட்டத்தைத் தேர்ந்தெடுக்க விவரங்களைக் கூறுங்கள்:\\n"
                        "* உங்கள் வணிகம் எத்தகையது (எ.கா. மளிகைக் கடை, கிளினிக், சிஏ அலுவலகம், தொழிற்சாலை)?\\n"
                        "* எந்த ஊர் மற்றும் எத்தனை பணியாளர்கள்?\\n"
                        "* உங்களிடம் ஜிஎஸ்டி உள்ளதா அல்லது உத்யம் சான்றிதழ் மட்டுமா?",
                        "Vanakkam! Naan nalamaga irukkiren nandri. Neenga eppadi irukkeenga? Airtel Business Udyam Digital-ukku varaverkirom."
                    ),
                    "latin": (
                        "### Vanakkam! Naan nallaa irukken, nandri 🙏\\n\\n"
                        "Neenga eppadi irukkeenga? Welcome to Airtel Business Udyam Digital.\\n"
                        "Ungal business-ku seriyana plan select panna indha details sollunga:\\n"
                        "* Enna madhiri business panreenga (e.g. Maligai kadai, Clinic, CA office, Factory)?\\n"
                        "* Endha ooru and ethanai staff irukkanga?\\n"
                        "* Ungalukku GST number irukka illa Udyam mattum dhaana?",
                        "Vanakkam! Naan nallaa irukken nandri. Neenga eppadi irukkeenga? Welcome to Airtel Business Udyam Digital."
                    ),
                },
                "hi": {
                    "native": (
                        "### नमस्ते! मैं बहुत अच्छा हूँ, धन्यवाद 🙏\\n\\n"
                        "आप कैसे हैं? एयरटेल बिजनेस उद्यम डिजिटल में आपका स्वागत है।\\n"
                        "आपके व्यवसाय के लिए सबसे सही प्लान चुनने के लिए कृपया बताएं:\\n"
                        "* आपका व्यवसाय किस प्रकार का है (उदा. किराना दुकान, क्लिनिक, सीए ऑफिस, फैक्ट्री)?\\n"
                        "* किस शहर में हैं और कितने कर्मचारी हैं?\\n"
                        "* क्या आपके पास जीएसटी नंबर है या केवल उद्यम प्रमाण पत्र?",
                        "Namaste! Main bahut accha hoon dhanyavad. Aap kaise hain? Airtel Business Udyam Digital mein aapka swagat hai. Kripya batayein aapka business kis type ka hai."
                    ),
                    "latin": (
                        "### Namaste! Main bilkul theek hoon, dhanyawaad 🙏\\n\\n"
                        "Aap kaise hain? Welcome to Airtel Business Udyam Digital.\\n"
                        "Aapke business ke liye best digital plan chunne ke liye batayein:\\n"
                        "* Aapka business kis tarah ka hai (e.g. Kirana store, Clinic, CA office, Factory)?\\n"
                        "* Kis city mein hain aur kitne log kaam karte hain?\\n"
                        "* Kya aapke paas GSTIN hai ya sirf Udyam certificate?",
                        "Namaste! Main bilkul theek hoon dhanyawaad. Aap kaise hain? Welcome to Airtel Business Udyam Digital. Aapke business ke liye kis tarah ki connectivity chahiye?"
                    ),
                },
                "kn": {
                    "native": (
                        "### ನಮಸ್ಕಾರ! ನಾನು ಆರಾಮಾಗಿದ್ದೇನೆ, ಧನ್ಯವಾದಗಳು 🙏\\n\\n"
                        "ನೀವು ಹೇಗಿದ್ದೀರಿ? ಏರ್‌ಟೆಲ್ ಬಿಸಿನೆಸ್ ಉದ್ಯಮ್ ಡಿಜಿಟಲ್‌ಗೆ ಸುಸ್ವಾಗತ.\\n"
                        "ನಿಮ್ಮ ವ್ಯಾಪಾರಕ್ಕೆ ಸೂಕ್ತವಾದ ಅತ್ಯುತ್ತಮ ಪ್ಲಾನ್‌ಗಾಗಿ ವಿವರಗಳನ್ನು ನೀಡಿ:\\n"
                        "* ನಿಮ್ಮ ವ್ಯಾಪಾರ ಯಾವ ರೀತಿಯದ್ದು (ಉದಾ. ಕಿರಾಣಿ ಅಂಗಡಿ, ಕ್ಲಿನಿಕ್, ಸಿಎ ಕಚೇರಿ, ಕಾರ್ಖಾನೆ)?\\n"
                        "* ಯಾವ ಊರು ಮತ್ತು ಎಷ್ಟು ಮಂದಿ ಸಿಬ್ಬಂದಿ ಇದ್ದಾರೆ?\\n"
                        "* ನಿಮ್ಮ ಬಳಿ ಜಿಎಸ್‌ಟಿ ಇದೆಯೇ ಅಥವಾ ಉದ್ಯಮ್ ಪ್ರಮಾಣಪತ್ರ ಮಾತ್ರವೇ?",
                        "Namaskara! Naanu aramavagiddini dhanyavadagalu. Neevu hegiddiri? Airtel Business Udyam Digital-ge suswagatha."
                    ),
                    "latin": (
                        "### Namaskara! Naanu chennagi iddini, dhanyavada 🙏\\n\\n"
                        "Neevu hegiddira? Welcome to Airtel Business Udyam Digital.\\n"
                        "Nimma business-ge sarihondona best plan select maadoke ee details heli:\\n"
                        "* Nimma business yavudhu (e.g. Kirana angadi, Clinic, CA office, Factory)?\\n"
                        "* Yaava ooru mathu eshtu jana staff iddare?\\n"
                        "* Nimmalli GST number idhya athva Udyam certificate matrava?",
                        "Namaskara! Naanu chennagi iddini dhanyavada. Neevu hegiddira? Welcome to Airtel Business Udyam Digital."
                    ),
                },
                "ml": {
                    "native": (
                        "### നമസ്കാരം! എനിക്ക് സുഖമാണ്, നന്ദി 🙏\\n\\n"
                        "സുഖമാണോ? എയർടെൽ ബിസിനസ്സ് ഉദ്യം ഡിജിറ്റലിലേക്ക് സ്വാഗതം.\\n"
                        "നിങ്ങളുടെ ബിസിനസ്സിന് ഏറ്റവും അനുയോജ്യമായ പ്ലാൻ കണ്ടെത്താൻ വിവരങ്ങൾ നൽകുക:\\n"
                        "* ഏത് തരത്തിലുള്ള ബിസിനസ്സാണ് (ഉദാ. പലചരക്ക് കട, ക്ലിനിക്ക്, സിഎ ഓഫീസ്, ഫാക്ടറി)?\\n"
                        "* ഏത് നഗരത്തിലാണ്, എത്ര ജീവനക്കാരുണ്ട്?\\n"
                        "* ജിഎസ്ടി ഉണ്ടോ അതോ ഉദ്യം സർട്ടിഫിക്കറ്റ് മാത്രമാണോ?",
                        "Namaskaram! Enikku sukhamanu nandi. Sukhamano? Airtel Business Udyam Digital-lekku swagatham."
                    ),
                    "latin": (
                        "### Namaskaram! Enikku sukhamanu, nandi 🙏\\n\\n"
                        "Sukhamano? Welcome to Airtel Business Udyam Digital.\\n"
                        "Ningalude business-nu yojicha plan thiranjedukkan ee details parayoo:\\n"
                        "* Enthekilum shop aano (e.g. Maligai kada, Clinic, CA office, Factory)?\\n"
                        "* Ethekilum city and ethra staff undu?\\n"
                        "* Ningalkku GST registration undo atho Udyam certificate mathramo?",
                        "Namaskaram! Enikku sukhamanu nandi. Sukhamano? Welcome to Airtel Business Udyam Digital."
                    ),
                },
                "bn": {
                    "native": (
                        "### নমস্কার! আমি ভালো আছি, ধন্যবাদ 🙏\\n\\n"
                        "আপনি কেমন আছেন? এয়ারটেল বিজনেস উদ্যম ডিজিটালে আপনাকে স্বাগতম।\\n"
                        "আপনার ব্যবসার জন্য সেরা ডিজিটাল প্ল্যান বেছে নিতে কিছু তথ্য জানান:\\n"
                        "* আপনার ব্যবসা কী ধরনের (যেমন মুদি দোকান, ক্লিনিক, সিএ অফিস, কারখানা)?\\n"
                        "* কোন শহরে এবং কতজন কর্মী আছেন?\\n"
                        "* আপনার কি জিএসটি (GSTIN) আছে নাকি শুধুমাত্র উদ্যোগ সার্টিফিকেট?",
                        "Nomoshkar! Ami bhalo achi dhonnobad. Apni kemon achen? Airtel Business Udyam Digital-e apnake swagoto."
                    ),
                    "latin": (
                        "### Nomoshkar! Ami bhalo achi, dhonnobad 🙏\\n\\n"
                        "Apni kemon achen? Welcome to Airtel Business Udyam Digital.\\n"
                        "Apnar business-er jonyo best connectivity plan select korte janan:\\n"
                        "* Apnar business ki dhoroner (e.g. Kirana store, Clinic, CA office, Factory)?\\n"
                        "* Kon city-te and koto jon staff ache?\\n"
                        "* Apnar kache GSTIN ache naki shudhumatro Udyam certificate?",
                        "Nomoshkar! Ami bhalo achi dhonnobad. Apni kemon achen? Welcome to Airtel Business Udyam Digital."
                    ),
                },
                "gu": {
                    "native": (
                        "### નમસ્તે! હું મજામાં છું, આભાર 🙏\\n\\n"
                        "તમે કેમ છો? એરટેલ બિઝનેસ ઉદ્યમ ડિજિટલમાં તમારું સ્વાગત છે.\\n"
                        "તમારા વ્યવસાય માટે શ્રેષ્ઠ પ્લાન પસંદ કરવા વિગતો આપો:\\n"
                        "* તમારો વ્યવસાય કેવા પ્રકારનો છે (દા.ત. કરિયાણાની દુકાન, ક્લિનિક, સીએ ઓફિસ, ફેક્ટરી)?\\n"
                        "* કયા શહેરમાં અને કેટલા કર્મચારીઓ છે?\\n"
                        "* તમારી પાસે જીએસટી છે કે ફક્ત ઉદ્યમ પ્રમાણપત્ર?",
                        "Namaste! Hu majama chhu aabhar. Tame kem cho? Airtel Business Udyam Digital-ma tamaru swagat chhe."
                    ),
                    "latin": (
                        "### Namaste! Hu majama chhu, aabhar 🙏\\n\\n"
                        "Tame kem cho? Welcome to Airtel Business Udyam Digital.\\n"
                        "Tamara business mate best plan pasand karva aatli vigat aapo:\\n"
                        "* Tamaro business kyo chhe (e.g. Kirana dukan, Clinic, CA office, Factory)?\\n"
                        "* Kya city ma chho ane ketla staff chhe?\\n"
                        "* Tamari pase GST number chhe ke fakt Udyam certificate?",
                        "Namaste! Hu majama chhu aabhar. Tame kem cho? Welcome to Airtel Business Udyam Digital."
                    ),
                },
                "mr": {
                    "native": (
                        "### नमस्कार! मी मजेत आहे, धन्यवाद 🙏\\n\\n"
                        "तुम्ही कसे आहात? एअरटेल बिझनेस उद्यम डिजिटलमध्ये आपले स्वागत आहे.\\n"
                        "आपल्या व्यवसायासाठी सर्वोत्तम प्लॅन निवडण्यासाठी माहिती द्या:\\n"
                        "* आपला व्यवसाय कोणत्या प्रकारचा आहे (उदा. किराणा दुकान, क्लिनिक, सीए ऑफिस, कारखाना)?\\n"
                        "* कोणत्या शहरात आणि किती कर्मचारी आहेत?\\n"
                        "* आपल्याकडे जीएसटी नंबर आहे की फक्त उद्यम प्रमाणपत्र?",
                        "Namaskar! Me majet aahe dhanyawad. Tumhi kase ahat? Airtel Business Udyam Digital-madhye aaple swagat aahe."
                    ),
                    "latin": (
                        "### Namaskar! Me majet aahe, dhanyawad 🙏\\n\\n"
                        "Tumhi kase ahat? Welcome to Airtel Business Udyam Digital.\\n"
                        "Aaplya business sathi best digital plan shodhnyasathi he sanga:\\n"
                        "* Aapla business kontya type cha aahe (e.g. Kirana dukan, Clinic, CA office, Factory)?\\n"
                        "* Konte shahar aani kiti staff kaam kartat?\\n"
                        "* Aaplyakade GSTIN aahe ka fakt Udyam certificate?",
                        "Namaskar! Me majet aahe dhanyawad. Tumhi kase ahat? Welcome to Airtel Business Udyam Digital."
                    ),
                },
                "or": {
                    "native": (
                        "### ନମସ୍କାର! ମୁଁ ଭଲରେ ଅଛି, ଧନ୍ୟବାଦ 🙏\\n\\n"
                        "ଆପଣ କେମିତି ଅଛନ୍ତି? ଏୟାରଟେଲ ବିଜନେସ ଉଦ୍ୟମ ଡିଜିଟାଲକୁ ଆପଣଙ୍କୁ ସ୍ୱାଗତ।\\n"
                        "ଆପଣଙ୍କ ବ୍ୟବସାୟ ପାଇଁ ସର୍ବୋତ୍ତମ ପ୍ଲାନ ବାଛିବା ପାଇଁ ବିବରଣୀ ପ୍ରଦାନ କରନ୍ତୁ:\\n"
                        "* ଆପଣଙ୍କର କେଉଁ ପ୍ରକାରର ବ୍ୟବସାୟ ଅଛି (ଯଥା ରାସନ ଦୋକାନ, କ୍ଲିନିକ, ସିଏ ଅଫିସ, କାରଖାନା)?\\n"
                        "* କେଉଁ ସହର ଏବଂ କେତେ କର୍ମଚାରୀ ଅଛନ୍ତି?\\n"
                        "* ଆପଣଙ୍କର ଜିଏସଟି ଅଛି ନା କେବଳ ଉଦ୍ୟମ ପ୍ରମାଣପତ୍ର?",
                        "Namaskar! Mu bhalare achi dhanyabad. Apana kemiti achanti? Airtel Business Udyam Digital-ku swagat."
                    ),
                    "latin": (
                        "### Namaskar! Mu bhalare achi, dhanyabad 🙏\\n\\n"
                        "Apana kemiti achanti? Welcome to Airtel Business Udyam Digital.\\n"
                        "Apnanka business pain best connectivity plan banchiba pain kahantu:\\n"
                        "* Apnanka business kouta (e.g. Rashan dokan, Clinic, CA office, Factory)?\\n"
                        "* Kouthi city re achi and kete loka kama karuchanti?\\n"
                        "* Apnankara GSTIN achi na kebala Udyam certificate?",
                        "Namaskar! Mu bhalare achi dhanyabad. Apana kemiti achanti? Welcome to Airtel Business Udyam Digital."
                    ),
                },
            }

            matched_greeting = greetings_map.get(active_lang, {}).get(effective_script)
            welcome_md = gemini_md or (matched_greeting[0] if matched_greeting else (
                "### Namaste! Welcome to Airtel Business Udyam Digital 🙏\\n\\n"
                "I am doing great, thank you! I am your AI Enterprise Telecom Advisor. Tell me a bit about your business:\\n"
                "* What kind of business do you run (e.g. retail shop, clinic, CA office, factory)?\\n"
                "* Which city and approximately how many staff?\\n"
                "* Do you have a registered GSTIN or Udyam certificate?"
            ))
            welcome_tts = gemini_tts or (matched_greeting[1] if matched_greeting else "Namaste! Airtel Business Udyam Digital mein aapka swagat hai. Kripya batayein ki aap kis sheher mein hain aur aapka business kis type ka hai.")
            return AdvisorResponse(
                slots=slots,
                quote=None,
                recommended_skus=[],
                display_markdown=welcome_md,
                spoken_tts_text=welcome_tts,
                next_suggested_prompts=[
                    "I run a Kirana store in Tier 2 with no GST",
                    "We are a CA office in Mumbai with GST",
                    "We have a factory in Surat with 30 staff",
                ],
            )"""

if old_greeting_block in code:
    code = code.replace(old_greeting_block, new_greeting_block, 1)
    print("Replaced greeting block with multi-script Romanized and Native handling.")
else:
    print("Warning: old_greeting_block not found")

with open("backend/app/services/advisor_agent.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Finished updating advisor_agent.py successfully.")
