from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text
from app.core.database import Base

class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"

    id = Column(Integer, primary_key=True, index=True)
    destination = Column(String(255), index=True, nullable=False)
    country = Column(String(100), nullable=False)
    
    police_number = Column(String(50), default="112")
    ambulance_number = Column(String(50), default="112")
    tourist_helpline = Column(String(50), nullable=True)
    embassy_contacts = Column(JSON, default=list) # [{"country": "USA", "phone": "+...", "address": "..."}]
    safe_zones = Column(JSON, default=list)        # list of high-safety zones/precincts


class SafetyAlert(Base):
    __tablename__ = "safety_alerts"

    id = Column(Integer, primary_key=True, index=True)
    destination = Column(String(255), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    severity = Column(String(20), default="low") # "low", "medium", "high", "critical"
    category = Column(String(50), default="weather") # "weather", "traffic", "health", "security"
    description = Column(Text, nullable=False)
    
    is_active = Column(Integer, default=1)
    reported_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
