import os
import sys
import threading
import requests
import customtkinter as ctk
from bs4 import BeautifulSoup
from PIL import Image


# ========================
# BRANDING
# ========================

APP_NAME = "Webklar MiniCheck"

PRIMARY = "#22C55E"
PRIMARY_HOVER = "#16A34A"
DARK_BG = "#020617"
CARD_BG = "#0B1220"
INPUT_BG = "#111827"
BORDER = "#1F2937"
TEXT = "#F8FAFC"
MUTED = "#94A3B8"


def resource_path(relative_path):
    """Funktioniert sowohl in Python als auch in der .exe."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# ========================
# WEBSITE ANALYSE
# ========================

def fetch_website_data(url: str) -> dict:
    try:
        response = requests.get(
            url,
            timeout=12,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        response.raise_for_status()
    except Exception:
        return {"error": "Website konnte nicht geladen werden."}

    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.title.string.strip() if soup.title and soup.title.string else "Kein Title gefunden"

    meta_description = soup.find("meta", attrs={"name": "description"})
    meta_description = (
        meta_description["content"].strip()
        if meta_description and meta_description.get("content")
        else "Keine Meta Description gefunden"
    )

    h1_tags = [h.get_text(strip=True) for h in soup.find_all("h1")]
    h2_tags = [h.get_text(strip=True) for h in soup.find_all("h2")[:8]]

    text = soup.get_text(" ", strip=True)[:3500]

    return {
        "url": url,
        "title": title,
        "meta_description": meta_description,
        "h1_tags": h1_tags,
        "h2_tags": h2_tags,
        "text_excerpt": text
    }


def generate_mini_check(data: dict) -> str:
    if "error" in data:
        return data["error"]

    prompt = f"""
Du bist ein deutscher Website-Optimierungsberater für lokale Unternehmen, Handwerker und Dienstleister.

WICHTIG:
- Antworte ausschließlich auf Deutsch.
- Verwende keine englischen Formulierungen.
- Schreibe professionell, klar und freundlich.
- Nutze nur die gelieferten Website-Daten.
- Erfinde keine Fakten.
- Wenn etwas nicht erkennbar ist, schreibe: "Aus den ausgelesenen Daten nicht erkennbar."
- Keine übertriebenen Versprechen.
- Kein Fachjargon ohne kurze Erklärung.

Analysiere ausschließlich diese Daten:

URL: {data["url"]}
Title: {data["title"]}
Meta Description: {data["meta_description"]}
H1: {data["h1_tags"]}
H2: {data["h2_tags"]}
Textauszug: {data["text_excerpt"]}

Erstelle einen kostenlosen Mini-Check auf Deutsch.

Struktur:

1. Ersteinschätzung
Schreibe 2–3 kurze Sätze zur Website.

2. Positive Punkte
Nenne 2 konkrete positive Punkte.

3. Schwachstellen
Nenne 3 konkrete Schwachstellen.
Formuliere vorsichtig, wenn Informationen fehlen.

4. Verbesserungsvorschläge
Nenne 3 konkrete und einfach verständliche Vorschläge.

5. SEO-Einschätzung
Erkläre kurz, wie gut die Website aus den Daten heraus für Google wirkt.

6. Conversion-Einschätzung
Erkläre kurz, ob Besucher wahrscheinlich schnell verstehen, was sie tun sollen.

7. Kurze Outreach-E-Mail an den Website-Besitzer
Regeln für die E-Mail:
- komplett auf Deutsch
- freundlich und respektvoll
- maximal 120 Wörter
- nicht zu verkäuferisch
- kein "Ich hoffe, diese E-Mail erreicht Sie gut"
- keine erfundenen Behauptungen
- konkrete Beobachtung aus dem Mini-Check erwähnen

Gib den Mini-Check sauber formatiert mit Überschriften aus.
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2
                }
            },
            timeout=180
        )
        response.raise_for_status()
        return response.json().get("response", "Keine Antwort vom Modell erhalten.")
    except Exception:
        return "Fehler: Ollama läuft vermutlich nicht. Bitte zuerst 'ollama serve' starten."


# ========================
# UI
# ========================

class MiniCheckApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")

        self.title(APP_NAME)
        self.geometry("1050x760")
        self.minsize(950, 680)
        self.configure(fg_color=DARK_BG)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main = ctk.CTkFrame(
            self,
            fg_color=DARK_BG,
            corner_radius=0
        )
        self.main.grid(row=0, column=0, sticky="nsew", padx=28, pady=24)

        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(2, weight=1)

        self.build_header()
        self.build_input_card()
        self.build_result_card()

    def build_header(self):
        header = ctk.CTkFrame(self.main, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 22))
        header.grid_columnconfigure(1, weight=1)

        logo_path = resource_path("assets/logo.png")

        try:
            logo_image = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(82, 82)
            )

            logo = ctk.CTkLabel(header, image=logo_image, text="")
            logo.grid(row=0, column=0, padx=(0, 18))
        except Exception:
            logo = ctk.CTkLabel(
                header,
                text="W",
                width=82,
                height=82,
                fg_color=CARD_BG,
                corner_radius=22,
                text_color=PRIMARY,
                font=("Arial", 38, "bold")
            )
            logo.grid(row=0, column=0, padx=(0, 18))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.grid(row=0, column=1, sticky="w")

        title = ctk.CTkLabel(
            title_box,
            text="Webklar MiniCheck Agent",
            text_color=TEXT,
            font=("Arial", 30, "bold")
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            title_box,
            text="Schnelle Website-Ersteinschätzung für lokale Unternehmen",
            text_color=MUTED,
            font=("Arial", 15)
        )
        subtitle.pack(anchor="w", pady=(4, 0))

        badge = ctk.CTkLabel(
            header,
            text="Lokaler Website-Check",
            fg_color="#052E1A",
            text_color=PRIMARY,
            corner_radius=999,
            padx=16,
            pady=8,
            font=("Arial", 13, "bold")
        )
        badge.grid(row=0, column=2, sticky="e")

    def build_input_card(self):
        card = ctk.CTkFrame(
            self.main,
            fg_color=CARD_BG,
            corner_radius=24,
            border_width=1,
            border_color=BORDER
        )
        card.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        card.grid_columnconfigure(0, weight=1)

        label = ctk.CTkLabel(
            card,
            text="Website-URL einfügen",
            text_color=TEXT,
            font=("Arial", 18, "bold")
        )
        label.grid(row=0, column=0, sticky="w", padx=24, pady=(22, 6))

        hint = ctk.CTkLabel(
            card,
            text="Beispiel: https://www.handwerker-musterstadt.de",
            text_color=MUTED,
            font=("Arial", 13)
        )
        hint.grid(row=1, column=0, sticky="w", padx=24, pady=(0, 14))

        input_row = ctk.CTkFrame(card, fg_color="transparent")
        input_row.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 22))
        input_row.grid_columnconfigure(0, weight=1)

        self.url_entry = ctk.CTkEntry(
            input_row,
            height=48,
            corner_radius=14,
            fg_color=INPUT_BG,
            border_color=BORDER,
            border_width=1,
            text_color=TEXT,
            placeholder_text="Website-Link hier einfügen...",
            font=("Arial", 15)
        )
        self.url_entry.grid(row=0, column=0, sticky="ew", padx=(0, 14))

        self.start_button = ctk.CTkButton(
            input_row,
            text="Analyse starten",
            height=48,
            width=180,
            corner_radius=14,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            text_color="#02130A",
            font=("Arial", 15, "bold"),
            command=self.start_check
        )
        self.start_button.grid(row=0, column=1)

    def build_result_card(self):
        card = ctk.CTkFrame(
            self.main,
            fg_color=CARD_BG,
            corner_radius=24,
            border_width=1,
            border_color=BORDER
        )
        card.grid(row=2, column=0, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(2, weight=1)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 10))
        top.grid_columnconfigure(0, weight=1)

        result_title = ctk.CTkLabel(
            top,
            text="Ergebnis",
            text_color=TEXT,
            font=("Arial", 18, "bold")
        )
        result_title.grid(row=0, column=0, sticky="w")

        self.status = ctk.CTkLabel(
            top,
            text="Bereit",
            fg_color="#111827",
            text_color=MUTED,
            corner_radius=999,
            padx=14,
            pady=7,
            font=("Arial", 13)
        )
        self.status.grid(row=0, column=1, sticky="e")

        self.progress = ctk.CTkProgressBar(
            card,
            height=8,
            corner_radius=999,
            progress_color=PRIMARY
        )
        self.progress.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 14))
        self.progress.set(0)

        self.result_box = ctk.CTkTextbox(
            card,
            fg_color="#050A14",
            text_color=TEXT,
            corner_radius=18,
            border_width=1,
            border_color=BORDER,
            font=("Consolas", 14),
            wrap="word"
        )
        self.result_box.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 24))

        self.result_box.insert(
            "end",
            "Hier erscheint gleich dein Mini-Check.\n\n"
            "Tipp: Für die beste Analyse eine vollständige URL einfügen, z. B. https://beispiel.de"
        )

    def start_check(self):
        url = self.url_entry.get().strip()

        if not url:
            self.status.configure(text="URL fehlt", text_color="#FCA5A5")
            return

        if not url.startswith("http"):
            url = "https://" + url

        self.result_box.delete("1.0", "end")
        self.result_box.insert("end", "Website wird geladen...\n\nAnalyse startet gleich...")
        self.status.configure(text="Analyse läuft", text_color=PRIMARY)
        self.progress.set(0.25)
        self.start_button.configure(state="disabled", text="Bitte warten...")

        thread = threading.Thread(target=self.run_check, args=(url,), daemon=True)
        thread.start()

    def run_check(self, url):
        data = fetch_website_data(url)

        self.progress.set(0.55)
        self.result_box.delete("1.0", "end")
        self.result_box.insert(
            "end",
            "Website-Daten wurden ausgelesen.\n\nKI erstellt den Mini-Check..."
        )

        result = generate_mini_check(data)

        self.progress.set(1)
        self.result_box.delete("1.0", "end")
        self.result_box.insert("end", result)

        self.status.configure(text="Fertig", text_color=PRIMARY)
        self.start_button.configure(state="normal", text="Analyse starten")


if __name__ == "__main__":
    app = MiniCheckApp()
    app.mainloop()
