import csv
import json
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path


def geocode_city(city, country):
    """Get latitude and longitude for a city using Open-Meteo geocoding API."""
    params = urllib.parse.urlencode({"name": city, "count": 5})
    url = f"https://geocoding-api.open-meteo.com/v1/search?{params}"

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            if "results" in data and data["results"]:
                for result in data["results"]:
                    if country and result.get("country", "").lower() == country.lower():
                        return result["longitude"], result["latitude"]
                result = data["results"][0]
                return result["latitude"], result["longitude"]
    except Exception as e:
        print(f"  Geocoding error for {city}: {e}")
    return 0, 0


def get_weather(lat, lon):
    """Fetch current weather from Open-Meteo API."""
    params = urllib.parse.urlencode({
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
    })
    url = f"https://api.open-meteo.com/v1/forecast?{params}"

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            current = data.get("current", {})
            units = data.get("current_units", {})
            return {
                "temperature": f"{current.get('temperature_2m', 'N/A')}{units.get('temperature_2m', '')}",
                "humidity": f"{current.get('relative_humidity_2m', 'N/A')}{units.get('relative_humidity_2m', '')}",
                "wind_speed": f"{current.get('wind_speed_10m', 'N/A')}{units.get('wind_speed_10m', '')}",
                "weather_code": current.get("weather_code", "N/A")
            }
    except Exception as e:
        print(f"  Weather fetch error: {e}")
    return {"temperature": "N/A", "humidity": "N/A", "wind_speed": "N/A", "weather_code": "N/A"}


def weather_code_to_description(code):
    """Convert WMO weather code to human-readable description."""
    codes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
    }
    return codes.get(code, "Unknown")


def flip_csv_columns(input_path, output_dir):
    """Read a CSV file, fetch weather, and write with reversed columns plus weather data."""
    with open(input_path, 'r', newline='') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        rows = list(reader)

    city_col = "city" if "city" in fieldnames else None
    country_col = "country" if "country" in fieldnames else None

    if not city_col:
        print("Warning: No 'city' column found. Skipping weather fetch.")

    weather_cols = ["temperature", "humidity", "wind_speed", "conditions"]
    reversed_fields = fieldnames[::-1]
    output_fields = reversed_fields + weather_cols

    output_rows = []
    for row in rows:
        city = row.get(city_col, "") if city_col else ""
        country = row.get(country_col, "") if country_col else ""

        print(f"Fetching weather for {city}, {country}...")
        lat, lon = geocode_city(city, country)

        if lat and lon:
            weather = get_weather(lat, lon)
            conditions = weather_code_to_description(weather["weather_code"])
        else:
            weather = {"temperature": "N/A", "humidity": "N/A", "wind_speed": "N/A"}
            conditions = "N/A"

        reversed_row = {field: row[field] for field in reversed_fields}
        reversed_row["temperature"] = weather["temperature"]
        reversed_row["humidity"] = weather["humidity"]
        reversed_row["wind_speed"] = weather["wind_speed"]
        reversed_row["conditions"] = conditions
        output_rows.append(reversed_row)

    timestamp = datetime.now().strftime("%H%M%S")
    output_filename = f"output_{timestamp}.csv"
    output_path = output_dir / output_filename

    with open(output_path, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Created: {output_path}")


def main():
    base_dir = Path(__file__).parent
    input_path = base_dir / "data" / "input.csv"
    output_dir = base_dir / "output"

    output_dir.mkdir(exist_ok=True)

    if not input_path.exists():
        print(f"Error: Input file not found at {input_path}")
        return

    flip_csv_columns(input_path, output_dir)


if __name__ == "__main__":
    main()
