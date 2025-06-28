from meteostat import Point, Daily
from datetime import datetime, timedelta
from .base import WeatherAPIClient, WeatherData
from config.settings import WeatherConfig
from exceptions.weather_exceptions import LocationNotSupportedError, DataFetchError
import pandas as pd


class MeteostatClient(WeatherAPIClient):
    def __init__(self):
        super().__init__("Meteostat")
        self.config = WeatherConfig()

    def is_available(self) -> bool:
        return True

    def fetch(self, location: str) -> WeatherData:
        self.logger.info(f"Pozyskanie danych pogodowych z Meteostat dla {location}")

        loc_key = location.lower()
        if loc_key not in self.config.LOCATIONS:
            raise LocationNotSupportedError(f"Lokalizacja o nazwie: '{location}' nie jest wspierane.")

        lat, lon = self.config.LOCATIONS[loc_key]
        point = Point(lat, lon)

        today = datetime.now()
        start = today - timedelta(days=self.config.HISTORICAL_DAYS)

        try:
            data = Daily(point, start, today).fetch()

            if data.empty:
                raise DataFetchError("Brak dostepnych danych z Meteostat")

            avg_temp = None
            if "tavg" in data.columns:
                avg_temp = self.safe_round(data["tavg"].mean())
            elif "tmin" in data.columns and "tmax" in data.columns:
                avg_temp = self.safe_round(((data["tmin"] + data["tmax"]) / 2).mean())

            series_data = []
            if "tavg" in data.columns:
                series_df = data[["tavg"]].reset_index()
                series_data = [
                    {"date": row["time"].strftime("%Y-%m-%d"), "temperature": self.safe_round(row["tavg"])}
                    for _, row in series_df.iterrows()
                    if pd.notna(row["tavg"])
                ]

            return WeatherData(
                source=self.name,
                location=location,
                timestamp=datetime.now(),
                avg_temp=avg_temp,
                max_temp=self.safe_round(data["tmax"].max()) if "tmax" in data.columns else None,
                min_temp=self.safe_round(data["tmin"].min()) if "tmin" in data.columns else None,
                humidity=self.safe_round(data["rhum"].mean()) if "rhum" in data.columns else None,
                pressure=self.safe_round(data["pres"].mean()) if "pres" in data.columns else None,
                wind_speed=self.safe_round(data["wspd"].mean()) if "wspd" in data.columns else None,
                precipitation=self.safe_round(data["prcp"].sum()) if "prcp" in data.columns else None,
                series=series_data
            )

        except Exception as e:
            raise DataFetchError(f"Wystapil blad podczas pozyskiwania danych z Meteostat: {str(e)}")
