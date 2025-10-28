# Travliaq Booking Scrapper

## Installation

1. Créer un environnement virtuel :
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Ubuntu
source venv/bin/activate
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
playwright install chromium
```

3. Copier .env.example vers .env et ajuster si besoin

## Tests rapides
```bash
python tests/test_simple.py
```

## Lancer l'API
```bash
uvicorn src.api.main:app --reload --port 8001
```

Endpoints :
- `GET /search_hotels?city=Paris&checkin=2025-12-01&checkout=2025-12-05&adults=2`
- `GET /hotel_details?hotel_id=123456`
