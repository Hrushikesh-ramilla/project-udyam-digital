import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  Sparkles,
  ArrowDown,
  Send,
  Volume2,
  Sliders,
  CheckCircle2,
  ArrowRight,
  ShieldCheck,
  Clock,
  Languages,
  Globe,
  Check,
  Building2,
  Cpu,
  Layers,
  RotateCcw,
  Bot,
  User,
  Mic,
  MicOff,
} from "lucide-react";
import { ProductItem, CommercialBreakdown, MSMEProfileSlots } from "../types";
import { fetchProducts, calculateQuote, optimizeBudget, sendChatMessage } from "../api";
import { toLatinScript, toNativeScript, hasIndicScript } from "../transliteration";

interface StudioStudioProps {
  profileSlots: MSMEProfileSlots | null;
  recommendedSkus: string[];
  onProfileUpdated: (slots: MSMEProfileSlots, skus?: string[]) => void;
  onProceedToKYC: (quote: CommercialBreakdown) => void;
}

export interface ChatMessage {
  id: string;
  sender: "user" | "assistant";
  textLatin: string;
  textNative: string;
  timestamp: string;
  spokenTts?: string | null;
  quote?: CommercialBreakdown | null;
  recommendedSkus?: string[] | null;
}

const INDIC_LANGS = [
  { code: "auto", native: "Auto", latinName: "Auto" },
  { code: "te", native: "తెలుగు", latinName: "Telugu" },
  { code: "ta", native: "தமிழ்", latinName: "Tamil" },
  { code: "bn", native: "বাংলা", latinName: "Bengali" },
  { code: "gu", native: "ગુજરાતી", latinName: "Gujarati" },
  { code: "mr", native: "मराठी", latinName: "Marathi" },
  { code: "kn", native: "ಕನ್ನಡ", latinName: "Kannada" },
  { code: "ml", native: "മലയാളം", latinName: "Malayalam" },
  { code: "or", native: "ଓଡ଼ିଆ", latinName: "Odia" },
  { code: "hi", native: "हिन्दी", latinName: "Hindi" },
  { code: "en", native: "English", latinName: "English" },
];

const BCP47_LANG_MAP: Record<string, string> = {
  auto: "en-IN",
  hi: "hi-IN",
  te: "te-IN",
  ta: "ta-IN",
  bn: "bn-IN",
  gu: "gu-IN",
  mr: "mr-IN",
  kn: "kn-IN",
  ml: "ml-IN",
  or: "or-IN",
  en: "en-IN",
};

const GREETINGS: Record<
  string,
  { latin: string; native: string }
> = {
  te: {
    latin: "Namaste! Mee business ki Airtel Enterprise connectivity gurinchi ela sahayam cheyagalanu?",
    native: "నమస్తే! మీ వ్యాపారానికి ఎయిర్‌టెల్ ఎంటర్‌ప్రైజ్ కనెక్టివిటీ గురించి ఎలా సహాయపడగలను?",
  },
  hi: {
    latin: "Namaste! Aapke business ke liye Airtel Enterprise connectivity me kaise madad kar sakta hoon?",
    native: "नमस्ते! आपके बिजनेस के लिए एयरटेल एंटरप्राइज कनेक्टिविटी में कैसे मदद कर सकता हूँ?",
  },
  ta: {
    latin: "Vanakkam! Ungal business-kku Airtel Enterprise connectivity pathi eppadi udhava mudiyum?",
    native: "வணக்கம்! உங்கள் வணிகத்திற்கு ஏர்டெல் எண்டர்பிரைஸ் இணைப்பு குறித்து எவ்வாறு உதவ முடியும்?",
  },
  bn: {
    latin: "Nomoshkar! Aponar business-er jonno Airtel Enterprise connectivity niye kivabe sahajjo korte pari?",
    native: "নমস্কার! আপনার ব্যবসার জন্য এয়ারটেল এন্টারপ্রাইজ কানেক্টিভিটি নিয়ে কীভাবে সাহায্য করতে পারি?",
  },
  gu: {
    latin: "Namaste! Tamara business mate Airtel Enterprise connectivity ma kem madad kari shaku?",
    native: "નમસ્તે! તમારા બિઝનેસ માટે એરટેલ એન્ટરપ્રાઇઝ કનેક્ટિવિટીમાં કેમ મદદ કરી શકું?",
  },
  mr: {
    latin: "Namaskar! Tumchya business sathi Airtel Enterprise connectivity madhye kashi madat karu shakto?",
    native: "नमस्कार! तुमच्या व्यवसायासाठी एअरटेल एंटरप्राइज कनेक्टिव्हिटी मध्ये कशी मदत करू शकतो?",
  },
  kn: {
    latin: "Namaskara! Nimma business-ge Airtel Enterprise connectivity bagge hege sahayavagali?",
    native: "ನಮಸ್ಕಾರ! ನಿಮ್ಮ ವ್ಯಾಪಾರಕ್ಕೆ ಏರ್‌ಟೆಲ್ ಎಂಟರ್‌ಪ್ರೈಸ್ ಕನೆಕ್ಟಿವಿಟಿ ಬಗ್ಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?",
  },
  ml: {
    latin: "Namaskaram! Ningalude business-nu Airtel Enterprise connectivity kurichu engane sahayikkanam?",
    native: "നമസ്കാരം! നിങ്ങളുടെ ബിസിനസ്സിന് എയർടെൽ എന്റർപ്രൈസ് കണക്റ്റിവിറ്റി കുറിച്ച് എങ്ങനെ സഹായിക്കണം?",
  },
  or: {
    latin: "Namaskar! Aapananka business pain Airtel Enterprise connectivity re kipari sahajya kari paribi?",
    native: "ନମସ୍କାର! ଆପଣଙ୍କ ବ୍ୟବସାୟ ପାଇଁ ଏୟାରଟେଲ ଏଣ୍ଟରପ୍ରାଇଜ୍ କନେକ୍ଟିଭିଟିରେ କିପରି ସାହାଯ୍ୟ କରି ପାରିବି?",
  },
  en: {
    latin: "Hello! How can I assist you with Airtel Enterprise connectivity for your business today?",
    native: "Hello! How can I assist you with Airtel Enterprise connectivity for your business today?",
  },
};

