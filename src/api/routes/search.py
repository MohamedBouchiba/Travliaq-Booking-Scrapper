from fastapi import APIRouter, HTTPException
from src.models.search import HotelSearchRequest, HotelSearchResult
from src.scrapers.search import SearchScraper
from datetime import date

router = APIRouter()

@router.get("/search_hotels", response_model=HotelSearchResult)
async def search_hotels(
    city: str,
    checkin: date,
    checkout: date,
    adults: int = 2,
    children: int = 0,
    rooms: int = 1
):
    """
    Recherche des hotels disponibles sur Booking.com

    Exemple: /search_hotels?city=Paris&checkin=2025-12-01&checkout=2025-12-05&adults=2
    """
    try:
        request = HotelSearchRequest(
            city=city,
            checkin=checkin,
            checkout=checkout,
            adults=adults,
            children=children,
            rooms=rooms
        )

        async with SearchScraper() as scraper:
            result = await scraper.search_hotels(request)
            return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur scraping: {str(e)}")
