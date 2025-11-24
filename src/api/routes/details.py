from fastapi import APIRouter, HTTPException, Query
from src.models.hotel import HotelDetailsRequest, HotelDetails
from src.scrapers.details import DetailsScraper
from typing import Optional

router = APIRouter()


@router.get("/hotel_details", response_model=HotelDetails)
async def get_hotel_details(
        hotel_id: str = Query(..., description="ID de l'hotel (ex: moder-flat-heart-of-iveme)"),
        country_code: Optional[str] = Query("fr", description="Code pays (ex: fr, gb, us)"),
        checkin: Optional[str] = Query(None, description="Date checkin (YYYY-MM-DD) pour prix chambres"),
        checkout: Optional[str] = Query(None, description="Date checkout (YYYY-MM-DD)"),
        adults: Optional[int] = Query(2, description="Nombre d'adultes"),
        rooms: Optional[int] = Query(1, description="Nombre de chambres")
):
    """
    Recupere les details complets d'un hotel specifique.

    Exemple: /hotel_details?hotel_id=moder-flat-heart-of-iveme&country_code=fr&checkin=2025-12-12&checkout=2025-12-15&adults=2
    """
    try:
        request = HotelDetailsRequest(
            hotel_id=hotel_id,
            country_code=country_code,
            checkin=checkin,
            checkout=checkout,
            adults=adults,
            rooms=rooms
        )

        async with DetailsScraper() as scraper:
            details, reviews = await scraper.get_hotel_details(request)
            return details

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur scraping details: {str(e)}")