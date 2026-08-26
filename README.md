# hAI.LLDesignEtsyScraper

CLI-Tool zum Exportieren von Etsy-Shop-Listings (Titel, Beschreibung, Preis, Bilder, Versand) via Etsy Open API v3.

## Features

- ✅ Interaktives Menü mit `whiptail` (oder reine CLI)
- ✅ Voll konfigurierbar über CLI-Args oder Umgebungsvariablen
- ✅ Container-freundlich (Docker)
- ✅ DietPi-kompatibel (läuft auf ARM/Raspberry Pi)
- ✅ Export als CSV + optionaler Bilder-Download
- ✅ Ideal für Agenten/Automation (alle Parameter über CLI)

## Voraussetzungen

- Python 3.9+
- `requests` Bibliothek
- Optional: `whiptail` für interaktives Menü
- Etsy API-Zugang (API Key, Shared Secret, Access Token, Shop ID)

## Installation

### Lokal (DietPi / Raspberry Pi)

```bash
# Abhängigkeiten installieren
sudo apt-get update
sudo apt-get install -y python3 python3-pip whiptail

# Python-Abhängigkeiten
pip3 install -r requirements.txt

# Skript ausführbar machen
chmod +x etsy-shop-exporter.py
```

### Docker

```bash
# Image bauen
docker build -t etsy-shop-exporter .

# Container starten (interaktiv)
docker run -it --rm \
  -v $(pwd)/etsy_export:/app/etsy_export \
  etsy-shop-exporter

# Container starten (reine CLI mit Args)
docker run -it --rm \
  -v $(pwd)/etsy_export:/app/etsy_export \
  etsy-shop-exporter \
    --api-key YOUR_KEY \
    --shared-secret YOUR_SECRET \
    --access-token YOUR_TOKEN \
    --shop-id 12345678 \
    --download-images
```

## Verwendung

### Interaktiv mit whiptail-Menü

```bash
python3 etsy-shop-exporter.py
```

Das Tool zeigt ein Menü an, in dem du:
- Konfiguration eingeben kannst
- Export starten kannst
- Bilder-Download aktivieren kannst

### Reine CLI (für Agenten/Automation)

```bash
python3 etsy-shop-exporter.py \
  --api-key YOUR_KEY \
  --shared-secret YOUR_SECRET \
  --access-token YOUR_TOKEN \
  --shop-id 12345678 \
  --output-dir ./my_export \
  --download-images \
  --no-menu
```

### Mit Umgebungsvariablen

```bash
export ETSY_API_KEY="your_key"
export ETSY_SHARED_SECRET="your_secret"
export ETSY_ACCESS_TOKEN="your_token"
export ETSY_SHOP_ID="12345678"

python3 etsy-shop-exporter.py --no-menu
```

## Genaue Benutzung (Schritt für Schritt)

### 1. Etsy API-Zugang einrichten

1. **Developer-Portal öffnen:**
   ```bash
   # Im Browser:
   https://www.etsy.com/developers/your-apps
   ```

