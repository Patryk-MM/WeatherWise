import pandas as pd
from typing import List, Dict

def merge_series(sources: List[Dict]) -> pd.DataFrame:
    series_list = []

    for src in sources:
        if "series" in src and not src["series"].empty:
            df = src["series"].copy()

            # Naprawa: automatycznie wykrywamy nazwę kolumny z datą
            date_col = next((col for col in df.columns if col.lower() in ['date', 'ds', 'time']), None)
            temp_col = next((col for col in df.columns if 'temp' in col.lower() or col.lower() == 'y'), None)

            if not date_col or not temp_col:
                print(f"⚠️ Nieprawidłowy format danych w {src['source']}")
                continue

            df = df.rename(columns={date_col: "ds", temp_col: "y"})
            series_list.append(df[["ds", "y"]])

    if not series_list:
        raise ValueError("No time series available in any source.")

    merged = pd.concat(series_list).groupby("ds", as_index=False).mean()
    merged["ds"] = pd.to_datetime(merged["ds"])
    return merged.sort_values("ds")
