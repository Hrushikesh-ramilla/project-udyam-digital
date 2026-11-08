import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  Mic,
  MicOff,
  Send,
  Volume2,
  ArrowDown,
  Sparkles,
  User,
  Bot,
  Languages,
} from "lucide-react";
import { MSMEProfileSlots } from "../types";
import { sendChatMessage } from "../api";

interface Message {
  id: string;
  sender: "user" | "advisor";
  text: string;
  spokenTts?: string;
  slots?: MSMEProfileSlots;
  recommendedSkus?: string[];
}

interface AdvisorChatProps {
  onProfileUpdated: (slots: MSMEProfileSlots, skus?: string[]) => void;
  onProceedToCPQ?: () => void;
}

const renderInlineFormatting = (line: string) => {
  const parts = line.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={i} className="font-semibold text-[#EBE5D9]">
          {part.slice(2, -2)}
        </strong>
      );
    }
    return part;
  });
};

const renderFormattedMessage = (text: string) => {
  const lines = text.split("\n");
  return (
    <div className="space-y-1.5 text-xs sm:text-[13px] leading-relaxed">
      {lines.map((line, idx) => {
        const trimmed = line.trim();
        if (!trimmed) return <div key={idx} className="h-1" />;

        if (trimmed.startsWith("### ")) {
          return (
            <h4 key={idx} className="font-serif text-base font-normal text-[#EBE5D9] tracking-tight">
              {trimmed.replace("### ", "")}
            </h4>
          );
        }

        if (trimmed.startsWith("* ") || trimmed.startsWith("- ")) {
          const content = trimmed.substring(2);
          return (
            <div key={idx} className="flex items-start space-x-2 pl-1 text-[#EBE5D9]/90">
              <span className="text-[#e40000] font-bold mt-0.5">•</span>
              <span>{renderInlineFormatting(content)}</span>
            </div>
          );
        }

        return <p key={idx} className="text-[#EBE5D9]/90">{renderInlineFormatting(line)}</p>;
      })}
    </div>
  );
};

interface SpeechRecognitionEvent {
  results: {
    [index: number]: {
      [index: number]: {
        transcript: string;
      };
    };
  };
}

interface ISpeechRecognition {
  lang: string;
  interimResults: boolean;
  onstart: () => void;
  onend: () => void;
  onerror: () => void;
  onresult: (event: SpeechRecognitionEvent) => void;
  start: () => void;
}

interface IWindowSpeech {
  SpeechRecognition?: new () => ISpeechRecognition;
  webkitSpeechRecognition?: new () => ISpeechRecognition;
}

interface LangOption {
  code: string;
  label: string;
  native: string;
  voiceTag: string;
}

const INDIC_LANGUAGES: LangOption[] = [
  { code: "auto", label: "Auto", native: "Auto", voiceTag: "en-IN" },
  { code: "te", label: "Telugu", native: "తెలుగు", voiceTag: "te-IN" },
  { code: "ta", label: "Tamil", native: "தமிழ்", voiceTag: "ta-IN" },
  { code: "bn", label: "Bengali", native: "বাংলা", voiceTag: "bn-IN" },
  { code: "gu", label: "Gujarati", native: "ગુજરાતી", voiceTag: "gu-IN" },
  { code: "mr", label: "Marathi", native: "मराठी", voiceTag: "mr-IN" },
  { code: "kn", label: "Kannada", native: "ಕನ್ನಡ", voiceTag: "kn-IN" },
  { code: "ml", label: "Malayalam", native: "മലയാളം", voiceTag: "ml-IN" },
  { code: "or", label: "Odia", native: "ଓଡ଼ିଆ", voiceTag: "or-IN" },
  { code: "hi", label: "Hindi", native: "हिन्दी", voiceTag: "hi-IN" },
  { code: "en", label: "English", native: "English", voiceTag: "en-IN" },
];

