from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import time


class HotelDetailsRequest(BaseModel):
    hotel_id: str = Field(..., description="ID de l'hotel (depuis search results)")
    country_code: Optional[str] = Field("fr", description="Code pays (ex: fr, gb, us)")
    checkin: Optional[str] = Field(None, description="Date checkin pour prix chambres (YYYY-MM-DD)")
    checkout: Optional[str] = Field(None, description="Date checkout pour prix chambres (YYYY-MM-DD)")
    adults: Optional[int] = Field(2, description="Nombre d'adultes pour prix chambres")
    rooms: Optional[int] = Field(1, description="Nombre de chambres")


class Address(BaseModel):
    full_address: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ReviewScores(BaseModel):
    overall: Optional[float] = None
    cleanliness: Optional[float] = None
    comfort: Optional[float] = None
    location: Optional[float] = None
    facilities: Optional[float] = None
    staff: Optional[float] = None
    value_for_money: Optional[float] = None
    wifi: Optional[float] = None


class RoomOption(BaseModel):
    room_type: str
    price: Optional[float] = None
    currency: str = "EUR"
    capacity: Optional[int] = None
    bed_type: Optional[str] = None
    room_size: Optional[str] = None
    amenities: List[str] = []
    max_occupancy: Optional[int] = None
    cancellation_policy: Optional[str] = None
    breakfast_included: bool = False
    refundable: bool = False


class NearbyAttraction(BaseModel):
    name: str
    distance: Optional[str] = None
    category: Optional[str] = None


class HotelPolicies(BaseModel):
    checkin_from: Optional[str] = None
    checkin_until: Optional[str] = None
    checkout_from: Optional[str] = None
    checkout_until: Optional[str] = None
    cancellation_policy: Optional[str] = None
    prepayment_policy: Optional[str] = None
    children_policy: Optional[str] = None
    pets_policy: Optional[str] = None
    age_restriction: Optional[str] = None


class HotelDetails(BaseModel):
    # Identifiants
    hotel_id: str
    name: str
    url: str

    # Localisation
    address: Optional[Address] = None

    # Description
    description: Optional[str] = None
    property_type: Optional[str] = None
    star_rating: Optional[int] = None

    # Avis et notes
    review_score: Optional[float] = None
    review_count: Optional[int] = None
    review_scores_detail: Optional[ReviewScores] = None
    review_category: Optional[str] = None  # "Fabuleux", "Tres bien", etc.

    # Visuels
    images: List[str] = []
    main_image: Optional[str] = None

    # Equipements
    amenities: List[str] = []
    popular_amenities: List[str] = []
    room_amenities: List[str] = []

    # Chambres disponibles
    rooms: List[RoomOption] = []

    # Prix
    cheapest_price: Optional[float] = None
    currency: str = "EUR"

    # Politiques
    policies: Optional[HotelPolicies] = None
    house_rules: List[str] = []

    # À proximité
    nearby_attractions: List[NearbyAttraction] = []

    # Langues parlées
    languages_spoken: List[str] = []

    # Contact
    phone: Optional[str] = None
    email: Optional[str] = None

    # Métadonnées
    scrape_timestamp: str
    scrape_parameters: Optional[Dict] = None

    class GuestReview(BaseModel):
        """Avis client complet."""
        reviewer_name: str
        reviewer_country: str
        review_date: str
        positive_text: str = ""
        negative_text: str = ""
        score: float
        tags: List[str] = Field(default_factory=list)

        class Config:
            json_schema_extra = {
                "example": {
                    "reviewer_name": "John Smith",
                    "reviewer_country": "United States",
                    "review_date": "December 15, 2024",
                    "positive_text": "Great location, clean room",
                    "negative_text": "Wifi was slow",
                    "score": 8.5,
                    "tags": ["Couple", "Leisure"]
                }
            }
