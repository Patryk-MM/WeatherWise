# dashboard/app.py
import streamlit as st
from main import WeatherWise
from utils.series_merge import TimeSeriesMerger
from models.prophet_model import WeatherForecaster

st.set_page_config(page_title="Prognoza pogody", layout="centered")

st.title("🌤️ Prognoza temperatury")
location = st.selectbox("Wybierz lokalizację:", ["Warsaw", "Krakow", "Poznan", "Gdansk"])

if st.button("🔍 Pobierz dane i przewiduj"):
    with st.spinner("⏳ Pobieranie danych pogodowych..."):
        try:
            weather = WeatherWise()
            merger = TimeSeriesMerger()
            prophet = WeatherForecaster()
            data = weather.fetch_all_data(location)
            combined_series = merger.merge_series(data)
            forecast = prophet.forecast_temperature(combined_series, periods=7)
        except Exception as e:
            st.error(f"Coś poszło nie tak: {e}")
        else:
            st.success("✅ Prognoza gotowa!")
            st.subheader("🔮 Prognozowane temperatury (°C)")
            st.dataframe(forecast.tail(7).set_index("ds"))
            st.subheader("📈 Wykres prognozy")
            fig = weather.forecaster.plot_forecast(
                forecast.tail(14),
                historical_df=combined_series.tail(30),
                title=f"Prognoza temperatury – {location}"
            )
            st.pyplot(fig)

