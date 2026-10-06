from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class SmartPackingRequest(BaseModel):
    destination: str
    duration_days: int = 3
    season_or_month: str = "Autumn"
    planned_activities: List[str] = Field(default_factory=lambda: ["hiking", "city_walk", "fine_dining"])
    traveler_type: str = "solo" # solo, family_with_kids, senior

class SmartPackingResponse(BaseModel):
    destination: str
    predicted_weather_summary: str
    clothing_essentials: List[str]
    gear_and_electronics: List[str]
    health_and_accessibility_items: List[str]
    important_documents: List[str]
    pro_tips: List[str]

class LandmarkRecognitionResponse(BaseModel):
    landmark_name: str
    location: str
    historical_summary: str
    architectural_style: str
    best_time_to_visit: str
    estimated_ticket_price: float
    fun_facts: List[str]
    audio_guide_script: str
    confidence_score: float

class TranslationRequest(BaseModel):
    source_language: str = "en"
    target_language: str = "ja"
    text: str = Field(..., examples=["Where is the nearest wheelchair accessible subway entrance?"])
    context: Optional[str] = "tourism_emergency"

class TranslationResponse(BaseModel):
    source_text: str
    translated_text: str
    phonetic_pronunciation: str
    cultural_etiquette_tip: Optional[str] = None

class AIChatRequest(BaseModel):
    trip_id: Optional[int] = None
    destination: Optional[str] = None
    query: str = Field(..., examples=["Explain why Fushimi Inari was scheduled early in the morning and give me photo spots."])
    conversation_history: Optional[List[Dict[str, str]]] = Field(default_factory=list)

class AIChatResponse(BaseModel):
    reply: str
    suggested_followups: List[str]
    contextual_links: Optional[List[Dict[str, str]]] = None