function transliterateToNative(text: string, lang: string): string {
  const lower = text.toLowerCase().trim();
  if (lower.includes("bagunnara") || lower.includes("ela unna")) {
    return "బాగున్నారా ఎలా ఉన్నారు";
  }
  if (lower.includes("vanakkam") || lower.includes("eppadi")) {
    return "வணக்கம் எப்படி இருக்கிறீர்கள்";
  }
  if (lower.includes("kaise ho") || lower.includes("namaste")) {
    return "नमस्ते कैसे हैं आप";
  }
  if (lower.includes("kem cho")) {
    return "નમસ્તે કેમ છો";
  }
  if (lower.includes("kase ahat")) {
    return "नमस्कार कसे आहात";
  }
  if (lower.includes("hegidd")) {
    return "ನಮಸ್ಕಾರ ಹೇಗಿದ್ದೀರಿ";
  }
  if (lower.includes("sukhamano")) {
    return "നമസ്കാരം സുഖമാണോ";
  }
  if (lower.includes("kemiti ach")) {
    return "ନମସ୍କାର କେମିତି ଅଛନ୍ତି";
  }
  if (lower.includes("clinic") && (lower.includes("hyderabad") || lower.includes("hyd"))) {
    return "హైదరాబాద్‌లో 10 మంది సిబ్బందితో క్లినిక్";
  }
  if (lower.includes("kirana")) {
    return "టైర్ 2 లో కిరాణా షాప్, జీఎస్టీ లేదు";
  }
  if (lower.includes("textile") || lower.includes("surat")) {
    return "સુરતમાં કાપડનું કારખાનું, ૨૫ કારીગરો";
  }
  return text;
}

function FormattedChatText({ text }: { text: string }) {
  const lines = text.split("\n");
  return (
    <div className="space-y-1 text-xs sm:text-sm leading-relaxed">
      {lines.map((line, idx) => {
        const trimmed = line.trim();
        if (!trimmed) return <div key={idx} className="h-0.5" />;
        if (trimmed.startsWith("### ")) {
          return (
            <h4
              key={idx}
              className="font-serif text-sm sm:text-base font-normal text-white mt-1 mb-0.5 tracking-tight"
            >
              {trimmed.slice(4)}
            </h4>
          );
        }
        if (trimmed.startsWith("* ") || trimmed.startsWith("- ")) {
          const bulletContent = trimmed.slice(2);
          return (
            <div key={idx} className="flex items-start space-x-2 my-0.5 pl-1">
              <span className="w-1.5 h-1.5 rounded-full bg-[#e40000] mt-1.5 shrink-0" />
              <div>{parseInlineMarkdown(bulletContent)}</div>
            </div>
          );
        }
        return <p key={idx}>{parseInlineMarkdown(trimmed)}</p>;
      })}
    </div>
  );
}

function parseInlineMarkdown(content: string) {
  const parts = content.split(/(\*\*.*?\*\*|\*.*?\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={i} className="font-semibold text-white">
          {part.slice(2, -2)}
        </strong>
      );
    }
    if (part.startsWith("*") && part.endsWith("*")) {
      return (
        <em key={i} className="italic text-[#d9ad63]">
          {part.slice(1, -1)}
        </em>
      );
    }
    return part;
  });
}

