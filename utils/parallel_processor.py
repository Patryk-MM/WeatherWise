from multiprocessing import Pool, cpu_count
from typing import Callable, Iterable, Any

def fetch_single_client(client_and_location):
    client, location = client_and_location
    try:
        return client.fetch(location)
    except Exception as e:
        print(f"Błąd z {client.name}: {e}")
        return None

class ParallelWeatherProcessor:
    @staticmethod
    def run_parallel(func: Callable[[Any], Any], args_list: Iterable[Any], processes: int = None) -> list:
        if processes is None:
            processes = max(1, cpu_count() - 1)

        with Pool(processes=processes) as pool:
            results = pool.map(func, args_list)

        return results
