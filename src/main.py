import os
from dotenv import load_dotenv
import requests
from datetime import datetime
import feedparser
from bs4 import BeautifulSoup

load_dotenv()

def get_news_from_sources():
    all_news = []
    
    try:
        print("  - Lade Tagesschau...")
        feed = feedparser.parse('https://www.tagesschau.de/xml/rss2/')
        for entry in feed.entries[:8]:
            if 'politik' in entry.link.lower() or 'inland' in entry.link.lower():
                all_news.append({
                    'title': entry.title,
                    'link': entry.link,
                    'summary': clean_html(entry.get('summary', '')),
                    'source': 'Tagesschau'
                })
    except Exception as e:
        print(f"    Tagesschau Fehler: {e}")
    
    try:
        print("  - Lade Spiegel...")
        feed = feedparser.parse('https://www.spiegel.de/politik/index.rss')
        for entry in feed.entries[:5]:
            all_news.append({
                'title': entry.title,
                'link': entry.link,
                'summary': clean_html(entry.get('description', '')),
                'source': 'Spiegel'
            })
    except Exception as e:
        print(f"    Spiegel Fehler: {e}")
    
    return all_news

def clean_html(text):
    if not text:
        return ""
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text().strip()

def format_telegram_message(news_items):
    today = datetime.now().strftime('%d.%m.%Y')
    message = f"📰 *Politik-Nachrichten vom {today}*\n\n"
    
    for i, news in enumerate(news_items[:5], 1):
        title = news['title'][:100]
        link = news['link']
        summary = news['summary'][:180] if news['summary'] else "Keine Zusammenfassung"
        source = news['source']
        
        message += f"*{i}. {title}*\n"
        message += f"{summary}\n"
        message += f"📌 {source} | {link}\n\n"
    
    message += f"_Gesendet um {datetime.now().strftime('%H:%M')} Uhr_"
    return message

def send_telegram(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print(f"✅ Nachricht erfolgreich gesendet!")
        return True
    except Exception as e:
        print(f"❌ Fehler beim Senden: {e}")
        if 'response' in locals():
            print(f"   Response: {response.text}")
        return False

def main():
    print(f"🕐 Start: {datetime.now().strftime('%H:%M:%S')}")
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        print("❌ TELEGRAM_BOT_TOKEN oder TELEGRAM_CHAT_ID fehlt!")
        return
    
    print("🔍 Sammle Nachrichten...")
    news = get_news_from_sources()
    
    if not news:
        print("❌ Keine Nachrichten gefunden!")
        return
    
    print(f"✅ {len(news)} Nachrichten gefunden")
    print("📤 Sende Telegram-Nachricht...")
    
    message = format_telegram_message(news)
    send_telegram(token, chat_id, message)
    
    print(f"🏁 Fertig: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()
