from abc import ABC, abstractmethod
from typing import Dict, Optional, List
import logging
from dataclasses import dataclass
from datetime import datetime


@dataclass
class WeatherData:
    source: str
    location: str
    timestamp: datetime
    avg_temp: Optional[float] = None
    max_temp: Optional[float] = None
    min_temp: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    wind_speed: Optional[float] = None
    precipitation: Optional[float] = None
    series: Optional[List[Dict]] = None

    def to_dict(self) -> Dict:
        return {
            'source': self.source,
            'location': self.location,
            'timestamp': self.timestamp.isoformat(),
            'avg_temp': self.avg_temp,
            'max_temp': self.max_temp,
            'min_temp': self.min_temp,
            'humidity': self.humidity,
            'pressure': self.pressure,
            'wind_speed': self.wind_speed,
            'precipitation': self.precipitation,
            'series': self.series
        }


class WeatherAPIClient(ABC):
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")

    @abstractmethod
    def fetch(self, location: str) -> WeatherData:
        """Fetch weather data for a given location"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the API is available and properly configured"""
        pass

    def safe_round(self, value, digits: int = 2) -> Optional[float]:
        """Safely round a value, handling None and NaN"""
        if value is None or (hasattr(value, 'isna') and value.isna()):
            return None
        try:
            return round(float(value), digits)
        except (ValueError, TypeError):
            return None