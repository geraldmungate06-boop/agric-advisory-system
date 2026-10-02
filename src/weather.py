from __future__ import annotations

import pandas as pd
import requests


def fetch_gweru_weather(start_date: str = "2020-01-01", end_date: str = "2024-12-31") -> pd.DataFrame:
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": -19.45,
        "longitude": 29.82,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "Africa/Harare",
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return pd.DataFrame()

    if "daily" not in payload:
        return pd.DataFrame()

    daily = payload["daily"]
    weather_df = pd.DataFrame(
        {
            "date": daily["time"],
            "temp_max": daily["temperature_2m_max"],
            "temp_min": daily["temperature_2m_min"],
            "rainfall": daily["precipitation_sum"],
        }
    )

    weather_df["date"] = pd.to_datetime(weather_df["date"])
    weather_df["month"] = weather_df["date"].dt.month
    weather_df["temp_mean"] = (weather_df["temp_max"] + weather_df["temp_min"]) / 2
    return weather_df


def get_optimal_planting_windows(weather_df: pd.DataFrame) -> pd.DataFrame:
    if weather_df.empty:
        return pd.DataFrame()

    monthly = (
        weather_df.groupby("month")
        .agg(
            mean_temp=("temp_mean", "mean"),
            rainfall=("rainfall", "mean"),
        )
        .reset_index()
    )

    monthly["planting_score"] = (
        monthly["rainfall"] * 0.7
        - abs(monthly["mean_temp"] - 25) * 0.8
        + monthly["rainfall"] * 0.2
    )

    monthly = monthly.sort_values("planting_score", ascending=False).head(3)
    month_names = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    }

    monthly["month_name"] = monthly["month"].map(month_names)
    return monthly[["month_name", "month", "mean_temp", "rainfall", "planting_score"]]
