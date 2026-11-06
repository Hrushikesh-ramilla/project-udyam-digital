# Unicode block bases for 8 Indic scripts
SCRIPT_BASES = {
    "devanagari": 0x0900,
    "bengali": 0x0980,
    "gujarati": 0x0A80,
    "odia": 0x0B00,
    "tamil": 0x0B80,
    "telugu": 0x0C00,
    "kannada": 0x0C80,
    "malayalam": 0x0D00,
}

# Common Brahmic offset mapping to Latin phonetic representations
INDEPENDENT_VOWELS = {
    0x04: "a", 0x05: "a", 0x06: "aa", 0x07: "i", 0x08: "ii", 0x09: "u", 0x0A: "uu",
    0x0B: "ri", 0x0C: "li", 0x0E: "e", 0x0F: "ee", 0x10: "ai", 0x12: "o", 0x13: "oo", 0x14: "au"
}

CONSONANTS = {
    0x15: "k", 0x16: "kh", 0x17: "g", 0x18: "gh", 0x19: "ng",
    0x1A: "ch", 0x1B: "chh", 0x1C: "j", 0x1D: "jh", 0x1E: "ny",
    0x1F: "t", 0x20: "th", 0x21: "d", 0x22: "dh", 0x23: "n",
    0x24: "t", 0x25: "th", 0x26: "d", 0x27: "dh", 0x28: "n", 0x29: "nn",
    0x2A: "p", 0x2B: "ph", 0x2C: "b", 0x2D: "bh", 0x2E: "m",
    0x2F: "y", 0x30: "r", 0x31: "rr", 0x32: "l", 0x33: "ll", 0x34: "lll",
    0x35: "v", 0x36: "sh", 0x37: "sh", 0x38: "s", 0x39: "h",
    0x58: "q", 0x59: "kh", 0x5A: "gh", 0x5B: "z", 0x5C: "r", 0x5D: "rh", 0x5E: "f"
}

VOWEL_SIGNS = {
    0x3E: "aa", 0x3F: "i", 0x40: "ii", 0x41: "u", 0x42: "uu", 0x43: "ri",
    0x46: "e", 0x47: "ee", 0x48: "ai", 0x4A: "o", 0x4B: "oo", 0x4C: "au"
}

VIRAMA_OFFSET = 0x4D
ANUSVARA_OFFSET = 0x02
VISARGA_OFFSET = 0x03
NUKTA_OFFSET = 0x3C

def indic_char_info(ch: str):
    cp = ord(ch)
    for name, base in SCRIPT_BASES.items():
        if base <= cp <= base + 0x7F:
            return name, cp - base
    return None, None

def indic_to_latin(text: str) -> str:
    """Translates/transliterates any Indic script text to Latin phonetic English words."""
    result = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        script, offset = indic_char_info(ch)
        if not script:
            result.append(ch)
            i += 1
            continue

        if offset in INDEPENDENT_VOWELS:
            result.append(INDEPENDENT_VOWELS[offset])
            i += 1
            continue

        if offset in CONSONANTS:
            cons = CONSONANTS[offset]
            # Check next character for virama, vowel sign, or nukta
            next_ch = text[i + 1] if i + 1 < n else ""
            next_script, next_offset = indic_char_info(next_ch) if next_ch else (None, None)

            if next_script == script and next_offset == VIRAMA_OFFSET:
                result.append(cons)
                i += 2
                continue
            elif next_script == script and next_offset in VOWEL_SIGNS:
                result.append(cons + VOWEL_SIGNS[next_offset])
                i += 2
                continue
            elif next_script == script and next_offset == ANUSVARA_OFFSET:
                result.append(cons + "am")
                i += 2
                continue
            else:
                # Inherent vowel
                # Tamil/Malayalam/Kannada/Telugu word-final consonant or standard 'a'
                result.append(cons + "a")
                i += 1
                continue

        if offset in VOWEL_SIGNS:
            result.append(VOWEL_SIGNS[offset])
            i += 1
            continue

        if offset == ANUSVARA_OFFSET:
            result.append("m")
            i += 1
            continue

        if offset == VIRAMA_OFFSET:
            i += 1
            continue

        # Default fallback
        i += 1

    s = "".join(result)
    # Clean up excessive duplicate vowels from inherent + matra combinations
    import re
    s = re.sub(r"a(aa|ee|oo|ai|au)", r"\1", s)
    return s

# Test cases
telugu_samples = [
    "నమస్కారం",
    "బాగున్నారా",
    "ఎలా ఉన్నారు",
    "హైదరాబాద్‌లో క్లినిక్ ఉంది",
    "మీ వ్యాపారానికి కనెక్టివిటీ కావాలా"
]

for s in telugu_samples:
    print(s, "->", indic_to_latin(s))
