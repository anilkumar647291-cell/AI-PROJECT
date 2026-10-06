from sqlalchemy import Column, Integer, String, Float, Boolean, JSON, Text
from app.core.database import Base

class Attraction(Base):
    __tablename__ = "attractions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    destination = Column(String(255), index=True, nullable=False)
    category = Column(String(50), nullable=False) # "monument", "museum", "park", "adventure", "culture"
    description = Column(Text, nullable=True)
    
    opening_time = Column(String(10), default="09:00")
    closing_time = Column(String(10), default="18:00")
    ticket_price = Column(Float, default=0.0)
    
    # Accessibility & Demographics
    is_wheelchair_accessible = Column(Boolean, default=True)
    senior_friendly = Column(Boolean, default=True)
    kid_friendly = Column(Boolean, default=True)
    
    # Smart & Green tourism metrics
    eco_rating = Column(Float, default=4.5) # Scale 1.0 - 5.0
    crowd_peak_hours = Column(JSON, default=list) # e.g. ["11:00", "14:00"]
    typical_duration_hours = Column(Float, default=2.0)
    
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)


class FoodPlace(Base):
    __tablename__ = "food_places"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    destination = Column(String(255), index=True, nullable=False)
    cuisine = Column(String(100), nullable=False)
    price_range = Column(String(10), default="$$") # $, $$, $$$, $$$$
    rating = Column(Float, default=4.5)
    
    # Dietary options e.g. ["vegan", "vegetarian", "halal", "gluten-free", "local_specialty"]
    dietary_options = Column(JSON, default=list)
    description = Column(Text, nullable=True)
    address = Column(String(255), nullable=True)
