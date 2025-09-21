import json
from config import openai, CHAT_MODEL, system_message
from tools import tools, handle_tool_call, artist


def chat(message, history):
    messages = [{"role": "system", "content": system_message}] + history + [
        {"role": "user", "content": message}
    ]

    while True:
        response = openai.chat.completions.create(
            model=CHAT_MODEL, messages=messages, tools=tools
        )
        msg = response.choices[0].message

        # If the model requested tool(s)
        if msg.tool_calls:
            messages.append(msg)  # assistant request
            for tool_call in msg.tool_calls:
                tool_response, args = handle_tool_call(tool_call)
                messages.append(tool_response)

                # 👇 Auto-image after weather (NOT as tool message)
                if tool_call.function.name == "get_weather":
                    city = args.get("destination_city")
                    weather = json.loads(tool_response["content"]).get("weather")
                    img_path = artist(city, weather)
                    if img_path:
                        # Instead of role=tool, we append it as assistant text
                        messages.append({
                            "role": "assistant",
                            "content": f"Here’s an image for {city} with current weather: ![{city}]({img_path})"
                        })

            continue  # loop back until we get final assistant text

        # Otherwise it's a normal assistant reply
        reply = msg.content
        messages.append({"role": "assistant", "content": reply})
        return reply, messages


# --- Main Program ---
if __name__ == "__main__":
    history = []
    print("\n🤖 UtilityAI Chatbot ready!")
    print("👉 I can help with:")
    print("   - 🌤 Weather (auto image included)")
    print("   - 🎨 City images directly (artist tool)")
    print("\n💡 Example prompts you can try:")
    print("   • What’s the weather in Paris,FR?")
    print("   • Show me an image of Rome in sunny weather")
    print("   • What’s the weather in Tokyo? (should also give you an image)")
    print("   • Can you generate an image of New York City at night?")
    print("\nType 'quit' to exit.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in {"quit", "exit"}:
            print("Goodbye 👋")
            break

        reply, history = chat(user_input, history)
        print("Bot:", reply, "\n")

    # Save chat history at the end
    with open("chat_history.json", "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    print("📝 Chat history saved to chat_history.json")
