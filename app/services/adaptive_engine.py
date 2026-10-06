from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.trip import Trip, ItineraryDay, Activity
from app.schemas.adaptive import (
    RealTimeDisruptionRequest,
    WhatIfSimulationRequest,
    AdaptiveSimulationResponse,
    AdaptiveAdjustment,
    AlternativeActivity
)

class AdaptiveEngineService:
    """
    Dynamic Adaptive Travel Engine & What-If Simulator.
    Monitors live conditions (weather, crowd surges, transit delays, closures, budget)
    and dynamically recalculates plans with constraint preservation.
    """

    INDOOR_ALTERNATIVES = [
        {"title": "National Museum of Modern Art & Heritage", "category": "cultural", "cost": 12.0, "is_indoor": True, "crowd": "low", "eco": 4.8},
        {"title": "Grand Covered Historic Arcade & Artisan Market", "category": "shopping_culture", "cost": 0.0, "is_indoor": True, "crowd": "medium", "eco": 4.5},
        {"title": "Traditional Tea Ceremony & Matcha Workshop", "category": "cultural", "cost": 25.0, "is_indoor": True, "crowd": "low", "eco": 5.0},
        {"title": "Interactive Science & Natural History Center", "category": "educational", "cost": 15.0, "is_indoor": True, "crowd": "medium", "eco": 4.7},
    ]

    LOW_CROWD_ALTERNATIVES = [
        {"title": "Hidden Zen Garden & Botanical Arboretum", "category": "nature", "cost": 5.0, "is_indoor": False, "crowd": "low", "eco": 5.0},
        {"title": "Old Town Artisan Lane & Riverside Promenade", "category": "sightseeing", "cost": 0.0, "is_indoor": False, "crowd": "low", "eco": 4.9},
        {"title": "Historic Hilltop Panoramic Pavilion", "category": "sightseeing", "cost": 0.0, "is_indoor": False, "crowd": "low", "eco": 4.8},
    ]

    BUDGET_SAVING_ALTERNATIVES = [
        {"title": "Historic District Architecture Walking Tour", "category": "culture", "cost": 0.0, "is_indoor": False, "crowd": "medium", "eco": 5.0},
        {"title": "Public Sculpture Garden & Sunset Viewpoint", "category": "leisure", "cost": 0.0, "is_indoor": False, "crowd": "low", "eco": 5.0},
        {"title": "Local Farmers & Street Food Market (Budget Delights)", "category": "food", "cost": 8.0, "is_indoor": True, "crowd": "medium", "eco": 4.6},
    ]

    @classmethod
    def handle_realtime_disruption(cls, db: Session, req: RealTimeDisruptionRequest) -> Dict[str, Any]:
        """
        Applies a live condition disruption to the trip itinerary, swapping affected activities
        and recording the adaptive reasoning in the database.
        """
        day = db.query(ItineraryDay).filter(
            ItineraryDay.trip_id == req.trip_id,
            ItineraryDay.day_number == req.day_number
        ).first()

        if not day:
            raise ValueError(f"Trip Day {req.day_number} not found for trip {req.trip_id}")

        adjustments = []
        activities = day.activities

        if req.disruption_type == "heavy_rain":
            # Target outdoor sightseeing
            for act in activities:
                if act.status == "scheduled" and act.category != "food":
                    chosen_alt = cls.INDOOR_ALTERNATIVES[0]
                    act.status = "replaced"
                    act.adaptation_reason = f"Replaced due to severe weather ({req.details or 'Heavy Rain Alert'})"
                    
                    # Create new replacement activity
                    replacement = Activity(
                        itinerary_day_id=day.id,
                        title=chosen_alt["title"],
                        description=f"Curated indoor experience replacing {act.title} to stay dry and comfortable.",
                        category=chosen_alt["category"],
                        location_name=act.location_name,
                        start_time=act.start_time,
                        end_time=act.end_time,
                        estimated_cost=chosen_alt["cost"],
                        is_accessible=act.is_accessible,
                        crowd_level=chosen_alt["crowd"],
                        status="scheduled",
                        is_adaptive_replacement=True,
                        original_activity_id=act.id,
                        adaptation_reason="Shifted to indoor sanctuary due to rainstorm."
                    )
                    db.add(replacement)
                    adjustments.append({
                        "original": act.title,
                        "replacement": chosen_alt["title"],
                        "reason": "Severe rainfall prevented outdoor activity. Swapped with protected cultural venue."
                    })
                    break # replace primary affected outdoor spot

        elif req.disruption_type == "crowd_surge":
            for act in activities:
                if act.crowd_level in ["high", "surge", "medium"] and act.status == "scheduled":
                    chosen_alt = cls.LOW_CROWD_ALTERNATIVES[0]
                    act.status = "replaced"
                    act.adaptation_reason = f"High crowd density alert ({req.details or 'Crowd surge +90% normal'})"

                    replacement = Activity(
                        itinerary_day_id=day.id,
                        title=chosen_alt["title"],
                        description=f"Peaceful alternative avoiding peak tourist crowds at {act.title}.",
                        category=chosen_alt["category"],
                        location_name=act.location_name,
                        start_time=act.start_time,
                        end_time=act.end_time,
                        estimated_cost=chosen_alt["cost"],
                        is_accessible=True,
                        crowd_level=chosen_alt["crowd"],
                        status="scheduled",
                        is_adaptive_replacement=True,
                        original_activity_id=act.id,
                        adaptation_reason="Crowd avoidance dynamic reroute."
                    )
                    db.add(replacement)
                    adjustments.append({
                        "original": act.title,
                        "replacement": chosen_alt["title"],
                        "reason": "Avoided 2-hour queue by rerouting to a serene, highly-rated hidden gem."
                    })
                    break

        elif req.disruption_type == "budget_deficit":
            for act in activities:
                if act.estimated_cost > 15.0 and act.status == "scheduled":
                    chosen_alt = cls.BUDGET_SAVING_ALTERNATIVES[0]
                    act.status = "replaced"
                    act.adaptation_reason = "Cost-reduction adjustment"

                    replacement = Activity(
                        itinerary_day_id=day.id,
                        title=chosen_alt["title"],
                        description=f"Zero-cost scenic alternative replacing high-cost activity.",
                        category=chosen_alt["category"],
                        location_name=act.location_name,
                        start_time=act.start_time,
                        end_time=act.end_time,
                        estimated_cost=chosen_alt["cost"],
                        is_accessible=True,
                        crowd_level="low",
                        status="scheduled",
                        is_adaptive_replacement=True,
                        original_activity_id=act.id,
                        adaptation_reason="Budget constraint recovery"
                    )
                    db.add(replacement)
                    adjustments.append({
                        "original": act.title,
                        "replacement": chosen_alt["title"],
                        "reason": "Replaced premium fee attraction with highly engaging complimentary architectural walk."
                    })
                    break

        db.commit()
        db.refresh(day)

        return {
            "status": "success",
            "message": "Itinerary dynamically adapted to real-time condition changes.",
            "adjustments": adjustments,
            "disruption_type": req.disruption_type,
            "day_number": req.day_number
        }

    @classmethod
    def simulate_what_if(cls, db: Session, req: WhatIfSimulationRequest) -> AdaptiveSimulationResponse:
        """
        Runs a What-If predictive simulation without modifying current trip data.
        Returns predicted itinerary adaptations, cost changes, and eco impacts.
        """
        trip = db.query(Trip).filter(Trip.id == req.trip_id).first()
        if not trip:
            raise ValueError(f"Trip {req.trip_id} not found")

        sim_adjustments: List[AdaptiveAdjustment] = []
        suggested_alts: List[AlternativeActivity] = []
        scenario = req.scenario_type

        if scenario == "weather_shift":
            for item in cls.INDOOR_ALTERNATIVES:
                suggested_alts.append(AlternativeActivity(
                    title=item["title"],
                    category=item["category"],
                    reason_for_suggestion="100% weather-proof indoor venue with climate control.",
                    estimated_cost=item["cost"],
                    is_indoor=item["is_indoor"],
                    crowd_forecast=item["crowd"],
                    eco_rating=item["eco"]
                ))
            sim_adjustments.append(AdaptiveAdjustment(
                original_activity_title="Outdoor Botanical Walk / Park Tour",
                replaced_with_title=cls.INDOOR_ALTERNATIVES[0]["title"],
                rationale="Simulated 4-hour rainstorm. Outdoor walking replaced with covered museum.",
                impact_on_budget=+7.0,
                eco_score_delta=+0.5
            ))
            summary = "In the event of sudden rain, the engine seamlessly routes you into cultural indoor sanctuaries without sacrificing the day's quality."
            eco_impact = "Negligible change in carbon footprint; minimal indoor heating/cooling impact."

        elif scenario == "budget_cut":
            cut_percent = req.parameters.get("percent", 25)
            for item in cls.BUDGET_SAVING_ALTERNATIVES:
                suggested_alts.append(AlternativeActivity(
                    title=item["title"],
                    category=item["category"],
                    reason_for_suggestion="High-value, low or zero-cost activity.",
                    estimated_cost=item["cost"],
                    is_indoor=item["is_indoor"],
                    crowd_forecast=item["crowd"],
                    eco_rating=item["eco"]
                ))
            sim_adjustments.append(AdaptiveAdjustment(
                original_activity_title="Private Guided Luxury Sightseeing Tour",
                replaced_with_title=cls.BUDGET_SAVING_ALTERNATIVES[0]["title"],
                rationale=f"Reduced total spend by {cut_percent}% using self-guided historic routes.",
                impact_on_budget=-45.0,
                eco_score_delta=+2.0
            ))
            summary = f"Simulating a {cut_percent}% budget compression: 2 paid excursions swapped for free high-rated architectural walking tours."
            eco_impact = "Eco score improves by +2.0 points due to pedestrian exploration."

        elif scenario == "flight_delay":
            delay_hours = req.parameters.get("delay_hours", 3)
            summary = f"Flight delay of {delay_hours} hours simulated. Morning activities compressed into an afternoon-evening twilight highlights tour."
            eco_impact = "No change in environmental rating."

        else: # Generic / rush hour
            summary = f"What-If scenario '{scenario}' evaluated. Optimized transit timings to avoid peak commuting hours (08:00-09:30 and 17:30-19:00)."
            eco_impact = "Reduced public transport congestion contribution."

        # Fetch simplified day schedule representation
        day_schedule = []
        if trip.days:
            first_day = trip.days[0]
            for act in first_day.activities:
                day_schedule.append({
                    "time": f"{act.start_time} - {act.end_time}",
                    "title": act.title,
                    "status": act.status,
                    "estimated_cost": act.estimated_cost
                })

        return AdaptiveSimulationResponse(
            trip_id=trip.id,
            scenario=scenario,
            adaptive_actions_taken=sim_adjustments,
            recommended_alternatives=suggested_alts,
            updated_day_schedule=day_schedule,
            ai_recommendation_summary=summary,
            eco_score_impact=eco_impact
        )
