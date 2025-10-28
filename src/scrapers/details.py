from .base import BaseScraper
from src.models.hotel import (
    HotelDetailsRequest, HotelDetails, Address, ReviewScores,
    RoomOption, NearbyAttraction, HotelPolicies
)
from config.settings import settings
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging
import re
import json

logger = logging.getLogger(__name__)


class GuestReview:
    """Modele pour un avis client."""

    def __init__(self, reviewer_name: str, reviewer_country: str, review_date: str,
                 positive_text: str, negative_text: str, score: float, tags: List[str] = None):
        self.reviewer_name = reviewer_name
        self.reviewer_country = reviewer_country
        self.review_date = review_date
        self.positive_text = positive_text
        self.negative_text = negative_text
        self.score = score
        self.tags = tags or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reviewer_name": self.reviewer_name,
            "reviewer_country": self.reviewer_country,
            "review_date": self.review_date,
            "positive_text": self.positive_text,
            "negative_text": self.negative_text,
            "score": self.score,
            "tags": self.tags
        }


class DetailsScraper(BaseScraper):
    """Scraper ULTRA-CORRIGÉ - extraction précise et propre."""

    async def get_hotel_details(self, request: HotelDetailsRequest) -> tuple:
        """Recupere TOUS les details + avis."""
        page = await self.new_page()

        try:
            url = self._build_hotel_url(request)
            logger.info(f"Scraping: {url}")
            await self.safe_goto(page, url)
            await page.wait_for_timeout(6000)

            html_content = await page.content()
            json_data = self._extract_json_ld(html_content)

            # === EXTRACTION ===
            name = await self._extract_name(page, json_data)
            logger.info(f"✓ Nom: {name}")

            address = await self._extract_address(page, html_content, json_data)
            description = await self._extract_description(page, html_content)

            # FIXÉ: property_type
            property_type = await self._extract_property_type_ultra_fixed(page, html_content, json_data)
            logger.info(f"✓ Type: {property_type}")

            star_rating = await self._extract_star_rating(page, html_content)

            # FIXÉ: review_category
            review_score, review_count, review_category = await self._extract_reviews_ultra_fixed(page, html_content,
                                                                                                  json_data)
            logger.info(f"✓ Avis: {review_score}/10 ({review_count}) - {review_category}")

            # FIXÉ: review_scores_detail
            review_scores_detail = await self._extract_detailed_scores_ultra_fixed(page, html_content)
            if review_scores_detail:
                logger.info(f"✓ Scores OK")

            # Avis clients
            guest_reviews = await self._extract_guest_reviews(page, html_content)
            logger.info(f"✓ Avis: {len(guest_reviews)}")

            # FIXÉ: Images sans apostrophes
            images, main_image = await self._extract_images_ultra_fixed(page, html_content, json_data)
            logger.info(f"✓ Images: {len(images)}")

            # FIXÉ: Amenities propres (pas de devises/langues)
            amenities, popular_amenities, room_amenities = await self._extract_amenities_ultra_fixed(page, html_content)
            logger.info(f"✓ Équipements: {len(amenities)}")

            rooms = await self._extract_rooms_enhanced(page, html_content)
            logger.info(f"✓ Chambres: {len(rooms)}")
            cheapest_price = min([r.price for r in rooms if r.price], default=None)

            policies = await self._extract_policies(page, html_content)
            house_rules = await self._extract_house_rules(page, html_content)

            # FIXÉ: Attractions propres
            nearby_attractions = await self._extract_nearby_ultra_fixed(page, html_content)
            logger.info(f"✓ Attractions: {len(nearby_attractions)}")

            languages_spoken = await self._extract_languages(page, html_content)
            phone, email = await self._extract_contact(html_content)

            result = HotelDetails(
                hotel_id=request.hotel_id,
                name=name,
                url=url,
                address=address,
                description=description,
                property_type=property_type,
                star_rating=star_rating,
                review_score=review_score,
                review_count=review_count,
                review_category=review_category,
                review_scores_detail=review_scores_detail,
                images=images,
                main_image=main_image,
                amenities=amenities,
                popular_amenities=popular_amenities,
                room_amenities=room_amenities,
                rooms=rooms,
                cheapest_price=cheapest_price,
                policies=policies,
                house_rules=house_rules,
                nearby_attractions=nearby_attractions,
                languages_spoken=languages_spoken,
                phone=phone,
                email=email,
                scrape_timestamp=datetime.utcnow().isoformat(),
                scrape_parameters={
                    "checkin": request.checkin,
                    "checkout": request.checkout,
                    "adults": request.adults,
                    "rooms": request.rooms
                }
            )

            return result, guest_reviews

        except Exception as e:
            logger.error(f"Erreur: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            await page.close()

    def _build_hotel_url(self, request: HotelDetailsRequest) -> str:
        base_url = f"{settings.booking_base_url}/hotel/fr/{request.hotel_id}.html"
        params = []
        if request.checkin:
            params.append(f"checkin={request.checkin}")
        if request.checkout:
            params.append(f"checkout={request.checkout}")
        if request.adults:
            params.append(f"group_adults={request.adults}")
        if request.rooms:
            params.append(f"no_rooms={request.rooms}")
        return f"{base_url}?{'&'.join(params)}" if params else base_url

    def _extract_json_ld(self, html_content: str) -> dict:
        try:
            json_match = re.search(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html_content,
                                   re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            return {}
        except:
            return {}

    async def _extract_name(self, page, json_data: dict) -> str:
        if json_data.get('name'):
            return json_data['name']

        selectors = [
            'h2[data-testid="property-name"]',
            'h2.pp-header__title',
            'h1.d2fee87262'
        ]

        for selector in selectors:
            try:
                elem = await page.query_selector(selector)
                if elem:
                    name = await elem.inner_text()
                    if name and 3 < len(name) < 200:
                        return name.strip()
            except:
                continue

        return "Unknown Hotel"

    async def _extract_address(self, page, html_content: str, json_data: dict) -> Optional[Address]:
        full_address = None
        lat, lon = None, None

        if json_data.get('address'):
            addr_obj = json_data['address']
            if isinstance(addr_obj, dict):
                street = addr_obj.get('streetAddress', '')
                city = addr_obj.get('addressLocality', '')
                postal = addr_obj.get('postalCode', '')
                country = addr_obj.get('addressCountry', '')
                full_address = f"{street}, {city}, {postal}, {country}".strip(', ')

        if not full_address:
            selectors = ['span[data-node_tt_id="location_score_tooltip"]', '.hp_address_subtitle']
            for selector in selectors:
                try:
                    elem = await page.query_selector(selector)
                    if elem:
                        addr = await elem.inner_text()
                        if addr and len(addr) > 10:
                            full_address = addr.strip()
                            break
                except:
                    continue

        if json_data.get('geo'):
            geo = json_data['geo']
            if isinstance(geo, dict):
                lat = geo.get('latitude')
                lon = geo.get('longitude')

        if not lat:
            lat_match = re.search(r'"latitude":\s*([-\d.]+)', html_content)
            lon_match = re.search(r'"longitude":\s*([-\d.]+)', html_content)
            if lat_match and lon_match:
                lat = float(lat_match.group(1))
                lon = float(lon_match.group(1))

        return Address(full_address=full_address, latitude=lat, longitude=lon) if full_address or lat else None

    async def _extract_description(self, page, html_content: str) -> Optional[str]:
        descriptions = []
        selectors = ['#property_description_content', '[data-testid="property-description"]']

        for selector in selectors:
            try:
                elem = await page.query_selector(selector)
                if elem:
                    text = await elem.inner_text()
                    if text and len(text) > 50:
                        descriptions.append(text.strip())
            except:
                continue

        return '\n\n'.join(descriptions) if descriptions else None

    async def _extract_property_type_ultra_fixed(self, page, html_content: str, json_data: dict) -> Optional[str]:
        """ULTRA-FIXÉ: Détecte le vrai type."""

        # Méthode 1: JSON-LD @type
        if json_data.get('@type'):
            types_valid = ['Hotel', 'Apartment', 'Resort', 'BedAndBreakfast', 'Hostel', 'Motel', 'Lodge']
            if json_data['@type'] in types_valid:
                return json_data['@type']

        # Méthode 2: Chercher dans les badges/labels VISIBLES
        try:
            # Selecteur précis pour badge de type
            badge_selectors = [
                '[data-testid="property-type-badge"]',
                'span[data-testid="badge-property-type"]',
                '.bui-badge.bui-badge--outline'
            ]

            for sel in badge_selectors:
                elem = await page.query_selector(sel)
                if elem:
                    text = await elem.inner_text()
                    text = text.strip()

                    # FILTRER les faux positifs
                    if text and 2 < len(text) < 30:
                        # Rejeter les prix
                        if '%' in text or 'off' in text.lower() or 'discount' in text.lower():
                            continue
                        # Rejeter les nombres
                        if text.replace('.', '').replace(',', '').isdigit():
                            continue

                        # Types valides
                        valid_types = ['hotel', 'apartment', 'resort', 'hostel', 'villa', 'bed and breakfast', 'motel',
                                       'lodge', 'entire']
                        if any(vt in text.lower() for vt in valid_types):
                            return text
        except:
            pass

        # Méthode 3: Analyser le titre de la page
        page_text = html_content[:10000].lower()

        if 'entire apartment' in page_text or 'entire flat' in page_text:
            return "Apartment"
        elif 'entire house' in page_text or 'entire home' in page_text:
            return "House"
        elif 'vacation home' in page_text:
            return "Vacation Home"
        elif 'hotel' in page_text[:2000]:
            return "Hotel"

        return None

    async def _extract_star_rating(self, page, html_content: str) -> Optional[int]:
        try:
            stars = await page.query_selector_all('[aria-label*="star"]')
            if stars and 1 <= len(stars) <= 5:
                return len(stars)
        except:
            pass
        return None

    async def _extract_reviews_ultra_fixed(self, page, html_content: str, json_data: dict) -> tuple:
        """ULTRA-FIXÉ: Score, count ET category."""
        score, count, category = None, None, None

        # Score
        if json_data.get('aggregateRating'):
            rating = json_data['aggregateRating']
            if isinstance(rating, dict):
                score = rating.get('ratingValue')
                count = rating.get('reviewCount')

        if not score:
            try:
                score_elem = await page.query_selector('.b5cd09854e.d10a6220b4, [data-testid="review-score-badge"]')
                if score_elem:
                    text = await score_elem.inner_text()
                    match = re.search(r'(\d+\.?\d*)', text)
                    if match:
                        score = float(match.group(1))
            except:
                pass

        if not count:
            count_match = re.search(r'(\d+)\s+(?:reviews?|avis)', html_content.lower())
            if count_match:
                count = int(count_match.group(1))

        # Category - Chercher JUSTE après le score
        if score:
            # Pattern: score puis categorie
            cat_pattern = rf'{score}\s*(?:/10)?\s*(Excellent|Fabulous|Very good|Good|Superb|Wonderful|Scored)'
            cat_match = re.search(cat_pattern, html_content, re.IGNORECASE)
            if cat_match:
                category = cat_match.group(1)

        # Fallback
        if not category:
            try:
                cat_elem = await page.query_selector('.b5cd09854e.c90c0a70d3.db63693c62')
                if cat_elem:
                    text = await cat_elem.inner_text()
                    for cat in ['Excellent', 'Fabulous', 'Very good', 'Good', 'Superb', 'Wonderful']:
                        if cat in text:
                            category = cat
                            break
            except:
                pass

        return score, count, category

    async def _extract_detailed_scores_ultra_fixed(self, page, html_content: str) -> Optional[ReviewScores]:
        """ULTRA-FIXÉ: Extraction précise des 7 scores."""
        scores = {}

        await page.wait_for_timeout(1000)

        # Méthode directe: Parser la section review_scores
        # Pattern: "Cleanliness</span><span ...>9.0</span>"
        categories_map = {
            'Staff': 'staff',
            'Personnel': 'staff',
            'Facilities': 'facilities',
            'Équipements': 'facilities',
            'Cleanliness': 'cleanliness',
            'Propreté': 'cleanliness',
            'Comfort': 'comfort',
            'Confort': 'comfort',
            'Value for money': 'value_for_money',
            'Rapport qualité': 'value_for_money',
            'Location': 'location',
            'Emplacement': 'location',
            'Free WiFi': 'wifi',
            'WiFi': 'wifi'
        }

        for label, field in categories_map.items():
            if field in scores:
                continue

            # Pattern précis: label suivi d'un score entre 0-10
            pattern = rf'{re.escape(label)}[^<>]*?(\d+\.?\d*)\s*(?:/10)?'
            match = re.search(pattern, html_content, re.IGNORECASE)

            if match:
                try:
                    value = float(match.group(1))
                    # Valider que c'est un score (0-10)
                    if 0 <= value <= 10:
                        scores[field] = value
                except:
                    pass

        return ReviewScores(**scores) if scores else None

    async def _extract_guest_reviews(self, page, html_content: str) -> List[GuestReview]:
        """Extrait les avis (peut être 0 si pas sur la page)."""
        reviews = []

        try:
            try:
                reviews_section = await page.query_selector('#review_list_page_container')
                if reviews_section:
                    await reviews_section.scroll_into_view_if_needed()
                    await page.wait_for_timeout(2000)
            except:
                pass

            review_items = await page.query_selector_all('.review_list_new_item_block, [data-testid="review-card"]')

            for item in review_items[:15]:
                try:
                    full_text = await item.inner_text()

                    name = "Anonymous"
                    try:
                        name_elem = await item.query_selector('.bui-avatar-block__title')
                        if name_elem:
                            name = (await name_elem.inner_text()).strip()
                    except:
                        pass

                    country = "Unknown"
                    try:
                        country_elem = await item.query_selector('.bui-avatar-block__subtitle')
                        if country_elem:
                            country = (await country_elem.inner_text()).strip()
                    except:
                        pass

                    date = None
                    date_match = re.search(r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})', full_text)
                    if date_match:
                        date = date_match.group(1)

                    score = None
                    try:
                        score_elem = await item.query_selector('.bui-review-score__badge')
                        if score_elem:
                            score_text = await score_elem.inner_text()
                            score_match = re.search(r'(\d+\.?\d*)', score_text)
                            if score_match:
                                score = float(score_match.group(1))
                    except:
                        pass

                    positive = ""
                    try:
                        pos_elem = await item.query_selector('.review_pos')
                        if pos_elem:
                            positive = (await pos_elem.inner_text()).strip()
                    except:
                        pass

                    negative = ""
                    try:
                        neg_elem = await item.query_selector('.review_neg')
                        if neg_elem:
                            negative = (await neg_elem.inner_text()).strip()
                    except:
                        pass

                    if name and (positive or negative):
                        review = GuestReview(
                            reviewer_name=name,
                            reviewer_country=country,
                            review_date=date or "Unknown",
                            positive_text=positive,
                            negative_text=negative,
                            score=score or 0.0,
                            tags=[]
                        )
                        reviews.append(review)

                except:
                    continue

            return reviews[:15]

        except:
            return []

    async def _extract_images_ultra_fixed(self, page, html_content: str, json_data: dict) -> tuple:
        """ULTRA-FIXÉ: Images propres sans apostrophes."""
        images = set()
        main_image = None

        # JSON-LD
        if json_data.get('image'):
            img_data = json_data['image']
            if isinstance(img_data, list):
                for img in img_data[:30]:
                    if isinstance(img, str):
                        images.add(img.rstrip("'\""))
                    elif isinstance(img, dict) and img.get('url'):
                        images.add(img['url'].rstrip("'\""))
            elif isinstance(img_data, str):
                images.add(img_data.rstrip("'\""))
                main_image = img_data.rstrip("'\"")

        # Selecteurs
        img_selectors = [
            'img[data-testid="property-gallery-image"]',
            '.bh-photo-grid-item img',
            '[data-component="photo-grid"] img'
        ]

        for selector in img_selectors:
            try:
                imgs = await page.query_selector_all(selector)
                for img in imgs[:40]:
                    src = await img.get_attribute('src')
                    if not src:
                        src = await img.get_attribute('data-src')

                    if src and 'bstatic.com' in src:
                        # Nettoyer
                        src = src.rstrip("'\"")
                        images.add(src)
                        if not main_image:
                            main_image = src
            except:
                continue

        # Regex PROPRE (sans quotes/apostrophes)
        img_pattern = r'(https://cf\.bstatic\.com/xdata/images/hotel/[^\s"\'<>]+\.(?:jpg|jpeg|png|webp)(?:\?[^\s"\'<>]*)?)'
        img_urls = re.findall(img_pattern, html_content)

        for url in img_urls[:50]:
            if '/images/hotel/' in url:
                url = url.rstrip("',\"")
                if 'max1024x768' not in url and 'max1280x900' not in url:
                    url = re.sub(r'/max\d+x?\d*/', '/max1024x768/', url)
                    url = re.sub(r'/square\d+/', '/max1024x768/', url)
                images.add(url)

        # Dédupliquer
        final_images = []
        seen_base = set()

        for img in images:
            base_match = re.search(r'/(\d+)\.(?:jpg|jpeg|png)', img)
            if base_match:
                base_id = base_match.group(1)
                if base_id not in seen_base:
                    seen_base.add(base_id)
                    final_images.append(img)
            else:
                final_images.append(img)

        return final_images, main_image

    async def _extract_amenities_ultra_fixed(self, page, html_content: str) -> tuple:
        """ULTRA-FIXÉ: Équipements propres SANS devises/langues/mois."""
        amenities = set()
        popular = []

        # Méthode 1: Sélecteurs VISUELS uniquement
        try:
            # Section "Most popular facilities"
            popular_section = await page.query_selector('div:has-text("Most popular facilities")')
            if popular_section:
                parent = await popular_section.query_selector('xpath=..')
                if parent:
                    items = await parent.query_selector_all('div, span')
                    for item in items[:15]:
                        text = await item.inner_text()
                        text = text.strip()
                        if text and 3 < len(text) < 50 and '\n' not in text:
                            if self._is_real_amenity(text):
                                popular.append(text)
                                amenities.add(text)
        except:
            pass

        # Méthode 2: Section "Facilities"
        try:
            facilities_items = await page.query_selector_all(
                '.facilitiesChecklistSection li, .hotel_facilities__list li')
            for item in facilities_items:
                text = await item.inner_text()
                text = text.strip()
                if text and 3 < len(text) < 80:
                    if self._is_real_amenity(text):
                        amenities.add(text)
        except:
            pass

        # Méthode 3: Keywords communs (TRÈS SÉLECTIF)
        common_amenities = [
            'Free WiFi', 'Free Wi-Fi', 'Parking', 'Free parking', 'Restaurant', 'Bar',
            'Room service', 'Fitness center', 'Fitness centre', 'Gym', 'Spa',
            'Swimming pool', 'Pool', 'Air conditioning', 'Heating',
            'Non-smoking rooms', 'Family rooms', 'Pet-friendly', 'Pets allowed',
            'Airport shuttle', '24-hour front desk', 'Reception', 'Concierge',
            'Elevator', 'Lift', 'Terrace', 'Garden', 'Balcony',
            'Kitchen', 'Kitchenette', 'Coffee machine', 'Electric kettle',
            'Washing machine', 'Dryer', 'Iron', 'Ironing facilities',
            'Safe', 'Soundproof', 'Wheelchair accessible'
        ]

        # Chercher UNIQUEMENT dans les 20000 premiers caractères (zone de description)
        search_zone = html_content[:20000].lower()

        for amenity in common_amenities:
            if amenity.lower() in search_zone:
                amenities.add(amenity)

        # Filtrer et nettoyer
        amenities_cleaned = [a for a in amenities if self._is_real_amenity(a)]

        logger.debug(f"Équipements finaux: {len(amenities_cleaned)}")
        return amenities_cleaned, popular, []

    def _is_real_amenity(self, text: str) -> bool:
        """Validation STRICTE pour équipements."""
        if not text or len(text) < 3 or len(text) > 80:
            return False

        # Liste NOIRE extensive
        blacklist_keywords = [
            # Devises
            'dollar', 'euro', 'pound', 'franc', 'peso', 'yen', 'yuan', 'rupee', 'riyal', 'dirham',
            'krona', 'krone', 'zloty', 'forint', 'leu', 'dinar', 'shekel', 'baht', 'ringgit',
            'won', 'currency', 'koruna',
            # Langues
            'english', 'français', 'español', 'deutsch', 'italiano', 'português', 'svenska',
            'dansk', 'norsk', 'suomi', 'polski', 'magyar', 'čeština', 'slovenčina',
            'hrvatski', 'srpski', 'român', 'bahasa', 'tiếng', 'việt',
            # Jours/Mois
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
            'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
            'september', 'october', 'november', 'december',
            'lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche',
            # Autres
            'genius', 'booking', 'hotel_', 'offline', 'openid', 'profile', 'email', 'phone',
            'address', 'unknown', 'sofort', 'paypal', 'qiwi', 'webmoney', 'alipay', 'wechat',
            'ideal', 'giropay', 'bancontact', 'tenpay', 'yandex',
            # Types de propriété
            'hotels', 'apartment', 'studio', 'suite', 'room', 'dorm', 'vacation home',
            'bungalow', 'villa', 'chalet', 'tent', 'trailer',
            # Modes de transport
            'gondola', 'chairlift', 'cablecar', 'funicular', 't-bar', 'j-bar', 'drag lift',
            # Divers
            'check-in', 'checkin', 'checkout', 'breakfast', 'dinner', 'meals', 'luggage',
            'select', 'upgrade', 'name', 'genius', 'loud', 'quiet', 'heat', 'cold', 'noise',
            'clean', 'comfort', 'location', 'value', 'staff', 'entire', 'tower', 'window',
            'total', 'business', 'economy', 'premium', 'first class'
        ]

        text_lower = text.lower()

        # Rejeter si contient un keyword de la blacklist
        for keyword in blacklist_keywords:
            if keyword in text_lower:
                return False

        # Rejeter si c'est un pays ou une région
        countries = ['france', 'paris', 'ile de france', 'georgia', 'abkhazia']
        if any(c in text_lower for c in countries):
            return False

        # Rejeter si commence par minuscule ou nombre
        if text[0].islower() or text[0].isdigit():
            return False

        # Rejeter si contient des caractères invalides
        if any(c in text for c in ['<', '>', '{', '}', '"', 'http', '.com', 'meter)']):
            return False

        return True

    async def _extract_rooms_enhanced(self, page, html_content: str) -> List[RoomOption]:
        rooms = []
        await page.wait_for_timeout(2000)

        try:
            room_rows = await page.query_selector_all('tr.js-rt-block-row, tr[data-room-id]')

            for row in room_rows[:20]:
                full_text = await row.inner_text()

                room_type = "Unknown Room"
                try:
                    name_elem = await row.query_selector('.hprt-roomtype-link')
                    if name_elem:
                        room_type = (await name_elem.inner_text()).strip()
                except:
                    pass

                if room_type == "Unknown Room":
                    for line in full_text.split('\n'):
                        if any(kw in line for kw in ['Bedroom', 'Room', 'Suite', 'Apartment']):
                            room_type = line.strip()
                            break

                price = None
                try:
                    price_elem = await row.query_selector('.bui-price-display__value')
                    if price_elem:
                        price_text = await price_elem.inner_text()
                        price = self._parse_price(price_text)
                except:
                    pass

                if not price:
                    price_matches = re.findall(r'€\s*(\d+)', full_text)
                    if price_matches:
                        price = float(price_matches[0])

                capacity = None
                cap_match = re.search(r'(\d+)\s*(?:guest|adult)', full_text.lower())
                if cap_match:
                    capacity = int(cap_match.group(1))

                room_size = None
                size_match = re.search(r'(\d+)\s*m[²2]', full_text)
                if size_match:
                    room_size = f"{size_match.group(1)} m²"

                bed_type = None
                if 'full bed' in full_text.lower():
                    bed_type = "Full bed"
                elif 'sofa bed' in full_text.lower():
                    bed_type = "Sofa bed"

                amenities = []
                for kw in ['WiFi', 'TV', 'Kitchen', 'Bathroom', 'View', 'Air conditioning']:
                    if kw.lower() in full_text.lower():
                        amenities.append(kw)

                cancellation = None
                refundable = False
                if 'free cancellation' in full_text.lower():
                    cancellation = "Free cancellation"
                    refundable = True
                elif 'non-refundable' in full_text.lower():
                    cancellation = "Non-refundable"

                breakfast = 'breakfast' in full_text.lower() and 'included' in full_text.lower()

                room = RoomOption(
                    room_type=room_type,
                    price=price,
                    capacity=capacity,
                    bed_type=bed_type,
                    room_size=room_size,
                    amenities=amenities,
                    cancellation_policy=cancellation,
                    breakfast_included=breakfast,
                    refundable=refundable
                )

                rooms.append(room)
        except Exception as e:
            logger.warning(f"Erreur rooms: {e}")

        return rooms

    def _parse_price(self, price_text: str) -> Optional[float]:
        try:
            cleaned = price_text.replace('€', '').replace('EUR', '').replace(',', '').strip()
            match = re.search(r'(\d+)', cleaned)
            return float(match.group(1)) if match else None
        except:
            return None

    async def _extract_policies(self, page, html_content: str) -> Optional[HotelPolicies]:
        policies = {}

        checkin_match = re.search(r'Check-in.*?(\d{1,2}:\d{2})', html_content, re.IGNORECASE)
        if checkin_match:
            policies['checkin_from'] = checkin_match.group(1)

        checkout_match = re.search(r'Check-out.*?(\d{1,2}:\d{2})', html_content, re.IGNORECASE)
        if checkout_match:
            policies['checkout_until'] = checkout_match.group(1)

        return HotelPolicies(**policies) if policies else None

    async def _extract_house_rules(self, page, html_content: str) -> List[str]:
        rules = []

        try:
            items = await page.query_selector_all('.hotel-rules__item')
            for item in items[:20]:
                text = await item.inner_text()
                text = text.strip()
                if text and 5 < len(text) < 200:
                    rules.append(text)
        except:
            pass

        return rules

    async def _extract_nearby_ultra_fixed(self, page, html_content: str) -> List[NearbyAttraction]:
        """ULTRA-FIXÉ: Attractions propres et réelles."""
        attractions = []

        try:
            # Méthode 1: Section "Area info" VISIBLE
            area_section = await page.query_selector('div:has-text("Area info"), div:has-text("What\'s nearby")')
            if area_section:
                parent = await area_section.query_selector('xpath=../..')
                if parent:
                    items = await parent.query_selector_all('tr, li')

                    for item in items[:50]:
                        text = await item.inner_text()
                        text = text.strip()

                        # Format: "Nom Distance"
                        match = re.match(r'^([A-Z][A-Za-z\s\-\'À-ÿ]{2,60}?)\s+([\d.,]+\s*(?:km|m))$', text)
                        if match:
                            name = match.group(1).strip()
                            distance = match.group(2).strip()

                            if self._is_valid_attraction(name):
                                category = self._categorize_attraction(name)
                                attractions.append(NearbyAttraction(
                                    name=name,
                                    distance=distance,
                                    category=category
                                ))
        except:
            pass

        # Méthode 2: Fallback - Chercher patterns spécifiques
        if len(attractions) < 3:
            patterns = [
                r'([A-Z][A-Za-z\s\-\']+(?:Museum|Station|Airport|Center|Centre|Tower|Park|Garden|Cathedral|Palace|Theatre|Opera|Gallery))\s+([\d.,]+\s*(?:km|m))',
                r'(Louvre|Eiffel Tower|Notre[ -]Dame|Arc de Triomphe|Sacré[ -]Cœur|Pantheon|Versailles)\s+([\d.,]+\s*(?:km|m))'
            ]

            for pattern in patterns:
                matches = re.findall(pattern, html_content[:30000])
                for name, distance in matches[:20]:
                    name = name.strip()
                    if self._is_valid_attraction(name) and name not in [a.name for a in attractions]:
                        category = self._categorize_attraction(name)
                        attractions.append(NearbyAttraction(
                            name=name,
                            distance=distance.strip(),
                            category=category
                        ))

        logger.debug(f"Attractions: {len(attractions)}")
        return attractions

    def _is_valid_attraction(self, name: str) -> bool:
        """Validation stricte des noms d'attractions."""
        if not name or len(name) < 3 or len(name) > 80:
            return False

        blacklist = [
            'located in', 'prime location', 'extra long', 'select up to',
            'great choice', 'no account', 'it only takes', 'we have more',
            'golf course (within', 'hello', 'output', 'property', '<b>', '</b>',
            'best of', 'subtitle', 'item"', 'the parkings', 'center, the apartment'
        ]

        name_lower = name.lower()
        for keyword in blacklist:
            if keyword in name_lower:
                return False

        # Doit commencer par majuscule
        if not name[0].isupper():
            return False

        # Pas trop de mots (max 6)
        if len(name.split()) > 6:
            return False

        return True

    def _categorize_attraction(self, name: str) -> str:
        name_lower = name.lower()

        if any(kw in name_lower for kw in ['restaurant', 'café', 'bar', 'bistro']):
            return "Restaurant"
        elif any(kw in name_lower for kw in ['museum', 'musée', 'gallery', 'louvre', 'orsay']):
            return "Museum"
        elif any(kw in name_lower for kw in ['metro', 'subway', 'station', 'train', 'gare', 'rail']):
            return "Public transport"
        elif any(kw in name_lower for kw in ['airport', 'aéroport']):
            return "Airport"
        elif any(kw in name_lower for kw in ['park', 'garden', 'jardin', 'parc']):
            return "Park"
        elif any(kw in name_lower for kw in
                 ['tower', 'tour', 'eiffel', 'cathedral', 'cathédrale', 'notre-dame', 'opera', 'opéra', 'arc',
                  'pantheon']):
            return "Monument"
        else:
            return "Attraction"

    async def _extract_languages(self, page, html_content: str) -> List[str]:
        languages = []

        try:
            lang_elem = await page.query_selector('[data-testid="languages-spoken"]')
            if lang_elem:
                text = await lang_elem.inner_text()
                langs = re.split(r'[,•\n]', text)
                for lang in langs:
                    lang = lang.strip()
                    if 2 < len(lang) < 30 and 'languages' not in lang.lower():
                        languages.append(lang)
        except:
            pass

        return languages

    async def _extract_contact(self, html_content: str) -> tuple:
        phone = None
        email = None

        phone_match = re.search(r'tel:\s*([+\d\s()-]{8,20})', html_content)
        if phone_match:
            phone = phone_match.group(1).strip()

        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', html_content)
        if email_match:
            email = email_match.group(1).strip()

        return phone, email