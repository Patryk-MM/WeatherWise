# exceptions/weather_exceptions.py
class WeatherAPIError(Exception):
    pass

class LocationNotSupportedError(WeatherAPIError):
    pass

class DataFetchError(WeatherAPIError):
    pass

class InsufficientDataError(WeatherAPIError):
    pass