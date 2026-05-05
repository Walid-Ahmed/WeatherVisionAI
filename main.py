import json
from config import openai, CHAT_MODEL
from tools import tools, handle_tool_call

# --- Chat function ---
# Builds the message history and runs the agentic loop.
# No system message is used — the model reasons purely from the tools array.
def chat(message, history):
    # Append the new user message to the existing conversation history
    messages = history + [{"role": "user", "content": message}]

    # Agentic loop: keep calling the model until it returns a final text reply.
    # Each iteration handles one tool call (get_weather or artist).
    # The model decides which tool to call and when based on tool descriptions alone.
    while True:
        response = openai.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            tools=tools,   # tools array exposed to the model — no system message needed
        )

        choice = response.choices[0]

        if choice.finish_reason == "tool_calls":
            # Model decided to call a tool — execute it and feed the result back
            tool_message = choice.message
            tool_response, _ = handle_tool_call(tool_message)
            messages.append(tool_message)    # assistant's tool-call request
            messages.append(tool_response)   # tool result (role: "tool")
            continue  # loop back so the model can continue reasoning

        # finish_reason == "stop" — model produced a final text reply
        reply = choice.message.content
        messages.append({"role": "assistant", "content": reply})
        return reply, messages


# --- Main program ---
if __name__ == "__main__":
    history = []
    print("\n🌦️ WeatherVisionAI ready!")
    print("👉 The assistant reasons on its own about when to call tools — no instructions needed.\n")
    print("Weather only (calls get_weather):")
    print("   - What's the weather in Paris,FR?")
    print("   - Is it hot in Tokyo,JP right now?")
    print("\nWeather + image (calls get_weather, then artist):")
    print("   - What's the weather in Toronto,CA? Also show me an image.")
    print("   - How cold is it in London,GB? Generate a city image too.")
    print("\nGeneral questions (no tools called):")
    print("   - What is your name?")
    print("   - What can you help me with?\n")
    print("Type 'quit' to exit.")
    print("💾 Your conversation will be saved to chat_history.json on exit.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in {"quit", "exit"}:
            print("Goodbye 👋")
            break

        reply, history = chat(user_input, history)
        print("Bot:", reply, "\n")

    # Save the full conversation to disk for inspection or replay
    with open("chat_history.json", "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    print("📝 Chat history saved to chat_history.json")
