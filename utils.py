def get_weather_icon(icon_code):
    """
    Maps OpenWeather icon codes to emoji icons.
    
    Args:
        icon_code (str): OpenWeather icon code
        
    Returns:
        str: Emoji icon representing the weather condition
    """
    icon_map = {
        # Clear
        '01d': '☀️',  # clear sky day
        '01n': '🌙',  # clear sky night
        
        # Few clouds
        '02d': '🌤️',  # few clouds day
        '02n': '☁️',  # few clouds night
        
        # Scattered clouds
        '03d': '⛅',  # scattered clouds day
        '03n': '☁️',  # scattered clouds night
        
        # Broken clouds
        '04d': '☁️',  # broken clouds day
        '04n': '☁️',  # broken clouds night
        
        # Shower rain
        '09d': '🌧️',  # shower rain day
        '09n': '🌧️',  # shower rain night
        
        # Rain
        '10d': '🌦️',  # rain day
        '10n': '🌧️',  # rain night
        
        # Thunderstorm
        '11d': '⛈️',  # thunderstorm day
        '11n': '⛈️',  # thunderstorm night
        
        # Snow
        '13d': '❄️',  # snow day
        '13n': '❄️',  # snow night
        
        # Mist
        '50d': '🌫️',  # mist day
        '50n': '🌫️',  # mist night
    }
    
    return icon_map.get(icon_code, '❓')

def temperature_color(temp, unit='metric'):
    """
    Returns a color based on the temperature.
    
    Args:
        temp (float): The temperature value
        unit (str): The unit of the temperature ('metric' for Celsius, 'imperial' for Fahrenheit)
        
    Returns:
        str: Hex color code
    """
    # Convert to Celsius if in Fahrenheit for consistent color mapping
    if unit == 'imperial':
        temp = (temp - 32) * 5/9
    
    if temp < -10:
        return "#0022FF"  # Very cold - deep blue
    elif temp < 0:
        return "#0066FF"  # Cold - blue
    elif temp < 10:
        return "#00AAFF"  # Cool - light blue
    elif temp < 20:
        return "#00CCAA"  # Mild - teal
    elif temp < 25:
        return "#00CC00"  # Warm - green
    elif temp < 30:
        return "#DDCC00"  # Hot - yellow
    elif temp < 35:
        return "#FF8800"  # Very hot - orange
    else:
        return "#FF0000"  # Extremely hot - red

def wind_direction_icon(degrees):
    """
    Returns an arrow icon pointing in the direction of the wind.
    
    Args:
        degrees (int): Wind direction in degrees (meteorological)
        
    Returns:
        str: Arrow icon representing wind direction
    """
    # Normalize the degrees to ensure it falls within 0-360
    degrees = degrees % 360
    
    if degrees >= 337.5 or degrees < 22.5:
        return "⬇️"  # North wind (comes from north, blows southward)
    elif 22.5 <= degrees < 67.5:
        return "↙️"  # Northeast wind
    elif 67.5 <= degrees < 112.5:
        return "⬅️"  # East wind
    elif 112.5 <= degrees < 157.5:
        return "↖️"  # Southeast wind
    elif 157.5 <= degrees < 202.5:
        return "⬆️"  # South wind
    elif 202.5 <= degrees < 247.5:
        return "↗️"  # Southwest wind
    elif 247.5 <= degrees < 292.5:
        return "➡️"  # West wind
    else:  # 292.5 <= degrees < 337.5
        return "↘️"  # Northwest wind
