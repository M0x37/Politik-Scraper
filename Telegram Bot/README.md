# 🤖 Telegram Politik Bot

Automatischer Telegram Bot, der täglich um 20:00 Berliner Zeit die 5 wichtigsten politischen Nachrichten sendet.

## 📁 Dateien in diesem Ordner:

- **`telegram_bot.py`** - Haupt-Skript für den Bot
- **`requirements.txt`** - Benötigte Python-Pakete
- **`SETUP_TELEGRAM.md`** - Detaillierte Einrichtungsanleitung

## 🚀 Schnellstart:

### 1. Python installieren
```bash
# Python 3.11+ wird empfohlen
python --version
```

### 2. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

### 3. Bot einrichten
Folge der Anleitung in `SETUP_TELEGRAM.md`:
- Bot Token von @BotFather holen
- Chat ID ermitteln
- Umgebungsvariablen setzen

### 4. Bot ausführen
```bash
# Umgebungsvariablen setzen
set TELEGRAM_BOT_TOKEN=dein_bot_token
set TELEGRAM_CHAT_ID=deine_chat_id

# Bot starten
python telegram_bot.py
```

## 📱 Bot Features:

- ✅ **Tägliche politische Nachrichten** (5 Stück)
- ✅ **Offizielle Quellen** (Tagesschau, n-tv, ZDF, DW, ARD)
- ✅ **Politik-Filter** (nur relevante politische Themen)
- ✅ **Duplikat-Entfernung** (keine doppelten Meldungen)
- ✅ **Kompakte Formatierung** (Überschrift + 1 Satz)
- ✅ **JSON-Export** (für Archivierung)

## ⏰ Automatisierung:

Für tägliche Ausführung um 20:00 Uhr:
- **GitHub Actions**: Automatischer Workflow
- **Cron Job**: Lokaler Scheduler
- **Systemd Service**: Linux-Dienst

## 🔧 Anpassungen:

### Anzahl Nachrichten ändern:
```python
# In telegram_bot.py Zeile ~262
news = self.get_daily_news(10)  # Statt 5
```

### Quellen anpassen:
```python
# In telegram_bot.py Zeile ~22
self.news_sources = [
    # Eigene Quellen hier einfügen
]
```

### Zeit ändern:
```yaml
# In .github/workflows/daily-news.yml
schedule:
  - cron: '0 19 * * *'  # 20:00 Berlin Zeit
```

## 📋 Benötigte Dateien:

1. **telegram_bot.py** - Haupt-Skript ✅
2. **requirements.txt** - Paketliste ✅
3. **SETUP_TELEGRAM.md** - Anleitung ✅

**Alles was du für den Betrieb brauchst ist in diesem Ordner!** 🎉
