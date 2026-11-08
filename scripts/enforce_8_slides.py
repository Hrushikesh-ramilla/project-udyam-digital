with open("docs/presentation/build_winner_deck.py", "r", encoding="utf-8") as f:
    code = f.read()

# We want generate_slides_html to stop after slides.append(s7)
target_end = """        <span class="slide-number">Slide 7 of 7</span>
      </div>
    </div>
    \"\"\"
    slides.append(s7)"""

replacement_end = """        <span class="slide-number">Slide 7 of 7</span>
      </div>
    </div>
    \"\"\"
    slides.append(s7)

    # Strictly 7 evaluated slides + 1 intro slide = exactly 8 slides total (zero annexures)
    return slides"""

if target_end in code:
    # Cut off everything from target_end to def main():
    main_idx = code.find("def main():")
    code = code[:code.find(target_end)] + replacement_end + "\n\n" + code[main_idx:]
    print("Truncated slides to exactly 8 slides in generate_slides_html()")
else:
    print("Could not find target_end in build_winner_deck.py")

# Also update print in main() and add auto-sync for underscore naming
code = code.replace(
    'print(f"Total Slides Generated: {len(slides)} (Slide 0 Intro + 7 Evaluated Slides + 3 Annexures)")',
    'print(f"Total Slides Generated: {len(slides)} (Slide 0 Intro + 7 Evaluated Slides = Exactly 8 Slides Total)")'
)

# Add copying underscore files in main()
old_completion = """    print(f"2. PPT: {OFFICIAL_PPTX} ({os.path.getsize(OFFICIAL_PPTX) / (1024*1024):.2f} MB)")"""

new_completion = """    print(f"2. PPT: {OFFICIAL_PPTX} ({os.path.getsize(OFFICIAL_PPTX) / (1024*1024):.2f} MB)")

    # Mirror to underscore filename convention
    und_pdf = "Neural_Nexus_ABV_IIITM_Gwalior.pdf"
    und_pptx = "Neural_Nexus_ABV_IIITM_Gwalior.pptx"
    shutil.copy2(OFFICIAL_PDF, und_pdf)
    shutil.copy2(OFFICIAL_PPTX, und_pptx)
    print(f"  -> Mirrored to {und_pdf} and {und_pptx}")"""

code = code.replace(old_completion, new_completion, 1)

with open("docs/presentation/build_winner_deck.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated build_winner_deck.py successfully.")
