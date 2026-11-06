with open("frontend/src/components/StudioStudio.tsx", "r", encoding="utf-8") as f:
    code = f.read()

# Replace the messages container block
old_container_block = '''        {/* Scrollable Preserved Message Thread Container */}
        <div ref={chatScrollRef} className="max-h-[380px] min-h-[160px] overflow-y-auto space-y-3 pr-2 no-scrollbar">
          {messages.length === 0 ? (
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
          ) : (
            messages.map((m) => {'''

new_container_block = '''        {/* Scrollable Preserved Message Thread Container (Empty on initial load) */}
        {(messages.length > 0 || loading) && (
          <div ref={chatScrollRef} className="max-h-[380px] overflow-y-auto space-y-3 pr-2 no-scrollbar">
            {messages.map((m) => {'''

code = code.replace(old_container_block, new_container_block)

# Replace the end of messages.map to match the closing of (messages.length > 0 || loading)
old_map_end = '''              );
            })
          )}

          {/* Typing Indicator */}'''

new_map_end = '''              );
            })}

            {/* Typing Indicator */}'''

code = code.replace(old_map_end, new_map_end)

# Also ensure closing tag for (messages.length > 0 || loading)
old_typing_end = '''              <span className="font-mono text-[11px]">Airtel Advisor is formulating solution...</span>
            </motion.div>
          )}
        </div>'''

new_typing_end = '''              <span className="font-mono text-[11px]">Airtel Advisor is formulating solution...</span>
            </motion.div>
          )}
          </div>
        )}'''

code = code.replace(old_typing_end, new_typing_end)

with open("frontend/src/components/StudioStudio.tsx", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated StudioStudio.tsx to zero initial text!")
