# unik_part2.py
import asyncio
import random
from unik_part1 import Number, String, Var, Assign, Give, Ask, Repeat, BinOp, TaskNode, AwaitNode

# -------------------------
# GLOBAL ENVIRONMENT
# -------------------------
GLOBAL_ENV = {}
TASKS = {}

# -------------------------
# HELPER FUNCTIONS
# -------------------------
async def run_task(task_id, block):
    for stmt in block:
        await execute(stmt)
    TASKS[task_id]["done"] = True

async def execute(node, env=None):
    if env is None: env = GLOBAL_ENV
    try:
        if isinstance(node, Number):
            return node.value
        elif isinstance(node, String):
            return node.value
        elif isinstance(node, Var):
            return env.get(node.name, None)
        elif isinstance(node, Assign):
            val = await execute(node.expr, env)
            env[node.var] = val
            return val
        elif isinstance(node, Give):
            val = await execute(node.expr, env)
            print(val)
            return val
        elif isinstance(node, Ask):
            user_input = input(node.prompt + ": ")
            env[node.var] = user_input
            return user_input
        elif isinstance(node, Repeat):
            for _ in range(node.count):
                for stmt in node.block:
                    await execute(stmt, env)
        elif isinstance(node, BinOp):
            left = await execute(node.left, env)
            right = await execute(node.right, env)
            return eval(f"{left}{node.op_sym}{right}")
        elif isinstance(node, TaskNode):
            task_id = f"task_{random.randint(1000,9999)}"
            TASKS[task_id] = {"done": False}
            asyncio.create_task(run_task(task_id, node.block))
            return task_id
        elif isinstance(node, AwaitNode):
            task_id = node.var
            while not TASKS.get(task_id, {}).get("done", True):
                await asyncio.sleep(0.1)
            return f"{task_id} completed"
        else:
            print(f"Unknown node: {node}")
    except Exception as e:
        print(f"[Runtime Error] {e}")

# -------------------------
# SIMULATED CROSS-DOMAIN COMMANDS
# -------------------------
async def read(filename):
    print(f"File {filename} read successfully.")
    return f"data_from_{filename}"

async def train(data, model_type="neural"):
    print(f"Model trained: {model_type} on {data}")
    return f"model_{model_type}"

async def serve(path, func):
    print(f"Server running at {path}")
    return f"server_{path}"

async def backup(path):
    print(f"Backing up {path}...")
    return f"backup_done_{path}"

# -------------------------
# EXECUTION WRAPPER
# -------------------------
async def run_program(ast_nodes):
    for stmt in ast_nodes:
        await execute(stmt)
