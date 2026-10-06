from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.recommendation import Attraction, FoodPlace
from app.schemas.recommendation import EcoTourismEvaluationRequest, EcoScoreResponse

class RecommendationService:
    """
    Service for curated attraction recommendations, local culinary discoveries,
    and eco-tourism sustainability scoring.
    """

    @staticmethod
    def get_attractions(
        db: Session,
        destination: Optional[str] = None,
        category: Optional[str] = None,
        wheelchair_only: bool = False,
        min_eco_rating: Optional[float] = None
    ) -> List[Attraction]:
        query = db.query(Attraction)
        if destination:
            query = query.filter(Attraction.destination.ilike(f"%{destination}%"))
        if category:
            query = query.filter(Attraction.category.ilike(f"%{category}%"))
        if wheelchair_only:
            query = query.filter(Attraction.is_wheelchair_accessible == True)
        if min_eco_rating:
            query = query.filter(Attraction.eco_rating >= min_eco_rating)
        return query.all()

    @staticmethod
    def get_food_places(
        db: Session,
        destination: Optional[str] = None,
        cuisine: Optional[str] = None,
        dietary: Optional[str] = None
    ) -> List[FoodPlace]:
        query = db.query(FoodPlace)
        if destination:
            query = query.filter(FoodPlace.destination.ilike(f"%{destination}%"))
        if cuisine:
            query = query.filter(FoodPlace.cuisine.ilike(f"%{cuisine}%"))
        places = query.all()
        if dietary:
            places = [p for p in places if p.dietary_options and dietary.lower() in [d.lower() for d in p.dietary_options]]
        return places

    @staticmethod
    def calculate_eco_score(req: EcoTourismEvaluationRequest) -> EcoScoreResponse:
        # Base scores by transit mode
        transit_co2 = {
            "electric_train": 14.0,
            "train": 28.0,
            "bus": 35.0,
            "walking": 0.0,
            "bike": 0.0,
            "electric_car": 40.0,
            "car": 110.0,
            "flight": 250.0
        }

        transit_score = {
            "walking": 100.0,
            "bike": 100.0,
            "electric_train": 95.0,
            "train": 88.0,
            "bus": 75.0,
            "electric_car": 70.0,
            "car": 45.0,
            "flight": 25.0
        }

        t_mode = req.transportation_mode.lower()
        t_score = transit_score.get(t_mode, 65.0)
        co2_est = transit_co2.get(t_mode, 80.0)

        stay_score = 90.0 if "eco" in req.stay_type.lower() else 70.0
        overall = round((t_score * 0.6) + (stay_score * 0.4), 1)

        badge = "Gold Eco-Traveler" if overall >= 85 else ("Silver Green Explorer" if overall >= 70 else "Bronze Traveler")

        tips = [
            f"Choosing {req.transportation_mode.replace('_', ' ')} saved ~{round(max(0, 150 - co2_est), 1)} kg CO2 compared to standard fossil transport.",
            "Use destination multi-ride digital metro cards to minimize single-use ticketing.",
            "Opt for farm-to-table dining to support local agro-economies."
        ]

        return EcoScoreResponse(
            destination=req.destination,
            total_eco_score=overall,
            sustainability_badge=badge,
            carbon_footprint_estimate_kg=co2_est,
            green_recommendations=tips
        )
