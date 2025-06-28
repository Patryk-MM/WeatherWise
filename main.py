import importlib
import pkgutil
import logging
import sys
from utils.parallel_processor import ParallelWeatherProcessor, fetch_single_client
from datetime import datetime
from pathlib import Path
from typing import List

from api_clients.base import WeatherAPIClient
from utils.aggregator import WeatherAggregator
from utils.performance import measure_time, profile_function
from utils.series_merge import TimeSeriesMerger
from models.prophet_model import WeatherForecaster
from config.settings import WeatherConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('weatherwise.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class WeatherWise:
    def __init__(self):
        self.config = WeatherConfig()
        self.aggregator = WeatherAggregator()
        self.merger = TimeSeriesMerger()
        self.forecaster = WeatherForecaster()

    def get_all_clients(self) -> List[WeatherAPIClient]:
        """Dynamiczne pobieranie danych pogodowych weather API clients"""
        clients = []

        for _, modname, _ in pkgutil.iter_modules(['api_clients']):
            if modname in ('base', '__init__'):
                continue

            try:
                module = importlib.import_module(f'api_clients.{modname}')
                for attr in dir(module):
                    obj = getattr(module, attr)
                    if (isinstance(obj, type) and
                            issubclass(obj, WeatherAPIClient) and
                            obj is not WeatherAPIClient):

                        client = obj()
                        if client.is_available():
                            clients.append(client)
                            logger.info(f"Zaladowano dla: {client.name}")
                        else:
                            logger.warning(f"{client.name} nie jest chwilowo dostepny")

            except ImportError as e:
                logger.error(f"Wystapil bląd z zaladowaniem modulu {modname}: {e}")

        return clients

    @measure_time
    @profile_function
    def fetch_all_data(self, location: str):
        clients = self.get_all_clients()
        print(f"Rozpoczynanie rownoleglego pobierania danych z {len(clients)} zrodel...")

        args_list = [(client, location) for client in clients]

        results = ParallelWeatherProcessor.run_parallel(fetch_single_client, args_list)
        return [r for r in results if r is not None]

    #def run_analysis(self, location: str = "Warsaw"):
    def run_analysis(self, location: str):
        """Run complete weather analysis"""
        logger.info(f"Rozpoczecie analizy pogodowej dla:  {location}")

        weather_data = self.fetch_all_data(location)

        if not weather_data:
            logger.error("Brak dostepnych danych pogodowych")
            return

        # Display raw data
        print(f"\n Dane pogodowe dla:  {location.title()}")
        print("=" * 50)

        for data in weather_data:
            print(f"\n Zrodlo: {data.source}")
            print(f"   Srednia Temperatura: {data.avg_temp}°C")
            print(f"   Max Temperatura: {data.max_temp}°C")
            print(f"   Min Temperatura: {data.min_temp}°C")
            print(f"   Wilgotnosc: {data.humidity}%")
            print(f"   Cisnienie: {data.pressure} hPa")
            print(f"   Predkosc wiatru: {data.wind_speed} m/s")
            print(f"   Opady atmosferyczne: {data.precipitation} mm")

        aggregated = self.aggregator.aggregate_weather_data(weather_data)

        print(f"\n Zagregowane podsumowanie pogody")
        print("=" * 50)
        for key, value in aggregated.items():
            if not key.endswith(('_min', '_max', '_count')):
                print(f"{key.replace('_', ' ').title()}: {value}")

        try:
            merged_series = self.merger.merge_series(weather_data)
            forecast = self.forecaster.forecast_temperature(merged_series)

            print(f"\n 7-Dniowa Prognoza Pogody")
            print("=" * 50)

            recent_forecast = forecast.tail(7)
            for _, row in recent_forecast.iterrows():
                date = row['ds'].strftime('%Y-%m-%d')
                temp = round(row['yhat'], 1)
                lower = round(row['yhat_lower'], 1)
                upper = round(row['yhat_upper'], 1)
                print(f"{date}: {temp}°C (range: {lower}°C - {upper}°C)")

            output_dir = Path(self.config.OUTPUT_DIR)
            output_dir.mkdir(exist_ok=True)

            plot_path = output_dir / f"forecast_{location.lower()}_{datetime.now().strftime('%Y%m%d')}.png"

            self.forecaster.plot_forecast(
                forecast.tail(14),
                merged_series.tail(30),
                title=f"Prognoza temperatury dla: {location.title()}",
                save_path=str(plot_path)
            )

            logger.info(f"Wykres prognozy zostal zapsiany w lokalizacji: {plot_path}")

        except Exception as e:
            logger.error(f"Nie udalo sie wygenerowac prognozy: {e}")


def main():
    weather_app = WeatherWise()

    location = "Krakow"

    try:
        weather_app.run_analysis(location)
    except KeyboardInterrupt:
        logger.info("Analiza przerwana")
    except Exception as e:
        logger.error(f"Analiza nie udała się: {e}")
        raise


if __name__ == "__main__":
    main()
