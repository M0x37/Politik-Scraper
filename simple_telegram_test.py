#!/usr/bin/env python3
"""
Einfacher Telegram Test
"""

import os
import requests
from datetime import datetime

def send_simple_message():
    """Sendet eine einfache Nachricht über Telegram Bot API"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    print(f"Token: {'✅' if bot_token else '❌'}")
    print(f"Chat ID: {'✅' if chat_id else '❌'}")
    
    if not bot_token or not chat_id:
        print("❌ Missing credentials")
        return False
    
    # Direkte API-Anfrage statt Bibliothek
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    message = f"📰 Testnachricht vom {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(url, json=data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Nachricht erfolgreich gesendet!")
                return True
            else:
                print(f"❌ API Error: {result.get('description', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    success = send_simple_message()
    
    # JSON für Artifact erstellen
    import json
    result_data = {
        'timestamp': datetime.now().isoformat(),
        'success': success,
        'message': 'Testnachricht gesendet' if success else 'Fehler beim Senden'
    }
    
    with open('telegram_test_result.json', 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    exit(0 if success else 1)
