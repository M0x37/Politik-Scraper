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
