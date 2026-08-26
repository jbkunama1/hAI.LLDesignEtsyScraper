#!/usr/bin/env python3
"""
Etsy Shop Exporter - CLI Tool
Exportiert Listings, Bilder und Versandinfos von Etsy via API v3.

Features:
- Interaktives Menü mit whiptail (oder reine CLI mit Args)
- Container- und DietPi-freundlich
- Export als CSV + optionaler Bilder-Download
- Voll konfigurierbar über Umgebungsvariablen oder CLI-Args
"""

import argparse
import csv
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import requests

# ─────────────────────────────────────────────────────────────
# Konfiguration
# ─────────────────────────────────────────────────────────────

DEFAULT_OUTPUT_DIR = Path("./etsy_export")
DEFAULT_BATCH_SIZE = 250  # Max Listings pro API-Request

# ─────────────────────────────────────────────────────────────
# Hilfsfunktionen
# ─────────────────────────────────────────────────────────────


def log(msg: str, level: str = "INFO"):
    """Log-Ausgabe mit Level."""
    print(f"[{level}] {msg}")


def run_whiptail(title: str, text: str, options: list) -> Optional[str]:
    """
    Fuhrt whiptail aus und gibt die Auswahl zurueck.
    options: Liste von Tupeln (tag, item)
    """
    if not os.path.exists("/usr/bin/whiptail"):
        log("whiptail nicht gefunden, verwende reine CLI", "WARN")
        return None

    cmd = [
        "whiptail",
        "--title", title,
        "--menu", text,
        "20", "70", "10"
    ]
    for tag, item in options:
        cmd.extend([tag, item])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:  # User abgebrochen
            log("Abbruch durch User", "WARN")
        else:
            log(f"whiptail Fehler: {e}", "ERROR")
        return None


