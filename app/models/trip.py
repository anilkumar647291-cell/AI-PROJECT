from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    destination = Column(String(255), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    total_days = Column(Integer, default=1)
    
    # Financial & Demographic Constraints
    budget = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    group_type = Column(String(50), default="solo") # solo, couple, family, friends, college_group, seniors
    group_size = Column(Integer, default=1)
    age_bracket = Column(String(50), nullable=True) # e.g. "18-25", "25-45", "60+"
    
    # Needs & Preferences
    accessibility_needs = Column(JSON, default=list) # e.g. ["wheelchair", "low_walking", "braille_audio"]
    interests = Column(JSON, default=list)           # e.g. ["nature", "culture", "culinary", "historical", "adventure"]
    travel_pace = Column(String(50), default="moderate") # "relaxed", "moderate", "fast-paced"
    
    # Dynamic Status & Metrics
    status = Column(String(50), default="planning") # "planning", "active", "completed", "cancelled"
    eco_score = Column(Float, default=80.0)         # 0-100 sustainability index
    realtime_adaptive_enabled = Column(Boolean, default=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    owner = relationship("User", back_populates="trips")
    days = relationship("ItineraryDay", back_populates="trip", cascade="all, delete-orphan", order_by="ItineraryDay.day_number")
    group_trip = relationship("GroupTrip", back_populates="trip", uselist=False, cascade="all, delete-orphan")


class ItineraryDay(Base):
    __tablename__ = "itinerary_days"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    day_number = Column(Integer, nullable=False)
    date = Column(DateTime, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Real-time condition snapshot
    weather_forecast = Column(JSON, default=dict) # {"temp": 24, "condition": "sunny", "rain_prob": 10}

    trip = relationship("Trip", back_populates="days")
    activities = relationship("Activity", back_populates="itinerary_day", cascade="all, delete-orphan", order_by="Activity.start_time")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    itinerary_day_id = Column(Integer, ForeignKey("itinerary_days.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), default="sightseeing") # sightseeing, food, cultural, adventure, relaxation
    location_name = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    start_time = Column(String(10), nullable=True) # e.g. "09:00"
    end_time = Column(String(10), nullable=True)   # e.g. "11:30"
    estimated_cost = Column(Float, default=0.0)
    
    # Accessibility and real-time attributes
    is_accessible = Column(Boolean, default=True)
    crowd_level = Column(String(20), default="medium") # low, medium, high, surge
    
    # Adaptation tracking
    status = Column(String(50), default="scheduled") # scheduled, completed, skipped, replaced
    is_adaptive_replacement = Column(Boolean, default=False)
    original_activity_id = Column(Integer, nullable=True)
    adaptation_reason = Column(Text, nullable=True) # e.g. "Shifted indoors due to heavy rainfall"

    itinerary_day = relationship("ItineraryDay", back_populates="activities")
