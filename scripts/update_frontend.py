path = 'frontend/src/components/StudioStudio.tsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add import
if 'from "../transliteration"' not in content:
    target_imp = 'import { fetchProducts, calculateQuote, optimizeBudget, sendChatMessage } from "../api";'
    new_imp = target_imp + '\nimport { toLatinScript, toNativeScript, hasIndicScript } from "../transliteration";'
    content = content.replace(target_imp, new_imp, 1)
    print("Added transliteration import")

# 2. Update handleSendMessage user message and assistant message
old_send_block = '''    const qLatin = textOverride || (hasIndic ? q : q);
    const qNative =
      nativeOverride || (hasIndic ? q : transliterateToNative(q, activeGreetingKey));

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
      const res = await sendChatMessage(
        q,
        profileSlots,
        selectedLang !== "auto" ? selectedLang : null,
        effectiveMode
      );
      onProfileUpdated(res.slots, res.recommended_skus);
      if (res.recommended_skus && res.recommended_skus.length > 0) {
        setSelectedProductIds(res.recommended_skus);
      }

      const advMsg: ChatMessage = {
        id: `adv_${Date.now()}`,
        sender: "assistant",
        textLatin: res.display_latin || res.display_markdown,
        textNative: res.display_native || res.display_markdown,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        spokenTts: res.spoken_tts_text,
      };
      setMessages((prev) => [...prev, advMsg]);'''

new_send_block = '''    const qLatin = hasIndic ? toLatinScript(q) : q;
    const qNative = hasIndic ? q : toNativeScript(q, activeGreetingKey);

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
      const res = await sendChatMessage(
        q,
        profileSlots,
        selectedLang !== "auto" ? selectedLang : null,
        effectiveMode
      );
      onProfileUpdated(res.slots, res.recommended_skus);
      if (res.recommended_skus && res.recommended_skus.length > 0) {
        setSelectedProductIds(res.recommended_skus);
      }

      const rawLatin = res.display_latin || res.display_markdown || "";
      const rawNative = res.display_native || res.display_markdown || "";

      const advLatin = hasIndicScript(rawLatin) ? toLatinScript(rawLatin) : (rawLatin || toLatinScript(rawNative));
      const advNative = hasIndicScript(rawNative) ? rawNative : (toNativeScript(rawNative || rawLatin, activeGreetingKey));

      const advMsg: ChatMessage = {
        id: `adv_${Date.now()}`,
        sender: "assistant",
        textLatin: advLatin,
        textNative: advNative,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        spokenTts: scriptMode === "latin" ? advLatin : (res.spoken_tts_text || advNative),
      };
      setMessages((prev) => [...prev, advMsg]);'''

if old_send_block in content:
    content = content.replace(old_send_block, new_send_block, 1)
    print("Updated handleSendMessage")

# 3. Update message rendering
old_render_block = '              const displayedText = scriptMode === "latin" ? m.textLatin : m.textNative;'
new_render_block = '''              let displayedText = scriptMode === "latin" ? (m.textLatin || m.textNative) : (m.textNative || m.textLatin);
              if (scriptMode === "latin" && hasIndicScript(displayedText)) {
                displayedText = toLatinScript(displayedText);
              } else if (scriptMode === "native" && !hasIndicScript(displayedText)) {
                displayedText = toNativeScript(displayedText, activeGreetingKey);
              }'''

if old_render_block in content:
    content = content.replace(old_render_block, new_render_block, 1)
    print("Updated message rendering block")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("StudioStudio.tsx successfully upgraded with client-side dual-script guarantees.")
