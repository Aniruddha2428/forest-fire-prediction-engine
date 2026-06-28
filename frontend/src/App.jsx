import { useState } from 'react';
import GlobeView from './GlobeView';

const HISTORICAL_EXAMPLES = [
  {
    name: "Simlipal Fire (Odisha)",
    description: "March 2021 Heatwave",
    metrics: { Temperature: 40, Humidity: 12, Wind_Speed: 18, Rain: 0 },
    coords: { lat: 21.92, lng: 86.41 }
  },
  {
    name: "Bandipur Wildfire",
    description: "Feb 2019 Dry Spell",
    metrics: { Temperature: 32, Humidity: 25, Wind_Speed: 22, Rain: 0 },
    coords: { lat: 11.66, lng: 76.62 }
  },
  {
    name: "Uttarakhand Blaze",
    description: "April 2024 Drought",
    metrics: { Temperature: 38, Humidity: 15, Wind_Speed: 15, Rain: 0 },
    coords: { lat: 30.06, lng: 79.01 }
  }
];

function App() {
  const [mode, setMode] = useState('live'); 
  const [locationName, setLocationName] = useState('');
  const [formData, setFormData] = useState({ Temperature: 35, Humidity: 30, Wind_Speed: 20, Rain: 0 });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [globeCoords, setGlobeCoords] = useState({ lat: 20, lng: 77 }); 

  const handleLiveSubmit = async (e) => {
    if (e) e.preventDefault();
    if (!locationName.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const response = await fetch('http://localhost:8000/predict-realtime', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ location_name: locationName })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Location Not Found");
      setResult(data);
      if (data.latitude && data.longitude) setGlobeCoords({ lat: data.latitude, lng: data.longitude });
    } catch (error) {
      setResult({ error: error.message });
    } finally { setLoading(false); }
  };

  const handleManualSubmit = async (e, customData = null, coords = null) => {
    if (e) e.preventDefault();
    setLoading(true);
    setResult(null);
    const dataToSubmit = customData || formData;
    try {
      const response = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dataToSubmit)
      });
      const data = await response.json();
      setResult(data);
      if (coords) setGlobeCoords(coords);
    } catch (error) {
      setResult({ error: "Server Error" });
    } finally { setLoading(false); }
  };

  const loadExample = (ex) => {
    setMode('manual');
    setFormData(ex.metrics);
    handleManualSubmit(null, ex.metrics, ex.coords);
  };

  return (
    <div className="main-container">
      <GlobeView coords={globeCoords} prediction={result?.prediction} />

      <div className="ui-overlay">
        <div className="top-bar">
          <h1 className="title-main">FOREST FIRE AI</h1>
          <form className="search-container" onSubmit={handleLiveSubmit}>
            <input 
              className="search-input"
              type="text" 
              placeholder="Search any global region (e.g. Amazon, Odisha, California)..."
              value={locationName} 
              onChange={(e) => setLocationName(e.target.value)} 
            />
            <button className="search-btn" type="submit" disabled={loading}>
              {loading ? "SEARCHING..." : "ANALYZE"}
            </button>
          </form>
        </div>

        <div className="mode-toggle-mini">
          <button className={`mini-btn ${mode === 'live' ? 'active' : ''}`} onClick={() => setMode('live')}>LIVE</button>
          <button className={`mini-btn ${mode === 'manual' ? 'active' : ''}`} onClick={() => setMode('manual')}>SIMULATE</button>
        </div>

        <div className="content-area">
          {result && (
            <div className="result-overlay">
              {result.error ? (
                <div className="result-card result-danger">
                  <p>{result.error}</p>
                </div>
              ) : (
                <>
                  <p style={{color: '#ff8e53', fontSize: '0.8rem', margin: '0 0 0.5rem 0'}}>📍 {result.resolved_location}</p>
                  <div className={`result-card ${result.prediction === 1 ? 'result-danger' : 'result-safe'}`}>
                    <h2 style={{margin: 0}}>{result.message}</h2>
                    <p style={{fontSize: '0.8rem', opacity: 0.8, margin: '5px 0 0 0'}}>
                      Prediction Confidence: {(result.probability * 100).toFixed(1)}%
                    </p>
                  </div>

                  <div className="weather-cards">
                    <div className="w-card"><span className="w-label">TEMP</span><span className="w-value">{result.weather_data.Temperature}°C</span></div>
                    <div className="w-card"><span className="w-label">HUMIDITY</span><span className="w-value">{result.weather_data.Humidity}%</span></div>
                    <div className="w-card"><span className="w-label">WIND</span><span className="w-value">{result.weather_data.Wind_Speed}k/h</span></div>
                    <div className="w-card"><span className="w-label">RAIN</span><span className="w-value">{result.weather_data.Rain}mm</span></div>
                  </div>
                </>
              )}
            </div>
          )}

          {mode === 'manual' && !result && (
            <div className="result-overlay">
              <h3 style={{margin: '0 0 1rem 0'}}>Parameter Simulation</h3>
              <form onSubmit={handleManualSubmit} className="simulation-panel">
                <div className="form-group-sim">
                  <label>Temperature <span>{formData.Temperature}°C</span></label>
                  <input type="range" min="-10" max="50" step="0.5" name="Temperature" value={formData.Temperature} onChange={(e) => setFormData({...formData, Temperature: parseFloat(e.target.value)})} />
                </div>
                <div className="form-group-sim">
                  <label>Humidity <span>{formData.Humidity}%</span></label>
                  <input type="range" min="0" max="100" step="1" name="Humidity" value={formData.Humidity} onChange={(e) => setFormData({...formData, Humidity: parseFloat(e.target.value)})} />
                </div>
                <button className="search-btn" style={{width: '100%', marginTop: '1rem'}} type="submit">RUN SIMULATION</button>
              </form>
            </div>
          )}
        </div>

        <div className="historical-strip">
          {HISTORICAL_EXAMPLES.map((ex, i) => (
            <div key={i} className="example-mini-card" onClick={() => loadExample(ex)}>
              <h5>{ex.name}</h5>
              <p>{ex.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
