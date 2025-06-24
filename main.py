# main.py
import importlib
import pkgutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from api_clients.base import WeatherAPIClient
from utils.aggregator import aggregate_weather_data
from models.prophet_model import forecast_temperature, plot_forecast
from utils.series_merge import merge_series

def get_all_clients():
    clients = []
    for _, modname, _ in pkgutil.iter_modules(['api_clients']):
        if modname in ('base', '__init__'):
            continue
        module = importlib.import_module(f'api_clients.{modname}')
        for attr in dir(module):
            obj = getattr(module, attr)
            if isinstance(obj, type) and issubclass(obj, WeatherAPIClient) and obj is not WeatherAPIClient:
                clients.append(obj())
    return clients

def fetch_all(location: str):
    results = []
    clients = get_all_clients()

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(client.fetch, location): client for client in clients}
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"Error: {e}")
    return results

if __name__ == "__main__":
    location = "Warsaw"
    all_data = fetch_all(location)
    print("\n📡 Zebrane dane pogodowe:\n")
    for entry in all_data:
        print(f"Źródło: {entry['source']}")
        for k, v in entry.items():
            if k != 'source':
                print(f"  {k}: {v}")
        print()

    # 🔁 Agregacja
    aggregated = aggregate_weather_data(all_data)
    print("📊 Agregowane dane pogodowe (średnia ze źródeł):\n")
    for k, v in aggregated.items():
        print(f"{k}: {v}")

    combined_series = merge_series(all_data)
    forecast = forecast_temperature(combined_series, periods=7)

    print(forecast.tail(7).to_string(index=False))

    plot_forecast(forecast.tail(14), title="Prognoza temperatury (ostatnie + 7 dni)")