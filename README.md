# Website Mini Check Agent

## 🚀 Was ist das?

Ein einfacher AI-Agent, der Websites von lokalen Unternehmen analysiert und automatisch:

- einen Mini-Check erstellt
- Schwachstellen erkennt
- Verbesserungsvorschläge gibt
- eine fertige Kunden-Mail generiert

---

## 🎯 Ziel

Mehr Kunden für Website-Optimierung gewinnen durch automatisierte Erstanalysen.

---

## ⚙️ Setup

```bash
git clone https://github.com/Takahiro1338/minicheck-agent.git
cd minicheck-agent
pip install -r requirements.txt
```

---

## 🧠 Ollama Setup

Dieses Projekt nutzt **kein OpenAI**, sondern läuft lokal über Ollama.

### 1. Ollama installieren

Download: https://ollama.com

### 2. Modell herunterladen

```bash
ollama pull llama3
```

### 3. Ollama starten

```bash
ollama serve
```

---

## ▶️ Start

```bash
python src/main.py
```

Dann Website eingeben:

```bash
Website eingeben: example.com
```

---

## 📦 Output

Der Agent erstellt automatisch:

- Mini-Check
- SEO-Einschätzung
- Verbesserungsvorschläge
- fertige Outreach-Mail
- Speicherung als `.txt` Datei

Beispiel:

```txt
mini_check_example_com.txt
```

---

## ⚠️ Fehlerbehebung

Falls ein Fehler auftritt:

### Ollama läuft nicht

```bash
ollama serve
```

### Modell fehlt

```bash
ollama pull llama3
```

---

## 📁 Projektstruktur

```txt
minicheck-agent/
├── src/
│   └── main.py
├── requirements.txt
└── README.md
```

---

## 🧠 Roadmap

- [ ] Screenshot Integration
- [ ] Mobile Analyse
- [ ] PDF Export
- [ ] Lead Scraper
- [ ] CRM Integration

---

## 👥 Team

Jerry, Edwin, David, Ivan
