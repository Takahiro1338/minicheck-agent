import threading
import requests
import customtkinter as ctk
from bs4 import BeautifulSoup
from PIL import Image

# Branding Farben (aus deinem Logo)
PRIMARY = "#22C55E"     # Grün
DARK_BG = "#020617"     # Fast schwarz
CARD_BG = "#0F172A"
TEXT = "#E5E7EB"

# ------------------------
# WEBSITE ANALYSE
# ------------------------
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

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": str(data),
                "stream": False
            },
            timeout=120
        )
        response.raise_for_status()
        return response.json().get("response", "Keine Antwort erhalten.")
    except Exception:
        return "Fehler: Ollama läuft nicht. Starte 'ollama serve'."


# ------------------------
# UI
# ------------------------
class MiniCheckApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Webklar MiniCheck")
        self.geometry("900x700")
        self.configure(fg_color=DARK_BG)

        ctk.set_appearance_mode("dark")

        # LOGO LADEN
        logo_image = ctk.CTkImage(
            light_image=Image.open("assets/logo.png"),
            dark_image=Image.open("assets/logo.png"),
            size=(120, 120)
        )

        self.logo_label = ctk.CTkLabel(self, image=logo_image, text="")
        self.logo_label.pack(pady=(20, 10))

        # TITEL
        self.headline = ctk.CTkLabel(
            self,
            text="MiniCheck Agent",
            font=("Arial", 28, "bold"),
            text_color=TEXT
        )
        self.headline.pack(pady=(0, 5))

        # SUBTEXT
        self.subline = ctk.CTkLabel(
            self,
            text="Website analysieren & Optimierungspotenziale erkennen",
            font=("Arial", 14),
            text_color="#94A3B8"
        )
        self.subline.pack(pady=(0, 20))

        # INPUT
        self.url_entry = ctk.CTkEntry(
            self,
            width=600,
            height=40,
            placeholder_text="https://deine-website.de",
        )
        self.url_entry.pack(pady=10)

        # BUTTON
        self.start_button = ctk.CTkButton(
            self,
            text="Mini-Check starten",
            fg_color=PRIMARY,
            hover_color="#16A34A",
            width=200,
            height=40,
            command=self.start_check
        )
        self.start_button.pack(pady=10)

        # STATUS
        self.status = ctk.CTkLabel(
            self,
            text="Bereit",
            text_color="#64748B"
        )
        self.status.pack(pady=5)

        # RESULT BOX
        self.result_box = ctk.CTkTextbox(
            self,
            width=800,
            height=400,
            fg_color=CARD_BG,
            text_color=TEXT
        )
        self.result_box.pack(pady=20)

    def start_check(self):
        url = self.url_entry.get().strip()

        if not url:
            self.status.configure(text="Bitte URL eingeben")
            return

        if not url.startswith("http"):
            url = "https://" + url

        self.result_box.delete("1.0", "end")
        self.result_box.insert("end", "Analyse läuft...\n")

        self.status.configure(text="Analysiere Website...")
        self.start_button.configure(state="disabled")

        thread = threading.Thread(target=self.run_check, args=(url,))
        thread.start()

    def run_check(self, url):
        data = fetch_website_data(url)
        result = generate_mini_check(data)

        self.result_box.delete("1.0", "end")
        self.result_box.insert("end", result)

        self.status.configure(text="Fertig")
        self.start_button.configure(state="normal")


if __name__ == "__main__":
    app = MiniCheckApp()
    app.mainloop()
