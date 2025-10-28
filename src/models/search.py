from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from enum import Enum


class PropertyType(str, Enum):
    """Types d'hebergement disponibles sur Booking"""
    HOTEL = "204"
    APARTMENT = "201"
    HOSTEL = "203"
    BED_AND_BREAKFAST = "208"
    VILLA = "213"
    RESORT = "206"
    GUEST_HOUSE = "216"
    ALL = "all"


class MealPlan(str, Enum):
    """Options de repas"""
    BREAKFAST_INCLUDED = "1"
    ALL_INCLUSIVE = "3"
    NO_PREFERENCE = "all"


class CancellationPolicy(str, Enum):
    """Politique d'annulation"""
    FREE_CANCELLATION = "1"
    NO_PREPAYMENT = "2"
    ALL = "all"


class HotelSearchRequest(BaseModel):
    # Criteres de base
    city: str = Field(..., description="Ville de destination")
    checkin: date = Field(..., description="Date d'arrivee (YYYY-MM-DD)")
    checkout: date = Field(..., description="Date de depart (YYYY-MM-DD)")
    adults: int = Field(2, ge=1, le=30, description="Nombre d'adultes (1-30)")
    children: int = Field(0, ge=0, le=10, description="Nombre d'enfants (0-10)")
    rooms: int = Field(1, ge=1, le=30, description="Nombre de chambres (1-30)")

    # Filtres avances
    min_price: Optional[int] = Field(None, ge=0, description="Prix minimum par nuit en EUR")
    max_price: Optional[int] = Field(None, ge=0, description="Prix maximum par nuit en EUR")

    min_review_score: Optional[float] = Field(None, ge=0, le=10, description="Note minimum (0-10, ex: 8.0 = Tres bien)")

    property_types: Optional[List[PropertyType]] = Field(None, description="Types d'hebergement souhaites")

    star_rating: Optional[List[int]] = Field(None, description="Nombre d'etoiles (1-5)")

    # Equipements
    free_wifi: bool = Field(False, description="WiFi gratuit requis")
    free_parking: bool = Field(False, description="Parking gratuit requis")
    pool: bool = Field(False, description="Piscine requise")
    fitness_center: bool = Field(False, description="Salle de sport requise")
    air_conditioning: bool = Field(False, description="Climatisation requise")
    restaurant: bool = Field(False, description="Restaurant requis")
    pets_allowed: bool = Field(False, description="Animaux acceptes")

    # Options
    meal_plan: Optional[MealPlan] = Field(None, description="Plan de repas")
    free_cancellation: bool = Field(False, description="Annulation gratuite uniquement")

    # Distance et localisation
    distance_from_center: Optional[int] = Field(None, ge=0, le=30, description="Distance max du centre en km")

    # Tri des resultats
    sort_by: Optional[str] = Field("popularity", description="Tri: popularity, price, review_score, distance")

    # Pagination
    max_results: int = Field(25, ge=1, le=100, description="Nombre max de resultats a scraper")


class HotelSummary(BaseModel):
    hotel_id: str
    name: str
    price: Optional[float] = None
    currency: str = "EUR"
    rating: Optional[float] = None
    review_score: Optional[float] = None
    review_count: Optional[int] = None
    location: Optional[str] = None
    image_url: Optional[str] = None
    url: str


class HotelSearchResult(BaseModel):
    request: HotelSearchRequest
    hotels: List[HotelSummary]
    total_found: int
    scrape_timestamp: str