# Documentation - Parametres de Recherche Hotels

## Vue d'ensemble

Le scraper Booking accepte un JSON avec de nombreux filtres pour affiner les resultats.

## Structure JSON Complete

```json
{
  "city": "Paris",                    // REQUIS - Ville de destination
  "checkin": "2025-12-15",            // REQUIS - Date arrivee (YYYY-MM-DD)
  "checkout": "2025-12-18",           // REQUIS - Date depart
  "adults": 2,                        // Nombre adultes (1-30, defaut: 2)
  "children": 0,                      // Nombre enfants (0-10, defaut: 0)
  "rooms": 1,                         // Nombre chambres (1-30, defaut: 1)
  
  "min_price": 80,                    // Prix min/nuit en EUR (optionnel)
  "max_price": 200,                   // Prix max/nuit en EUR (optionnel)
  
  "min_review_score": 8.0,            // Note minimum 0-10 (optionnel)
  
  "property_types": [                 // Types hebergement (optionnel)
    "HOTEL",
    "APARTMENT"
  ],
  
  "star_rating": [4, 5],              // Etoiles 1-5 (optionnel, liste)
  
  "free_wifi": true,                  // WiFi gratuit (boolean, defaut: false)
  "free_parking": false,              // Parking gratuit (boolean)
  "pool": false,                      // Piscine (boolean)
  "fitness_center": true,             // Salle sport (boolean)
  "air_conditioning": true,           // Climatisation (boolean)
  "restaurant": true,                 // Restaurant (boolean)
  "pets_allowed": false,              // Animaux (boolean)
  
  "meal_plan": "BREAKFAST_INCLUDED",  // Plan repas (optionnel)
  "free_cancellation": true,          // Annulation gratuite (boolean)
  
  "distance_from_center": 5,          // Distance max centre en km (optionnel)
  
  "sort_by": "review_score",          // Tri resultats (optionnel)
  
  "max_results": 50                   // Limite resultats (1-100, defaut: 25)
}
```

## Parametres Detailles

### 1. Criteres de Base (REQUIS)

- **city** (string) : Ville de destination
  - Ex: "Paris", "New York", "Tokyo"

- **checkin** (date) : Date d'arrivee
  - Format: "YYYY-MM-DD"
  - Ex: "2025-12-15"

- **checkout** (date) : Date de depart
  - Format: "YYYY-MM-DD"
  - Doit etre apres checkin

- **adults** (int) : Nombre d'adultes
  - Min: 1, Max: 30
  - Defaut: 2

- **children** (int) : Nombre d'enfants
  - Min: 0, Max: 10
  - Defaut: 0

- **rooms** (int) : Nombre de chambres
  - Min: 1, Max: 30
  - Defaut: 1

### 2. Filtres Prix

- **min_price** (int, optionnel) : Prix minimum par nuit en EUR
  - Ex: 50, 100, 150

- **max_price** (int, optionnel) : Prix maximum par nuit en EUR
  - Ex: 200, 500, 1000

### 3. Filtres Qualite

- **min_review_score** (float, optionnel) : Note minimum
  - Echelle: 0-10
  - Ex: 8.0 = "Tres bien", 9.0 = "Fabuleux"
  - Correspondance Booking:
    - 6.0+ = Agreable
    - 7.0+ = Bien
    - 8.0+ = Tres bien
    - 9.0+ = Fabuleux

### 4. Types d'Hebergement

- **property_types** (liste, optionnel) : Types souhaites
  - Valeurs possibles:
    - "HOTEL" : Hotels classiques
    - "APARTMENT" : Appartements
    - "HOSTEL" : Auberges de jeunesse
    - "BED_AND_BREAKFAST" : Chambres d'hotes
    - "VILLA" : Villas
    - "RESORT" : Complexes hoteliers
    - "GUEST_HOUSE" : Maisons d'hotes
    - "ALL" : Tous types
  - Ex: ["HOTEL", "APARTMENT"]

### 5. Classification

- **star_rating** (liste int, optionnel) : Nombre d'etoiles
  - Valeurs: 1, 2, 3, 4, 5
  - Ex: [4, 5] pour 4-5 etoiles uniquement

### 6. Equipements (tous boolean, defaut: false)

- **free_wifi** : WiFi gratuit requis
- **free_parking** : Parking gratuit requis
- **pool** : Piscine requise
- **fitness_center** : Salle de sport requise
- **air_conditioning** : Climatisation requise
- **restaurant** : Restaurant sur place requis
- **pets_allowed** : Accepte les animaux

### 7. Options de Sejour

- **meal_plan** (string, optionnel) : Plan de repas
  - Valeurs:
    - "BREAKFAST_INCLUDED" : Petit-dejeuner inclus
    - "ALL_INCLUSIVE" : Tout compris
    - "NO_PREFERENCE" : Sans preference

