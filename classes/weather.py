"""
weather.py - Weather Information Fetcher Tool.

Queries live weather metrics for requested cities via the wttr.in weather API.
"""

import requests
from pydantic import BaseModel, Field

from app.config import TIME_OUT


class WeatherInput(BaseModel):
    """Pydantic input schema for weather city parameters."""

    cities: list[str] = Field(
        description="A list of city names to fetch weather for. Correct any typos in city names first."
    )


class Weather:
    """Handles weather API interaction and data formatting."""

    @staticmethod
    def get_weather(cities: list[str]) -> dict:
        """
        Fetches current weather details (condition, temperature, wind, rainfall, humidity)
        for a list of cities.

        Args:
            cities (list[str]): Names of cities to query.

        Returns:
            dict: Nested dictionary mapping city names to weather statistics or error logs.
        """
        weather_data = {}
        for city in cities:
            try:
                city_name = city.strip()
                response = requests.get(
                    f"https://wttr.in/{city_name}?format=%C+%t+%w+%p+%h",
                    timeout=TIME_OUT,
                )
                response.raise_for_status()
                parts = response.text.split()

                if len(parts) < 5:
                    raise ValueError("Unexpected weather response format")

                weather_data[city_name] = {
                    "condition": " ".join(parts[:-4]),
                    "temperature": parts[-4],
                    "wind": parts[-3],
                    "rainfall": parts[-2],
                    "humidity": parts[-1],
                }
            except (requests.RequestException, ValueError) as error:
                weather_data[city] = {"error": f"Unable to fetch weather data: {error}"}

        return weather_data


if __name__ == "__main__":
    # Test script execution
    print(Weather.get_weather(["Ahmedabad", "Delhi"]))
