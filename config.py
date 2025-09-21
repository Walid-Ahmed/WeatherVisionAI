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

# --- Default models ---
CHAT_MODEL = "gpt-4o-mini"
IMAGE_MODEL = "dall-e-3"

# --- System prompt ---
system_message = (
    "You are UtilityAI, a helpful personal assistant. "
    "You can provide current weather, generate images of cities with weather, "
    "convert currencies, fetch Wikipedia summaries, and give the latest AI news. "
    "When the user asks only for weather, call get_weather. "
    "When the user also asks for a picture, call both get_weather and artist. "
    "Keep responses short, polite, and accurate. "
    "If you cannot find an answer, say so."
)
