"""
weather.py - Weather Information Fetcher Tool.

Queries live weather metrics for requested cities via the wttr.in weather API.
"""

import requests

from app.config import TIME_OUT


class Weather:
    """Handles weather API interaction and data formatting."""
    def __init__(self) -> None:
        self.FICTIONAL_LOCATIONS = {
                "asgard",
                "asgard city",
                "wakanda",
                "atlantis",
                "gotham",
                "metropolis",
                "hogwarts",
            }

    
    def get_weather(self, cities: list[str]) -> dict:
        """
        Fetches current weather details for a list of cities. All kind of typos/misspells in city names should be corrected

        Args:
            cities (list[str]): Names of cities to query.

        Returns:
            dict: Nested dictionary mapping city names to weather statistics or error logs.
        """
        weather_data = {}
        for city in cities:
            try:
                city_name = city.strip().lower()

                # Guard against known fictional/mythical locations
                if city_name in self.FICTIONAL_LOCATIONS:
                    weather_data[city] = {
                        "success": False,
                        "error": f"'{city}' is a fictional or non-real location. Real-world weather data is not available.",
                    }
                    continue

                response = requests.get(
                    f"https://wttr.in/{city_name}?format=%C+%t+%w+%p+%h",
                    timeout=TIME_OUT,
                )
                # Check if API returned an invalid location page (wttr returns plain text error)
                if response.status_code != 200 or 'location not found' in response.text:
                    weather_data[city] = {
                        "success": False,
                        "error" : f"Could not find weather data for '{city}'. Please check the city spelling."
                    }
                    continue

                parts = response.text.split()
                if len(parts) < 5:
                    weather_data[city] = {
                        "error": f"Invalid response format returned for '{city}'."
                    }
                    continue

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
    print(Weather().get_weather(["Ahmedabad", "Delhi"]))
