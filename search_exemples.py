# Exemples JSON pour recherche hotels Booking
# A copier-coller ou utiliser directement dans vos tests

# EXEMPLE 1 - Recherche Minimale (backward compatible)
MINIMAL = {
    "city": "Paris",
    "checkin": "2025-12-01",
    "checkout": "2025-12-05",
    "adults": 2
}

# EXEMPLE 2 - Hotels Haut de Gamme
LUXURY = {
    "city": "Paris",
    "checkin": "2025-12-15",
    "checkout": "2025-12-18",
    "adults": 2,
    "rooms": 1,
    "min_price": 200,
    "min_review_score": 9.0,
    "property_types": ["HOTEL"],
    "star_rating": [5],
    "free_wifi": True,
    "pool": True,
    "fitness_center": True,
    "restaurant": True,
    "meal_plan": "BREAKFAST_INCLUDED",
    "free_cancellation": True,
    "distance_from_center": 3,
    "sort_by": "review_score",
    "max_results": 20
}

# EXEMPLE 3 - Petit Budget
BUDGET = {
    "city": "Berlin",
    "checkin": "2025-12-10",
    "checkout": "2025-12-13",
    "adults": 2,
    "max_price": 80,
    "property_types": ["HOSTEL", "APARTMENT"],
    "free_wifi": True,
    "free_cancellation": True,
    "sort_by": "price",
    "max_results": 30
}

# EXEMPLE 4 - Voyage Famille
FAMILY = {
    "city": "Barcelona",
    "checkin": "2025-12-20",
    "checkout": "2025-12-27",
    "adults": 2,
    "children": 2,
    "rooms": 2,
    "property_types": ["APARTMENT", "VILLA"],
    "min_review_score": 7.5,
    "free_wifi": True,
    "free_parking": True,
    "pool": True,
    "distance_from_center": 10,
    "max_results": 25
}

# EXEMPLE 5 - Voyage d'Affaires
BUSINESS = {
    "city": "London",
    "checkin": "2025-11-20",
    "checkout": "2025-11-23",
    "adults": 1,
    "property_types": ["HOTEL"],
    "star_rating": [4, 5],
    "min_review_score": 8.0,
    "free_wifi": True,
    "fitness_center": True,
    "restaurant": True,
    "free_cancellation": True,
    "distance_from_center": 3,
    "sort_by": "distance",
    "max_results": 15
}

# EXEMPLE 6 - Sejour Romantique
ROMANTIC = {
    "city": "Venice",
    "checkin": "2026-02-14",
    "checkout": "2026-02-17",
    "adults": 2,
    "min_price": 150,
    "max_price": 300,
    "property_types": ["HOTEL", "BED_AND_BREAKFAST"],
    "star_rating": [4, 5],
    "min_review_score": 8.5,
    "free_wifi": True,
    "restaurant": True,
    "meal_plan": "BREAKFAST_INCLUDED",
    "distance_from_center": 2,
    "sort_by": "review_score",
    "max_results": 20
}

# EXEMPLE 7 - Backpacker / Auberges
BACKPACKER = {
    "city": "Amsterdam",
    "checkin": "2025-11-05",
    "checkout": "2025-11-08",
    "adults": 1,
    "max_price": 50,
    "property_types": ["HOSTEL"],
    "free_wifi": True,
    "free_cancellation": True,
    "distance_from_center": 5,
    "sort_by": "price",
    "max_results": 40
}

# EXEMPLE 8 - Tout Inclus / Resort
ALL_INCLUSIVE = {
    "city": "Cancun",
    "checkin": "2026-01-10",
    "checkout": "2026-01-17",
    "adults": 2,
    "property_types": ["RESORT"],
    "min_review_score": 8.0,
    "pool": True,
    "restaurant": True,
    "fitness_center": True,
    "meal_plan": "ALL_INCLUSIVE",
    "sort_by": "review_score",
    "max_results": 25
}

# EXEMPLE 9 - Avec Animaux
PET_FRIENDLY = {
    "city": "Munich",
    "checkin": "2025-12-05",
    "checkout": "2025-12-08",
    "adults": 2,
    "property_types": ["HOTEL", "APARTMENT"],
    "pets_allowed": True,
    "free_parking": True,
    "free_wifi": True,
    "min_review_score": 7.0,
    "max_results": 30
}

# EXEMPLE 10 - Recherche Ultra Complete (tous les parametres)
FULL_FEATURED = {
    "city": "Rome",
    "checkin": "2025-12-01",
    "checkout": "2025-12-05",
    "adults": 2,
    "children": 1,
    "rooms": 1,
    "min_price": 100,
    "max_price": 250,
    "min_review_score": 8.0,
    "property_types": ["HOTEL", "APARTMENT"],
    "star_rating": [4, 5],
    "free_wifi": True,
    "free_parking": False,
    "pool": False,
    "fitness_center": True,
    "air_conditioning": True,
    "restaurant": True,
    "pets_allowed": False,
    "meal_plan": "BREAKFAST_INCLUDED",
    "free_cancellation": True,
    "distance_from_center": 5,
    "sort_by": "review_score",
    "max_results": 50
}

# Fonction utilitaire pour tester un exemple
if __name__ == "__main__":
    import asyncio
    import sys
    from pathlib import Path
    from datetime import datetime

    # Ajouter le projet au path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))

    from src.scrapers.search import SearchScraper
    from src.models.search import HotelSearchRequest


    async def test_example(example_name, example_data):
        """Test un exemple specifique."""
        print(f"\n{'=' * 60}")
        print(f"TEST: {example_name}")
        print(f"{'=' * 60}")

        # Convertir dates string en date objects
        from datetime import date
        example_data['checkin'] = date.fromisoformat(example_data['checkin'])
        example_data['checkout'] = date.fromisoformat(example_data['checkout'])

        request = HotelSearchRequest(**example_data)

        print(f"Ville: {request.city}")
        print(f"Dates: {request.checkin} -> {request.checkout}")
        print(
            f"Filtres actifs: {len([k for k, v in example_data.items() if v and k not in ['city', 'checkin', 'checkout', 'adults', 'children', 'rooms']])}")

        try:
            async with SearchScraper() as scraper:
                result = await scraper.search_hotels(request)

            print(f"\nResultats: {result.total_found} hotels")
            if result.hotels:
                print(f"Premier: {result.hotels[0].name} - {result.hotels[0].price} EUR")
            print("SUCCES")
            return True
        except Exception as e:
            print(f"ERREUR: {e}")
            return False


    # Test de tous les exemples
    examples = {
        "Minimal": MINIMAL,
        "Luxe": LUXURY,
        "Budget": BUDGET,
        "Famille": FAMILY,
        "Business": BUSINESS
    }


    async def run_all():
        results = {}
        for name, data in examples.items():
            results[name] = await test_example(name, data.copy())

        print(f"\n{'=' * 60}")
        print("RESUME DES TESTS")
        print(f"{'=' * 60}")
        for name, success in results.items():
            status = "OK" if success else "FAIL"
            print(f"{name}: {status}")


    asyncio.run(run_all())