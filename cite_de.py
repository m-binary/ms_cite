import pyperclip
import time
import re

last_clipboard = ""

# Mapping für Experteninterviews: "Experteninterview NACHNAME" -> "citekey"
INTERVIEW_MAPPING = {
    "Experteninterview S": "keys2024",
    "Experteninterview N": "keyn2023",
    # Weitere Experteninterviews hier hinzufügen:
    # "Experteninterview NACHNAME": "citekey",
}

# Muster für einzelne Quelle im Format: Zitierschlüssel, S.xxff.
# Unterstützt: zhang2024, S.5 | zhang2024, S.5f. | zhang2024, S.5ff. | zhang2024, S.5-10 | zhang2024
# Auch: Experteninterview NACHNAME(/NACHNAME), S.xx
patterns = [
    (re.compile(r"^(.+?),\s*S\.(\d+)-(\d+)\.?$"), "range"),           # z.B. zhang2024, S.5-10
    (re.compile(r"^(.+?),\s*S\.(\d+)(ff?)\.?$"), "f-style"),          # z.B. zhang2024, S.5f. oder S.5ff.
    (re.compile(r"^(.+?),\s*S\.(\d+)\.?$"), "single"),                # z.B. zhang2024, S.5
    (re.compile(r"^(.+?)$"), "nopage"),                               # z.B. zhang2024 (ohne Seite)
]

print("📋 Watching clipboard... Press Ctrl+C to stop.")

def is_already_latex(text):
    """Prüft, ob der Text bereits eine LaTeX-Zitation ist (um Endlosschleifen zu vermeiden)."""
    return text.strip().startswith("\\cite")

def format_citation(bibkey, style, page1=None, page2=None, f_suffix=None):
    bibkey = bibkey.strip()
    # Mapping anwenden (z.B. für Experteninterviews)
    bibkey = INTERVIEW_MAPPING.get(bibkey, bibkey)
    
    if style == "single":
        return f"\\cite[S. {page1}]{{{bibkey}}}"
    elif style == "range":
        return f"\\cite[S. {page1}–{page2}]{{{bibkey}}}"
    elif style == "f-style":
        # Deutsche Konvention: "S. 5 f." oder "S. 5 ff." (mit Leerzeichen und Punkt)
        if f_suffix == "ff":
            return f"\\cite[S. {page1} ff.]{{{bibkey}}}"
        else:
            return f"\\cite[S. {page1} f.]{{{bibkey}}}"
    elif style == "nopage":
        return f"\\cite{{{bibkey}}}"
    return None


def parse_single_citation(text):
    """Parst eine einzelne Zitation und gibt das formatierte LaTeX zurück."""
    text = text.strip()
    for pattern, style in patterns:
        match = pattern.fullmatch(text)
        if match:
            if style == "range":
                bibkey, p1, p2 = match.groups()
                return format_citation(bibkey, style, p1, p2)
            elif style == "f-style":
                bibkey, p1, f_suffix = match.groups()
                return format_citation(bibkey, style, p1, f_suffix=f_suffix)
            elif style == "single":
                bibkey, p1 = match.groups()
                return format_citation(bibkey, style, p1)
            elif style == "nopage":
                bibkey = match.group(1)
                return format_citation(bibkey, style)
    return None

while True:
    try:
        clipboard = pyperclip.paste()
        if clipboard != last_clipboard:
            last_clipboard = clipboard.strip()
            
            # Eigene Ausgabe ignorieren (verhindert Endlosschleife)
            if is_already_latex(last_clipboard):
                continue
            
            # Mehrere Quellen durch Semikolon getrennt
            citations = [c.strip() for c in last_clipboard.split(";")]
            latex_parts = []
            failed_citations = []
            
            for citation in citations:
                if citation:  # Leere Einträge ignorieren
                    latex = parse_single_citation(citation)
                    if latex:
                        latex_parts.append(latex)
                    else:
                        failed_citations.append(citation)
            
            if failed_citations:
                error_msg = f"⚠️ Parsing fehlgeschlagen für: {'; '.join(failed_citations)}"
                pyperclip.copy(error_msg)
                print(f"❌ {error_msg}")
            elif latex_parts:
                result = " ".join(latex_parts)
                pyperclip.copy(result)
                print(f"✅ Converted: {result}")
                
        time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n👋 Stopped.")
        break