2. **Neue App erstellen:**
   - Klicke auf „Create a new app"
   - Gib einen Namen ein (z. B. „Mein Etsy Exporter")
   - Akzeptiere die Bedingungen
   - Speichere

3. **API-Zugangsdaten notieren:**
   - **API Key** (keystring)
   - **Shared Secret**

4. **OAuth Access Token holen:**
   - Nutze den Etsy OAuth Flow mit den Scopes:
     - `listings_r` (Listings lesen)
     - `shipping_r` (Versand lesen)
   - Oder nutze das vereinfachte Verfahren für eigene Apps

5. **Shop ID finden:**
   ```bash
   # Gehe zu deinem Shop:
   https://www.etsy.com/de/shop/DEIN_SHOP_NAME
   
   # Die Shop ID ist in der URL:
   # https://www.etsy.com/de/shop/DEIN_SHOP_NAME?ref=hdr_shop_menu
   # Oder im Seller-Dashboard unter Einstellungen
   ```

### 2. Tool starten

#### Interaktiv (empfohlen für den Einstieg)

```bash
python3 etsy-shop-exporter.py
```

Das Menü zeigt:

```
┌─────────────────────────────────────┐
│      Etsy Shop Exporter             │
├─────────────────────────────────────┤
│  Waehle eine Aktion:                │
│  • Export starten                   │
│  • Konfiguration eingeben           │
│  • Beenden                          │
└─────────────────────────────────────┘
```

**Schritte:**
1. Wähle „Konfiguration eingeben"
2. Gib die API-Zugangsdaten ein (API Key, Shared Secret, Access Token, Shop ID)
3. Wähle „Bilder herunterladen" (Ja/Nein)
4. Wähle „Export starten"

#### Reine CLI (für Automation)

```bash
# Minimal (ohne Bilder)
python3 etsy-shop-exporter.py \
  --api-key "dein_api_key" \
  --shared-secret "dein_shared_secret" \
  --access-token "dein_access_token" \
  --shop-id "12345678" \
  --no-menu

# Mit Bildern und eigenem Output-Dir
python3 etsy-shop-exporter.py \
  --api-key "dein_api_key" \
  --shared-secret "dein_shared_secret" \
  --access-token "dein_access_token" \
  --shop-id "12345678" \
  --output-dir ./mein_export \
  --download-images \
  --no-menu
```

#### Mit Umgebungsvariablen (für Cron/CI)

```bash
# .env Datei erstellen
cp example.env .env

# .env bearbeiten
nano .env

# Inhalt:
ETSY_API_KEY=dein_api_key
ETSY_SHARED_SECRET=dein_shared_secret
ETSY_ACCESS_TOKEN=dein_access_token
ETSY_SHOP_ID=12345678
ETSY_OUTPUT_DIR=./etsy_export
ETSY_DOWNLOAD_IMAGES=1

# Umgebungsvariablen laden
source .env

# Tool starten
python3 etsy-shop-exporter.py --no-menu
```

### 3. Export auswerten

Nach erfolgreicher Ausführung:

```
etsy_export/
├── listings.csv          # CSV mit allen Produktdaten
└── images/               # (optional) Bilder-Ordner
    ├── 1234567890/       # Listing-ID
    │   ├── image_000.jpg # Hauptbild
    │   ├── image_001.jpg # Zweites Bild
    │   └── ...
    └── ...
```

**CSV-Datei lesen:**

```python
import csv

with open("etsy_export/listings.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"Titel: {row['title']}")
        print(f"Preis: {row['price']} {row['currency_code']}")
        print(f"Bilder: {row['image_urls'].split('|')}")
        print("---")
```

### 4. Für Telegram-Shop-Import vorbereiten

Die CSV enthält alle benötigten Felder:

| Telegram-Shop-Feld | CSV-Spalte |
|-------------------|-----------|
| `title` | `title` |
| `description` | `description` |
| `price` | `price` |
| `currency` | `currency_code` |
| `image_url` | `image_urls` (erste URL) |
| `shipping_cost` | `shipping_cost` |
| `shipping_currency` | `shipping_currency` |

## CLI-Argumente (vollständig)

| Argument | Typ | Default | Beschreibung |
|----------|-----|---------|-------------|
| `--api-key` | String | - | Etsy API Key (keystring) |
| `--shared-secret` | String | - | Etsy Shared Secret |
| `--access-token` | String | - | OAuth Access Token |
| `--shop-id` | String | - | Etsy Shop ID |
| `--output-dir` | Path | `./etsy_export` | Ausgabeverzeichnis |
| `--download-images` | Flag | `False` | Bilder herunterladen |
| `--batch-size` | Integer | `250` | Listings pro API-Request |
| `--no-menu` | Flag | `False` | Kein whiptail-Menü, nur CLI |

## Umgebungsvariablen

| Variable | Beschreibung |
|----------|-------------|
| `ETSY_API_KEY` | Etsy API Key |
| `ETSY_SHARED_SECRET` | Etsy Shared Secret |
| `ETSY_ACCESS_TOKEN` | Etsy OAuth Access Token |
| `ETSY_SHOP_ID` | Etsy Shop ID |
| `ETSY_OUTPUT_DIR` | Ausgabeverzeichnis |
| `ETSY_DOWNLOAD_IMAGES` | `1` = Bilder herunterladen, `0` = nein |

## Docker-Nutzung

### Image bauen

```bash
docker build -t etsy-shop-exporter .
```

### Container starten

**Interaktiv (mit Menü):**

```bash
docker run -it --rm \
  -v $(pwd)/etsy_export:/app/etsy_export \
  etsy-shop-exporter
```

**Reine CLI (für Automation):**

```bash
docker run -it --rm \
  -v $(pwd)/etsy_export:/app/etsy_export \
  -e ETSY_API_KEY="dein_api_key" \
  -e ETSY_SHARED_SECRET="dein_shared_secret" \
  -e ETSY_ACCESS_TOKEN="dein_access_token" \
  -e ETSY_SHOP_ID="12345678" \
  -e ETSY_DOWNLOAD_IMAGES="1" \
  etsy-shop-exporter \
    --no-menu
```

### Docker Compose

```bash
# .env Datei erstellen
cp example.env .env
nano .env  # Werte eintragen

# Starten
docker-compose up
```

## Beispiel: Cron-Job (täglicher Export)

```bash
# Crontab bearbeiten
crontab -e

# Täglich um 3:00 Uhr exportieren
0 3 * * * /usr/bin/python3 /path/to/etsy-shop-exporter.py \
  --api-key "dein_api_key" \
  --shared-secret "dein_shared_secret" \
  --access-token "dein_access_token" \
  --shop-id "12345678" \
  --output-dir /path/to/export \
  --no-menu >> /var/log/etsy-export.log 2>&1
```

## Troubleshooting

| Problem | Lösung |
|---------|--------|
| `401 Unauthorized` | Access Token ungültig/abgelaufen → neu generieren |
| `403 Forbidden` | Falsche Scopes → `listings_r`, `shipping_r` prüfen |
| `429 Too Many Requests` | Rate Limit erreicht → warten oder `--batch-size` reduzieren |
| `whiptail: command not found` | Tool ist nicht installiert → `--no-menu` verwenden |
| `CSV leer` | Shop hat keine Listings oder API-Zugriff fehlt |

## Lizenz

MIT