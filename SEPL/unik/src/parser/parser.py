# src/parser/parser.py
from src.ast.nodes import *
from collections import deque

class Parser:
    def __init__(self, tokens):
        self.tokens = deque(tokens)
        self.current = None
        self.next_token()

    def next_token(self):
        self.current = self.tokens.popleft() if self.tokens else None

    def match(self, kind, value=None):
        if self.current and self.current.type == kind and (value is None or self.current.value == value):
            tok = self.current
            self.next_token()
            return tok
        return None

    def expect(self, kind, value=None):
        tok = self.match(kind, value)
        if not tok:
            raise SyntaxError(f"Expected {kind} {value or ''}, got {self.current}")
        return tok

    # ---------- Entry ----------
    def parse(self):
        nodes = []
        while self.current:
            nodes.append(self.parse_stmt())
        return nodes

    # ---------- Statements ----------
    def parse_stmt(self):
        if self.match("KEYWORD", "give"):
            return self.parse_print()
        if self.match("KEYWORD", "ask"):
            return self.parse_input()
        if self.match("KEYWORD", "func"):
            return self.parse_funcdef()
        if self.match("KEYWORD", "class"):
            return self.parse_classdef()
        if self.match("KEYWORD", "if"):
            return self.parse_if()
        if self.match("KEYWORD", "loop"):
            return self.parse_for()
        if self.match("KEYWORD", "repeat"):
            return self.parse_repeat()
        if self.match("KEYWORD", "try"):
            return self.parse_trycatch()
        if self.match("KEYWORD", "alter"):
            return self.parse_alter()
        if self.match("KEYWORD", "aik"):
            return self.parse_ai()
        if self.match("KEYWORD", "ret"):
            val = self.parse_expr()
            return Return(val)
        if self.match("KEYWORD", "break"):
            return Break()
        # assignment / expression
        return self.parse_assign_or_expr()

    def parse_print(self):
        exprs = [self.parse_expr()]
        while self.match("PUNC", ","):
            exprs.append(self.parse_expr())
        # combine as BinOp with string concat
        node = exprs[0]
        for e in exprs[1:]:
            node = BinOp(node, "+", e)
        return Print(node)

    def parse_input(self):
        prompt = self.parse_expr()
        self.expect("OP", "->")
        name = self.expect("ID").value
        return Assign(name, Input(prompt))

    def parse_assign_or_expr(self):
        if self.current and self.current.type == "ID":
            name = self.current.value
            self.next_token()
            if self.match("OP", "="):
                expr = self.parse_expr()
                return Assign(name, expr)
            elif self.match("PUNC", "("):
                args = self.parse_arglist()
                return FuncCall(name, args)
            else:
                return Var(name)
        return self.parse_expr()

    # ---------- Expressions ----------
    def parse_expr(self):
        left = self.parse_term()
        while self.current and self.current.type == "OP" and self.current.value in ("+", "-", "==", "!=", "<", ">", "<=", ">="):
            op = self.current.value
            self.next_token()
            right = self.parse_term()
            left = BinOp(left, op, right)
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.current and self.current.type == "OP" and self.current.value in ("*", "/", "%"):
            op = self.current.value
            self.next_token()
            right = self.parse_factor()
            left = BinOp(left, op, right)
        return left

    def parse_factor(self):
        if self.current.type == "NUMBER":
            val = self.current.value
            self.next_token()
            return Number(val)
        if self.current.type == "STRING":
            val = self.current.value
            self.next_token()
            return String(val)
        if self.current.type == "ID":
            name = self.current.value
            self.next_token()
            if self.match("PUNC", "("):
                args = self.parse_arglist()
                return FuncCall(name, args)
            return Var(name)
        if self.match("PUNC", "("):
            expr = self.parse_expr()
            self.expect("PUNC", ")")
            return expr
        raise SyntaxError(f"Unexpected token {self.current}")

    def parse_arglist(self):
        args = []
        if not self.match("PUNC", ")"):
            while True:
                args.append(self.parse_expr())
                if self.match("PUNC", ")"): break
                self.expect("PUNC", ",")
        return args

    # ---------- Functions ----------
    def parse_funcdef(self):
        name = self.expect("ID").value
        self.expect("PUNC", "(")
        params = []
        if not self.match("PUNC", ")"):
            while True:
                params.append(self.expect("ID").value)
                if self.match("PUNC", ")"): break
                self.expect("PUNC", ",")
        if self.match("OP", "->"):
            expr = self.parse_expr()
            return FuncDef(name, params, single_line_expr=expr)
        body = self.parse_block()
        return FuncDef(name, params, body=body)

    def parse_classdef(self):
        name = self.expect("ID").value
        body = self.parse_block()
        return ClassDef(name, body)

    def parse_if(self):
        cond = self.parse_expr()
        body = self.parse_block()
        orelse = []
        if self.match("KEYWORD", "else"):
            orelse = self.parse_block()
        return If(cond, body, orelse)

    def parse_for(self):
        var = self.expect("ID").value
        self.expect("KEYWORD", "in")
        start = self.parse_expr()
        self.expect("OP", "..")
        end = self.parse_expr()
        body = self.parse_block()
        return ForLoop(var, start, end, Number(1), body)

    def parse_repeat(self):
        cond = self.parse_expr()
        body = self.parse_block()
        return Repeat(cond, body)

    def parse_trycatch(self):
        try_body = self.parse_block()
        self.expect("KEYWORD", "catch")
        catch_body = self.parse_block()
        finally_body = []
        if self.match("KEYWORD", "finally"):
            finally_body = self.parse_block()
        return TryCatch(try_body, catch_body, finally_body)

    def parse_alter(self):
        expr = self.parse_expr()
        cases = {}
        self.expect("PUNC", "{")
        while not self.match("PUNC", "}"):
            key = self.parse_expr()
            self.expect("OP", "->")
            val = self.parse_expr()
            cases[key] = val
            self.match("PUNC", ",")
        return AlterCase(expr, cases)

    def parse_ai(self):
        self.expect("OP", "@")
        self.expect("PUNC", "{")
        prompt = self.expect("STRING").value
        self.expect("PUNC", "}")
        return AI(prompt)

    def parse_block(self):
        self.expect("PUNC", "{")
        stmts = []
        while not self.match("PUNC", "}"):
            stmts.append(self.parse_stmt())
        return stmts
