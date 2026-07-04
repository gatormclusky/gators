# Weather Dashboard

A comprehensive, real-time weather dashboard with support for multiple weather APIs, interactive visualizations, and responsive design.

## Features

- **Multi-API Support**
  - Open-Meteo (free, no API key required)
  - OpenWeatherMap (free tier with API key)
  - WeatherAPI (free tier with API key)
  - Fallback mechanisms for reliability

- **Weather Data**
  - Real-time current conditions
  - 5-day forecast
  - Hourly forecasts
  - Air quality data
  - UV index
  - Wind speed and direction
  - Humidity and pressure

- **Features**
  - Location search by city name or coordinates
  - Favorite locations management (localStorage)
  - Unit preferences (Celsius/Fahrenheit, km/h/mph)
  - Temperature charts and graphs
  - Weather alerts
  - Responsive design (mobile, tablet, desktop)
  - Dark/light theme
  - Auto-refresh capability

- **Accuracy**
  - High-precision weather data from reliable sources
  - Multiple data validation checks
  - Error handling and fallback options

## Technology Stack

### Backend
- **Python 3.9+** / **Node.js 16+**
- **Flask** / **Express.js**
- **Requests** / **Axios** for API calls
- **Environment variables** for API key management

### Frontend
- **React 18+** / **Vue.js 3+** / **Vanilla JavaScript**
- **TailwindCSS** / **Bootstrap 5** for styling
- **Chart.js** / **D3.js** for data visualization
- **Axios** for HTTP requests
- **Local Storage** for preferences

## Installation

### Backend Setup (Python Flask)

```bash
# Navigate to backend directory
cd weather-dashboard/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "OPENWEATHER_API_KEY=your_api_key_here" > .env
echo "WEATHERAPI_KEY=your_api_key_here" >> .env
echo "FLASK_ENV=development" >> .env

# Run development server
flask run
```

### Backend Setup (Node.js Express)

```bash
cd weather-dashboard/backend-node

# Install dependencies
npm install

# Create .env file
echo "OPENWEATHER_API_KEY=your_api_key" > .env
echo "WEATHERAPI_KEY=your_api_key" >> .env
echo "PORT=5000" >> .env

# Run development server
npm run dev
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd weather-dashboard/frontend

# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

## API Endpoints

### GET /api/weather/current
Fetch current weather for a location

**Query Parameters:**
- `lat` (required): Latitude
- `lon` (required): Longitude
- `units` (optional): 'metric' or 'imperial' (default: 'metric')
- `api` (optional): 'openmeteo', 'openweather', 'weatherapi' (default: auto-select)

**Response:**
```json
{
  "status": "success",
  "data": {
    "temp": 22.5,
    "feels_like": 21.0,
    "description": "Partly cloudy",
    "humidity": 65,
    "pressure": 1013,
    "wind_speed": 12,
    "wind_direction": 180,
    "uv_index": 6,
    "air_quality": "Good",
    "visibility": 10000,
    "precipitation": 0
  }
}
```

### GET /api/weather/forecast
Fetch 5-day forecast

**Query Parameters:**
- `lat` (required): Latitude
- `lon` (required): Longitude
- `units` (optional): 'metric' or 'imperial'

**Response:**
```json
{
  "status": "success",
  "forecast": [
    {
      "date": "2024-01-15",
      "temp_max": 25,
      "temp_min": 18,
      "description": "Sunny",
      "precipitation": 0,
      "humidity": 60
    }
  ]
}
```

### GET /api/weather/search
Search location by name

**Query Parameters:**
- `q` (required): City name or location
- `limit` (optional): Number of results (default: 5)

**Response:**
```json
{
  "status": "success",
  "results": [
    {
      "name": "London",
      "country": "United Kingdom",
      "lat": 51.5085,
      "lon": -0.1257
    }
  ]
}
```

### GET /api/weather/alerts
Fetch weather alerts for a location

**Query Parameters:**
- `lat` (required): Latitude
- `lon` (required): Longitude

### POST /api/weather/favorites
Manage favorite locations

**Request Body:**
```json
{
  "action": "add",
  "location": {
    "name": "London",
    "lat": 51.5085,
    "lon": -0.1257
  }
}
```

## Configuration

### Environment Variables (.env)

```bash
# Weather API Keys (get free keys from their websites)
OPENWEATHER_API_KEY=your_openweather_api_key
WEATHERAI_KEY=your_weatherapi_key

