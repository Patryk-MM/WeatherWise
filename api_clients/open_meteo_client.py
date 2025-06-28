import requests
from datetime import datetime, timedelta
from .base import WeatherAPIClient, WeatherData
from config.settings import WeatherConfig
from exceptions.weather_exceptions import LocationNotSupportedError, DataFetchError
import pandas as pd


class OpenMeteoClient(WeatherAPIClient):
    def __init__(self):
        super().__init__("OpenMeteo")
        self.config = WeatherConfig()
        self.base_url = "https://archive-api.open-meteo.com/v1/archive"

    def is_available(self) -> bool:
        return True

    def fetch(self, location: str) -> WeatherData:
        self.logger.info(f"Pozyskanie danych pogodowych z Open-Meteo dla {location}")

        loc_key = location.lower()
        if loc_key not in self.config.LOCATIONS:
            raise LocationNotSupportedError(f"Lokalizacja o nazwie: '{location}' nie jest wspierane.")

        lat, lon = self.config.LOCATIONS[loc_key]

        today = datetime.now().date()
        start_date = today - timedelta(days=self.config.HISTORICAL_DAYS)

        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date.isoformat(),
            "end_date": today.isoformat(),
            "daily": "temperature_2m_mean,temperature_2m_max,temperature_2m_min,relative_humidity_2m_mean,surface_pressure_mean,wind_speed_10m_mean,precipitation_sum",
            "timezone": "Europe/Warsaw"
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            daily = data.get("daily", {})
            if not daily:
                raise DataFetchError("Brak dostepnych danych z Open-Meteo")

            df = pd.DataFrame(daily)

            series_data = []
            if "time" in df.columns and "temperature_2m_mean" in df.columns:
                series_data = [
                    {"date": row["time"], "temperature": self.safe_round(row["temperature_2m_mean"])}
                    for _, row in df.iterrows()
                    if pd.notna(row["temperature_2m_mean"])
                ]

            return WeatherData(
                source=self.name,
                location=location,
                timestamp=datetime.now(),
                avg_temp=self.safe_round(
                    df["temperature_2m_mean"].mean()) if "temperature_2m_mean" in df.columns else None,
                max_temp=self.safe_round(
                    df["temperature_2m_max"].max()) if "temperature_2m_max" in df.columns else None,
                min_temp=self.safe_round(
                    df["temperature_2m_min"].min()) if "temperature_2m_min" in df.columns else None,
                humidity=self.safe_round(
                    df["relative_humidity_2m_mean"].mean()) if "relative_humidity_2m_mean" in df.columns else None,
                pressure=self.safe_round(
                    df["surface_pressure_mean"].mean()) if "surface_pressure_mean" in df.columns else None,
                wind_speed=self.safe_round(
                    df["wind_speed_10m_mean"].mean()) if "wind_speed_10m_mean" in df.columns else None,
                precipitation=self.safe_round(
                    df["precipitation_sum"].sum()) if "precipitation_sum" in df.columns else None,
                series=series_data
            )

        except requests.RequestException as e:
            raise DataFetchError(f"Wystapil blad podczas pozyskiwania danych z Open-Meteo: {str(e)}")
        except Exception as e:
            raise DataFetchError(f"Wystapil blad podczas procesowania danych z Open-Meteo : {str(e)}")
