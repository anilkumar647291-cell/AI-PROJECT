from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.trip import Trip, ItineraryDay, Activity
from app.schemas.trip import TripCreate, TripUpdate, TripResponse
from app.api.deps import get_current_user
from app.services.itinerary_generator import ItineraryGeneratorService

router = APIRouter()

@router.post("/", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def create_trip(
    trip_in: TripCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates a new trip and triggers the AI constraint engine to automatically
    generate an optimized, personalized day-by-day itinerary.
    """
    trip = Trip(
        user_id=current_user.id,
        title=trip_in.title,
        destination=trip_in.destination,
        start_date=trip_in.start_date,
        end_date=trip_in.end_date,
        total_days=trip_in.total_days,
        budget=trip_in.budget,
        currency=trip_in.currency,
        group_type=trip_in.group_type,
        group_size=trip_in.group_size,
        age_bracket=trip_in.age_bracket,
        accessibility_needs=trip_in.accessibility_needs,
        interests=trip_in.interests,
        travel_pace=trip_in.travel_pace,
        status="planning"
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)

    # Generate personalized itinerary
    trip = ItineraryGeneratorService.generate_full_itinerary(db, trip)
    return trip

@router.get("/", response_model=List[TripResponse])
def get_user_trips(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all trips created by the authenticated tourist."""
    trips = db.query(Trip).filter(Trip.user_id == current_user.id).order_by(Trip.created_at.desc()).all()
    return trips

@router.get("/{trip_id}", response_model=TripResponse)
def get_trip_by_id(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve full trip details with day schedules and activities."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    if trip.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return trip

@router.put("/{trip_id}", response_model=TripResponse)
def update_trip(
    trip_id: int,
    trip_update: TripUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update trip parameters."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    if trip.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    for field, value in trip_update.model_dump(exclude_unset=True).items():
        setattr(trip, field, value)

    db.commit()
    db.refresh(trip)
    return trip

@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a trip and all its associated itinerary days and activities."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    if trip.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    db.delete(trip)
    db.commit()
    return None

@router.post("/{trip_id}/regenerate", response_model=TripResponse)
def regenerate_itinerary(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Purges existing itinerary and re-runs the recommendation engine."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    if trip.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Clear old days and activities
    for day in trip.days:
        db.delete(day)
    db.commit()
    db.refresh(trip)

    trip = ItineraryGeneratorService.generate_full_itinerary(db, trip)
    return trip
