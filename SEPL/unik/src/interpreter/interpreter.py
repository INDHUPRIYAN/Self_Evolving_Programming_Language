import os
import time
from src.ast.nodes import *

class Environment:
    """Stores variables, functions, and classes."""
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise NameError(f"Variable '{name}' not defined")

    def set(self, name, value):
        self.vars[name] = value

    def update(self, name, value):
        if name in self.vars:
            self.vars[name] = value
        elif self.parent:
            self.parent.update(name, value)
        else:
            raise NameError(f"Variable '{name}' not defined")


class Interpreter:
    """Executes AST nodes for Unik."""

    def __init__(self):
        self.global_env = Environment()

    def run(self, nodes, env=None):
        env = env or self.global_env
        result = None
        for node in nodes:
            result = self.eval(node, env)
        return result

    # ----------------- Node Evaluation -----------------
    def eval(self, node, env):
        if isinstance(node, Number):
            return node.value
        elif isinstance(node, String):
            return node.value
        elif isinstance(node, Boolean):
            return node.value
        elif isinstance(node, Var):
            return env.get(node.name)
        elif isinstance(node, Assign):
            val = self.eval(node.expr, env)
            env.set(node.name, val)
            return val
        elif isinstance(node, BinOp):
            left = self.eval(node.left, env)
            right = self.eval(node.right, env)
            return self.apply_op(left, node.op, right)
        elif isinstance(node, Print):
            val = self.eval(node.expr, env)
            print(val)
            return val
        elif isinstance(node, Input):
            prompt = self.eval(node.prompt, env) if node.prompt else ""
            return input(prompt)
        elif isinstance(node, FuncDef):
            env.set(node.name, node)
            return node
        elif isinstance(node, FuncCall):
            func = env.get(node.name)
            if not isinstance(func, FuncDef):
                raise TypeError(f"{node.name} is not a function")
            args = [self.eval(a, env) for a in node.args]
            return self.call_function(func, args, env)
        elif isinstance(node, ClassDef):
            env.set(node.name, node)
            return node
        elif isinstance(node, AI):
            return self.eval_ai(node.prompt, env)
        elif isinstance(node, If):
            cond = self.eval(node.cond, env)
            if cond:
                return self.run(node.body, Environment(env))
            else:
                return self.run(node.orelse, Environment(env))
        elif isinstance(node, AlterCase):
            val = self.eval(node.expr, env)
            for key, block in node.cases.items():
                if val == key:
                    return self.run(block, Environment(env))
            if node.default:
                return self.run(node.default, Environment(env))
        elif isinstance(node, ForLoop):
            start = self.eval(node.start, env)
            end = self.eval(node.end, env)
            step = self.eval(node.step, env) if node.step else 1
            for i in range(start, end, step):
                env.set(node.var, i)
                self.run(node.body, Environment(env))
        elif isinstance(node, Repeat):
            while self.eval(node.cond, env):
                self.run(node.body, Environment(env))
        elif isinstance(node, TryCatch):
            try:
                return self.run(node.try_body, Environment(env))
            except Exception as e:
                env.set("error", e)
                return self.run(node.catch_body, Environment(env))
            finally:
                if node.finally_body:
                    self.run(node.finally_body, Environment(env))
        elif isinstance(node, Return):
            return self.eval(node.value, env) if node.value else None
        elif isinstance(node, Break):
            raise StopIteration("Break")
        else:
            raise TypeError(f"Unknown node type: {type(node)}")

    # ----------------- Function Execution -----------------
    def call_function(self, func_def, args, env):
        local = Environment(env)
        for i, param in enumerate(func_def.params):
            val = args[i] if i < len(args) else None
            local.set(param, val)
        if func_def.single_line_expr:
            return self.eval(func_def.single_line_expr, local)
        else:
            return self.run(func_def.body, local)

    # ----------------- Operators -----------------
    def apply_op(self, left, op, right):
        if op == "+": return left + right
        elif op == "-": return left - right
        elif op == "*": return left * right
        elif op == "/": return left / right
        elif op == "%": return left % right
        elif op == "==": return left == right
        elif op == "!=": return left != right
        elif op == "<": return left < right
        elif op == "<=": return left <= right
        elif op == ">": return left > right
        elif op == ">=": return left >= right
        elif op == "&&": return left and right
        elif op == "||": return left or right
        else:
            raise SyntaxError(f"Unsupported operator {op}")

    # ----------------- AI Integration -----------------
    def eval_ai(self, prompt, env):
        print(f"[AI] Generating code for prompt: {prompt}")
        # Placeholder: actual AI code generation can be integrated here
        return None


# ----------------- Quick Test -----------------
if __name__ == "__main__":
    from lexer.lexer import Lexer
    from src.parser.parser import Parser

    code = '''
    x = 10
    y = 20
    aik @{"Write addition function for x and y"}
    func add(a, b) -> a + b
    give add(x, y)
    '''

    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.run(ast)
