import os
import json
import requests
from datetime import datetime
from config import openai, IMAGE_MODEL, weather_api_key
from PIL import Image
from io import BytesIO

# --- Internal artist helper ---
def artist(city, weather):
    print(f"🎨 artist called for {city} with weather: {weather}")
    try:
        # Generate image with OpenAI
        image_response = openai.images.generate(
            model=IMAGE_MODEL,  # "dall-e-3"
            prompt=f"A vibrant pop-art style image of {city} with {weather}. Show landmarks and atmosphere.",
            size="1024x1024",
            n=1
        )

        # Get URL of generated image
        image_url = image_response.data[0].url

        # Download the image
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))

        # Ensure images directory exists
        os.makedirs("images", exist_ok=True)

        # Save with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{city.lower().replace(',','').replace(' ','')}_{timestamp}.png"
        filepath = os.path.join("images", filename)
        img.save(filepath)

        print(f"✅ Image saved as {filepath}")

        # Show the image in default viewer
        try:
            img.show()
            print("👀 Image opened in default viewer.")
        except Exception as e:
            print(f"⚠️ Could not auto-open image: {e}")

        return filepath

    except Exception as e:
        print(f"❌ Image generation failed: {e}")
        return None



# --- Weather Tool (calls artist internally) ---
def get_weather(destination_city: str):
    """Fetch current weather for a city using OpenWeather API + generate an image."""
    print(f"🔧 get_weather called for {destination_city}")

    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": destination_city, "appid": weather_api_key, "units": "metric"}

    try:
        response = requests.get(url, params=params)
        print(f"🌍 Weather API status: {response.status_code}")
        print(f"🌍 Weather API raw: {response.text[:200]}")  # truncated debug

        if response.status_code == 200:
            data = response.json()
            desc = data["weather"][0]["description"].capitalize()
            temp = data["main"]["temp"]
            weather_text = f"{desc} with {temp}°C"

            # Call artist internally
            artist(destination_city, weather_text)

            return weather_text
        else:
            return f"Weather data not available for {destination_city}"
    except Exception as e:
        return f"Error fetching weather: {e}"


# --- Tool Schema ---
weather_function = {
    "name": "get_weather",
    "description": "Get the current weather for a city. This tool also generates an image of the city with its weather.",
    "parameters": {
        "type": "object",
        "properties": {
            "destination_city": {"type": "string"},
        },
        "required": ["destination_city"],
    },
}

# --- Tools list ---
tools = [{"type": "function", "function": weather_function}]

# --- Tool handler ---
def handle_tool_call(message):
    tool_call = message.tool_calls[0]
    arguments = json.loads(tool_call.function.arguments)

    if tool_call.function.name == "get_weather":
        destination = arguments.get("destination_city")
        result = get_weather(destination)
        response = {
            "role": "tool",
            "content": json.dumps({"destination_city": destination, "weather": result}),
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
