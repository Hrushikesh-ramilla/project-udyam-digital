method_code = '''
    def _generate_human_fallback(
        self,
        user_message: str,
        clean_msg: str,
        active_lang: str,
        effective_script: str,
        slots: MSMEProfileSlots,
        is_foreign: bool = False,
        is_unrelated: bool = False,
        is_terse: bool = False,
        is_greeting: bool = False,
    ) -> tuple[str, str, str]:
        """Generates a warm, witty, context-attuned human response across all edge categories."""
        # 1. Foreign Greetings
        if is_foreign:
            if re.search(r"\\bhola\\b", clean_msg):
                lat = "¡Hola! Welcome to Airtel Business. While my superpowers are in Indian regional languages, I am delighted to assist you in English! Are you looking to set up high-speed fiber or digital services for your business?"
                nat = "¡Hola! ఎయిర్‌టెల్ బిజినెస్‌కు స్వాగతం. భారతీయ వ్యాపారాల కోసం హై-స్పీడ్ ఫైబర్ మరియు డిజిటల్ సేవలను మేము అందిస్తున్నాము. మీ వ్యాపార వివరాలను తెలపండి."
                tts = "Hola! Welcome to Airtel Business. How can I help power your enterprise today?"
                return lat, nat, tts
            if re.search(r"\\bbonjour\\b", clean_msg):
                lat = "Bonjour! Bienvenue to Airtel Business. How can I help power your enterprise with gigabit fiber today?"
                nat = "Bonjour! ఎయిర్‌టెల్ బిజినెస్‌కు స్వాగతం. మీ వ్యాపారానికి గిగాబిట్ ఫైబర్ ఇంటర్నెట్ కావాలా?"
                tts = "Bonjour! Welcome to Airtel Business. How can I help power your enterprise today?"
                return lat, nat, tts
            if re.search(r"\\bciao\\b", clean_msg):
                lat = "Ciao! Welcome to Airtel Business. Looking to get your business connected with high-speed fiber broadband?"
                nat = "Ciao! ఎయిర్‌టెల్ బిజినెస్‌కు స్వాగతం. మీ వ్యాపారానికి హై-స్పీడ్ ఫైబర్ బ్రాడ్‌బ్యాండ్ కావాలా?"
                tts = "Ciao! Welcome to Airtel Business. Looking to get your business connected?"
                return lat, nat, tts
            if re.search(r"\\baloha\\b", clean_msg):
                lat = "Aloha! Welcome to Airtel Business. What kind of business connectivity can we set up for you today?"
                nat = "Aloha! ఎయిర్‌టెల్ బిజినెస్‌కు స్వాగతం. మీ వ్యాపారానికి ఎలాంటి కనెక్టివిటీ కావాలి?"
                tts = "Aloha! Welcome to Airtel Business. What kind of business connectivity can we set up for you today?"
                return lat, nat, tts
            # General foreign
            lat = "Welcome to Airtel Business Udyam Digital! While our core focus is Indian enterprises, I'd love to help you in English. Are you setting up a new business, shop, or office?"
            nat = "ఎయిర్‌టెల్ బిజినెస్ ఉద్యమ్ డిజిటల్‌కు స్వాగతం! భారతీయ వ్యాపారాల కోసం అత్యుత్తమ కనెక్టివిటీని మేము అందిస్తున్నాము. మీ వ్యాపార వివరాలు తెలపండి."
            tts = "Welcome to Airtel Business Udyam Digital. How can I help your enterprise today?"
            return lat, nat, tts

        # 2. Unrelated / Playful Queries
        if is_unrelated:
            if re.search(r"\\b(biryani|butter\\s*chicken|recipe|cook|food)\\b", clean_msg):
                lat = "That sounds delicious, but my superpower is high-speed enterprise fiber, not secret recipes! If you run a restaurant, cafe, or cloud kitchen, I can set you up with zero-drop Airtel fiber for seamless online deliveries and POS billing. What kind of business setup do you have?"
                nat = "రుచికరమైన వంటకం! కానీ నా నైపుణ్యం హై-స్పీడ్ ఫైబర్ కనెక్టివిటీలో ఉంది. మీరు రెస్టారెంట్ లేదా క్లౌడ్ కిచెన్ నడుపుతుంటే, ఆన్‌లైన్ ఆర్డర్ల కోసం ఎయిర్‌టెల్ బిజినెస్ ఫైబర్ అందిస్తాము. మీ వ్యాపార వివరాలు తెలపండి."
                tts = "Sounds delicious! If you run a food business or restaurant, Airtel fiber can power your online orders seamlessly."
                return lat, nat, tts
            if re.search(r"\\b(weather|monsoon|rain)\\b", clean_msg):
                lat = "Whether it's monsoon downpours or peak summer heat, Airtel Business fiber stays rock-solid with 99.9% uptime SLA! What kind of business setup are you looking to connect?"
                nat = "వర్షాలు పడినా లేదా ఎండలు కాసినా, ఎయిర్‌టెల్ బిజినెస్ ఫైబర్ 99.9% అప్‌టైమ్ ఎస్‌ఎల్‌ఏతో నిరంతరం పనిచేస్తుంది! మీ వ్యాపారానికి ఎలాంటి కనెక్షన్ కావాలి?"
                tts = "Rain or shine, Airtel Business fiber stays rock solid with 99.9% uptime SLA. What business setup are you connecting?"
                return lat, nat, tts
            if re.search(r"\\bpoem\\b", clean_msg):
                lat = "High-speed connections that never fray / Powering your enterprise day by day! Now, tell me about your business so we can get your digital setup rolling."
                nat = "ఎప్పటికీ ఆగని హై-స్పీడ్ కనెక్టివిటీతో మీ వ్యాపారాన్ని ముందుకు నడిపించండి! మీ వ్యాపార వివరాలు తెలపండి."
                tts = "High-speed connections that never fray, powering your enterprise day by day! Tell me about your business requirements."
                return lat, nat, tts
            if re.search(r"\\b(moon|distance)\\b", clean_msg):
                lat = "The Moon is about 384,400 km away—still faster than data traveling on a slow connection! With Airtel gigabit fiber, your business gets ultra-low latency. What kind of office or shop are you looking to connect?"
                nat = "చంద్రుడు 3,84,400 కి.మీ దూరంలో ఉన్నాడు! ఎయిర్‌టెల్ గిగాబిట్ ఫైబర్‌తో మీ వ్యాపారానికి అల్ట్రా-లో లేటెన్సీ లభిస్తుంది. మీ ఆఫీస్ లేదా దుకాణం వివరాలు తెలపండి."
                tts = "The Moon is 384,400 km away! With Airtel gigabit fiber, your business gets lightning-fast low latency."
                return lat, nat, tts
            if re.search(r"\\b(python|binary\\s*search|code|programming)\\b", clean_msg):
                lat = "While I love clean algorithms and fast code, my day job is connecting tech offices, studios, and businesses with dedicated static IPs and gigabit fiber! Are you setting up connectivity for a tech team?"
                nat = "సాఫ్ట్‌వేర్ కోడింగ్ బాగుంది, కానీ టెక్ ఆఫీసులు మరియు డెవలపర్‌ల కోసం డెడికేటెడ్ స్టాటిక్ ఐపీ, హై-స్పీడ్ ఫైబర్ అందించడమే నా ముఖ్య పని! మీ టెక్ టీమ్ వివరాలు తెలపండి."
                tts = "While I love clean algorithms, my specialty is connecting tech offices with dedicated static IPs and gigabit fiber!"
                return lat, nat, tts
            if re.search(r"\\b(movie|sci-fi)\\b", clean_msg):
                lat = "For top-tier sci-fi: Inception, Interstellar, and The Matrix! To stream them in 4K or power a creative studio, Airtel gigabit fiber is your best bet. What business setup are you looking to power up?"
                nat = "సినిమాలు చూడటానికి లేదా డిజిటల్ స్టూడియో నడపడానికి ఎయిర్‌టెల్ గిగాబిట్ ఫైబర్ అత్యుత్తమమైనది. మీ వ్యాపారానికి ఎలాంటి ప్లాన్ కావాలి?"
                tts = "Top sci-fi recommendations: Inception, Interstellar, and The Matrix! What business setup are you looking to power up?"
                return lat, nat, tts
            if re.search(r"\\bjoke\\b", clean_msg):
                lat = "Why did the router get an award? Because it had outstanding connections! Speaking of great connections, how can Airtel Business fiber power your enterprise today?"
                nat = "రౌటర్‌కు ఎందుకు అవార్డు వచ్చిందో తెలుసా? ఎందుకంటే దాని కనెక్షన్లు అద్భుతం! మీ వ్యాపారానికి ఎయిర్‌టెల్ ఫైబర్ కనెక్షన్ ఎలా అందించగలను?"
                tts = "Why did the router get an award? Because it had outstanding connections! How can Airtel Business fiber power your enterprise today?"
                return lat, nat, tts
            if re.search(r"\\b(capital\\s*of|capital\\s*city)\\b", clean_msg):
                lat = "It's Canberra! Speaking of capital ideas, what kind of business or office are you looking to power with Airtel enterprise connectivity?"
                nat = "ఆస్ట్రేలియా రాజధాని కాన్‌బెర్రా! మీ వ్యాపార కార్యాలయానికి ఎయిర్‌టెల్ ఎంటర్‌ప్రైజ్ కనెక్టివిటీ అందించడానికి వివరాలు తెలపండి."
                tts = "It's Canberra! What kind of business or office are you looking to power with Airtel enterprise connectivity?"
                return lat, nat, tts

        # 3. Terse / Ambiguous Queries
        if is_terse:
            if clean_msg in {"internet", "broadband"}:
                lat = "Looking for lightning-fast business internet? We provide high-speed fiber with 99.9% uptime and zero setup fees under Udyam. What kind of business do you run and in which city?"
                nat = "హై-స్పీడ్ బిజినెస్ ఇంటర్నెట్ కావాలా? ఉద్యమ్ కింద సున్నా సెటప్ ఫీజుతో 99.9% అప్‌టైమ్ ఫైబర్ అందిస్తున్నాము. మీది ఏ వ్యాపారం మరియు ఏ ఊరు?"
                tts = "Looking for lightning-fast business internet? What kind of business do you run and in which city?"
                return lat, nat, tts
            if clean_msg in {"plans"}:
                lat = "We have curated business packs starting from ₹999/month for retail shops up to gigabit fiber for offices! Which city is your business in, and what do you do?"
                nat = "రిటైల్ షాపుల కోసం నెలకు ₹999 నుండి ఎంటర్‌ప్రైజ్ ప్లాన్‌ల వరకు అందుబాటులో ఉన్నాయి! మీ వ్యాపారం ఏ నగరంలో ఉంది?"
                tts = "We have curated business packs from 999 rupees a month. Which city is your business in?"
                return lat, nat, tts
            if clean_msg in {"price", "how much"}:
                lat = "Our MSME plans start at ₹999/month for retail with zero setup fee under Udyam, up to dedicated corporate lines. Which city is your business located in?"
                nat = "మా ఎంఎస్ఎంఈ ప్లాన్లు నెలకు ₹999 నుండి ప్రారంభమవుతాయి. మీ వ్యాపారం ఏ నగరంలో ఉంది?"
                tts = "Our plans start at 999 rupees a month with zero setup fee. Which city is your business located in?"
                return lat, nat, tts
            if clean_msg in {"speed"}:
                lat = "Speeds range from 100 Mbps symmetrical fiber up to 1 Gbps dedicated leased lines! What type of enterprise do you run?"
                nat = "100 Mbps నుండి 1 Gbps వరకు డెడికేటెడ్ స్పీడ్స్ అందుబాటులో ఉన్నాయి! మీది ఏ తరహా వ్యాపారం?"
                tts = "Speeds range from 100 Mbps up to 1 Gbps dedicated leased lines! What type of enterprise do you run?"
                return lat, nat, tts
            if clean_msg in {"enterprise"}:
                lat = "Airtel Enterprise delivers dedicated leased lines, static IPs, cloud backup, and SD-WAN across India. What is your company's profile and city?"
                nat = "ఎయిర్‌టెల్ ఎంటర్‌ప్రైజ్ లీజ్డ్ లైన్లు, స్టాటిక్ ఐపీ, క్లౌడ్ బ్యాకప్ మరియు ఎస్డీ-వాన్ అందిస్తుంది. మీ కంపెనీ వివరాలు తెలపండి."
                tts = "Airtel Enterprise delivers dedicated leased lines and SD-WAN across India. What is your company's profile and city?"
                return lat, nat, tts
            if clean_msg in {"quote"}:
                lat = "I'd love to generate an instant, audited CPQ quote for you! Just tell me your business type (e.g. clinic, shop, factory, office), city, and team size."
                nat = "మీ వ్యాపారం కోసం తక్షణ సిపిక్యు కొటేషన్ అందించడానికి సిద్ధంగా ఉన్నాను! మీ వ్యాపార రకం, నగరం మరియు సిబ్బంది సంఖ్య తెలపండి."
                tts = "I'd love to generate an instant quote for you! Just tell me your business type, city, and team size."
                return lat, nat, tts
            if clean_msg in {"connection"}:
                lat = "Let's get your enterprise connected! Do you need fiber broadband for a single shop, an office, or multiple branches across cities?"
                nat = "మీ వ్యాపారానికి కనెక్టివిటీ అందిద్దాం! ఒంటి షాప్ కోసమా, ఆఫీస్ కోసమా లేదా పలు బ్రాంచీల కోసమా?"
                tts = "Let's get your enterprise connected! Do you need fiber broadband for a single shop or an office?"
                return lat, nat, tts
            if clean_msg in {"airtel"}:
                lat = "Airtel Business Udyam Digital at your service! How can I assist you with broadband, static IPs, or enterprise solutions today?"
                nat = "ఎయిర్‌టెల్ బిజినెస్ ఉద్యమ్ డిజిటల్ సేవలో ఉంది! బ్రాడ్‌బ్యాండ్, స్టాటిక్ ఐపీ లేదా క్లౌడ్ సేవల గురించి ఎలా సహాయపడగలను?"
                tts = "Airtel Business Udyam Digital at your service! How can I assist you today?"
                return lat, nat, tts

        # 4. Regional Greetings
        if is_greeting:
            if active_lang == "te":
                lat = "Namaskaram! Nenu bagunnanu, dhanyavadalu 🙏 Meeru ela unnaru? Welcome to Airtel Business. Mee business ki kotha fiber connection kosam chusthunnara? Ee oori lo undi mee business?"
                nat = "నమస్కారం! నేను బాగున్నాను, ధన్యవాదాలు 🙏 మీరు ఎలా ఉన్నారు? ఎయిర్‌టెల్ బిజినెస్‌కు స్వాగతం. మీ వ్యాపారానికి ఫైబర్ కనెక్షన్ కోసం చూస్తున్నారా? మీ వ్యాపారం ఏ ఊరిలో ఉంది?"
                tts = "Namaskaram! Nenu bagunnanu, dhanyavadalu. Meeru ela unnaru? Welcome to Airtel Business."
                return lat, nat, tts
            if active_lang == "hi":
                lat = "Namaste! Main bilkul theek hoon, dhanyawaad 🙏 Aap kaise hain? Welcome to Airtel Business Udyam Digital. Apne business ya dukan ke liye internet connection dekh rahe hain? Kis city mein hai aapka setup?"
                nat = "नमस्ते! मैं बिल्कुल ठीक हूँ, धन्यवाद 🙏 आप कैसे हैं? एयरटेल बिजनेस उद्यम डिजिटल में आपका स्वागत है। अपने व्यवसाय के लिए इंटरनेट कनेक्शन देख रहे हैं? किस शहर में है आपका सेटअप?"
                tts = "Namaste! Main bilkul theek hoon, dhanyawaad. Aap kaise hain? Welcome to Airtel Business."
                return lat, nat, tts
            if active_lang == "ta":
                lat = "Vanakkam! Naan nallaa irukken, nandri 🙏 Neenga eppadi irukkeenga? Welcome to Airtel Business. Ungal business-ku fiber internet pathi therinjukka virumbureengala? Endha ooru ungalukku?"
                nat = "வணக்கம்! நான் நலமாக இருக்கிறேன், நன்றி 🙏 நீங்கள் எப்படி இருக்கிறீர்கள்? ஏர்டెல் பிசினஸுக்கு வரவேற்கிறோம். உங்கள் வணிகத்திற்கு ஃபைபர் இணையம் வேண்டுமா? எந்த ஊர் உங்களுடையது?"
                tts = "Vanakkam! Naan nallaa irukken, nandri. Neenga eppadi irukkeenga? Welcome to Airtel Business."
                return lat, nat, tts
            if active_lang == "bn":
                lat = "Nomoshkar! Ami bhalo achi, dhonnobad 🙏 Apni kemon achen? Welcome to Airtel Business. Apnar dokan ba office-er jonyo internet connection lagbe? Kon shohore apnar business?"
                nat = "নমস্কার! আমি ভালো আছি, ধন্যবাদ 🙏 আপনি কেমন আছেন? এয়ারটেল বিজনেসে স্বাগতম। আপনার ব্যবসার জন্য ইন্টারনেট কানেকশন খুঁজছেন? কোন শহরে আপনার ব্যবসা?"
                tts = "Nomoshkar! Ami bhalo achi, dhonnobad. Apni kemon achen? Welcome to Airtel Business."
                return lat, nat, tts
            if active_lang == "gu":
                lat = "Namaste! Hu majama chhu, aabhar 🙏 Tame kem cho? Welcome to Airtel Business. Tamara business mate fiber internet joyie chhe? Kya sheher ma chhe tamaro business?"
                nat = "નમસ્તે! હું મજામાં છું, આભાર 🙏 તમે કેમ છો? એરટેલ બિઝનેસમાં સ્વાગત છે. તમારા વ્યવસાય માટે ફાઇબર ઇન્ટરનેટ જોઈએ છે? કયા શહેરમાં છે તમારો વ્યવસાય?"
                tts = "Namaste! Hu majama chhu, aabhar. Tame kem cho? Welcome to Airtel Business."
                return lat, nat, tts
            if active_lang == "kn":
                lat = "Namaskara! Naanu chennagi iddini, dhanyavada 🙏 Neevu hegiddira? Welcome to Airtel Business. Nimma business-ge fiber internet connection beka? Yaava ooru nimmadhu?"
                nat = "ನಮಸ್ಕಾರ! ನಾನು ಆರಾಮಾಗಿದ್ದೇನೆ, ಧನ್ಯವಾದಗಳು 🙏 ನೀವು ಹೇಗಿದ್ದೀರಿ? ಏರ್‌ಟೆಲ್ ಬಿಸಿನೆಸ್‌ಗೆ ಸುಸ್ವಾಗತ. ನಿಮ್ಮ ವ್ಯಾಪಾರಕ್ಕೆ ಫೈಬರ್ ಇಂಟರ್ನೆಟ್ ಸಂಪರ್ಕ ಬೇಕೇ? ಯಾವ ಊರು ನಿಮ್ಮದು?"
                tts = "Namaskara! Naanu chennagi iddini, dhanyavada. Neevu hegiddira? Welcome to Airtel Business."
                return lat, nat, tts
            if active_lang == "ml":
                lat = "Namaskaram! Enikku sukhamanu, nandi 🙏 Sukhamano? Welcome to Airtel Business. Ningalude business-nu fiber internet connection aano nokkunnath? Ethekilum city aano?"
                nat = "നമസ്കാരം! എനിക്ക് സുഖമാണ്, നന്ദി 🙏 സുഖമാണോ? എയർടെൽ ബിസിനസ്സിലേക്ക് സ്വാഗതം. നിങ്ങളുടെ ബിസിനസ്സിന് ഫൈബർ ഇന്റർനെറ്റ് കണക്ഷനാണോ നോക്കുന്നത്? ഏത് നగരത്തിലാണ്?"
                tts = "Namaskaram! Enikku sukhamanu, nandi. Sukhamano? Welcome to Airtel Business."
                return lat, nat, tts
            if active_lang == "mr":
                lat = "Namaskar! Me majet aahe, dhanyawad 🙏 Tumhi kase ahat? Welcome to Airtel Business. Aplya business sathi fiber internet connection hawe aahe ka? Konte shahar aahe aaple?"
                nat = "नमस्कार! मी मजेत आहे, धन्यवाद 🙏 तुम्ही कसे आहात? एअरटेल बिझनेसमध्ये आपले स्वागत आहे. आपल्या व्यवसायासाठी फायबर इंटरनेट हवे आहे का? कोणते शहर आहे आपले?"
                tts = "Namaskar! Me majet aahe, dhanyawad. Tumhi kase ahat? Welcome to Airtel Business."
                return lat, nat, tts
            if active_lang == "or":
                lat = "Namaskar! Mu bhalare achi, dhanyabad 🙏 Apana kemiti achanti? Welcome to Airtel Business. Apnanka business pain fiber internet connection darkar ki? Kouthi city re apnanka business?"
                nat = "ନମସ୍କାର! ମୁଁ ଭଲରେ ଅଛି, ଧନ୍ୟବାଦ 🙏 ଆପଣ କେମିତି ଅଛନ୍ତି? ଏୟାରଟେଲ ବିଜନେସକୁ ସ୍ୱାଗତ। ଆପଣଙ୍କ ବ୍ୟବସାୟ ପାଇଁ ଫାଇବର ଇଣ୍ଟରନେଟ ଦରକାର କି? କେଉଁ ସହରରେ ଆପଣଙ୍କ ବ୍ୟବସାୟ?"
                tts = "Namaskar! Mu bhalare achi, dhanyabad. Apana kemiti achanti? Welcome to Airtel Business."
                return lat, nat, tts
            # General greeting
            lat = "Namaste! Welcome to Airtel Business Udyam Digital 🙏 How can I assist your enterprise with broadband, static IPs, or digital connectivity today?"
            nat = "నమస్కారం! ఎయిర్‌టెల్ బిజినెస్ ఉద్యమ్ డిజిటల్‌కు స్వాగతం 🙏 మీ వ్యాపారానికి కనెక్టివిటీ లేదా డిజిటల్ సేవల గురించి ఎలా సహాయపడగలను?"
            tts = "Namaste! Welcome to Airtel Business Udyam Digital. How can I assist your enterprise today?"
            return lat, nat, tts

        # 5. Incomplete Turn: Warm, Conversational Clarification Question
        missing_text = []
        if "business_type" in slots.missing_slots:
            missing_text.append("what kind of business you run (e.g. retail shop, clinic, CA office, factory)")
        if "city_or_tier" in slots.missing_slots:
            missing_text.append("which city or town you are located in")
        if "gstin_status" in slots.missing_slots:
            missing_text.append("whether you have a registered GST number or only Udyam")

        details_str = ", ".join(missing_text) if missing_text else "your business type and city"
        lat = f"Namaste! I'd love to help you configure the ideal business connectivity plan. Could you please clarify {details_str}?"
        nat = "నమస్కారం! మీ వ్యాపారానికి తగిన ఖచ్చితమైన ప్లాన్ అందించడానికి దయచేసి మీ వ్యాపార రకం, నగరం మరియు జీఎస్టీ వివరాలు తెలపండి."
        tts = "Namaste! I'd love to help you configure the ideal business plan. Could you please clarify your business type and city?"
        return lat, nat, tts
'''

with open("backend/app/services/advisor_agent.py", "a", encoding="utf-8") as f:
    f.write(method_code)

print("Appended _generate_human_fallback to advisor_agent.py")
