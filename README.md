# Global Forest Fire AI Prediction System

This project is a high-performance, real-time forest fire prediction system. It utilizes a machine learning model trained on global weather data and integrates with live weather APIs to predict fire risk for any location worldwide.

## Forest Fire Prediction Parameters

Here are the main parameters that forest fire prediction models depend on:

### 1. Meteorological & Weather Variables (Most Common)
These directly affect how dry the fuel is and how fast a fire could spread:
*   **Temperature:** Higher temperatures increase evaporation, drying out vegetation.
*   **Relative Humidity:** Low humidity makes it easier for fires to ignite and spread.
*   **Wind Speed:** High winds supply more oxygen and carry embers, causing rapid fire spread.
*   **Wind Direction:** Helps predict which way the fire will travel.
*   **Precipitation (Rainfall):** The amount of recent rain drastically reduces fire probability.

### 2. The Fire Weather Index (FWI) System
Many advanced models use calculated indices rather than raw weather data. The Canadian Forest Fire Weather Index is a global standard and includes:
*   **FFMC (Fine Fuel Moisture Code):** Indicates how dry the surface litter (leaves, pine needles) is.
*   **DMC (Duff Moisture Code):** Measures the moisture in the loosely compacted organic layers of the soil.
*   **DC (Drought Code):** Measures deep soil moisture (indicating long-term drought).
*   **ISI (Initial Spread Index):** Combines wind speed and FFMC to predict the rate of spread.

### 3. Topographical Variables (Terrain)
The shape of the land heavily influences fire behavior:
*   **Elevation:** Higher altitudes usually have different vegetation and cooler temperatures.
*   **Slope:** Fires spread much faster uphill because the heat from the flames pre-heats the fuel above it.
*   **Aspect:** The compass direction a slope faces (e.g., South-facing slopes get more sun and are generally drier and warmer).

### 4. Fuel & Vegetation
*   **Vegetation Type / Land Cover:** Whether the area is grassland, dense pine forest, or brush. Different plants burn at different intensities.
*   **Canopy Density:** How thick the treetops are.

### 5. Anthropogenic (Human) Factors
Since many fires are started by humans, models often include spatial proximity data:
*   **Distance to Roads:** Closer to roads usually means a higher chance of a cigarette or car fire sparking the brush.
*   **Distance to Settlements / Campsites:** Higher human activity increases accidental ignitions.

---

## Parameters used in this AI System

| Parameter | Description |
| :--- | :--- |
| **Temperature** | Max temperature in Celsius |
| **Humidity** | Relative Humidity in % |
| **Wind Speed** | Wind speed in km/h |
| **Rain** | Total rain in mm |
| **Classes** | Target variable (1 = Fire Risk, 0 = Safe) |

### Why these parameters for Real-Time?
In our current real-time system, we prioritize **Temperature, Humidity, Wind Speed, and Rain**.
*   **Global Availability:** These are the most reliable real-time metrics available globally from satellite weather stations via the Open-Meteo API.
*   **Direct Impact:** They are the "Big Four" that determine immediate atmospheric fire risk.
*   **Model Accuracy:** Our Machine Learning model is optimized to detect high-risk patterns within these environmental variables across different continents.

---

## Run Commands

### Backend (FastAPI)
```bash
uv run uvicorn backend.main:app --reload
```

### Frontend (React/Vite)
```bash
cd frontend && npm run dev
```
