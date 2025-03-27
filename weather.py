import requests
import os
import streamlit as st

class WeatherAPI:
    """
    A class to handle interactions with the OpenWeather API.
    """
    
    def __init__(self):
        """
        Initialize the WeatherAPI with the API key from environment variables.
        """
        # Get API key from environment variables with a default fallback for development
        self.api_key = os.getenv("OPENWEATHER_API_KEY", "")
        if not self.api_key:
            raise ValueError("OpenWeather API key not found. Please set the OPENWEATHER_API_KEY environment variable.")
        
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self, city, units='metric'):
        """
        Get current weather data for a specified city.
        
        Args:
            city (str): City name to get weather data for
            units (str): Unit system - 'metric' (Celsius) or 'imperial' (Fahrenheit)
            
        Returns:
            dict: Current weather data
            
        Raises:
            Exception: If the API request fails
        """
        endpoint = f"{self.base_url}/weather"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': units
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()  # Raise an exception for 4XX/5XX responses
            
            return response.json()
        
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 404:
                raise Exception(f"City '{city}' not found. Please check the spelling and try again.")
            elif response.status_code == 401:
                raise Exception("Invalid API key. Please check your OpenWeather API key.")
            else:
                raise Exception(f"HTTP error occurred: {http_err}")
        
        except requests.exceptions.ConnectionError:
            raise Exception("Network error. Please check your internet connection.")
        
        except requests.exceptions.Timeout:
            raise Exception("Request timed out. Please try again later.")
        
        except requests.exceptions.RequestException as err:
            raise Exception(f"An error occurred: {err}")
    
    def get_forecast(self, city, units='metric'):
        """
        Get 5-day weather forecast data for a specified city.
        
        Args:
            city (str): City name to get forecast data for
            units (str): Unit system - 'metric' (Celsius) or 'imperial' (Fahrenheit)
            
        Returns:
            dict: Forecast weather data
            
        Raises:
            Exception: If the API request fails
        """
        endpoint = f"{self.base_url}/forecast"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': units
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            
            return response.json()
        
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 404:
                raise Exception(f"City '{city}' not found. Please check the spelling and try again.")
            elif response.status_code == 401:
                raise Exception("Invalid API key. Please check your OpenWeather API key.")
            else:
                raise Exception(f"HTTP error occurred: {http_err}")
        
        except requests.exceptions.ConnectionError:
            raise Exception("Network error. Please check your internet connection.")
        
        except requests.exceptions.Timeout:
            raise Exception("Request timed out. Please try again later.")
        
        except requests.exceptions.RequestException as err:
            raise Exception(f"An error occurred: {err}")
