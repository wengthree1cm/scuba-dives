# routes_conditions.py
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import date as date_cls
import httpx

router = APIRouter(prefix="/api", tags=["conditions"])

OPEN_METEO_GEO = "https://geocoding-api.open-meteo.com/v1/search"
OPEN_METEO_WEATHER = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_MARINE = "https://marine-api.open-meteo.com/v1/marine"

@router.get("/geocode")
async def geocode(q: str = Query(..., min_length=1), count: int = 5, language: str = "zh", format: str = "json"):
    params = {"name": q, "count": count, "language": "en", "format": format}
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(OPEN_METEO_GEO, params=params)
    r.raise_for_status()
    data = r.json()
    results = []
    for item in data.get("results", []):
        results.append({
            "name": item.get("name"),
            "country": item.get("country"),
            "admin1": item.get("admin1"),
            "lat": item.get("latitude"),
            "lon": item.get("longitude"),
        })
    return {"results": results}

@router.get("/conditions")
async def conditions(
    lat: float,
    lon: float,
    date: Optional[str] = None,   
    days: int = 1,                
    timezone: str = "auto"
):
    today = date_cls.today()
    if date:
        try:
            start = date_cls.fromisoformat(date)
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式应为 YYYY-MM-DD")
    else:
        start = today
    end = start
    if days > 1:
        end = start.fromordinal(start.toordinal() + min(days - 1, 9))  

    weather_params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "wind_speed_10m",
            "wind_direction_10m",
            "precipitation",
            "cloud_cover",
            "visibility"
        ]),
        "daily": ",".join([
            "sunrise",
            "sunset",
            "uv_index_max",
            "precipitation_sum",
            "wind_speed_10m_max",
            "wind_gusts_10m_max",
        ]),
        "timezone": timezone,
        "start_date": start.isoformat(),
        "end_date": end.isoformat()
    }

    marine_params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join([
            "wave_height",
            "wave_direction",
            "wave_period",
            "swell_wave_height",
            "swell_wave_direction",
            "swell_wave_period",
            "wind_wave_height",
            "wind_wave_direction",
            "wind_wave_period",
            "sea_surface_temperature"
        ]),
        "timezone": timezone,
        "start_date": start.isoformat(),
        "end_date": end.isoformat()
    }

    async with httpx.AsyncClient(timeout=20) as client:
        wx, mx = await client.get(OPEN_METEO_WEATHER, params=weather_params), await client.get(OPEN_METEO_MARINE, params=marine_params)

    wx.raise_for_status()
    mx.raise_for_status()

    weather = wx.json()
    marine = mx.json()

    out = {
        "location": {"lat": lat, "lon": lon},
        "range": {"start": start.isoformat(), "end": end.isoformat()},
        "timezone": weather.get("timezone", timezone),
        "current_hint": {
            "temp_c": (weather.get("hourly", {}).get("temperature_2m") or [None])[0],
            "wind_speed": (weather.get("hourly", {}).get("wind_speed_10m") or [None])[0],
            "wind_dir": (weather.get("hourly", {}).get("wind_direction_10m") or [None])[0],
            "visibility": (weather.get("hourly", {}).get("visibility") or [None])[0],
            "wave_height": (marine.get("hourly", {}).get("wave_height") or [None])[0],
            "water_temp": (marine.get("hourly", {}).get("water_temperature") or [None])[0]
        },
        "hourly": {
            "time": weather.get("hourly", {}).get("time", []),
            "temp_c": weather.get("hourly", {}).get("temperature_2m", []),
            "wind_speed": weather.get("hourly", {}).get("wind_speed_10m", []),
            "precip": weather.get("hourly", {}).get("precipitation", []),
            "cloud": weather.get("hourly", {}).get("cloud_cover", []),
            "visibility": weather.get("hourly", {}).get("visibility", []),
            "wave_height": marine.get("hourly", {}).get("wave_height", []),
            "wave_period": marine.get("hourly", {}).get("wave_period", []),
            "water_temp": marine.get("hourly", {}).get("water_temperature", []),
        },
        "daily": weather.get("daily", {})
    }
    return out
