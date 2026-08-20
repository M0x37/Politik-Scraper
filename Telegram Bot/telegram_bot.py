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
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Dict
import logging

import re
import telegram

from telegram import Bot

from dotenv import load_dotenv

# Lädt Variablen aus der .env-Datei im Projektordner.
# Bestehende Umgebungsvariablen haben Vorrang.
load_dotenv()

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
    
    def _contains_keyword(self, text: str, keywords: List[str]) -> bool:
        """Prüft Keywords als ganze Wörter bzw. vollständige Phrasen."""
        normalized = re.sub(r'\s+', ' ', text.casefold()).strip()
        for keyword in keywords:
            pattern = r'(?<!\w)' + re.escape(keyword.casefold()).replace(r'\ ', r'\s+') + r'(?!\w)'
            if re.search(pattern, normalized):
                return True
        return False

    def is_political_news(self, title: str, summary: str, filter_keywords: List[str]) -> bool:
        """Akzeptiert nur Nachrichten mit einem eindeutigen Politikbezug im Titel."""
        if not title:
            return False

        political_keywords = [
            'politik', 'regierung', 'bundesregierung', 'bundestag', 'bundesrat', 'kanzler',
            'minister', 'ministerium', 'senator', 'senatorin', 'wahl', 'partei', 'koalition',
            'gesetz', 'parlament',
            'abgeordnete', 'brüssel', 'eu-kommission', 'eu-parlament', 'eu-rat',
            'ungarn', 'orban', 'öffentlich-rechtlich', 'kampfjet', 'drohne',
            'rumänien',
            'europäische union', 'europawahl',
            'bundestagswahl', 'landtagswahl', 'kommunalwahl', 'cdu', 'csu', 'spd',
            'grüne', 'fdp', 'afd', 'linke', 'bsw', 'merz', 'scholz', 'baerbock',
            'lindner', 'habeck', 'faeser', 'wissing', 'kabinett', 'opposition',
            'ausschuss', 'außenpolitik', 'innenpolitik', 'wirtschaftspolitik',
            'sozialpolitik', 'klimapolitik', 'verteidigungspolitik', 'finanzpolitik',
            'sicherheitspolitik', 'diplomatie', 'gipfel', 'sanktionen', 'nato',
            'migration', 'asyl', 'flüchtlinge', 'grenze', 'abkommen', 'vertrag',
            'strafgerichtshof', 'internationaler strafgerichtshof', 'nord-stream',
            'invasion', 'ukraine', 'russland'
        ]
        political_keywords.extend(filter_keywords)

        non_political_keywords = [
            'sport', 'fußball', 'bundesliga', 'champions league', 'formel 1', 'tennis',
            'wimbledon', 'olympia', 'unterhaltung', 'film', 'musik', 'kino', 'netflix',
            'promi', 'celebrity', 'wetter', 'unwetter', 'sturm', 'regen', 'schnee',
            'rezepte', 'kochen', 'backen', 'reise', 'urlaub', 'hotel', 'flug', 'ferien',
            'gesundheit', 'krankheit', 'medizin', 'arzt', 'krankenhaus', 'tier',
            'haustier', 'hund', 'katze', 'pferd'
        ]

        title_has_politics = self._contains_keyword(title, political_keywords)

        # Für die tägliche Ausgabe zählt der Titel. So werden zufällige Begriffe
        # in RSS-Beschreibungen nicht dazu benutzt, Nicht-Politik einzuschleusen.
        if not title_has_politics:
            return False

        # Offensichtliche Nicht-Politik-Themen bleiben ausgeschlossen, außer der
        # Titel enthält zusätzlich einen starken politischen Begriff.
        if self._contains_keyword(title, non_political_keywords):
            strong_politics = [
                'regierung', 'bundesregierung', 'bundestag', 'kanzler', 'minister',
                'wahl', 'partei', 'koalition', 'gesetz', 'parlament', 'politik',
                'abgeordnete', 'eu-kommission', 'eu-parlament'
            ]
            if not self._contains_keyword(title, strong_politics):
                return False

        return True

    def fetch_news_from_source(self, source: Dict) -> List[Dict]:
        """Holt Nachrichten von einer einzelnen Quelle"""
        try:
            logger.info(f"Hole Nachrichten von {source['name']}...")
            
            feed = feedparser.parse(source['url'])
            news_items = []
            
            for entry in feed.entries[:20]:

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

                    # Titel und RSS-Kontext gemeinsam prüfen, damit relevante
                    # politische Ereignisse nicht wegen eines neutralen Titels
                    # verloren gehen.
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
        
        message = f"Tagesnachrichten vom {datetime.now().strftime('%d.%m.%Y')}\n\n"

        for i, news in enumerate(news_items, 1):
            message += f"{i}. {news['title']}\n"
            message += f"{news['summary']}\n\n"
        
        return message

    def send_news_text_to_telegram(self, news_items: List[Dict]) -> bool:
        """Sendet die fünf Nachrichten zusätzlich als normalen Telegram-Text."""
        try:
            logger.info("Sende die fünf Nachrichten zusätzlich als normalen Text...")
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            response = requests.post(
                url,
                json={
                    'chat_id': self.chat_id,
                    'text': self.format_telegram_message(news_items),
                },
                timeout=60,
            )
            result = response.json()
            if response.status_code == 200 and result.get('ok'):
                logger.info("Die normale Textnachricht wurde erfolgreich gesendet")
                return True
            logger.error("Telegram Text API Error: %s", result.get('description', response.text))
            return False
        except Exception as e:
            logger.error(f"Fehler beim Senden der normalen Textnachricht: {e}")
            return False

    def send_news_image_to_telegram(self, news_items: List[Dict], png_path: Path) -> bool:
        """Sendet das eine gemeinsame Handschrift-PNG an Telegram."""
        try:
            logger.info("Sende ein gemeinsames Nachrichtenblatt an Telegram...")
            url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"
            caption = f"Politik-Nachrichten vom {datetime.now().strftime('%d.%m.%Y')} – 5 Meldungen"

            with png_path.open('rb') as image_file:
                response = requests.post(
                    url,
                    data={'chat_id': self.chat_id, 'caption': caption},
                    files={'photo': ('politik-nachrichten.png', image_file, 'image/png')},
                    timeout=60,
                )

            result = response.json()
            if response.status_code == 200 and result.get('ok'):
                logger.info("Das eine Nachrichtenblatt wurde erfolgreich an Telegram gesendet")
                return True

            logger.error("Telegram API Error: %s", result.get('description', response.text))
            return False
        except Exception as e:
            logger.error(f"Fehler beim Senden des Nachrichtenblatts: {e}")
            return False


