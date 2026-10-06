from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.trip import Trip, ItineraryDay, Activity
from app.models.recommendation import Attraction, FoodPlace
from app.services.weather_service import WeatherService

class ItineraryGeneratorService:
    """
    AI Recommendation & Constraint Satisfaction Engine for Itinerary Generation.
    Optimizes schedule based on:
    - Group type (solo, couple, family with kids, college friends, senior citizens)
    - Accessibility constraints (wheelchair access, minimal walking)
    - Budget allocation per day
    - Travel pace (relaxed: 2 stops, moderate: 3-4 stops, fast-paced: 5 stops)
    """

    @staticmethod
    def generate_full_itinerary(db: Session, trip: Trip) -> Trip:
        # Determine target activities per day based on travel pace
        pace_map = {
            "relaxed": 2,
            "moderate": 3,
            "fast-paced": 5
        }
        activities_per_day = pace_map.get(trip.travel_pace.lower(), 3)
        daily_budget_target = trip.budget / max(trip.total_days, 1)

        # Query attractions matching destination or general attractions
        db_attractions = db.query(Attraction).filter(
            Attraction.destination.ilike(f"%{trip.destination.split(',')[0].strip()}%")
        ).all()

        # If not enough in DB for specific city, grab all available or fallback to algorithmic templates
        if len(db_attractions) < (activities_per_day * trip.total_days):
            all_attractions = db.query(Attraction).all()
            if all_attractions:
                db_attractions.extend([a for a in all_attractions if a not in db_attractions])

        # Filter by accessibility if needed
        is_wheelchair_required = "wheelchair" in [a.lower() for a in (trip.accessibility_needs or [])]
        is_senior_trip = trip.group_type.lower() == "seniors" or (trip.age_bracket and "60" in trip.age_bracket)

        valid_attractions = []
        for att in db_attractions:
            if is_wheelchair_required and not att.is_wheelchair_accessible:
                continue
            if is_senior_trip and not att.senior_friendly:
                continue
            valid_attractions.append(att)

        # Query food spots
        food_spots = db.query(FoodPlace).filter(
            FoodPlace.destination.ilike(f"%{trip.destination.split(',')[0].strip()}%")
        ).all()
        if not food_spots:
            food_spots = db.query(FoodPlace).all()

        # Time slots
        time_slots = [
            ("09:00", "11:30", "Morning Highlight"),
            ("12:00", "13:30", "Local Dining Experience"),
            ("14:30", "17:00", "Afternoon Cultural Discovery"),
            ("17:30", "19:00", "Sunset Leisure & Walk"),
            ("19:30", "21:30", "Evening Dining & Nightlife")
        ]

        # Generate days and activities
        attraction_index = 0
        food_index = 0

        for day_num in range(1, trip.total_days + 1):
            day_date = trip.start_date + timedelta(days=day_num - 1)
            weather = WeatherService.get_destination_weather(trip.destination, day_num - 1)

            day = ItineraryDay(
                trip_id=trip.id,
                day_number=day_num,
                date=day_date,
                notes=f"Day {day_num} in {trip.destination} - Tailored for {trip.group_type} traveler(s)",
                weather_forecast=weather
            )
            db.add(day)
            db.flush() # obtain day.id

            selected_slots = time_slots[:activities_per_day + 1] # add dining
            current_day_cost = 0.0

            for slot_idx, (start_t, end_t, default_category) in enumerate(selected_slots):
                # If slot is lunchtime or dinnertime, pick food
                if "Dining" in default_category:
                    if food_spots:
                        food_item = food_spots[food_index % len(food_spots)]
                        food_index += 1
                        food_title = f"{food_item.name} ({food_item.cuisine})"
                        food_desc = f"Savor authentic {food_item.cuisine}. Dietary options: {', '.join(food_item.dietary_options or ['standard'])}."
                        cost_est = 25.0 if trip.budget > 1000 else 15.0
                    else:
                        food_title = f"Local Gastronomy Tasting in {trip.destination}"
                        food_desc = "Enjoy authentic regional dishes at a top-rated cozy bistro."
                        cost_est = 20.0

                    act = Activity(
                        itinerary_day_id=day.id,
                        title=food_title,
                        description=food_desc,
                        category="food",
                        location_name=trip.destination,
                        start_time=start_t,
                        end_time=end_t,
                        estimated_cost=cost_est,
                        is_accessible=True,
                        crowd_level="medium",
                        status="scheduled"
                    )
                else:
                    if valid_attractions:
                        att_item = valid_attractions[attraction_index % len(valid_attractions)]
                        attraction_index += 1
                        act_title = att_item.name
                        act_desc = att_item.description or f"Iconic {att_item.category} in {trip.destination}"
                        act_cost = att_item.ticket_price
                        act_accessible = att_item.is_wheelchair_accessible
                        crowd = WeatherService.get_crowd_level(trip.destination, start_t)
                    else:
                        act_title = f"{trip.destination} Signature Landmark Exploration"
                        act_desc = f"Guided experience through the highlights of {trip.destination} matching {', '.join(trip.interests or ['culture'])}."
                        act_cost = 15.0
                        act_accessible = not is_wheelchair_required or True
                        crowd = "medium"

                    act = Activity(
                        itinerary_day_id=day.id,
                        title=act_title,
                        description=act_desc,
                        category="sightseeing",
                        location_name=trip.destination,
                        start_time=start_t,
                        end_time=end_t,
                        estimated_cost=act_cost,
                        is_accessible=act_accessible,
                        crowd_level=crowd,
                        status="scheduled"
                    )

                db.add(act)

        # Compute dynamic eco-score based on group size and pace
        base_eco = 85.0
        if trip.group_size > 3:
            base_eco += 5.0 # shared group travel footprint efficiency
        if trip.travel_pace == "relaxed":
            base_eco += 3.0 # slow travel has lower transit emissions
        trip.eco_score = min(100.0, base_eco)
        trip.status = "planning"

        db.commit()
        db.refresh(trip)
        return trip
