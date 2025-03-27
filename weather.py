import requests
import os
import streamlit as st
import time

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
        
        # Display API key status
        st.sidebar.expander("API Key Status").write(f"""
        API Key: {'*' * (len(self.api_key) - 4) + self.api_key[-4:] if self.api_key else 'Not provided'}
        
        **Note:** New OpenWeather API keys may take up to 2 hours to activate after creation.
        """)
        
        # Add a test API endpoint button
        if st.sidebar.button("Test API Key"):
            self.test_api_key()
    
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
        
        response = None
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()  # Raise an exception for 4XX/5XX responses
            
            return response.json()
        
        except requests.exceptions.HTTPError as http_err:
            if response and response.status_code == 404:
                raise Exception(f"City '{city}' not found. Please check the spelling and try again.")
            elif response and response.status_code == 401:
                # Try to get more detailed error message
                try:
                    error_data = response.json()
                    error_message = error_data.get('message', 'Invalid API key')
                    raise Exception(f"API key error: {error_message}. New API keys can take up to 2 hours to activate.")
                except:
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
        
        response = None
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            
            return response.json()
        
        except requests.exceptions.HTTPError as http_err:
            if response and response.status_code == 404:
                raise Exception(f"City '{city}' not found. Please check the spelling and try again.")
            elif response and response.status_code == 401:
                # Try to get more detailed error message
                try:
                    error_data = response.json()
                    error_message = error_data.get('message', 'Invalid API key')
                    raise Exception(f"API key error: {error_message}. New API keys can take up to 2 hours to activate.")
                except:
                    raise Exception("Invalid API key. Please check your OpenWeather API key.")
            else:
                raise Exception(f"HTTP error occurred: {http_err}")
        
        except requests.exceptions.ConnectionError:
            raise Exception("Network error. Please check your internet connection.")
        
        except requests.exceptions.Timeout:
            raise Exception("Request timed out. Please try again later.")
        
        except requests.exceptions.RequestException as err:
            raise Exception(f"An error occurred: {err}")
            
    def test_api_key(self):
        """
        Test the API key by making a simple request and showing the result
        """
        # Create a spinner while testing
        with st.sidebar.status("Testing API key..."):
            # Test URL for a simple request
            test_url = f"{self.base_url}/weather?q=London&appid={self.api_key}"
            
            response = None
            try:
                # Make the request
                response = requests.get(test_url)
                
                # Check if successful
                if response.status_code == 200:
                    st.sidebar.success("✅ API key is valid and active!")
                    return True
                elif response.status_code == 401:
                    error_data = response.json()
                    st.sidebar.error(f"❌ API key error: {error_data.get('message', 'Invalid API key')}")
                    
                    # Provide more detailed information
                    st.sidebar.info("""
                    **Common reasons for API key issues:**
                    1. **New API key:** OpenWeather typically takes up to 2 hours to activate new API keys
                    2. **Typo in key:** Double-check that the key was copied correctly
                    3. **Free account limits:** Make sure you're not exceeding the limits of the free tier
                    
                    You can verify your API key status on the [OpenWeather website](https://home.openweathermap.org/api_keys).
                    """)
                    return False
                else:
                    st.sidebar.warning(f"⚠️ Unexpected response (Code {response.status_code})")
                    return False
                    
            except Exception as e:
                st.sidebar.error(f"❌ Error testing API: {str(e)}")
                return False
