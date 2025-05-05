import requests
import os

weather_api_key = os.getenv("WEATHER_API_KEY")
WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather(city: str) -> str:
    url = f"{WEATHER_BASE_URL}?q={city}&appid={weather_api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        temperature = data['main']['temp']
        condition = data['weather'][0]['main']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        
        weather_report = (
            f"🌍 Weather in {city.capitalize()}\n"
            f"🌡 Temperature: {temperature}°C\n"
            f"🌤 Condition: {condition}\n"
            f"💧 Humidity: {humidity}%\n"
            f"🌬 Wind Speed: {wind_speed} m/s"
        )

        return weather_report
    
    else:
        return "❌ Error: City not found or API request failed!"