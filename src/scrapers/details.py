"""
Scraper FINAL AMÉLIORÉ - Extraction précise avec bons sélecteurs
Version corrigée pour attractions, house rules, équipements, langues
"""

from playwright.async_api import Page, Browser
from playwright.async_api import async_playwright
from config.settings import settings
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
import logging
import re
import json
import html as html_module

from src.models.hotel import (
    HotelDetailsRequest, HotelDetails, Address, ReviewScores,
    RoomOption, NearbyAttraction, HotelPolicies
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GuestReview:
    """Modèle pour un avis client."""

    def __init__(self, reviewer_name: str, reviewer_country: str, review_date: str,
                 positive_text: str, negative_text: str, score: float, tags: List[str] = None):
        self.reviewer_name = reviewer_name
        self.reviewer_country = reviewer_country
        self.review_date = review_date
        self.positive_text = positive_text
        self.negative_text = negative_text
        self.score = score
        self.tags = tags or []


class DetailsScraper:
    """Scraper FINAL avec extraction précise."""

    def __init__(self):
        self.browser: Browser = None
        self.context = None
        self.playwright = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=settings.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        self.context = await self.browser.new_context(
            user_agent=settings.user_agent,
            viewport={'width': 1920, 'height': 1080},
            locale='en-US'
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def get_hotel_details(self, request: HotelDetailsRequest) -> Tuple[HotelDetails, List[GuestReview]]:
        """Extraction complète avec sélecteurs précis."""
        page = await self.context.new_page()

        try:
            url = self._build_hotel_url(request)
            logger.info(f"🔍 Scraping: {url}")

            await page.goto(url, wait_until='domcontentloaded', timeout=60000)
            await page.wait_for_timeout(5000)

            await self._mega_scroll(page)

            html_content = await page.content()
            json_data = self._extract_all_json_ld(html_content)

            logger.info("📊 Extraction précise...")

            name = await self._extract_name(page, json_data)
            address = await self._extract_address(page, html_content, json_data)
            description = await self._extract_description_full(page, html_content, json_data)
            property_type = await self._extract_property_type(page, html_content, json_data)
            star_rating = await self._extract_star_rating_complete(page, html_content, json_data)

            review_score, review_count, review_category = await self._extract_reviews(
                page, html_content, json_data
            )

            review_scores_detail = await self._extract_detailed_scores_guaranteed(page, html_content)

            images, main_image = await self._extract_images_decoded(page, html_content, json_data)

            # ÉQUIPEMENTS - extraction ciblée sur les vraies facilities
            amenities, popular_amenities = await self._extract_amenities_targeted(page, html_content, json_data)

            rooms = await self._extract_rooms_complete(page, html_content)
            cheapest_price = min([r.price for r in rooms if r.price], default=None)

            policies = await self._extract_policies(page, html_content)

            # HOUSE RULES - ciblage précis sur .b0400e5749
            house_rules = await self._extract_house_rules_targeted(page, html_content)

            # ATTRACTIONS - ciblage précis sur [data-testid="poi-block-list"]
            nearby_attractions = await self._extract_nearby_targeted(page, html_content)

            # LANGUES - extraction ciblée
            languages_spoken = await self._extract_languages_targeted(page, html_content)

            phone, email = await self._extract_contact_complete(page, html_content)

            guest_reviews = await self._extract_all_reviews_guaranteed(page, html_content)

            logger.info(f"✅ {name} | {len(guest_reviews)} avis | {len(images)} images | {len(amenities)} équipements")

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
            logger.error(f"❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            await page.close()

    async def _mega_scroll(self, page: Page):
        """Scroll complet."""
        try:
            for i in range(10):
                await page.evaluate(f"window.scrollTo(0, {i * 1200})")
                await page.wait_for_timeout(400)

            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)

            try:
                read_all_btn = await page.query_selector('[data-testid="fr-read-all-reviews"], button:has-text("Read all reviews")')
                if read_all_btn:
                    await read_all_btn.click()
                    await page.wait_for_timeout(2000)
            except:
                pass
        except:
            pass

    def _build_hotel_url(self, request: HotelDetailsRequest) -> str:
        # Si l'ID est déjà une URL complète
        if "booking.com" in request.hotel_id and "http" in request.hotel_id:
            base_url = request.hotel_id.split('?')[0]
        else:
            # Construction standard avec code pays
            country = request.country_code if request.country_code else "fr"
            base_url = f"{settings.booking_base_url}/hotel/{country}/{request.hotel_id}.html"

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

    def _extract_all_json_ld(self, html: str) -> List[dict]:
        json_blocks = []
        try:
            pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
            matches = re.findall(pattern, html, re.DOTALL)
            for match in matches:
                try:
                    json_blocks.append(json.loads(match))
                except:
                    pass
        except:
            pass
        return json_blocks

    async def _extract_name(self, page: Page, json_data: List[dict]) -> str:
        for jdata in json_data:
            if jdata.get('name') and len(str(jdata['name'])) > 3:
                return str(jdata['name']).strip()

        selectors = ['h2[data-testid="property-name"]', 'h1[data-testid="title"]', 'h2.pp-header__title']
        for sel in selectors:
            try:
                elem = await page.query_selector(sel)
                if elem:
                    text = await elem.inner_text()
                    if text and len(text) > 3:
                        return text.strip()
            except:
                pass

        return "Unknown Hotel"

    async def _extract_address(self, page: Page, html: str, json_data: List[dict]) -> Optional[Address]:
        full_address = None
        lat, lon = None, None

        for jdata in json_data:
            if jdata.get('address') and isinstance(jdata['address'], dict):
                addr = jdata['address']
                parts = [str(addr.get(k, '')) for k in ['streetAddress', 'addressLocality', 'postalCode', 'addressCountry'] if addr.get(k)]
                if parts:
                    full_address = ', '.join(parts)

            if jdata.get('geo') and isinstance(jdata['geo'], dict):
                lat = jdata['geo'].get('latitude')
                lon = jdata['geo'].get('longitude')

        if not lat:
            for pattern in [r'"latitude":\s*([-\d.]+)', r'"lat":\s*([-\d.]+)']:
                match = re.search(pattern, html)
                if match:
                    lat = float(match.group(1))
                    break

        if not lon:
            for pattern in [r'"longitude":\s*([-\d.]+)', r'"lng":\s*([-\d.]+)']:
                match = re.search(pattern, html)
                if match:
                    lon = float(match.group(1))
                    break

        return Address(full_address=full_address, latitude=lat, longitude=lon) if (full_address or lat) else None

    async def _extract_description_full(self, page: Page, html: str, json_data: List[dict]) -> Optional[str]:
        descriptions = []

        for jdata in json_data:
            if jdata.get('description'):
                desc = jdata['description']
                if isinstance(desc, str) and len(desc) > 50:
                    descriptions.append(desc)

        try:
            desc_container = await page.query_selector('#property_description_content, [data-testid="property-description"]')
            if desc_container:
                full_text = await desc_container.inner_text()
                if full_text and len(full_text) > 50:
                    descriptions.append(full_text.strip())
        except:
            pass

        desc_selectors = ['.hp_desc_main_content', '[data-capla-component*="description"]']
        for selector in desc_selectors:
            try:
                section = await page.query_selector(selector)
                if section:
                    text = await section.inner_text()
                    if text and len(text) > 50:
                        descriptions.append(text.strip())
            except:
                pass

        unique_desc = []
        seen = set()
        for desc in descriptions:
            normalized = desc[:100].lower()
            if normalized not in seen:
                seen.add(normalized)
                unique_desc.append(desc)

        return '\n\n'.join(unique_desc) if unique_desc else None

    async def _extract_property_type(self, page: Page, html: str, json_data: List[dict]) -> Optional[str]:
        for jdata in json_data:
            ptype = jdata.get('@type')
            if ptype and ptype in ['Hotel', 'Apartment', 'Resort', 'BedAndBreakfast', 'Hostel']:
                return ptype

        keywords = {
            'Apartment': ['apartment', 'flat', 'appartement'],
            'Hotel': ['hotel', 'hôtel'],
            'Resort': ['resort'],
            'Hostel': ['hostel', 'auberge'],
            'Villa': ['villa'],
            'Guesthouse': ['guest house', 'guesthouse']
        }

        search_text = html[:10000].lower()

        for category, terms in keywords.items():
            for term in terms:
                if term in search_text:
                    return category

        try:
            badge = await page.query_selector('[data-testid="property-type-badge"]')
            if badge:
                text = await badge.inner_text()
                if text and len(text) < 30:
                    return text.strip()
        except:
            pass

        return "Hotel"

    async def _extract_star_rating_complete(self, page: Page, html: str, json_data: List[dict]) -> Optional[int]:
        for jdata in json_data:
            if jdata.get('starRating'):
                try:
                    rating = jdata['starRating']
                    if isinstance(rating, dict):
                        rating = rating.get('ratingValue')
                    rating_int = int(float(rating))
                    if 1 <= rating_int <= 5:
                        return rating_int
                except:
                    pass

        try:
            stars = await page.query_selector_all('[aria-label*="star" i]')
            if 1 <= len(stars) <= 5:
                return len(stars)
        except:
            pass

        try:
            star_icons = await page.query_selector_all('.bui-star-rating__icon, svg[data-testid="star"]')
            if 1 <= len(star_icons) <= 5:
                return len(star_icons)
        except:
            pass

        star_patterns = [
            r'(\d)-star',
            r'(\d)\s+stars?',
            r'"starRating"[:\s]*"?(\d)"?',
        ]

        for pattern in star_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                try:
                    stars = int(match.group(1))
                    if 1 <= stars <= 5:
                        return stars
                except:
                    pass

        return None

    async def _extract_reviews(self, page: Page, html: str, json_data: List[dict]) -> Tuple[Optional[float], Optional[int], Optional[str]]:
        score, count, category = None, None, None

        for jdata in json_data:
            if jdata.get('aggregateRating'):
                rating = jdata['aggregateRating']
                if isinstance(rating, dict):
                    score = rating.get('ratingValue')
                    count = rating.get('reviewCount')

        if not score:
            try:
                score_elem = await page.query_selector('[data-testid="review-score-badge"], .b5cd09854e.d10a6220b4')
                if score_elem:
                    text = await score_elem.inner_text()
                    match = re.search(r'(\d+\.?\d*)', text)
                    if match:
                        score = float(match.group(1))
            except:
                pass

        if not count:
            count_patterns = [
                r'(\d[\d,]+)\s+(?:reviews?|avis)',
                r'"reviewCount":\s*(\d+)',
            ]
            for pattern in count_patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    count = int(match.group(1).replace(',', ''))
                    break

        if score:
            categories = ['Exceptional', 'Wonderful', 'Excellent', 'Very good', 'Fabulous', 'Superb', 'Good']
            for cat in categories:
                if re.search(rf'{re.escape(str(score))}[^a-zA-Z]*{cat}', html, re.IGNORECASE):
                    category = cat
                    break

        return score, count, category

    async def _extract_detailed_scores_guaranteed(self, page: Page, html: str) -> Optional[ReviewScores]:
        scores = {}

        categories = {
            'staff': ['Staff', 'Personnel'],
            'facilities': ['Facilities', 'Équipements', 'Equipements'],
            'cleanliness': ['Cleanliness', 'Propreté', 'Proprete'],
            'comfort': ['Comfort', 'Confort'],
            'value_for_money': ['Value for money', 'Rapport qualité', 'Value'],
            'location': ['Location', 'Emplacement'],
            'wifi': ['WiFi', 'Wi-Fi', 'Free WiFi', 'Free Wifi']
        }

        try:
            subscore_items = await page.query_selector_all('[data-testid="review-subscore"]')

            for item in subscore_items:
                text = await item.inner_text()

                for field, labels in categories.items():
                    if field in scores:
                        continue

                    for label in labels:
                        if label in text:
                            score_match = re.search(r'\b(\d+\.?\d*)\b', text)
                            if score_match:
                                value = float(score_match.group(1))
                                if 0 <= value <= 10:
                                    scores[field] = value
                                    break
        except:
            pass

        for field, labels in categories.items():
            if field in scores:
                continue

            for label in labels:
                pattern = rf'{re.escape(label)}[^\d]*?(\d+\.?\d*)'
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    try:
                        value = float(match.group(1))
                        if 0 <= value <= 10:
                            scores[field] = value
                            break
                    except:
                        pass

        logger.info(f"📊 Scores détaillés: {len(scores)} catégories")

        return ReviewScores(**scores) if scores else None

    async def _extract_images_decoded(self, page: Page, html: str, json_data: List[dict]) -> Tuple[List[str], Optional[str]]:
        images_set = set()
        main_image = None

        img_pattern = r'(https://cf\.bstatic\.com/xdata/images/hotel/[^\s"\'<>]+\.(?:jpg|jpeg|png|webp)\?[^\s"\'<>]+)'

        all_urls = re.findall(img_pattern, html)

        seen_ids = set()

        for url in all_urls:
            url = html_module.unescape(url)

            id_match = re.search(r'/(\d+)\.(?:jpg|jpeg|png|webp)', url)
            if not id_match:
                continue

            img_id = id_match.group(1)

            if img_id in seen_ids:
                continue

            if 'k=' in url and 'o=' in url:
                seen_ids.add(img_id)

                url = re.sub(r'/square\d+/', '/max1024x768/', url)
                url = re.sub(r'/max\d+/', '/max1024x768/', url)

                images_set.add(url)

                if not main_image:
                    main_image = url

        images = list(images_set)

        logger.info(f"📸 {len(images)} images")

        return images[:50], main_image

    async def _extract_amenities_targeted(self, page: Page, html: str, json_data: List[dict]) -> Tuple[List[str], List[str]]:
        """ÉQUIPEMENTS - Extraction exhaustive complète."""
        amenities = set()
        popular = []

        # JSON-LD
        for jdata in json_data:
            if jdata.get('amenityFeature'):
                features = jdata['amenityFeature']
                if isinstance(features, list):
                    for feat in features:
                        if isinstance(feat, dict) and feat.get('name'):
                            name = feat['name']
                            if 3 < len(name) < 60:
                                amenities.add(name)

        # Section "Most popular facilities"
        try:
            popular_wrapper = await page.query_selector('[data-testid="property-most-popular-facilities-wrapper"]')
            if popular_wrapper:
                items = await popular_wrapper.query_selector_all('li .f6b6d2a959')
                for item in items:
                    text = await item.inner_text()
                    text = text.strip()
                    if 3 < len(text) < 60:
                        amenities.add(text)
                        if len(popular) < 15:
                            popular.append(text)
        except:
            pass

        # Toutes les sections de facilities par catégorie
        try:
            facility_groups = await page.query_selector_all('[data-testid="facility-group-container"]')

            for group in facility_groups:
                try:
                    items = await group.query_selector_all('li .f6b6d2a959')
                    for item in items:
                        text = await item.inner_text()
                        text = text.strip()
                        if 3 < len(text) < 60:
                            amenities.add(text)
                except:
                    continue
        except:
            pass

        # Équipements dans les chambres - sélecteur .hprt-facilities-facility
        try:
            room_facilities = await page.query_selector_all('.hprt-facilities-facility')
            for facility in room_facilities:
                try:
                    data_name = await facility.get_attribute('data-name-en')
                    if data_name and 3 < len(data_name) < 60:
                        amenities.add(data_name)
                except:
                    pass
        except:
            pass

        # Liste .hprt-facilities-others
        try:
            others_list = await page.query_selector('.hprt-facilities-others')
            if others_list:
                items = await others_list.query_selector_all('li .hprt-facilities-facility')
                for item in items:
                    try:
                        data_name = await item.get_attribute('data-name-en')
                        if data_name and 3 < len(data_name) < 60:
                            amenities.add(data_name)
                        else:
                            text_elem = await item.query_selector('.other_facility_badge--default_color')
                            if text_elem:
                                text = await text_elem.inner_text()
                                text = text.strip()
                                if 3 < len(text) < 60:
                                    amenities.add(text)
                    except:
                        pass
        except:
            pass

        cleaned = sorted(list(amenities))

        logger.info(f"🔧 {len(cleaned)} équipements")

        return cleaned, popular[:15]

    async def _extract_rooms_complete(self, page: Page, html: str) -> List[RoomOption]:
        rooms = []

        try:
            await page.wait_for_selector('tr[data-room-id], .hprt-table tr', timeout=5000)
        except:
            pass

        room_rows = await page.query_selector_all('tr[data-room-id], tr.js-rt-block-row')

        for row in room_rows[:30]:
            try:
                text = await row.inner_text()

                room_type = "Unknown Room"
                try:
                    name_elem = await row.query_selector('.hprt-roomtype-link, [data-testid="room-name"]')
                    if name_elem:
                        room_type = (await name_elem.inner_text()).strip()
                except:
                    pass

                price = None
                try:
                    price_elem = await row.query_selector('.bui-price-display__value, [data-testid="price"]')
                    if price_elem:
                        price_text = await price_elem.inner_text()
                        price = self._parse_price(price_text)
                except:
                    pass

                if not price:
                    price_matches = re.findall(r'[€$£]\s*(\d[\d,]*)', text)
                    if price_matches:
                        price = float(price_matches[0].replace(',', ''))

                capacity = None
                cap_patterns = [
                    r'(\d+)\s+(?:adults?|guests?|persons?)',
                    r'Sleeps\s+(\d+)',
                    r'Max\s+(\d+)',
                    r'x\s+(\d+)'
                ]

                for pattern in cap_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        capacity = int(match.group(1))
                        break

                if not capacity and 'solo' in room_type.lower():
                    capacity = 1
                elif not capacity and 'double' in room_type.lower():
                    capacity = 2

                room_size = None
                size_match = re.search(r'(\d+)\s*m[²2]', text)
                if size_match:
                    room_size = f"{size_match.group(1)} m²"

                bed_type = None
                bed_keywords = {
                    'King bed': ['king bed'],
                    'Queen bed': ['queen bed'],
                    'Full bed': ['full bed', 'double bed'],
                    'Twin beds': ['twin beds', '2 single beds'],
                    'Sofa bed': ['sofa bed']
                }

                text_lower = text.lower()
                for bed, keywords in bed_keywords.items():
                    if any(kw in text_lower for kw in keywords):
                        bed_type = bed
                        break

                amenities = []
                for kw in ['WiFi', 'TV', 'Kitchen', 'Bathroom', 'View', 'Air conditioning', 'Heating', 'Balcony', 'Bath', 'Shower']:
                    if kw.lower() in text_lower:
                        amenities.append(kw)

                cancellation = None
                refundable = False

                if 'free cancellation' in text_lower:
                    cancellation = "Free cancellation"
                    refundable = True
                elif 'non-refundable' in text_lower or 'non refundable' in text_lower:
                    cancellation = "Non-refundable"

                breakfast = ('breakfast' in text_lower) and ('included' in text_lower)

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

            except:
                continue

        return rooms

    def _parse_price(self, price_text: str) -> Optional[float]:
        try:
            cleaned = re.sub(r'[^\d.,]', '', price_text)
            cleaned = cleaned.replace(',', '')
            match = re.search(r'(\d+(?:\.\d+)?)', cleaned)
            if match:
                return float(match.group(1))
        except:
            pass
        return None

    async def _extract_policies(self, page: Page, html: str) -> Optional[HotelPolicies]:
        policies = {}

        checkin_match = re.search(r'Check-in.*?(\d{1,2}:\d{2})', html, re.IGNORECASE)
        if checkin_match:
            policies['checkin_from'] = checkin_match.group(1)

        checkout_match = re.search(r'Check-out.*?(\d{1,2}:\d{2})', html, re.IGNORECASE)
        if checkout_match:
            policies['checkout_until'] = checkout_match.group(1)

        return HotelPolicies(**policies) if policies else None

    async def _extract_house_rules_targeted(self, page: Page, html: str) -> List[str]:
        """HOUSE RULES - Ciblage précis sur .b0400e5749."""
        rules = []

        try:
            # Cibler spécifiquement les blocs de règles
            rule_blocks = await page.query_selector_all('.b0400e5749')

            for block in rule_blocks:
                # Titre de la règle
                try:
                    title_elem = await block.query_selector('.e7addce19e')
                    if title_elem:
                        title = (await title_elem.inner_text()).strip()

                        # Contenu de la règle
                        content_elem = await block.query_selector('.c92998be48, .da7e3382bac')
                        if content_elem:
                            content = (await content_elem.inner_text()).strip()

                            # Combiner titre + contenu
                            if title and content:
                                full_rule = f"{title}: {content}"
                                if len(full_rule) > 10 and len(full_rule) < 300:
                                    rules.append(full_rule)
                except:
                    continue
        except:
            pass

        logger.info(f"📋 {len(rules)} règles")

        return rules[:30]

    async def _extract_nearby_targeted(self, page: Page, html: str) -> List[NearbyAttraction]:
        """ATTRACTIONS - Ciblage précis sur [data-testid="poi-block-list"]."""
        attractions = []
        seen = set()

        try:
            # Cibler les listes POI
            poi_lists = await page.query_selector_all('[data-testid="poi-block-list"]')

            for poi_list in poi_lists:
                # Trouver la catégorie
                try:
                    parent_block = await poi_list.query_selector('xpath=ancestor::div[@data-testid="poi-block"]')
                    if not parent_block:
                        parent_block = await poi_list.query_selector('xpath=ancestor::div[2]')

                    category = "Attraction"
                    if parent_block:
                        try:
                            category_elem = await parent_block.query_selector('h3 div')
                            if category_elem:
                                category_text = (await category_elem.inner_text()).strip()

                                # Mapper les catégories
                                if 'restaurant' in category_text.lower() or 'cafe' in category_text.lower():
                                    category = "Restaurant"
                                elif 'transit' in category_text.lower() or 'transport' in category_text.lower():
                                    category = "Public transport"
                                elif 'airport' in category_text.lower():
                                    category = "Airport"
                                elif 'natural' in category_text.lower():
                                    category = "Park"
                                elif 'attraction' in category_text.lower():
                                    category = "Attraction"
                                else:
                                    category = category_text
                        except:
                            pass

                    # Extraire chaque item
                    items = await poi_list.query_selector_all('li')

                    for item in items:
                        try:
                            # Nom de l'attraction
                            name_elem = await item.query_selector('.d1bc97eb82, .aa225776f2')
                            if not name_elem:
                                continue

                            name_text = await name_elem.inner_text()
                            name = name_text.strip()

                            # Distance
                            distance_elem = await item.query_selector('.a0a56631d6, .b99b6ef58f')
                            distance = "Unknown"
                            if distance_elem:
                                distance = (await distance_elem.inner_text()).strip()

                            # Validation
                            if len(name) > 2 and name not in seen:
                                seen.add(name)
                                attractions.append(NearbyAttraction(
                                    name=name,
                                    distance=distance,
                                    category=category
                                ))
                        except:
                            continue
                except:
                    continue
        except:
            pass

        logger.info(f"🗺️  {len(attractions)} attractions")

        return attractions[:100]

    async def _extract_languages_targeted(self, page: Page, html: str) -> List[str]:
        """LANGUES - Extraction ciblée."""
        languages = []

        # Cibler la section "Languages Spoken"
        try:
            lang_groups = await page.query_selector_all('[data-testid="facility-group-container"]')

            for group in lang_groups:
                try:
                    h3 = await group.query_selector('h3')
                    if h3:
                        h3_text = await h3.inner_text()
                        if 'language' in h3_text.lower():
                            items = await group.query_selector_all('li .f6b6d2a959')
                            for item in items:
                                lang = await item.inner_text()
                                lang = lang.strip()
                                if 2 < len(lang) < 30:
                                    languages.append(lang)
                            break
                except:
                    continue
        except:
            pass

        # Fallback regex patterns
        if not languages:
            try:
                lang_patterns = [
                    r'Languages?\s+spoken[:\s]+([A-Za-zÀ-ÿ,\s•·]+)',
                    r'Langues?\s+parlées[:\s]+([A-Za-zÀ-ÿ,\s•·]+)',
                ]

                for pattern in lang_patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        text = match.group(1)
                        langs = re.split(r'[,•·\n]', text)

                        for lang in langs[:15]:
                            lang = lang.strip()
                            if 2 < len(lang) < 30 and lang[0].isupper():
                                if not any(kw in lang.lower() for kw in ['hotel', 'overview', 'skip', 'booking']):
                                    languages.append(lang)
                        break
            except:
                pass

        logger.info(f"🗣️  {len(languages)} langues")

        return languages[:15]

    async def _extract_contact_complete(self, page: Page, html: str) -> Tuple[Optional[str], Optional[str]]:
        phone = None
        email = None

        phone_patterns = [
            r'tel:\s*([+\d\s()-]{8,20})',
            r'Phone:?\s*([+\d\s()-]{8,20})',
        ]

        for pattern in phone_patterns:
            match = re.search(pattern, html)
            if match:
                phone = match.group(1).strip()
                break

        email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        email_match = re.search(email_pattern, html)
        if email_match:
            email_candidate = email_match.group(1)
            if not any(x in email_candidate.lower() for x in ['png', 'jpg', 'gif', 'svg']):
                email = email_candidate

        return phone, email

    async def _extract_all_reviews_guaranteed(self, page: Page, html: str) -> List[GuestReview]:
        reviews = []

        try:
            featured_items = await page.query_selector_all('[data-testid="featuredreview"]')

            logger.info(f"💬 {len(featured_items)} featured reviews")

            for item in featured_items[:15]:
                try:
                    name = "Anonymous"
                    try:
                        name_elem = await item.query_selector('.b08850ce41.f546354b44')
                        if name_elem:
                            name = (await name_elem.inner_text()).strip()
                    except:
                        pass

                    country = "Unknown"
                    try:
                        country_elem = await item.query_selector('.d838fb5f41.aea5eccb71')
                        if country_elem:
                            country = (await country_elem.inner_text()).strip()
                    except:
                        pass

                    text = ""
                    try:
                        text_elem = await item.query_selector('[data-testid="featuredreview-text"] .b99b6ef58f')
                        if text_elem:
                            text = (await text_elem.inner_text()).strip()
                            text = text.replace('"', '').strip()
                    except:
                        pass

                    if name and text:
                        review = GuestReview(
                            reviewer_name=name,
                            reviewer_country=country,
                            review_date="Recent",
                            positive_text=text,
                            negative_text="",
                            score=0.0,
                            tags=[]
                        )
                        reviews.append(review)

                except:
                    continue
        except:
            pass

        try:
            full_reviews = await page.query_selector_all('.review_list_new_item_block, [data-testid="review-card"]')

            for item in full_reviews[:15]:
                try:
                    text = await item.inner_text()

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

                    date = "Unknown"
                    date_match = re.search(r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})', text)
                    if date_match:
                        date = date_match.group(1)

                    score = 0.0
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
                    negative = ""

                    try:
                        pos_elem = await item.query_selector('.review_pos')
                        if pos_elem:
                            positive = (await pos_elem.inner_text()).strip()
                    except:
                        pass

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
                            review_date=date,
                            positive_text=positive,
                            negative_text=negative,
                            score=score,
                            tags=[]
                        )
                        reviews.append(review)

                except:
                    continue
        except:
            pass

        logger.info(f"✅ {len(reviews)} avis total")

        return reviews