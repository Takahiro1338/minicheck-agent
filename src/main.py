import requests
from bs4 import BeautifulSoup


def fetch_website_data(url: str) -> dict:
    try:
        response = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0"
        })
    except:
        return {"error": "Website konnte nicht geladen werden"}

    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.title.string.strip() if soup.title else "Kein Title gefunden"

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
        return "Fehler beim Laden der Website."

    prompt = f"""
Du bist Experte für Website-Optimierung für lokale Unternehmen in Deutschland.

Analysiere diese Website:

URL: {data["url"]}
Title: {data["title"]}
Meta Description: {data["meta_description"]}
H1: {data["h1_tags"]}
Text: {data["text_excerpt"]}

Erstelle einen Mini-Check für unsere Agentur.

WICHTIG:
- Schreibe ALLES auf Deutsch
- Einfach und verständlich
- Keine Fachbegriffe ohne Erklärung
- Kurz und prägnant

Struktur:

1. Kurze Ersteinschätzung (max 2 Sätze)
2. 2 positive Punkte
3. 3 konkrete Schwachstellen
4. 3 konkrete Verbesserungsvorschläge
5. Kurze SEO- und Conversion-Einschätzung (max 2 Sätze)

6. Outreach-E-Mail:
- max 80 Wörter
- locker & freundlich
- KEIN Agentur-Blabla
- Ziel: Interesse wecken
- Call-to-Action: kostenloser Mini-Check anbieten
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    return response.json()["response"]

    
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    return response.json()["response"]

if __name__ == "__main__":
    url = input("Website eingeben: ")

    if not url.startswith("http"):
        url = "https://" + url

    data = fetch_website_data(url)
    result = generate_mini_check(data)

    print("\n--- MINI CHECK ---\n")
    print(result)

    filename = data["url"].replace("https://", "").replace("http://", "")
    filename = filename.replace("/", "_").replace(".", "_")
    filename = f"mini_check_{filename}.txt"

    with open(filename, "w", encoding="utf-8") as file:
        file.write(result)

    print(f"\n✅ Mini-Check gespeichert als: {filename}")
