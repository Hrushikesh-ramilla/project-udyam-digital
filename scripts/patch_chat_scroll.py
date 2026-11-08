import re

# 1. Update frontend/src/index.css
with open("frontend/src/index.css", "r", encoding="utf-8") as f:
    css_content = f.read()

scrollbar_css = """
/* Custom Chat & Container Scrollbar */
.scrollbar-thin::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.scrollbar-thin::-webkit-scrollbar-track {
  background: rgba(3, 4, 5, 0.4);
  border-radius: 9999px;
}
.scrollbar-thin::-webkit-scrollbar-thumb {
  background: rgba(235, 229, 217, 0.28);
  border-radius: 9999px;
  border: 1px solid rgba(235, 229, 217, 0.08);
}
.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background: rgba(235, 229, 217, 0.55);
}
.scrollbar-thin {
  scrollbar-width: thin;
  scrollbar-color: rgba(235, 229, 217, 0.28) rgba(3, 4, 5, 0.4);
}
"""

if ".scrollbar-thin" not in css_content:
    css_content += "\n" + scrollbar_css
    with open("frontend/src/index.css", "w", encoding="utf-8") as f:
        f.write(css_content)
    print("Updated frontend/src/index.css with .scrollbar-thin")

# 2. Update frontend/src/components/StudioStudio.tsx
with open("frontend/src/components/StudioStudio.tsx", "r", encoding="utf-8") as f:
    studio_content = f.read()

# Replace scrollToBottom
old_scroll_fn = """  // Auto-scroll inner chat container smoothly without jumping page
  const scrollToBottom = () => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTo({
        top: chatScrollRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  };"""

new_scroll_fn = """  // Auto-scroll inner chat container smoothly without jumping page
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
  };"""

if old_scroll_fn in studio_content:
    studio_content = studio_content.replace(old_scroll_fn, new_scroll_fn)
    print("Replaced scrollToBottom in StudioStudio.tsx")

# Add data-lenis-prevent to outer chat card
old_outer_card = """      {/* WhatsApp / ChatGPT Preserved Chat Thread Box */}
      <div className="luxury-glass rounded-3xl p-5 sm:p-7 border border-[rgba(235,229,217,0.08)] shadow-[0_20px_50px_rgba(0,0,0,0.7)] space-y-4">"""

new_outer_card = """      {/* WhatsApp / ChatGPT Preserved Chat Thread Box */}
      <div data-lenis-prevent="true" className="luxury-glass rounded-3xl p-5 sm:p-7 border border-[rgba(235,229,217,0.08)] shadow-[0_20px_50px_rgba(0,0,0,0.7)] space-y-4">"""

if old_outer_card in studio_content:
    studio_content = studio_content.replace(old_outer_card, new_outer_card)
    print("Added data-lenis-prevent to outer chat card in StudioStudio.tsx")

# Update chatScrollRef div
old_chat_div = """        {/* Scrollable Preserved Message Thread Container (Empty on initial load) */}
        {(messages.length > 0 || loading) && (
          <div ref={chatScrollRef} className="max-h-[380px] overflow-y-auto space-y-3 pr-2 no-scrollbar">"""

new_chat_div = """        {/* Scrollable Preserved Message Thread Container (Empty on initial load) */}
        {(messages.length > 0 || loading) && (
          <div
            ref={chatScrollRef}
            data-lenis-prevent="true"
            data-lenis-prevent-wheel="true"
            data-lenis-prevent-touch="true"
            className="max-h-[420px] overflow-y-auto overscroll-contain space-y-3 pr-2 scrollbar-thin"
            style={{ overscrollBehavior: "contain" }}
            onWheel={(e) => {
              e.stopPropagation();
            }}
          >"""

if old_chat_div in studio_content:
    studio_content = studio_content.replace(old_chat_div, new_chat_div)
    print("Replaced chatScrollRef div with isolated scroll in StudioStudio.tsx")
else:
    print("Warning: old_chat_div not found in StudioStudio.tsx")

with open("frontend/src/components/StudioStudio.tsx", "w", encoding="utf-8") as f:
    f.write(studio_content)

# 3. Update frontend/src/components/AdvisorChat.tsx
with open("frontend/src/components/AdvisorChat.tsx", "r", encoding="utf-8") as f:
    advisor_content = f.read()

old_adv_feed = """      {/* Messages Feed */}
      <div className="flex-1 p-4 overflow-y-auto space-y-3">"""

new_adv_feed = """      {/* Messages Feed */}
      <div
        data-lenis-prevent="true"
        data-lenis-prevent-wheel="true"
        data-lenis-prevent-touch="true"
        className="flex-1 p-4 overflow-y-auto overscroll-contain space-y-3 scrollbar-thin"
        style={{ overscrollBehavior: "contain" }}
        onWheel={(e) => e.stopPropagation()}
      >"""

if old_adv_feed in advisor_content:
    advisor_content = advisor_content.replace(old_adv_feed, new_adv_feed)
    with open("frontend/src/components/AdvisorChat.tsx", "w", encoding="utf-8") as f:
        f.write(advisor_content)
    print("Updated AdvisorChat.tsx")

# 4. Update frontend/src/components/CPQCart.tsx
with open("frontend/src/components/CPQCart.tsx", "r", encoding="utf-8") as f:
    cpq_content = f.read()

old_cart_div1 = """              {/* Itemized SKUs */}
              <div className="divide-y divide-[rgba(235,229,217,0.04)] max-h-48 overflow-y-auto pr-1">"""

new_cart_div1 = """              {/* Itemized SKUs */}
              <div
                data-lenis-prevent="true"
                data-lenis-prevent-wheel="true"
                className="divide-y divide-[rgba(235,229,217,0.04)] max-h-48 overflow-y-auto overscroll-contain pr-1 scrollbar-thin"
                style={{ overscrollBehavior: "contain" }}
                onWheel={(e) => e.stopPropagation()}
              >"""

old_cart_div2 = """          <motion.div
            key="catalogue"
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
            className="space-y-3 max-h-[580px] overflow-y-auto pr-1"
          >"""

new_cart_div2 = """          <motion.div
            key="catalogue"
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
            data-lenis-prevent="true"
            data-lenis-prevent-wheel="true"
            className="space-y-3 max-h-[580px] overflow-y-auto overscroll-contain pr-1 scrollbar-thin"
            style={{ overscrollBehavior: "contain" }}
            onWheel={(e) => e.stopPropagation()}
          >"""

if old_cart_div1 in cpq_content:
    cpq_content = cpq_content.replace(old_cart_div1, new_cart_div1)
if old_cart_div2 in cpq_content:
    cpq_content = cpq_content.replace(old_cart_div2, new_cart_div2)

with open("frontend/src/components/CPQCart.tsx", "w", encoding="utf-8") as f:
    f.write(cpq_content)
print("Updated CPQCart.tsx")
