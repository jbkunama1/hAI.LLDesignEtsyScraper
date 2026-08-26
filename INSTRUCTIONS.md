# Etsy Shop Exporter – Agent Instructions

Diese Anleitung richtet sich an **Agenten** (KI-Assistenten, Automation-Skripte, CI/CD-Pipelines), die das Tool programmatisch steuern sollen.

---

## 📋 Quick Start für Agenten

### 1. Voraussetzungen prüfen

Stelle sicher, dass folgende Werte verfügbar sind:

| Variable | Beschreibung | Quelle |
|----------|-------------|--------|
| `ETSY_API_KEY` | Etsy API Key (keystring) | Etsy Developer Portal |
| `ETSY_SHARED_SECRET` | Etsy Shared Secret | Etsy Developer Portal |
| `ETSY_ACCESS_TOKEN` | OAuth 2.0 Access Token | Etsy OAuth Flow |
| `ETSY_SHOP_ID` | Shop-ID (numerisch) | Etsy Shop-URL oder API |

### 2. Tool ausfuhren (CLI-Modus)

```bash
python3 etsy-shop-exporter.py \
  --api-key "$ETSY_API_KEY" \
  --shared-secret "$ETSY_SHARED_SECRET" \
  --access-token "$ETSY_ACCESS_TOKEN" \
  --shop-id "$ETSY_SHOP_ID" \
  --output-dir "/path/to/output" \
  --download-images \
  --no-menu
```

### 3. Ausgabe prüfen

Nach erfolgreicher Ausführung:

```
/path/to/output/
├── listings.csv          # Hauptdaten (CSV, UTF-8)
└── images/               # Bilder-Ordner (optional)
    ├── <listing_id>/
    │   ├── image_000.jpg
    │   ├── image_001.jpg
    │   └── ...
```

---

## 📊 CSV-Format (listings.csv)

Die CSV-Datei ist **UTF-8 kodiert**, mit Kopfzeile und folgenden Spalten:

| Spalte | Typ | Beschreibung | Beispiel |
|--------|-----|-------------|----------|
| `listing_id` | Integer | Etsy Listing-ID | `1234567890` |
| `title` | String | Produkttitel | `Handgemachte Keramik Tasse` |
| `description` | String | Produktbeschreibung (HTML-frei) | `Wunderschone Tasse aus...` |
| `price` | Float | Preis | `24.99` |
| `currency_code` | String | Wahrung | `EUR` |
| `quantity` | Integer | Verfuugbare Menge | `5` |
| `tags` | String | Tags (durch `|` getrennt) | `keramik|tasse|handmade` |
| `materials` | String | Materialien (durch `|` getrennt) | `ton|glasur` |
| `category_path` | String | Kategorie-Pfad (durch ` > ` getrennt) | `Kunst & Sammler > Keramik` |
| `sku_values` | String | SKU-Werte (durch `|` getrennt) | `KER-TASSE-001` |
| `shipping_profile_id` | Integer | Versandprofil-ID | `98765432` |
| `shipping_cost` | Float | Versandkosten | `4.99` |
| `shipping_currency` | String | Wahrung der Versandkosten | `EUR` |
| `image_urls` | String | Bild-URLs (durch `|` getrennt) | `https://...|https://...` |
| `url` | String | Etsy-Listing-URL | `https://etsy.com/de/listing/...` |

### CSV lesen (Python-Beispiel)

```python
import csv

with open("listings.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"Listing {row['listing_id']}: {row['title']} - {row['price']} {row['currency_code']}")
```

---

## 🖼️ Bilder-Ordnerstruktur

Wenn `--download-images` aktiviert ist:

```
images/
├── 1234567890/           # Listing-ID als Ordnername
│   ├── image_000.jpg     # Erstes Bild (Hauptbild)
│   ├── image_001.jpg     # Zweites Bild
│   ├── image_002.jpg
│   └── ...
├── 1234567891/
│   └── ...
└── ...
```

### Bild-Zuordnung

- Ordnername = `listing_id` aus der CSV
- Dateiname = `image_XXX.ext` (fortlaufend nummeriert)
- `image_000.jpg` ist in der Regel das Hauptbild (Reihenfolge wie in Etsy)

---

## 🔧 CLI-Argumente (vollstandig)

