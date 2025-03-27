import streamlit as st
import datetime
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import pandas as pd
import random
import os

from weather import WeatherAPI
from utils import get_weather_icon, temperature_color, wind_direction_icon

# Page configuration
st.set_page_config(
    page_title="Weather Dashboard",
    page_icon="🌤️",
    layout="wide",
)

# Initialize session state variables
if 'unit' not in st.session_state:
    st.session_state.unit = 'metric'  # Default to Celsius
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.datetime.now()
if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = False

# Function to load demo data
def get_demo_weather(city="London", units="metric"):
    """
    Generate sample weather data for demonstration purposes when API key is not working
    """
    # Sample data structure for current weather
    temp_base = 18.5 if units == "metric" else 65.3
    temp_variation = random.uniform(-3, 3)
    
    sample_current = {
        "coord": {"lon": -0.1257, "lat": 51.5085},
        "weather": [{"id": 801, "main": "Clouds", "description": "few clouds", "icon": "02d"}],
        "base": "stations",
        "main": {
            "temp": temp_base + temp_variation,
            "feels_like": temp_base + temp_variation - 0.6,
            "temp_min": temp_base + temp_variation - 2,
            "temp_max": temp_base + temp_variation + 2,
            "pressure": 1015,
            "humidity": 68
        },
        "visibility": 10000,
        "wind": {"speed": 4.12 if units == "metric" else 9.22, "deg": 240, "gust": 8.49},
        "clouds": {"all": 20},
        "dt": int(datetime.datetime.now().timestamp()),
        "sys": {
            "type": 2,
            "id": 2075535,
            "country": "GB",
            "sunrise": int((datetime.datetime.now().replace(hour=5, minute=30)).timestamp()),
            "sunset": int((datetime.datetime.now().replace(hour=20, minute=30)).timestamp())
        },
        "timezone": 3600,
        "id": 2643743,
        "name": city,
        "cod": 200
    }
    
    return sample_current

