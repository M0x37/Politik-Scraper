# 📧 E-Mail-Benachrichtigung einrichten

## 1. GitHub Secrets einrichten

Gehe zu deinem GitHub Repository → Settings → Secrets and variables → Actions

Füge diese 3 Secrets hinzu:

### `EMAIL_USERNAME`
Deine Gmail-Adresse (z.B. `deine.email@gmail.com`)

### `EMAIL_PASSWORD`
**Wichtig:** Verwende ein "App Password", nicht dein normales Passwort!

**App Password erstellen:**
1. Google Konto → Sicherheit
2. 2-Faktor-Authentifizierung aktivieren (falls nicht schon)
3. "App-Passwörter" → "Neues App-Passwort"
4. App auswählen: "Andere (benutzerdefinierter Name)"
5. Name eingeben: "Politik Scraper"
6. 16-stelliges Passwort kopieren

### `RECIPIENT_EMAIL`
Die E-Mail-Adresse, die die Nachrichten erhalten soll

## 2. Alternative: Andere E-Mail-Anbieter

### Outlook/Hotmail:
```yaml
server_address: smtp-mail.outlook.com
server_port: 587
```

### GMX:
```yaml
server_address: mail.gmx.net
server_port: 587
```

### Web.de:
```yaml
server_address: smtp.web.de
server_port: 587
```

## 3. Testen

1. Repository zu GitHub pushen
2. Actions → Daily News Scraper → "Run workflow"
3. Prüfen ob E-Mail ankommt

## 4. Automatisierung

Nach erfolgreichem Test läuft der Workflow automatisch täglich um 20:00 Berlin Zeit.
