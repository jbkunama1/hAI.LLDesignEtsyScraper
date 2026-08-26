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

## CLI-Argumente

| Argument | Beschreibung |
|----------|-------------|
| `--api-key` | Etsy API Key (keystring) |
| `--shared-secret` | Etsy Shared Secret |
| `--access-token` | Etsy OAuth Access Token |
| `--shop-id` | Etsy Shop ID |
| `--output-dir` | Ausgabeverzeichnis (Default: `./etsy_export`) |
| `--download-images` | Bilder herunterladen (Default: nein) |
| `--batch-size` | Listings pro API-Request (Default: 250) |
| `--no-menu` | Kein whiptail-Menü, nur CLI |

## Umgebungsvariablen

| Variable | Beschreibung |
|----------|-------------|
| `ETSY_API_KEY` | Etsy API Key |
| `ETSY_SHARED_SECRET` | Etsy Shared Secret |
| `ETSY_ACCESS_TOKEN` | Etsy OAuth Access Token |
| `ETSY_SHOP_ID` | Etsy Shop ID |
| `ETSY_OUTPUT_DIR` | Ausgabeverzeichnis |
| `ETSY_DOWNLOAD_IMAGES` | `1` = Bilder herunterladen, `0` = nein |

## Ausgabe

Nach dem Export findest du im Ausgabeverzeichnis:

```
etsy_export/
├── listings.csv          # Alle Listings als CSV
└── images/               # (optional) Bilder-Ordner
    ├── 12345678/         # Bilder pro Listing-ID
    │   ├── image_000.jpg
    │   ├── image_001.jpg
    │   └── ...
    └── ...
```

### CSV-Spalten

| Spalte | Beschreibung |
|--------|-------------|
| `listing_id` | Etsy Listing ID |
| `title` | Titel des Produkts |
| `description` | Beschreibung |
| `price` | Preis |
| `currency_code` | Währung (z.B. EUR) |
| `quantity` | Verfügbare Menge |
| `tags` | Tags (durch `|` getrennt) |
| `materials` | Materialien (durch `|` getrennt) |
| `category_path` | Kategorie-Pfad |
| `sku_values` | SKU-Werte |
| `shipping_profile_id` | Versandprofil-ID |
| `shipping_cost` | Versandkosten |
| `shipping_currency` | Währung der Versandkosten |
| `image_urls` | Bild-URLs (durch `|` getrennt) |
| `url` | Etsy-Listing-URL |

## Etsy API Zugang

1. Gehe zu https://www.etsy.com/developers/your-apps
2. Erstelle eine neue App ("Create a new app")
3. Notiere API Key und Shared Secret
4. Hole einen OAuth Access Token mit den Scopes:
   - `listings_r` (Listings lesen)
   - `shipping_r` (Versand lesen)
5. Finde deine Shop ID unter https://www.etsy.com/de/sell

## Beispiel: Cron-Job (täglicher Export)

```bash
# Crontab bearbeiten
crontab -e

# Täglich um 3:00 Uhr exportieren
0 3 * * * /usr/bin/python3 /path/to/etsy-shop-exporter.py \
  --api-key YOUR_KEY \
  --shared-secret YOUR_SECRET \
  --access-token YOUR_TOKEN \
  --shop-id 12345678 \
  --output-dir /path/to/export \
  --no-menu >> /var/log/etsy-export.log 2>&1
```

## Lizenz

MIT