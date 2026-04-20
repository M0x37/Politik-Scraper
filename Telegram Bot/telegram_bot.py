#!/usr/bin/env python3
"""
Telegram Bot für tägliche politische Nachrichten
Sendet täglich um 20:00 Berliner Zeit 5 politische Nachrichten
"""

import requests
import feedparser
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
from typing import List, Dict
import logging
import telegram
from telegram import Bot
import urllib.parse
import webbrowser

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NewsTelegramBot:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.news_sources = [
            {
                'name': 'Tagesschau Politik',
                'url': 'https://www.tagesschau.de/xml/rss2/',
                'language': 'de',
                'filter_keywords': ['Politik', 'Regierung', 'Bundestag', 'Kanzler', 'Minister', 'Wahl', 'Partei', 'Koalition', 'Gesetz', 'Parlament']
            },
            {
                'name': 'n-tv Politik',
                'url': 'https://n-tv.de/rss/ressort/politik.rss',
                'language': 'de',
                'filter_keywords': []
            },
            {
                'name': 'ZDF Politik',
                'url': 'https://www.zdf.de/rss/zdf/nachrichten/politik/rss-90-1.xml',
                'language': 'de',
                'filter_keywords': []
            },
            {
                'name': 'Deutsche Welle Politik',
                'url': 'https://rss.dw.com/xml/rss-de-politik',
                'language': 'de',
                'filter_keywords': []
            },
            {
                'name': 'ARD Politik',
                'url': 'https://www.tagesschau.de/xml/rss2/',
                'language': 'de',
                'filter_keywords': ['Politik', 'Regierung', 'Bundestag', 'Kanzler', 'Minister', 'Wahl', 'Partei', 'Koalition', 'Gesetz', 'Parlament']
            }
        ]
    
    def is_political_news(self, title: str, summary: str, filter_keywords: List[str]) -> bool:
        """Prüft ob eine Nachricht politisch relevant ist"""
        if not title and not summary:
            return False
        
        text = f"{title} {summary}".lower()
        
        political_keywords = [
            'politik', 'regierung', 'bundestag', 'kanzler', 'minister', 'wahl', 'partei', 
            'koalition', 'gesetz', 'parlament', 'abgeordnete', 'bund', 'länder',
            'eu', 'european union', 'brüssel', 'merkel', 'scholz', 'baerbock',
            'lindner', 'habeck', 'faeser', 'wissing', 'ampel', 'cdu', 'spd',
            'grüne', 'fdp', 'afd', 'linke', 'bsw', 'friedrich merz',
            'kabinett', 'kabinettssitzung', 'ministerpräsident', 'mp',
            'opposition', 'regierungskoalition', 'koalitionsausschuss',
            'bundestagswahl', 'landtagswahl', 'europawahl', 'kommunalwahl',
            'gesetzgebung', 'bundestag', 'bundesrat', 'ausschuss',
            'außenpolitik', 'innenpolitik', 'wirtschaftspolitik', 'sozialpolitik',
            'klimapolitik', 'verteidigungspolitik', 'finanzpolitik',
            'diplomatie', 'gipfel', 'konferenz', 'vertrag', 'abkommen',
            'sanktionen', 'russland', 'ukraine', 'usa', 'china', 'nato',
            'flüchtlinge', 'migration', 'asyl', 'grenze', 'integration'
        ]
        
        all_keywords = political_keywords + filter_keywords
        
        for keyword in all_keywords:
            if keyword.lower() in text:
                return True
        
        non_political_keywords = [
            'sport', 'fußball', 'bundesliga', 'champions league', 'fc bayern',
            'borussia dortmund', 'formel 1', 'tennis', 'wimbledon', 'olympia',
            'unterhaltung', 'film', 'musik', 'kino', 'serie', 'netflix',
            'promi', 'celebrity', 'royal', 'könig', 'königin', 'prinz',
            'wetter', 'unwetter', 'sturm', 'regen', 'schnee', 'hitze',
            'rezepte', 'kochen', 'backen', 'essen', 'trinken',
            'reise', 'urlaub', 'hotel', 'flug', 'ferien',
            'gesundheit', 'krankheit', 'medizin', 'arzt', 'krankenhaus',
            'tier', 'haustier', 'hund', 'katze', 'pferd'
        ]
        
        for keyword in non_political_keywords:
            if keyword.lower() in text:
                return False
        
        return False
    
    def fetch_news_from_source(self, source: Dict) -> List[Dict]:
        """Holt Nachrichten von einer einzelnen Quelle"""
        try:
            logger.info(f"Hole Nachrichten von {source['name']}...")
            
            feed = feedparser.parse(source['url'])
            news_items = []
            
            for entry in feed.entries[:10]:
                try:
                    title = entry.title.strip()
                    link = entry.link
                    
                    summary = ""
                    if hasattr(entry, 'summary'):
                        summary = BeautifulSoup(entry.summary, 'html.parser').get_text().strip()
                    elif hasattr(entry, 'description'):
                        summary = BeautifulSoup(entry.description, 'html.parser').get_text().strip()
                    
                    if not summary and link:
                        summary = self.get_content_summary(link)
                    
                    if not self.is_political_news(title, summary, source.get('filter_keywords', [])):
                        continue
                    
                    if summary:
                        summary = self.get_first_sentence(summary)
                    
                    news_items.append({
                        'title': title,
                        'summary': summary,
                        'link': link,
                        'source': source['name'],
                        'published': getattr(entry, 'published', datetime.now().isoformat())
                    })
                    
                except Exception as e:
                    logger.warning(f"Fehler bei der Verarbeitung eines Eintrags von {source['name']}: {e}")
                    continue
            
            logger.info(f"{len(news_items)} Nachrichten von {source['name']} geholt")
            return news_items
            
        except Exception as e:
            logger.error(f"Fehler beim Abruf von {source['name']}: {e}")
            return []
    
    def get_content_summary(self, url: str) -> str:
        """Holt eine kurze Zusammenfassung von der URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            content_selectors = [
                'article p',
                '.article-content p',
                '.content p',
                'main p',
                '.text p'
            ]
            
            for selector in content_selectors:
                paragraphs = soup.select(selector)
                if paragraphs:
                    text = ' '.join([p.get_text().strip() for p in paragraphs[:3]])
                    if text:
                        return text
            
            return ""
            
        except Exception as e:
            logger.warning(f"Konnte Inhalt von {url} nicht holen: {e}")
            return ""
    
    def get_first_sentence(self, text: str) -> str:
        """Extrahiert den ersten vollständigen Satz aus einem Text"""
        if not text:
            return ""
        
        sentence_endings = ['.', '!', '?']
        for i, char in enumerate(text):
            if char in sentence_endings:
                if i < len(text) - 1 and text[i+1] == ' ':
                    return text[:i+1].strip()
        
        return text[:200].strip() + ('...' if len(text) > 200 else '')
    
    def get_daily_news(self, limit: int = 5) -> List[Dict]:
        """Holt die Top-Politiknachrichten des Tages"""
        all_news = []
        
        for source in self.news_sources:
            news = self.fetch_news_from_source(source)
            all_news.extend(news)
        
        all_news.sort(key=lambda x: x.get('published', ''), reverse=True)
        
        unique_news = []
        seen_titles = set()
        
        for news in all_news:
            title_lower = news['title'].lower()
            is_duplicate = False
            for seen_title in seen_titles:
                if self.similarity_check(title_lower, seen_title) > 0.8:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_news.append(news)
                seen_titles.add(title_lower)
                
                if len(unique_news) >= limit:
                    break
        
        logger.info(f"{len(unique_news)} einzigartige Nachrichten gefunden")
        return unique_news[:limit]
    
    def similarity_check(self, text1: str, text2: str) -> float:
        """Einfache Ähnlichkeitsprüfung zwischen zwei Texten"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def format_telegram_message(self, news_items: List[Dict]) -> str:
        """Formatiert Nachrichten für Telegram"""
        if not news_items:
            return " Keine politischen Nachrichten gefunden."
        
        message = f" *Tagesnachrichten vom {datetime.now().strftime('%d.%m.%Y')}*\n\n"
        
        for i, news in enumerate(news_items, 1):
            message += f"*{i}. {news['title']}*\n"
            message += f"{news['summary']}\n\n"
        
        return message
    
    def open_in_converter(self, text: str) -> None:
        """Öffnet den Text im Handschrift Converter"""
        try:
            encoded = urllib.parse.quote(text)
            converter_url = f"https://sozi-zeta.vercel.app/?text={encoded}"
            logger.info(f"Öffne Converter: {converter_url}")
            webbrowser.open(converter_url)
        except Exception as e:
            logger.warning(f"Konnte Converter nicht öffnen: {e}")
    
    def send_news_to_telegram(self) -> bool:
        """Sendet tägliche Nachrichten an Telegram"""
        try:
            logger.info("Sende tägliche Nachrichten an Telegram...")
            
            # Nachrichten holen
            news = self.get_daily_news(5)
            
            # Nachricht formatieren
            message = self.format_telegram_message(news)
            
            # Direkte API-Anfrage statt Bibliothek
            import requests
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    logger.info("Nachrichten erfolgreich an Telegram gesendet")
                    return True
                else:
                    logger.error(f"API Error: {result.get('description')}")
                    return False
            else:
                logger.error(f"HTTP Error: {response.status_code} - {response.text}")
                return False
            
        except Exception as e:
            logger.error(f"Fehler beim Senden an Telegram: {e}")
            return False

