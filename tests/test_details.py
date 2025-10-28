"""
Test ultra-complet - Version corrigée sans modification du modèle.
Remplacer tests/test_details.py par ce fichier.
"""

import asyncio
import sys
from pathlib import Path
import json

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.scrapers.details import DetailsScraper
from src.models.hotel import HotelDetailsRequest

def print_header(text: str):
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)

async def test_complete_extraction():
    """Test affichant TOUTES les donnees extraites."""

    print("\n" + "#"*80)
    print("#  TEST EXTRACTION COMPLETE - BOOKING.COM")
    print("#"*80)

    request = HotelDetailsRequest(
        hotel_id="moder-flat-heart-of-iveme",
        checkin="2025-12-12",
        checkout="2025-12-15",
        adults=2,
        rooms=1
    )

    print(f"\n📍 Hotel ID: {request.hotel_id}")
    print(f"📅 Dates: {request.checkin} → {request.checkout}")
    print(f"👥 Occupants: {request.adults} adultes, {request.rooms} chambre(s)")
    print("\n⏳ Scraping en cours...\n")

    try:
        async with DetailsScraper() as scraper:
            # Le scraper retourne maintenant (HotelDetails, List[GuestReview])
            result, guest_reviews = await scraper.get_hotel_details(request)

        # === INFOS GÉNÉRALES ===
        print_header("📋 INFORMATIONS GÉNÉRALES")
        print(f"Nom: {result.name}")
        print(f"Type: {result.property_type or 'N/A'}")
        print(f"Etoiles: {result.star_rating if result.star_rating else 'N/A'}")
        print(f"URL: {result.url}")

        # === ADRESSE ===
        print_header("📍 ADRESSE & LOCALISATION")
        if result.address:
            print(f"Adresse: {result.address.full_address}")
            print(f"GPS: {result.address.latitude}, {result.address.longitude}")
        else:
            print("❌ Adresse non disponible")

        # === DESCRIPTION ===
        print_header("📝 DESCRIPTION")
        if result.description:
            desc_preview = result.description[:300] + "..." if len(result.description) > 300 else result.description
            print(desc_preview)
            print(f"\n[Total: {len(result.description)} caracteres]")
        else:
            print("❌ Description non disponible")

        # === AVIS & NOTES ===
        print_header(f"⭐ AVIS & NOTES")
        print(f"Note globale: {result.review_score}/10" if result.review_score else "❌ Note non disponible")
        print(f"Nombre d'avis: {result.review_count}" if result.review_count else "❌ Nombre non disponible")
        print(f"Categorie: {result.review_category}" if result.review_category else "❌ Categorie non disponible")

        if result.review_scores_detail:
            print("\n📊 Notes detaillees:")
            scores_dict = {
                'Personnel': result.review_scores_detail.staff,
                'Equipements': result.review_scores_detail.facilities,
                'Proprete': result.review_scores_detail.cleanliness,
                'Confort': result.review_scores_detail.comfort,
                'Rapport qualite/prix': result.review_scores_detail.value_for_money,
                'Emplacement': result.review_scores_detail.location,
                'WiFi': result.review_scores_detail.wifi
            }

            for label, score in scores_dict.items():
                if score:
                    bar = "█" * int(score) + "░" * (10 - int(score))
                    print(f"  {label:20s}: {score:4.1f}/10 [{bar}]")

        # === AVIS CLIENTS ===
        if guest_reviews:
            print_header(f"💬 AVIS CLIENTS ({len(guest_reviews)} avis extraits)")

            for idx, review in enumerate(guest_reviews, 1):
                print(f"\n--- AVIS #{idx} ---")
                print(f"👤 {review.reviewer_name} ({review.reviewer_country})")
                print(f"📅 {review.review_date}")
                print(f"⭐ Score: {review.score}/10")

                if review.tags:
                    print(f"🏷️  Tags: {', '.join(review.tags)}")

                if review.positive_text:
                    pos_preview = review.positive_text[:150] + "..." if len(review.positive_text) > 150 else review.positive_text
                    print(f"✅ Positif: {pos_preview}")

                if review.negative_text:
                    neg_preview = review.negative_text[:150] + "..." if len(review.negative_text) > 150 else review.negative_text
                    print(f"❌ Negatif: {neg_preview}")
        else:
            print_header("💬 AVIS CLIENTS")
            print("⚠️  Aucun avis extrait (la page peut ne pas afficher d'avis publics)")

        # === IMAGES ===
        print_header(f"📸 IMAGES ({len(result.images)} photos)")
        if result.main_image:
            print(f"\n🖼️  Image principale:")
            print(f"   {result.main_image}")

        if result.images:
            print(f"\n📷 Toutes les images:")
            for idx, img in enumerate(result.images[:10], 1):
                print(f"   [{idx:2d}] {img[:80]}...")

            if len(result.images) > 10:
                print(f"   ... et {len(result.images) - 10} autres images")

        # === ÉQUIPEMENTS ===
        print_header(f"🔧 ÉQUIPEMENTS ({len(result.amenities)} au total)")

        if result.popular_amenities:
            print(f"\n⭐ Equipements populaires:")
            for amenity in result.popular_amenities[:10]:
                print(f"   • {amenity}")

        if result.amenities:
            print(f"\n📋 Tous les equipements:")
            for i in range(0, min(len(result.amenities), 30), 3):
                row = result.amenities[i:i+3]
                print(f"   • {row[0]:30s}" +
                      (f"• {row[1]:30s}" if len(row) > 1 else "") +
                      (f"• {row[2]}" if len(row) > 2 else ""))

            if len(result.amenities) > 30:
                print(f"   ... et {len(result.amenities) - 30} autres equipements")

        # === CHAMBRES ===
        print_header(f"🛏️  CHAMBRES DISPONIBLES ({len(result.rooms)} types)")

        if result.cheapest_price:
            print(f"\n💰 Prix le moins cher: {result.cheapest_price} {result.currency}")

        if result.rooms:
            for idx, room in enumerate(result.rooms, 1):
                print(f"\n--- CHAMBRE #{idx} ---")
                print(f"Type: {room.room_type}")
                print(f"Prix: {room.price} {room.currency}" if room.price else "Prix: N/A")

                details = []
                if room.capacity:
                    details.append(f"👥 {room.capacity} pers.")
                if room.room_size:
                    details.append(f"📐 {room.room_size}")
                if room.bed_type:
                    details.append(f"🛏️  {room.bed_type}")

                if details:
                    print("Details: " + " | ".join(details))

                if room.breakfast_included:
                    print("🍳 Petit-dejeuner inclus")

                if room.refundable:
                    print("✅ Remboursable")
                else:
                    print("❌ Non remboursable")

                if room.cancellation_policy:
                    print(f"📋 {room.cancellation_policy}")

                if room.amenities:
                    print(f"Equipements: {', '.join(room.amenities)}")

        # === POLITIQUES ===
        print_header("📜 POLITIQUES & RÈGLES")

        if result.policies:
            print("⏰ Horaires:")
            if result.policies.checkin_from:
                print(f"   Check-in: {result.policies.checkin_from}")
            if result.policies.checkout_until:
                print(f"   Check-out: {result.policies.checkout_until}")

        if result.house_rules:
            print(f"\n📋 Regles de la maison ({len(result.house_rules)}):")
            for rule in result.house_rules[:10]:
                print(f"   • {rule}")

        # === À PROXIMITÉ ===
        print_header(f"🗺️  À PROXIMITÉ ({len(result.nearby_attractions)} lieux)")

        if result.nearby_attractions:
            by_category = {}
            for attr in result.nearby_attractions:
                cat = attr.category or "Autre"
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(attr)

            for category, attractions in sorted(by_category.items()):
                print(f"\n{category} ({len(attractions)}):")
                for attr in attractions[:10]:
                    print(f"   • {attr.name:40s} {attr.distance:>10s}")

        # === LANGUES & CONTACT ===
        print_header("🌍 LANGUES & CONTACT")

        if result.languages_spoken:
            print(f"Langues parlees: {', '.join(result.languages_spoken)}")

        print(f"Telephone: {result.phone if result.phone else 'Non disponible'}")
        print(f"Email: {result.email if result.email else 'Non disponible'}")

        # === RÉSUMÉ ===
        print_header("📊 RÉSUMÉ STATISTIQUE")
        stats = [
            f"Description: {len(result.description) if result.description else 0} caracteres",
            f"Images: {len(result.images)}",
            f"Equipements: {len(result.amenities)}",
            f"Chambres: {len(result.rooms)}",
            f"Attractions: {len(result.nearby_attractions)}",
            f"Regles: {len(result.house_rules)}",
            f"Langues: {len(result.languages_spoken)}",
            f"Avis extraits: {len(guest_reviews)}",
        ]

        for stat in stats:
            print(f"  • {stat}")

        # === EXPORT JSON ===
        print_header("💾 EXPORT JSON")

        result_dict = {
            "hotel_id": result.hotel_id,
            "name": result.name,
            "url": result.url,
            "property_type": result.property_type,
            "star_rating": result.star_rating,
            "address": {
                "full_address": result.address.full_address if result.address else None,
                "latitude": result.address.latitude if result.address else None,
                "longitude": result.address.longitude if result.address else None,
            } if result.address else None,
            "description": result.description,
            "review_score": result.review_score,
            "review_count": result.review_count,
            "review_category": result.review_category,
            "review_scores_detail": {
                "staff": result.review_scores_detail.staff if result.review_scores_detail else None,
                "facilities": result.review_scores_detail.facilities if result.review_scores_detail else None,
                "cleanliness": result.review_scores_detail.cleanliness if result.review_scores_detail else None,
                "comfort": result.review_scores_detail.comfort if result.review_scores_detail else None,
                "value_for_money": result.review_scores_detail.value_for_money if result.review_scores_detail else None,
                "location": result.review_scores_detail.location if result.review_scores_detail else None,
                "wifi": result.review_scores_detail.wifi if result.review_scores_detail else None,
            } if result.review_scores_detail else None,
            "images": result.images,
            "main_image": result.main_image,
            "amenities": result.amenities,
            "popular_amenities": result.popular_amenities,
            "rooms": [
                {
                    "room_type": r.room_type,
                    "price": r.price,
                    "currency": r.currency,
                    "capacity": r.capacity,
                    "bed_type": r.bed_type,
                    "room_size": r.room_size,
                    "amenities": r.amenities,
                    "breakfast_included": r.breakfast_included,
                    "refundable": r.refundable,
                    "cancellation_policy": r.cancellation_policy,
                }
                for r in result.rooms
            ],
            "nearby_attractions": [
                {
                    "name": a.name,
                    "distance": a.distance,
                    "category": a.category
                }
                for a in result.nearby_attractions
            ],
            "guest_reviews": [
                {
                    "reviewer_name": r.reviewer_name,
                    "reviewer_country": r.reviewer_country,
                    "review_date": r.review_date,
                    "positive_text": r.positive_text,
                    "negative_text": r.negative_text,
                    "score": r.score,
                    "tags": r.tags
                }
                for r in guest_reviews
            ] if guest_reviews else [],
            "cheapest_price": result.cheapest_price,
            "scrape_timestamp": result.scrape_timestamp
        }

        output_file = Path(__file__).parent.parent / "hotel_details_complete.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, indent=2, ensure_ascii=False)

        print(f"\n💾 JSON sauvegarde: {output_file}")
        print(f"   Taille: {output_file.stat().st_size / 1024:.1f} KB")

        print("\n" + "="*80)
        print("✅ TEST RÉUSSI - EXTRACTION COMPLÈTE")
        print("="*80)

        return True

    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_complete_extraction())
    exit(0 if success else 1)