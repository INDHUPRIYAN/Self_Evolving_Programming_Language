# src/main.py  (single-file Unik runtime) - updated
# Added: break/continue/return handling, for-loop semantics, short-circuit logic, and parser keywords fixes.

import re
import sys
import json
import os

# ----------------------------
# Lexer
# ----------------------------
class Token:
    def __init__(self, typ, value, line, col):
        self.type = typ
        self.value = value
        self.line = line
        self.col = col
    def __repr__(self):
        return f"{self.type}({self.value!r}) at {self.line}:{self.col}"

class Lexer:
    KEYWORDS = {
        "func","class","trait","init","self",
        "if","else","alter","match","case",
        "loop","repeat","break","continue","return","ret",
        "try","catch","finally",
        "give","ask","askfile","givefile",
        "true","false","in",
        "task","run","async","await","wait",
        "test","aik","import","from","as",
    }

    TOKEN_SPEC = [
        ("STRING", r'"(?:\\.|[^"\\])*"'),
        ("NUMBER", r'\d+\.\d+|\d+'),
        # multi-char ops
        ("OP", r'\|\>|\.\.|->|==|!=|<=|>=|\+=|-=|\*=|/=|%=:|\+\+|--|&&|\|\||::|:\?'),
        # single-char ops
        ("OP", r'[+\-*/%<>=!?:@\$]'),
        ("ID", r'[A-Za-z_][A-Za-z0-9_]*'),
        ("PUNC", r'[\(\)\{\}\[\],;.]'),
        ("NEWLINE", r'\n'),
        ("SKIP", r'[ \t\r]+'),
        ("COMMENT", r'\#.*'),
        ("MISMATCH", r'.'),
    ]

    def __init__(self, code=None):
        self.code = code
        parts = []
        for i,(name,pat) in enumerate(self.TOKEN_SPEC):
            parts.append(f'(?P<{name}{i}>{pat})')
        self.master = re.compile('|'.join(parts))
        self.group_to_type = {f"{name}{i}":name for i,(name,_) in enumerate(self.TOKEN_SPEC)}

    def tokenize(self, code=None):
        if code is None:
            code = self.code or ""
        pos = 0
        line = 1
        col = 1
        tokens = []
        m = self.master.match
        L = len(code)
        while pos < L:
            match = m(code, pos)
            if not match:
                raise SyntaxError(f"Unexpected character {code[pos]!r} at {line}:{col}")
            g = match.lastgroup
            raw = match.group(g)
            typ = self.group_to_type[g]
            if typ == "NEWLINE":
                pos = match.end(); line += 1; col = 1; continue
            if typ in ("SKIP","COMMENT"):
                # update pos/col
                if "\n" in raw:
                    line += raw.count("\n")
                    col = len(raw.rsplit("\n",1)[-1]) + 1
                else:
                    col += len(raw)
                pos = match.end()
                continue
            if typ == "MISMATCH":
                raise SyntaxError(f"Unexpected token {raw!r} at {line}:{col}")
            if typ == "ID" and raw in self.KEYWORDS:
                typ = "KEYWORD"
            tok = Token(typ, raw, line, col)
            tokens.append(tok)
            consumed = len(raw)
            pos = match.end()
            if "\n" in raw:
                line += raw.count("\n")
                col = len(raw.rsplit("\n",1)[-1]) + 1
            else:
                col += consumed
        return tokens

# ----------------------------
# AST Nodes
# ----------------------------
class Node: pass

class Number(Node):
    def __init__(self, v): self.value = float(v) if '.' in v else int(v)
    def __repr__(self): return f"Number({self.value})"

class String(Node):
    def __init__(self, v): self.value = v[1:-1].encode('utf8').decode('unicode_escape')
    def __repr__(self): return f"String({self.value!r})"

class Boolean(Node):
    def __init__(self,v): self.value = (v=="true")
    def __repr__(self): return f"Boolean({self.value})"

