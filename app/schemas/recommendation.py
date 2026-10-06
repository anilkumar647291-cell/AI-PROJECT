from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class AttractionBase(BaseModel):
    name: str
    destination: str
    category: str
    description: Optional[str] = None
    opening_time: str = "09:00"
    closing_time: str = "18:00"
    ticket_price: float = 0.0
    is_wheelchair_accessible: bool = True
    senior_friendly: bool = True
    kid_friendly: bool = True
    eco_rating: float = Field(default=4.5, ge=1.0, le=5.0)
    typical_duration_hours: float = 2.0
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class AttractionCreate(AttractionBase):
    pass

class AttractionResponse(AttractionBase):
    id: int
    crowd_peak_hours: List[str] = []
    model_config = ConfigDict(from_attributes=True)

class FoodPlaceBase(BaseModel):
    name: str
    destination: str
    cuisine: str
    price_range: str = "$$"
    rating: float = 4.5
    dietary_options: List[str] = []
    description: Optional[str] = None
    address: Optional[str] = None

class FoodPlaceCreate(FoodPlaceBase):
    pass

class FoodPlaceResponse(FoodPlaceBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class EcoTourismEvaluationRequest(BaseModel):
    destination: str
    transportation_mode: str = Field(default="electric_train", examples=["electric_train"]) # train, bus, flight, car, walking, bike
    attraction_ids: List[int] = Field(default_factory=list)
    stay_type: str = Field(default="eco_lodge", examples=["eco_certified_hotel"])

class EcoScoreResponse(BaseModel):
    destination: str
    total_eco_score: float # 0 - 100
    sustainability_badge: str # "Gold Eco-Traveler", "Silver Explorer", etc.
    carbon_footprint_estimate_kg: float
    green_recommendations: List[str]
