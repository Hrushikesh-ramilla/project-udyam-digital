import re
import json

def generate_human_response(user_msg: str, active_lang: str, script_mode: str, slots_complete: bool):
    clean = user_msg.lower().strip()
    
    # 1. Foreign Greetings
    if re.search(r"\bhola\b", clean):
        lat = "¡Hola! Welcome to Airtel Business. While my primary languages are Indian regional languages, I am happy to assist you in English! Are you looking to set up high-speed fiber or business internet?"
        nat = "¡Hola! ఎయిర్‌టెల్ బిజినెస్‌కు స్వాగతం. భారతీయ వ్యాపారాల కోసం హై-స్పీడ్ ఫైబర్ మరియు డిజిటల్ సేవలను మేము అందిస్తున్నాము. మీ వ్యాపార వివరాలను తెలపండి."
        return lat, nat
    if re.search(r"\bbonjour\b", clean):
        lat = "Bonjour! Bienvenue to Airtel Business. How can I help power your enterprise with gigabit fiber today?"
        nat = "Bonjour! ఎయిర్‌టెల్ బిజినెస్‌కు స్వాగతం. మీ వ్యాపారానికి గిగాబిట్ ఫైబర్ ఇంటర్నెట్ కావాలా?"
        return lat, nat
    if re.search(r"\bciao\b", clean):
        lat = "Ciao! Welcome to Airtel Business. Looking to get your business connected with high-speed fiber broadband?"
        nat = "Ciao! ఎయిర్‌టెల్ బిజినెస్‌కు స్వాగతం. మీ వ్యాపారానికి హై-స్పీడ్ ఫైబర్ బ్రాడ్‌బ్యాండ్ కావాలా?"
        return lat, nat
    if re.search(r"\baloha\b", clean):
        lat = "Aloha! Welcome to Airtel Business. What kind of business connectivity can we set up for you today?"
        nat = "Aloha! ఎయిర్‌టెల్ బిజినెస్‌కు స్వాగతం. మీ వ్యాపారానికి ఎలాంటి కనెక్టివిటీ కావాలి?"
        return lat, nat
    if re.search(r"\b(konnichiwa|privet|merhaba|sawasdee|hallo|salut|wie\s*gehts|que\s*tal)\b", clean):
        lat = "Welcome to Airtel Business Udyam Digital! While our core focus is Indian enterprises, I'd love to help you in English. Are you setting up a new business, shop, or office?"
        nat = "ఎయిర్‌టెల్ బిజినెస్ ఉద్యమ్ డిజిటల్‌కు స్వాగతం! భారతీయ వ్యాపారాల కోసం అత్యుత్తమ కనెక్టివిటీని మేము అందిస్తున్నాము. మీ వ్యాపార వివరాలు తెలపండి."
        return lat, nat

    # 2. Unrelated / Witty responses
    if re.search(r"\b(biryani|butter chicken|recipe|how to cook)\b", clean):
        lat = "That sounds delicious, but my superpower is high-speed fiber, not secret recipes! But if you're running a restaurant, cafe, or cloud kitchen, I can set you up with zero-drop Airtel fiber for seamless online deliveries and POS billing. What kind of business setup do you have?"
        nat = "వంటకం అద్భుతంగా ఉంది, కానీ నా నైపుణ్యం హై-స్పీడ్ ఫైబర్ కనెక్టివిటీలో ఉంది! మీరు రెస్టారెంట్ లేదా క్లౌడ్ కిచెన్ నడుపుతుంటే, నిరంతర ఆన్‌లైన్ ఆర్డర్లు మరియు బిల్లింగ్ కోసం ఎయిర్‌టెల్ బిజినెస్ ఫైబర్ అందిస్తాము."
        return lat, nat
    if re.search(r"\b(weather|monsoon|rain)\b", clean):
        lat = "Whether it's monsoon downpours or peak summer heat, Airtel Business fiber stays rock-solid with 99.9% uptime SLA! What kind of business setup are you looking to connect?"
        nat = "వర్షాలు పడినా లేదా ఎండలు కాసినా, ఎయిర్‌టెల్ బిజినెస్ ఫైబర్ 99.9% అప్‌టైమ్ ఎస్‌ఎల్‌ఏతో నిరంతరం పనిచేస్తుంది! మీ వ్యాపారానికి ఎలాంటి కనెక్షన్ కావాలి?"
        return lat, nat
    if re.search(r"\bpoem\b", clean):
        lat = "High-speed connections that never fray / Powering your enterprise day by day! Now, tell me about your business so we can get your digital setup rolling."
        nat = "ఎప్పటికీ ఆగని హై-స్పీడ్ కనెక్టివిటీతో మీ వ్యాపారాన్ని ముందుకు నడిపించండి! మీ వ్యాపార వివరాలు తెలపండి."
        return lat, nat
    if re.search(r"\b(moon|distance)\b", clean):
        lat = "The Moon is about 384,400 km away—still faster than data traveling on a slow connection! With Airtel gigabit fiber, your business gets ultra-low latency. What kind of office or shop are you looking to connect?"
        nat = "చంద్రుడు 3,84,400 కి.మీ దూరంలో ఉన్నాడు! ఎయిర్‌టెల్ గిగాబిట్ ఫైబర్‌తో మీ వ్యాపారానికి అల్ట్రా-లో లేటెన్సీ లభిస్తుంది. మీ ఆఫీస్ లేదా దుకాణం వివరాలు తెలపండి."
        return lat, nat
    if re.search(r"\b(python|binary search|code|programming)\b", clean):
        lat = "While I love clean algorithms and fast code, my day job is connecting tech offices, studios, and businesses with dedicated static IPs and gigabit fiber! Are you setting up connectivity for a tech team?"
        nat = "సాఫ్ట్‌వేర్ కోడింగ్ బాగుంది, కానీ టెక్ ఆఫీసులు మరియు డెవలపర్‌ల కోసం డెడికేటెడ్ స్టాటిక్ ఐపీ, హై-స్పీడ్ ఫైబర్ అందించడమే నా ముఖ్య పని! మీ టెక్ టీమ్ వివరాలు తెలపండి."
        return lat, nat
    if re.search(r"\b(movie|sci-fi)\b", clean):
        lat = "For top-tier sci-fi: Inception, Interstellar, and The Matrix! To stream them in 4K or power a creative studio, Airtel gigabit fiber is your best bet. What business setup are you looking to power up?"
        nat = "సినిమాలు చూడటానికి లేదా డిజిటల్ స్టూడియో నడపడానికి ఎయిర్‌టెల్ గిగాబిట్ ఫైబర్ అత్యుత్తమమైనది. మీ వ్యాపారానికి ఎలాంటి ప్లాన్ కావాలి?"
        return lat, nat
    if re.search(r"\bjoke\b", clean):
        lat = "Why did the router get an award? Because it had outstanding connections! Speaking of great connections, how can Airtel Business fiber power your enterprise today?"
        nat = "రౌటర్‌కు ఎందుకు అవార్డు వచ్చిందో తెలుసా? ఎందుకంటే దాని కనెక్షన్లు అద్భుతం! మీ వ్యాపారానికి ఎయిర్‌టెల్ ఫైబర్ కనెక్షన్ ఎలా అందించగలను?"
        return lat, nat
    if re.search(r"\b(capital of australia|capital city)\b", clean):
        lat = "It's Canberra! Speaking of capital ideas, what kind of business or office are you looking to power with Airtel enterprise connectivity?"
        nat = "ఆస్ట్రేలియా రాజధాని కాన్‌బెర్రా! మీ వ్యాపార కార్యాలయానికి ఎయిర్‌టెల్ ఎంటర్‌ప్రైజ్ కనెక్టివిటీ అందించడానికి వివరాలు తెలపండి."
        return lat, nat

    # 3. Ambiguous / Terse
    if clean in ["internet", "broadband"]:
        lat = "Looking for lightning-fast business internet? We provide high-speed fiber with 99.9% uptime and zero setup fees under Udyam. What kind of business do you run and in which city?"
        nat = "హై-స్పీడ్ బిజినెస్ ఇంటర్నెట్ కావాలా? ఉద్యమ్ కింద సున్నా సెటప్ ఫీజుతో 99.9% అప్‌టైమ్ ఫైబర్ అందిస్తున్నాము. మీది ఏ వ్యాపారం మరియు ఏ ఊరు?"
        return lat, nat
    if clean in ["plans"]:
        lat = "We have curated business packs from ₹999/month for retail shops to multi-gigabit fiber for enterprises! Which city is your business in, and what do you do?"
        nat = "రిటైల్ షాపుల కోసం నెలకు ₹999 నుండి ఎంటర్‌ప్రైజ్ ప్లాన్‌ల వరకు అందుబాటులో ఉన్నాయి! మీ వ్యాపారం ఏ నగరంలో ఉంది?"
        return lat, nat
    if clean in ["price", "how much"]:
        lat = "Our MSME plans start at ₹999/month for retail with zero setup fee under Udyam, up to dedicated corporate lines. Which city is your business located in?"
        nat = "మా ఎంఎస్ఎంఈ ప్లాన్లు నెలకు ₹999 నుండి ప్రారంభమవుతాయి. మీ వ్యాపారం ఏ నగరంలో ఉంది?"
        return lat, nat
    if clean in ["speed"]:
        lat = "Speeds range from 100 Mbps symmetrical fiber up to 1 Gbps dedicated leased lines! What type of enterprise do you run?"
        nat = "100 Mbps నుండి 1 Gbps వరకు డెడికేటెడ్ స్పీడ్స్ అందుబాటులో ఉన్నాయి! మీది ఏ తరహా వ్యాపారం?"
        return lat, nat
    if clean in ["enterprise"]:
        lat = "Airtel Enterprise delivers dedicated leased lines, static IPs, cloud backup, and SD-WAN across India. What is your company's profile and city?"
        nat = "ఎయిర్‌టెల్ ఎంటర్‌ప్రైజ్ లీజ్డ్ లైన్లు, స్టాటిక్ ఐపీ, క్లౌడ్ బ్యాకప్ మరియు ఎస్డీ-వాన్ అందిస్తుంది. మీ కంపెనీ వివరాలు తెలపండి."
        return lat, nat
    if clean in ["quote"]:
        lat = "I'd love to generate an instant, audited CPQ quote for you! Just tell me your business type (e.g. clinic, shop, factory, office), city, and team size."
        nat = "మీ వ్యాపారం కోసం తక్షణ సిపిక్యు కొటేషన్ అందించడానికి సిద్ధంగా ఉన్నాను! మీ వ్యాపార రకం, నగరం మరియు సిబ్బంది సంఖ్య తెలపండి."
        return lat, nat
    if clean in ["connection"]:
        lat = "Let's get your enterprise connected! Do you need fiber broadband for a single shop, an office, or multiple branches across cities?"
        nat = "మీ వ్యాపారానికి కనెక్టివిటీ అందిద్దాం! ఒంటి షాప్ కోసమా, ఆఫీస్ కోసమా లేదా పలు బ్రాంచీల కోసమా?"
        return lat, nat
    if clean in ["airtel"]:
        lat = "Airtel Business Udyam Digital at your service! How can I assist you with broadband, static IPs, or enterprise solutions today?"
        nat = "ఎయిర్‌టెల్ బిజినెస్ ఉద్యమ్ డిజిటల్ సేవలో ఉంది! బ్రాడ్‌బ్యాండ్, స్టాటిక్ ఐపీ లేదా క్లౌడ్ సేవల గురించి ఎలా సహాయపడగలను?"
        return lat, nat

    # Default friendly conversational prompt
    lat = "I'd love to help configure the perfect plan for you! Could you please share what kind of business you run (e.g. clinic, retail shop, CA office, factory) and which city you are located in?"
    nat = "మీ వ్యాపారానికి సరిపోయే ఉత్తమమైన ప్లాన్ అందించడానికి దయచేసి తెలపండి: మీది ఏ తరహా వ్యాపారం (ఉదా. క్లినిక్, షాప్, ఆఫీస్, ఫ్యాక్టరీ) మరియు ఏ నగరంలో ఉంది?"
    return lat, nat

print("Standalone human test generator loaded successfully.")
