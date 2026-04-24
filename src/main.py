import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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
Du bist Experte für Website-Optimierung für lokale Unternehmen.

Analysiere diese Website:

URL: {data["url"]}
Title: {data["title"]}
Meta Description: {data["meta_description"]}
H1: {data["h1_tags"]}
Text: {data["text_excerpt"]}

Erstelle:
- 2 positive Punkte
- 3 Schwächen
- 3 Verbesserungen
- kurze SEO Einschätzung
- fertige E-Mail an den Kunden

Wichtig:
- verständlich
- nicht zu technisch
- freundlich formuliert
"""

    response = client.responses.create(
        model="gpt-5.5",
        input=prompt
    )

    return response.output_text


if __name__ == "__main__":
    url = input("Website eingeben: ")

    if not url.startswith("http"):
        url = "https://" + url

    data = fetch_website_data(url)
    result = generate_mini_check(data)

    print("\n--- MINI CHECK ---\n")
    print(result)
