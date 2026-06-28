import React, { useEffect, useRef, useState } from 'react';
import Globe from 'react-globe.gl';

const GlobeView = ({ coords, prediction }) => {
  const globeEl = useRef();
  const [pointsData, setPointsData] = useState([]);

  useEffect(() => {
    // Enable auto-rotation
    globeEl.current.controls().autoRotate = true;
    globeEl.current.controls().autoRotateSpeed = 0.5;

    if (coords && coords.lat && coords.lng) {
      // Add a point to the globe
      const newPoint = {
        lat: coords.lat,
        lng: coords.lng,
        size: 0.2,
        color: prediction === 1 ? '#ff4d4d' : '#4dff88',
        label: prediction === 1 ? '🔥 HIGH RISK' : '✅ SAFE'
      };
      
      setPointsData([newPoint]);

      // Rotate globe to point of interest
      globeEl.current.pointOfView({
        lat: coords.lat,
        lng: coords.lng,
        altitude: 1.8
      }, 2000); 
    }
  }, [coords, prediction]);

  return (
    <div className="globe-background">
      <Globe
        ref={globeEl}
        globeImageUrl="https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg"
        bumpImageUrl="https://unpkg.com/three-globe/example/img/earth-topology.png"
        backgroundImageUrl="https://unpkg.com/three-globe/example/img/night-sky.png"
        atmosphereColor="#3a228a"
        atmosphereAltitude={0.15}
        pointsData={pointsData}
        pointColor="color"
        pointAltitude={0.07}
        pointRadius="size"
        pointLabel="label"
        labelsData={pointsData}
        labelText="label"
        labelSize={2}
        labelDotRadius={0.4}
        labelColor={() => 'rgba(255, 255, 255, 0.9)'}
        labelResolution={2}
      />
    </div>
  );
};

export default GlobeView;
