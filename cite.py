import pyperclip
import time
import re

last_clipboard = ""

# Muster: Seitenbereich, f/ff, einzelne Seite, oder nur BibKey
patterns = [
    (re.compile(r"^([a-zA-Z]+\w*),?\s+p\.?\s*(\d+)-(\d+)$", re.IGNORECASE), "range"),      # z. B. zhang2024 p. 5-7
    (re.compile(r"^([a-zA-Z]+\w*),?\s+p\.?\s*(\d+)f{1,2}\.?$", re.IGNORECASE), "f-style"), # z. B. zhang2024 p. 5f / 5ff
    (re.compile(r"^([a-zA-Z]+\w*),?\s+p{0,2}\.?\s*(\d+)$", re.IGNORECASE), "single"),      # z. B. zhang2024 p. 5
    (re.compile(r"^([a-zA-Z]+\w*),?$", re.IGNORECASE), "nopage"),                         # z. B. zhang2024
]

print("📋 Watching clipboard... Press Ctrl+C to stop.")

def format_citation(bibkey, style, page1=None, page2=None):
    if style == "single":
        return f"\\cite[S. {page1}]{{{bibkey}}}"
    elif style == "range":
        return f"\\cite[S. {page1}–{page2}]{{{bibkey}}}"
    elif style == "f-style":
        page1 = int(page1)
        page2 = page1 + (1 if 'f' in last_clipboard.lower() and 'ff' not in last_clipboard.lower() else 2)
        return f"\\cite[S. {page1}f]{{{bibkey}}}"
    elif style == "nopage":
        return f"\\cite{{{bibkey}}}"
    return None

while True:
    try:
        clipboard = pyperclip.paste()
        if clipboard != last_clipboard:
            last_clipboard = clipboard.strip()
            for pattern, style in patterns:
                match = pattern.fullmatch(last_clipboard)
                if match:
                    if style == "range":
                        bibkey, p1, p2 = match.groups()
                        latex = format_citation(bibkey, style, p1, p2)
                    elif style == "single" or style == "f-style":
                        bibkey, p1 = match.groups()
                        latex = format_citation(bibkey, style, p1)
                    elif style == "nopage":
                        bibkey = match.group(1)
                        latex = format_citation(bibkey, style)
                    if latex:
                        pyperclip.copy(latex)
                        print(f"✅ Converted: {latex}")
                        break
        time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n👋 Stopped.")
        break
