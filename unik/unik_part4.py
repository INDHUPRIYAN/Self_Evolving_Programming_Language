import asyncio
from unik_part2 import run_program, GLOBAL_ENV
from unik_part3 import execute_with_debug, aik
from unik_part1 import lex, Parser
# -------------------------
# CONVERSATIONAL COMMANDS
# -------------------------
CONVERSATION_TEMPLATES = {
    "add login system": "Created login.unik template.",
    "connect to firebase": "Added Firebase connection snippet."
}

async def handle_conversation(cmd):
    response = CONVERSATION_TEMPLATES.get(cmd.lower(), None)
    if response:
        print(f"✔ {response}")
    else:
        # fallback to AI suggestion
        aik(cmd)

# -------------------------
# REPL
# -------------------------
async def repl():
    print("Welcome to Unik REPL! Type 'exit' to quit.")
    buffer = ""
    while True:
        try:
            line = input("unik> ")
            if line.strip().lower() == "exit":
                break
            if line.strip() == "":
                continue
            # Check for conversational command
            if line.split()[0].lower() in ["add", "connect", "generate"]:
                await handle_conversation(line)
                continue
            # Append line to buffer for multi-line support
            buffer += line + "\n"
            # Simple heuristic: parse on closing brace or single line
            if "}" in line or line.strip().startswith("give") or line.strip().startswith("ask") or "=" in line:
                tokens = lex(buffer)
                parser = Parser(tokens)
                try:
                    nodes = parser.parse()
                    for node in nodes:
                        await execute_with_debug(node, GLOBAL_ENV)
                except Exception as e:
                    print(f"[Parser Error] {e}")
                buffer = ""
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt - use 'exit' to quit")
        except Exception as e:
            print(f"[REPL Error] {e}")

# -------------------------
# MAIN ENTRY
# -------------------------
if __name__ == "__main__":
    asyncio.run(repl())
