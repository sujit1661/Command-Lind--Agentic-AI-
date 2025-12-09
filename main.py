import os
import json
from openai import OpenAI

client = OpenAI(
    api_key="",
    base_url="https://generativelanguage.googleapis.com/v1beta/"
)


# -------------------------
# LOCAL FUNCTIONS
# -------------------------

def run_cmd(cmd: str) -> str:
    if cmd.startswith("mkdir"):
        folder_name = cmd.split(" ", 1)[1]
        try:
            os.makedirs(folder_name, exist_ok=True)
            # 👇 GET THE FULL PATH ON YOUR COMPUTER
            abs_path = os.path.abspath(folder_name)
            return f"📁 Created folder at: {abs_path}"
        except Exception as e:
            return f"❌ mkdir error: {e}"

    return "⚠️ Only mkdir allowed here."


def write_file(filename: str, content: str) -> str:
    try:
        folder = os.path.dirname(filename)
        if folder and not os.path.exists(folder):
            os.makedirs(folder)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

        return f"📝 File written: {filename}"
    except Exception as e:
        return f"❌ write error: {e}"


available_functions = {
    "run_cmd": run_cmd,
    "write_file": write_file
}


# -------------------------
# TOOL SCHEMA
# -------------------------

tools = [
    {
        "type": "function",
        "function": {
            "name": "run_cmd",
            "parameters": {
                "type": "object",
                "properties": {
                    "cmd": {"type": "string"}
                },
                "required": ["cmd"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["filename", "content"]
            }
        }
    }
]


# -------------------------
# SYSTEM PROMPT
# -------------------------

system_prompt = """
You are a ONE-SHOT project builder.
User gives ONE prompt → You create EVERYTHING.

Rules:
- Plan ALL files before tool calls.
- Use multiple write_file calls in SAME response.
- After executing ALL files, produce ONE summary message.
- NEVER reply `Task completed.` without context.
- Return human readable explanation of what you built.
"""


# -------------------------
# MAIN LOOP
# -------------------------
def main():
    messages = [{"role": "system", "content": system_prompt}]

    while True:
        user = input("\nYou: ")
        messages.append({"role": "user", "content": user})

        response = client.chat.completions.create(
            model="gemini-2.0-flash",  # 2.5 is not standard yet, usually 1.5 or 2.0
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        msg = response.choices[0].message
        # -------------------------------------------------------
        # ✅ CRITICAL FIX: Append the assistant's thought process
        # to the history BEFORE handling the tools.
        # -------------------------------------------------------
        messages.append(msg)
        # ---------- TOOL CALL HANDLER ----------
        if msg.tool_calls:
            for tool_call in msg.tool_calls:
                fn = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                result = available_functions[fn](**args)
                print(f"⚙️ {fn}: {result}")

                messages.append({
                    "role": "tool",
                    "name": fn,
                    "tool_call_id": tool_call.id,
                    "content": result
                })

            # Get the final response after tools have run
            final = client.chat.completions.create(
                model="gemini-2.0-flash",
                messages=messages
            )
            print("\n🔹 Bot Summary:\n", final.choices[0].message.content or "(no content)")
            # Optional: Append final answer so conversation continues contextually
            messages.append(final.choices[0].message)

        else:
            # If no tools were called, just print the response
            print("\n🔹 Bot:\n", msg.content)

if __name__ == "__main__":
    main()
