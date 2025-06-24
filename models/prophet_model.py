from prophet import Prophet
import pandas as pd
import matplotlib.pyplot as plt


def forecast_temperature(df: pd.DataFrame, periods: int = 7) -> pd.DataFrame:
    df = df.rename(columns={"date": "ds", "temperature": "y"}) if "date" in df else df

    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)

    return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]


def plot_forecast(forecast_df, title="Prognoza temperatury"):
    plt.figure(figsize=(10, 5))
    plt.plot(forecast_df["ds"], forecast_df["yhat"], label="Prognozowana temp.", color="blue")
    plt.fill_between(forecast_df["ds"], forecast_df["yhat_lower"], forecast_df["yhat_upper"],
                     color="lightblue", alpha=0.4, label="Przedział ufności")
    plt.xticks(rotation=45)
    plt.xlabel("Data")
    plt.ylabel("Temperatura [°C]")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.grid(True)
    plt.show()
