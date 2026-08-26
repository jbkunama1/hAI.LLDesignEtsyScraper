FROM python:3.11-slim

LABEL maintainer="Etsy Shop Exporter"
LABEL description="CLI Tool zum Exportieren von Etsy Listings via API v3"

# whiptail installieren (fuer interaktives Menue)
RUN apt-get update && apt-get install -y --no-install-recommends \
    whiptail \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis
WORKDIR /app

# Abhaengigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Skript kopieren
COPY etsy-shop-exporter.py .

# Ausfuehrbar machen
RUN chmod +x etsy-shop-exporter.py

# Default Output-Dir
VOLUME ["/app/etsy_export"]

# Default Command (kann via CLI-Args ueberschrieben werden)
ENTRYPOINT ["python", "etsy-shop-exporter.py"]
CMD ["--help"]