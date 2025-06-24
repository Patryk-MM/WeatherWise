# exceptions/weather_exceptions.py
class WeatherAPIError(Exception):
    """Base exception for weather API errors"""
    pass

class LocationNotSupportedError(WeatherAPIError):
    """Raised when location is not supported"""
    pass

class DataFetchError(WeatherAPIError):
    """Raised when data fetching fails"""
    pass

class InsufficientDataError(WeatherAPIError):
    """Raised when there's not enough data for analysis"""
    pass