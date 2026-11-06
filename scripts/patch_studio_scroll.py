with open("frontend/src/components/StudioStudio.tsx", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("const messagesEndRef = useRef<HTMLDivElement>(null);", "const chatScrollRef = useRef<HTMLDivElement>(null);")

old_scroll = """  // Auto-scroll chat to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };"""

new_scroll = """  // Auto-scroll inner chat container smoothly without jumping page
  const scrollToBottom = () => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTo({
        top: chatScrollRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  };"""

content = content.replace(old_scroll, new_scroll)

with open("frontend/src/components/StudioStudio.tsx", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated scrollToBottom successfully.")
