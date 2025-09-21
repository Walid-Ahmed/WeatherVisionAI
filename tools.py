import json
import base64
import requests
from io import BytesIO
from datetime import datetime
from PIL import Image
from config import openai, IMAGE_MODEL, weather_api_key


# --- Weather Tool ---
def get_weather(destination_city):
    print(f"🔧 get_weather called for {destination_city}")
    city = destination_city.strip().replace(", ", ",")

    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": weather_api_key, "units": "metric"}

    try:
        response = requests.get(url, params=params)
        print(f"🌍 Weather API status: {response.status_code}")
        print(f"🌍 Weather API raw: {response.text[:200]}")  # log first 200 chars

        if response.status_code == 200:
            data = response.json()
            desc = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            return f"{desc.capitalize()} with {temp}°C"
        else:
            return f"Weather data not available for {city}"
    except Exception as e:
        return f"Error fetching weather: {e}"


weather_function = {
    "name": "get_weather",
    "description": "Get the current weather for a destination city using OpenWeatherMap.",
    "parameters": {
        "type": "object",
        "properties": {
            "destination_city": {"type": "string"},
        },
        "required": ["destination_city"],
    },
}


# --- Artist Tool (Image Generation) ---
def artist(city, weather=""):
    print(f"🎨 artist called for {city} with weather: {weather}")
    try:
        prompt = f"An image representing {city}"
        if weather:
            prompt += f" with {weather} weather"
        prompt += ", in a vibrant pop-art style, showing tourist landmarks."

        image_response = openai.images.generate(
            model=IMAGE_MODEL,   # e.g. "dall-e-3"
            prompt=prompt,
            size="1024x1024",
            n=1,
            response_format="b64_json"
        )

        # Decode base64 image
        image_base64 = image_response.data[0].b64_json
        if not image_base64:
            print("❌ No image data returned from API")
            return None

        image_data = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_data))

        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{city.lower().replace(' ', '_')}_{timestamp}.png"

        # Save and show the file
        image.save(filename)
        print(f"✅ Image saved as {filename}")
        image.show()

        return filename  # return saved file path

    except Exception as e:
        print(f"❌ Image generation failed: {e}")
        return None


artist_function = {
    "name": "artist",
    "description": "Generate an image of a city (optionally including weather context).",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {"type": "string"},
            "weather": {"type": "string"},
        },
        "required": ["city"],
    },
}


# --- Tools Registry ---
tools = [
    {"type": "function", "function": weather_function},
    {"type": "function", "function": artist_function},
]


# --- Handle Tool Calls ---
def handle_tool_call(tool_call):
    arguments = json.loads(tool_call.function.arguments)

    if tool_call.function.name == "get_weather":
        destination = arguments.get("destination_city")
        result = get_weather(destination)
        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps({
                "destination_city": destination,
                "weather": result
            })
        }, arguments

    elif tool_call.function.name == "artist":
        city = arguments.get("city")
        weather = arguments.get("weather", "")
        result = artist(city, weather)
        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps({
                "city": city,
                "image": result
            })
        }, arguments

    else:
        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps({"error": "Unknown tool"})
        }, {}
