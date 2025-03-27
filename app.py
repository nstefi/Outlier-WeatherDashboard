import streamlit as st
import datetime
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import pandas as pd

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

# Initialize WeatherAPI with OpenWeather API key from environment
weather_api = WeatherAPI()

# Header
st.title("🌤️ Weather Dashboard")

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

# Main content
if search_button or 'weather_data' not in st.session_state:
    with st.spinner("Fetching weather data..."):
        try:
            # Get current weather
            current_weather = weather_api.get_current_weather(city_name, st.session_state.unit)
            
            # Get forecast
            forecast = weather_api.get_forecast(city_name, st.session_state.unit)
            
            # Store in session state
            st.session_state.weather_data = current_weather
            st.session_state.forecast_data = forecast
            st.session_state.last_update = datetime.datetime.now()
            
        except Exception as e:
            st.error(f"Error fetching weather data: {str(e)}")
            if 'weather_data' not in st.session_state:
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
