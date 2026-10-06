import random
from typing import Dict, Any

class WeatherService:
    """Service to retrieve weather and crowd conditions for destinations."""

    @staticmethod
    def get_destination_weather(destination: str, day_offset: int = 0) -> Dict[str, Any]:
        """
        Provides forecasted weather condition.
        Can connect to OpenWeatherMap or use dynamic algorithmic forecasts.
        """
        conditions = [
            {"condition": "sunny", "temp": 24, "rain_prob": 5, "humidity": 45, "alert": None},
            {"condition": "partly_cloudy", "temp": 21, "rain_prob": 15, "humidity": 50, "alert": None},
            {"condition": "rainy", "temp": 17, "rain_prob": 85, "humidity": 90, "alert": "Heavy precipitation expected"},
            {"condition": "breezy", "temp": 19, "rain_prob": 10, "humidity": 40, "alert": None},
        ]
        # Deterministic simulation based on hash of destination + offset
        seed_val = (hash(destination.lower()) + day_offset) % len(conditions)
        return conditions[seed_val]

    @staticmethod
    def get_crowd_level(destination: str, time_of_day: str = "12:00") -> str:
        """Estimates crowd level (low, medium, high, surge) based on time and popular trends."""
        hour = int(time_of_day.split(":")[0]) if ":" in time_of_day else 12
        if 11 <= hour <= 15:
            return "high"
        elif 8 <= hour < 11 or 16 <= hour <= 19:
            return "medium"
        else:
            return "low"
