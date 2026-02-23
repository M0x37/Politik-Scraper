# 🤖 Telegram Bot einrichten

## 1. Telegram Bot erstellen

### Bot Token erhalten:
1. Telegram öffnen → **@BotFather** suchen
2. `/start` senden
3. `/newbot` senden
4. Bot-Namen eingeben (z.B. "Politik News Bot")
5. Benutzername eingeben (z.B. `politik_news_bot`)
6. **Bot Token kopieren** (lange Zeichenfolge wie `1234567890:ABC...`)

### Chat ID erhalten:
1. Bot starten → Nachricht senden
2. Browser öffnen: `https://api.telegram.org/bot<DEIN_BOT_TOKEN>/getUpdates`
3. `chat.id` Wert kopieren (meistens eine Zahl)

## 2. GitHub Secrets einrichten

Gehe zu deinem GitHub Repository → Settings → Secrets and variables → Actions

Füge diese 2 Secrets hinzu:

### `TELEGRAM_BOT_TOKEN`
Dein Bot Token von BotFather

### `TELEGRAM_CHAT_ID`
Deine Chat ID (Zahl)

## 3. Bot testen

### Lokal testen:
```bash
# Umgebungsvariablen setzen
set TELEGRAM_BOT_TOKEN=dein_bot_token
set TELEGRAM_CHAT_ID=deine_chat_id

# Bot ausführen
cd src
python telegram_bot.py
```

### GitHub Actions testen:
1. Repository zu GitHub pushen
2. Actions → Daily News Scraper → "Run workflow"
3. Prüfen ob Nachricht in Telegram ankommt

## 4. Automatisierung

Nach erfolgreichem Test läuft der Bot automatisch täglich um 20:00 Berlin Zeit und sendet die 5 wichtigsten politischen Nachrichten.

## 5. Bot anpassen

### Nachricht format ändern:
In `src/telegram_bot.py` die `format_telegram_message()` Methode anpassen.

### Anzahl Nachrichten ändern:
```python
news = self.get_daily_news(10)  # Statt 5 Nachrichten
```

### Zeit ändern:
In `.github/workflows/daily-news.yml` den Cron-Job anpassen:
```yaml
schedule:
  - cron: '0 19 * * *'  # 20:00 Berlin Zeit
```

## 6. Fehlersuche

### Bot antwortet nicht:
- Bot Token korrekt?
- Chat ID korrekt?
- Bot gestartet (Nachricht gesendet)?

### Keine Nachrichten:
- Internetverbindung prüfen
- RSS-Feeds erreichbar?
- Logs in GitHub Actions ansehen

### Nachrichten format falsch:
- Markdown-Syntax prüfen
- Sonderzeichen escapen
