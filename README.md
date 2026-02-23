# Politik Scraper - Tägliche Politische Nachrichten

Automatisierter News-Scraper, der täglich um 20:00 Berliner Zeit die 5 wichtigsten **politischen** Nachrichten des Tages sammelt und formatiert.

## Features

- 🕐 **Tägliche Ausführung**: Läuft automatisch jeden Tag um 20:00 Berliner Zeit
- 📰 **5 Top-Politiknachrichten**: Sammlet ausschließlich politische Nachrichten
- 📝 **Kompakte Formatierung**: Jede Nachricht mit Überschrift und einem Satz
- 🔄 **Offizielle Quellen**: Tagesschau, n-tv, ZDF, Deutsche Welle, ARD
- 🚫 **Duplikat-Filter**: Entfernt doppelte Meldungen
- 🎯 **Politik-Filter**: Filtert automatisch nicht-politische Inhalte heraus
- 📊 **JSON-Export**: Speichert Nachrichten als JSON-Datei

## Quellen

**Offizielle politische Nachrichtenquellen:**
- **Tagesschau Politik**: `https://www.tagesschau.de/xml/rss2/` (mit Politik-Filter)
- **n-tv Politik**: `https://n-tv.de/rss/ressort/politik.rss`
- **ZDF Politik**: `https://www.zdf.de/rss/zdf/nachrichten/politik/rss-90-1.xml`
- **Deutsche Welle Politik**: `https://rss.dw.com/xml/rss-de-politik`
- **ARD Politik**: `https://www.tagesschau.de/xml/rss2/` (mit Politik-Filter)

## GitHub Actions Workflow

Der Workflow ist unter `.github/workflows/daily-news.yml` konfiguriert und:

- Läuft täglich um 19:00 UTC (20:00 Berliner Zeit)
- Kann manuell gestartet werden
- Speichert Ergebnisse als Artefakte für 30 Tage
- Erstellt eine Zusammenfassung im GitHub Actions Log

## Lokale Ausführung

### Voraussetzungen

- Python 3.11+
- pip

### Installation

```bash
# Abhängigkeiten installieren
pip install -r requirements.txt
```

### Ausführen

```bash
cd src
python news_scraper.py
```

## Ausgabeformat

Die Ausgabe enthält:

1. **Überschrift** der Nachricht
2. **Ein Satz** als Zusammenfassung
3. **Quellenangabe**

Beispiel:
```
📰 **Tagesnachrichten vom 23.02.2026**

**1. Neue Klimaschutzmaßnahmen beschlossen**
Die Bundesregierung hat heute ein neues Paket zur Reduzierung von CO2-Emissionen verabschiedet.
📍 Quelle: Tagesschau

**2. Wirtschaftswachstum im ersten Quartal stärker als erwartet**
Das deutsche Wirtschaftswachstum übertrifft die Prognosen der Experten deutlich.
📍 Quelle: Spiegel Online
```

## Dateistruktur

```
.
├── .github/
│   └── workflows/
│       └── daily-news.yml    # GitHub Actions Workflow
├── src/
│   └── news_scraper.py      # Haupt-Skript
├── requirements.txt         # Python-Abhängigkeiten
└── README.md               # Diese Datei
```

## Anpassungen

### Neue Nachrichtenquellen hinzufügen

Füge neue Quellen in `src/news_scraper.py` in der `news_sources` Liste hinzu:

```python
{
    'name': 'Neue Quelle',
    'url': 'https://beispiel.com/rss.xml',
    'language': 'de'
}
```

### Anzahl der Nachrichten ändern

Passe den `limit` Parameter in der `get_daily_news()` Methode:

```python
news = scraper.get_daily_news(10)  # Statt 5 Nachrichten
```

### Zeitzone anpassen

Ändere den Cron-Job in `.github/workflows/daily-news.yml`:

```yaml
schedule:
  - cron: '0 19 * * *'  # 19:00 UTC = 20:00 Berlin (Sommerzeit)
  - cron: '0 20 * * *'  # 20:00 UTC = 21:00 Berlin (Sommerzeit)
```

## Fehlerbehandlung

Der Scraper enthält umfassende Fehlerbehandlung:

- **Netzwerkfehler**: Timeout-Wiederholungen
- **Parse-Fehler**: Fallback auf alternative Methoden
- **Datenverarbeitung**: Überspringt fehlerhafte Einträge
- **Logging**: Detaillierte Logs zur Fehlersuche

## Lizenz

MIT License
