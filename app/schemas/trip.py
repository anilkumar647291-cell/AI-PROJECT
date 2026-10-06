from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class ActivityBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str = "sightseeing"
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    start_time: Optional[str] = "09:00"
    end_time: Optional[str] = "11:00"
    estimated_cost: float = 0.0
    is_accessible: bool = True
    crowd_level: str = "medium"

class ActivityCreate(ActivityBase):
    pass

class ActivityResponse(ActivityBase):
    id: int
    itinerary_day_id: int
    status: str
    is_adaptive_replacement: bool
    original_activity_id: Optional[int] = None
    adaptation_reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ItineraryDayResponse(BaseModel):
    id: int
    trip_id: int
    day_number: int
    date: datetime
    notes: Optional[str] = None
    weather_forecast: Optional[Dict[str, Any]] = None
    activities: List[ActivityResponse] = []

    model_config = ConfigDict(from_attributes=True)

class TripCreate(BaseModel):
    title: str = Field(..., examples=["Enchanting Kyoto Exploration"])
    destination: str = Field(..., examples=["Kyoto, Japan"])
    start_date: datetime
    end_date: datetime
    total_days: int = Field(default=3, ge=1, le=30)
    budget: float = Field(..., gt=0, examples=[1200.0])
    currency: str = Field(default="USD")
    group_type: str = Field(default="solo", examples=["solo"]) # solo, couple, family, friends, college_group, seniors
    group_size: int = Field(default=1, ge=1)
    age_bracket: Optional[str] = Field(default="25-45", examples=["25-45"])
    accessibility_needs: List[str] = Field(default_factory=list, examples=[["wheelchair"]])
    interests: List[str] = Field(default_factory=lambda: ["culture", "nature", "food"], examples=[["culture", "food"]])
    travel_pace: str = Field(default="moderate", examples=["moderate"]) # relaxed, moderate, fast-paced

class TripUpdate(BaseModel):
    title: Optional[str] = None
    budget: Optional[float] = None
    status: Optional[str] = None
    travel_pace: Optional[str] = None
    realtime_adaptive_enabled: Optional[bool] = None

class TripResponse(BaseModel):
    id: int
    user_id: int
    title: str
    destination: str
    start_date: datetime
    end_date: datetime
    total_days: int
    budget: float
    currency: str
    group_type: str
    group_size: int
    age_bracket: Optional[str]
    accessibility_needs: List[str]
    interests: List[str]
    travel_pace: str
    status: str
    eco_score: float
    realtime_adaptive_enabled: bool
    created_at: datetime
    days: List[ItineraryDayResponse] = []

    model_config = ConfigDict(from_attributes=True)
