#!/usr/bin/env python3
"""
Etsy Export Agent - Vollautomatischer Export

Dieses Skript demonstriert, wie ein Agent das Tool programmatisch steuern kann.
Alle Konfigurationswerte werden aus Umgebungsvariablen gelesen.

Verwendung:
  export ETSY_API_KEY="..."
  export ETSY_SHARED_SECRET="..."
  export ETSY_ACCESS_TOKEN="..."
  export ETSY_SHOP_ID="..."
  python3 example-agent.py
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def log(msg: str, level: str = "INFO"):
    """Log-Ausgabe mit Timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {msg}")


def validate_config(config: dict) -> list:
    """
    Validiert die Konfiguration und gibt fehlende Parameter zurueck.
    """
    required = ["api_key", "shared_secret", "access_token", "shop_id"]
    return [k for k in required if not config.get(k)]


def build_command(config: dict) -> list:
    """
    Baut den CLI-Befehl aus der Konfiguration.
    """
    cmd = [
        "python3", "etsy-shop-exporter.py",
        "--api-key", config["api_key"],
        "--shared-secret", config["shared_secret"],
        "--access-token", config["access_token"],
        "--shop-id", config["shop_id"],
        "--output-dir", config["output_dir"],
        "--no-menu"
    ]
    
    if config.get("download_images"):
        cmd.append("--download-images")
    
    if config.get("batch_size"):
        cmd.extend(["--batch-size", str(config["batch_size"])])
    
    return cmd


def main():
    log("Etsy Export Agent gestartet")
    
    # Konfiguration aus Umgebungsvariablen
    config = {
        "api_key": os.getenv("ETSY_API_KEY"),
        "shared_secret": os.getenv("ETSY_SHARED_SECRET"),
        "access_token": os.getenv("ETSY_ACCESS_TOKEN"),
        "shop_id": os.getenv("ETSY_SHOP_ID"),
        "output_dir": os.getenv("ETSY_OUTPUT_DIR", "./etsy_export"),
        "download_images": os.getenv("ETSY_DOWNLOAD_IMAGES", "0") == "1",
        "batch_size": int(os.getenv("ETSY_BATCH_SIZE", "250")) if os.getenv("ETSY_BATCH_SIZE") else 250
    }
    
    # Parameter validieren
    missing = validate_config(config)
    if missing:
        log(f"Fehlende Parameter: {missing}", "ERROR")
        log("Bitte setze folgende Umgebungsvariablen:", "ERROR")
        for param in missing:
            log(f"  ETSY_{param.upper().replace('_', '_')}", "ERROR")
        sys.exit(2)
    
    log(f"Konfiguration geladen:")
    log(f"  API Key: {config['api_key'][:8]}...")
    log(f"  Shop ID: {config['shop_id']}")
    log(f"  Output Dir: {config['output_dir']}")
    log(f"  Bilder herunterladen: {config['download_images']}")
    log(f"  Batch Size: {config['batch_size']}")
    
    # CLI-Befehl bauen
    cmd = build_command(config)
    log(f"Starte Export: {' '.join(cmd)}")
    
    # Export ausfuhren
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        # stdout ausgeben
        if result.stdout:
            for line in result.stdout.strip().split("\n"):
                log(f"Tool: {line}")
        
        # stderr ausgeben (als WARN oder ERROR)
        if result.stderr:
            for line in result.stderr.strip().split("\n"):
                log(f"Tool (STDERR): {line}", "WARN")
        
        # Return Code pruefen
        if result.returncode != 0:
            log(f"Export fehlgeschlagen (Return Code: {result.returncode})", "ERROR")
            sys.exit(result.returncode)
        
        # Erfolg - CSV-Datei pruefen
        output_path = Path(config["output_dir"])
        csv_file = output_path / "listings.csv"
        
        if csv_file.exists():
            # CSV-Statistiken
            with csv_file.open("r", encoding="utf-8") as f:
                lines = f.readlines()
                listing_count = len(lines) - 1  # Ohne Kopfzeile
            
            log(f"Export erfolgreich!", "SUCCESS")
            log(f"  CSV-Datei: {csv_file}")
            log(f"  Listings exportiert: {listing_count}")
            
            # Bilder-Ordner pruefen
            if config["download_images"]:
                images_dir = output_path / "images"
                if images_dir.exists():
                    image_count = sum(1 for _ in images_dir.rglob("*.jpg"))
                    log(f"  Bilder heruntergeladen: {image_count}")
        else:
            log("CSV-Datei nicht gefunden!", "ERROR")
            sys.exit(1)
        
    except FileNotFoundError:
        log("etsy-shop-exporter.py nicht gefunden!", "ERROR")
        log("Stelle sicher, dass das Skript im aktuellen Verzeichnis liegt.", "ERROR")
        sys.exit(1)
    except Exception as e:
        log(f"Unerwarteter Fehler: {e}", "ERROR")
        sys.exit(1)
    
    log("Agent beendet")
    sys.exit(0)


if __name__ == "__main__":
    main()