| Argument | Typ | Default | Beschreibung |
|----------|-----|---------|-------------|
| `--api-key` | String | - | Etsy API Key (keystring) |
| `--shared-secret` | String | - | Etsy Shared Secret |
| `--access-token` | String | - | OAuth Access Token |
| `--shop-id` | String | - | Etsy Shop ID |
| `--output-dir` | Path | `./etsy_export` | Ausgabeverzeichnis |
| `--download-images` | Flag | `False` | Bilder herunterladen |
| `--batch-size` | Integer | `250` | Listings pro API-Request |
| `--no-menu` | Flag | `False` | Kein whiptail-Menue |

---

## 🌍 Umgebungsvariablen (Alternative)

Alle CLI-Argumente können auch als Umgebungsvariablen gesetzt werden:

| Variable | Entspricht | Beispiel |
|----------|-----------|----------|
| `ETSY_API_KEY` | `--api-key` | `your_key` |
| `ETSY_SHARED_SECRET` | `--shared-secret` | `your_secret` |
| `ETSY_ACCESS_TOKEN` | `--access-token` | `your_token` |
| `ETSY_SHOP_ID` | `--shop-id` | `12345678` |
| `ETSY_OUTPUT_DIR` | `--output-dir` | `/app/etsy_export` |
| `ETSY_DOWNLOAD_IMAGES` | `--download-images` | `1` oder `0` |

### Beispiel (Shell)

```bash
export ETSY_API_KEY="your_key"
export ETSY_SHARED_SECRET="your_secret"
export ETSY_ACCESS_TOKEN="your_token"
export ETSY_SHOP_ID="12345678"
export ETSY_OUTPUT_DIR="/app/etsy_export"
export ETSY_DOWNLOAD_IMAGES="1"

python3 etsy-shop-exporter.py --no-menu
```

---

## 🐳 Docker-Nutzung für Agenten

### Image bauen

```bash
docker build -t etsy-shop-exporter:latest .
```

### Container ausfuhren (CLI-Modus)

```bash
docker run -it --rm \
  -v /host/output:/app/etsy_export \
  -e ETSY_API_KEY="your_key" \
  -e ETSY_SHARED_SECRET="your_secret" \
  -e ETSY_ACCESS_TOKEN="your_token" \
  -e ETSY_SHOP_ID="12345678" \
  -e ETSY_DOWNLOAD_IMAGES="1" \
  etsy-shop-exporter:latest \
    --no-menu
```

### Docker Compose (Automation)

```yaml
# docker-compose.agent.yml
version: '3.8'

services:
  etsy-exporter:
    image: etsy-shop-exporter:latest
    container_name: etsy-exporter
    volumes:
      - /host/output:/app/etsy_export
    environment:
      - ETSY_API_KEY=${ETSY_API_KEY}
      - ETSY_SHARED_SECRET=${ETSY_SHARED_SECRET}
      - ETSY_ACCESS_TOKEN=${ETSY_ACCESS_TOKEN}
      - ETSY_SHOP_ID=${ETSY_SHOP_ID}
      - ETSY_DOWNLOAD_IMAGES=${ETSY_DOWNLOAD_IMAGES:-0}
    command: ["--no-menu"]
```

Starten:
```bash
docker-compose -f docker-compose.agent.yml up
```

---

## 📝 Return Codes

| Code | Bedeutung |
|------|----------|
| `0` | Erfolgreich abgeschlossen |
| `1` | Allgemeiner Fehler (API, Netzwerk, etc.) |
| `2` | Konfigurationsfehler (fehlende Parameter) |

### Beispiel (Shell)

```bash
if python3 etsy-shop-exporter.py --no-menu; then
  echo "Export erfolgreich"
else
  echo "Export fehlgeschlagen" >&2
  exit 1
fi
```

---

## 🔄 Typische Agenten-Workflows

### 1. Tglicher Export (Cron)

```bash
# Crontab
0 3 * * * /usr/bin/python3 /opt/etsy-shop-exporter/etsy-shop-exporter.py \
  --api-key "$ETSY_API_KEY" \
  --shared-secret "$ETSY_SHARED_SECRET" \
  --access-token "$ETSY_ACCESS_TOKEN" \
  --shop-id "$ETSY_SHOP_ID" \
  --output-dir "/data/etsy_export" \
  --no-menu >> /var/log/etsy-export.log 2>&1
```

### 2. GitHub Actions (CI/CD)