def main():
    """Hauptfunktion"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        logger.warning("TELEGRAM_BOT_TOKEN und TELEGRAM_CHAT_ID nicht gesetzt - nur Converter wird geöffnet")

    bot = NewsTelegramBot(bot_token or '', chat_id or '')
    
    try:
        # Nachrichten holen (unabhängig vom Senden)
        news = bot.get_daily_news(5)
        
        # Immer JSON erstellen
        output_data = {
            'date': datetime.now().isoformat(),
            'news_count': len(news),
            'news': news
        }
        
        with open('daily_news.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON-Datei erstellt mit {len(news)} Nachrichten")
        
        # Nachricht formatieren für Telegram UND Converter
        message = bot.format_telegram_message(news)
        
        # Im Converter öffnen
        bot.open_in_converter(message)
        
        # Nur an Telegram senden wenn Token und Chat ID vorhanden
        success = False
        if bot_token and chat_id:
            success = bot.send_news_to_telegram()
        else:
            logger.info("Telegram Senden übersprungen (keine Credentials)")
        
        output_data['telegram_sent'] = success
        
        # JSON aktualisieren mit Sendestatus
        with open('daily_news.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        logger.info("Telegram Bot Ausführung abgeschlossen")
        
    except Exception as e:
        logger.error(f"Fehler bei der Bot-Ausführung: {e}")
        # Auch bei Fehler JSON erstellen
        error_data = {
            'date': datetime.now().isoformat(),
            'news_count': 0,
            'news': [],
            'telegram_sent': False,
            'error': str(e)
        }
        with open('daily_news.json', 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=2)
        raise

if __name__ == "__main__":
    main()
