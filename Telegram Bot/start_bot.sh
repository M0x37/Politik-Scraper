#!/bin/bash

echo "=== Telegram Politik Bot Starter ==="
echo

# Prüfen ob Python installiert ist
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 ist nicht installiert!"
    echo "Bitte installiere Python 3.11+:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  macOS: brew install python3"
    echo "  Oder von https://python.org"
    exit 1
fi

echo "✅ Python3 gefunden"

# Prüfen ob requirements.txt existiert
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt nicht gefunden!"
    echo "Stelle sicher dass alle Dateien im selben Ordner sind"
    exit 1
fi

# Abhängigkeiten installieren
echo "📦 Installiere Abhängigkeiten..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Fehler bei der Installation!"
    exit 1
fi

echo "✅ Abhängigkeiten installiert"

# Umgebungsvariablen prüfen
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo
    echo "🔧 Einrichtung erforderlich:"
    echo "1. Bot Token von @BotFather holen"
    echo "2. Chat ID ermitteln (siehe SETUP_TELEGRAM.md)"
    echo "3. Umgebungsvariablen setzen:"
    echo "   export TELEGRAM_BOT_TOKEN=dein_token"
    echo "   export TELEGRAM_CHAT_ID=deine_id"
    echo
    exit 1
fi

if [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo
    echo "❌ TELEGRAM_CHAT_ID nicht gesetzt!"
    echo "export TELEGRAM_CHAT_ID=deine_chat_id"
    exit 1
fi

echo "✅ Umgebungsvariablen gefunden"

# Bot starten
echo
echo "🤖 Starte Telegram Bot..."
echo

python3 telegram_bot.py

if [ $? -eq 0 ]; then
    echo
    echo "✅ Bot erfolgreich ausgeführt"
else
    echo
    echo "❌ Bot ist mit Fehler beendet"
fi
