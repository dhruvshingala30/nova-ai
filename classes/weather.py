import requests

from app.config import TIME_OUT


class Weather:
    @staticmethod
    def get_weather(cities: list[str]):
        """
        Get the current weather for a given list of cities.
        Args:
            cities (list[str]): The names of the cities to get the weather for.
        Returns:
            dict: A dictionary containing the weather information for the specified cities.
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
    print(Weather.get_weather(["Ahmedabad", "Delhi"]))
