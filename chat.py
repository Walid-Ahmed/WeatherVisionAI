from config import system_message, MODEL, openai
from tools import tools, handle_tool_call


def chat(message, history):
    """Chat function: adds user msg, handles tools, returns reply + history."""

    # Build conversation so far
    messages = [{"role": "system", "content": system_message}] + history + [
        {"role": "user", "content": message}
    ]

    # First model call
    response = openai.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools
    )

    # If the assistant requests a tool
    if response.choices[0].finish_reason == "tool_calls":
        tool_request = response.choices[0].message
        response_tool, _ = handle_tool_call(tool_request)

        # Add tool call + tool response
        messages.extend([tool_request, response_tool])

        # Call model again with tool response
        response = openai.chat.completions.create(model=MODEL, messages=messages)

    # Final assistant reply
    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})

    return reply, messages
