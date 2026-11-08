with open("frontend/src/components/StudioStudio.tsx", "r", encoding="utf-8") as f:
    text = f.read()

target = """    try {
      const res = await sendChatMessage(
        q,
        profileSlots,
        selectedLang !== "auto" ? selectedLang : null,
        effectiveMode
      );"""

replacement = """    try {
      const historyPayload = messages.slice(-4).map((m) => ({
        role: m.sender === "user" ? "user" : "assistant",
        content: scriptMode === "latin" ? (m.textLatin || m.textNative) : (m.textNative || m.textLatin),
      }));

      const res = await sendChatMessage(
        q,
        profileSlots,
        selectedLang !== "auto" ? selectedLang : null,
        effectiveMode,
        historyPayload
      );"""

if target in text:
    text = text.replace(target, replacement, 1)
    with open("frontend/src/components/StudioStudio.tsx", "w", encoding="utf-8") as f:
        f.write(text)
    print("Successfully patched StudioStudio.tsx with historyPayload")
else:
    print("Target not found in StudioStudio.tsx")