class Var(Node):
    def __init__(self,name): self.name=name
    def __repr__(self): return f"Var({self.name})"

class Assign(Node):
    def __init__(self,name,expr): self.name=name; self.expr=expr
    def __repr__(self): return f"Assign({self.name}={self.expr})"

class BinOp(Node):
    def __init__(self,left,op,right): self.left=left; self.op=op; self.right=right
    def __repr__(self): return f"BinOp({self.left} {self.op} {self.right})"

class Print(Node):
    def __init__(self,expr): self.expr=expr
    def __repr__(self): return f"Print({self.expr})"

class Input(Node):
    def __init__(self,prompt=None): self.prompt=prompt
    def __repr__(self): return f"Input({self.prompt})"

class FuncDef(Node):
    def __init__(self,name,params,body=None,single=None, is_async=False):
        self.name=name; self.params=params; self.body=body or []; self.single=single; self.is_async=is_async
    def __repr__(self): return f"FuncDef({self.name}/{len(self.params)})"

class FuncCall(Node):
    def __init__(self,callee,args):
        self.callee=callee; self.args=args
    def __repr__(self): return f"FuncCall({self.callee}, {self.args})"

class If(Node):
    def __init__(self,cond,body,orelse): self.cond=cond; self.body=body; self.orelse=orelse
    def __repr__(self): return f"If({self.cond})"

class ForLoop(Node):
    def __init__(self, var, start, end, step, body, foreach=False):
        self.var = var
        self.start = start
        self.end = end
        self.step = step
        self.body = body
        self.foreach = foreach  # True if loop over collection

class Repeat(Node):
    def __init__(self,cond,body): self.cond=cond; self.body=body
    def __repr__(self): return f"Repeat({self.cond})"

class ClassDef(Node):
    def __init__(self,name,body,parent=None): self.name=name; self.body=body; self.parent=parent
    def __repr__(self): return f"ClassDef({self.name})"

class Return(Node):
    def __init__(self,val=None): self.val=val
    def __repr__(self): return f"Return({self.val})"

class Break(Node):
    def __repr__(self): return "Break()"

class Continue(Node):
    def __repr__(self): return "Continue()"

class TryCatch(Node):
    def __init__(self,tryb,catchb,finallyb=None): self.tryb=tryb; self.catchb=catchb; self.finallyb=finallyb

class AlterCase(Node):
    def __init__(self,expr,cases,default=None): self.expr=expr; self.cases=cases; self.default=default

class AI(Node):
    def __init__(self,prompt): self.prompt=prompt
    def __repr__(self): return f"AI({self.prompt})"

class ListLiteral(Node):
    def __init__(self,items): self.items=items
    def __repr__(self): return f"List({self.items})"

class DictLiteral(Node):
    def __init__(self,pairs): self.pairs=pairs
    def __repr__(self): return f"Dict({self.pairs})"

class AttrAccess(Node):
    def __init__(self, obj, attr): self.obj=obj; self.attr=attr
    def __repr__(self): return f"Attr({self.obj}.{self.attr})"

