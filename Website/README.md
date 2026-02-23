# 🌐 Politik News Website

Eine moderne, responsive Website zur Anzeige der täglichen politischen Nachrichten vom Telegram Bot.

## 📁 Dateien:

- **`index.html`** - Haupt-HTML-Seite
- **`style.css`** - Modernes CSS mit Responsive Design
- **`script.js`** - JavaScript für Interaktivität
- **`README.md`** - Diese Datei

## 🚀 Funktionen:

### 📱 Nachrichten-Anzeige:
- **Automatisches Laden** der neuesten Nachrichten
- **Kopier-Button** für jede Nachricht (Handy/PC/iPad kompatibel)
- **Responsive Design** für alle Geräte
- **Auto-Refresh** alle 5 Minuten
- **Demo-Modus** wenn keine Daten verfügbar

### 🎨 Design:
- **Modernes UI** mit Glassmorphismus-Effekten
- **Gradient-Hintergrund** mit professionellem Look
- **Font Awesome Icons** für bessere Visualisierung
- **Hover-Effekte** und sanfte Animationen
- **Mobile-First** Responsive Design

### 🔧 Technische Features:
- **Clipboard API** mit Fallback für ältere Browser
- **JSON-Lade** mit Fehlerbehandlung
- **HTML-Escaping** für Sicherheit
- **Auto-Refresh** mit Intervall
- **Demo-Daten** wenn keine Verbindung möglich

## 📋 Nutzung:

### 1. Website öffnen:
```bash
# Doppelklick auf index.html oder
# Oder lokaler Webserver
python -m http.server 8000
# Dann http://localhost:8000
```

### 2. Nachrichten kopieren:
- **Klick auf "Kopieren"** Button bei jeder Nachricht
- **Automatische Bestätigung** mit "Kopiert!" Status
- **Kompatibel** mit Handy, PC, iPad

### 3. Automatische Updates:
- **Alle 5 Minuten** werden die Nachrichten neu geladen
- **Manuell** über "Aktualisieren" Button
- **Demo-Modus** wenn keine aktuellen Daten

## 🔗 Integration mit Bot:

### Option 1: JSON-Datei
```bash
# daily_news.json vom Bot in Website-Ordner kopieren
cp "Telegram Bot/daily_news.json" "Website/"
```

### Option 2: Live-API
```javascript
// In script.js die URL anpassen
const response = await fetch('https://deine-api.com/news');
```

## 📱 Mobile Optimierung:

- **Touch-Friendly** Buttons und Interaktionen
- **Lesbare Schriftgrößen** auf kleinen Bildschirmen
- **Optimiertes Layout** für Hoch- und Querformat
- **Schnelle Ladezeiten** durch minimale Ressourcen

## 🎨 Anpassungen:

### Farben ändern:
```css
/* In style.css */
:root {
    --primary-color: #667eea;
    --secondary-color: #2c3e50;
    --success-color: #27ae60;
}
```

### Auto-Refresh Intervall:
```javascript
// In script.js
setInterval(() => this.loadNews(), 10 * 60 * 1000); // 10 Minuten
```

## 🌐 Deployment:

### GitHub Pages:
1. Website-Ordner in `docs` umbenennen
2. Zu GitHub pushen
3. GitHub Pages aktivieren

### Netlify/Vercel:
1. Website-Ordner hochladen
2. Build-Einstellungen: Ausgabeverzeichnis `Website`
3. Automatisches Deployment

## 📊 Browser-Kompatibilität:

- ✅ **Chrome 80+**
- ✅ **Firefox 75+**
- ✅ **Safari 13+**
- ✅ **Edge 80+**
- ✅ **Mobile Browser** (iOS Safari, Chrome Mobile)

**Die Website funktioniert auf allen modernen Geräten und Browsern!** 🎉
