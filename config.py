import os
from dotenv import load_dotenv
from openai import OpenAI

# --- Load environment variables ---
load_dotenv(override=True)

# --- API keys ---
openai_api_key = os.getenv("OPENAI_API_KEY")
weather_api_key = os.getenv("OPENWEATHER_API_KEY")

# --- Check keys ---
if openai_api_key:
    print(f"✅ OpenAI API Key found, begins with: {openai_api_key[:8]}")
else:
    print("❌ OpenAI API Key not set in .env")

if weather_api_key:
    print("✅ OpenWeather API Key found")
else:
    print("❌ OpenWeather API Key missing")

# --- OpenAI client ---
openai = OpenAI(api_key=openai_api_key)

# --- Models ---
CHAT_MODEL = "gpt-4o-mini"
IMAGE_MODEL = "dall-e-3"

# --- System message ---
system_message = (
    "You are WeatherVisionAI, a helpful assistant. "
    "When the user asks about the weather, you must always call get_weather. "
    "The get_weather tool will automatically also generate a city image. "
    "Never answer weather questions without calling get_weather."
)
