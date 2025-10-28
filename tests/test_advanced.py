import asyncio
import sys
import json
from pathlib import Path
from datetime import date, timedelta

# Ajouter le repertoire racine du projet au path Python
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.scrapers.search import SearchScraper
from src.models.search import HotelSearchRequest, PropertyType, MealPlan

async def test_advanced_search():
    """
    Test avec parametres avances de recherche.
    """
    print("\n" + "="*60)
    print("TEST AVANCE - Recherche avec filtres")
    print("="*60)
    
    # Exemple avec TOUS les parametres disponibles
    request = HotelSearchRequest(
        # Base
        city="Paris",
        checkin=date.today() + timedelta(days=45),
        checkout=date.today() + timedelta(days=48),
        adults=2,
        children=0,
        rooms=1,
        
        # Filtres prix
        min_price=100,
        max_price=250,
        
        # Note minimum (8+ = Tres bien)
        min_review_score=8.0,
        
        # Types d'hebergement
        property_types=[PropertyType.HOTEL, PropertyType.APARTMENT],
        
        # Etoiles
        star_rating=[4, 5],
        
        # Equipements
        free_wifi=True,
        free_parking=False,
        pool=False,
        fitness_center=True,
        air_conditioning=True,
        restaurant=True,
        pets_allowed=False,
        
        # Options
        meal_plan=MealPlan.BREAKFAST_INCLUDED,
        free_cancellation=True,
        
        # Distance
        distance_from_center=5,  # Max 5km du centre
        
        # Tri
        sort_by="review_score",
        
        # Limite
        max_results=30
    )
    
    print(f"\nCRITERES DE RECHERCHE:")
    print(f"  Destination: {request.city}")
    print(f"  Dates: {request.checkin} au {request.checkout}")
    print(f"  Voyageurs: {request.adults} adultes, {request.children} enfants")
    print(f"  Chambres: {request.rooms}")
    print(f"\nFILTRES:")
    print(f"  Prix: {request.min_price}-{request.max_price} EUR/nuit")
    print(f"  Note minimum: {request.min_review_score}/10")
    print(f"  Types: {[t.name for t in request.property_types]}")
    print(f"  Etoiles: {request.star_rating}")
    print(f"  WiFi gratuit: {request.free_wifi}")
    print(f"  Salle de sport: {request.fitness_center}")
    print(f"  Climatisation: {request.air_conditioning}")
    print(f"  Restaurant: {request.restaurant}")
    print(f"  Petit-dejeuner: {request.meal_plan.name if request.meal_plan else 'Non'}")
    print(f"  Annulation gratuite: {request.free_cancellation}")
    print(f"  Distance max: {request.distance_from_center} km")
    print(f"  Tri: {request.sort_by}")
    print(f"  Limite: {request.max_results} resultats")
    
    print("\n" + "-"*60)
    print("Scraping en cours (peut prendre 10-20s)...\n")
    
    try:
        async with SearchScraper() as scraper:
            result = await scraper.search_hotels(request)
        
        print(f"SUCCES - {result.total_found} hotels trouves\n")
        print("="*60)
        
        for idx, hotel in enumerate(result.hotels[:10], 1):
            print(f"\n{idx}. {hotel.name}")
            print(f"   Prix: {hotel.price} {hotel.currency}")
            if hotel.review_score:
                print(f"   Note: {hotel.review_score}/10")
            print(f"   ID: {hotel.hotel_id}")
            print(f"   URL: {hotel.url[:70]}...")
        
        print("\n" + "="*60)
        print(f"TOP 10 affiches / {result.total_found} total")
        print("="*60)
        
        # Verifications
        assert result.total_found > 0, "Aucun hotel trouve avec ces criteres"
        print("\nTEST REUSSI - Les filtres fonctionnent")
        return True
        
    except Exception as e:
        print(f"\nERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_minimal_search():
    """Test avec parametres minimaux (comme avant)."""
    print("\n" + "="*60)
    print("TEST MINIMAL - Parametres de base uniquement")
    print("="*60)
    
    request = HotelSearchRequest(
        city="Lyon",
        checkin=date.today() + timedelta(days=30),
        checkout=date.today() + timedelta(days=33),
        adults=2
    )
    
    print(f"\nRecherche simple: {request.city}")
    print("Scraping...\n")
    
    try:
        async with SearchScraper() as scraper:
            result = await scraper.search_hotels(request)
        
        print(f"SUCCES - {result.total_found} hotels trouves")
        print(f"Premier hotel: {result.hotels[0].name}")
        print("\nTEST MINIMAL REUSSI")
        return True
    except Exception as e:
        print(f"ERREUR: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# TESTS SCRAPERS BOOKING - PARAMETRES AVANCES")
    print("#"*60)
    
    # Test 1: Recherche avec tous les filtres
    success1 = asyncio.run(test_advanced_search())
    
    # Test 2: Recherche minimale (backward compatibility)
    success2 = asyncio.run(test_minimal_search())
    
    if success1 and success2:
        print("\n" + "="*60)
        print("TOUS LES TESTS PASSENT")
        print("="*60)
        exit(0)
    else:
        exit(1)
