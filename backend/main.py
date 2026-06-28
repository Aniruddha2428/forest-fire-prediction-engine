from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import os
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

@app.post("/predict")
def predict_fire(features: WeatherFeatures):
    if not model:
        raise HTTPException(status_code=500, detail="Model not loaded properly.")
        
    input_data = np.array([[
        features.Temperature,
        features.Humidity,
        features.Wind_Speed,
        features.Rain
    ]])
    
    probability = model.predict_proba(input_data)[0][1]
    prediction = int(probability > 0.5)
    
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
        
    async with httpx.AsyncClient() as client:
        # Step 1: Geocode the location name
        async def get_geo(query_str):
            # Fetch up to 10 results to check for Indian alternatives
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={query_str}&count=10&language=en&format=json"
            resp = await client.get(url)
            if resp.status_code == 200 and resp.json().get('results'):
                results = resp.json()['results']
                
                # If user didn't specify a country, prioritize India (IN)
                if "," not in query_str.lower() and "india" not in query_str.lower():
                    india_results = [r for r in results if r.get('country_code') == 'IN']
                    if india_results:
                        return india_results[0]
                
                return results[0] # Fallback to the first match
            return None

        location_data = await get_geo(query.location_name)

        if not location_data:
            raise HTTPException(status_code=404, detail="Location not found. Please try a specific city name (e.g., Jaipur instead of Rajasthan).")

        lat = location_data['latitude']
        lon = location_data['longitude']
        resolved_name = f"{location_data.get('name')}, {location_data.get('country', '')}"

        # Step 2: Fetch current weather for these coordinates
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m"
        weather_resp = await client.get(weather_url)
        
        if weather_resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch weather data.")
            
        current = weather_resp.json()['current']
        
        features = WeatherFeatures(
            Temperature=current['temperature_2m'],
            Humidity=current['relative_humidity_2m'],
            Rain=current['precipitation'],
            Wind_Speed=current['wind_speed_10m']
        )
        
        # Step 3: Predict
        input_data = np.array([[
            features.Temperature,
            features.Humidity,
            features.Wind_Speed,
            features.Rain
        ]])
        
        probability = model.predict_proba(input_data)[0][1]
        prediction = int(probability > 0.5)
        
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
