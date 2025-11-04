# unik_part1.py
import re
import traceback
import asyncio
import json
import os

# -------------------------
# LEXER / TOKENIZER
# -------------------------
TOKEN_SPEC = [
    ("NUMBER", r'\d+'),
    ("STRING", r'"[^"]*"'),
    ("ASSIGN", r'->|='),  # assignment or arrow
    ("ID", r'[A-Za-z_][A-Za-z0-9_]*'),
    ("REPEAT", r'repeat'),
    ("TIMES", r'times'),
    ("TASK", r'task'),
    ("AWAIT", r'await'),
    ("LBRACE", r'\{'),
    ("RBRACE", r'\}'),
    ("PLUS", r'\+'),
    ("MINUS", r'-'),
    ("MUL", r'\*'),
    ("DIV", r'/'),
    ("MOD", r'%'),
    ("POW", r'\*\*'),
    ("LPAREN", r'\('),
    ("RPAREN", r'\)'),
    ("COMMA", r','),
    ("SKIP", r'[ \t]+'),
    ("NEWLINE", r'\n'),
]

TOKEN_REGEX = '|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPEC)

class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value
    def __repr__(self):
        return f"<{self.type}:{self.value}>"

def lex(code):
    tokens = []
    for mo in re.finditer(TOKEN_REGEX, code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == "NUMBER":
            value = int(value)
        elif kind == "STRING":
            value = value[1:-1]
        elif kind in ("SKIP", "NEWLINE"):
            continue
        tokens.append(Token(kind, value))
    return tokens

# -------------------------
# AST NODES
# -------------------------
class ASTNode: pass

class Number(ASTNode):
    def __init__(self, value): self.value = value
class String(ASTNode):
    def __init__(self, value): self.value = value
class Var(ASTNode):
    def __init__(self, name): self.name = name
class Assign(ASTNode):
    def __init__(self, var, expr): self.var = var; self.expr = expr
class Give(ASTNode):
    def __init__(self, expr): self.expr = expr
class Ask(ASTNode):
    def __init__(self, prompt, var): self.prompt = prompt; self.var = var
class Repeat(ASTNode):
    def __init__(self, count, block): self.count = count; self.block = block
class BinOp(ASTNode):
    def __init__(self, left, op, right): self.left = left; self.op_sym = op; self.right = right
class TaskNode(ASTNode):
    def __init__(self, block): self.block = block
class AwaitNode(ASTNode):
    def __init__(self, var): self.var = var

# -------------------------
# PARSER
# -------------------------
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
    def current(self):
        if self.pos < len(self.tokens): return self.tokens[self.pos]
        return None
    def eat(self, type_=None):
        tok = self.current()
        if tok is None: return None
        if type_ and tok.type != type_: raise SyntaxError(f"Expected {type_}, got {tok.type}")
        self.pos += 1
        return tok
    def parse(self):
        nodes = []
        while self.current() is not None:
            nodes.append(self.statement())
        return nodes
    def statement(self):
        tok = self.current()
        if tok.type == "ID" and tok.value == "give":
            self.eat("ID")
            expr = self.expr()
            return Give(expr)
        elif tok.type == "ID" and tok.value == "ask":
            self.eat("ID")
            prompt = self.eat("STRING").value
            self.eat("ASSIGN")
            var = self.eat("ID").value
            return Ask(prompt, var)
        elif tok.type == "REPEAT":
            self.eat("REPEAT")
            count = int(self.eat("NUMBER").value)
            self.eat("TIMES")
            self.eat("LBRACE")
            block = []
            while self.current().type != "RBRACE":
                block.append(self.statement())
            self.eat("RBRACE")
            return Repeat(count, block)
        elif tok.type == "TASK":
            self.eat("TASK")
            self.eat("LBRACE")
            block = []
            while self.current().type != "RBRACE":
                block.append(self.statement())
            self.eat("RBRACE")
            return TaskNode(block)
        elif tok.type == "AWAIT":
            self.eat("AWAIT")
            var = self.eat("ID").value
            return AwaitNode(var)
        elif tok.type == "ID":
            var_name = self.eat("ID").value
            self.eat("ASSIGN")
            expr = self.expr()
            return Assign(var_name, expr)
        else:
            raise SyntaxError(f"Unknown statement starting with {tok.value}")
    def expr(self):
        left = self.term()
        while self.current() and self.current().type in ("PLUS", "MINUS", "MUL", "DIV", "MOD", "POW"):
            op = self.eat().value
            right = self.term()
            left = BinOp(left, op, right)
        return left
    def term(self):
        tok = self.current()
        if tok.type == "NUMBER":
            self.eat("NUMBER")
            return Number(tok.value)
        elif tok.type == "STRING":
            self.eat("STRING")
            return String(tok.value)
        elif tok.type == "ID":
            self.eat("ID")
            return Var(tok.value)
        else:
            raise SyntaxError(f"Unexpected token {tok.type}")
