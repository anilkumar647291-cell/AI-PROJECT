from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class SOSRequest(BaseModel):
    trip_id: Optional[int] = None
    destination: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    emergency_type: str = Field(..., examples=["medical"]) # medical, theft, lost, natural_hazard, harassment
    user_notes: Optional[str] = Field(None, examples=["Feeling sudden severe altitude sickness near summit"])

class SOSResponse(BaseModel):
    alert_id: str
    status: str # "DISPATCHED", "PENDING_ASSISTANCE"
    timestamp: datetime
    immediate_actions: List[str]
    local_emergency_numbers: Dict[str, str]
    nearest_hospital_or_safe_haven: str
    sms_notification_sent_to_contacts: bool

class SafetyIndexResponse(BaseModel):
    destination: str
    safety_score: float # 0 - 100
    risk_level: str # "Very Safe", "Moderate Caution", "High Risk"
    safe_neighborhoods: List[str]
    caution_zones: List[str]
    night_safety_rating: str
    safety_tips_for_tourists: List[str]

class EmergencyContactResponse(BaseModel):
    destination: str
    country: str
    police_number: str
    ambulance_number: str
    tourist_helpline: Optional[str]
    embassy_contacts: List[Dict[str, Any]]
    safe_zones: List[str]
    model_config = ConfigDict(from_attributes=True)

class SafetyAlertResponse(BaseModel):
    id: int
    destination: str
    title: str
    severity: str
    category: str
    description: str
    reported_at: datetime
    model_config = ConfigDict(from_attributes=True)
