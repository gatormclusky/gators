import React from 'react';
import { Cloud, CloudRain, Sun } from 'lucide-react';

function Forecast({ forecast, units }) {
  const tempUnit = units === 'metric' ? '°C' : '°F';

  const getWeatherIcon = (description) => {
    if (description.includes('rain')) return <CloudRain size={32} />;
    if (description.includes('cloud')) return <Cloud size={32} />;
    return <Sun size={32} />;
  };

  return (
    <div className="forecast">
      <h2>5-Day Forecast</h2>
      <div className="forecast-grid">
        {forecast.slice(0, 5).map((day, index) => (
          <div key={index} className="forecast-card">
            <div className="forecast-date">
              {new Date(day.date).toLocaleDateString('en-US', { 
                weekday: 'short',
                month: 'short',
                day: 'numeric'
              })}
            </div>
            <div className="forecast-icon">
              {getWeatherIcon(day.description)}
            </div>
            <div className="forecast-temps">
              <div className="temp-max">{Math.round(day.temp_max)}{tempUnit}</div>
              <div className="temp-min">{Math.round(day.temp_min)}{tempUnit}</div>
            </div>
            <div className="forecast-description">{day.description}</div>
            {day.precipitation > 0 && (
              <div className="forecast-precip">💧 {day.precipitation}mm</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Forecast;
