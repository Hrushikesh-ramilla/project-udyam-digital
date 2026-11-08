with open("backend/app/services/advisor_agent.py", "r", encoding="utf-8") as f:
    text = f.read()

target = """        # 1. Foreign Greetings
        if is_foreign:"""

comparison_block = '''        # 0. Plan Comparison & Alternative Options Query
        if re.search(r"\\b(compare|comparison|multiple|options|alternatives|vs|other plans?|not only one|only one|another plan|different plan|kore option|aur option)\\b", clean_msg):
            budget = slots.monthly_budget_cap or 1500
            tier = slots.city_tier or 2
            lat = (
                "### Flexible Airtel Business Options for Your Enterprise\\n\\n"
                "You definitely have multiple great options—we never force just one setup on you! "
                f"Based on your profile in Tier {tier} (budget ~₹{budget:,}/mo), here is how our top options compare:\\n\\n"
                "1. **Option 1: The Wireless Champion (Biz 5G AirFiber 100 + Secure Wi-Fi)**\\n"
                "   * **Net Monthly:** ₹1,298/month (includes bundle discount)\\n"
                "   * **SLA & Install:** Ready in **3 days** with zero road-digging or wire cuts.\\n"
                "   * **Why it fits:** Plug-and-play 5G antenna gives 100 Mbps with an isolated guest Wi-Fi for customers so your billing counter never slows down.\\n\\n"
                "2. **Option 2: The High-Reliability Wired Pack (Biz Fibre 100 + 4G LTE Auto-Failover)**\\n"
                "   * **Net Monthly:** ₹1,398/month\\n"
                "   * **SLA & Install:** Ready in **4 business days** via physical optical fiber.\\n"
                "   * **Why it fits:** High physical fiber stability plus automatic 4G cellular backup so UPI payment checkouts never freeze during cable cuts.\\n\\n"
                "3. **Option 3: Pure Essential Fiber (Biz Fibre 100)**\\n"
                "   * **Net Monthly:** ₹1,099/month (Waived ₹0 setup fee on 12-month agreement)\\n"
                "   * **Why it fits:** Maximum savings, symmetric 100 Mbps pipe, 100% legal onboarding with your Udyam certificate.\\n\\n"
                "Which configuration aligns best with your day-to-day business priority?"
            )
            nat = (
                "### మీ వ్యాపారం కోసం ఎయిర్‌టెల్ బిజినెస్ ప్లాన్‌ల పోలిక\\n\\n"
                "మీ వ్యాపారానికి ఖచ్చితంగా బహుళ ఉత్తమ ఎంపికలు ఉన్నాయి! "
                f"టైర్ {tier} లోని మీ వ్యాపారం కోసం (బడ్జెట్ సుమారు ₹{budget:,}/నెల) ప్రధాన ఎంపికలు ఇక్కడ ఉన్నాయి:\\n\\n"
                "1. **ఎంపిక 1: వైర్‌లెస్ ఛాంపియన్ (బిజ్ 5G ఎయిర్‌ఫైబర్ 100 + సురక్షిత వై-ఫై)**\\n"
                "   * **నెలవారీ:** నెలకు ₹1,298 (బండిల్ డిస్కౌంట్‌తో)\\n"
                "   * **యాక్టివేషన్:** కేబుల్ కట్స్ లేకుండా 3 రోజుల్లో ప్రారంభం.\\n"
                "   * **ప్రయోజనం:** ప్లగ్ అండ్ ప్లే 5G యాంటెన్నాతో కస్టమర్ల కోసం ప్రత్యేక గెస్ట్ వై-ఫై.\\n\\n"
                "2. **ఎంపిక 2: హై-రెసిలెన్స్ వైర్డ్ ప్యాక్ (బిజ్ ఫైబర్ 100 + 4G ఆటో-ఫెయిల్‌ఓవర్)**\\n"
                "   * **నెలవారీ:** నెలకు ₹1,398\\n"
                "   * **ప్రయోజనం:** వైర్ కట్ అయినా ఆటోమేటిక్ 4G సెల్యులార్ బ్యాకప్‌తో నిరంతర యూపీఐ లావాదేవీలు.\\n\\n"
                "3. **ఎంపిక 3: ఎసెన్షియల్ ఫైబర్ (బిజ్ ఫైబర్ 100)**\\n"
                "   * **నెలవారీ:** నెలకు ₹1,099 (12 నెలల ఒప్పందంపై ₹0 సెటప్ రుసుము)\\n"
                "   * **ప్రయోజనం:** ఉద్యమ్ సర్టిఫికేట్‌తో తక్కువ ఖర్చులో హై-స్పీడ్ ఇంటర్నెట్.\\n\\n"
                "మీ రోజువారీ వ్యాపారానికి ఏ ప్లాన్ అనుకూలంగా ఉంటుంది?"
            )
            tts = (
                "Aapke business ke liye hamare paas AirFiber wireless aur Fixed Fiber dono ke shandar vikalp hain. "
                "AirFiber 1298 rupaye mein guest Wi-Fi ke saath 3 din mein activate hota hai, "
                "jabki Fixed Fiber 4G failover ke saath 1398 rupaye mein aata hai."
            )
            return lat, nat, tts

        # 1. Foreign Greetings
        if is_foreign:'''

if target in text:
    text = text.replace(target, comparison_block, 1)
    with open("backend/app/services/advisor_agent.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Added comparison handler to _generate_human_fallback")
else:
    print("Target not found in advisor_agent.py")
