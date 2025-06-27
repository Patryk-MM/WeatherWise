import pandas as pd
from typing import List, Optional
from api_clients.base import WeatherData
from exceptions.weather_exceptions import InsufficientDataError


class TimeSeriesMerger:
    @staticmethod
    def merge_series(weather_data_list: List[WeatherData]) -> pd.DataFrame:
        series_list = []

        for data in weather_data_list:
            if not data.series:
                continue

            df = pd.DataFrame(data.series)
            if df.empty:
                continue

            # Ensure proper column names
            if "date" in df.columns and "temperature" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                df = df.dropna(subset=["temperature"])
                series_list.append(df[["date", "temperature"]])

        if not series_list:
            raise InsufficientDataError("No time series data available from any source")

        # Merge all series and calculate mean for overlapping dates
        merged = pd.concat(series_list).groupby("date", as_index=False).agg({
            "temperature": ["mean", "count", "std"]
        })

        # Flatten column names
        merged.columns = ["date", "temperature_mean", "temperature_count", "temperature_std"]
        merged = merged.sort_values("date").reset_index(drop=True)

        # Rename for Prophet compatibility
        merged = merged.rename(columns={"date": "ds", "temperature_mean": "y"})

        return merged