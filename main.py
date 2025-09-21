import json
from config import openai, CHAT_MODEL, system_message
from tools import tools, handle_tool_call

# --- Chat function ---
def chat(message, history):
    messages = [{"role": "system", "content": system_message}] + history + [
        {"role": "user", "content": message}
    ]

    while True:
        response = openai.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            tools=tools,
        )

        choice = response.choices[0]

        if choice.finish_reason == "tool_calls":
            tool_message = choice.message
            tool_response, _ = handle_tool_call(tool_message)
            messages.append(tool_message)
            messages.append(tool_response)
            continue  # loop until final reply

        reply = choice.message.content
        messages.append({"role": "assistant", "content": reply})
        return reply, messages


# --- Main program ---
if __name__ == "__main__":
    history = []
    print("\n🌦️ WeatherVisionAI ready!")
    print("👉 Ask me about the weather in any city, and I’ll also generate an image for you.")
    print("Examples:")
    print("   - What’s the weather in Paris,FR?")
    print("   - How is the weather in Toronto,CA?")
    print("   - Tell me the weather in Tokyo,JP\n")
    print("Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in {"quit", "exit"}:
            print("Goodbye 👋")
            break

        reply, history = chat(user_input, history)
        print("Bot:", reply, "\n")

    # Save chat history
    with open("chat_history.json", "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    print("📝 Chat history saved to chat_history.json")

