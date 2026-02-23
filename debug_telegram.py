#!/usr/bin/env python3
"""
Debug-Skript für Telegram Bot
"""

import os
import json
from datetime import datetime

def test_telegram_connection():
    """Testet die Telegram Verbindung"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    print(f"Bot Token vorhanden: {'Ja' if bot_token else 'Nein'}")
    print(f"Chat ID vorhanden: {'Ja' if chat_id else 'Nein'}")
    
    if bot_token:
        print(f"Bot Token Länge: {len(bot_token)}")
        print(f"Bot Token Start: {bot_token[:10]}...")
    
    if chat_id:
        print(f"Chat ID: {chat_id}")
    
    # Testnachricht senden
    if bot_token and chat_id:
        try:
            import telegram
            from telegram import Bot
            
            bot = Bot(token=bot_token)
            
            # Einfache Testnachricht
            test_message = f"🧪 Testnachricht vom {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            
            result = bot.send_message(
                chat_id=chat_id,
                text=test_message
            )
            
            print("✅ Testnachricht erfolgreich gesendet!")
            print(f"Message ID: {result.message_id}")
            
        except Exception as e:
            print(f"❌ Fehler beim Senden: {e}")
            print(f"Fehler-Typ: {type(e).__name__}")
            
            # Häufige Fehler analysieren
            error_str = str(e).lower()
            if "chat not found" in error_str:
                print("💡 Tipp: Chat ID ist falsch oder Bot wurde nicht gestartet")
            elif "unauthorized" in error_str or "forbidden" in error_str:
                print("💡 Tipp: Bot Token ist falsch oder Bot wurde blockiert")
            elif "bad request" in error_str:
                print("💡 Tipp: Nachrichtformat oder Token-Format falsch")

if __name__ == "__main__":
    test_telegram_connection()
