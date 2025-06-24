from typing import List, Dict, Optional
from api_clients.base import WeatherData
import statistics


class WeatherAggregator:
    @staticmethod
    def aggregate_weather_data(weather_data_list: List[WeatherData]) -> Dict[str, Optional[float]]:
        """Aggregate weather data from multiple sources using median for robustness"""
        if not weather_data_list:
            return {}

        fields = ["avg_temp", "max_temp", "min_temp", "humidity", "pressure", "wind_speed", "precipitation"]
        result = {}

        for field in fields:
            values = [getattr(data, field) for data in weather_data_list
                      if getattr(data, field) is not None]

            if values:
                # Use median for robustness against outliers
                result[field] = round(statistics.median(values), 2)
                # Also provide min/max for transparency
                result[f"{field}_min"] = round(min(values), 2)
                result[f"{field}_max"] = round(max(values), 2)
                result[f"{field}_count"] = len(values)
            else:
                result[field] = None
                result[f"{field}_min"] = None
                result[f"{field}_max"] = None
                result[f"{field}_count"] = 0

        return result
