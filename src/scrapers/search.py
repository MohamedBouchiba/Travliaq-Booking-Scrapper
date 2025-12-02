from .base import BaseScraper
from src.models.search import HotelSearchRequest, HotelSearchResult, HotelSummary, PropertyType
from config.settings import settings
from datetime import datetime
import logging
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class SearchScraper(BaseScraper):
    """Scraper pour la liste d'hotels avec filtres avances."""

    async def search_hotels(self, request: HotelSearchRequest) -> HotelSearchResult:
        """
        Recherche les hotels disponibles selon les criteres.
        """
        page = await self.new_page()

        try:
            # Construction de l'URL de recherche Booking avec tous les filtres
            url = self._build_search_url(request)
            await self.safe_goto(page, url)

            # Attendre que les resultats se chargent
            await page.wait_for_selector('[data-testid="property-card"]', timeout=90000)

            # Extraction des hotels
            hotels = await self._extract_hotels(page, request.max_results)

            return HotelSearchResult(
                request=request,
                hotels=hotels,
                total_found=len(hotels),
                scrape_timestamp=datetime.utcnow().isoformat()
            )

        except Exception as e:
            logger.error(f"Erreur lors du scraping: {e}")
            raise
        finally:
            await page.close()

    def _build_search_url(self, request: HotelSearchRequest) -> str:
        """Construit l'URL de recherche Booking avec tous les parametres de filtrage."""
        checkin = request.checkin.strftime("%Y-%m-%d")
        checkout = request.checkout.strftime("%Y-%m-%d")

        # Parametres de base
        params = {
            "ss": request.city,
            "checkin": checkin,
            "checkout": checkout,
            "group_adults": request.adults,
            "group_children": request.children,
            "no_rooms": request.rooms,
        }

        # Filtres de prix
        if request.min_price:
            params["min_price"] = request.min_price
        if request.max_price:
            params["max_price"] = request.max_price

        # Note minimum (Booking utilise review_score_filter)
        if request.min_review_score:
            # Booking: 60=6+, 70=7+, 80=8+, 90=9+
            score_value = int(request.min_review_score * 10)
            params["review_score"] = score_value

        # Types d'hebergement
        if request.property_types:
            for prop_type in request.property_types:
                if prop_type != PropertyType.ALL:
                    params[f"nflt=ht_id%3D{prop_type.value}"] = ""

        # Etoiles
        if request.star_rating:
            for star in request.star_rating:
                params[f"nflt=class%3D{star}"] = ""

        # Equipements (facility filters)
        facilities = []
        if request.free_wifi:
            facilities.append("107")  # Free WiFi
        if request.free_parking:
            facilities.append("2")  # Free parking
        if request.pool:
            facilities.append("433")  # Pool
        if request.fitness_center:
            facilities.append("43")  # Fitness center
        if request.air_conditioning:
            facilities.append("11")  # Air conditioning
        if request.restaurant:
            facilities.append("3")  # Restaurant
        if request.pets_allowed:
            facilities.append("4")  # Pets allowed

        for facility in facilities:
            params[f"nflt=fc%3D{facility}"] = ""

        # Plan de repas
        if request.meal_plan and request.meal_plan != "all":
            params["mealplan"] = request.meal_plan.value

        # Annulation gratuite
        if request.free_cancellation:
            params["nflt"] = "fc=1"  # Free cancellation

        # Distance du centre
        if request.distance_from_center:
            params["distance"] = request.distance_from_center * 1000  # metres

        # Tri
        sort_mapping = {
            "popularity": "popularity",
            "price": "price",
            "review_score": "review_score_and_price",
            "distance": "distance_from_search"
        }
        params["order"] = sort_mapping.get(request.sort_by, "popularity")

        # Construction URL finale
        base_url = f"{settings.booking_base_url}/searchresults.html"
        return f"{base_url}?{urlencode(params, doseq=True)}"

    async def _extract_hotels(self, page, max_results: int = 25) -> list[HotelSummary]:
        """Extrait la liste des hotels depuis la page de resultats."""
        hotels = []

        # Selecteurs Booking (peuvent changer!)
        cards = await page.query_selector_all('[data-testid="property-card"]')

        # Limiter au nombre max demande
        cards_to_process = cards[:max_results]
        logger.info(f"Extraction de {len(cards_to_process)} hotels...")

        for card in cards_to_process:
            try:
                # Extraction des donnees de chaque hotel
                name_elem = await card.query_selector('[data-testid="title"]')
                name = await name_elem.inner_text() if name_elem else "Unknown"

                price_elem = await card.query_selector('[data-testid="price-and-discounted-price"]')
                price_text = await price_elem.inner_text() if price_elem else "0"
                price = self._parse_price(price_text)

                link_elem = await card.query_selector('a[data-testid="title-link"]')
                url = await link_elem.get_attribute('href') if link_elem else ""
                hotel_id = self._extract_hotel_id(url)

                # Extraction note (si disponible)
                review_score = None
                review_elem = await card.query_selector('[data-testid="review-score"]')
                if review_elem:
                    score_text = await review_elem.inner_text()
                    review_score = self._parse_review_score(score_text)

                hotels.append(HotelSummary(
                    hotel_id=hotel_id,
                    name=name.strip(),
                    price=price,
                    currency="EUR",
                    review_score=review_score,
                    url=f"{settings.booking_base_url}{url}" if url else ""
                ))
            except Exception as e:
                logger.warning(f"Erreur extraction hotel: {e}")
                continue

        return hotels

    def _parse_price(self, price_text: str) -> float:
        """Parse le texte de prix en float."""
        try:
            # Enlever symboles monetaires et espaces
            cleaned = price_text.replace('€', '').replace('$', '').replace(',', '').replace(' ', '').strip()
            # Extraire le premier nombre trouve
            import re
            match = re.search(r'\d+', cleaned)
            if match:
                return float(match.group())
            return 0.0
        except:
            return 0.0

    def _parse_review_score(self, score_text: str) -> float:
        """Parse la note de l'hotel."""
        try:
            import re
            match = re.search(r'(\d+\.?\d*)', score_text)
            if match:
                return float(match.group(1))
            return None
        except:
            return None

    def _extract_hotel_id(self, url: str) -> str:
        """Extrait l'ID hotel depuis l'URL."""
        try:
            # Format typique: /hotel/fr/name.html?hotel_id=123456
            if 'hotel_id=' in url:
                return url.split('hotel_id=')[1].split('&')[0]
            return url.split('/')[-1].split('.')[0]
        except:
            return "unknown"