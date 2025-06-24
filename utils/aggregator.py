# utils/aggregator.py
from typing import List, Dict

def aggregate_weather_data(data_sources: List[Dict]) -> Dict:
    fields = ["avg_temp", "max_temp", "min_temp", "avg_humidity"]
    result = {}

    for field in fields:
        values = [d[field] for d in data_sources if d.get(field) is not None]
        if values:
            result[field] = round(sum(values) / len(values), 2)
        else:
            result[field] = None

    return result
