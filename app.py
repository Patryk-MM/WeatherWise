# dashboard/app.py
import streamlit as st
from main import WeatherWise
from utils.series_merge import TimeSeriesMerger
from models.prophet_model import WeatherForecaster

st.set_page_config(page_title="Prognoza pogody", layout="centered")

st.title("Prognoza temperatury")
location = st.selectbox("Wybierz lokalizację:", ["Warsaw", "Krakow", "Poznan", "Gdansk"])

if st.button("Pobierz dane i pokaz prognoze"):
    with st.spinner("Pobieranie danych pogodowych..."):
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
            st.success("Prognoza gotowa!")


           # st.subheader("Prognozowane temperatury (°C)")
           # st.dataframe(forecast.tail(7).set_index("ds"))

            forecast_display = forecast.tail(7).rename(columns={
                "ds": "Dzień",
                "yhat": "Prognoza",
                "yhat_lower": "Min Temp",
                "yhat_upper": "Max Temp"
            })
            forecast_display["Dzień"] = forecast_display["Dzień"].dt.strftime("%d.%m.%Y")
            forecast_display = forecast_display.set_index("Dzień")

            st.subheader("Prognoza temperatur na 7 dni")
            st.dataframe(forecast_display)



            st.subheader("Wykres prognozy")
            fig = weather.forecaster.plot_forecast(
                forecast.tail(14),
                historical_df=combined_series.tail(30),
                title=f"Prognoza temperatury - {location}"
            )

# zapisanie wykresu
            from pathlib import Path
            from datetime import datetime

            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            plot_path = output_dir / f"forecast_{location.lower()}_{datetime.now().strftime('%Y%m%d')}.png"
            fig.savefig(str(plot_path), dpi=300, bbox_inches='tight')




#pokazuje wykres na stronie
            st.pyplot(fig)

