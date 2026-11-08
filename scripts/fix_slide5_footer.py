with open("docs/presentation/build_winner_deck.py", "r", encoding="utf-8") as f:
    text = f.read()

# Make slide 5 cards fit cleanly with 250px fixed heights and compact padding
old_card1 = """          <!-- Screen 1: Multilingual Advisor -->
          <div class="card" style="padding: 12px 14px; display: flex; flex-direction: column; gap: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 13.5px; font-weight: 800; color: #121316;">1. Multilingual Natural Language Advisor</span>
              <span class="badge-pill">10 Indian Languages</span>
            </div>
            <div style="flex: 1; border: 1px solid #DDD8CE; border-radius: 6px; overflow: hidden; background: #000; display: flex; justify-content: center; align-items: center;">
              <img src="{img_screen_advisor_b64}" style="width: 100%; height: 100%; object-fit: cover;">
            </div>
            <div style="font-size: 11.5px; color: #5A5A5D; line-height: 1.35;">
              Shop owners chat or speak in Hindi, Tamil, Telugu, etc. The assistant understands business needs and explains bundle recommendations in plain language with voice audio.
            </div>
          </div>"""

new_card1 = """          <!-- Screen 1: Multilingual Advisor -->
          <div class="card" style="padding: 10px 12px; display: flex; flex-direction: column; gap: 6px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 13px; font-weight: 800; color: #121316;">1. Multilingual Natural Language Advisor</span>
              <span class="badge-pill">10 Indian Languages</span>
            </div>
            <div style="height: 250px; border: 1px solid #DDD8CE; border-radius: 6px; overflow: hidden; background: #000; display: flex; justify-content: center; align-items: center;">
              <img src="{img_screen_advisor_b64}" style="width: 100%; height: 100%; object-fit: cover;">
            </div>
            <div style="font-size: 11px; color: #5A5A5D; line-height: 1.3;">
              Shop owners chat or speak in Hindi, Tamil, Telugu, etc. The assistant understands business needs and explains bundle recommendations in plain language with voice audio.
            </div>
          </div>"""

old_card2 = """          <!-- Screen 2: Dynamic Cart & Reverse Budget -->
          <div class="card" style="padding: 12px 14px; display: flex; flex-direction: column; gap: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 13.5px; font-weight: 800; color: #121316;">2. Dynamic Cart & "Mera Budget" Slider</span>
              <span class="badge-pill">&lt;0.5ms Solver</span>
            </div>
            <div style="flex: 1; border: 1px solid #DDD8CE; border-radius: 6px; overflow: hidden; background: #000; display: flex; justify-content: center; align-items: center;">
              <img src="{img_screen_cart_b64}" style="width: 100%; height: 100%; object-fit: cover;">
            </div>
            <div style="font-size: 11.5px; color: #5A5A5D; line-height: 1.35;">
              Transparent monthly price breakdown. Moving the budget slider automatically recalculates the best compliant bundle in under 1ms, applying multi-category discounts.
            </div>
          </div>"""

new_card2 = """          <!-- Screen 2: Dynamic Cart & Reverse Budget -->
          <div class="card" style="padding: 10px 12px; display: flex; flex-direction: column; gap: 6px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 13px; font-weight: 800; color: #121316;">2. Dynamic Cart & "Mera Budget" Slider</span>
              <span class="badge-pill">&lt;0.5ms Solver</span>
            </div>
            <div style="height: 250px; border: 1px solid #DDD8CE; border-radius: 6px; overflow: hidden; background: #000; display: flex; justify-content: center; align-items: center;">
              <img src="{img_screen_cart_b64}" style="width: 100%; height: 100%; object-fit: cover;">
            </div>
            <div style="font-size: 11px; color: #5A5A5D; line-height: 1.3;">
              Transparent monthly price breakdown. Moving the budget slider automatically recalculates the best compliant bundle in under 1ms, applying multi-category discounts.
            </div>
          </div>"""

