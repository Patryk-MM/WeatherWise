# api_clients/open_meteo_client.py
import requests
from datetime import datetime, timedelta
from .base import WeatherAPIClient
import pandas as pd

class OpenMeteoClient(WeatherAPIClient):
    def fetch(self, location: str):
        print("Fetching from Open-Meteo...")

        location_map = {
            "warsaw": (52.2297, 21.0122),
            "krakow": (50.0647, 19.9450),
            "poznan": (52.4064, 16.9252)
        }

        loc_key = location.lower()
        if loc_key not in location_map:
            raise ValueError("Unsupported location.")

        lat, lon = location_map[loc_key]

        today = datetime.now().date()
        start_date = today - timedelta(days=365)

        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date.isoformat(),
            "end_date": today.isoformat(),
            "daily": "temperature_2m_mean,temperature_2m_max,temperature_2m_min,relative_humidity_2m_mean",
            "timezone": "Europe/Warsaw"
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        daily = data.get("daily", {})
        df = pd.DataFrame(daily)

        return {
            "source": "OpenMeteo",
            "avg_temp": self.safe_round(df["temperature_2m_mean"].mean(), 2),
            "max_temp": self.safe_round(df["temperature_2m_max"].max(), 2),
            "min_temp": self.safe_round(df["temperature_2m_min"].min(), 2),
            "avg_humidity": self.safe_round(df["relative_humidity_2m_mean"].mean(), 2) if "relative_humidity_2m_mean" in df else None,
            "series": df.rename(columns={"date": "date"})
        }

    def safe_round(self, value, digits):
        if pd.isna(value) or value is None:
            return None
        return round(value, digits)
