import requests
import pandas as pd
import numpy as np
import time

# Define locations (latitude, longitude)
LOCATIONS = {
    # India Focus
    "Jharkhand_India": (23.6102, 85.2799),
    "Bangalore_India": (12.9716, 77.5946),
    "New_Delhi_India": (28.6139, 77.2090),
    "Odisha_India": (20.9517, 85.0985),
    "Uttarakhand_India": (30.0668, 79.0193),
    "Maharashtra_India": (19.7515, 75.7139),
    # Global
    "California_USA": (36.7783, -119.4179),
    "Amazon_Brazil": (-3.4653, -62.2159),
    "New_South_Wales_Australia": (-31.2532, 146.9211),
    "British_Columbia_Canada": (53.7267, -127.6476)
}

START_DATE = "2022-01-01"
END_DATE = "2023-12-31" # 2 years of data

def fetch_weather_data(name, lat, lon):
    print(f"Fetching data for {name}...")
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={START_DATE}&end_date={END_DATE}&daily=temperature_2m_max,relative_humidity_2m_mean,wind_speed_10m_max,precipitation_sum&timezone=auto"
    
    # Retry mechanism
    for attempt in range(3):
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            df = pd.DataFrame(data['daily'])
            df['Location'] = name
            return df
        except Exception as e:
            print(f"Attempt {attempt+1} failed for {name}: {e}")
            time.sleep(2)
            
    print(f"Failed to fetch data for {name} after 3 attempts.")
    return None

def calculate_fire_probability(row):
    """
    Synthetic heuristic to simulate whether a fire occurred based on weather conditions.
    High Temp + Low Humidity + High Wind + No Rain = High Probability of Fire.
    """
    temp = row['temperature_2m_max']
    rh = row['relative_humidity_2m_mean']
    wind = row['wind_speed_10m_max']
    rain = row['precipitation_sum']
    
    # Handle missing values
    if pd.isna(temp) or pd.isna(rh) or pd.isna(wind) or pd.isna(rain):
        return 0
        
    score = 0
    if temp > 30: score += 2
    if temp > 38: score += 2
    if rh < 40: score += 2
    if rh < 25: score += 2
    if rain == 0: score += 2
    if wind > 20: score += 1
    
    # If score is high, there's a strong chance of fire. Introduce some randomness.
    if temp > 35 and rh < 20 and rain == 0:
        return 1 # Immediate fire risk in extreme dry heat
    
    if score >= 7:
        return 1 # Very high risk
    elif score >= 5:
        return np.random.choice([1, 0], p=[0.6, 0.4])
    elif score >= 3:
        return np.random.choice([1, 0], p=[0.1, 0.9])
    else:
        return 0 # Definitely safe

def main():
    all_dataframes = []
    
    for name, coords in LOCATIONS.items():
        df = fetch_weather_data(name, coords[0], coords[1])
        if df is not None:
            all_dataframes.append(df)
        time.sleep(1) # Be nice to the API
        
    if not all_dataframes:
        print("No data fetched.")
        return
        
    final_df = pd.concat(all_dataframes, ignore_index=True)
    
    # Drop rows with NaN values
    final_df = final_df.dropna()
    
    # Calculate probability using original API column names
    final_df['Classes'] = final_df.apply(calculate_fire_probability, axis=1)

    # Rename columns to match our ML model needs
    final_df = final_df.rename(columns={
        'temperature_2m_max': 'Temperature',
        'relative_humidity_2m_mean': 'Humidity',
        'wind_speed_10m_max': 'Wind_Speed',
        'precipitation_sum': 'Rain'
    })
    
    cols = ['Location', 'time', 'Temperature', 'Humidity', 'Wind_Speed', 'Rain', 'Classes']
    final_df = final_df[cols]
    
    output_filename = "global_forest_fire_dataset.csv"
    final_df.to_csv(output_filename, index=False)
    print(f"\\nSuccessfully generated dataset with {len(final_df)} rows: {output_filename}")
    
    # Print some statistics
    print("\\nDataset Summary:")
    print(final_df['Classes'].value_counts(normalize=True).mul(100).round(2).astype(str) + '%')

if __name__ == "__main__":
    main()