- **free_cancellation** (boolean) : Annulation gratuite uniquement
  - true = seulement les offres avec annulation gratuite

### 8. Localisation

- **distance_from_center** (int, optionnel) : Distance max du centre-ville
  - Unite: kilometres
  - Ex: 5 = maximum 5km du centre

### 9. Tri des Resultats

- **sort_by** (string, optionnel) : Ordre de tri
  - Valeurs:
    - "popularity" : Par popularite (defaut)
    - "price" : Par prix croissant
    - "review_score" : Par note decroissante
    - "distance" : Par distance du centre

### 10. Pagination

- **max_results** (int) : Nombre max de resultats a scraper
  - Min: 1, Max: 100
  - Defaut: 25
  - Note: Plus le nombre est eleve, plus le scraping prend du temps

## Exemples d'Utilisation

### Exemple 1: Recherche Simple (Minimum)

```json
{
  "city": "Paris",
  "checkin": "2025-12-01",
  "checkout": "2025-12-05",
  "adults": 2
}
```

### Exemple 2: Hotels Haut de Gamme

```json
{
  "city": "Paris",
  "checkin": "2025-12-01",
  "checkout": "2025-12-05",
  "adults": 2,
  "min_price": 200,
  "min_review_score": 9.0,
  "star_rating": [5],
  "free_wifi": true,
  "pool": true,
  "restaurant": true,
  "sort_by": "review_score"
}
```

### Exemple 3: Petit Budget

```json
{
  "city": "Berlin",
  "checkin": "2025-12-10",
  "checkout": "2025-12-13",
  "adults": 2,
  "max_price": 80,
  "property_types": ["HOSTEL", "APARTMENT"],
  "free_wifi": true,
  "free_cancellation": true,
  "sort_by": "price"
}
```

### Exemple 4: Voyage Famille

```json
{
  "city": "Barcelona",
  "checkin": "2025-12-15",
  "checkout": "2025-12-22",
  "adults": 2,
  "children": 2,
  "rooms": 2,
  "property_types": ["APARTMENT", "VILLA"],
  "free_parking": true,
  "pool": true,
  "distance_from_center": 10,
  "max_results": 30
}
```

### Exemple 5: Voyage d'Affaires

```json
{
  "city": "London",
  "checkin": "2025-11-20",
  "checkout": "2025-11-23",
  "adults": 1,
  "property_types": ["HOTEL"],
  "star_rating": [4, 5],
  "free_wifi": true,
  "fitness_center": true,
  "restaurant": true,
  "free_cancellation": true,
  "distance_from_center": 3,
  "sort_by": "distance"
}
```

## Utilisation dans Python

```python
from src.models.search import HotelSearchRequest, PropertyType, MealPlan
from datetime import date

# Methode 1: Construction directe
request = HotelSearchRequest(
    city="Paris",
    checkin=date(2025, 12, 15),
    checkout=date(2025, 12, 18),
    adults=2,
    min_price=100,
    max_price=250,
    min_review_score=8.0,
    property_types=[PropertyType.HOTEL, PropertyType.APARTMENT],
    star_rating=[4, 5],
    free_wifi=True,
    meal_plan=MealPlan.BREAKFAST_INCLUDED,
    free_cancellation=True,
    sort_by="review_score",
    max_results=50
)

# Methode 2: Depuis JSON
import json
with open('search_params.json') as f:
    data = json.load(f)
    request = HotelSearchRequest(**data)

# Methode 3: Via API (FastAPI parse automatiquement)
# GET /search_hotels?city=Paris&checkin=2025-12-15&...
```

## Notes Importantes

1. **Performance** : Plus vous ajoutez de filtres restrictifs, moins vous aurez de resultats, mais plus ils seront pertinents.

2. **Temps de scraping** : Proportionnel a `max_results`. 25 resultats = ~5-10s, 100 resultats = ~20-30s.

3. **Blocages** : Si vous faites trop de requetes rapprochees avec beaucoup de resultats, Booking peut vous bloquer temporairement.

4. **Compatibilite backward** : Les 3 parametres de base suffisent, tous les autres sont optionnels.

5. **Combinaison filtres** : Tous les filtres sont cumulatifs (AND logique). Plus vous en ajoutez, plus les resultats seront affines.

## Codes Internes Booking (Reference)

### Types d'hebergement
- 204 = Hotel
- 201 = Appartement
- 203 = Auberge
- 208 = Chambre d'hotes
- 213 = Villa
- 206 = Resort
- 216 = Guest house

### Equipements
- 107 = WiFi gratuit
- 2 = Parking gratuit
- 433 = Piscine
- 43 = Salle de sport
- 11 = Climatisation
- 3 = Restaurant
- 4 = Animaux acceptes

Ces codes sont utilises en interne par le scraper pour construire l'URL Booking correcte.