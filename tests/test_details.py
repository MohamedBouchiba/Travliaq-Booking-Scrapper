"""
Script de test ultra-complet pour le scraper Booking.com ROBUSTE
Teste l'extraction complète de toutes les données
"""

import asyncio
import sys
from pathlib import Path
import json

# Ajouter le répertoire racine du projet au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Imports du projet
from src.scrapers.details import DetailsScraper
from src.models.hotel import HotelDetailsRequest



def print_section(title: str):
    """Affiche un séparateur de section."""
    print("\n" + "=" * 100)
    print(f"  {title}")
    print("=" * 100)


def format_list(items, max_items=10, indent=2):
    """Formate une liste pour l'affichage."""
    if not items:
        return "  ⚠️  Aucun élément"

    spaces = " " * indent
    output = []
    for idx, item in enumerate(items[:max_items], 1):
        output.append(f"{spaces}• {item}")

    if len(items) > max_items:
        output.append(f"{spaces}... et {len(items) - max_items} autres")

    return "\n".join(output)


async def test_complete_extraction():
    """Test d'extraction complète avec affichage détaillé."""

    print("\n" + "#" * 100)
    print("#  TEST EXTRACTION ROBUSTE - BOOKING.COM")
    print("#  Version: Ultra-Robuste Multi-Stratégies")
    print("#" * 100)

    # Configuration de la requête
    request = HotelDetailsRequest(
        hotel_id="moder-flat-heart-of-iveme",
        checkin="2025-12-12",
        checkout="2025-12-15",
        adults=2,
        rooms=1
    )

    print(f"\n📍 Configuration:")
    print(f"  • Hotel ID: {request.hotel_id}")
    print(f"  • Dates: {request.checkin} → {request.checkout}")
    print(f"  • Occupants: {request.adults} adultes, {request.rooms} chambre(s)")
    print("\n⏳ Lancement du scraping...")

    try:
        async with DetailsScraper() as scraper:
            hotel_details, guest_reviews = await scraper.get_hotel_details(request)

        # === INFORMATIONS GÉNÉRALES ===
        print_section("📋 INFORMATIONS GÉNÉRALES")
        print(f"Nom: {hotel_details.name}")
        print(f"Type: {hotel_details.property_type or 'Non disponible'}")
        print(f"Étoiles: {'⭐' * hotel_details.star_rating if hotel_details.star_rating else 'Non classé'}")
        print(f"URL: {hotel_details.url}")

        # === ADRESSE ===
        print_section("📍 ADRESSE & LOCALISATION")
        if hotel_details.address:
            print(f"Adresse complète: {hotel_details.address.full_address or 'Non disponible'}")
            if hotel_details.address.latitude and hotel_details.address.longitude:
                print(f"Coordonnées GPS: {hotel_details.address.latitude:.6f}, {hotel_details.address.longitude:.6f}")
            else:
                print("Coordonnées GPS: Non disponibles")
        else:
            print("⚠️  Adresse non disponible")

        # === DESCRIPTION ===
        print_section("📝 DESCRIPTION")
        if hotel_details.description:
            desc_length = len(hotel_details.description)
            if desc_length > 500:
                preview = hotel_details.description[:500] + "..."
            else:
                preview = hotel_details.description

            print(preview)
            print(f"\n📊 Longueur totale: {desc_length} caractères")
        else:
            print("⚠️  Description non disponible")

        # === AVIS & NOTES ===
        print_section("⭐ AVIS & NOTES GLOBALES")

        if hotel_details.review_score:
            score_bar = "█" * int(hotel_details.review_score) + "░" * (10 - int(hotel_details.review_score))
            print(f"Note globale: {hotel_details.review_score}/10  [{score_bar}]")
        else:
            print("Note globale: Non disponible")

        if hotel_details.review_count:
            print(f"Nombre d'avis: {hotel_details.review_count:,}")
        else:
            print("Nombre d'avis: Non disponible")

        if hotel_details.review_category:
            print(f"Catégorie: {hotel_details.review_category}")
        else:
            print("Catégorie: Non disponible")

        # === NOTES DÉTAILLÉES ===
        print_section("📊 NOTES DÉTAILLÉES PAR CATÉGORIE")

        if hotel_details.review_scores_detail:
            scores = hotel_details.review_scores_detail
            score_items = [
                ("Personnel", scores.staff),
                ("Équipements", scores.facilities),
                ("Propreté", scores.cleanliness),
                ("Confort", scores.comfort),
                ("Rapport qualité/prix", scores.value_for_money),
                ("Emplacement", scores.location),
                ("WiFi", scores.wifi)
            ]

            print()
            for label, score in score_items:
                if score is not None:
                    bar = "█" * int(score) + "░" * (10 - int(score))
                    print(f"  {label:22s}: {score:4.1f}/10  [{bar}]")
                else:
                    print(f"  {label:22s}: Non disponible")
        else:
            print("⚠️  Notes détaillées non disponibles")

        # === AVIS CLIENTS ===
        print_section(f"💬 AVIS CLIENTS ({len(guest_reviews)} avis extraits)")

        if guest_reviews:
            for idx, review in enumerate(guest_reviews[:5], 1):
                print(f"\n─── Avis #{idx} {'─' * 85}")
                print(f"👤 {review.reviewer_name} ({review.reviewer_country})")
                print(f"📅 {review.review_date}")

                if review.score:
                    print(f"⭐ Score: {review.score}/10")

                if review.tags:
                    print(f"🏷️  Tags: {', '.join(review.tags)}")

                if review.positive_text:
                    pos_preview = review.positive_text[:200] + "..." if len(review.positive_text) > 200 else review.positive_text
                    print(f"✅ Positif: {pos_preview}")

                if review.negative_text:
                    neg_preview = review.negative_text[:200] + "..." if len(review.negative_text) > 200 else review.negative_text
                    print(f"❌ Négatif: {neg_preview}")

            if len(guest_reviews) > 5:
                print(f"\n... et {len(guest_reviews) - 5} autres avis")
        else:
            print("⚠️  Aucun avis extrait (page sans avis publics)")

        # === IMAGES ===
        print_section(f"📸 IMAGES ({len(hotel_details.images)} photos)")

        if hotel_details.main_image:
            print(f"\n🖼️  Image principale:")
            print(f"   {hotel_details.main_image}")

        if hotel_details.images:
            print(f"\n📷 Galerie complète:")
            for idx, img_url in enumerate(hotel_details.images[:15], 1):
                short_url = img_url[:100] + "..." if len(img_url) > 100 else img_url
                print(f"   [{idx:2d}] {short_url}")

            if len(hotel_details.images) > 15:
                print(f"   ... et {len(hotel_details.images) - 15} autres images")
        else:
            print("⚠️  Aucune image disponible")

        # === ÉQUIPEMENTS ===
        print_section(f"🔧 ÉQUIPEMENTS & SERVICES ({len(hotel_details.amenities)} au total)")

        if hotel_details.popular_amenities:
            print(f"\n⭐ Équipements populaires ({len(hotel_details.popular_amenities)}):")
            print(format_list(hotel_details.popular_amenities))

        if hotel_details.amenities:
            print(f"\n📋 Tous les équipements ({len(hotel_details.amenities)}):")
            # Afficher en colonnes
            for i in range(0, min(len(hotel_details.amenities), 30), 3):
                row = hotel_details.amenities[i:i+3]
                line = "  • " + row[0].ljust(32)
                if len(row) > 1:
                    line += "• " + row[1].ljust(32)
                if len(row) > 2:
                    line += "• " + row[2]
                print(line)

            if len(hotel_details.amenities) > 30:
                print(f"  ... et {len(hotel_details.amenities) - 30} autres équipements")
        else:
            print("⚠️  Aucun équipement listé")

        # === CHAMBRES ===
        print_section(f"🛏️  CHAMBRES DISPONIBLES ({len(hotel_details.rooms)} types)")

        if hotel_details.cheapest_price:
            print(f"\n💰 Prix le moins cher: {hotel_details.cheapest_price:.2f} {hotel_details.currency}")

        if hotel_details.rooms:
            for idx, room in enumerate(hotel_details.rooms[:10], 1):
                print(f"\n─── Chambre #{idx} {'─' * 85}")
                print(f"📌 Type: {room.room_type}")

                if room.price:
                    print(f"💶 Prix: {room.price:.2f} {room.currency}")
                else:
                    print("💶 Prix: Non disponible")

                # Détails
                details = []
                if room.capacity:
                    details.append(f"👥 {room.capacity} pers.")
                if room.room_size:
                    details.append(f"📐 {room.room_size}")
                if room.bed_type:
                    details.append(f"🛏️  {room.bed_type}")

                if details:
                    print(f"📊 Détails: {' | '.join(details)}")

                # Services
                if room.breakfast_included:
                    print("🍳 Petit-déjeuner: Inclus")

                if room.refundable:
                    print("✅ Annulation: Remboursable")
                else:
                    print("❌ Annulation: Non remboursable")

                if room.cancellation_policy:
                    print(f"📋 Politique: {room.cancellation_policy}")

                # Équipements de la chambre
                if room.amenities:
                    print(f"🔧 Équipements: {', '.join(room.amenities[:10])}")
                    if len(room.amenities) > 10:
                        print(f"   ... et {len(room.amenities) - 10} autres")

            if len(hotel_details.rooms) > 10:
                print(f"\n... et {len(hotel_details.rooms) - 10} autres types de chambres")
        else:
            print("⚠️  Aucune chambre disponible pour ces dates")

        # === POLITIQUES ===
        print_section("📜 POLITIQUES & RÈGLES")

        if hotel_details.policies:
            print("\n⏰ Horaires:")
            if hotel_details.policies.checkin_from:
                print(f"  • Check-in à partir de: {hotel_details.policies.checkin_from}")
            if hotel_details.policies.checkout_until:
                print(f"  • Check-out jusqu'à: {hotel_details.policies.checkout_until}")

        if hotel_details.house_rules:
            print(f"\n📋 Règles de la maison ({len(hotel_details.house_rules)}):")
            print(format_list(hotel_details.house_rules, max_items=15))
        else:
            print("\n⚠️  Règles de la maison non disponibles")

        # === À PROXIMITÉ ===
        print_section(f"🗺️  ATTRACTIONS À PROXIMITÉ ({len(hotel_details.nearby_attractions)} lieux)")

        if hotel_details.nearby_attractions:
            # Grouper par catégorie
            by_category = {}
            for attr in hotel_details.nearby_attractions:
                cat = attr.category or "Autre"
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(attr)

            for category in sorted(by_category.keys()):
                attractions = by_category[category]
                print(f"\n📍 {category} ({len(attractions)}):")
                for attr in attractions[:15]:
                    print(f"  • {attr.name:45s} {attr.distance:>12s}")

                if len(attractions) > 15:
                    print(f"  ... et {len(attractions) - 15} autres")
        else:
            print("⚠️  Aucune attraction répertoriée")

        # === LANGUES & CONTACT ===
        print_section("🌐 LANGUES & CONTACT")

        if hotel_details.languages_spoken:
            print(f"\n🗣️  Langues parlées ({len(hotel_details.languages_spoken)}):")
            print(f"  {', '.join(hotel_details.languages_spoken)}")
        else:
            print("\n⚠️  Langues parlées non spécifiées")

        print(f"\n📞 Téléphone: {hotel_details.phone if hotel_details.phone else 'Non disponible'}")
        print(f"📧 Email: {hotel_details.email if hotel_details.email else 'Non disponible'}")

        # === RÉSUMÉ STATISTIQUE ===
        print_section("📊 RÉSUMÉ STATISTIQUE DE L'EXTRACTION")

        stats = {
            "Nom": "✓" if hotel_details.name != "Unknown Hotel" else "✗",
            "Adresse": "✓" if hotel_details.address else "✗",
            "Description": f"✓ ({len(hotel_details.description)} car.)" if hotel_details.description else "✗",
            "Type propriété": "✓" if hotel_details.property_type else "✗",
            "Étoiles": f"✓ ({hotel_details.star_rating}★)" if hotel_details.star_rating else "✗",
            "Note globale": f"✓ ({hotel_details.review_score}/10)" if hotel_details.review_score else "✗",
            "Nombre d'avis": f"✓ ({hotel_details.review_count})" if hotel_details.review_count else "✗",
            "Catégorie avis": "✓" if hotel_details.review_category else "✗",
            "Notes détaillées": "✓" if hotel_details.review_scores_detail else "✗",
            "Images": f"✓ ({len(hotel_details.images)})" if hotel_details.images else "✗",
            "Équipements": f"✓ ({len(hotel_details.amenities)})" if hotel_details.amenities else "✗",
            "Chambres": f"✓ ({len(hotel_details.rooms)})" if hotel_details.rooms else "✗",
            "Prix": f"✓ ({hotel_details.cheapest_price}€)" if hotel_details.cheapest_price else "✗",
            "Politiques": "✓" if hotel_details.policies else "✗",
            "Règles": f"✓ ({len(hotel_details.house_rules)})" if hotel_details.house_rules else "✗",
            "Attractions": f"✓ ({len(hotel_details.nearby_attractions)})" if hotel_details.nearby_attractions else "✗",
            "Langues": f"✓ ({len(hotel_details.languages_spoken)})" if hotel_details.languages_spoken else "✗",
            "Contact": "✓" if (hotel_details.phone or hotel_details.email) else "✗",
            "Avis clients": f"✓ ({len(guest_reviews)})" if guest_reviews else "✗"
        }

        print()
        successful = sum(1 for v in stats.values() if v.startswith("✓"))
        total = len(stats)

        for key, value in stats.items():
            print(f"  {key:20s}: {value}")

        print(f"\n🎯 Taux de réussite: {successful}/{total} ({successful/total*100:.1f}%)")

        # === EXPORT JSON ===
        print_section("💾 EXPORT JSON")

        # Préparer le dictionnaire pour JSON
        export_data = {
            "hotel_id": hotel_details.hotel_id,
            "name": hotel_details.name,
            "url": hotel_details.url,
            "property_type": hotel_details.property_type,
            "star_rating": hotel_details.star_rating,
            "address": {
                "full_address": hotel_details.address.full_address if hotel_details.address else None,
                "latitude": hotel_details.address.latitude if hotel_details.address else None,
                "longitude": hotel_details.address.longitude if hotel_details.address else None
            } if hotel_details.address else None,
            "description": hotel_details.description,
            "review_score": hotel_details.review_score,
            "review_count": hotel_details.review_count,
            "review_category": hotel_details.review_category,
            "review_scores_detail": {
                "staff": hotel_details.review_scores_detail.staff,
                "facilities": hotel_details.review_scores_detail.facilities,
                "cleanliness": hotel_details.review_scores_detail.cleanliness,
                "comfort": hotel_details.review_scores_detail.comfort,
                "value_for_money": hotel_details.review_scores_detail.value_for_money,
                "location": hotel_details.review_scores_detail.location,
                "wifi": hotel_details.review_scores_detail.wifi
            } if hotel_details.review_scores_detail else None,
            "images": hotel_details.images,
            "main_image": hotel_details.main_image,
            "amenities": hotel_details.amenities,
            "popular_amenities": hotel_details.popular_amenities,
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
                    "cancellation_policy": r.cancellation_policy
                }
                for r in hotel_details.rooms
            ],
            "cheapest_price": hotel_details.cheapest_price,
            "currency": hotel_details.currency,
            "policies": {
                "checkin_from": hotel_details.policies.checkin_from,
                "checkout_until": hotel_details.policies.checkout_until
            } if hotel_details.policies else None,
            "house_rules": hotel_details.house_rules,
            "nearby_attractions": [
                {
                    "name": a.name,
                    "distance": a.distance,
                    "category": a.category
                }
                for a in hotel_details.nearby_attractions
            ],
            "languages_spoken": hotel_details.languages_spoken,
            "phone": hotel_details.phone,
            "email": hotel_details.email,
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
            ],
            "scrape_timestamp": hotel_details.scrape_timestamp,
            "scrape_parameters": hotel_details.scrape_parameters
        }

        # Sauvegarder
        output_file = Path(__file__).parent / "hotel_details_robust_extraction.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        file_size_kb = output_file.stat().st_size / 1024
        print(f"\n💾 Fichier JSON sauvegardé:")
        print(f"   📁 Chemin: {output_file}")
        print(f"   📊 Taille: {file_size_kb:.1f} KB")

        # === CONCLUSION ===
        print("\n" + "=" * 100)
        print("✅ TEST TERMINÉ AVEC SUCCÈS")
        print("=" * 100)
        print(f"\n🎉 Extraction robuste complète!")
        print(f"📈 {successful}/{total} champs extraits avec succès ({successful/total*100:.1f}%)")
        print(f"💾 Résultats sauvegardés dans: {output_file.name}")
        print()

        return True

    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_complete_extraction())
    sys.exit(0 if success else 1)