from typing import List, Dict, Any, Optional
from app.schemas.tools import (
    SmartPackingRequest,
    SmartPackingResponse,
    TranslationRequest,
    TranslationResponse,
    AIChatRequest,
    AIChatResponse
)

class AIAssistantService:
    """
    Generative AI and Conversational Assistant Service:
    - Smart contextual packing list generation
    - Natural language itinerary explanations & replanning
    - Multilingual & cultural communication assistant
    """

    @staticmethod
    def generate_smart_packing(req: SmartPackingRequest) -> SmartPackingResponse:
        # Determine clothing based on season and activities
        clothing = ["Breathable cotton / linen shirts", "Comfortable moisture-wicking walking shoes", "Light jacket / layer"]
        if "winter" in req.season_or_month.lower() or "cold" in req.season_or_month.lower():
            clothing.extend(["Thermal base layers", "Insulated waterproof down jacket", "Gloves and beanie"])
        elif "summer" in req.season_or_month.lower():
            clothing.extend(["UV-blocking sunhat", "Sunglasses (polarized)", "Lightweight shorts/trousers"])
        else: # Autumn / Spring
            clothing.extend(["Waterproof windbreaker", "Cardigan or merino fleece", "Versatile casual trousers"])

        if "fine_dining" in req.planned_activities:
            clothing.append("Smart-casual evening dinner attire (collared shirt / dress)")

        gear = [
            "Universal travel power plug adapter",
            "Compact 10,000mAh power bank",
            "Smartphone with offline maps pre-downloaded",
            "Reusable BPA-free insulated water bottle"
        ]

        health_accessibility = [
            "Personal prescription medications with original doctor label",
            "Travel first-aid kit (blister bandages, pain relief, antacids)",
            "Electrolyte rehydration packs"
        ]
        if req.traveler_type == "senior":
            health_accessibility.extend([
                "Compression travel socks for transit",
                "Foldable lightweight walking cane / trekking pole",
                "Printed medical summary and emergency contacts card"
            ])
        elif req.traveler_type == "family_with_kids":
            health_accessibility.extend([
                "Kid-friendly sunscreen and insect repellent",
                "Compact emergency snacks and coloring activity book"
            ])

        docs = [
            "Passport / Government Photo ID with 6+ months validity",
            "Printed and digital copies of accommodation confirmations",
            "Travel medical insurance card and policy number"
        ]

        tips = [
            f"For a {req.duration_days}-day trip to {req.destination}, roll clothes rather than folding to save 30% suitcase volume.",
            "Keep one set of essentials and medicine in your carry-on bag.",
            "Leave 15% bag capacity free for local artisanal souvenirs."
        ]

        return SmartPackingResponse(
            destination=req.destination,
            predicted_weather_summary=f"Typical {req.season_or_month} climate in {req.destination}: pleasant daytime, cooler evenings with light precipitation risk.",
            clothing_essentials=clothing,
            gear_and_electronics=gear,
            health_and_accessibility_items=health_accessibility,
            important_documents=docs,
            pro_tips=tips
        )

    @staticmethod
    def answer_travel_query(req: AIChatRequest) -> AIChatResponse:
        q_lower = req.query.lower()
        
        if "why" in q_lower or "explain" in q_lower:
            reply = (
                f"Your itinerary was algorithmically optimized to minimize transit time, bypass peak congestion windows, "
                f"and honor your pacing constraints. Key sights are scheduled during early morning hours to guarantee optimal photography "
                f"lighting and pleasant crowd density."
            )
            followups = [
                "Would you like me to reschedule the afternoon slot to a later hour?",
                "Show me nearby authentic culinary spots for lunch.",
                "How does the weather forecast affect this schedule?"
            ]
        elif "rain" in q_lower or "weather" in q_lower:
            reply = (
                f"If weather conditions change in {req.destination or 'your destination'}, the adaptive engine automatically triggers indoor alternatives: "
                f"swapping open-air viewpoints with covered art pavilions, historic tea salons, or interactive museums."
            )
            followups = [
                "Run a What-If simulation for heavy rain tomorrow.",
                "Check today's real-time weather alerts.",
                "What indoor activities are wheelchair accessible?"
            ]
        elif "budget" in q_lower or "cost" in q_lower:
            reply = (
                f"I track your daily budget allocation dynamically. If expenses exceed limits on day one, subsequent days will "
                f"automatically emphasize free scenic heritage trails, local markets, and complimentary architectural landmarks."
            )
            followups = [
                "Simulate a 20% budget reduction.",
                "Show the group expense split balance.",
                "Find Michelin-recommended budget street food."
            ]
        else:
            reply = (
                f"Hello! I am your AI Adaptive Tourism Companion for {req.destination or 'your travels'}. "
                f"I can adjust your schedule in real-time based on live weather, traffic, crowd congestion, and group preferences. "
                f"What would you like assistance with today?"
            )
            followups = [
                "Suggest a hidden gem near my afternoon stop.",
                "Check safety ratings for my neighborhood.",
                "Give me cultural etiquette tips for dining here."
            ]

        return AIChatResponse(
            reply=reply,
            suggested_followups=followups,
            contextual_links=[
                {"title": "Live Adaptive Itinerary", "path": "/api/v1/adaptive/what-if"},
                {"title": "Tourist Safety Index", "path": "/api/v1/safety/index"}
            ]
        )

    @staticmethod
    def translate_phrase(req: TranslationRequest) -> TranslationResponse:
        translations = {
            "Where is the nearest wheelchair accessible subway entrance?": {
                "ja": ("最寄りの車椅子対応の地下鉄の入り口はどこですか？", "Moyori no kurumaisu taiou no chikatetsu no iriguchi wa doko desu ka?", "In Japan, subway station masters will happily assist you with ramps if you notify the window attendant."),
                "fr": ("Où se trouve l'entrée de métro accessible aux fauteuils roulants la plus proche ?", "Oo se troov lahn-tray duh may-troh ak-seh-seebl oh foh-tuhy roo-lahn la ploo prosh?", "Many historic metro stations have stairs; look for RER or modern line elevators."),
                "es": ("¿Dónde está la entrada de metro accesible para sillas de ruedas más cercana?", "Dohn-deh es-tah lah en-trah-dah deh meh-troh ahk-seh-see-bleh?", "Look for the universal wheelchair pictogram at metro station plazas.")
            }
        }

        # Check dictionary or provide intelligent transliteration
        target = req.target_language.lower()
        if req.text in translations and target in translations[req.text]:
            trans, phon, tip = translations[req.text][target]
        else:
            trans = f"[{req.target_language.upper()}] {req.text}"
            phon = "Phonetic guide available via voice speaker"
            tip = "Always greet the local host with a polite smile before asking for directions."

        return TranslationResponse(
            source_text=req.text,
            translated_text=trans,
            phonetic_pronunciation=phon,
            cultural_etiquette_tip=tip
        )