# Server Configuration
FLASK_ENV=development
PORT=5000
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Optional Settings
DEFAULT_UNITS=metric
DEFAULT_LOCATION=London,UK
CACHE_TTL=600
```

### API Key Setup

1. **Open-Meteo**: No API key needed! Free for non-commercial use.
2. **OpenWeatherMap**: Get free tier at https://openweathermap.org/api
3. **WeatherAPI**: Free tier at https://www.weatherapi.com/

## Usage

### Basic Example (Frontend)

```javascript
// Fetch current weather
const response = await fetch('/api/weather/current?lat=51.5085&lon=-0.1257&units=metric');
const data = await response.json();
console.log(`Temperature: ${data.data.temp}°C`);

// Fetch forecast
const forecast = await fetch('/api/weather/forecast?lat=51.5085&lon=-0.1257');
const forecastData = await forecast.json();
```

### Backend Usage (Python)

```python
from weather_api import WeatherClient

client = WeatherClient()

# Get current weather
weather = client.get_current_weather(51.5085, -0.1257)
print(f"Temperature: {weather['temp']}°C")

# Get forecast
forecast = client.get_forecast(51.5085, -0.1257)
for day in forecast:
    print(f"{day['date']}: {day['temp_max']}°C")
```

## File Structure

```
weather-dashboard/
├── README.md
├── backend/                    # Python Flask backend
│   ├── app.py
│   ├── weather_api.py         # Weather API client
│   ├── routes/
│   │   ├── weather.py
│   │   └── locations.py
│   ├── utils/
│   │   ├── cache.py
│   │   ├── validators.py
│   │   └── error_handler.py
│   ├── requirements.txt
│   └── .env.example
│
├── backend-node/              # Node.js Express backend (alternative)
│   ├── server.js
│   ├── weather-client.js
│   ├── routes/
│   ├── package.json
│   └── .env.example
│
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── CurrentWeather.jsx
│   │   │   ├── Forecast.jsx
│   │   │   ├── SearchBar.jsx
│   │   │   ├── Favorites.jsx
│   │   │   └── ThemeToggle.jsx
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   └── Settings.jsx
│   │   ├── hooks/
│   │   │   ├── useWeather.js
│   │   │   └── useLocalStorage.js
│   │   ├── styles/
│   │   │   └── App.css
│   │   ├── App.jsx
│   │   └── index.jsx
│   ├── public/
│   ├── package.json
│   └── .env.example
│
├── docker-compose.yml         # Docker setup
└── .gitignore
```

## Deployment

### Docker

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access at http://localhost:3000
```

### Heroku

```bash
# Deploy backend
cd backend
git push heroku main

# Deploy frontend
cd ../frontend
npm run build
git push heroku main
```

### AWS/GCP/Azure

See deployment guides in `/docs/deployment/`

## Testing

### Backend Tests

```bash
cd backend
pip install pytest pytest-cov
pytest tests/ -v --cov=.
```

### Frontend Tests

```bash
cd frontend
npm test
npm run test:coverage
```

## Performance

- **Response Time**: < 500ms for current weather
- **Forecast Load**: < 1s for 5-day forecast
- **Caching**: 10-minute TTL for weather data
- **API Calls**: Optimized to minimize external API usage

## Error Handling

The dashboard includes comprehensive error handling:
- Invalid location fallback
- API downtime graceful degradation
- Network error recovery
- User-friendly error messages

## Contributing

Contributions welcome! Please see CONTRIBUTING.md

## License

MIT License

## Support

For issues and questions, open an issue on GitHub or contact support.
