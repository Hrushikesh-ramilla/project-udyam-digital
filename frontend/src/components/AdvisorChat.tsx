import React, { useState, useEffect, useRef } from "react";
import { Mic, MicOff, Send, Volume2, Sparkles, User, Bot, CheckCircle2, ArrowRight } from "lucide-react";
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
        <strong key={i} className="font-bold text-white">
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
    <div className="space-y-1.5 text-xs sm:text-sm">
      {lines.map((line, idx) => {
        const trimmed = line.trim();
        if (!trimmed) return <div key={idx} className="h-1" />;

        if (trimmed.startsWith("### ")) {
          return (
            <h4 key={idx} className="font-bold text-white text-sm sm:text-base tracking-tight mb-1">
              {trimmed.replace("### ", "")}
            </h4>
          );
        }

        if (trimmed.startsWith("* ") || trimmed.startsWith("- ")) {
          const content = trimmed.substring(2);
          return (
            <div key={idx} className="flex items-start space-x-1.5 ml-1">
              <span className="text-red-400 font-bold">•</span>
              <span>{renderInlineFormatting(content)}</span>
            </div>
          );
        }

        return <p key={idx}>{renderInlineFormatting(line)}</p>;
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

export const AdvisorChat: React.FC<AdvisorChatProps> = ({ onProfileUpdated, onProceedToCPQ }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "m0",
      sender: "advisor",
      text: "### Namaste! Welcome to Airtel Business Udyam Digital 🙏\n\nI am your AI Enterprise Advisor. Tell me about your business in **Hindi, Hinglish, or English**:\n* What kind of business do you run?\n* Which city and how many staff?\n* Do you have a GST number or Udyam certificate?",
      spokenTts: "Namaste! Airtel Business Udyam Digital mein aapka swagat hai. Kripya batayein ki aap kis sheher mein hain aur aapka business kis type ka hai.",
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
      // Try to select Hindi or Indian English voice if available
      const voices = window.speechSynthesis.getVoices();
      const indicVoice = voices.find((v) => v.lang === "hi-IN" || v.lang === "en-IN");
      if (indicVoice) utterance.voice = indicVoice;
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
    recognition.lang = "en-IN"; // Captures Indian English and Hinglish smoothly
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

      // Speak back using symbol-free TTS text
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
          text: "I encountered a connection error. Please try again or use the presets below.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const quickPrompts = [
    "Bhaiya, meri Jaipur mein 2 medical shops hain, 6 staff, GPay atakta hai, GST nahi hai.",
    "We are a CA firm in Mumbai with 15 staff, active GSTIN, need fast cloud email.",
    "Textile unit in Surat with 30 workers, active GST, budget 15000/mo.",
  ];

  return (
    <div className="flex flex-col h-[580px] bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
      {/* Advisor Header with Extracted Slots Badges */}
      <div className="p-4 bg-slate-950/70 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-red-600/20 border border-red-500/30 flex items-center justify-center text-red-500">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">Multilingual AI Telecom Advisor</h3>
            <p className="text-xs text-slate-400">Hindi • Hinglish • English (Web Speech Voice-Enabled)</p>
          </div>
        </div>

        {/* Live Slot Tags & Action */}
        <div className="flex items-center space-x-2">
          {currentSlots && currentSlots.is_complete && (
            <div className="hidden md:flex items-center space-x-1.5 text-xs">
              <span className="bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-2 py-0.5 rounded-md font-medium">
                Tier {currentSlots.city_tier}
              </span>
              <span className="bg-sky-500/20 text-sky-300 border border-sky-500/30 px-2 py-0.5 rounded-md font-medium capitalize">
                {currentSlots.segment}
              </span>
              <span className={`px-2 py-0.5 rounded-md font-medium border ${
                currentSlots.has_gstin
                  ? "bg-purple-500/20 text-purple-300 border-purple-500/30"
                  : "bg-amber-500/20 text-amber-300 border-amber-500/30"
              }`}>
                {currentSlots.has_gstin ? "GST Registered" : "Udyam Only (GST-Free)"}
              </span>
            </div>
          )}

          {currentSlots && currentSlots.is_complete && onProceedToCPQ && (
            <button
              onClick={onProceedToCPQ}
              className="flex items-center space-x-1 px-3 py-1.5 rounded-xl bg-red-600 hover:bg-red-500 text-white text-xs font-semibold shadow-md shadow-red-600/30 transition-all cursor-pointer"
            >
              <span>CPQ Cart</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Messages Feed */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex items-start space-x-2.5 ${m.sender === "user" ? "flex-row-reverse space-x-reverse" : ""}`}
          >
            <div
              className={`w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 text-xs font-bold ${
                m.sender === "user" ? "bg-red-600 text-white" : "bg-slate-800 text-red-400 border border-slate-700"
              }`}
            >
              {m.sender === "user" ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm ${
                m.sender === "user"
                  ? "bg-red-600 text-white rounded-tr-none"
                  : "bg-slate-800/90 text-slate-100 border border-slate-700/60 rounded-tl-none"
              }`}
            >
              {renderFormattedMessage(m.text)}

              {/* TTS Listen Button for Advisor messages */}
              {m.spokenTts && (
                <div className="mt-2 pt-2 border-t border-slate-700/50 flex items-center justify-between text-xs text-slate-400">
                  <span className="text-[11px] text-slate-400">Spoken TTS Narration Ready</span>
                  <button
                    onClick={() => speakText(m.spokenTts!)}
                    className="flex items-center space-x-1 text-red-400 hover:text-red-300 transition-colors"
                  >
                    <Volume2 className="w-3.5 h-3.5" />
                    <span>Listen</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center space-x-2 text-slate-400 text-xs">
            <div className="w-2 h-2 rounded-full bg-red-500 animate-ping" />
            <span>Consulting deterministic CPQ catalogue...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompts Chips */}
      <div className="px-3 py-1.5 bg-slate-950/40 border-t border-slate-800/50 flex items-center space-x-2 overflow-x-auto text-xs no-scrollbar">
        <span className="text-slate-400 text-[11px] whitespace-nowrap">Try:</span>
        {quickPrompts.map((p, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(p)}
            className="bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 px-2.5 py-1 rounded-full whitespace-nowrap transition-colors"
          >
            {p.slice(0, 32)}...
          </button>
        ))}
      </div>

      {/* Input Bar */}
      <div className="p-3 bg-slate-950 border-t border-slate-800 flex items-center space-x-2">
        <button
          onClick={handleVoiceInput}
          className={`p-2.5 rounded-xl border transition-all ${
            isListening
              ? "bg-red-600 text-white border-red-500 animate-pulse"
              : "bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700 hover:text-white"
          }`}
          title="Click to speak in Hindi/Hinglish"
        >
          {isListening ? <MicOff className="w-4 h-4 text-white" /> : <Mic className="w-4 h-4" />}
        </button>

        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder={isListening ? "Listening... bolna shuru karein..." : "Type or speak in Hindi / Hinglish..."}
          className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-2 text-sm text-white focus:outline-none focus:border-red-500 placeholder-slate-500 transition-colors"
        />

        <button
          onClick={() => handleSend()}
          disabled={!input.trim()}
          className="p-2.5 bg-red-600 hover:bg-red-500 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-xl transition-all shadow-md shadow-red-600/20"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
