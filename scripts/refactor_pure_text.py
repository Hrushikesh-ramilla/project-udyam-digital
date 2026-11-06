with open("frontend/src/components/StudioStudio.tsx", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update GREETINGS type definition
old_greetings_type = '''const GREETINGS: Record<
  string,
  { latin: string; native: string; actionLatin: string; actionNative: string }
> = {'''

new_greetings_type = '''const GREETINGS: Record<
  string,
  { latin: string; native: string }
> = {'''

code = code.replace(old_greetings_type, new_greetings_type)

# Remove actionLatin and actionNative from GREETINGS entries
import re
code = re.sub(r'\s*actionLatin:[^\n]+', '', code)
code = re.sub(r'\s*actionNative:[^\n]+', '', code)

# 2. Update initial 2 messages rendering (lines 567-617)
old_cards_block = '''          {messages.length === 0 ? (
            /* First Time Minimal Left/Right Cards */
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 py-2">
              {/* Left Card: English Words */}
              <motion.div
                whileHover={{ y: -2, borderColor: "rgba(228,0,0,0.4)" }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleStartConversation("latin")}
                className="p-4 sm:p-5 rounded-2xl bg-white/[0.02] hover:bg-white/[0.04] border border-white/[0.08] transition-all cursor-pointer flex flex-col justify-between space-y-3 group shadow-lg"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-medium bg-[#e40000]/15 text-[#ff6b6b] border border-[#e40000]/30">
                      🔤 English Words
                    </span>
                    <span className="text-[10px] text-[#B39D82]/60 font-mono">Latin Alphabet</span>
                  </div>
                  <p className="font-serif text-sm sm:text-base text-[#EBE5D9] leading-relaxed">
                    {activeGreeting.latin}
                  </p>
                </div>
                <div className="pt-2 flex items-center justify-between text-xs text-[#d9ad63] group-hover:text-[#EBE5D9] transition-colors border-t border-white/[0.04]">
                  <span>{activeGreeting.actionLatin}</span>
                  <ArrowRight className="w-3.5 h-3.5 transform group-hover:translate-x-1 transition-transform" />
                </div>
              </motion.div>

              {/* Right Card: Traditional Native Script */}
              <motion.div
                whileHover={{ y: -2, borderColor: "rgba(217,173,99,0.4)" }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleStartConversation("native")}
                className="p-4 sm:p-5 rounded-2xl bg-white/[0.02] hover:bg-white/[0.04] border border-white/[0.08] transition-all cursor-pointer flex flex-col justify-between space-y-3 group shadow-lg"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-[#d9ad63]/15 text-[#d9ad63] border border-[#d9ad63]/30">
                      🪶 సాంప్రదాయ లిపి
                    </span>
                    <span className="text-[10px] text-[#B39D82]/60 font-mono">Native Script</span>
                  </div>
                  <p className="font-serif text-sm sm:text-base text-[#EBE5D9] leading-relaxed">
                    {activeGreeting.native}
                  </p>
                </div>
                <div className="pt-2 flex items-center justify-between text-xs text-[#d9ad63] group-hover:text-[#EBE5D9] transition-colors border-t border-white/[0.04]">
                  <span>{activeGreeting.actionNative}</span>
                  <ArrowRight className="w-3.5 h-3.5 transform group-hover:translate-x-1 transition-transform" />
                </div>
              </motion.div>
            </div>
          ) : ('''

new_cards_block = '''          {messages.length === 0 ? (
            /* First Turn: Just the text messages side-by-side, zero badges/labels/buttons */
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 py-1">
              {/* Left Message: English Words */}
              <motion.div
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                onClick={() => handleStartConversation("latin")}
                className="p-4 rounded-2xl rounded-tl-sm bg-[#030405] hover:bg-white/[0.04] border border-[rgba(235,229,217,0.08)] hover:border-[#e40000]/40 transition-all cursor-pointer text-xs sm:text-sm text-[#EBE5D9] leading-relaxed shadow-sm font-sans"
              >
                {activeGreeting.latin}
              </motion.div>

              {/* Right Message: Traditional Script */}
              <motion.div
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                onClick={() => handleStartConversation("native")}
                className="p-4 rounded-2xl rounded-tl-sm bg-[#030405] hover:bg-white/[0.04] border border-[rgba(235,229,217,0.08)] hover:border-[#e40000]/40 transition-all cursor-pointer text-xs sm:text-sm text-[#EBE5D9] leading-relaxed shadow-sm font-sans"
              >
                {activeGreeting.native}
              </motion.div>
            </div>
          ) : ('''

code = code.replace(old_cards_block, new_cards_block)

# 3. Simplify placeholder
old_placeholder = '''            placeholder={
              scriptMode === "latin"
                ? "Type in English words (e.g. \\"bagunnara ela unnaru\\", \\"10 staff clinic in Hyderabad\\")..."
                : "సాంప్రదాయ లిపిలో టైప్ చేయండి (ఉదా. \\"హైదరాబాద్‌లో 4 మందితో క్లినిక్ ఉంది\\")..."
            }'''

new_placeholder = '''            placeholder={
              scriptMode === "latin"
                ? "Type a message..."
                : (selectedLang === "hi" ? "संदेश टाइप करें..." : "సందేశాన్ని టైప్ చేయండి...")
            }'''

code = code.replace(old_placeholder, new_placeholder)

with open("frontend/src/components/StudioStudio.tsx", "w", encoding="utf-8") as f:
    f.write(code)

print("Applied pure text message refactor successfully!")
