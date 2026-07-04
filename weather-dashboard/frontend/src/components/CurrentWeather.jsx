import React from 'react';
import { Cloud, Wind, Droplets, Eye, Gauge } from 'lucide-react';

function CurrentWeather({ weather, location, units }) {
  const tempUnit = units === 'metric' ? '°C' : '°F';
  const speedUnit = units === 'metric' ? 'km/h' : 'mph';

  return (
    <div className="current-weather">
      <div className="weather-header">
        <div className="location">{location}</div>
        <div className="timestamp">
          {new Date().toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          })}
        </div>
      </div>

      <div className="weather-main">
        <div className="temperature-display">
          <div className="temp">{Math.round(weather.temp)}{tempUnit}</div>
          <div className="description">{weather.description}</div>
          <div className="feels-like">Feels like {Math.round(weather.feels_like)}{tempUnit}</div>
        </div>

        <div className="weather-icon">
          <Cloud size={80} />
        </div>
      </div>

      <div className="weather-details">
        <div className="detail-card">
          <div className="detail-icon"><Droplets size={24} /></div>
          <div className="detail-content">
            <div className="detail-label">Humidity</div>
            <div className="detail-value">{weather.humidity}%</div>
          </div>
        </div>

        <div className="detail-card">
          <div className="detail-icon"><Wind size={24} /></div>
          <div className="detail-content">
            <div className="detail-label">Wind Speed</div>
            <div className="detail-value">{Math.round(weather.wind_speed)} {speedUnit}</div>
          </div>
        </div>

        {weather.pressure && (
          <div className="detail-card">
            <div className="detail-icon"><Gauge size={24} /></div>
            <div className="detail-content">
              <div className="detail-label">Pressure</div>
              <div className="detail-value">{weather.pressure} mb</div>
            </div>
          </div>
        )}

        {weather.visibility && (
          <div className="detail-card">
            <div className="detail-icon"><Eye size={24} /></div>
            <div className="detail-content">
              <div className="detail-label">Visibility</div>
              <div className="detail-value">{(weather.visibility / 1000).toFixed(1)} km</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default CurrentWeather;
