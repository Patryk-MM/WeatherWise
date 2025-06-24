# weatherwise/api_clients/base.py
from abc import ABC, abstractmethod
from typing import Dict

class WeatherAPIClient(ABC):
    @abstractmethod
    def fetch(self, location: str) -> Dict:
        """Fetch weather data for a given location"""
        pass
