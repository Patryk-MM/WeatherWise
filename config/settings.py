# config/settings.py
from dataclasses import dataclass, field
from typing import Dict, Tuple
import os


@dataclass
class WeatherConfig:
    # API Configuration
    OPENWEATHER_API_KEY: str = field(default_factory=lambda: os.getenv('OPENWEATHER_API_KEY', ''))
    WEATHERAPI_KEY: str = field(default_factory=lambda: os.getenv('WEATHERAPI_KEY', ''))

    # Location mappings
    LOCATIONS: Dict[str, Tuple[float, float]] = field(default_factory=lambda: {
        "warsaw": (52.2297, 21.0122),
        "krakow": (50.0647, 19.9450),
        "poznan": (52.4064, 16.9252),
        "gdansk": (54.3520, 18.6466),
        "wroclaw": (51.1079, 17.0385),
        "lodz": (51.7592, 19.4559)
    })

    # Forecast settings
    FORECAST_DAYS: int = 7
    HISTORICAL_DAYS: int = 365

    # Output settings
    OUTPUT_DIR: str = "output"
    PLOT_STYLE: str = "default"
    FIGURE_SIZE: Tuple[int, int] = field(default_factory=lambda: (12, 8))