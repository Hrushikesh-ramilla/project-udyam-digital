import React, { useState, useEffect, useRef } from "react";
import {
  Mic,
  MicOff,
  Send,
  Volume2,
  Sparkles,
  User,
  Bot,
  CheckCircle2,
  ArrowRight,
  Languages,
  Zap,
  Activity,
  Layers,
  HelpCircle,
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
        <strong key={i} className="font-semibold text-white">
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
    <div className="space-y-2 text-xs sm:text-[13px] leading-relaxed">
      {lines.map((line, idx) => {
        const trimmed = line.trim();
        if (!trimmed) return <div key={idx} className="h-1" />;

        if (trimmed.startsWith("### ")) {
          return (
            <h4 key={idx} className="font-serif text-base sm:text-lg font-normal text-white tracking-tight pt-1">
              {trimmed.replace("### ", "")}
            </h4>
          );
        }

        if (trimmed.startsWith("* ") || trimmed.startsWith("- ")) {
          const content = trimmed.substring(2);
          return (
            <div key={idx} className="flex items-start space-x-2 pl-1 text-white/80">
              <span className="text-[#e40000] font-bold mt-0.5">•</span>
              <span>{renderInlineFormatting(content)}</span>
            </div>
          );
        }

        return <p key={idx} className="text-white/80">{renderInlineFormatting(line)}</p>;
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
  { code: "auto", label: "Auto", native: "Auto-Detect", voiceTag: "en-IN" },
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

export const AdvisorChat: React.FC<AdvisorChatProps> = ({ onProfileUpdated, onProceedToCPQ }) => {
  const [selectedLang, setSelectedLang] = useState<string>("auto");
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "m0",
      sender: "advisor",
      text: "### Enterprise Telecom Copilot\n\nNamaste! I architect custom Airtel connectivity solutions tailored for Bharat's micro-enterprises. Speak or type in your native regional language (Telugu, Tamil, Bengali, Gujarati, Marathi, Kannada, Malayalam, Odia, Hindi, or English) — or select an archetype below to test the deterministic DAG solver.",
      spokenTts: "Namaste! Welcome to Airtel Business Udyam Digital. Please describe your business and telecom requirements in your preferred language.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [currentSlots, setCurrentSlots] = useState<MSMEProfileSlots | null>(null);
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

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
      alert("Web Speech API is not supported in this browser. Please type your message.");
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
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          id: `err_${Date.now()}`,
          sender: "advisor",
          text: "I encountered a connection error. Please try again or click one of the verified archetypes below.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Verified Business Archetypes for instant live demos
  const archetypes = [
    {
      title: "Kirana / Retail (Non-GST)",
      badge: "GST-Free",
      color: "border-emerald-500/30 text-emerald-400 bg-emerald-500/10",
      query: "जयपुर में 2 मेडिकल किराना शॉप्स हैं, 4 स्टाफ, यूपीఐ बार बार रुकता है, जीएसटी नहीं है, बजट 1500 महीना",
    },
    {
      title: "Clinic & Diagnostics",
      badge: "Low-Latency",
      color: "border-sky-500/30 text-sky-400 bg-sky-500/10",
      query: "హైదరాబాద్‌లో 4 మందితో క్లినిక్ ఉంది, జీఎస్టీ లేదు, 2500 బడ్జెట్, వేగవంతమైన వైఫై కావాలి",
    },
    {
      title: "Legal & CA Chambers",
      badge: "GSTIN Mandated",
      color: "border-champagne-400/30 text-champagne-400 bg-champagne-400/10",
      query: "CA firm in Mumbai with 15 staff, active GSTIN, need static IP fiber and secure cloud backup, budget 6000",
    },
    {
      title: "Surat Textile Unit",
      badge: "IoT Enterprise",
      color: "border-red-500/30 text-red-400 bg-red-500/10",
      query: "સુરતમાં કાપડનું કારખાનું છે, ૨૫ કારીગરો, જીએસટી છે, સીસીટીવી અને વાઇફાઇ ૬ જોઈએ, બજેટ ૧૫૦૦૦",
    },
  ];

  return (
    <div className="flex flex-col h-[650px] glass-card rounded-2xl overflow-hidden border border-white/[0.08] shadow-[0_24px_60px_rgba(0,0,0,0.8)]">
      {/* Copilot Header */}
      <div className="p-4 bg-[#0a0a09]/90 border-b border-white/[0.07] flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="relative flex items-center justify-center">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#e40000]/20 to-[#e40000]/5 border border-[#e40000]/30 flex items-center justify-center text-[#e40000]">
              <Sparkles className="w-4 h-4" />
            </div>
            {loading && (
              <span className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            )}
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="font-serif text-base font-medium text-white tracking-tight">
                Multilingual Telecom Copilot
              </h3>
              <span className="text-[9px] font-mono uppercase tracking-[0.2em] bg-white/[0.04] text-white/50 border border-white/[0.06] px-2 py-0.5 rounded-full">
                10 Indic Scripts
              </span>
            </div>
            <p className="text-[10px] font-mono text-white/40">
              Deterministic Entity Extraction · Zero Hallucination DAG Solver
            </p>
          </div>
        </div>

        {/* Live Slot Badges */}
        <div className="flex items-center space-x-2">
          {currentSlots?.is_complete && (
            <div className="flex items-center space-x-1.5 text-[10px] font-mono">
              <span className="bg-white/[0.04] text-white/80 border border-white/[0.08] px-2 py-0.5 rounded-full">
                Tier {currentSlots.city_tier}
              </span>
              <span className="bg-white/[0.04] text-white/80 border border-white/[0.08] px-2 py-0.5 rounded-full capitalize">
                {currentSlots.segment}
              </span>
              <span
                className={`px-2 py-0.5 rounded-full border ${
                  currentSlots.has_gstin
                    ? "bg-purple-500/15 text-purple-300 border-purple-500/30"
                    : "bg-emerald-500/15 text-emerald-400 border-emerald-500/30"
                }`}
              >
                {currentSlots.has_gstin ? "GSTIN Mandated" : "Non-GST Eligible"}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Indic Language Selector Bar */}
      <div className="px-3.5 py-2 bg-[#080808]/90 border-b border-white/[0.05] flex items-center space-x-1.5 overflow-x-auto no-scrollbar">
        <span className="text-[9px] font-mono uppercase tracking-[0.2em] text-white/40 shrink-0 mr-1 flex items-center space-x-1">
          <Languages className="w-3 h-3 text-[#e40000]" />
          <span>Script:</span>
        </span>
        {INDIC_LANGUAGES.map((lang) => (
          <button
            key={lang.code}
            onClick={() => setSelectedLang(lang.code)}
            className={`px-2.5 py-1 rounded-full text-[11px] font-medium transition-all shrink-0 cursor-pointer ${
              selectedLang === lang.code
                ? "bg-[#e40000] text-white shadow-[0_0_12px_rgba(228,0,0,0.4)]"
                : "bg-white/[0.03] text-white/60 hover:text-white hover:bg-white/[0.08] border border-white/[0.05]"
            }`}
          >
            {lang.native}
          </button>
        ))}
      </div>

      {/* Messages Feed */}
      <div className="flex-1 p-4 sm:p-5 overflow-y-auto space-y-4">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex items-start space-x-3 ${m.sender === "user" ? "flex-row-reverse space-x-reverse" : ""}`}
          >
            <div
              className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 text-xs font-mono font-medium ${
                m.sender === "user"
                  ? "bg-[#e40000] text-white shadow-[0_0_12px_rgba(228,0,0,0.3)]"
                  : "bg-white/[0.06] text-white/70 border border-white/[0.08]"
              }`}
            >
              {m.sender === "user" ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
            </div>

            <div
              className={`max-w-[85%] rounded-2xl p-4 shadow-xl ${
                m.sender === "user"
                  ? "bg-gradient-to-r from-[#b30000] to-[#e40000] text-white rounded-tr-none border border-red-500/30"
                  : "bg-[#111110]/95 text-[#f2efea] border border-white/[0.08] rounded-tl-none backdrop-blur-xl"
              }`}
            >
              {renderFormattedMessage(m.text)}

              {/* TTS Listen Button for Copilot */}
              {m.spokenTts && (
                <div className="mt-3 pt-2.5 border-t border-white/[0.06] flex items-center justify-between text-xs text-white/40">
                  <span className="text-[10px] font-mono tracking-wider uppercase">Spoken Voice Ready</span>
                  <button
                    onClick={() => speakText(m.spokenTts!)}
                    className="flex items-center space-x-1.5 text-[#d9ad63] hover:text-white transition-colors cursor-pointer text-xs"
                  >
                    <Volume2 className="w-3.5 h-3.5" />
                    <span>Play Narration</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center space-x-3 text-white/60 text-xs bg-[#111110]/90 border border-white/[0.08] w-fit px-4 py-2 rounded-full shadow-lg">
            <div className="flex items-end space-x-1 h-3">
              <span className="w-1 bg-[#e40000] rounded-full audio-bar-1" />
              <span className="w-1 bg-[#d9ad63] rounded-full audio-bar-2" />
              <span className="w-1 bg-[#e40000] rounded-full audio-bar-3" />
              <span className="w-1 bg-white rounded-full audio-bar-4" />
            </div>
            <span className="font-mono text-[11px] text-white/60">Solving CPQ DAG Constraints...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Archetype Quick-Triggers */}
      <div className="px-3 py-2 bg-[#080808]/60 border-t border-white/[0.05] overflow-x-auto no-scrollbar">
        <div className="flex items-center space-x-2 text-xs">
          <span className="text-[9px] font-mono uppercase tracking-[0.2em] text-white/40 shrink-0 flex items-center space-x-1">
            <Zap className="w-3 h-3 text-[#d9ad63]" />
            <span>Presets:</span>
          </span>
          {archetypes.map((arch, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(arch.query)}
              className="bg-[#121210] hover:bg-[#181816] border border-white/[0.07] hover:border-white/[0.18] px-3 py-1.5 rounded-xl whitespace-nowrap transition-all text-xs flex items-center space-x-2 shrink-0 cursor-pointer group"
            >
              <span className="font-medium text-white/90 group-hover:text-white">{arch.title}</span>
              <span className={`text-[9px] font-mono px-1.5 py-0.2 rounded-full border ${arch.color}`}>
                {arch.badge}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Input Bar */}
      <div className="p-3 bg-[#0a0a09]/95 border-t border-white/[0.08] flex items-center space-x-2">
        <button
          onClick={handleVoiceInput}
          className={`p-2.5 rounded-xl border transition-all cursor-pointer ${
            isListening
              ? "bg-[#e40000] text-white border-red-500 animate-pulse shadow-[0_0_16px_rgba(228,0,0,0.6)]"
              : "bg-white/[0.04] text-white/70 border-white/[0.08] hover:bg-white/[0.08] hover:text-white"
          }`}
          title="Click to speak via Web Speech API"
        >
          {isListening ? <MicOff className="w-4 h-4 text-white" /> : <Mic className="w-4 h-4" />}
        </button>

        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder={
            isListening
              ? "Listening in " + (INDIC_LANGUAGES.find((l) => l.code === selectedLang)?.native || "Indic") + "..."
              : "Type or speak in Telugu, Tamil, Bengali, Gujarati, Kannada, Marathi, Hindi, English..."
          }
          className="flex-1 bg-[#121210] border border-white/[0.08] rounded-xl px-4 py-2.5 text-xs sm:text-sm text-white placeholder-white/40 focus:outline-none focus:border-[#e40000] transition-colors"
        />

        <button
          onClick={() => handleSend()}
          disabled={!input.trim()}
          className="p-2.5 bg-[#e40000] hover:bg-[#b30000] disabled:opacity-30 disabled:cursor-not-allowed text-white rounded-xl transition-all shadow-[0_0_16px_rgba(228,0,0,0.3)] cursor-pointer"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
