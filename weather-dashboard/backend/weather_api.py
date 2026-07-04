"""
Weather API Client - Multi-provider support
Supports: Open-Meteo, OpenWeatherMap, WeatherAPI
"""

import requests
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from functools import wraps

logger = logging.getLogger(__name__)


class APIError(Exception):
    """API Error exception"""
    pass


class WeatherClient:
    """Main weather client with multi-provider support"""
    
    def __init__(self):
        self.openweather_key = os.getenv('OPENWEATHER_API_KEY')
        self.weatherapi_key = os.getenv('WEATHERAPI_KEY')
        self.openmeteo_url = 'https://api.open-meteo.com/v1'
        self.openweather_url = 'https://api.openweathermap.org/data/2.5'
        self.weatherapi_url = 'https://api.weatherapi.com/v1'
        
        self.timeout = 10
    
    def _retry(max_retries=3, delay=1):
        """Decorator for retrying failed requests"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except (requests.RequestException, APIError) as e:
                        if attempt == max_retries - 1:
                            raise
                        logger.warning(f"Attempt {attempt + 1} failed, retrying...")
                        import time
                        time.sleep(delay)
                return None
            return wrapper
        return decorator
    
    @_retry(max_retries=3)
    def get_current_weather(self, latitude: float, longitude: float, 
                           units: str = 'metric', 
                           api_provider: str = 'auto') -> Dict:
        """Get current weather data
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            units: 'metric' or 'imperial'
            api_provider: 'openmeteo', 'openweather', 'weatherapi', or 'auto'
        
        Returns:
            Dictionary with weather data
        """
        if api_provider == 'auto':
            # Try Open-Meteo first (no API key needed)
            try:
                return self._get_current_openmeteo(latitude, longitude, units)
            except Exception as e:
                logger.warning(f"Open-Meteo failed: {e}, trying OpenWeather")
                if self.openweather_key:
                    try:
                        return self._get_current_openweather(latitude, longitude, units)
                    except Exception as e:
                        logger.warning(f"OpenWeather failed: {e}")
                raise APIError("All weather APIs failed")
        
        elif api_provider == 'openmeteo':
            return self._get_current_openmeteo(latitude, longitude, units)
        elif api_provider == 'openweather':
            return self._get_current_openweather(latitude, longitude, units)
        elif api_provider == 'weatherapi':
            return self._get_current_weatherapi(latitude, longitude, units)
        else:
            raise APIError(f"Unknown API provider: {api_provider}")
    
    def _get_current_openmeteo(self, lat: float, lon: float, units: str) -> Dict:
        """Get current weather from Open-Meteo"""
        url = f"{self.openmeteo_url}/forecast"
        params = {
            'latitude': lat,
            'longitude': lon,
            'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,wind_speed_10m,wind_direction_10m',
            'temperature_unit': 'fahrenheit' if units == 'imperial' else 'celsius',
            'wind_speed_unit': 'mph' if units == 'imperial' else 'kmh'
        }
        
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        
        current = data.get('current', {})
        
        return {
            'temp': current.get('temperature_2m'),
            'feels_like': current.get('apparent_temperature'),
            'description': self._weather_code_to_description(current.get('weather_code')),
            'humidity': current.get('relative_humidity_2m'),
            'wind_speed': current.get('wind_speed_10m'),
            'wind_direction': current.get('wind_direction_10m'),
            'precipitation': current.get('precipitation', 0),
            'rain': current.get('rain', 0),
            'api_source': 'open-meteo'
        }
    
    def _get_current_openweather(self, lat: float, lon: float, units: str) -> Dict:
        """Get current weather from OpenWeatherMap"""
        url = f"{self.openweather_url}/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'units': units,
            'appid': self.openweather_key
        }
        
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        
        return {
            'temp': data.get('main', {}).get('temp'),
            'feels_like': data.get('main', {}).get('feels_like'),
            'description': data.get('weather', [{}])[0].get('main'),
            'humidity': data.get('main', {}).get('humidity'),
            'pressure': data.get('main', {}).get('pressure'),
            'wind_speed': data.get('wind', {}).get('speed'),
            'wind_direction': data.get('wind', {}).get('deg'),
            'visibility': data.get('visibility'),
            'api_source': 'openweathermap'
        }
    
    def _get_current_weatherapi(self, lat: float, lon: float, units: str) -> Dict:
        """Get current weather from WeatherAPI"""
        url = f"{self.weatherapi_url}/current.json"
        params = {
            'q': f"{lat},{lon}",
            'aqi': 'yes',
            'key': self.weatherapi_key
        }
        
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        
        current = data.get('current', {})
        
        return {
            'temp': current.get('temp_c') if units == 'metric' else current.get('temp_f'),
            'feels_like': current.get('feelslike_c') if units == 'metric' else current.get('feelslike_f'),
            'description': current.get('condition', {}).get('text'),
            'humidity': current.get('humidity'),
            'wind_speed': current.get('wind_kph') if units == 'metric' else current.get('wind_mph'),
            'wind_direction': current.get('wind_degree'),
            'precipitation': current.get('precip_mm') if units == 'metric' else current.get('precip_in'),
            'visibility': current.get('vis_km') if units == 'metric' else current.get('vis_miles'),
            'api_source': 'weatherapi'
        }
    
    def get_forecast(self, latitude: float, longitude: float, 
                     days: int = 5, units: str = 'metric') -> List[Dict]:
        """Get weather forecast
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            days: Number of days (1-10)
            units: 'metric' or 'imperial'
        
        Returns:
            List of daily forecast dictionaries
        """
        url = f"{self.openmeteo_url}/forecast"
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code,wind_speed_10m_max',
            'forecast_days': min(days, 16),
            'temperature_unit': 'fahrenheit' if units == 'imperial' else 'celsius',
            'wind_speed_unit': 'mph' if units == 'imperial' else 'kmh'
        }
        
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        
        forecast = []
        daily = data.get('daily', {})
        
        times = daily.get('time', [])
        temps_max = daily.get('temperature_2m_max', [])
        temps_min = daily.get('temperature_2m_min', [])
        codes = daily.get('weather_code', [])
        precip = daily.get('precipitation_sum', [])
        
        for i, date in enumerate(times):
            forecast.append({
                'date': date,
                'temp_max': temps_max[i] if i < len(temps_max) else None,
                'temp_min': temps_min[i] if i < len(temps_min) else None,
                'description': self._weather_code_to_description(codes[i]) if i < len(codes) else 'N/A',
                'precipitation': precip[i] if i < len(precip) else 0
            })
        
        return forecast
    
    def get_hourly_forecast(self, latitude: float, longitude: float,
                           hours: int = 24, units: str = 'metric') -> List[Dict]:
        """Get hourly forecast"""
        url = f"{self.openmeteo_url}/forecast"
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'hourly': 'temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m',
            'temperature_unit': 'fahrenheit' if units == 'imperial' else 'celsius',
        }
        
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        
        hourly = []
        hourly_data = data.get('hourly', {})
        
        times = hourly_data.get('time', [])[:hours]
        temps = hourly_data.get('temperature_2m', [])[:hours]
        humidity = hourly_data.get('relative_humidity_2m', [])[:hours]
        precip = hourly_data.get('precipitation', [])[:hours]
        codes = hourly_data.get('weather_code', [])[:hours]
        
        for i, time in enumerate(times):
            hourly.append({
                'time': time,
                'temp': temps[i] if i < len(temps) else None,
                'humidity': humidity[i] if i < len(humidity) else None,
                'precipitation': precip[i] if i < len(precip) else 0,
                'description': self._weather_code_to_description(codes[i]) if i < len(codes) else 'N/A'
            })
        
        return hourly
    
    def search_locations(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for locations"""
        url = 'https://geocoding-api.open-meteo.com/v1/search'
        params = {
            'name': query,
            'count': limit,
            'language': 'en'
        }
        
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for result in data.get('results', []):
            results.append({
                'name': result.get('name'),
                'admin1': result.get('admin1'),
                'country': result.get('country'),
                'lat': result.get('latitude'),
                'lon': result.get('longitude')
            })
        
        return results
    
    def get_weather_alerts(self, latitude: float, longitude: float) -> List[Dict]:
        """Get weather alerts (uses NWS API for US locations)"""
        # This is a simplified version - implement based on available APIs
        return []
    
    def get_air_quality(self, latitude: float, longitude: float) -> Dict:
        """Get air quality data"""
        url = f"{self.openmeteo_url}/air-quality"
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'current': 'pm10,pm2_5,o3,no2',
        }
        
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            current = data.get('current', {})
            
            return {
                'pm10': current.get('pm10'),
                'pm2_5': current.get('pm2_5'),
                'o3': current.get('o3'),
                'no2': current.get('no2'),
                'aqi_category': self._calculate_aqi_category(current.get('pm2_5'))
            }
        except Exception as e:
            logger.warning(f"Failed to fetch air quality: {e}")
            return {}
    
    @staticmethod
    def _weather_code_to_description(code: int) -> str:
        """Convert WMO weather code to description"""
        codes = {
            0: 'Clear sky',
            1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast',
            45: 'Foggy', 48: 'Foggy',
            51: 'Light drizzle', 53: 'Moderate drizzle', 55: 'Dense drizzle',
            61: 'Slight rain', 63: 'Moderate rain', 65: 'Heavy rain',
            71: 'Slight snow', 73: 'Moderate snow', 75: 'Heavy snow',
            80: 'Slight rain showers', 81: 'Moderate rain showers', 82: 'Violent rain showers',
            85: 'Slight snow showers', 86: 'Heavy snow showers',
            95: 'Thunderstorm', 96: 'Thunderstorm with slight hail', 99: 'Thunderstorm with heavy hail'
        }
        return codes.get(code, 'Unknown')
    
    @staticmethod
    def _calculate_aqi_category(pm2_5: float) -> str:
        """Calculate air quality index category"""
        if pm2_5 <= 12:
            return 'Good'
        elif pm2_5 <= 35.4:
            return 'Moderate'
        elif pm2_5 <= 55.4:
            return 'Unhealthy for Sensitive Groups'
        elif pm2_5 <= 150.4:
            return 'Unhealthy'
        else:
            return 'Hazardous'
