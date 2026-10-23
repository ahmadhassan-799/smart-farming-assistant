import requests


def get_weather(city):
    city = city.strip()

    if not city:
        return "Please enter a city name."

    try:
        # Find city coordinates
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_response = requests.get(
            geo_url,
            params={"name": city, "count": 1, "language": "en", "format": "json"},
            timeout=10,
        )
        geo_response.raise_for_status()
        geo_data = geo_response.json()

        results = geo_data.get("results", [])
        if not results:
            return f"Could not find the city: {city}"

        place = results[0]
        latitude = place["latitude"]
        longitude = place["longitude"]
        city_name = place["name"]

        # Get current weather
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_response = requests.get(
            weather_url,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
                "timezone": "auto",
            },
            timeout=10,
        )
        weather_response.raise_for_status()
        current = weather_response.json()["current"]

        return (
            f"Current weather in {city_name}:\n"
            f"Temperature: {current['temperature_2m']}°C\n"
            f"Feels like: {current['apparent_temperature']}°C\n"
            f"Humidity: {current['relative_humidity_2m']}%\n"
            f"Wind speed: {current['wind_speed_10m']} km/h\n"
            f"Precipitation: {current['precipitation']} mm\n"
            f"Weather code: {current['weather_code']}\n"
            f"Observation time: {current['time']}\n"
            f"Source: Open-Meteo"
        )

    except Exception as error:
        return f"Weather service failed: {error}"


if __name__ == "__main__":
    city = input("Enter your city: ")
    print(get_weather(city))