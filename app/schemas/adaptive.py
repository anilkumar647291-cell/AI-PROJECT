from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class RealTimeDisruptionRequest(BaseModel):
    trip_id: int
    day_number: int
    disruption_type: str = Field(
        ...,
        description="Type of disruption: 'heavy_rain', 'crowd_surge', 'traffic_delay', 'attraction_closed', 'budget_deficit'",
        examples=["heavy_rain"]
    )
    affected_activity_id: Optional[int] = Field(None, description="Optional specific activity affected")
    details: Optional[str] = Field(None, examples=["Torrential downpour forecasted from 11:00 to 16:00"])

class WhatIfSimulationRequest(BaseModel):
    trip_id: int
    scenario_type: str = Field(
        ...,
        description="Scenarios: 'weather_shift', 'budget_cut', 'flight_delay', 'crowd_rush_hour', 'accessibility_change'",
        examples=["weather_shift"]
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        examples=[{"condition": "heavy_rain", "duration_hours": 4, "day_number": 1}]
    )

class AlternativeActivity(BaseModel):
    title: str
    category: str
    reason_for_suggestion: str
    estimated_cost: float
    is_indoor: bool
    crowd_forecast: str
    eco_rating: float

class AdaptiveAdjustment(BaseModel):
    original_activity_title: str
    replaced_with_title: str
    rationale: str
    impact_on_budget: float
    eco_score_delta: float

class AdaptiveSimulationResponse(BaseModel):
    trip_id: int
    scenario: str
    adaptive_actions_taken: List[AdaptiveAdjustment]
    recommended_alternatives: List[AlternativeActivity]
    updated_day_schedule: List[Dict[str, Any]]
    ai_recommendation_summary: str
    eco_score_impact: str
