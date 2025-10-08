# ------------------- AST Nodes for Unik -------------------

class Node:
    pass

# ------------------- Basic Values -------------------
class Number(Node):
    def __init__(self, value):
        self.value = float(value) if '.' in str(value) else int(value)

class String(Node):
    def __init__(self, value):
        self.value = value.strip('"')

class Boolean(Node):
    def __init__(self, value):
        self.value = value

class Var(Node):
    def __init__(self, name):
        self.name = name

# ------------------- Assignment & Operations -------------------
class Assign(Node):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

class BinOp(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

# ------------------- I/O -------------------
class Print(Node):
    def __init__(self, expr):
        self.expr = expr

class Input(Node):
    def __init__(self, prompt=None):
        self.prompt = prompt

# ------------------- Functions -------------------
class FuncDef(Node):
    def __init__(self, name, params, body=None, single_line_expr=None):
        self.name = name
        self.params = params
        self.body = body or []
        self.single_line_expr = single_line_expr

class FuncCall(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Return(Node):
    def __init__(self, value=None):
        self.value = value

# ------------------- Conditionals -------------------
class If(Node):
    def __init__(self, cond, body, orelse):
        self.cond = cond
        self.body = body
        self.orelse = orelse

class AlterCase(Node):
    def __init__(self, expr, cases, default=None):
        self.expr = expr
        self.cases = cases  # dictionary {case_value: body}
        self.default = default

# ------------------- Loops -------------------
class ForLoop(Node):
    def __init__(self, var, start, end, step, body):
        self.var = var
        self.start = start
        self.end = end
        self.step = step
        self.body = body

class Repeat(Node):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

class Break(Node):
    pass

# ------------------- Classes & OOP -------------------
class ClassDef(Node):
    def __init__(self, name, body, parent=None):
        self.name = name
        self.body = body
        self.parent = parent

# ------------------- Error Handling -------------------
class TryCatch(Node):
    def __init__(self, try_body, catch_body, finally_body=None):
        self.try_body = try_body
        self.catch_body = catch_body
        self.finally_body = finally_body

# ------------------- AI Integration -------------------
class AI(Node):
    def __init__(self, prompt):
        self.prompt = prompt

# ------------------- Tasks & Async -------------------
class Task(Node):
    def __init__(self, name, body):
        self.name = name
        self.body = body

class Await(Node):
    def __init__(self, expr):
        self.expr = expr

class AsyncFuncDef(Node):
    def __init__(self, name, params, body=None, single_line_expr=None):
        self.name = name
        self.params = params
        self.body = body or []
        self.single_line_expr = single_line_expr

# ------------------- Testing -------------------
class TestBlock(Node):
    def __init__(self, description, body):
        self.description = description
        self.body = body
