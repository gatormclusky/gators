"""
Weather Dashboard Backend - Flask Application
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import logging
from logging_config import setup_logging

from weather_api import WeatherClient
from utils.cache import cache
from utils.validators import validate_coordinates, validate_units
from utils.error_handler import handle_error, APIError

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Enable CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize cache
cache.init_app(app)

# Setup logging
logger = setup_logging()

# Initialize weather client
weather_client = WeatherClient()


# Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'weather-dashboard',
        'version': '1.0.0'
    }), 200


@app.route('/api/weather/current', methods=['GET'])
@cache.cached(timeout=600, query_string=True)
def get_current_weather():
    """Get current weather for coordinates
    
    Query Parameters:
        lat: Latitude (required)
        lon: Longitude (required)
        units: 'metric' or 'imperial' (optional, default: metric)
        api: API provider to use (optional, auto-select by default)
    """
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        units = request.args.get('units', 'metric')
        api = request.args.get('api', 'auto')
        
        # Validate inputs
        if not validate_coordinates(lat, lon):
            raise APIError('Invalid latitude or longitude', 400)
        
        if not validate_units(units):
            raise APIError('Units must be "metric" or "imperial"', 400)
        
        logger.info(f"Fetching current weather: lat={lat}, lon={lon}, units={units}")
        
        # Fetch weather data
        weather = weather_client.get_current_weather(
            latitude=lat,
            longitude=lon,
            units=units,
            api_provider=api
        )
        
        return jsonify({
            'status': 'success',
            'data': weather
        }), 200
    
    except APIError as e:
        return handle_error(e)
    except Exception as e:
        logger.error(f"Error fetching current weather: {str(e)}")
        return handle_error(APIError('Internal server error', 500))


@app.route('/api/weather/forecast', methods=['GET'])
@cache.cached(timeout=600, query_string=True)
def get_forecast():
    """Get weather forecast for coordinates
    
    Query Parameters:
        lat: Latitude (required)
        lon: Longitude (required)
        days: Number of forecast days (default: 5, max: 10)
        units: 'metric' or 'imperial' (optional)
    """
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        days = request.args.get('days', 5, type=int)
        units = request.args.get('units', 'metric')
        
        if not validate_coordinates(lat, lon):
            raise APIError('Invalid coordinates', 400)
        
        if days < 1 or days > 10:
            raise APIError('Days must be between 1 and 10', 400)
        
        logger.info(f"Fetching forecast: lat={lat}, lon={lon}, days={days}")
        
        forecast = weather_client.get_forecast(
            latitude=lat,
            longitude=lon,
            days=days,
            units=units
        )
        
        return jsonify({
            'status': 'success',
            'forecast': forecast
        }), 200
    
    except APIError as e:
        return handle_error(e)
    except Exception as e:
        logger.error(f"Error fetching forecast: {str(e)}")
        return handle_error(APIError('Internal server error', 500))


@app.route('/api/weather/hourly', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_hourly_forecast():
    """Get hourly forecast
    
    Query Parameters:
        lat: Latitude (required)
        lon: Longitude (required)
        hours: Number of hours (default: 24, max: 168)
    """
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        hours = request.args.get('hours', 24, type=int)
        units = request.args.get('units', 'metric')
        
        if not validate_coordinates(lat, lon):
            raise APIError('Invalid coordinates', 400)
        
        if hours < 1 or hours > 168:
            raise APIError('Hours must be between 1 and 168', 400)
        
        hourly = weather_client.get_hourly_forecast(
            latitude=lat,
            longitude=lon,
            hours=hours,
            units=units
        )
        
        return jsonify({
            'status': 'success',
            'hourly': hourly
        }), 200
    
    except APIError as e:
        return handle_error(e)
    except Exception as e:
        logger.error(f"Error fetching hourly forecast: {str(e)}")
        return handle_error(APIError('Internal server error', 500))


@app.route('/api/weather/search', methods=['GET'])
@cache.cached(timeout=3600, query_string=True)
def search_locations():
    """Search locations by name
    
    Query Parameters:
        q: Search query (required)
        limit: Number of results (default: 5, max: 10)
    """
    try:
        query = request.args.get('q', '').strip()
        limit = request.args.get('limit', 5, type=int)
        
        if not query:
            raise APIError('Search query cannot be empty', 400)
        
        if len(query) < 2:
            raise APIError('Search query must be at least 2 characters', 400)
        
        limit = min(limit, 10)  # Cap at 10 results
        
        logger.info(f"Searching locations: q={query}, limit={limit}")
        
        results = weather_client.search_locations(query, limit)
        
        return jsonify({
            'status': 'success',
            'results': results
        }), 200
    
    except APIError as e:
        return handle_error(e)
    except Exception as e:
        logger.error(f"Error searching locations: {str(e)}")
        return handle_error(APIError('Internal server error', 500))


@app.route('/api/weather/alerts', methods=['GET'])
def get_weather_alerts():
    """Get weather alerts for coordinates
    
    Query Parameters:
        lat: Latitude (required)
        lon: Longitude (required)
    """
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        
        if not validate_coordinates(lat, lon):
            raise APIError('Invalid coordinates', 400)
        
        alerts = weather_client.get_weather_alerts(lat, lon)
        
        return jsonify({
            'status': 'success',
            'alerts': alerts
        }), 200
    
    except APIError as e:
        return handle_error(e)
    except Exception as e:
        logger.error(f"Error fetching alerts: {str(e)}")
        return handle_error(APIError('Internal server error', 500))


@app.route('/api/weather/air-quality', methods=['GET'])
@cache.cached(timeout=600, query_string=True)
def get_air_quality():
    """Get air quality data
    
    Query Parameters:
        lat: Latitude (required)
        lon: Longitude (required)
    """
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        
        if not validate_coordinates(lat, lon):
            raise APIError('Invalid coordinates', 400)
        
        air_quality = weather_client.get_air_quality(lat, lon)
        
        return jsonify({
            'status': 'success',
            'air_quality': air_quality
        }), 200
    
    except APIError as e:
        return handle_error(e)
    except Exception as e:
        logger.error(f"Error fetching air quality: {str(e)}")
        return handle_error(APIError('Internal server error', 500))


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
