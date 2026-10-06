from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.safety import SafetyAlert, EmergencyContact
from app.schemas.safety import (
    SOSRequest,
    SOSResponse,
    SafetyIndexResponse,
    EmergencyContactResponse,
    SafetyAlertResponse
)
from app.services.safety_service import SafetyService

router = APIRouter()

@router.get("/index", response_model=SafetyIndexResponse)
def get_safety_index(
    destination: str = Query(..., description="Destination city name, e.g. 'Kyoto' or 'Paris'")
):
    """Retrieve tourist safety indicators, risk levels, and safe precincts."""
    return SafetyService.get_destination_safety_index(destination)

@router.get("/contacts", response_model=EmergencyContactResponse)
def get_destination_emergency_contacts(
    destination: str = Query(..., description="Destination city or country"),
    db: Session = Depends(get_db)
):
    """Get local police, ambulance, tourist helpline, and embassy contacts."""
    return SafetyService.get_emergency_contacts(db, destination)

@router.post("/sos", response_model=SOSResponse, status_code=status.HTTP_201_CREATED)
def trigger_sos_emergency(req: SOSRequest):
    """
    Emergency SOS Dispatch:
    Dispatches immediate distress signals with GPS coordinates, outputs safety guidance,
    and returns direct hotlines for urgent medical or security response.
    """
    return SafetyService.dispatch_sos(req)

@router.get("/alerts", response_model=List[SafetyAlertResponse])
def get_safety_alerts(
    destination: str = Query(..., description="Destination to check alerts for"),
    db: Session = Depends(get_db)
):
    """Fetch active safety advisories, meteorological alerts, or transit disruptions."""
    alerts = db.query(SafetyAlert).filter(
        SafetyAlert.destination.ilike(f"%{destination.split(',')[0].strip()}%"),
        SafetyAlert.is_active == 1
    ).all()
    return alerts
