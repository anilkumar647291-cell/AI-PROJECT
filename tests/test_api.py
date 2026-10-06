import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine
from seed_data import seed_database

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_user_registration_and_login():
    import uuid
    random_email = f"user_{uuid.uuid4().hex[:6]}@example.com"
    reg_payload = {
        "email": random_email,
        "password": "strongpassword123",
        "full_name": "Test Traveler",
        "preferences": {
            "dietary": ["vegan"],
            "mobility": "normal",
            "interests": ["nature", "culture"],
            "travel_pace": "relaxed"
        }
    }
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    user_data = reg_res.json()
    assert user_data["email"] == random_email

    # Login
    login_res = client.post("/api/v1/auth/login", json={
        "email": random_email,
        "password": "strongpassword123"
    })
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

def test_trip_creation_and_adaptive_itinerary():
    # Login as demo user
    login_res = client.post("/api/v1/auth/login", json={
        "email": "traveler@example.com",
        "password": "travelpass123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create trip
    trip_payload = {
        "title": "Autumn Splendor in Kyoto",
        "destination": "Kyoto, Japan",
        "start_date": "2026-10-15T09:00:00",
        "end_date": "2026-10-18T18:00:00",
        "total_days": 3,
        "budget": 1500.0,
        "currency": "USD",
        "group_type": "solo",
        "group_size": 1,
        "age_bracket": "25-45",
        "accessibility_needs": [],
        "interests": ["culture", "monument", "nature"],
        "travel_pace": "moderate"
    }

    create_res = client.post("/api/v1/trips/", json=trip_payload, headers=headers)
    assert create_res.status_code == 201
    trip_data = create_res.json()
    trip_id = trip_data["id"]
    assert trip_data["destination"] == "Kyoto, Japan"
    assert len(trip_data["days"]) == 3
    assert len(trip_data["days"][0]["activities"]) > 0

    # Test Real-time Disruption (e.g. Heavy Rain)
    disruption_payload = {
        "trip_id": trip_id,
        "day_number": 1,
        "disruption_type": "heavy_rain",
        "details": "Flash storm forecasted"
    }
    disrupt_res = client.post("/api/v1/adaptive/realtime-disruption", json=disruption_payload, headers=headers)
    assert disrupt_res.status_code == 200
    assert disrupt_res.json()["status"] == "success"

    # Test What-If Simulation
    what_if_payload = {
        "trip_id": trip_id,
        "scenario_type": "budget_cut",
        "parameters": {"percent": 30}
    }
    what_if_res = client.post("/api/v1/adaptive/what-if", json=what_if_payload, headers=headers)
    assert what_if_res.status_code == 200
    sim_data = what_if_res.json()
    assert sim_data["scenario"] == "budget_cut"
    assert len(sim_data["recommended_alternatives"]) > 0

def test_group_travel_and_expense_split():
    login_res = client.post("/api/v1/auth/login", json={
        "email": "traveler@example.com",
        "password": "travelpass123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create a fresh trip for the group
    trip_payload = {
        "title": "Group Expedition",
        "destination": "Kyoto, Japan",
        "start_date": "2026-11-01T09:00:00",
        "end_date": "2026-11-04T18:00:00",
        "total_days": 3,
        "budget": 3000.0,
        "currency": "USD",
        "group_type": "friends",
        "group_size": 4,
        "interests": ["food", "sightseeing"],
        "travel_pace": "moderate"
    }
    trip_res = client.post("/api/v1/trips/", json=trip_payload, headers=headers)
    new_trip_id = trip_res.json()["id"]

    # Create Group Trip
    group_res = client.post("/api/v1/groups/create", json={"trip_id": new_trip_id, "total_shared_budget": 2000.0}, headers=headers)
    assert group_res.status_code in [200, 201]
    group_id = group_res.json()["id"]
    invite_code = group_res.json()["invite_code"]
    assert len(invite_code) == 8

    # Add Expense
    exp_res = client.post(f"/api/v1/groups/expenses/{group_id}", json={
        "title": "Group Dinner",
        "amount": 150.0,
        "category": "food",
        "split_type": "equal"
    }, headers=headers)
    assert exp_res.status_code == 200

    # Expense Summary & Settlement
    sum_res = client.get(f"/api/v1/groups/expenses/{group_id}/summary", headers=headers)
    assert sum_res.status_code == 200
    assert sum_res.json()["total_group_spending"] == 150.0

def test_safety_and_emergency():
    # Destination Safety Index
    safe_res = client.get("/api/v1/safety/index?destination=Kyoto")
    assert safe_res.status_code == 200
    assert safe_res.json()["safety_score"] > 80

    # SOS Trigger
    sos_res = client.post("/api/v1/safety/sos", json={
        "destination": "Kyoto, Japan",
        "emergency_type": "medical",
        "user_notes": "Mild sprain during mountain walk"
    })
    assert sos_res.status_code == 201
    assert sos_res.json()["status"] == "DISPATCHED"

def test_eco_evaluation_and_tools():
    # Eco Scorer
    eco_res = client.post("/api/v1/recommendations/eco-evaluate", json={
        "destination": "Kyoto, Japan",
        "transportation_mode": "electric_train",
        "stay_type": "eco_lodge"
    })
    assert eco_res.status_code == 200
    assert eco_res.json()["total_eco_score"] >= 80

    # Smart Packing
    pack_res = client.post("/api/v1/tools/smart-packing", json={
        "destination": "Kyoto, Japan",
        "duration_days": 4,
        "season_or_month": "Autumn",
        "planned_activities": ["walking", "dining"],
        "traveler_type": "solo"
    })
    assert pack_res.status_code == 200
    assert len(pack_res.json()["clothing_essentials"]) > 0

    # Landmark Recognition
    land_res = client.post("/api/v1/tools/landmark-recognition", data={"landmark_hint": "Fushimi Inari"})
    assert land_res.status_code == 200
    assert land_res.json()["landmark_name"] == "Fushimi Inari Taisha"

    # AI Chat
    chat_res = client.post("/api/v1/ai-chat/message", json={
        "destination": "Kyoto, Japan",
        "query": "Explain how rainy weather affects my trip plan"
    })
    assert chat_res.status_code == 200
    assert len(chat_res.json()["reply"]) > 0
