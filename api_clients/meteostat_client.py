from meteostat import Point, Daily
from datetime import datetime, timedelta
from .base import WeatherAPIClient
import pandas as pd

class MeteostatClient(WeatherAPIClient):
    def fetch(self, location: str):
        print("Fetching from Meteostat...")

        location_map = {
            "warsaw": Point(52.2297, 21.0122),
            "krakow": Point(50.0647, 19.9450),
            "poznan": Point(52.4064, 16.9252)
        }

        loc_key = location.lower()
        if loc_key not in location_map:
            raise ValueError("Unsupported location.")

        point = location_map[loc_key]
        today = datetime.now()
        start = today - timedelta(days=365)

        data: pd.DataFrame = Daily(point, start, today).fetch()

        if data.empty:
            print("⚠️ Brak danych z Meteostata")
            return {
                "source": "Meteostat",
                "avg_temp": None,
                "max_temp": None,
                "min_temp": None,
                "avg_humidity": None
            }

        # fallback jeśli nie ma tavg
        if "tavg" in data:
            avg_temp = self.safe_round(data["tavg"].mean(), 2)
        elif "tmin" in data and "tmax" in data:
            avg_temp = self.safe_round(((data["tmin"] + data["tmax"]) / 2).mean(), 2)
        else:
            avg_temp = None

        return {
            "source": "Meteostat",
            "avg_temp": avg_temp,
            "max_temp": self.safe_round(data["tmax"].max(), 2) if "tmax" in data else None,
            "min_temp": self.safe_round(data["tmin"].min(), 2) if "tmin" in data else None,
            "avg_humidity": self.safe_round(data["rhum"].mean(), 2) if "rhum" in data else None,
            "series": data[["tavg"]].rename(columns={"tavg": "temperature"}).reset_index().dropna()
        }

    def safe_round(self, value, digits):
        if pd.isna(value) or value is None:
            return None
        return round(value, digits)
