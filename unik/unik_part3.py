# unik_part3.py
import json
import os
from unik_part2 import execute, GLOBAL_ENV, TASKS

# -------------------------
# SELF-EVOLVING CACHE
# -------------------------
CACHE_FILE = ".unik_ai_cache.json"

if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        AI_CACHE = json.load(f)
else:
    AI_CACHE = {"errors": {}, "patterns": {}, "suggestions": {}}

def save_cache():
    with open(CACHE_FILE, "w") as f:
        json.dump(AI_CACHE, f, indent=2)

# -------------------------
# AI INTEGRATION (SIMULATED)
# -------------------------
def aik(prompt, context=None):
    """
    Simulated AI engine:
    - Generates code snippet suggestion
    - Returns placeholder AST (Number/String)
    - Stores usage in cache
    """
    key = prompt.lower()
    suggestion = f"# AI Suggestion for: {prompt}"
    AI_CACHE["suggestions"][key] = suggestion
    save_cache()
    print(f"[AI Suggestion] {suggestion}")
    # Return placeholder AST node for demo
    from unik_part1 import String
    return String(f"<AI-generated code for '{prompt}'>")

# -------------------------
# EXPLAINABLE DEBUGGER
# -------------------------
async def execute_with_debug(node, env=None):
    if env is None:
        env = GLOBAL_ENV
    try:
        return await execute(node, env)
    except Exception as e:
        # Log error in cache
        err_msg = str(e)
        AI_CACHE["errors"].setdefault(err_msg, 0)
        AI_CACHE["errors"][err_msg] += 1
        save_cache()
        # Human-readable explanation
        explanation = explain_error(node, e)
        print(f"[Error] {err_msg}")
        print(f"[Hint] {explanation}")

def explain_error(node, error):
    """
    Basic explainable error generator
    """
    msg = str(error)
    if "unsupported operand type" in msg or "TypeError" in msg:
        return "Type mismatch. Check variable types or cast them."
    elif "division by zero" in msg:
        return "Division by zero. Ensure denominator is non-zero."
    elif "NameError" in msg:
        return "Variable not defined. Did you declare it before use?"
    else:
        return "Check your code logic."

# -------------------------
# SELF-EVOLVING PATTERNS
# -------------------------
def log_pattern(node_type):
    """
    Track frequently used patterns (like repeat loops)
    """
    key = str(node_type)
    AI_CACHE["patterns"].setdefault(key, 0)
    AI_CACHE["patterns"][key] += 1
    save_cache()