def build_handwriting_text(news_items: List[Dict]) -> str:
    """Baut aus genau fünf Meldungen den gemeinsamen Text für ein Blatt."""
    if len(news_items) != 5:
        raise ValueError(f"Es werden genau 5 Nachrichten benötigt, erhalten: {len(news_items)}")

    parts = [f"Politik-Nachrichten vom {datetime.now().strftime('%d.%m.%Y')}", ""]
    for index, news in enumerate(news_items, 1):
        parts.append(f"{index}. {news['title']}")
        if news.get('summary'):
            parts.append(news['summary'])
        parts.append("")
    return "\n".join(parts).strip() + "\n"


def render_handwriting_sheet(news_items: List[Dict]) -> Path:
    """Startet den integrierten Converter und exportiert genau eine PNG-Datei."""
    project_root = Path(__file__).resolve().parents[1]
    converter_dir = project_root / 'handwriting-converter'
    renderer = converter_dir / 'render_sheet.cjs'
    if not renderer.exists():
        raise FileNotFoundError(f"Converter-Renderer fehlt: {renderer}")

    npm_command = shutil.which('npm') or shutil.which('npm.cmd')
    node_command = shutil.which('node')
    if not npm_command or not node_command:
        raise RuntimeError('Node.js und npm müssen installiert sein.')

    output_path = project_root / 'daily_news_handwritten.png'
    with tempfile.TemporaryDirectory(prefix='politik-news-') as temp_dir:
        input_path = Path(temp_dir) / 'news.txt'
        input_path.write_text(build_handwriting_text(news_items), encoding='utf-8')
        port = os.getenv('HANDWRITING_PORT', '3000')
        server = subprocess.Popen(
            [npm_command, 'start', '--', '--port', port],
            cwd=converter_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        try:
            for _ in range(60):
                try:
                    requests.get(f'http://127.0.0.1:{port}', timeout=2)
                    break
                except requests.RequestException:
                    import time
                    time.sleep(1)
            else:
                raise RuntimeError('Der lokale Handwriting-Converter ist nicht gestartet.')

            subprocess.run(
                [node_command, str(renderer), str(input_path), str(output_path), port],
                cwd=converter_dir,
                check=True,
            )
        finally:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()

    if not output_path.exists() or output_path.stat().st_size == 0:
        raise RuntimeError('Die gemeinsame PNG-Datei wurde nicht erzeugt.')
    logger.info("Ein gemeinsames PNG erstellt: %s", output_path)
    return output_path

def main():
    """Hauptfunktion"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
    chat_id = os.getenv('TELEGRAM_CHAT_ID', '').strip()

    missing = []
    if not bot_token:
        missing.append('TELEGRAM_BOT_TOKEN')
    if not chat_id:
        missing.append('TELEGRAM_CHAT_ID')

    if missing:
        logger.warning(
            "Fehlende Umgebungsvariablen: %s. "
            "Lege im Projektordner eine .env-Datei anhand von .env.example an.",
            ', '.join(missing)
        )

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
        
        if len(news) != 5:
            raise RuntimeError(f"Es wurden nicht genau 5 Nachrichten gefunden: {len(news)}")

        # Alle fünf Meldungen gemeinsam als ein Handschriftblatt rendern.
        png_path = render_handwriting_sheet(news)
        output_data['handwritten_png'] = str(png_path.name)

        image_sent = False
        text_sent = False
        if bot_token and chat_id:
            # Erst das gemeinsame Handschriftblatt, danach die normale Textliste.
            image_sent = bot.send_news_image_to_telegram(news, png_path)
            text_sent = bot.send_news_text_to_telegram(news)
        else:
            logger.info("Telegram Senden übersprungen (keine Credentials)")

        output_data['telegram_image_sent'] = image_sent
        output_data['telegram_text_sent'] = text_sent
        output_data['telegram_sent'] = image_sent and text_sent

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
