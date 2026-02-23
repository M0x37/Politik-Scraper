#!/usr/bin/env python3
"""
Täglicher News-Scraper für GitHub Actions
Sendet täglich um 20:00 Berliner Zeit 5 Nachrichten mit Überschrift und einem Satz
"""

import requests
import feedparser
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
from typing import List, Dict
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NewsScraper:
    def __init__(self):
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
    
    def fetch_news_from_source(self, source: Dict) -> List[Dict]:
        """Holt Nachrichten von einer einzelnen Quelle"""
        try:
            logger.info(f"Hole Nachrichten von {source['name']}...")
            
            # RSS Feed parsen
            feed = feedparser.parse(source['url'])
            news_items = []
            
            for entry in feed.entries[:10]:  # Nur die ersten 10 Einträge
                try:
                    # Titel und Link extrahieren
                    title = entry.title.strip()
                    link = entry.link
                    
                    # Zusammenfassung extrahieren
                    summary = ""
                    if hasattr(entry, 'summary'):
                        summary = BeautifulSoup(entry.summary, 'html.parser').get_text().strip()
                    elif hasattr(entry, 'description'):
                        summary = BeautifulSoup(entry.description, 'html.parser').get_text().strip()
                    
                    # Wenn keine Zusammenfassung vorhanden, versuche den Inhalt zu holen
                    if not summary and link:
                        summary = self.get_content_summary(link)
                    
                    # Politik-Filter anwenden
                    if not self.is_political_news(title, summary, source.get('filter_keywords', [])):
                        continue
                    
                    # Nur einen Satz als Zusammenfassung
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
    
    def is_political_news(self, title: str, summary: str, filter_keywords: List[str]) -> bool:
        """Prüft ob eine Nachricht politisch relevant ist"""
        if not title and not summary:
            return False
        
        # Text für Analyse vorbereiten
        text = f"{title} {summary}".lower()
        
        # Politik-bezogene Keywords
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
        
        # Alle Keywords kombinieren
        all_keywords = political_keywords + filter_keywords
        
        # Prüfen ob mindestens ein Keyword gefunden wird
        for keyword in all_keywords:
            if keyword.lower() in text:
                return True
        
        # Zusätzliche Prüfung: Nicht-Politik-Themen ausschließen
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
    
    def get_content_summary(self, url: str) -> str:
        """Holt eine kurze Zusammenfassung von der URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Versuche verschiedene gängige Selektoren für Artikelinhalt
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
        
        # Satzzeichen finden
        sentence_endings = ['.', '!', '?']
        for i, char in enumerate(text):
            if char in sentence_endings:
                # Prüfen ob es wirklich ein Satzende ist (nicht Abkürzung)
                if i < len(text) - 1 and text[i+1] == ' ':
                    return text[:i+1].strip()
        
        # Wenn kein Satzende gefunden, die ersten 200 Zeichen zurückgeben
        return text[:200].strip() + ('...' if len(text) > 200 else '')
    
    def get_daily_news(self, limit: int = 5) -> List[Dict]:
        """Holt die Top-Nachrichten des Tages"""
        all_news = []
        
        # Nachrichten von allen Quellen holen
        for source in self.news_sources:
            news = self.fetch_news_from_source(source)
            all_news.extend(news)
        
        # Nach Veröffentlichungsdatum sortieren (neueste zuerst)
        all_news.sort(key=lambda x: x.get('published', ''), reverse=True)
        
        # Duplikate entfernen (basierend auf ähnlichen Titeln)
        unique_news = []
        seen_titles = set()
        
        for news in all_news:
            title_lower = news['title'].lower()
            # Prüfen auf ähnliche Titel (einfache Duplikatserkennung)
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
    
    def format_news_output(self, news_items: List[Dict]) -> str:
        """Formatiert die Nachrichten für die Ausgabe"""
        if not news_items:
            return "Keine Nachrichten gefunden."
        
        output = f"Tagesnachrichten vom {datetime.now().strftime('%d.%m.%Y')}\n\n"
        
        for i, news in enumerate(news_items, 1):
            output += f"{i}. {news['title']}\n"
            output += f"{news['summary']}\n\n"
        
        return output

def main():
    """Hauptfunktion"""
    scraper = NewsScraper()
    
    try:
        logger.info("Starte tägliche Nachrichtensammlung...")
        
        # Nachrichten holen
        news = scraper.get_daily_news(5)
        
        # Ausgabe formatieren
        formatted_output = scraper.format_news_output(news)
        
        # Ausgabe in Console (für GitHub Actions Log)
        print("=" * 50)
        print(formatted_output)
        print("=" * 50)
        
        # Optional: Als JSON speichern für andere Verwendungszwecke
        output_data = {
            'date': datetime.now().isoformat(),
            'news_count': len(news),
            'news': news
        }
        
        with open('daily_news.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        logger.info("Nachrichtensammlung abgeschlossen")
        
    except Exception as e:
        logger.error(f"Fehler bei der Nachrichtensammlung: {e}")
        raise

if __name__ == "__main__":
    main()
