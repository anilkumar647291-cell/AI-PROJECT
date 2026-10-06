from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.adaptive import (
    RealTimeDisruptionRequest,
    WhatIfSimulationRequest,
    AdaptiveSimulationResponse
)
from app.api.deps import get_current_user
from app.services.adaptive_engine import AdaptiveEngineService
from app.services.weather_service import WeatherService

router = APIRouter()

@router.post("/realtime-disruption")
def apply_realtime_disruption(
    disruption: RealTimeDisruptionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Real-Time Adaptive Engine Trigger:
    Simulates or receives dynamic events (heavy rain, crowd surge, budget deficit, closures)
    and dynamically re-plans the itinerary while preserving constraints.
    """
    try:
        result = AdaptiveEngineService.handle_realtime_disruption(db, disruption)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/what-if", response_model=AdaptiveSimulationResponse)
def simulate_what_if_scenario(
    sim_request: WhatIfSimulationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    What-If Travel Simulator:
    Simulate hypothetical conditions (e.g., sudden storm, 30% budget cut, flight delays)
    to preview alternative destinations, schedule adjustments, budget impacts, and eco changes.
    """
    try:
        response = AdaptiveEngineService.simulate_what_if(db, sim_request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/weather/{destination}")
def get_live_destination_conditions(destination: str):
    """Retrieve real-time weather and crowd congestion forecasts for a destination."""
    weather = WeatherService.get_destination_weather(destination)
    crowd_morning = WeatherService.get_crowd_level(destination, "10:00")
    crowd_noon = WeatherService.get_crowd_level(destination, "13:00")
    crowd_evening = WeatherService.get_crowd_level(destination, "18:00")

    return {
        "destination": destination,
        "current_weather": weather,
        "crowd_forecast": {
            "morning": crowd_morning,
            "afternoon": crowd_noon,
            "evening": crowd_evening
        }
    }
