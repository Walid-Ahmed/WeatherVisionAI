# WeatherVisionAI 🌤️🖼️

[![GitHub Repo](https://img.shields.io/badge/GitHub-WeatherVisionAI-blue?logo=github)](https://github.com/Walid-Ahmed/WeatherVisionAI/)

WeatherVisionAI is an **agentic AI assistant** that answers weather questions and **automatically generates images** reflecting the weather in that city.  
It combines OpenWeatherMap (for live weather) with OpenAI’s image generation (for visual context).  

👉 Repo: [https://github.com/Walid-Ahmed/WeatherVisionAI/](https://github.com/Walid-Ahmed/WeatherVisionAI/)


## Tool Calling (No Agent Framework)

This project uses the OpenAI Python SDK directly for tool calling (function calling).  
No agent framework is used (e.g., LangChain, CrewAI). Tools are provided to the model in the API request, and the model can choose to call them (via `tool_calls`), which the application executes in Python.

```python
response = openai.chat.completions.create(
    model=CHAT_MODEL,
    messages=messages,
    tools=tools,  # expose available tools to the model (framework-free tool calling)
)
```

### Known Limitation: Only the first tool call is handled

In `tools.py`, the tool handler reads only the first tool call from the response:

```python
tool_call = message.tool_calls[0]  # only handles the first tool call
```

If the model were to return multiple tool calls in a single response, the remaining ones would be silently ignored. **This is intentional** — the app exposes only one tool (`get_weather`), so the model will never return more than one tool call per turn. No fix is needed for the current design.

### One tool exposed to the model, two Python functions

`tools.py` contains two functions — `get_weather` and `artist` — but only `get_weather` is registered in the `tools` list passed to the model. `artist` is an internal helper called directly by `get_weather` to generate the city image; the model has no knowledge of it and cannot call it independently. This is intentional to keep the design simple.



## 🚀 Features
- Ask about weather in any city (with optional country code).
- Automatically generates a pop-art style image representing the city under current weather conditions.
- Images saved in the `images/` folder and previewed inline.
- Simple and extensible design (agentic workflow: `weather → image`).

---

## ⚙️ Setup

### 1. Clone the repo
```bash
git clone https://github.com/Walid-Ahmed/WeatherVisionAI.git
cd WeatherVisionAI
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create `.env` file
Create a file named `.env` in the project root with your API keys:

```env
OPENAI_API_KEY=your_openai_key_here
OPENWEATHER_API_KEY=your_openweathermap_key_here
```

> 🔑 Get free weather API key from: [https://openweathermap.org/api](https://openweathermap.org/api)

---

## 🔧 Configuration

All configuration lives in `config.py`. It loads API keys from a `.env` file and defines the models used throughout the app.

| Setting | Value | Purpose |
|---|---|---|
| `CHAT_MODEL` | `gpt-4o-mini` | Handles conversation and tool-call decisions |
| `IMAGE_MODEL` | `dall-e-3` | Generates the city weather image via `artist` |
| `OPENAI_API_KEY` | from `.env` | Authenticates both chat and image API calls |
| `OPENWEATHER_API_KEY` | from `.env` | Fetches live weather data |

To swap models, edit the constants in `config.py`:

```python
CHAT_MODEL = "gpt-4o-mini"   # change to e.g. "gpt-4o" for a more capable chat model
IMAGE_MODEL = "dall-e-3"     # only dall-e-3 and dall-e-2 are supported
```

---

## ▶️ Usage
Run the assistant:

```bash
python main.py
```

Then type questions like:
- `What's the weather in Toronto,CA?`
- `How is the weather in Paris,FR?`
- `Tell me the weather in Tokyo,JP`

---

## 🧠 Workflow

WeatherVisionAI uses an **agentic flow**. The model decides whether to call a tool based on the user's question:

```mermaid
flowchart TD
    User["💬 User Question"] --> AI["🤖 AI Assistant\ngpt-4o-mini"]

    AI -->|"finish_reason = tool_calls\ne.g. What's the weather in Paris?"| ToolCall["🌤️ get_weather\ntool called"]
    AI -->|"finish_reason = stop\ne.g. What is your name?"| DirectReply["💬 Direct Reply\n(no tool needed)"]

    ToolCall --> Artist["🎨 artist\n(called internally by get_weather)"]
    Artist --> WeatherReply["🌦️ Weather Report + City Image"]
```

---

## 🖼️ Example

**Prompt:**
```
You: How is the weather in Toronto,CA?
```

**Response:**
```
🔧 get_weather called for Toronto,CA  
🎨 artist called for Toronto,CA with weather: Clear sky with 21.12°C  
✅ Image saved as images/sample_toronto.png  
Bot: The weather in Toronto, CA is clear sky with a temperature of 21.12°C.
```

**Generated Image:**

![Sample Toronto Weather](torontoca_20250921_191544.png)

---

## 📂 Project Structure
```
WeatherVisionAI/
│── main.py          # Chat loop, handles agentic workflow
│── tools.py         # Weather tool + artist image generator
│── config.py        # API keys and system configuration
│── requirements.txt # Dependencies
│── images/          # Saved generated images
│── README.md        # Project documentation
```

---

## 🏷️ Repo
👉 GitHub Repo: [https://github.com/Walid-Ahmed/WeatherVisionAI/](https://github.com/Walid-Ahmed/WeatherVisionAI/)

---

## 📜 License
MIT License – free to use, modify, and share.
