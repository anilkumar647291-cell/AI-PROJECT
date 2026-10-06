from app.core.database import SessionLocal, Base, engine
from app.core.security import hash_password
from app.models.user import User
from app.models.recommendation import Attraction, FoodPlace
from app.models.safety import EmergencyContact, SafetyAlert

def seed_database():
    print("Creating tables if they don't exist...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Seed Demo User
        if not db.query(User).filter(User.email == "traveler@example.com").first():
            demo_user = User(
                email="traveler@example.com",
                hashed_password=hash_password("travelpass123"),
                full_name="Alex Mercer",
                preferences={
                    "dietary": ["vegetarian"],
                    "mobility": "normal",
                    "interests": ["culture", "photography", "local_cuisine"],
                    "travel_pace": "moderate"
                }
            )
            db.add(demo_user)
            print("[OK] Seeded demo traveler user (traveler@example.com / travelpass123)")

        # 2. Seed Attractions (Kyoto, Paris, Rome)
        sample_attractions = [
            # Kyoto
            {
                "name": "Fushimi Inari Taisha",
                "destination": "Kyoto, Japan",
                "category": "monument",
                "description": "Legendary Shinto shrine famed for thousands of vibrant vermilion torii gates stretching along forest paths.",
                "opening_time": "06:00",
                "closing_time": "18:00",
                "ticket_price": 0.0,
                "is_wheelchair_accessible": False,
                "senior_friendly": True,
                "kid_friendly": True,
                "eco_rating": 4.9,
                "typical_duration_hours": 2.5
            },
            {
                "name": "Kinkaku-ji (The Golden Pavilion)",
                "destination": "Kyoto, Japan",
                "category": "monument",
                "description": "Zen Buddhist temple whose top two floors are completely covered in gleaming gold leaf overlooking a reflective pond.",
                "opening_time": "09:00",
                "closing_time": "17:00",
                "ticket_price": 5.0,
                "is_wheelchair_accessible": True,
                "senior_friendly": True,
                "kid_friendly": True,
                "eco_rating": 4.8,
                "typical_duration_hours": 1.5
            },
            {
                "name": "Arashiyama Bamboo Grove",
                "destination": "Kyoto, Japan",
                "category": "nature",
                "description": "Towering soaring green bamboo stalks creating a natural cathedral of whispering stalks.",
                "opening_time": "00:00",
                "closing_time": "23:59",
                "ticket_price": 0.0,
                "is_wheelchair_accessible": True,
                "senior_friendly": True,
                "kid_friendly": True,
                "eco_rating": 5.0,
                "typical_duration_hours": 1.5
            },
            {
                "name": "Kyoto National Museum of Modern Art",
                "destination": "Kyoto, Japan",
                "category": "museum",
                "description": "World-class indoor gallery exhibiting contemporary Japanese masters and Kyoto craft arts.",
                "opening_time": "09:30",
                "closing_time": "17:00",
                "ticket_price": 10.0,
                "is_wheelchair_accessible": True,
                "senior_friendly": True,
                "kid_friendly": True,
                "eco_rating": 4.7,
                "typical_duration_hours": 2.0
            },
            # Paris
            {
                "name": "Louvre Museum",
                "destination": "Paris, France",
                "category": "museum",
                "description": "The world's largest art museum and historic monument home to the Mona Lisa and Venus de Milo.",
                "opening_time": "09:00",
                "closing_time": "18:00",
                "ticket_price": 17.0,
                "is_wheelchair_accessible": True,
                "senior_friendly": True,
                "kid_friendly": True,
                "eco_rating": 4.6,
                "typical_duration_hours": 3.5
            },
            {
                "name": "Eiffel Tower Champ de Mars",
                "destination": "Paris, France",
                "category": "monument",
                "description": "Iconic wrought-iron lattice landmark offering sweeping panoramic vistas of Paris.",
                "opening_time": "09:00",
                "closing_time": "23:45",
                "ticket_price": 28.0,
                "is_wheelchair_accessible": True,
                "senior_friendly": True,
                "kid_friendly": True,
                "eco_rating": 4.5,
                "typical_duration_hours": 2.0
            }
        ]

        for att in sample_attractions:
            if not db.query(Attraction).filter(Attraction.name == att["name"]).first():
                db.add(Attraction(**att))
        print(f"[OK] Seeded {len(sample_attractions)} iconic attractions")

        # 3. Seed Food Places
        sample_food = [
            {
                "name": "Gion Karyo Kaiseki",
                "destination": "Kyoto, Japan",
                "cuisine": "Traditional Kaiseki",
                "price_range": "$$$",
                "rating": 4.8,
                "dietary_options": ["vegetarian", "local_specialty"],
                "description": "Multi-course seasonal Kyoto dining in a restored historic townhouse.",
                "address": "Gion Hanami-koji, Kyoto"
            },
            {
                "name": "TowZen Vegan Ramen",
                "destination": "Kyoto, Japan",
                "cuisine": "Ramen & Soy Cuisine",
                "price_range": "$$",
                "rating": 4.9,
                "dietary_options": ["vegan", "vegetarian", "halal_friendly"],
                "description": "Creamy rich soy milk broth ramen crafted with natural organic ingredients.",
                "address": "Kamigamo, Kyoto"
            },
            {
                "name": "Nishiki Market Street Food Bites",
                "destination": "Kyoto, Japan",
                "cuisine": "Japanese Street Food",
                "price_range": "$",
                "rating": 4.7,
                "dietary_options": ["vegetarian", "seafood", "local_specialty"],
                "description": "Known as Kyoto's Kitchen, offering skewers, matcha sweets, and pickles.",
                "address": "Nakagyo Ward, Kyoto"
            },
            {
                "name": "Le Potager de Charlotte",
                "destination": "Paris, France",
                "cuisine": "Modern French Plant-Based",
                "price_range": "$$",
                "rating": 4.9,
                "dietary_options": ["vegan", "vegetarian", "gluten-free"],
                "description": "Artfully presented gourmet plant-based French dining.",
                "address": "Rue de la Rochefoucauld, Paris"
            }
        ]

        for food in sample_food:
            if not db.query(FoodPlace).filter(FoodPlace.name == food["name"]).first():
                db.add(FoodPlace(**food))
        print(f"[OK] Seeded {len(sample_food)} local culinary dining spots")

        # 4. Seed Emergency Contacts
        sample_emergency = [
            {
                "destination": "Kyoto, Japan",
                "country": "Japan",
                "police_number": "110",
                "ambulance_number": "119",
                "tourist_helpline": "+81-75-343-0564",
                "embassy_contacts": [
                    {"country": "United States", "phone": "+81-3-3224-5000", "address": "Tokyo Consulate / Embassy"},
                    {"country": "United Kingdom", "phone": "+81-3-5276-6000", "address": "Chiyoda, Tokyo"}
                ],
                "safe_zones": ["Kyoto Station Tourist Police Box", "Kawaramachi Police Station"]
            },
            {
                "destination": "Paris, France",
                "country": "France",
                "police_number": "17",
                "ambulance_number": "15",
                "tourist_helpline": "+33-1-49-52-42-63",
                "embassy_contacts": [
                    {"country": "United States", "phone": "+33-1-43-12-22-22", "address": "2 Avenue Gabriel, Paris"}
                ],
                "safe_zones": ["Hotel de Ville Police Station", "Gare de Lyon Information Bureau"]
            }
        ]

        for em in sample_emergency:
            if not db.query(EmergencyContact).filter(EmergencyContact.destination == em["destination"]).first():
                db.add(EmergencyContact(**em))
        print("[OK] Seeded emergency contacts and safety infrastructure")

        db.commit()
        print("\nAll seed data successfully committed!")
    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
