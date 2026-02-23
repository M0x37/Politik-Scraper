#!/usr/bin/env python3
"""
Direkter Test des Telegram Sendens
"""

import os
import requests
import json
from datetime import datetime

def direct_send_test():
    """Sendet Testnachricht direkt über API"""
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    print("=== DIREKT SEND TEST ===")
    print(f"Bot Token: {bot_token[:10]}..." if bot_token else "❌ Missing")
    print(f"Chat ID: {chat_id}" if chat_id else "❌ Missing")
    
    if not bot_token or not chat_id:
        print("❌ Missing credentials")
        return False
    
    # Test 1: Bot Info abrufen
    print("\n=== BOT INFO ===")
    try:
        bot_info_url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(bot_info_url, timeout=10)
        print(f"Bot Info Status: {response.status_code}")
        
        if response.status_code == 200:
            bot_data = response.json()
            if bot_data.get('ok'):
                bot = bot_data.get('result', {})
                print(f"✅ Bot Name: {bot.get('first_name')}")
                print(f"✅ Bot Username: @{bot.get('username')}")
            else:
                print(f"❌ Bot Error: {bot_data.get('description')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False
    
    # Test 2: Nachricht senden
    print("\n=== SEND TEST ===")
    try:
        send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        message = f"🧪 **Direkter Test**\n\n📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\nDies ist eine Testnachricht vom Politik Scraper Bot."
        
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        response = requests.post(send_url, json=data, timeout=30)
        print(f"Send Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Nachricht erfolgreich gesendet!")
                return True
            else:
                print(f"❌ API Error: {result.get('description')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    success = direct_send_test()
    
    result = {
        'timestamp': datetime.now().isoformat(),
        'direct_send_success': success,
        'message': 'Direct send test completed'
    }
    
    with open('direct_send_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    exit(0 if success else 1)
