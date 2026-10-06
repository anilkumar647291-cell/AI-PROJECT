from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.recommendation import Attraction, FoodPlace
from app.schemas.recommendation import (
    AttractionResponse,
    AttractionCreate,
    FoodPlaceResponse,
    FoodPlaceCreate,
    EcoTourismEvaluationRequest,
    EcoScoreResponse
)
from app.services.recommendation_service import RecommendationService

router = APIRouter()

@router.get("/attractions", response_model=List[AttractionResponse])
def list_attractions(
    destination: Optional[str] = Query(None, description="Filter by destination/city"),
    category: Optional[str] = Query(None, description="Filter by category e.g. monument, museum, nature"),
    wheelchair_only: bool = Query(False, description="Filter wheelchair accessible spots only"),
    min_eco_rating: Optional[float] = Query(None, ge=1.0, le=5.0, description="Filter by minimum eco rating"),
    db: Session = Depends(get_db)
):
    """Retrieve attractions tailored by destination, accessibility constraints, and eco-scores."""
    return RecommendationService.get_attractions(
        db, destination, category, wheelchair_only, min_eco_rating
    )

@router.post("/attractions", response_model=AttractionResponse, status_code=status.HTTP_201_CREATED)
def add_attraction(attraction_in: AttractionCreate, db: Session = Depends(get_db)):
    """Register a new tourism attraction."""
    attraction = Attraction(**attraction_in.model_dump())
    db.add(attraction)
    db.commit()
    db.refresh(attraction)
    return attraction

@router.get("/food", response_model=List[FoodPlaceResponse])
def list_food_places(
    destination: Optional[str] = Query(None, description="City / Destination"),
    cuisine: Optional[str] = Query(None, description="e.g. Japanese, Italian, Street Food"),
    dietary: Optional[str] = Query(None, description="e.g. vegan, vegetarian, halal, gluten-free"),
    db: Session = Depends(get_db)
):
    """Retrieve local food recommendations with dietary preferences (halal, vegan, gluten-free)."""
    return RecommendationService.get_food_places(db, destination, cuisine, dietary)

@router.post("/food", response_model=FoodPlaceResponse, status_code=status.HTTP_201_CREATED)
def add_food_place(food_in: FoodPlaceCreate, db: Session = Depends(get_db)):
    """Register a local food place or restaurant."""
    food = FoodPlace(**food_in.model_dump())
    db.add(food)
    db.commit()
    db.refresh(food)
    return food

@router.post("/eco-evaluate", response_model=EcoScoreResponse)
def evaluate_eco_tourism(req: EcoTourismEvaluationRequest):
    """
    Eco-Tourism Scorer:
    Evaluates transportation modes and accommodation sustainability to calculate
    carbon footprint savings and award green explorer badges.
    """
    return RecommendationService.calculate_eco_score(req)
