import threading
import requests
import customtkinter as ctk
from bs4 import BeautifulSoup


BRAND_COLOR = "#2563EB"      # Blau
DARK_BG = "#0F172A"          # Dunkles Navy
CARD_BG = "#1E293B"
TEXT_COLOR = "#F8FAFC"


def fetch_website_data(url: str) -> dict:
    try:
        response = requests.get(
            url,
            timeout=10,
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
    text = soup.get_text(" ", strip=True)[:3000]

    return {
        "url": url,
        "title": title,
        "meta_description": meta_description,
        "h1_tags": h1_tags,
        "text_excerpt": text
    }


def generate_mini_check(data: dict) -> str:
    if "error" in data:
        return data["error"]

    prompt = f"""
Du bist Website-Optimierungsberater für kleine und lokale Unternehmen.

Wichtig:
- Erfinde keine Fakten.
- Nutze nur die gelieferten Website-Daten.
- Wenn Informationen fehlen, schreibe klar: "Aus den ausgelesenen Daten nicht erkennbar".
- Schreibe konkret, aber vorsichtig.
- Keine übertriebenen Versprechen.

Analysiere diese Website:

URL: {data["url"]}
Title: {data["title"]}
Meta Description: {data["meta_description"]}
H1: {data["h1_tags"]}
Textauszug: {data["text_excerpt"]}

Erstelle einen kostenlosen Mini-Check.

Struktur:
1. Kurze Ersteinschätzung
2. 2 positive Punkte
3. 3 konkrete Schwachstellen
4. 3 konkrete Verbesserungsvorschläge
5. Kurze SEO- und Conversion-Einschätzung
6. Fertige Outreach-E-Mail an den Website-Besitzer

Für die Outreach-E-Mail:
- Wir sind eine externe Website-Optimierungs-Agentur
- freundlich und respektvoll
- nicht zu verkäuferisch
- maximal 120 Wörter
- keine Behauptungen, die nicht aus den Daten hervorgehen
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        response.raise_for_status()
        return response.json().get("response", "Keine Antwort vom Modell erhalten.")
    except Exception:
        return "Fehler: Ollama läuft vermutlich nicht. Bitte zuerst 'ollama serve' starten."


class MiniCheckApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MiniCheck Agent")
        self.geometry("900x650")
        self.configure(fg_color=DARK_BG)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.headline = ctk.CTkLabel(
            self,
            text="MiniCheck Agent",
            font=("Arial", 30, "bold"),
            text_color=TEXT_COLOR
        )
        self.headline.pack(pady=(25, 5))

        self.subline = ctk.CTkLabel(
            self,
            text="Website-Link einfügen und kostenlosen Mini-Check erstellen",
            font=("Arial", 15),
            text_color="#CBD5E1"
        )
        self.subline.pack(pady=(0, 20))

        self.url_entry = ctk.CTkEntry(
            self,
            width=650,
            height=42,
            placeholder_text="z. B. https://beispiel.de",
            font=("Arial", 14)
        )
        self.url_entry.pack(pady=10)

        self.start_button = ctk.CTkButton(
            self,
            text="Mini-Check starten",
            width=220,
            height=42,
            fg_color=BRAND_COLOR,
            hover_color="#1D4ED8",
            command=self.start_check
        )
        self.start_button.pack(pady=12)

        self.status_label = ctk.CTkLabel(
            self,
            text="Bereit.",
            font=("Arial", 13),
            text_color="#94A3B8"
        )
        self.status_label.pack(pady=(0, 10))

        self.result_box = ctk.CTkTextbox(
            self,
            width=820,
            height=400,
            fg_color=CARD_BG,
            text_color=TEXT_COLOR,
            font=("Arial", 14),
            wrap="word"
        )
        self.result_box.pack(pady=10)

    def start_check(self):
        url = self.url_entry.get().strip()

        if not url:
            self.status_label.configure(text="Bitte eine Website-URL eingeben.")
            return

        if not url.startswith("http"):
            url = "https://" + url

        self.result_box.delete("1.0", "end")
        self.result_box.insert("end", "Mini-Check wird erstellt...\n")
        self.status_label.configure(text="Analyse läuft...")
        self.start_button.configure(state="disabled")

        thread = threading.Thread(target=self.run_check, args=(url,))
        thread.start()

    def run_check(self, url):
        data = fetch_website_data(url)
        result = generate_mini_check(data)

        self.result_box.delete("1.0", "end")
        self.result_box.insert("end", result)

        self.status_label.configure(text="Mini-Check abgeschlossen.")
        self.start_button.configure(state="normal")


if __name__ == "__main__":
    app = MiniCheckApp()
    app.mainloop()
