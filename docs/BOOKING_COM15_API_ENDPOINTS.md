# Documentation API Booking-com15 (DataCrawler) - Endpoints Hotels

## Vue d'ensemble

**API**: Booking COM (booking-com15)
**Provider**: DataCrawler
**Plateforme**: RapidAPI
**URL**: https://rapidapi.com/DataCrawler/api/booking-com15

L'API permet de rechercher en temps réel:
- Prix des hôtels
- Prix des vols
- Locations de voitures
- Taxis
- Attractions

**Note**: L'API fournit uniquement des endpoints GET (lecture seule).

---

## Endpoints Hotels Identifiés

### 1. Recherche de Destinations / Autocomplete

| Endpoint | Description |
|----------|-------------|
| `hotels/searchDestination` | Recherche de destinations par texte (autocomplete) |

**Paramètres probables**:
- `query` - Texte de recherche (ville, pays, région)
- `locale` - Langue (ex: "en-us", "fr")

**Retour**: Liste de destinations avec `dest_id` et `dest_type`

---

### 2. Recherche d'Hôtels

| Endpoint | Description |
|----------|-------------|
| `hotels/searchHotels` | Recherche d'hôtels disponibles |
| `properties/list-by-map` | Recherche d'hôtels par zone géographique |

**Paramètres requis**:
- `dest_id` - ID de destination (obtenu via searchDestination)
- `dest_type` - Type de destination (city, region, country, hotel, airport)
- `checkin_date` - Date d'arrivée (format: YYYY-MM-DD)
- `checkout_date` - Date de départ (format: YYYY-MM-DD)
- `adults_number` - Nombre d'adultes
- `room_number` - Nombre de chambres

**Paramètres optionnels** (probables):
- `children_number` - Nombre d'enfants
- `children_ages` - Ages des enfants
- `filter_by_currency` - Devise (EUR, USD, etc.)
- `locale` - Langue
- `order_by` - Tri (price, popularity, review_score, distance)
- `units` - Unités (metric, imperial)
- `page_number` - Pagination
- `price_min` / `price_max` - Filtres de prix
- `categories_filter_ids` - Filtres de catégories

**Paramètres géographiques** (pour list-by-map):
- `latitude` / `longitude` - Coordonnées centrales
- `bbox` - Bounding box (ne_lat, ne_lng, sw_lat, sw_lng)

---

### 3. Détails d'Hôtel

| Endpoint | Description |
|----------|-------------|
| `hotels/getHotelDetails` | Informations détaillées d'un hôtel |

**Paramètres requis**:
- `hotel_id` - ID de l'hôtel (obtenu via searchHotels)
- `checkin_date` - Date d'arrivée
- `checkout_date` - Date de départ
- `adults_number` - Nombre d'adultes

**Paramètres optionnels**:
- `locale` - Langue
- `currency_code` - Devise

---

### 4. Photos d'Hôtel

| Endpoint | Description |
|----------|-------------|
| `hotels/getHotelPhotos` | Photos d'un hôtel |

**Paramètres requis**:
- `hotel_id` - ID de l'hôtel

**Paramètres optionnels**:
- `locale` - Langue

---

### 5. Avis / Reviews

| Endpoint | Description |
|----------|-------------|
| `hotels/getHotelReviews` | Avis clients d'un hôtel |
| `properties/get-featured-reviews` | Avis en vedette |

**Paramètres requis**:
- `hotel_id` - ID de l'hôtel

**Paramètres optionnels**:
- `locale` - Langue (ex: "en-us")
- `sort_type` - Type de tri (SORT_HIGHEST_RATED, SORT_MOST_RECENT, etc.)
- `customer_type` - Type de client (individual, review_group_family, etc.)
- `page_number` - Pagination

---

### 6. Équipements / Facilities

| Endpoint | Description |
|----------|-------------|
| `properties/get-facilities` | Liste des équipements de l'hôtel |

**Paramètres requis**:
- `hotel_id` - ID de l'hôtel

---

### 7. Carte Statique

| Endpoint | Description |
|----------|-------------|
| `properties/get-static-map` | Image carte de localisation |

**Paramètres requis**:
- `hotel_id` - ID de l'hôtel

---

### 8. Filtres de Recherche

| Endpoint | Description |
|----------|-------------|
| `hotels/getFilters` | Liste des filtres disponibles pour la recherche |

**Paramètres**: Similaires à searchHotels

---

### 9. Chambres / Disponibilité

| Endpoint | Description |
|----------|-------------|
| `hotels/getRooms` | Chambres disponibles et tarifs |

**Paramètres requis**:
- `hotel_id` - ID de l'hôtel
- `checkin_date` - Date d'arrivée
- `checkout_date` - Date de départ
- `adults_number` - Nombre d'adultes
- `room_number` - Nombre de chambres

---

## Informations Techniques

### Headers Requis
```
X-RapidAPI-Key: YOUR_API_KEY
X-RapidAPI-Host: booking-com15.p.rapidapi.com
```

### Base URL
```
https://booking-com15.p.rapidapi.com/api/v1/
```

### Exemple de Requête (Python)
```python
import requests

url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchDestination"

querystring = {"query": "Paris"}

headers = {
    "X-RapidAPI-Key": "YOUR_API_KEY",
    "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)
print(response.json())
```

### Exemple de Requête (JavaScript)
```javascript
const axios = require('axios');

const options = {
  method: 'GET',
  url: 'https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotels',
  params: {
    dest_id: '-1456928',
    dest_type: 'city',
    checkin_date: '2025-01-15',
    checkout_date: '2025-01-18',
    adults_number: '2',
    room_number: '1'
  },
  headers: {
    'X-RapidAPI-Key': 'YOUR_API_KEY',
    'X-RapidAPI-Host': 'booking-com15.p.rapidapi.com'
  }
};

axios.request(options).then(response => {
  console.log(response.data);
});
```

---

## Tarification

| Plan | Requêtes/mois | Prix |
|------|---------------|------|
| **Free** | 500 | Gratuit |
| **ULTRA Plan** | - | Contacter le provider |
| **MEGA Plan** | - | Contacter le provider |

---

## Limitations

- Endpoints GET uniquement (lecture seule)
- Pas de création/modification de réservations
- Redirection vers Booking.com pour finaliser les réservations
- Rate limiting selon le plan choisi

---

## Comparaison avec le Scraper Existant

| Aspect | API RapidAPI | Scraper Actuel |
|--------|--------------|----------------|
| **Fiabilité** | Stable (API officielle) | Peut casser si Booking change |
| **Vitesse** | Rapide | Plus lent (scraping) |
| **Coût** | Payant après 500 req/mois | Gratuit |
| **Données** | Structurées (JSON) | Extraction manuelle |
| **Risque blocage** | Aucun | Possible |

---

## Sources

- [Booking COM API - RapidAPI](https://rapidapi.com/DataCrawler/api/booking-com15)
- [Booking COM API Details](https://rapidapi.com/DataCrawler/api/booking-com15/details)
- [Documentation officielle Booking.com](https://developers.booking.com/)
- [Discussions communautaires](https://community.latenode.com/t/finding-hotel-id-on-booking-com-via-rapidapi-whats-the-method/1751)

---

## Note Importante

Cette documentation est basée sur des recherches web et peut ne pas être exhaustive. Pour les spécifications exactes des paramètres et les structures de réponse, consultez directement le playground de l'API sur RapidAPI:

**https://rapidapi.com/DataCrawler/api/booking-com15/playground**
