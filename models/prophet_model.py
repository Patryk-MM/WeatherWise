from prophet import Prophet
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from config.settings import WeatherConfig
import os


class WeatherForecaster:
    def __init__(self):
        self.config = WeatherConfig()
        self.model = None

    def forecast_temperature(self, df: pd.DataFrame, periods: int = None) -> pd.DataFrame:
        if periods is None:
            periods = self.config.FORECAST_DAYS

        if "date" in df.columns:
            df = df.rename(columns={"date": "ds", "temperature": "y"})

        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            changepoint_prior_scale=0.05
        )

        self.model.fit(df)

        future = self.model.make_future_dataframe(periods=periods)
        forecast = self.model.predict(future)

        return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]

    def plot_forecast(self, forecast_df: pd.DataFrame, historical_df: pd.DataFrame = None,
                      title: str = "Temperature Forecast", save_path: str = None):

        plt.style.use(self.config.PLOT_STYLE)
        fig, ax = plt.subplots(figsize=self.config.FIGURE_SIZE)

        if historical_df is not None:
            ax.plot(historical_df["ds"], historical_df["y"],
                    label="Historical Data", color="gray", alpha=0.7, linewidth=1)

        ax.plot(forecast_df["ds"], forecast_df["yhat"],
                label="Forecast", color="blue", linewidth=2)

        ax.fill_between(forecast_df["ds"], forecast_df["yhat_lower"], forecast_df["yhat_upper"],
                        color="lightblue", alpha=0.4, label="Confidence Interval")

        ax.set_xlabel("Date")
        ax.set_ylabel("Temperature (°C)")
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save if needed
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            fig.savefig(save_path, dpi=300, bbox_inches='tight')

        return fig