```yaml
# .github/workflows/etsy-export.yml
name: Etsy Export

on:
  schedule:
    - cron: '0 3 * * *'  # Täglich um 3:00 UTC
  workflow_dispatch:

jobs:
  export:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build Docker Image
        run: docker build -t etsy-shop-exporter .
      
      - name: Run Export
        run: |
          docker run -it --rm \
            -v $(pwd)/output:/app/etsy_export \
            -e ETSY_API_KEY=${{ secrets.ETSY_API_KEY }} \
            -e ETSY_SHARED_SECRET=${{ secrets.ETSY_SHARED_SECRET }} \
            -e ETSY_ACCESS_TOKEN=${{ secrets.ETSY_ACCESS_TOKEN }} \
            -e ETSY_SHOP_ID=${{ secrets.ETSY_SHOP_ID }} \
            etsy-shop-exporter --no-menu
      
      - name: Upload CSV
        uses: actions/upload-artifact@v4
        with:
          name: etsy-listings
          path: output/listings.csv
```

### 3. Python-Agent (vollstandiges Beispiel)

```python
#!/usr/bin/env python3
"""
Etsy Export Agent - Vollautomatischer Export
"""

import os
import subprocess
import sys
from pathlib import Path

def main():
    # Konfiguration aus Umgebungsvariablen
    config = {
        "api_key": os.getenv("ETSY_API_KEY"),
        "shared_secret": os.getenv("ETSY_SHARED_SECRET"),
        "access_token": os.getenv("ETSY_ACCESS_TOKEN"),
        "shop_id": os.getenv("ETSY_SHOP_ID"),
        "output_dir": os.getenv("ETSY_OUTPUT_DIR", "./etsy_export"),
        "download_images": os.getenv("ETSY_DOWNLOAD_IMAGES", "0") == "1"
    }
    
    # Parameter validieren
    required = ["api_key", "shared_secret", "access_token", "shop_id"]
    missing = [k for k in required if not config.get(k)]
    if missing:
        print(f"Fehlende Parameter: {missing}", file=sys.stderr)
        sys.exit(2)
    
    # CLI-Argumente bauen
    cmd = [
        "python3", "etsy-shop-exporter.py",
        "--api-key", config["api_key"],
        "--shared-secret", config["shared_secret"],
        "--access-token", config["access_token"],
        "--shop-id", config["shop_id"],
        "--output-dir", config["output_dir"],
        "--no-menu"
    ]
    
    if config["download_images"]:
        cmd.append("--download-images")
    
    # Ausfuhren
    print(f"Starte Export: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Log-Ausgabe
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    # Return Code prufen
    if result.returncode != 0:
        print(f"Export fehlgeschlagen (Code: {result.returncode})", file=sys.stderr)
        sys.exit(result.returncode)
    
    # Erfolg
    output_path = Path(config["output_dir"])
    csv_file = output_path / "listings.csv"
    
    if csv_file.exists():
        print(f"Export erfolgreich: {csv_file}")
        sys.exit(0)
    else:
        print("CSV-Datei nicht gefunden!", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## 📌 Best Practices für Agenten

1. **Logging aktivieren**
   - stdout/stderr des Tools in Log-Dateien umleiten
   - Beispiel: `>> /var/log/etsy-export.log 2>&1`

2. **Fehlerbehandlung**
   - Return Codes prüfen (0 = Erfolg)
   - Bei Fehlern: Retry-Logik mit Backoff implementieren

3. **Idempotenz**
   - Output-Dir bei jedem Run leeren oder timestamped Subdirs verwenden
   - Beispiel: `--output-dir ./etsy_export_$(date +%Y%m%d_%H%M%S)`

4. **Sicherheit**
   - API-Credentials nicht im Code hardcoden
   - Umgebungsvariablen oder Secret-Manager verwenden

5. **Ressourcen schonen**
   - `--batch-size` anpassen (Default: 250)
   - Bei vielen Listings: Pagination im Auge behalten

---

## 🆘 Troubleshooting

| Problem | Lösung |
|---------|--------|
| `401 Unauthorized` | Access Token ungultig/abgelaufen → neu generieren |
| `403 Forbidden` | Falsche Scopes → `listings_r`, `shipping_r` prufen |
| `429 Too Many Requests` | Rate Limit erreicht → warten oder `--batch-size` reduzieren |
| `whiptail: command not found` | Tool ist nicht installiert → `--no-menu` verwenden |
| `CSV leer` | Shop hat keine Listings oder API-Zugriff fehlt |

---

## 📞 Support

Bei Fragen oder Problemen:

1. Logs prüfen (stdout/stderr)
2. API-Credentials validieren (Etsy Developer Portal)
3. Netzwerkverbindung testen (`curl https://openapi.etsy.com/v3/application`)
4. Issue im Repository erstellen (falls vorhanden)

---

**Letzte Aktualisierung:** 2026-08-27  
**Version:** 1.0.0