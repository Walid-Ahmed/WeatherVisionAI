import os
import json
import requests
from datetime import datetime
from config import openai, IMAGE_MODEL, weather_api_key
from PIL import Image
from io import BytesIO


# --- artist ---
# Generates a weather-accurate pop-art city image using DALL-E.
# Called by handle_tool_call when the model decides an image is needed.
# The weather string (e.g. "Scattered clouds with 15.98°C") is injected into
# the prompt so sky colour, lighting, and atmosphere match real conditions.
def artist(city, weather="clear sky"):
    print(f"🎨 artist called for {city} with weather: {weather}")
    try:
        image_response = openai.images.generate(
            model=IMAGE_MODEL,
            prompt=(
                f"A vibrant pop-art style image of {city}. "
                f"Current weather: {weather}. "
                f"The scene must visually reflect these exact conditions: "
                f"sky colour, lighting, clothing on people, and atmosphere should all match the weather. "
                f"Show recognisable landmarks of {city}."
            ),
            size="1024x1024",
            n=1
        )

        image_url = image_response.data[0].url

        # Download and save the image locally
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))

        os.makedirs("images", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{city.lower().replace(',','').replace(' ','')}_{timestamp}.png"
        filepath = os.path.join("images", filename)
        img.save(filepath)

        print(f"✅ Image saved as {filepath}")

        try:
            img.show()
            print("👀 Image opened in default viewer.")
        except Exception as e:
            print(f"⚠️ Could not auto-open image: {e}")

        return filepath

    except Exception as e:
        print(f"❌ Image generation failed: {e}")
        return None


# --- get_weather ---
# Fetches live weather from OpenWeatherMap and returns a short description string
# e.g. "Scattered clouds with 15.98°C".
# This string is returned to the model as a tool result and can be passed to
# artist as-is so the image prompt reflects real conditions.
def get_weather(destination_city: str):
    print(f"🔧 get_weather called for {destination_city}")

    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": destination_city, "appid": weather_api_key, "units": "metric"}

    try:
        response = requests.get(url, params=params)
        print(f"🌍 Weather API status: {response.status_code}")
        print(f"🌍 Weather API raw: {response.text[:200]}")

        if response.status_code == 200:
            data = response.json()
            desc = data["weather"][0]["description"].capitalize()
            temp = data["main"]["temp"]
            # Format: "<Description> with <temp>°C" — reused verbatim in the artist prompt
            weather_text = f"{desc} with {temp}°C"
            return weather_text
        else:
            return f"Weather data not available for {destination_city}"
    except Exception as e:
        return f"Error fetching weather: {e}"


# --- Tool schemas ---
# These descriptions are the only guidance the model receives.
# No system message is used — the model decides when and how to call tools
# based solely on these descriptions.

weather_function = {
    "name": "get_weather",
    "description": "Get the current real-time weather for a city.",
    "parameters": {
        "type": "object",
        "properties": {
            "destination_city": {"type": "string"},
        },
        "required": ["destination_city"],
    },
}

artist_function = {
    "name": "artist",
    # Explicit instruction to only call when the user asks for an image,
    # preventing the model from always generating one after get_weather.
    "description": "Generate a pop-art style image of a city reflecting its current weather. Only call this when the user explicitly asks for an image.",
    "parameters": {
        "type": "object",
        "properties": {
            "city":    {"type": "string", "description": "City name"},
            "weather": {"type": "string", "description": "Weather description returned by get_weather. Defaults to 'clear sky' if not available."},
        },
        "required": ["city"],
    },
}

# Both tools are passed to the model on every API call
tools = [
    {"type": "function", "function": weather_function},
    {"type": "function", "function": artist_function},
]


# --- Tool handler ---
# Executes whichever tool the model chose and returns a "tool" role message
# containing the result, which is appended to the conversation so the model
# can continue reasoning in the next loop iteration.
# Only message.tool_calls[0] is processed — one call per loop turn.
def handle_tool_call(message):
    tool_call = message.tool_calls[0]
    arguments = json.loads(tool_call.function.arguments)

    if tool_call.function.name == "get_weather":
        destination = arguments.get("destination_city")
        result = get_weather(destination)
        # Return weather text so the model can pass it to artist if needed
        response = {
            "role": "tool",
            "content": json.dumps({"destination_city": destination, "weather": result}),
            "tool_call_id": tool_call.id,
        }
        return response, arguments

    elif tool_call.function.name == "artist":
        city    = arguments.get("city")
        weather = arguments.get("weather", "clear sky")  # default if model skips get_weather
        filepath = artist(city, weather)
        response = {
            "role": "tool",
            "content": json.dumps({"image_saved": filepath}),
            "tool_call_id": tool_call.id,
        }
        return response, arguments

    else:
        response = {
            "role": "tool",
            "content": json.dumps({"error": "Unknown tool"}),
            "tool_call_id": tool_call.id,
        }
        return response, {}
