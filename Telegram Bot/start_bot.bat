@echo off
echo === Telegram Politik Bot Starter ===
echo.

REM Prüfen ob Python installiert ist
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python ist nicht installiert!
    echo Bitte installiere Python 3.11+ von https://python.org
    pause
    exit /b 1
)

echo ✅ Python gefunden

REM Prüfen ob requirements.txt existiert
if not exist "requirements.txt" (
    echo ❌ requirements.txt nicht gefunden!
    echo Stelle sicher dass alle Dateien im selben Ordner sind
    pause
    exit /b 1
)

REM Abhängigkeiten installieren
echo 📦 Installiere Abhängigkeiten...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Fehler bei der Installation!
    pause
    exit /b 1
)

echo ✅ Abhängigkeiten installiert

REM Umgebungsvariablen prüfen
if "%TELEGRAM_BOT_TOKEN%"=="" (
    echo.
    echo 🔧 Einrichtung erforderlich:
    echo 1. Bot Token von @BotFather holen
    echo 2. Chat ID ermitteln (siehe SETUP_TELEGRAM.md)
    echo 3. Umgebungsvariablen setzen:
    echo    set TELEGRAM_BOT_TOKEN=dein_token
    echo    set TELEGRAM_CHAT_ID=deine_id
    echo.
    pause
    exit /b 1
)

if "%TELEGRAM_CHAT_ID%"=="" (
    echo.
    echo ❌ TELEGRAM_CHAT_ID nicht gesetzt!
    echo set TELEGRAM_CHAT_ID=deine_chat_id
    pause
    exit /b 1
)

echo ✅ Umgebungsvariablen gefunden

REM Bot starten
echo.
echo 🤖 Starte Telegram Bot...
echo.
python telegram_bot.py

if errorlevel 1 (
    echo.
    echo ❌ Bot ist mit Fehler beendet
    pause
) else (
    echo.
    echo ✅ Bot erfolgreich ausgeführt
)

pause
