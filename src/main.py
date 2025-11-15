<<<<<<< HEAD
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
=======
import requests
from bs4 import BeautifulSoup
import telegram
import os
import asyncio

# --- Configuration ---
NEWS_SOURCE_URL = "https://www.tagesschau.de/" # Example news source, replace with a suitable one
NUM_TOPICS = 5

# --- Scraping Function ---
def scrape_news(url):
    """
    Scrapes political news headlines and links from the given URL.
    Returns a list of dictionaries, each containing 'title' and 'link'.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news from {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    news_items = []

    # --- IMPORTANT: This part needs to be adapted for the specific news website ---
    # Example for Tagesschau.de (this might need adjustment if the website structure changes)
    # Look for common elements like <h2> tags within specific divs or articles
    articles = soup.find_all('article', class_='teaser') # Adjust class or tag as needed

    for article in articles[:NUM_TOPICS]:
        title_tag = article.find('span', class_='headline') # Adjust class or tag as needed
        link_tag = article.find('a', class_='teaser__link') # Adjust class or tag as needed

        if title_tag and link_tag and link_tag.get('href'):
            title = title_tag.get_text(strip=True)
            link = "https://www.tagesschau.de" + link_tag['href'] if link_tag['href'].startswith('/') else link_tag['href']
            news_items.append({'title': title, 'link': link})
    # --- End of website-specific scraping ---

    return news_items

# --- Summarization Function ---
def summarize_article(url):
    """
    Fetches an article and provides a basic summary.
    This is a placeholder. For better summaries, consider integrating an LLM.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching article for summarization from {url}: {e}")
        return "Could not retrieve article content for summary."

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # --- IMPORTANT: This part needs to be adapted for the specific news website ---
    # Example: Try to find paragraph tags within the main content area
    content_div = soup.find('div', class_='meldung') # Adjust class or tag as needed
    if content_div:
        paragraphs = content_div.find_all('p')
        summary_sentences = []
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text:
                # Take the first few sentences as a basic summary
                sentences = text.split('.')
                summary_sentences.extend([s.strip() for s in sentences if s.strip()])
                if len(summary_sentences) >= 3: # Aim for at least 3 sentences
                    break
        return ". ".join(summary_sentences[:3]) + "..." if summary_sentences else "No summary available."
    # --- End of website-specific summarization content extraction ---

    return "No summary available."

# --- Telegram Function ---
async def send_telegram_message(bot_token, chat_id, message):
    """
    Sends a message to a specified Telegram chat.
    """
    try:
        bot = telegram.Bot(token=bot_token)
        await bot.send_message(chat_id=chat_id, text=message, parse_mode=telegram.ParseMode.HTML)
        print("Message sent successfully to Telegram.")
    except Exception as e:
        print(f"Error sending message to Telegram: {e}")

# --- Main Logic ---
async def main():
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not telegram_bot_token or not telegram_chat_id:
        print("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID environment variables are not set.")
        print("Please set them up in your GitHub Secrets or local environment.")
        return

    print(f"Scraping news from {NEWS_SOURCE_URL}...")
    news_items = scrape_news(NEWS_SOURCE_URL)

    if not news_items:
        print("No news items found or an error occurred during scraping.")
        await send_telegram_message(telegram_bot_token, telegram_chat_id, "Konnte heute keine politischen Nachrichten finden.")
        return

    message_parts = ["<b>Tägliche Politische Nachrichten:</b>\n"]
    for i, item in enumerate(news_items):
        print(f"Summarizing: {item['title']} ({item['link']})")
        summary = summarize_article(item['link'])
        message_parts.append(f"<b>{i+1}. {item['title']}</b>\n")
        message_parts.append(f"{summary}\n")
        message_parts.append(f"<a href='{item['link']}'>Mehr lesen</a>\n\n")
    
    full_message = "".join(message_parts)
    await send_telegram_message(telegram_bot_token, telegram_chat_id, full_message)

if __name__ == "__main__":
    asyncio.run(main())
>>>>>>> 5d5a50c5b375233dbc8a67c08fee31137aefb5ae
