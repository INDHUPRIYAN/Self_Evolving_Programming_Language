from sepl_interpreter.lexer import tokenize
from sepl_interpreter.ast_nodes import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def eat(self, token_type):
        tok = self.current_token()
        if tok and tok.type == token_type:
            self.pos += 1
            return tok
        else:
            raise RuntimeError(f"Expected {token_type}, got {tok}")

    def lookahead_type(self, n):
        if (self.pos + n) < len(self.tokens):
            return self.tokens[self.pos + n].type
        return None

    def parse(self):
        statements = []
        while self.pos < len(self.tokens):
            tok = self.current_token()

            if tok.type == 'ID' and tok.value == 'main':
                self.eat('ID')
                self.eat('COLON')

            elif tok.type == 'ID' and tok.value == 'give':
                statements.append(self.parse_output())

            elif tok.type == 'ID' and tok.value == 'if':
                statements.append(self.parse_if())

            elif self.lookahead_type(1) == 'ASSIGN':
                statements.append(self.parse_assignment())
            
            elif tok.type == 'NUMBER':
                left = NumberNode(float(self.eat('NUMBER').value))

            else:
                self.pos += 1

        return ProgramNode(statements)

    def parse_assignment(self):
        var_name = self.eat('ID').value
        self.eat('ASSIGN')
        expr = self.parse_expression()

        if self.current_token() and self.current_token().type == 'ARROW':
            self.eat('ARROW')
            self.eat('ID')

        return AssignmentNode(var_name, expr)

    def parse_output(self):
        self.eat('ID')  # give
        expr = self.parse_expression()
        return OutputNode(expr)

    def parse_expression(self):
        tok = self.current_token()
        if tok.type == 'ID' and tok.value == 'ask':
            self.eat('ID')
            prompt = ''
            if self.current_token() and self.current_token().type == 'STRING':
                prompt = self.eat('STRING').value.strip('"')
            left = InputNode(prompt)

        elif tok.type == 'STRING':
            left = StringNode(self.eat('STRING').value.strip('"'))

        elif tok.type == 'NUMBER':
            left = NumberNode(float(self.eat('NUMBER').value))

        elif tok.type == 'ID':
            left = VarNode(self.eat('ID').value)

        else:
            raise RuntimeError(f"Unexpected token in expression: {tok}")

        if self.current_token() and self.current_token().type in (
            'PLUS', 'MINUS', 'MUL', 'DIV', 'MOD', 'EQ', 'NEQ', 'LT', 'LTE', 'GT', 'GTE', 'AND', 'OR'):
            op_tok = self.eat(self.current_token().type)
            right = self.parse_expression()
            return BinaryOpNode(left, op_tok.value, right)

        return left

    def parse_if(self):
        self.eat('ID')  # if
        self.eat('COLON')
        condition = self.parse_expression()
        true_block = self.parse_block()

        elif_blocks = []
        else_block = None

        while self.current_token() and self.current_token().type == 'ID' and self.current_token().value == 'elif':
            self.eat('ID')
            self.eat('COLON')
            elif_cond = self.parse_expression()
            elif_block = self.parse_block()
            elif_blocks.append((elif_cond, elif_block))

        if self.current_token() and self.current_token().type == 'ID' and self.current_token().value == 'else':
            self.eat('ID')
            else_block = self.parse_block()

        return IfNode(condition, true_block, elif_blocks, else_block)

    def parse_block(self):
        statements = []
        while self.current_token():
            tok = self.current_token()
            if tok.type == 'ID' and tok.value in ('give',):
                statements.append(self.parse_output())
            elif tok.type == 'ID' and self.lookahead_type(1) == 'ASSIGN':
                statements.append(self.parse_assignment())
            elif tok.type == 'ID' and tok.value == 'if':
                statements.append(self.parse_if())
            elif tok.type == 'ID' and tok.value in ('elif', 'else', 'main'):
                break
            else:
                self.pos += 1
        return statements