export const AdvisorChat: React.FC<AdvisorChatProps> = ({ onProfileUpdated }) => {
  const [selectedLang, setSelectedLang] = useState<string>("auto");
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "m0",
      sender: "advisor",
      text: "### Enterprise Telecom Copilot\n\nConfigure custom enterprise connectivity in your mother tongue. Speak or type across 10 Indian languages, or select a verified archetype below.",
      spokenTts: "Welcome to Airtel Business Udyam Digital. Please describe your business and telecom requirements in your preferred language.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [currentSlots, setCurrentSlots] = useState<MSMEProfileSlots | null>(null);
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
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


  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const speakText = (text: string) => {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      const voices = window.speechSynthesis.getVoices();
      const activeLang = INDIC_LANGUAGES.find((l) => l.code === selectedLang);
      const prefix = activeLang && activeLang.code !== "auto" ? activeLang.voiceTag.split("-")[0] : "en";
      const matchedVoice = voices.find((v) => v.lang.startsWith(prefix)) || voices.find((v) => v.lang === "hi-IN" || v.lang === "en-IN");
      if (matchedVoice) utterance.voice = matchedVoice;
      window.speechSynthesis.speak(utterance);
    }
  };

  const handleVoiceInput = () => {
    const speechWindow = window as unknown as IWindowSpeech;
    const SpeechRecognitionClass =
      speechWindow.SpeechRecognition || speechWindow.webkitSpeechRecognition;

    if (!SpeechRecognitionClass) {
      alert("Web Speech API not supported in this browser. Please type.");
      return;
    }

    if (isListening) {
      setIsListening(false);
      return;
    }

    const recognition = new SpeechRecognitionClass();
    const activeLang = INDIC_LANGUAGES.find((l) => l.code === selectedLang);
    recognition.lang = activeLang && activeLang.code !== "auto" ? activeLang.voiceTag : "en-IN";
    recognition.interimResults = false;

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => setIsListening(false);

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript);
      handleSend(transcript);
    };

    recognition.start();
  };

  const handleSend = async (textToSend?: string) => {
    const query = (textToSend || input).trim();
    if (!query) return;

    const userMsg: Message = {
      id: `u_${Date.now()}`,
      sender: "user",
      text: query,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await sendChatMessage(query, currentSlots);
      setCurrentSlots(res.slots);
      onProfileUpdated(res.slots, res.recommended_skus);

      const botMsg: Message = {
        id: `b_${Date.now()}`,
        sender: "advisor",
        text: res.display_markdown,
        spokenTts: res.spoken_tts_text,
        slots: res.slots,
        recommendedSkus: res.recommended_skus,
      };

      setMessages((prev) => [...prev, botMsg]);

      if (res.spoken_tts_text) {
        speakText(res.spoken_tts_text);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: `err_${Date.now()}`,
          sender: "advisor",
          text: "Connection timeout. Please select a verified archetype below.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const archetypes = [
    {
      title: "Kirana (Non-GST)",
      badge: "GST-Free",
      query: "जयपुर में 2 मेडिकल किराना शॉप्स हैं, 4 स्टाफ, यूपीआई रुकता है, जीएसटी नहीं है, बजट 1500 महीना",
    },
    {
      title: "Clinic & Health",
      badge: "Low-Latency",
      query: "హైదరాబాద్‌లో 4 మందితో క్లినిక్ ఉంది, జీఎస్టీ లేదు, 2500 బడ్జెట్, వేగవంతమైన వైఫై కావాలి",
    },
    {
      title: "CA Chambers",
      badge: "GSTIN",
      query: "CA firm in Mumbai with 15 staff, active GSTIN, need static IP fiber and secure cloud backup, budget 6000",
    },
    {
      title: "Textile Mill",
      badge: "IoT",
      query: "સુરતમાં કાપડનું કારખાનું છે, ૨૫ કારીગરો, જીએસટી છે, સીસીટીવી અને વાઇફાઇ ૬ જોઈએ, બજેટ ૧૫૦૦૦",
    },
  ];

  return (
    <div className="flex flex-col h-[620px] luxury-glass rounded-2xl overflow-hidden border border-[rgba(235,229,217,0.06)] shadow-apple-card">
      {/* Header */}
      <div className="p-4 bg-[#080a0d]/90 border-b border-[rgba(235,229,217,0.06)] flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="w-7 h-7 rounded-lg bg-[#e40000]/15 border border-[#e40000]/30 flex items-center justify-center text-[#e40000]">
            <Sparkles className="w-3.5 h-3.5" />
          </div>
          <div>
            <h3 className="font-sans text-sm font-medium text-[#EBE5D9]">
              Telecom Copilot
            </h3>
            <p className="text-[10px] font-mono text-[#B39D82]">10 Indic Languages · DAG Solver</p>
          </div>
        </div>

        {/* Live Slot Tags */}
        {currentSlots?.is_complete && (
          <div className="flex items-center space-x-1 text-[10px] font-mono">
            <span className="bg-white/[0.04] text-[#EBE5D9] px-2 py-0.5 rounded-full border border-white/[0.06]">
              Tier {currentSlots.city_tier}
            </span>
            <span className="bg-white/[0.04] text-[#EBE5D9] px-2 py-0.5 rounded-full border border-white/[0.06] capitalize">
              {currentSlots.segment}
            </span>
            <span
              className={`px-2 py-0.5 rounded-full border ${
                currentSlots.has_gstin
                  ? "bg-purple-500/15 text-purple-300 border-purple-500/30"
                  : "bg-emerald-500/15 text-emerald-400 border-emerald-500/30"
              }`}
            >
              {currentSlots.has_gstin ? "GSTIN" : "Non-GST"}
            </span>
          </div>
        )}
      </div>

      {/* Indic Language Pills */}
      <div className="px-3 py-1.5 bg-[#050709] border-b border-[rgba(235,229,217,0.04)] flex items-center space-x-1 overflow-x-auto no-scrollbar">
        <span className="text-[9px] font-mono tracking-wider text-[#B39D82]/60 uppercase shrink-0 mr-1 flex items-center space-x-1">
          <Languages className="w-3 h-3 text-[#e40000]" />
          <span>Script:</span>
        </span>
        {INDIC_LANGUAGES.map((lang) => (
          <motion.button
            key={lang.code}
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.96 }}
            onClick={() => setSelectedLang(lang.code)}
            className={`px-2.5 py-0.5 rounded-full text-[11px] font-medium transition-colors shrink-0 cursor-pointer ${
              selectedLang === lang.code
                ? "bg-[#e40000] text-white shadow-[0_0_12px_rgba(228,0,0,0.4)]"
                : "bg-white/[0.03] text-[#B39D82] hover:text-[#EBE5D9] border border-white/[0.04]"
            }`}
          >
            {lang.native}
          </motion.button>
        ))}
      </div>

      {/* Messages Feed */}
      <div
        className="flex-1 p-4 overflow-y-auto overscroll-y-auto space-y-3 scrollbar-thin"
        onWheel={(e) => {
          const el = e.currentTarget;
          const { scrollTop, scrollHeight, clientHeight } = el;
          const isDown = e.deltaY > 0;
          const isUp = e.deltaY < 0;
          const atBottom = scrollTop + clientHeight >= scrollHeight - 2;
          const atTop = scrollTop <= 2;
          if ((isDown && atBottom) || (isUp && atTop)) {
            return;
          }
          e.stopPropagation();
        }}
      >
        <AnimatePresence initial={false}>
          {messages.map((m) => (
            <motion.div
              key={m.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
              className={`flex items-start space-x-2.5 ${m.sender === "user" ? "flex-row-reverse space-x-reverse" : ""}`}
            >
              <div
                className={`w-6 h-6 rounded-lg flex items-center justify-center shrink-0 text-xs font-mono ${
                  m.sender === "user"
                    ? "bg-[#e40000] text-white shadow-[0_0_12px_rgba(228,0,0,0.3)]"
                    : "bg-[#0f1216] text-[#B39D82] border border-[rgba(235,229,217,0.06)]"
                }`}
              >
                {m.sender === "user" ? <User className="w-3 h-3" /> : <Bot className="w-3 h-3" />}
              </div>

              <div
                className={`max-w-[85%] rounded-2xl p-3.5 shadow-md ${
                  m.sender === "user"
                    ? "bg-[#e40000] text-white rounded-tr-none"
                    : "bg-[#0b0e12]/95 text-[#EBE5D9] border border-[rgba(235,229,217,0.06)] rounded-tl-none"
                }`}
              >
                {renderFormattedMessage(m.text)}

                {/* Issue #14: In-Chat Action Button */}
                {m.sender === "advisor" && (m.recommendedSkus?.length || 0) > 0 && (
                  <div className="mt-2.5 pt-2.5 border-t border-white/[0.08]">
                    <button
                      onClick={scrollToCartSection}
                      className="w-full inline-flex items-center justify-center space-x-1.5 px-3 py-1.5 rounded-lg bg-[#e40000] hover:bg-[#b30000] text-white text-xs font-medium shadow-[0_0_12px_rgba(228,0,0,0.4)] transition-all cursor-pointer"
                    >
                      <span>Review in Cart & Start KYC</span>
                      <ArrowDown className="w-3 h-3 animate-bounce" />
                    </button>
                  </div>
                )}

                {m.spokenTts && (
                  <div className="mt-2.5 pt-2 border-t border-[rgba(235,229,217,0.06)] flex items-center justify-between text-xs text-[#B39D82]">
                    <span className="text-[9px] font-mono uppercase tracking-wider">Voice Ready</span>
                    <button
                      onClick={() => speakText(m.spokenTts!)}
                      className="flex items-center space-x-1 text-[#d9ad63] hover:text-[#EBE5D9] transition-colors cursor-pointer text-xs"
                    >
                      <Volume2 className="w-3 h-3" />
                      <span>Play</span>
                    </button>
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center space-x-2 text-[#B39D82] text-xs bg-[#0b0e12] border border-[rgba(235,229,217,0.06)] w-fit px-3 py-1.5 rounded-full"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-[#e40000] animate-pulse" />
            <span className="font-mono text-[10px]">Evaluating DAG constraints...</span>
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Archetype Quick-Triggers */}
      <div className="px-3 py-2 bg-[#050709] border-t border-[rgba(235,229,217,0.04)] overflow-x-auto no-scrollbar">
        <div className="flex items-center space-x-1.5 text-xs">
          <span className="text-[9px] font-mono tracking-wider text-[#B39D82]/50 uppercase shrink-0">
            Presets:
          </span>
          {archetypes.map((arch, idx) => (
            <motion.button
              key={idx}
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => handleSend(arch.query)}
              className="bg-[#0b0e12] hover:bg-[#12161c] border border-[rgba(235,229,217,0.06)] hover:border-[rgba(235,229,217,0.14)] px-2.5 py-1 rounded-xl whitespace-nowrap transition-all text-xs flex items-center space-x-1.5 shrink-0 cursor-pointer"
            >
              <span className="text-[#EBE5D9] font-medium text-[11px]">{arch.title}</span>
              <span className="text-[9px] font-mono text-[#B39D82] bg-white/[0.04] px-1 py-0.2 rounded">
                {arch.badge}
              </span>
            </motion.button>
          ))}
        </div>
      </div>

      {/* Input Bar */}
      <div className="p-3 bg-[#080a0d] border-t border-[rgba(235,229,217,0.06)] flex items-center space-x-2">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleVoiceInput}
          className={`p-2 rounded-xl border transition-all cursor-pointer ${
            isListening
              ? "bg-[#e40000] text-white border-red-500 animate-pulse shadow-[0_0_16px_rgba(228,0,0,0.6)]"
              : "bg-white/[0.04] text-[#B39D82] border-white/[0.06] hover:bg-white/[0.08] hover:text-[#EBE5D9]"
          }`}
          title="Voice input"
        >
          {isListening ? <MicOff className="w-4 h-4 text-white" /> : <Mic className="w-4 h-4" />}
        </motion.button>

        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Speak or type in Telugu, Tamil, Bengali, Hindi, English..."
          className="flex-1 bg-[#030405] border border-[rgba(235,229,217,0.08)] rounded-xl px-3.5 py-2 text-xs text-[#EBE5D9] placeholder-[#B39D82]/40 focus:outline-none focus:border-[#e40000] transition-colors"
        />

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => handleSend()}
          disabled={!input.trim()}
          className="p-2 bg-[#e40000] hover:bg-[#b30000] disabled:opacity-20 disabled:cursor-not-allowed text-white rounded-xl transition-all shadow-[0_0_12px_rgba(228,0,0,0.3)] cursor-pointer"
        >
          <Send className="w-4 h-4" />
        </motion.button>
      </div>
    </div>
  );
};
