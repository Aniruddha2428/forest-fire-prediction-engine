from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import os
from urllib.parse import quote
import numpy as np
import httpx

app = FastAPI(title="Forest Fire Prediction API")

# Add CORS middleware to allow React frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the trained model at startup
model_path = os.path.join(os.path.dirname(__file__), "best_model.pkl")
try:
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Define input schemas
class WeatherFeatures(BaseModel):
    Temperature: float
    Humidity: float
    Wind_Speed: float
    Rain: float

class LocationQuery(BaseModel):
    location_name: str


def _predict_with_model(features: WeatherFeatures):
    if not model:
        raise HTTPException(status_code=500, detail="Model not loaded properly.")

    input_data = np.array([[
        features.Temperature,
        features.Humidity,
        features.Wind_Speed,
        features.Rain
    ]], dtype=float)

    probability = float(model.predict_proba(input_data)[0][1])
    prediction = int(probability > 0.5)
    return probability, prediction


@app.post("/predict")
def predict_fire(features: WeatherFeatures):
    probability, prediction = _predict_with_model(features)

    return {
        "prediction": prediction,
        "probability": probability,
        "message": "High Fire Risk!" if prediction == 1 else "Forest is Safe",
        "weather_data": features.dict()
    }


@app.post("/predict-realtime")
async def predict_realtime(query: LocationQuery):
    if not model:
        raise HTTPException(status_code=500, detail="Model not loaded properly.")

    async with httpx.AsyncClient(timeout=15.0) as client:
        # Step 1: Geocode the location name
        async def get_geo(query_str: str):
            query_str = (query_str or "").strip()
            if not query_str:
                return None

            encoded_query = quote(query_str)
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_query}&count=10&language=en&format=json"

            try:
                resp = await client.get(url)
            except httpx.HTTPError as exc:
                raise HTTPException(status_code=502, detail=f"Location service failed: {exc}") from exc

            if resp.status_code != 200:
                raise HTTPException(status_code=502, detail="Location service is currently unavailable.")

            try:
                payload = resp.json()
            except ValueError as exc:
                raise HTTPException(status_code=502, detail="Location service returned an invalid response.") from exc

            results = payload.get("results") or []
            if not results:
                return None

            if "," not in query_str.lower() and "india" not in query_str.lower():
                india_results = [r for r in results if str(r.get("country_code", "")).upper() == "IN"]
                if india_results:
                    return india_results[0]

            return results[0]

        location_data = await get_geo(query.location_name)

        if not location_data:
            raise HTTPException(status_code=404, detail="Location not found. Please try a more specific city name (for example, Jaipur instead of Rajasthan).")

        lat = location_data.get("latitude")
        lon = location_data.get("longitude")
        if lat is None or lon is None:
            raise HTTPException(status_code=502, detail="Location service returned incomplete coordinates.")

        resolved_name = f"{location_data.get('name')}, {location_data.get('country', '')}"

        # Step 2: Fetch current weather for these coordinates
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m"
        try:
            weather_resp = await client.get(weather_url)
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail=f"Weather service failed: {exc}") from exc

        if weather_resp.status_code != 200:
            raise HTTPException(status_code=502, detail="Failed to fetch weather data.")

        try:
            current = weather_resp.json().get("current")
        except ValueError as exc:
            raise HTTPException(status_code=502, detail="Weather service returned an invalid response.") from exc

        if not isinstance(current, dict):
            raise HTTPException(status_code=502, detail="Weather service returned an unexpected payload.")

        temperature = current.get("temperature_2m")
        humidity = current.get("relative_humidity_2m")
        rain = current.get("precipitation")
        wind_speed = current.get("wind_speed_10m")

        if temperature is None or humidity is None or rain is None or wind_speed is None:
            raise HTTPException(status_code=502, detail="Weather data was incomplete.")

        features = WeatherFeatures(
            Temperature=float(temperature),
            Humidity=float(humidity),
            Rain=float(rain),
            Wind_Speed=float(wind_speed)
        )

        probability, prediction = _predict_with_model(features)

        return {
            "prediction": prediction,
            "probability": probability,
            "message": "High Fire Risk!" if prediction == 1 else "Forest is Safe",
            "resolved_location": resolved_name,
            "latitude": lat,
            "longitude": lon,
            "weather_data": features.dict()
        }

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Forest Fire API is running"}
