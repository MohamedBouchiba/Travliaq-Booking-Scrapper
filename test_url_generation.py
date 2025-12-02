"""Test de génération d'URL pour les détails d'hôtel."""
from src.models.hotel import HotelDetailsRequest
from src.scrapers.details import DetailsScraper
from config.settings import settings

def test_url_generation():
    """Teste la génération d'URL."""

    # Exemple 1: Avec tous les paramètres
    request1 = HotelDetailsRequest(
        hotel_id="bermondsey-heights-by-sleepy-lodge",
        country_code="en",
        checkin="2025-12-10",
        checkout="2025-12-15",
        adults=1,
        rooms=1
    )

    scraper = DetailsScraper()
    url1 = scraper._build_hotel_url(request1)
    print(f"URL 1 (complète): {url1}")

    # Exemple 2: Sans dates
    request2 = HotelDetailsRequest(
        hotel_id="moder-flat-heart-of-iveme",
        country_code="fr"
    )

    url2 = scraper._build_hotel_url(request2)
    print(f"URL 2 (minimale): {url2}")

    # Vérifications
    assert "bermondsey-heights-by-sleepy-lodge" in url1
    assert "checkin=2025-12-10" in url1
    assert "checkout=2025-12-15" in url1
    assert "group_adults=1" in url1
    assert "no_rooms=1" in url1

    assert "moder-flat-heart-of-iveme" in url2
    assert "checkin" not in url2

    print("\n✓ Tous les tests passent!")
    print(f"\nURL attendue pour votre requête:")
    print(f"https://www.booking.com/hotel/en/bermondsey-heights-by-sleepy-lodge.html?checkin=2025-12-10&checkout=2025-12-15&group_adults=1&no_rooms=1")

if __name__ == "__main__":
    test_url_generation()