def get_demo_forecast(city="London", units="metric"):
    """
    Generate sample forecast data for demonstration purposes
    """
    # Sample forecast data structure
    sample_forecast = {
        "cod": "200",
        "message": 0,
        "cnt": 40,
        "list": [],
        "city": {
            "id": 2643743,
            "name": city,
            "coord": {"lat": 51.5085, "lon": -0.1257},
            "country": "GB",
            "population": 1000000,
            "timezone": 3600,
            "sunrise": int((datetime.datetime.now().replace(hour=5, minute=30)).timestamp()),
            "sunset": int((datetime.datetime.now().replace(hour=20, minute=30)).timestamp())
        }
    }
    
    # Generate forecast data for next 5 days (40 entries, every 3 hours)
    base_temp = 18.5 if units == "metric" else 65.3
    current_time = datetime.datetime.now()
    
    for i in range(40):
        forecast_time = current_time + datetime.timedelta(hours=i*3)
        hour_of_day = forecast_time.hour
        
        # Temperature varies by time of day
        temp_offset = -2 if hour_of_day < 6 else (3 if 10 <= hour_of_day <= 16 else 0)
        temp = base_temp + temp_offset
        
        # Add some random variation
        temp_variation = random.uniform(-1.5, 1.5)
        temp += temp_variation
        
        # Icon varies by time of day
        if hour_of_day >= 20 or hour_of_day < 6:
            icon = "01n"  # night
        else:
            icons = ["01d", "02d", "03d", "04d"]
            icon = icons[random.randint(0, len(icons)-1)]
            
        entry = {
            "dt": int(forecast_time.timestamp()),
            "main": {
                "temp": temp,
                "feels_like": temp - 0.6,
                "temp_min": temp - 1.7,
                "temp_max": temp + 1.2,
                "pressure": 1015 + random.randint(-3, 3),
                "humidity": 68 + random.randint(-10, 10),
            },
            "weather": [
                {
                    "id": 800,
                    "main": "Clear" if "01" in icon else "Clouds",
                    "description": "clear sky" if "01" in icon else "few clouds",
                    "icon": icon
                }
            ],
            "clouds": {"all": 0 if "01" in icon else 20 + random.randint(0, 80)},
            "wind": {
                "speed": 4.12 + random.uniform(-2, 2),
                "deg": random.randint(0, 360)
            },
            "visibility": 10000,
            "pop": random.uniform(0, 1) if random.random() > 0.7 else 0,
            "sys": {"pod": "n" if hour_of_day >= 20 or hour_of_day < 6 else "d"},
            "dt_txt": forecast_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        sample_forecast["list"].append(entry)
    
    return sample_forecast

# Try to initialize WeatherAPI with OpenWeather API key from environment
try:
    weather_api = WeatherAPI()
    api_initialized = True
except Exception as e:
    st.error(f"Error initializing Weather API: {str(e)}")
    api_initialized = False
    st.session_state.demo_mode = True  # Automatically enable demo mode if API initialization fails

# Header
st.title("🌤️ Weather Dashboard")

# Show message if in demo mode
if st.session_state.demo_mode:
    st.markdown("""
    <div style="background-color:#F0F2F6;padding:15px;border-radius:10px;margin-bottom:15px;">
        <h3 style="margin-top:0;color:#FF4B4B;">⚠️ Demo Mode Active</h3>
        <p>This dashboard is currently displaying <b>simulated weather data</b> because:</p>
        <ul>
            <li>Your OpenWeather API key may still be in the activation process (can take up to 2 hours)</li>
            <li>Or demo mode was manually enabled for testing</li>
        </ul>
        <p>To use real weather data, please ensure your API key is active and disable demo mode in the sidebar.</p>
    </div>
    """, unsafe_allow_html=True)
    
# Removed free API plan information block

# Sidebar for controls
with st.sidebar:
    st.header("Location Settings")
    
    # Search by city name
    city_name = st.text_input("Enter City Name", "London")
    search_button = st.button("Search")
    
    # Units selection
    unit_option = st.radio(
        "Temperature Unit",
        options=["Celsius (°C)", "Fahrenheit (°F)"],
        index=0 if st.session_state.unit == 'metric' else 1
    )
    
    # Update unit in session state
    if (unit_option == "Celsius (°C)" and st.session_state.unit != 'metric') or \
       (unit_option == "Fahrenheit (°F)" and st.session_state.unit != 'imperial'):
        st.session_state.unit = 'metric' if unit_option == "Celsius (°C)" else 'imperial'
        search_button = True  # Force refresh with new unit

    # Show last update time
    st.write(f"Last updated: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Demo mode option - only show if API is not initialized
    if not api_initialized:
        st.warning("⚠️ **API Key Not Active**")
        st.markdown("""
        Your OpenWeather API key may not be active yet. New API keys can take up to 2 hours to activate.
        
        The dashboard is running in demo mode with simulated data.
        """)
        demo_enabled = True
    else:
        # API is working properly, disable demo mode
        demo_enabled = False
        
        if st.session_state.demo_mode != demo_enabled:
            st.session_state.demo_mode = demo_enabled
    
    # Removed information about API key activation

# Main content
if search_button or 'weather_data' not in st.session_state:
    with st.spinner("Fetching weather data..."):
        try:
            # Check if in demo mode or API failed
            if st.session_state.demo_mode or not api_initialized:
                # Show notification that we're using demo data
                if not st.session_state.get('demo_notification_shown', False):
                    st.info("🧪 Using demo data - weather information is simulated")
                    st.session_state.demo_notification_shown = True
                
                # Get simulated weather data
                current_weather = get_demo_weather(city_name, st.session_state.unit)
                forecast = get_demo_forecast(city_name, st.session_state.unit)
            else:
                # Get real weather data from API
                current_weather = weather_api.get_current_weather(city_name, st.session_state.unit)
                forecast = weather_api.get_forecast(city_name, st.session_state.unit)
            
            # Store in session state
            st.session_state.weather_data = current_weather
            st.session_state.forecast_data = forecast
            st.session_state.last_update = datetime.datetime.now()
            
        except Exception as e:
            st.error(f"Error fetching weather data: {str(e)}")
            
            # If API is failing but we're not in demo mode yet, switch to demo mode
            if not st.session_state.demo_mode and 'Invalid API key' in str(e):
                st.warning("Switching to demo mode due to API key issues")
                st.session_state.demo_mode = True
                
                # Get simulated weather data as a fallback
                current_weather = get_demo_weather(city_name, st.session_state.unit)
                forecast = get_demo_forecast(city_name, st.session_state.unit)
                
                # Store in session state
                st.session_state.weather_data = current_weather
                st.session_state.forecast_data = forecast
                st.session_state.last_update = datetime.datetime.now()
                
                # Show info about demo mode
                st.info("🧪 Using demo data - weather information is simulated")
                st.session_state.demo_notification_shown = True
            elif 'weather_data' not in st.session_state:
                st.stop()

# Display current weather
try:
    weather_data = st.session_state.weather_data
    forecast_data = st.session_state.forecast_data
    
    # Location information
    st.header(f"Current Weather in {weather_data['name']}, {weather_data['sys']['country']}")
    
    # Create columns for layout
    col1, col2, col3 = st.columns([1, 1, 1])
    
    # Column 1: Basic weather info and icon
    with col1:
        weather_condition = weather_data['weather'][0]['description'].capitalize()
        
        # Weather icon display
        weather_icon = get_weather_icon(weather_data['weather'][0]['icon'])
        st.markdown(f'<div style="text-align: center; font-size: 100px;">{weather_icon}</div>', unsafe_allow_html=True)
        
        st.markdown(f"<h2 style='text-align: center;'>{weather_condition}</h2>", unsafe_allow_html=True)
        
        # Display temperature with color
        temp = weather_data['main']['temp']
        temp_unit = "°C" if st.session_state.unit == 'metric' else "°F"
        temp_color = temperature_color(temp, st.session_state.unit)
        st.markdown(f"<h1 style='text-align: center; color: {temp_color};'>{temp:.1f}{temp_unit}</h1>", unsafe_allow_html=True)
        
        # Feels like temperature
        feels_like = weather_data['main']['feels_like']
        st.markdown(f"<p style='text-align: center;'>Feels like: {feels_like:.1f}{temp_unit}</p>", unsafe_allow_html=True)
    
    # Column 2: Additional weather metrics
    with col2:
        st.subheader("Details")
        
        # Min/Max temperature
        min_temp = weather_data['main']['temp_min']
        max_temp = weather_data['main']['temp_max']
        st.write(f"Min/Max: {min_temp:.1f}{temp_unit} / {max_temp:.1f}{temp_unit}")
        
        # Humidity
        humidity = weather_data['main']['humidity']
        st.write(f"Humidity: {humidity}%")
        
        # Pressure
        pressure = weather_data['main']['pressure']
        st.write(f"Pressure: {pressure} hPa")
        
        # Visibility
        visibility = weather_data.get('visibility', 0) / 1000  # Convert to km
        st.write(f"Visibility: {visibility:.1f} km")
        
        # Cloudiness
        clouds = weather_data['clouds']['all']
        st.write(f"Cloudiness: {clouds}%")

    # Column 3: Wind information with visual indicator
    with col3:
        st.subheader("Wind")
        
        # Wind speed
        wind_speed = weather_data['wind']['speed']
        speed_unit = "m/s" if st.session_state.unit == 'metric' else "mph"
        st.write(f"Speed: {wind_speed} {speed_unit}")
        
        # Wind direction
        wind_deg = weather_data.get('wind', {}).get('deg', 0)
        direction_icon = wind_direction_icon(wind_deg)
        st.markdown(f"<p>Direction: {wind_deg}° {direction_icon}</p>", unsafe_allow_html=True)
        
        # Wind gust if available
        if 'gust' in weather_data.get('wind', {}):
            wind_gust = weather_data['wind']['gust']
            st.write(f"Gust: {wind_gust} {speed_unit}")
        
        # Sunrise/Sunset times
        timezone_offset = weather_data['timezone']
        sunrise_time = datetime.datetime.fromtimestamp(weather_data['sys']['sunrise'] + timezone_offset - 3600)
        sunset_time = datetime.datetime.fromtimestamp(weather_data['sys']['sunset'] + timezone_offset - 3600)
        
        st.write(f"Sunrise: {sunrise_time.strftime('%H:%M')}")
        st.write(f"Sunset: {sunset_time.strftime('%H:%M')}")

    # Forecast section
    st.header("5-Day Forecast")
    
    # Process forecast data for plotting
    forecast_dates = []
    forecast_temps = []
    forecast_weather_icons = []
    forecast_weather_desc = []
    
    # Get daily forecasts (taking the noon forecast for each day)
    daily_forecasts = {}
    
    for forecast_item in forecast_data['list']:
        forecast_dt = datetime.datetime.fromtimestamp(forecast_item['dt'])
        forecast_date = forecast_dt.date()
        
        # Use noon forecast for each day
        if forecast_date not in daily_forecasts or (12 <= forecast_dt.hour <= 15):
            daily_forecasts[forecast_date] = forecast_item
    
    # Sort by date
    sorted_dates = sorted(daily_forecasts.keys())
    
    # Create forecast cards using columns
    forecast_cols = st.columns(len(sorted_dates))
    
    for i, date in enumerate(sorted_dates):
        forecast_item = daily_forecasts[date]
        
        with forecast_cols[i]:
            # Date
            st.write(f"**{date.strftime('%a, %b %d')}**")
            
            # Weather icon
            icon_code = forecast_item['weather'][0]['icon']
            weather_icon = get_weather_icon(icon_code)
            st.markdown(f'<div style="text-align: center; font-size: 40px;">{weather_icon}</div>', unsafe_allow_html=True)
            
            # Weather description
            weather_desc = forecast_item['weather'][0]['description'].capitalize()
            st.write(f"{weather_desc}")
            
            # Temperature
            temp = forecast_item['main']['temp']
            st.write(f"**{temp:.1f}{temp_unit}**")
            
            # Additional info
            st.write(f"Humidity: {forecast_item['main']['humidity']}%")
            wind_speed = forecast_item['wind']['speed']
            st.write(f"Wind: {wind_speed} {speed_unit}")

    # Temperature trend chart
    st.subheader("Temperature Trend (48 hours)")
    
    # Prepare data for the chart
    chart_data = []
    
    for i, forecast_item in enumerate(forecast_data['list'][:16]):  # Show first 48 hours (16 entries)
        forecast_dt = datetime.datetime.fromtimestamp(forecast_item['dt'])
        temp = forecast_item['main']['temp']
        feels_like = forecast_item['main']['feels_like']
        
        chart_data.append({
            'Time': forecast_dt, 
            'Temperature': temp,
            'Feels Like': feels_like
        })
    
    df = pd.DataFrame(chart_data)
    
    # Create interactive temperature chart
    fig = px.line(df, x='Time', y=['Temperature', 'Feels Like'], 
                  labels={'value': f'Temperature ({temp_unit})', 'variable': 'Metric'},
                  template='plotly_white')
    
    fig.update_layout(
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=10, r=10, t=30, b=10)
    )
    
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error displaying weather data: {str(e)}")