old_card3 = """          <!-- Screen 3: Zero-Persistence KYC Gate -->
          <div class="card" style="padding: 12px 14px; display: flex; flex-direction: column; gap: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 13.5px; font-weight: 800; color: #121316;">3. Fast & Safe KYC (Zero-Persistence DPDP)</span>
              <span class="badge-pill">Traps Planted Defects</span>
            </div>
            <div style="flex: 1; border: 1px solid #DDD8CE; border-radius: 6px; overflow: hidden; background: #000; display: flex; justify-content: center; align-items: center;">
              <img src="{img_screen_kyc_b64}" style="width: 100%; height: 100%; object-fit: cover;">
            </div>
            <div style="font-size: 11.5px; color: #5A5A5D; line-height: 1.35;">
              Upload certificates and bills. Instant verification of GSTIN/Udyam registries under 200ms. In-memory masking ensures 12-digit national IDs never touch storage.
            </div>
          </div>"""

new_card3 = """          <!-- Screen 3: Zero-Persistence KYC Gate -->
          <div class="card" style="padding: 10px 12px; display: flex; flex-direction: column; gap: 6px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 13px; font-weight: 800; color: #121316;">3. Fast & Safe KYC (Zero-Persistence DPDP)</span>
              <span class="badge-pill">Traps Planted Defects</span>
            </div>
            <div style="height: 250px; border: 1px solid #DDD8CE; border-radius: 6px; overflow: hidden; background: #000; display: flex; justify-content: center; align-items: center;">
              <img src="{img_screen_kyc_b64}" style="width: 100%; height: 100%; object-fit: cover;">
            </div>
            <div style="font-size: 11px; color: #5A5A5D; line-height: 1.3;">
              Upload certificates and bills. Instant verification of GSTIN/Udyam registries under 200ms. In-memory masking ensures 12-digit national IDs never touch storage.
            </div>
          </div>"""

# Card 4
old_card4_box = """            <!-- Live Provisioning Flow Tracker Simulation -->
            <div style="flex: 1; border: 1px solid #DDD8CE; border-radius: 6px; overflow: hidden; background: #0B0C0E; padding: 14px 16px; display: flex; flex-direction: column; justify-content: space-between;">"""

new_card4_box = """            <!-- Live Provisioning Flow Tracker Simulation -->
            <div style="height: 250px; border: 1px solid #DDD8CE; border-radius: 6px; overflow: hidden; background: #0B0C0E; padding: 10px 12px; display: flex; flex-direction: column; justify-content: space-between;">"""

old_card4_div = """          <!-- Screen 4: Real-Time Tracker & Lead Rescue -->
          <div class="card" style="padding: 12px 14px; display: flex; flex-direction: column; gap: 8px;">"""

new_card4_div = """          <!-- Screen 4: Real-Time Tracker & Lead Rescue -->
          <div class="card" style="padding: 10px 12px; display: flex; flex-direction: column; gap: 6px;">"""

old_card4_caption = """            <div style="font-size: 11.5px; color: #5A5A5D; line-height: 1.35;">
              Self-serve view shows progress from payment to technician dispatch with OTP. If a user pauses, an automated WhatsApp rescue message with a token brings them back.
            </div>"""

new_card4_caption = """            <div style="font-size: 11px; color: #5A5A5D; line-height: 1.3;">
              Self-serve view shows progress from payment to technician dispatch with OTP. If a user pauses, an automated WhatsApp rescue message with a token brings them back.
            </div>"""

for old_s, new_s in [
    (old_card1, new_card1),
    (old_card2, new_card2),
    (old_card3, new_card3),
    (old_card4_div, new_card4_div),
    (old_card4_box, new_card4_box),
    (old_card4_caption, new_card4_caption),
]:
    if old_s in text:
        text = text.replace(old_s, new_s, 1)

with open("docs/presentation/build_winner_deck.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Updated Slide 5 cards sizing.")