export const StudioStudio: React.FC<StudioStudioProps> = ({
  profileSlots,
  recommendedSkus,
  onProfileUpdated,
  onProceedToKYC,
}) => {
  const [selectedLang, setSelectedLang] = useState("auto");
  const [scriptMode, setScriptMode] = useState<"latin" | "native">("latin");
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const toggleSpeechRecognition = () => {
    if (isListening) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsListening(false);
      return;
    }

    const SpeechRec =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;

    if (!SpeechRec) {
      alert("Speech recognition is not supported in this browser. Please use Chrome or Edge.");
      return;
    }

    try {
      const recognition = new SpeechRec();
      recognition.lang = BCP47_LANG_MAP[selectedLang] || "en-IN";
      recognition.interimResults = true;
      recognition.continuous = false;

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onresult = (event: any) => {
        const transcript = Array.from(event.results)
          .map((result: any) => (result as any)[0].transcript)
          .join("");
        setInput(transcript);
      };

      recognition.onerror = (event: any) => {
        console.warn("Speech recognition error:", event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err) {
      console.error("Speech recognition start failed:", err);
      setIsListening(false);
    }
  };

  // Chat message history (WhatsApp / ChatGPT preserved thread)
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const chatScrollRef = useRef<HTMLDivElement>(null);

  // CPQ state
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [selectedProductIds, setSelectedProductIds] = useState<string[]>(["P01", "P11", "P16", "P22"]);
  const [contractMonths, setContractMonths] = useState<number>(12);
  const [budgetSlider, setBudgetSlider] = useState<number>(2500);
  const [quote, setQuote] = useState<CommercialBreakdown | null>(null);
  const [activeArchetype, setActiveArchetype] = useState<string | null>(null);

  const initializedRef = useRef(false);
  const latestSlotsRef = useRef<MSMEProfileSlots | null>(profileSlots);
  useEffect(() => {
    if (profileSlots) latestSlotsRef.current = profileSlots;
  }, [profileSlots]);

  // Smooth scroll and pulse trigger for Configured Solution Architecture (Issue #14)
  const scrollToCartSection = () => {
    const el = document.getElementById("cpq-cart-section");
    if ((window as unknown as { __lenis?: { scrollTo: (target: string, opts?: { offset?: number }) => void } }).__lenis) {
      (window as unknown as { __lenis: { scrollTo: (target: string, opts?: { offset?: number }) => void } }).__lenis.scrollTo("#cpq-cart-section", { offset: -30 });
    } else if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
    if (el) {
      el.classList.add("ring-2", "ring-[#e40000]", "transition-all", "duration-500");
      setTimeout(() => {
        el.classList.remove("ring-2", "ring-[#e40000]");
      }, 2000);
    }
  };

  // Auto-scroll inner chat container smoothly without jumping page
  const scrollToBottom = () => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTo({
        top: chatScrollRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
    setTimeout(() => {
      if (chatScrollRef.current) {
        chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
      }
    }, 100);
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Load products
  useEffect(() => {
    async function load() {
      const prods = await fetchProducts();
      setProducts(prods);
    }
    load();
  }, []);

  // Real-time synchronization of recommendedSkus to Dynamic Cart (Issue #15)
  useEffect(() => {
    if (recommendedSkus && recommendedSkus.length > 0) {
      setSelectedProductIds(recommendedSkus);
    }
  }, [recommendedSkus]);

  // Recalculate quote
  useEffect(() => {
    if (selectedProductIds.length === 0) {
      setQuote(null);
      return;
    }
    async function runCalc() {
      try {
        const cart = selectedProductIds.map((pid) => ({ product_id: pid, quantity: 1 }));
        const res = await calculateQuote(cart, contractMonths);
        setQuote(res);
      } catch (err) {
        console.error("Quote calc failed", err);
      }
    }
    runCalc();
  }, [selectedProductIds, contractMonths]);

  // Text-to-speech
  const speakText = (text: string) => {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const clean = text.replace(/[*#_`-]/g, " ").trim();
      const utterance = new SpeechSynthesisUtterance(clean);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  };

  const archetypes = [
    {
      id: "micro",
      title: "Kirana & Retail",
      price: "₹1,499",
      badge: "GST-Free",
      desc: "Fiber 100M · Dual-Band Wi-Fi 6 · UPI Priority",
      skus: ["P01", "P09"],
      queryLatin: "Kirana store in Tier 2, 3 staff, no GST, need UPI uptime and WiFi, budget 1500",
      queryNative: "టైర్ 2 లో కిరాణా షాప్, 3 మంది సిబ్బంది, జీఎస్టీ లేదు, యూపీఐ మరియు వైఫై కావాలి, బడ్జెట్ 1500",
    },
    {
      id: "clinic",
      title: "Polyclinic & Health",
      price: "₹2,499",
      badge: "Static IP",
      desc: "Fiber 200M · Static IP · Telehealth SLA 4 Days",
      skus: ["P01", "P11", "P16", "P22"],
      queryLatin: "Dental clinic in Hyderabad Tier 1, 4 staff, GST registered, need static IP and cloud email",
      queryNative: "హైదరాబాద్ టైర్ 1 లో దంత క్లినిక్, 4 మంది సిబ్బంది, జీఎస్టీ ఉంది, స్టాటిక్ ఐపీ మరియు క్లౌడ్ ఇమెయిల్ కావాలి",
    },
    {
      id: "ca_firm",
      title: "CA & Corporate Firm",
      price: "₹4,999",
      badge: "GSTIN Mandated",
      desc: "Fiber 300M · Secure Cloud Backup · Active GSTIN",
      skus: ["P02", "P11", "P16", "P21"],
      queryLatin: "CA firm in Mumbai Tier 1, 10 employees, GSTIN active, need 300M fiber and cloud security, budget 5000",
      queryNative: "ముంబై టైర్ 1 లో సిఏ సంస్థ, 10 మంది ఉద్యోగులు, క్రియాశీల జీఎస్టీ, 300M ఫైబర్ మరియు క్లౌడ్ భద్రత కావాలి, బడ్జెట్ 5000",
    },
    {
      id: "mfg",
      title: "Textile Mill",
      price: "₹14,999",
      badge: "IoT & CCTV",
      desc: "Gigabit Fiber · SD-WAN · Multi-Camera Cloud AI",
      skus: ["P01", "P05", "P09", "P11", "P12", "P16"],
      queryLatin: "Surat ma textile mill chhe, 25 karigaro, GST chhe, CCTV ane WiFi 6 joie, budget 15000",
      queryNative: "સુરતમાં કાપડનું કારખાનું છે, ૨૫ કારીગરો, જીએસટી છે, સીસીટીવી અને વાઇફાઇ ૬ જોઈએ, બજેટ ૧૫૦૦૦",
    },
  ];

  const activeGreetingKey = selectedLang === "auto" ? "en" : selectedLang;
  const activeGreeting = GREETINGS[activeGreetingKey] || GREETINGS["te"];

  const handleSelectArchetype = (arch: typeof archetypes[0]) => {
    setActiveArchetype(arch.id);
    setSelectedProductIds(arch.skus);
    handleSend(arch.queryLatin, arch.queryNative);
  };

  const handleStartConversation = (mode: "latin" | "native") => {
    setScriptMode(mode);
    const greeting = GREETINGS[activeGreetingKey] || GREETINGS["te"];
    const initMsg: ChatMessage = {
      id: `adv_${Date.now()}`,
      sender: "assistant",
      textLatin: greeting.latin,
      textNative: greeting.native,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      spokenTts: mode === "latin" ? greeting.latin : greeting.native,
    };
    setMessages([initMsg]);
  };

  const handleClearChat = () => {
    setMessages([]);
  };

  const handleSend = async (textOverride?: string, nativeOverride?: string) => {
    const q = (textOverride || input).trim();
    if (!q) return;
    setInput("");

    const hasIndic = /[\u0900-\u0D7F]/.test(q);
    const effectiveMode = scriptMode || (hasIndic ? "native" : "latin");
    if (!scriptMode) {
      setScriptMode(effectiveMode);
    }

    const qLatin = hasIndic ? toLatinScript(q) : q;
    const qNative = hasIndic ? q : toNativeScript(q, "auto");

    const userMsg: ChatMessage = {
      id: `usr_${Date.now()}`,
      sender: "user",
      textLatin: qLatin,
      textNative: qNative,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const historyPayload = messages.slice(-4).map((m) => ({
        role: m.sender === "user" ? "user" : "assistant",
        content: scriptMode === "latin" ? (m.textLatin || m.textNative) : (m.textNative || m.textLatin),
      }));

      const activeSlots = latestSlotsRef.current || profileSlots;
      const res = await sendChatMessage(
        q,
        activeSlots,
        null, // Unconstrained AI multilingual auto-detect for all 22 Indian languages
        effectiveMode,
        historyPayload
      );
      latestSlotsRef.current = res.slots;
      onProfileUpdated(res.slots, res.recommended_skus);
      if (res.recommended_skus && res.recommended_skus.length > 0) {
        setSelectedProductIds(res.recommended_skus);
      }

      const rawLatin = res.display_latin || res.display_markdown || "";
      const rawNative = res.display_native || res.display_markdown || "";

      const isBogusGreeting = hasIndicScript(rawNative) && rawNative.length < 50 && rawLatin.length > 80 && (rawNative.includes("स्वागत") || rawNative.includes("స్వాగతం") || rawNative.includes("வரவேற்கிறோம்"));

      const advLatin = hasIndicScript(rawLatin) ? toLatinScript(rawLatin) : (rawLatin || toLatinScript(rawNative));
      const advNative = (hasIndicScript(rawNative) && !isBogusGreeting) ? rawNative : toNativeScript(advLatin, "hi");

      const advMsg: ChatMessage = {
        id: `adv_${Date.now()}`,
        sender: "assistant",
        textLatin: advLatin,
        textNative: advNative,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        spokenTts: scriptMode === "latin" ? advLatin : (res.spoken_tts_text || advNative),
        quote: res.quote,
        recommendedSkus: res.recommended_skus,
      };
      setMessages((prev) => [...prev, advMsg]);
    } catch {
      const errorMsg: ChatMessage = {
        id: `adv_err_${Date.now()}`,
        sender: "assistant",
        textLatin: "I am experiencing a temporary connection delay to the Airtel Enterprise Advisor service. Please try asking your question again in a moment.",
        textNative: selectedLang === "te"
          ? "ఎయిర్‌టెల్ ఎంటర్‌ప్రైజ్ సేవతో కనెక్టివిటీ సమస్య ఏర్పడింది. దయచేసి మళ్లీ ప్రయత్నించండి."
          : (selectedLang === "hi"
            ? "एयरटेल एंटरप्राइज सेवा से कनेक्ट करने में कुछ समस्या आ रही है। कृपया कुछ देर बाद पुनः प्रयास करें।"
            : "I am experiencing a temporary connection delay to the Airtel Enterprise Advisor service. Please try asking your question again in a moment."),
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        spokenTts: "I am experiencing a temporary connection delay. Please try again.",
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleRunOptimizer = async () => {
    try {
      const profilePayload = {
        segment: profileSlots?.segment || "micro",
        city_tier: profileSlots?.city_tier || 2,
        employee_count: profileSlots?.employee_count || 3,
        num_sites: profileSlots?.num_sites || 1,
        has_gstin: profileSlots?.has_gstin || false,
        detected_needs: profileSlots?.detected_needs || [],
      };
      const res = await optimizeBudget(profilePayload, budgetSlider);
      setSelectedProductIds(res.selected_skus);
      setQuote(res.commercials);
    } catch (err) {
      console.error("Budget optimizer failed", err);
    }
  };

  return (
    <div className="space-y-8 w-full">
      {/* Archetype Quick Select Ribbon */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {archetypes.map((arch) => {
          const isSelected = activeArchetype === arch.id;
          return (
            <motion.div
              key={arch.id}
              whileHover={{ y: -2 }}
              onClick={() => handleSelectArchetype(arch)}
              className={`p-5 rounded-2xl cursor-pointer transition-all border ${
                isSelected
                  ? "bg-slate-800/95 border-[#e40000] ring-1 ring-[#e40000] shadow-[0_0_24px_rgba(228,0,0,0.25)]"
                  : "bg-slate-900/80 border-slate-700/60 hover:border-slate-500 hover:bg-slate-800/50"
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-base font-bold text-white tracking-tight truncate">
                  {arch.title}
                </span>
                <span
                  className={`text-xs font-mono font-semibold px-2.5 py-0.5 rounded-full border ${
                    isSelected
                      ? "bg-[#e40000]/20 text-[#ff4d4d] border-[#e40000]/30"
                      : "bg-slate-800 text-slate-300 border-slate-700"
                  }`}
                >
                  {arch.badge}
                </span>
              </div>
              <div className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight my-1.5">
                {arch.price} <span className="text-sm font-medium text-slate-400">/mo</span>
              </div>
              <p className="text-xs text-slate-300 font-medium leading-relaxed mt-2 line-clamp-2">{arch.desc}</p>
            </motion.div>
          );
        })}
      </div>

      {/* WhatsApp / ChatGPT Preserved Chat Thread Box */}
      <div className="luxury-glass rounded-3xl p-5 sm:p-7 border border-[rgba(235,229,217,0.08)] shadow-[0_20px_50px_rgba(0,0,0,0.7)] space-y-4">
        {/* Chat Header & Dual-Script Mode Switch */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[rgba(235,229,217,0.06)]">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-xl bg-[#e40000] flex items-center justify-center text-white shadow-sm">
              <Bot className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base sm:text-lg font-bold text-white tracking-tight">
                  Airtel Enterprise Advisor
                </h3>
                <span className="live-pulse-dot" />
              </div>
              <p className="text-xs text-slate-400 font-mono">
                Universal AI Engine · Auto-Detects Any Global & Indian Language
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2 self-start sm:self-auto">
            {/* Real-time Script Mode Switch */}
            <div className="flex items-center space-x-1 bg-[#030405] p-1 rounded-xl border border-[rgba(235,229,217,0.08)]">
              <button
                onClick={() => setScriptMode("latin")}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition-all cursor-pointer flex items-center space-x-1.5 ${
                  scriptMode === "latin"
                    ? "bg-[#e40000] text-white shadow-[0_0_12px_rgba(228,0,0,0.4)]"
                    : "text-slate-300 hover:text-white"
                }`}
                title="Speak in regional language using English alphabet (e.g. bagunnara ela unnaru)"
              >
                <span>🔤 English Words</span>
              </button>
              <button
                onClick={() => setScriptMode("native")}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition-all cursor-pointer flex items-center space-x-1.5 ${
                  scriptMode === "native"
                    ? "bg-[#e40000] text-white shadow-[0_0_12px_rgba(228,0,0,0.4)]"
                    : "text-slate-300 hover:text-white"
                }`}
                title="Speak in traditional native regional scripts (e.g. బాగున్నారా)"
              >
                <span>🪶 Native Script</span>
              </button>
            </div>

            {/* Clear History Button */}
            <button
              onClick={handleClearChat}
              className="p-1.5 rounded-xl bg-white/[0.03] hover:bg-white/[0.08] text-slate-300 hover:text-white border border-white/[0.06] transition-colors cursor-pointer"
              title="Reset conversation"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>



        {/* Scrollable Preserved Message Thread Container (Empty on initial load) */}
        {(messages.length > 0 || loading) && (
          <div
            ref={chatScrollRef}
            className="max-h-[420px] overflow-y-auto overscroll-y-auto space-y-3 pr-2 scrollbar-thin"
            onWheel={(e) => {
              const el = chatScrollRef.current;
              if (!el) return;
              const { scrollTop, scrollHeight, clientHeight } = el;
              const isDown = e.deltaY > 0;
              const isUp = e.deltaY < 0;
              const atBottom = scrollTop + clientHeight >= scrollHeight - 5;
              const atTop = scrollTop <= 5;
              // Seamless scroll chaining: bubble to parent page when at scroll boundaries
              if ((isDown && atBottom) || (isUp && atTop)) {
                return;
              }
              e.stopPropagation();
            }}
          >
            {messages.map((m) => {
              const isUser = m.sender === "user";
              let displayedText = scriptMode === "latin" ? (m.textLatin || m.textNative) : (m.textNative || m.textLatin);
              
              if (scriptMode === "native" && displayedText.length < 50 && (m.textLatin?.length || 0) > 80 && (displayedText.includes("स्वागत") || displayedText.includes("స్వాగతం"))) {
                displayedText = toNativeScript(m.textLatin, "hi");
              }

              if (scriptMode === "latin" && hasIndicScript(displayedText)) {
                displayedText = toLatinScript(displayedText);
              } else if (scriptMode === "native" && !hasIndicScript(displayedText)) {
                displayedText = toNativeScript(displayedText, "auto");
              }
              return (
                <motion.div
                  key={m.id}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2 }}
                  className={`flex flex-col ${isUser ? "items-end" : "items-start"}`}
                >
                  <div
                    className={`rounded-2xl p-4 text-sm sm:text-base leading-relaxed max-w-[90%] sm:max-w-[80%] shadow-sm ${
                      isUser
                        ? "bg-gradient-to-r from-[#e40000]/30 to-[#e40000]/15 border border-[#e40000]/50 text-white rounded-tr-sm shadow-sm"
                        : "bg-slate-900/95 border border-slate-700/70 text-slate-100 rounded-tl-sm space-y-2.5 shadow-sm"
                    }`}
                  >
                    <FormattedChatText text={displayedText} />

                    {/* Issue #14: Interactive In-Chat CTA Card */}
                    {!isUser && Boolean(m.quote) && (m.recommendedSkus?.length || 0) > 0 && (
                      <div className="mt-2.5 pt-2.5 border-t border-white/[0.08] space-y-2">
                        <div className="p-3 rounded-xl bg-gradient-to-r from-white/[0.04] to-white/[0.02] border border-white/[0.08] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                          <div className="space-y-0.5">
                            <div className="flex items-center space-x-1.5 text-[10px] font-mono text-[#d9ad63] uppercase tracking-wider">
                              <Sparkles className="w-3 h-3 text-[#d9ad63]" />
                              <span>Recommended Enterprise Solution</span>
                            </div>
                            <div className="text-xs font-semibold text-white">
                              {m.quote!.items.map((i) => i.product_name).join(" + ")} · ₹{m.quote!.net_mrc_inr.toLocaleString()}/mo
                            </div>
                            <div className="text-[10px] text-slate-300">
                              {m.quote!.net_otc_inr === 0 ? "₹0 Setup Fee Waived (12-Mo Agreement)" : "Fast Track Setup"} · {m.quote!.guaranteed_sla_days || 3}d SLA
                            </div>
                          </div>
                          <button
                            onClick={scrollToCartSection}
                            className="inline-flex items-center justify-center space-x-1.5 px-3 py-2 rounded-xl bg-[#e40000] hover:bg-[#b30000] text-white text-xs font-medium shadow-[0_0_15px_rgba(228,0,0,0.4)] transition-all cursor-pointer shrink-0"
                          >
                            <span>Review in Cart & Start KYC</span>
                            <ArrowDown className="w-3.5 h-3.5 animate-bounce" />
                          </button>
                        </div>
                      </div>
                    )}

                    {/* Audio Listen Button for Advisor */}
                    {!isUser && m.spokenTts && (
                      <div className="pt-1.5 flex items-center justify-between text-[11px] text-slate-300 border-t border-white/[0.04]">
                        <button
                          onClick={() => speakText(m.spokenTts || "")}
                          className="text-xs text-[#d9ad63] hover:text-white flex items-center space-x-1.5 cursor-pointer font-mono"
                        >
                          <Volume2 className="w-3.5 h-3.5" />
                          <span>Listen Audio</span>
                        </button>
                        <span className="font-mono text-[10px] text-slate-300/50">{m.timestamp}</span>
                      </div>
                    )}
                    {isUser && (
                      <div className="text-right text-[10px] font-mono text-white/50 mt-1">
                        {m.timestamp}
                      </div>
                    )}
                  </div>
                </motion.div>
              );
            })}

            {/* Typing Indicator */}
          {loading && (
            <motion.div
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center space-x-2 text-xs text-slate-300 bg-[#030405] p-3 rounded-2xl rounded-tl-sm w-fit border border-[rgba(235,229,217,0.06)]"
            >
              <div className="flex space-x-1 items-center">
                <span className="w-1.5 h-1.5 bg-[#e40000] rounded-full animate-bounce [animation-delay:-0.3s]" />
                <span className="w-1.5 h-1.5 bg-[#e40000] rounded-full animate-bounce [animation-delay:-0.15s]" />
                <span className="w-1.5 h-1.5 bg-[#e40000] rounded-full animate-bounce" />
              </div>
              <span className="font-mono text-[11px]">Airtel Advisor is formulating solution...</span>
            </motion.div>
          )}
          </div>
        )}

        {/* Input Bar */}
        <div className="flex items-center space-x-2.5 bg-slate-900/90 rounded-2xl p-2.5 border border-slate-700/80 focus-within:border-[#e40000] transition-colors shadow-inner">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder={
              isListening
                ? "Listening... speak now in your regional language..."
                : scriptMode === "latin"
                ? "Type a message..."
                : "Type or speak in any language worldwide (English, Hindi, Telugu, Spanish, French, etc.)..."
            }
            className="flex-1 bg-transparent px-4 py-2 text-sm text-white placeholder-slate-500 focus:outline-none font-medium"
          />
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            type="button"
            onClick={toggleSpeechRecognition}
            title={isListening ? "Listening... click to stop" : `Voice input in ${selectedLang === "auto" ? "English / Indic" : selectedLang}`}
            className={`p-3 rounded-xl transition-all cursor-pointer ${
              isListening
                ? "bg-red-500 text-white animate-pulse shadow-[0_0_16px_rgba(239,68,68,0.6)]"
                : "bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
            }`}
          >
            {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => handleSend()}
            disabled={!input.trim() || loading}
            className="p-3 bg-[#e40000] hover:bg-[#b30000] disabled:opacity-30 text-white rounded-xl transition-all shadow-[0_0_16px_rgba(228,0,0,0.4)] cursor-pointer"
          >
            <Send className="w-4 h-4" />
          </motion.button>
        </div>
      </div>

      {/* Live Solution Blueprint & Commercial Action Card */}
      {quote && (
        <motion.div
          id="cpq-cart-section"
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="luxury-glass rounded-3xl p-6 sm:p-8 border border-[rgba(235,229,217,0.12)] space-y-6 scroll-mt-6"
        >
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[rgba(235,229,217,0.08)]">
            <div>
              <span className="text-[10px] font-mono text-[#d9ad63] uppercase tracking-widest block mb-1">
                Configured Solution Architecture
              </span>
              <h3 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                Smart Enterprise Connectivity Pack
              </h3>
              <div className="flex items-center space-x-3 text-xs text-slate-300 mt-1">
                <span className="flex items-center space-x-1">
                  <Clock className="w-3.5 h-3.5 text-[#e40000]" />
                  <span>{quote.guaranteed_sla_days} Days SLA Guarantee</span>
                </span>
                <span>·</span>
                <span className="flex items-center space-x-1">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                  <span>
                    {quote.gst_exempt_eligible
                      ? "Non-GST Eligible (Udyam Verified)"
                      : "B2B ITC Eligible"}
                  </span>
                </span>
              </div>
            </div>

            <div className="text-right">
              <span className="text-[10px] font-mono text-slate-300 uppercase tracking-widest block">
                Net Monthly Investment
              </span>
              <div className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
                ₹{quote.net_mrc_inr.toLocaleString()}{" "}
                <span className="text-sm font-medium text-slate-400">/month</span>
              </div>
              <p className="text-[10px] text-emerald-400 font-mono mt-0.5">
                {quote.net_otc_inr === 0 ? "100% One-Time Setup Fee (OTC) Waived" : `OTC: ₹${quote.net_otc_inr}`}
              </p>
            </div>
          </div>

          {/* Bundled SKUs */}
          <div>
            <h4 className="text-[10px] font-mono text-slate-300 uppercase tracking-widest mb-3">
              Bundled Enterprise SKUs:
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5">
              {quote.items.map((item) => (
                <div
                  key={item.product_id}
                  className="flex flex-col justify-between p-3 rounded-xl bg-slate-900/80 border border-slate-700/60 gap-1.5"
                >
                  <div className="flex items-start justify-between w-full">
                    <div className="flex items-center space-x-2.5 min-w-0">
                      <CheckCircle2 className="w-4 h-4 text-[#e40000] shrink-0 mt-0.5" />
                      <div className="truncate">
                        <div className="text-xs font-medium text-white truncate">
                          {item.product_name}
                        </div>
                        <div className="text-[10px] text-slate-300 font-mono">
                          {item.product_id} · SLA {item.install_days}d
                        </div>
                      </div>
                    </div>
                    <span className="text-xs font-mono text-white shrink-0 ml-2">
                      ₹{item.total_mrc_inr}/mo
                    </span>
                  </div>
                  {item.reason_explanation && (
                    <div className="flex items-center gap-1.5 text-[9.5px] text-amber-300/90 font-mono bg-amber-500/10 px-2 py-1 rounded-md border border-amber-500/20">
                      <Sparkles className="w-2.5 h-2.5 text-amber-400 shrink-0" />
                      <span className="line-clamp-2 leading-tight">{item.reason_explanation}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Interactive Budget Reverse Optimization Slider */}
          <div className="p-4 sm:p-5 rounded-2xl bg-slate-900/90 border border-slate-700/60 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-white flex items-center space-x-2">
                <Sliders className="w-3.5 h-3.5 text-[#e40000]" />
                <span>Reverse Budget Optimization Slider</span>
              </span>
              <span className="text-xl font-bold text-amber-400 tracking-tight">
                ₹{budgetSlider.toLocaleString()}{" "}
                <span className="text-xs font-medium text-slate-400">/mo target</span>
              </span>
            </div>
            <input
              type="range"
              min="999"
              max="25000"
              step="500"
              value={budgetSlider}
              onChange={(e) => setBudgetSlider(Number(e.target.value))}
              className="w-full h-1.5 bg-white/10 rounded-lg appearance-none cursor-pointer accent-[#e40000]"
            />
            <div className="flex justify-between items-center text-[10px] font-mono text-slate-300">
              <span>₹999 (Kirana Entry)</span>
              <button
                onClick={handleRunOptimizer}
                className="text-[#d9ad63] hover:text-white font-medium underline cursor-pointer"
              >
                Re-optimize bundle for ₹{budgetSlider.toLocaleString()} →
              </button>
              <span>₹25,000 (Gigabit Enterprise)</span>
            </div>
          </div>

          {/* CTA Proceed to Instant KYC */}
          <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="text-xs text-slate-300 leading-relaxed">
              <span>Zero field verification required · </span>
              <span className="text-emerald-400">DPDP Act 2023 Compliant In-Memory Redaction</span>
            </div>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onProceedToKYC(quote)}
              className="w-full sm:w-auto px-7 py-3.5 rounded-xl bg-[#e40000] hover:bg-[#b30000] text-white font-bold text-sm tracking-wide transition-all shadow-[0_0_25px_rgba(228,0,0,0.5)] flex items-center justify-center space-x-2 cursor-pointer"
            >
              <span>Proceed to Instant KYC</span>
              <ArrowRight className="w-4 h-4" />
            </motion.button>
          </div>
        </motion.div>
      )}
    </div>
  );
};