# ----------------------------
# Parser (recursive descent)
# ----------------------------
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def cur(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, typ=None, val=None):
        tok = self.cur()
        if not tok:
            raise SyntaxError("Unexpected end")
        if typ and tok.type != typ:
            raise SyntaxError(f"Expected {typ}, got {tok.type} ({tok.value}) at {tok.line}:{tok.col}")
        if val and tok.value != val:
            raise SyntaxError(f"Expected {val}, got {tok.value} at {tok.line}:{tok.col}")
        self.pos += 1
        return tok

    def match(self, typ=None, val=None):
        tok = self.cur()
        if not tok:
            return False
        if typ and tok.type != typ:
            return False
        if val and tok.value != val:
            return False
        return True

    # ----------------------------
    # Main parse loop
    # ----------------------------
    def parse(self):
        stmts = []
        while self.cur():
            stmts.append(self.parse_stmt())
        return stmts

    # ----------------------------
    # Statements
    # ----------------------------
    def parse_stmt(self):
        if self.match("KEYWORD", "give"):
            self.eat("KEYWORD", "give")
            expr = self.parse_expr()
            parts = [expr]
            while self.match("PUNC", ","):
                self.eat("PUNC", ",")
                parts.append(self.parse_expr())
            expr_fold = parts[0]
            for p in parts[1:]:
                expr_fold = BinOp(expr_fold, "+", p)
            return Print(expr_fold)

        if self.match("KEYWORD", "ask"):
            self.eat("KEYWORD", "ask")
            prompt = None
            if self.match("STRING"):
                prompt = String(self.eat("STRING").value)
            if self.match("OP", "->"):
                self.eat("OP", "->")
                name = self.eat("ID").value
                return Assign(name, Input(prompt))
            return Input(prompt)

        if self.match("KEYWORD", "func"):
            return self.parse_func()
        if self.match("KEYWORD", "class"):
            return self.parse_class()
        if self.match("KEYWORD", "if"):
            return self.parse_if()
        if self.match("KEYWORD", "loop") or self.match("KEYWORD", "repeat"):
            return self.parse_loop()

        # control flow keywords
        if self.match("KEYWORD", "break"):
            self.eat("KEYWORD", "break")
            return Break()
        if self.match("KEYWORD", "continue"):
            self.eat("KEYWORD", "continue")
            return Continue()
        if self.match("KEYWORD", "return") or self.match("KEYWORD", "ret"):
            self.eat(self.cur().type, self.cur().value)
            val = None
            if not self.match("PUNC", "}") and not self.match(None, None):
                # attempt to parse an expression unless block end or EOF
                try:
                    val = self.parse_expr()
                except SyntaxError:
                    val = None
            return Return(val)

        if self.match("KEYWORD", "try"):
            self.eat("KEYWORD", "try")
            tryb = self.parse_block()
            self.eat("KEYWORD", "catch")
            catchb = self.parse_block()
            finallyb = None
            if self.match("KEYWORD", "finally"):
                self.eat("KEYWORD", "finally")
                finallyb = self.parse_block()
            return TryCatch(tryb, catchb, finallyb)
        if self.match("KEYWORD", "aik"):
            self.eat("KEYWORD", "aik")
            # aik @ { "prompt" }
            if self.match("OP", "@"):
                self.eat("OP", "@")
            self.eat("PUNC", "{")
            s = self.eat("STRING").value
            self.eat("PUNC", "}")
            return AI(s)

        return self.parse_assign_or_expr()

    # ----------------------------
    # Block of statements
    # ----------------------------
    def parse_block(self):
        self.eat("PUNC", "{")
        stmts = []
        while not self.match("PUNC", "}"):
            stmts.append(self.parse_stmt())
        self.eat("PUNC", "}")
        return stmts

    # ----------------------------
    # Function
    # ----------------------------
    def parse_func(self):
        self.eat("KEYWORD", "func")
        name = self.eat("ID").value
        self.eat("PUNC", "(")
        params = []
        if not self.match("PUNC", ")"):
            while True:
                params.append(self.eat("ID").value)
                if self.match("PUNC", ")"):
                    break
                self.eat("PUNC", ",")
        self.eat("PUNC", ")")
        is_async = False
        if self.match("KEYWORD", "async"):
            is_async = True
            self.eat("KEYWORD", "async")
        if self.match("OP", "->"):
            self.eat("OP", "->")
            single = self.parse_expr()
            return FuncDef(name, params, body=None, single=single, is_async=is_async)
        body = self.parse_block()
        return FuncDef(name, params, body=body, single=None, is_async=is_async)

    # ----------------------------
    # Class
    # ----------------------------
    def parse_class(self):
        self.eat("KEYWORD", "class")
        name = self.eat("ID").value
        parent = None
        if self.match("OP", ":"):
            self.eat("OP", ":")
            parent = self.eat("ID").value
        body = self.parse_block()
        return ClassDef(name, body, parent)

    # ----------------------------
    # If-Else
    # ----------------------------
    def parse_if(self):
        self.eat("KEYWORD", "if")
        cond = self.parse_expr()
        if self.match("OP", "->"):
            self.eat("OP", "->")
            stmt = self.parse_stmt()
            body = [stmt]
        else:
            body = self.parse_block()
        orelse = []
        if self.match("KEYWORD", "else"):
            self.eat("KEYWORD", "else")
            if self.match("OP", "->"):
                self.eat("OP", "->")
                orelse = [self.parse_stmt()]
            else:
                orelse = self.parse_block()
        return If(cond, body, orelse)

    # ----------------------------
    # Loop / Repeat
    # ----------------------------
    def parse_loop(self):
        if self.match("KEYWORD", "loop"):
            self.eat("KEYWORD", "loop")
            var = self.eat("ID").value

            if self.match("KEYWORD", "in"):
                self.eat("KEYWORD", "in")
                start = self.parse_expr()
                # range loop
                if self.match("OP", ".."):
                    self.eat("OP", "..")
                    end = self.parse_expr()
                    step = None
                    if self.match("PUNC", ","):
                        self.eat("PUNC", ",")
                        step = self.parse_expr()
                    body = self.parse_block() if not self.match("OP", "->") else [self.parse_stmt()]
                    return ForLoop(var, start, end, step, body, foreach=False)
                else:
                    # for-each loop
                    body = self.parse_block() if not self.match("OP", "->") else [self.parse_stmt()]
                    return ForLoop(var, start, None, None, body, foreach=True)

            elif self.match("OP", "="):
                self.eat("OP", "=")
                start = self.parse_expr()
                if self.match("OP", ".."):
                    self.eat("OP", "..")
                    end = self.parse_expr()
                    step = None
                    if self.match("PUNC", ","):
                        self.eat("PUNC", ",")
                        step = self.parse_expr()
                    body = self.parse_block() if not self.match("OP", "->") else [self.parse_stmt()]
                    return ForLoop(var, start, end, step, body, foreach=False)
                else:
                    raise SyntaxError("Expected '..' in loop range after '='")
            else:
                raise SyntaxError("Expected 'in' or '=' after loop variable")

        elif self.match("KEYWORD", "repeat"):
            self.eat("KEYWORD", "repeat")
            cond = self.parse_expr()
            body = self.parse_block() if not self.match("OP", "->") else [self.parse_stmt()]
            return Repeat(cond, body)

        else:
            raise SyntaxError("Invalid loop syntax")

    # ----------------------------
    # Assignment / Expression
    # ----------------------------
    def parse_assign_or_expr(self):
        if self.match("ID"):
            name = self.eat("ID").value
            if self.match("OP", ":"):
                self.eat("OP", ":")
                ann = self.eat("ID").value
                if self.match("OP", "="):
                    self.eat("OP", "=")
                    expr = self.parse_expr()
                    return Assign(name, expr)
                return Assign(name, Number("0"))
            if self.match("OP", "="):
                self.eat("OP", "=")
                expr = self.parse_expr()
                return Assign(name, expr)
            node = Var(name)
            while self.match("PUNC", "."):
                self.eat("PUNC", ".")
                attr = self.eat("ID").value
                node = AttrAccess(node, attr)
            if self.match("PUNC", "("):
                self.eat("PUNC", "(")
                args = []
                if not self.match("PUNC", ")"):
                    while True:
                        args.append(self.parse_expr())
                        if self.match("PUNC", ")"):
                            break
                        self.eat("PUNC", ",")
                self.eat("PUNC", ")")
                return FuncCall(node, args)
            return node
        return self.parse_expr()

    # ----------------------------
    # Expressions (precedence)
    # ----------------------------
    def parse_expr(self):
        return self.parse_pipeline()

    def parse_pipeline(self):
        left = self.parse_logic()
        while self.match("OP", "|>"):
            self.eat("OP", "|>")
            right = self.parse_logic()
            left = BinOp(left, "|>", right)
        return left

    def parse_logic(self):
        left = self.parse_cmp()
        while self.match("OP", "&&") or self.match("OP", "||"):
            op = self.eat("OP").value
            right = self.parse_cmp()
            left = BinOp(left, op, right)
        return left

    def parse_cmp(self):
        left = self.parse_add()
        while self.match("OP") and self.cur().value in ("==", "!=", "<", ">", "<=", ">="):
            op = self.eat("OP").value
            right = self.parse_add()
            left = BinOp(left, op, right)
        return left

    def parse_add(self):
        left = self.parse_mul()
        while self.match("OP") and self.cur().value in ("+", "-"):
            op = self.eat("OP").value
            right = self.parse_mul()
            left = BinOp(left, op, right)
        return left

    def parse_mul(self):
        left = self.parse_unary()
        while self.match("OP") and self.cur().value in ("*", "/", "%"):
            op = self.eat("OP").value
            right = self.parse_unary()
            left = BinOp(left, op, right)
        return left

    def parse_unary(self):
        if self.match("OP") and self.cur().value in ("-", "!", "+"):
            op = self.eat("OP").value
            node = self.parse_unary()
            return BinOp(Number("0") if op == "-" else node, op, node)
        return self.parse_primary()

    def parse_primary(self):
        # Added: handle `ask` as an expression here (so `x = ask "prompt"` works)
        if self.match("KEYWORD", "ask"):
            self.eat("KEYWORD", "ask")
            prompt = None
            if self.match("STRING"):
                prompt = String(self.eat("STRING").value)
            # return Input node which can be used as expression or used via -> assignment form in parse_stmt
            return Input(prompt)

        if self.match("NUMBER"):
            return Number(self.eat("NUMBER").value)
        if self.match("STRING"):
            return String(self.eat("STRING").value)
        if self.match("KEYWORD") and self.cur().value in ("true", "false"):
            return Boolean(self.eat("KEYWORD").value)
        if self.match("PUNC", "["):
            self.eat("PUNC", "[")
            items = []
            if not self.match("PUNC", "]"):
                while True:
                    items.append(self.parse_expr())
                    if self.match("PUNC", "]"):
                        break
                    self.eat("PUNC", ",")
            self.eat("PUNC", "]")
            return ListLiteral(items)
        if self.match("PUNC", "{"):
            self.eat("PUNC", "{")
            pairs = []
            if not self.match("PUNC", "}"):
                while True:
                    keynode = self.parse_expr()
                    self.eat("OP", ":")
                    valnode = self.parse_expr()
                    pairs.append((keynode, valnode))
                    if self.match("PUNC", "}"):
                        break
                    self.eat("PUNC", ",")
            self.eat("PUNC", "}")
            return DictLiteral(pairs)
        if self.match("PUNC", "("):
            self.eat("PUNC", "(")
            node = self.parse_expr()
            self.eat("PUNC", ")")
            return node
        if self.match("ID"):
            name = self.eat("ID").value
            node = Var(name)
            while self.match("PUNC", "."):
                self.eat("PUNC", ".")
                attr = self.eat("ID").value
                node = AttrAccess(node, attr)
            if self.match("PUNC", "("):
                self.eat("PUNC", "(")
                args = []
                if not self.match("PUNC", ")"):
                    while True:
                        args.append(self.parse_expr())
                        if self.match("PUNC", ")"):
                            break
                        self.eat("PUNC", ",")
                self.eat("PUNC", ")")
                return FuncCall(node, args)
            return node
        raise SyntaxError(f"Unexpected token: {self.cur()}")

