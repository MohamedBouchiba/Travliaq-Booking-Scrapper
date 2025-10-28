import asyncio
import sys
from pathlib import Path
from datetime import date, timedelta

# Ajouter le repertoire racine du projet au path Python
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.scrapers.search import SearchScraper
from src.models.search import HotelSearchRequest


async def test_search_hotels():
    """
    Test simple du scraper de recherche d'hotels.
    """
    print("\n" + "=" * 60)
    print("TEST SIMPLE - Travliaq Booking Scraper Search")
    print("=" * 60)

    # Parametres de test
    checkin = date.today() + timedelta(days=30)
    checkout = checkin + timedelta(days=3)

    request = HotelSearchRequest(
        city="Paris",
        checkin=checkin,
        checkout=checkout,
        adults=2,
        rooms=1
    )

    print(f"\nRecherche: {request.city}")
    print(f"Check-in: {request.checkin}")
    print(f"Check-out: {request.checkout}")
    print(f"Adultes: {request.adults}")
    print("\nScraping en cours...\n")

    try:
        async with SearchScraper() as scraper:
            result = await scraper.search_hotels(request)

        print(f"SUCCES - {result.total_found} hotels trouves\n")
        print("-" * 60)

        for idx, hotel in enumerate(result.hotels[:5], 1):
            print(f"\n{idx}. {hotel.name}")
            print(f"   Prix: {hotel.price} {hotel.currency}")
            print(f"   ID: {hotel.hotel_id}")
            print(f"   URL: {hotel.url[:80]}...")

        print("\n" + "=" * 60)
        print("TEST REUSSI")
        print("=" * 60)

        # Verifications
        assert result.total_found > 0, "Aucun hotel trouve"
        assert len(result.hotels) > 0, "Liste vide"
        assert result.hotels[0].name != "Unknown", "Extraction nom echouee"

        print("\nTous les checks passent")
        return True

    except Exception as e:
        print(f"\nERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_search_hotels())
    exit(0 if success else 1)