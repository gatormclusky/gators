import React, { useState, useEffect } from 'react';
import './App.css';
import CurrentWeather from './components/CurrentWeather';
import Forecast from './components/Forecast';
import SearchBar from './components/SearchBar';
import Favorites from './components/Favorites';
import ThemeToggle from './components/ThemeToggle';
import { useWeather } from './hooks/useWeather';
import { useLocalStorage } from './hooks/useLocalStorage';

function App() {
  const [theme, setTheme] = useLocalStorage('theme', 'light');
  const [units, setUnits] = useLocalStorage('units', 'metric');
  const [location, setLocation] = useLocalStorage('currentLocation', {
    lat: 51.5085,
    lon: -0.1257,
    name: 'London, UK'
  });
  
  const { weather, forecast, loading, error, refetch } = useWeather(
    location.lat,
    location.lon,
    units
  );

  useEffect(() => {
    // Apply theme
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }, [theme]);

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  const toggleUnits = () => {
    setUnits(units === 'metric' ? 'imperial' : 'metric');
  };

  const handleLocationSelect = (newLocation) => {
    setLocation(newLocation);
  };

  return (
    <div className={`app ${theme}`}>
      <header className="header">
        <div className="container">
          <h1>Weather Dashboard</h1>
          <div className="header-controls">
            <button onClick={toggleUnits} className="unit-toggle">
              {units === 'metric' ? '°F' : '°C'}
            </button>
            <ThemeToggle theme={theme} onToggle={toggleTheme} />
          </div>
        </div>
      </header>

      <main className="container">
        <SearchBar onLocationSelect={handleLocationSelect} />
        
        <div className="content">
          <div className="main-section">
            {loading && <div className="loading">Loading weather data...</div>}
            {error && <div className="error">{error}</div>}
            
            {weather && (
              <>
                <CurrentWeather 
                  weather={weather} 
                  location={location.name}
                  units={units}
                />
                <Forecast forecast={forecast} units={units} />
              </>
            )}
          </div>

          <aside className="sidebar">
            <Favorites 
              currentLocation={location}
              onLocationSelect={handleLocationSelect}
            />
          </aside>
        </div>
      </main>

      <footer className="footer">
        <p>&copy; 2024 Weather Dashboard. Data from Open-Meteo, OpenWeatherMap, WeatherAPI</p>
      </footer>
    </div>
  );
}

export default App;
