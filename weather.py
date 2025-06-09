import requests
import os
import streamlit as st

weather_api_key = os.getenv("WEATHER_API_KEY")
WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather(city: str) -> str:
    url = f"{WEATHER_BASE_URL}?q={city}&appid={weather_api_key}&units=metric"
    response = requests.get(url)

    weather_report = {}

    if response.status_code == 200:
        data = response.json()
        weather_report['temp'] = data['main']['temp']
        weather_report['condition'] = data['weather'][0]['main']
        weather_report['humidity'] = data['main']['humidity']
        weather_report['wind_speed'] = data['wind']['speed']
        
        return weather_report
    
    else:
        return "❌ Error: City not found or API request failed!"