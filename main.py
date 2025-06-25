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

# Configure logging
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
        """Dynamically load all weather API clients"""
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
                            logger.info(f"Loaded client: {client.name}")
                        else:
                            logger.warning(f"Client {client.name} is not available")

            except ImportError as e:
                logger.error(f"Failed to load module {modname}: {e}")

        return clients

    @measure_time
    @profile_function
    def fetch_all_data(self, location: str):
        clients = self.get_all_clients()
        print(f"🔁 Rozpoczynanie równoległego pobierania danych z {len(clients)} źródeł...")

        # przygotuj argumenty: lista (client, location)
        args_list = [(client, location) for client in clients]

        results = ParallelWeatherProcessor.run_parallel(fetch_single_client, args_list)
        return [r for r in results if r is not None]

    def run_analysis(self, location: str = "Warsaw"):
        """Run complete weather analysis"""
        logger.info(f"Starting weather analysis for {location}")

        # Fetch data from all sources
        weather_data = self.fetch_all_data(location)

        if not weather_data:
            logger.error("No weather data available")
            return

        # Display raw data
        print(f"\n🌤️  Weather Data for {location.title()}")
        print("=" * 50)

        for data in weather_data:
            print(f"\n📡 Source: {data.source}")
            print(f"   Average Temperature: {data.avg_temp}°C")
            print(f"   Max Temperature: {data.max_temp}°C")
            print(f"   Min Temperature: {data.min_temp}°C")
            print(f"   Humidity: {data.humidity}%")
            print(f"   Pressure: {data.pressure} hPa")
            print(f"   Wind Speed: {data.wind_speed} m/s")
            print(f"   Precipitation: {data.precipitation} mm")

        # Aggregate data
        aggregated = self.aggregator.aggregate_weather_data(weather_data)

        print(f"\n📊 Aggregated Weather Summary")
        print("=" * 50)
        for key, value in aggregated.items():
            if not key.endswith(('_min', '_max', '_count')):
                print(f"{key.replace('_', ' ').title()}: {value}")

        # Generate forecast
        try:
            merged_series = self.merger.merge_series(weather_data)
            forecast = self.forecaster.forecast_temperature(merged_series)

            print(f"\n🔮 7-Day Temperature Forecast")
            print("=" * 50)

            recent_forecast = forecast.tail(7)
            for _, row in recent_forecast.iterrows():
                date = row['ds'].strftime('%Y-%m-%d')
                temp = round(row['yhat'], 1)
                lower = round(row['yhat_lower'], 1)
                upper = round(row['yhat_upper'], 1)
                print(f"{date}: {temp}°C (range: {lower}°C - {upper}°C)")

            # Create and save plot
            output_dir = Path(self.config.OUTPUT_DIR)
            output_dir.mkdir(exist_ok=True)

            plot_path = output_dir / f"forecast_{location.lower()}_{datetime.now().strftime('%Y%m%d')}.png"

            self.forecaster.plot_forecast(
                forecast.tail(14),
                merged_series.tail(30),
                title=f"Temperature Forecast for {location.title()}",
                save_path=str(plot_path)
            )

            logger.info(f"Forecast plot saved to {plot_path}")

        except Exception as e:
            logger.error(f"Failed to generate forecast: {e}")


def main():
    """Main entry point"""
    weather_app = WeatherWise()

    # You can change the location here or make it configurable
    location = "Krakow"

    try:
        weather_app.run_analysis(location)
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise


if __name__ == "__main__":
    main()
