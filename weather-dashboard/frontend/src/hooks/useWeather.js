import { useState, useEffect } from 'react';
import axios from 'axios';

export function useWeather(lat, lon, units) {
  const [weather, setWeather] = useState(null);
  const [forecast, setForecast] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchWeather = async () => {
    setLoading(true);
    setError(null);

    try {
      const [weatherRes, forecastRes] = await Promise.all([
        axios.get('/api/weather/current', {
          params: { lat, lon, units }
        }),
        axios.get('/api/weather/forecast', {
          params: { lat, lon, units }
        })
      ]);

      setWeather(weatherRes.data.data);
      setForecast(forecastRes.data.forecast);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to fetch weather data');
      console.error('Weather fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWeather();
    // Auto-refresh every 10 minutes
    const interval = setInterval(fetchWeather, 600000);
    return () => clearInterval(interval);
  }, [lat, lon, units]);

  return { weather, forecast, loading, error, refetch: fetchWeather };
}
