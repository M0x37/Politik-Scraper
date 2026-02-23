#!/usr/bin/env python3
"""
Überprüft die GitHub Secrets
"""

import os
import json
from datetime import datetime

def check_secrets():
    """Überprüft ob die Secrets vorhanden sind"""
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    print("=== SECRET CHECK ===")
    print(f"TELEGRAM_BOT_TOKEN: {'✅ Present' if bot_token else '❌ Missing'}")
    print(f"TELEGRAM_CHAT_ID: {'✅ Present' if chat_id else '❌ Missing'}")
    
    if bot_token:
        print(f"Token length: {len(bot_token)}")
        print(f"Token starts with: {bot_token[:10]}...")
        print(f"Token format ok: {bot_token.startswith(('1', '2', '3', '4', '5', '6', '7', '8', '9', '0')) and ':' in bot_token}")
    
    if chat_id:
        print(f"Chat ID: {chat_id}")
        print(f"Chat ID is numeric: {chat_id.lstrip('-').isdigit()}")
    
    # Test API call ohne zu senden
    if bot_token:
        try:
            import requests
            url = f"https://api.telegram.org/bot{bot_token}/getMe"
            response = requests.get(url, timeout=10)
            
            print(f"\n=== BOT INFO ===")
            print(f"API Status: {response.status_code}")
            
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get('ok'):
                    bot_data = bot_info.get('result', {})
                    print(f"Bot Name: {bot_data.get('first_name', 'Unknown')}")
                    print(f"Bot Username: @{bot_data.get('username', 'Unknown')}")
                    print(f"Bot can send messages: {bot_data.get('can_send_messages', False)}")
                    print("✅ Bot Token is valid!")
                else:
                    print(f"❌ Bot API Error: {bot_info.get('description')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception checking bot: {e}")
    
    # Ergebnisse speichern
    result = {
        'timestamp': datetime.now().isoformat(),
        'bot_token_present': bool(bot_token),
        'chat_id_present': bool(chat_id),
        'bot_token_length': len(bot_token) if bot_token else 0,
        'chat_id': chat_id if chat_id else None,
        'check_completed': True
    }
    
    with open('secrets_check.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("\n=== RESULTS SAVED ===")
    print("Check results saved to secrets_check.json")

if __name__ == "__main__":
    check_secrets()