import os

# ----------------------------
# Interpreter Environment
# ----------------------------
class Env:
    def __init__(self, parent=None):
        self.map = {}
        self.parent = parent

    def get(self, name):
        if isinstance(name, AttrAccess):
            obj = self.eval_node(name.obj)
            if isinstance(obj, UnikObject):
                return obj.get_attr(name.attr)
            raise NameError(f"Not an object for attribute access")
        if name in self.map:
            return self.map[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Variable '{name}' not defined")

    def set(self, name, val):
        self.map[name] = val

    def update(self, name, val):
        if name in self.map:
            self.map[name] = val
        elif self.parent:
            self.parent.update(name, val)
        else:
            self.map[name] = val

# ----------------------------
# Control flow exceptions
# ----------------------------
class BreakException(Exception): pass
class ContinueException(Exception): pass
class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

# ----------------------------
# Function & Object wrappers
# ----------------------------
class UnikFunction:
    def __init__(self, defnode, env):
        self.defnode = defnode
        self.env = env

    def call(self, args, interp):
        local = Env(self.env)
        # bind params
        for i, param in enumerate(self.defnode.params):
            val = interp.eval_node_in_env(args[i], interp.global_env) if i < len(args) else None
            local.set(param, val)
        try:
            if self.defnode.single is not None:
                return interp.eval_node_in_env(self.defnode.single, local)
            return interp.run_block(self.defnode.body, local)
        except ReturnException as r:
            return r.value

class UnikObject:
    def __init__(self, classname, fields=None, methods=None):
        self.classname = classname
        self.fields = fields or {}
        self.methods = methods or {}

    def get_attr(self, name):
        if name in self.fields: return self.fields[name]
        if name in self.methods: return self.methods[name]
        raise AttributeError(f"{self.classname} has no attribute {name}")

    def set_attr(self, name, val):
        self.fields[name] = val

# ----------------------------
# Interpreter
# ----------------------------
class Interpreter:
    def __init__(self):
        self.global_env = Env()
        self.cache_dir = ".unik_ai_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        self.register_builtins()

    def register_builtins(self):
        self.global_env.set("len", lambda x: len(x))
        # keep a 'give' alias to the built-in print for convenience
        self.global_env.set("print", lambda *a: print(*a))
        def _map(fn, lst):
            out = []
            for v in lst:
                out.append(fn.call([v] if not isinstance(v, (int, float)) else [v], self))
            return out
        def _filter(fn, lst):
            out = []
            for v in lst:
                res = fn.call([v] if not isinstance(v, (int, float)) else [v], self)
                if res: out.append(v)
            return out
        self.global_env.set("map", _map)
        self.global_env.set("filter", _filter)

    def run(self, nodes):
        result = None
        for n in nodes:
            result = self.eval_node(n)
        return result

    def run_block(self, block, env):
        res = None
        for st in block:
            try:
                res = self.eval_node_in_env(st, env)
            except ReturnException as r:
                # bubble up return to caller
                raise r
            except BreakException:
                # propagate to nearest loop
                raise
            except ContinueException:
                raise
        return res

    def eval_node(self, node):
        return self.eval_node_in_env(node, self.global_env)

    def eval_node_in_env(self, node, env):
        # ----------------------------
        # Basic nodes
        # ----------------------------
        if isinstance(node, Number): return node.value
        if isinstance(node, String): return node.value
        if isinstance(node, Boolean): return node.value
        if isinstance(node, Var): return env.get(node.name)
        if isinstance(node, Assign):
            val = self.eval_node_in_env(node.expr, env)
            env.set(node.name, val)
            return val

        # BinOp: support short-circuit for logical operators
        if isinstance(node, BinOp):
            op = node.op
            if op == "&&":
                l = self.eval_node_in_env(node.left, env)
                if not bool(l):
                    return False
                return bool(self.eval_node_in_env(node.right, env))
            if op == "||":
                l = self.eval_node_in_env(node.left, env)
                if bool(l):
                    return True
                return bool(self.eval_node_in_env(node.right, env))
            # non-short-circuit ops
            l = self.eval_node_in_env(node.left, env)
            r = self.eval_node_in_env(node.right, env)
            return self.apply_op(op, l, r)

        if isinstance(node, Print):
            v = self.eval_node_in_env(node.expr, env)
            # prefer 'give' semantics: print items concatenated with space if tuple-like
            print(v)
            return v
        if isinstance(node, Input):
            if node.prompt:
                prompt_val = self.eval_node_in_env(node.prompt, env)
                return input(str(prompt_val))
            return input()
        if isinstance(node, FuncDef):
            func = UnikFunction(node, env)
            env.set(node.name, func)
            return func
        if isinstance(node, FuncCall):
            callee = node.callee
            if isinstance(callee, Var):
                fn = env.get(callee.name)
                # builtin python-callable
                if callable(fn) and not isinstance(fn, UnikFunction):
                    args = [self.eval_node_in_env(a, env) for a in node.args]
                    return fn(*args)
                if isinstance(fn, UnikFunction):
                    return fn.call(node.args, self)
                raise TypeError(f"{callee.name} is not callable")
            elif isinstance(callee, AttrAccess):
                obj = self.eval_node_in_env(callee.obj, env)
                if isinstance(obj, UnikObject):
                    meth = obj.get_attr(callee.attr)
                    if isinstance(meth, UnikFunction):
                        return meth.call(node.args, self)
                    if callable(meth):
                        args = [self.eval_node_in_env(a, env) for a in node.args]
                        return meth(*args)
                raise TypeError("Attribute not callable")
            else:
                raise TypeError("Unsupported callee type")
        if isinstance(node, ClassDef):
            methods, fields = {}, {}
            for mem in node.body:
                if isinstance(mem, FuncDef):
                    methods[mem.name] = UnikFunction(mem, self.global_env)
                elif isinstance(mem, Assign):
                    fields[mem.name] = self.eval_node_in_env(mem.expr, self.global_env)
            def class_factory(*args):
                obj = UnikObject(node.name, fields.copy(), methods.copy())
                # support both 'init' and '__init__'
                init_name = "__init__" if "__init__" in obj.methods else "init"
                if init_name in obj.methods:
                    init_fn = obj.methods[init_name]
                    local = Env(self.global_env)
                    local.set("self", obj)
                    init_fn.call([a for a in args], self)
                return obj
            env.set(node.name, class_factory)
            return node
        if isinstance(node, If):
            cond = self.eval_node_in_env(node.cond, env)
            if cond:
                return self.run_block(node.body, Env(env))
            else:
                return self.run_block(node.orelse, Env(env))

        # ----------------------------
        # Loop & Repeat nodes
        # ----------------------------
        if isinstance(node, ForLoop):
            if node.foreach:
                iterable = self.eval_node_in_env(node.start, env)
                # accept iterables (list, tuple, str, range)
                for item in iterable:
                    loop_env = Env(env)
                    loop_env.set(node.var, item)
                    try:
                        for stmt in node.body:
                            self.eval_node_in_env(stmt, loop_env)
                    except ContinueException:
                        continue
                    except BreakException:
                        break
                    except ReturnException:
                        raise
            else:
                start = self.eval_node_in_env(node.start, env)
                end = self.eval_node_in_env(node.end, env)
                step = self.eval_node_in_env(node.step, env) if node.step else 1
                # handle numeric iteration, inclusive end
                i = start
                # decide comparison operator based on step sign
                if step == 0:
                    raise ValueError("Loop step cannot be 0")
                if step > 0:
                    cond = lambda v: v <= end
                else:
                    cond = lambda v: v >= end
                while cond(i):
                    loop_env = Env(env)
                    loop_env.set(node.var, i)
                    try:
                        for stmt in node.body:
                            self.eval_node_in_env(stmt, loop_env)
                    except ContinueException:
                        i += step
                        continue
                    except BreakException:
                        break
                    except ReturnException:
                        raise
                    i += step
            return None

        if isinstance(node, Repeat):
            # repeat runs while condition true (spec ambiguous) - implement as while cond: body
            while self.eval_node_in_env(node.cond, env):
                try:
                    self.run_block(node.body, Env(env))
                except ContinueException:
                    continue
                except BreakException:
                    break
                except ReturnException:
                    raise
            return None

        # ----------------------------
        # Control flow nodes
        # ----------------------------
        if isinstance(node, Break):
            raise BreakException()
        if isinstance(node, Continue):
            raise ContinueException()
        if isinstance(node, Return):
            val = self.eval_node_in_env(node.val, env) if node.val is not None else None
            raise ReturnException(val)

        # ----------------------------
        # Literals / Attributes / AI stub
        # ----------------------------
        if isinstance(node, ListLiteral):
            return [self.eval_node_in_env(it, env) for it in node.items]
        if isinstance(node, DictLiteral):
            return {self.eval_node_in_env(k, env): self.eval_node_in_env(v, env) for k, v in node.pairs}
        if isinstance(node, AttrAccess):
            base = self.eval_node_in_env(node.obj, env)
            if isinstance(base, UnikObject):
                return base.get_attr(node.attr)
            if isinstance(base, dict):
                return base.get(node.attr)
            raise AttributeError("Attribute access on non-object")
        if isinstance(node, AI):
            prompt = node.prompt
            key = f"ai_{abs(hash(prompt))}"
            cache_path = os.path.join(self.cache_dir, key + ".unik")
            if os.path.exists(cache_path):
                with open(cache_path,'r',encoding='utf8') as f: gen=f.read()
            else:
                low = prompt.lower()
                if "add" in low and "function" in low:
                    gen = 'func add(a, b) -> a + b\ngive add(x, y)\n'
                else:
                    gen = f'# AI GENERATED (stub): {prompt}\n'
                with open(cache_path,'w',encoding='utf8') as f:
                    f.write(gen)
            lex = Lexer(gen)
            toks = lex.tokenize(gen)
            parsed = Parser(toks).parse()
            return self.run(parsed)

        raise TypeError(f"Unimplemented node exec: {node}")

    # ----------------------------
    # Operators
    # ----------------------------
    def apply_op(self, op, l, r):
        if op == "+": return str(l) + str(r) if isinstance(l, str) or isinstance(r, str) else l + r
        if op == "-": return l - r
        if op == "*": return l * r
        if op == "/": return l / r
        if op == "%": return l % r
        if op == "==": return l == r
        if op == "!=": return l != r
        if op == "<": return l < r
        if op == "<=": return l <= r
        if op == ">": return l > r
        if op == ">=": return l >= r
        if op == "&&": return bool(l) and bool(r)
        if op == "||": return bool(l) or bool(r)
        if op == "|>":
            # pipeline: if right is Var (function name) or callable, call it
            if isinstance(r, Var):
                fn = self.global_env.get(r.name)
                if callable(fn): return fn(l)
            if callable(r): return r(l)
            return l
        raise SyntaxError(f"Unknown operator {op}")

# ----------------------------
# REPL & runner
# ----------------------------
def run_file(path):
    with open(path,'r',encoding='utf8') as f:
        code = f.read()
    lx = Lexer(code)
    toks = lx.tokenize(code)
    ast = Parser(toks).parse()
    interp = Interpreter()
    interp.run(ast)

def repl():
    interp = Interpreter()
    print("Welcome to Unik REPL (single-file runtime). Type 'exit' or '.exit' to quit. .load <file>")
    buffer = ""
    while True:
        try:
            line = input("unik> ")
        except EOFError:
            break
        if not line:
            continue
        if line.strip() in ("exit", ".exit"): break
        if line.startswith(".load"):
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                filename = parts[1].strip()
                if not os.path.exists(filename):
                    print(f"[Error] File '{filename}' not found")
                    continue
                run_file(filename)
            else:
                print("Usage: .load <filename>")
            continue
        # allow entering multiple statements separated by ';'
        try:
            code = line
            lx = Lexer(code)
            toks = lx.tokenize(code)
            ast = Parser(toks).parse()
            res = interp.run(ast)
        except Exception as e:
            print(f"[Error] {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        repl()
