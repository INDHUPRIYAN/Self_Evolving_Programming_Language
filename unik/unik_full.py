# unik_full.py
import asyncio
import json
import os

# -------------------------
# AST NODES
# -------------------------
class Node: pass

class Number(Node):
    def __init__(self, value): self.value = value

class String(Node):
    def __init__(self, value): self.value = value

class Var(Node):
    def __init__(self, name): self.name = name

class Assign(Node):
    def __init__(self, name, value): self.name = name; self.value = value

class Give(Node):
    def __init__(self, expr): self.expr = expr

class Ask(Node):
    def __init__(self, prompt, name): self.prompt = prompt; self.name = name

class Repeat(Node):
    def __init__(self, count, body): self.count = count; self.body = body

class Task(Node):
    def __init__(self, body): self.body = body

class Seq(Node):
    def __init__(self, statements): self.statements = statements

# -------------------------
# LEXER (simplified)
# -------------------------
def lex(code):
    """Very basic lexer splitting by spaces and symbols"""
    tokens = code.replace("{"," { ").replace("}"," } ").replace("+"," + ").split()
    return tokens

# -------------------------
# PARSER (simplified)
# -------------------------
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        if self.pos < len(self.tokens): return self.tokens[self.pos]
        return None

    def eat(self, expected=None):
        tok = self.current()
        if expected and tok != expected:
            raise Exception(f"Expected {expected}, got {tok}")
        self.pos += 1
        return tok

    def parse_expr(self):
        tok = self.current()
        if tok is None:
            return None
        if tok.isdigit():
            self.eat(); return Number(int(tok))
        elif tok.startswith('"') and tok.endswith('"'):
            self.eat(); return String(tok.strip('"'))
        elif tok.isidentifier():
            self.eat(); return Var(tok)
        elif tok == "(":
            self.eat()
            node = self.parse_expr()
            self.eat(")")
            return node
        elif tok == "+":
            self.eat()
            return self.parse_expr()
        return None

    def parse_statement(self):
        tok = self.current()
        if tok == "give":
            self.eat(); expr = self.parse_expr(); return Give(expr)
        elif tok == "ask":
            self.eat()
            prompt = self.eat()
            if self.current() == "->":
                self.eat(); name = self.eat()
                return Ask(prompt.strip('"'), name)
        elif tok == "repeat":
            self.eat(); count = int(self.eat()); self.eat("{")
            stmts = []
            while self.current() != "}":
                stmts.append(self.parse_statement())
            self.eat("}")
            return Repeat(count, Seq(stmts))
        elif tok == "task":
            self.eat(); self.eat("{")
            stmts = []
            while self.current() != "}":
                stmts.append(self.parse_statement())
            self.eat("}")
            return Task(Seq(stmts))
        elif "=" in self.tokens:
            idx = self.tokens.index("=")
            name = self.tokens[0]
            self.pos = idx + 1
            value = self.parse_expr()
            return Assign(name, value)
        else:
            self.eat()
            return None

    def parse(self):
        stmts = []
        while self.current() is not None:
            stmt = self.parse_statement()
            if stmt:
                stmts.append(stmt)
        return stmts

# -------------------------
# ENVIRONMENT
# -------------------------
GLOBAL_ENV = {}

# -------------------------
# AI CACHE
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

def aik(prompt, context=None):
    key = prompt.lower()
    suggestion = f"# AI Suggestion for: {prompt}"
    AI_CACHE["suggestions"][key] = suggestion
    save_cache()
    print(f"[AI Suggestion] {suggestion}")
    return String(f"<AI-generated code for '{prompt}'>")

# -------------------------
# EXECUTOR
# -------------------------
async def execute(node, env):
    if isinstance(node, Number): return node.value
    if isinstance(node, String): return node.value
    if isinstance(node, Var):
        if node.name in env: return env[node.name]
        raise Exception(f"NameError: {node.name} not defined")
    if isinstance(node, Assign):
        val = await execute(node.value, env)
        env[node.name] = val
        return val
    if isinstance(node, Give):
        val = await execute(node.expr, env)
        print(val)
        return val
    if isinstance(node, Ask):
        val = input(f"{node.prompt}: ")
        env[node.name] = val
        return val
    if isinstance(node, Repeat):
        for _ in range(node.count):
            await execute(node.body, env)
    if isinstance(node, Seq):
        for stmt in node.statements:
            await execute(stmt, env)
    if isinstance(node, Task):
        # simple async task
        asyncio.create_task(execute(node.body, env))

async def execute_with_debug(node, env=None):
    if env is None: env = GLOBAL_ENV
    try:
        return await execute(node, env)
    except Exception as e:
        err_msg = str(e)
        AI_CACHE["errors"].setdefault(err_msg, 0)
        AI_CACHE["errors"][err_msg] += 1
        save_cache()
        print(f"[Error] {err_msg}")
        print(f"[Hint] {explain_error(node, e)}")

def explain_error(node, error):
    msg = str(error)
    if "not defined" in msg:
        return "Variable not defined. Did you declare it before use?"
    elif "unsupported operand" in msg:
        return "Type mismatch. Check variable types."
    else:
        return "Check your code logic."

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
            if line.strip().lower() == "exit": break
            if line.strip() == "": continue
            if line.split()[0].lower() in ["add","connect","generate"]:
                await handle_conversation(line)
                continue
            buffer += line + "\n"
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
# MAIN
# -------------------------
if __name__ == "__main__":
    asyncio.run(repl())