def input_whiptail(title: str, prompt: str, default: str = "") -> Optional[str]:
    """
    Eingabefeld mit whiptail.
    """
    if not os.path.exists("/usr/bin/whiptail"):
        return None

    cmd = [
        "whiptail",
        "--title", title,
        "--inputbox", prompt,
        "10", "70",
        default
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


# ─────────────────────────────────────────────────────────────
# Etsy API Client
# ─────────────────────────────────────────────────────────────


class EtsyAPIClient:
    def __init__(self, api_key: str, shared_secret: str, access_token: str, shop_id: str):
        self.api_key = api_key
        self.shared_secret = shared_secret
        self.access_token = access_token
        self.shop_id = shop_id
        self.base_url = "https://openapi.etsy.com/v3/application"

    def _headers(self) -> dict:
        return {
            "x-api-key": f"{self.api_key}:{self.shared_secret}",
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }

    def get_listings(self, limit: int = DEFAULT_BATCH_SIZE, offset: int = 0) -> dict:
        """
        Holt Listings fuer den Shop.
        """
        url = f"{self.base_url}/shops/{self.shop_id}/listings"
        params = {"limit": limit, "offset": offset}
        resp = requests.get(url, headers=self._headers(), params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_shipping_profiles(self) -> dict:
        """
        Holt alle Versandprofile des Shops.
        """
        url = f"{self.base_url}/shops/{self.shop_id}/shipping-profiles"
        resp = requests.get(url, headers=self._headers(), timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_batch_shipping(self, listing_ids: list) -> dict:
        """
        Holt Versandinfos fuer mehrere Listings auf einmal.
        """
        url = f"{self.base_url}/listings/batch/shipping"
        params = {"listing_ids": ",".join(map(str, listing_ids))}
        resp = requests.get(url, headers=self._headers(), params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()


# ─────────────────────────────────────────────────────────────
# Export-Logik
# ─────────────────────────────────────────────────────────────


def download_images(images: list, output_dir: Path, listing_id: str):
    """
    Laedt alle Bilder eines Listings herunter.
    """
    images_dir = output_dir / "images" / str(listing_id)
    images_dir.mkdir(parents=True, exist_ok=True)

    for i, img in enumerate(images):
        url = img.get("url_570xN") or img.get("url_1140xN") or img.get("url_original")
        if not url:
            continue
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            ext = Path(url).suffix or ".jpg"
            file_path = images_dir / f"image_{i:03d}{ext}"
            file_path.write_bytes(resp.content)
            log(f"Bild gespeichert: {file_path}")
        except Exception as e:
            log(f"Fehler beim Bild-Download: {e}", "ERROR")


def export_listings_to_csv(listings: list, shipping_data: dict, output_file: Path):
    """
    Schreibt Listings als CSV.
    """
    if not listings:
        log("Keine Listings zum Exportieren", "WARN")
        return

    fieldnames = [
        "listing_id",
        "title",
        "description",
        "price",
        "currency_code",
        "quantity",
        "tags",
        "materials",
        "category_path",
        "sku_values",
        "shipping_profile_id",
        "shipping_cost",
        "shipping_currency",
        "image_urls",
        "url"
    ]

    with output_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for listing in listings:
            shipping_info = shipping_data.get(str(listing["listing_id"]), {})
            row = {
                "listing_id": listing["listing_id"],
                "title": listing.get("title", ""),
                "description": listing.get("description", ""),
                "price": listing.get("price", ""),
                "currency_code": listing.get("currency_code", ""),
                "quantity": listing.get("quantity", ""),
                "tags": "|".join(listing.get("tags", [])),
                "materials": "|".join(listing.get("materials", [])),
                "category_path": " > ".join(listing.get("category_path", [])),
                "sku_values": "|".join(listing.get("sku_values", [])),
                "shipping_profile_id": listing.get("shipping_profile_id", ""),
                "shipping_cost": shipping_info.get("primary_profile", {}).get("price", ""),
                "shipping_currency": shipping_info.get("primary_profile", {}).get("currency_code", ""),
                "image_urls": "|".join([img.get("url_570xN") or img.get("url_original") or "" for img in listing.get("images", [])]),
                "url": listing.get("url", "")
            }
            writer.writerow(row)

    log(f"CSV gespeichert: {output_file}")


# ─────────────────────────────────────────────────────────────
# Hauptlogik
# ─────────────────────────────────────────────────────────────


def parse_args():
    parser = argparse.ArgumentParser(
        description="Etsy Shop Exporter - CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiel (reine CLI):
  python etsy-shop-exporter.py \\
    --api-key YOUR_KEY \\
    --shared-secret YOUR_SECRET \\
    --access-token YOUR_TOKEN \\
    --shop-id 12345678 \\
    --output-dir ./export \\
    --download-images

Umgebungsvariablen (optional):
  ETSY_API_KEY, ETSY_SHARED_SECRET, ETSY_ACCESS_TOKEN, ETSY_SHOP_ID
        """
    )

    parser.add_argument("--api-key", type=str, help="Etsy API Key (keystring)")
    parser.add_argument("--shared-secret", type=str, help="Etsy Shared Secret")
    parser.add_argument("--access-token", type=str, help="Etsy OAuth Access Token")
    parser.add_argument("--shop-id", type=str, help="Etsy Shop ID")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Ausgabeverzeichnis")
    parser.add_argument("--download-images", action="store_true", help="Bilder herunterladen")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help="Listings pro Batch")
    parser.add_argument("--no-menu", action="store_true", help="Kein whiptail-Menue, nur CLI")

    return parser.parse_args()


def get_config_interactive(args) -> dict:
    """
    Holt Konfiguration interaktiv via whiptail oder CLI-Input.
    """
    config = {}

    # API Key
    if args.api_key:
        config["api_key"] = args.api_key
    else:
        config["api_key"] = os.getenv("ETSY_API_KEY") or input("Etsy API Key: ").strip()

    # Shared Secret
    if args.shared_secret:
        config["shared_secret"] = args.shared_secret
    else:
        config["shared_secret"] = os.getenv("ETSY_SHARED_SECRET") or input("Etsy Shared Secret: ").strip()

    # Access Token
    if args.access_token:
        config["access_token"] = args.access_token
    else:
        config["access_token"] = os.getenv("ETSY_ACCESS_TOKEN") or input("Etsy Access Token: ").strip()

    # Shop ID
    if args.shop_id:
        config["shop_id"] = args.shop_id
    else:
        config["shop_id"] = os.getenv("ETSY_SHOP_ID") or input("Etsy Shop ID: ").strip()

    # Output Dir
    if args.output_dir:
        config["output_dir"] = args.output_dir
    else:
        output_input = input(f"Ausgabeverzeichnis [{DEFAULT_OUTPUT_DIR}]: ").strip()
        config["output_dir"] = Path(output_input) if output_input else DEFAULT_OUTPUT_DIR

    # Bilder herunterladen?
    config["download_images"] = args.download_images
    if not args.download_images:
        dl_input = input("Bilder herunterladen? (y/n) [n]: ").strip().lower()
        config["download_images"] = dl_input == "y"

    return config


def main():
    args = parse_args()

    log("Etsy Shop Exporter gestartet")

    # Konfiguration holen
    if not args.no_menu and os.path.exists("/usr/bin/whiptail"):
        # Whiptail-Menue
        while True:
            choice = run_whiptail(
                "Etsy Shop Exporter",
                "Waehle eine Aktion:",
                [
                    ("start", "Export starten"),
                    ("config", "Konfiguration eingeben"),
                    ("quit", "Beenden")
                ]
            )

            if choice == "quit" or choice is None:
                log("Beende Programm")
                sys.exit(0)

            if choice == "config":
                # Konfiguration eingeben
                api_key = input_whiptail("Konfiguration", "Etsy API Key:", os.getenv("ETSY_API_KEY", "")) or ""
                shared_secret = input_whiptail("Konfiguration", "Etsy Shared Secret:", os.getenv("ETSY_SHARED_SECRET", "")) or ""
                access_token = input_whiptail("Konfiguration", "Etsy Access Token:", os.getenv("ETSY_ACCESS_TOKEN", "")) or ""
                shop_id = input_whiptail("Konfiguration", "Etsy Shop ID:", os.getenv("ETSY_SHOP_ID", "")) or ""
                output_dir = input_whiptail("Konfiguration", "Ausgabeverzeichnis:", str(DEFAULT_OUTPUT_DIR)) or str(DEFAULT_OUTPUT_DIR)
                dl_images = run_whiptail(
                    "Konfiguration",
                    "Bilder herunterladen?",
                    [("yes", "Ja"), ("no", "Nein")]
                )

                # Als Umgebungsvariablen speichern (fuer naechste Runs)
                os.environ["ETSY_API_KEY"] = api_key
                os.environ["ETSY_SHARED_SECRET"] = shared_secret
                os.environ["ETSY_ACCESS_TOKEN"] = access_token
                os.environ["ETSY_SHOP_ID"] = shop_id
                os.environ["ETSY_OUTPUT_DIR"] = output_dir
                os.environ["ETSY_DOWNLOAD_IMAGES"] = "1" if dl_images == "yes" else "0"

                log("Konfiguration gespeichert")
                continue

            if choice == "start":
                break
    else:
        # Reine CLI
        pass

    # Konfiguration zusammenstellen
    config = get_config_interactive(args)

    api_key = config["api_key"]
    shared_secret = config["shared_secret"]
    access_token = config["access_token"]
    shop_id = config["shop_id"]
    output_dir = config["output_dir"]
    download_images_flag = config["download_images"]

    # Output-Dir erstellen
    output_dir.mkdir(parents=True, exist_ok=True)

    # API Client initialisieren
    try:
        client = EtsyAPIClient(api_key, shared_secret, access_token, shop_id)
    except Exception as e:
        log(f"Fehler beim Initialisieren des API-Clients: {e}", "ERROR")
        sys.exit(1)

    # Alle Listings holen (mit Pagination)
    all_listings = []
    offset = 0
    log("Hole Listings...")

    try:
        while True:
            resp = client.get_listings(limit=args.batch_size, offset=offset)
            listings = resp.get("results", [])
            if not listings:
                break
            all_listings.extend(listings)
            log(f"{len(all_listings)} Listings geladen...")
            if len(listings) < args.batch_size:
                break
            offset += args.batch_size
    except Exception as e:
        log(f"Fehler beim Abrufen der Listings: {e}", "ERROR")
        sys.exit(1)

    log(f"Insgesamt {len(all_listings)} Listings gefunden")

    # Versandinfos holen (batchweise)
    shipping_data = {}
    if all_listings:
        try:
            listing_ids = [l["listing_id"] for l in all_listings]
            # In Batches von 25 (Etsy Limit fuer batch/shipping)
            batch_size_shipping = 25
            for i in range(0, len(listing_ids), batch_size_shipping):
                batch_ids = listing_ids[i:i + batch_size_shipping]
                shipping_resp = client.get_batch_shipping(batch_ids)
                shipping_results = shipping_resp.get("results", [])
                for item in shipping_results:
                    listing_id = str(item.get("listing_id", ""))
                    shipping_data[listing_id] = item
            log("Versandinfos geladen")
        except Exception as e:
            log(f"Fehler beim Abrufen der Versandinfos: {e}", "WARN")

    # Bilder herunterladen (optional)
    if download_images_flag:
        log("Lade Bilder herunter...")
        for listing in all_listings:
            images = listing.get("images", [])
            if images:
                download_images(images, output_dir, listing["listing_id"])

    # CSV exportieren
    csv_file = output_dir / "listings.csv"
    export_listings_to_csv(all_listings, shipping_data, csv_file)

    log("Export abgeschlossen!")
    log(f"Output: {output_dir}")


if __name__ == "__main__":
    main()
