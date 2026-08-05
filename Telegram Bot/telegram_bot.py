#!/usr/bin/env python3
"""
Telegram Bot für tägliche politische Nachrichten
Sendet täglich um 20:00 Berliner Zeit 5 politische Nachrichten
"""

import requests
import feedparser
from bs4 import BeautifulSoup
import json
import re
import time
import calendar
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
                'filter_keywords': [],
                'politics_ressort': True
            },
            {
                'name': 'ZDF Politik',
                'url': 'https://www.zdf.de/rss/zdf/nachrichten/politik/rss-90-1.xml',
                'language': 'de',
                'filter_keywords': [],
                'politics_ressort': True
            },
            {
                'name': 'Deutsche Welle Politik',
                'url': 'https://rss.dw.com/xml/rss-de-politik',
                'language': 'de',
                'filter_keywords': [],
                'politics_ressort': True
            },
            {
                'name': 'ARD Politik',
                'url': 'https://www.tagesschau.de/xml/rss2/',
                'language': 'de',
                'filter_keywords': ['Politik', 'Regierung', 'Bundestag', 'Kanzler', 'Minister', 'Wahl', 'Partei', 'Koalition', 'Gesetz', 'Parlament']
            }
        ]
    
    def is_political_news(self, title: str, summary: str, filter_keywords: List[str], politics_ressort: bool = False) -> bool:
        """Prüft ob eine Nachricht politisch relevant ist"""
        if not title and not summary:
            return False

        text = f"{title} {summary}".lower()

        # Themen, die niemals Politikmeldungen sind (Wortgrenzen beachten, damit
        # z.B. 'Gesundheitsminister' nicht durch 'gesundheit' aussortiert wird)
        non_political_keywords = [
            'sport', 'fussball', 'bundesliga', 'champions league', 'fc bayern',
            'borussia dortmund', 'formel 1', 'tennis', 'wimbledon', 'olympia',
            'unterhaltung', 'film', 'musik', 'kino', 'serie', 'netflix',
            'promi', 'celebrity', 'royal', 'könig', 'königin', 'prinz',
            'wetter', 'unwetter', 'sturm', 'regen', 'schnee', 'hitze',
            'rezepte', 'kochen', 'backen', 'reise', 'urlaub', 'hotel',
            'flug', 'ferien', 'tier', 'haustier', 'hund', 'katze', 'pferd'
        ]

        for keyword in non_political_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                return False

        # Dedizierte Politik-Ressort-Feeds (n-tv, ZDF, DW): alles behalten,
        # was kein klar unpolitischer Inhalt ist
        if politics_ressort:
            return True

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
            'flüchtlinge', 'migration', 'asyl', 'grenze', 'integration',
            # Zusätzliche Begriffe für bessere Erkennung in allgemeinen Feeds
            'haushalt', 'steuer', 'wirtschaft', 'ministerium', 'bürgergeld',
            'rente', 'grundgesetz', 'verfassung', 'justiz', 'gericht', 'urteil',
            'bundesregierung', 'ministerpräsidentenkonferenz', 'bundeswehr',
            'sicherheit', 'verbraucherschutz', 'bildungspolitik'
        ]

        all_keywords = political_keywords + filter_keywords

        for keyword in all_keywords:
            if keyword.lower() in text:
                return True

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

                    if not self.is_political_news(title, summary, source.get('filter_keywords', []), source.get('politics_ressort', False)):
                        continue

                    if summary:
                        summary = self.get_summary(summary)

                    published_str = getattr(entry, 'published', None) or getattr(entry, 'updated', None) or datetime.now().isoformat()
                    published_ts = None
                    if getattr(entry, 'published_parsed', None):
                        published_ts = calendar.timegm(entry.published_parsed)
                    elif getattr(entry, 'updated_parsed', None):
                        published_ts = calendar.timegm(entry.updated_parsed)
                    if published_ts is None:
                        published_ts = time.time()

                    news_items.append({
                        'title': title,
                        'summary': summary,
                        'link': link,
                        'source': source['name'],
                        'published': published_str,
                        'published_ts': published_ts
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
    
    def _clean_text(self, text: str) -> str:
        """Bereinigt Rohtext: Leerzeichen, Zeitstempel-Präfixe, überflüssige Zeichen"""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        text = re.sub(r'^\s*(stand:)?\s*\d{2}\.\d{2}\.\d{4}\s*\d{1,2}:\d{2}\s*uhr\s*', '', text, flags=re.IGNORECASE)
        return text.strip(' …')

    def get_summary(self, text: str, max_len: int = 240) -> str:
        """Extrahiert 1–2 vollständige Sätze als kompakte Zusammenfassung"""
        if not text:
            return ""

        text = self._clean_text(text)

        # Typische RSS-Füllsätze am Ende entfernen
        for filler in ['mehr dazu in kürze', 'weitere informationen finden sie',
                       'lesen sie auch', 'siehe auch', 'mehr bei']:
            idx = text.lower().find(filler)
            if idx > 40:
                text = text[:idx].strip()

        sentences = re.split(r'(?<=[.!?])\s+', text)
        summary = ""
        truncated = False
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            if len(sentence) > max_len:
                sentence = sentence[:max_len].rsplit(' ', 1)[0]
                truncated = True
            if not summary:
                summary = sentence
            elif len(summary) + len(sentence) + 1 <= max_len:
                summary += " " + sentence
            else:
                truncated = True
                break

        if not summary:
            summary = text[:max_len]
            truncated = len(text) > max_len

        return summary.strip() + ("…" if truncated else "")

    def _normalize_title(self, title: str) -> str:
        """Normalisiert Titel für die Duplikat-Erkennung"""
        if not title:
            return ""
        t = title.lower()
        # Quellen-Suffixe entfernen (z.B. ' | tagesschau.de', ' - n-tv.de')
        t = re.sub(r'\s*[-|–—]\s*(tagesschau|ntv|n-tv|zdf|dw|ard|deutschland).*$', '', t)
        t = re.sub(r'[^a-zäöüß0-9\s]', '', t)
        return re.sub(r'\s+', ' ', t).strip()

    def _news_score(self, news: Dict) -> float:
        """Bewertet eine Meldung: Aktualität + Qualität der Zusammenfassung"""
        score = 0.0

        published_ts = news.get('published_ts')
        if published_ts:
            age_hours = (time.time() - float(published_ts)) / 3600.0
            score += max(0.0, 1.0 - age_hours / 72.0)

        summary = news.get('summary') or ''
        score += min(1.0, len(summary) / 200.0) * 1.5

        return score
    
    def get_daily_news(self, limit: int = 5) -> List[Dict]:
        """Holt die Top-Politiknachrichten des Tages"""
        all_news = []

        for source in self.news_sources:
            news = self.fetch_news_from_source(source)
            all_news.extend(news)

        # Beste Meldungen zuerst (Aktualität + Qualität der Zusammenfassung)
        all_news.sort(key=lambda x: self._news_score(x), reverse=True)

        unique_news = []
        seen_titles = set()
        seen_links = set()

        for news in all_news:
            link = news.get('link', '').strip().lower()
            if link:
                if link in seen_links:
                    continue
                seen_links.add(link)

            title_lower = self._normalize_title(news.get('title', ''))
            is_duplicate = False
            for seen_title in seen_titles:
                if self.similarity_check(title_lower, seen_title) > 0.5:
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
        """Ähnlichkeitsprüfung auf Wort-Bigramm-Ebene"""
        def bigrams(text: str) -> set:
            words = text.split()
            if len(words) <= 1:
                return set(words)
            return {f"{words[i]} {words[i + 1]}" for i in range(len(words) - 1)}

        b1 = bigrams(self._normalize_title(text1))
        b2 = bigrams(self._normalize_title(text2))

        if not b1 or not b2:
            return 0.0

        intersection = b1.intersection(b2)
        union = b1.union(b2)
        return len(intersection) / len(union)
    
    def _escape_markdown(self, text: str) -> str:
        """Escape-Markdown-Sonderzeichen für Telegram (legacy Markdown)"""
        for char in ['\\', '_', '*', '[', ']', '`']:
            text = text.replace(char, '\\' + char)
        return text

    def format_telegram_message(self, news_items: List[Dict]) -> str:
        """Formatiert Nachrichten für Telegram (ohne Quellenangabe)"""
        if not news_items:
            return "*Keine politischen Nachrichten gefunden.*"

        date_str = datetime.now().strftime('%d.%m.%Y')
        message = f"*Tagesnachrichten vom {date_str}*\n\n"

        for i, news in enumerate(news_items, 1):
            title = self._escape_markdown(news.get('title', '').strip())
            summary = self._escape_markdown(news.get('summary', '').strip())
            link = news.get('link', '').strip()

            message += f"*{i}. {title}*\n"
            if summary:
                message += f"{summary}\n"
            if link:
                message += f"{link}\n"
            message += "\n──────────────\n\n"

        # Telegram-Limit (4096 Zeichen) absichern
        if len(message) > 4096:
            message = message[:4090].rsplit('\n', 1)[0] + '\n\n...'

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
