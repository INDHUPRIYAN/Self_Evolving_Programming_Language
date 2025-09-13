import re

TOKEN_SPECIFICATION = [
    ('NUMBER',   r'\d+(\.\d+)?'),                # Integers or floats
    ('EQ',       r'=='),                        # Equal operator
    ('NEQ',      r'!='),                        # Not equal operator
    ('LTE',      r'<='),                        # Less than or equal
    ('GTE',      r'>='),                        # Greater than or equal
    ('LT',       r'<'),                         # Less than
    ('GT',       r'>'),                         # Greater than
    ('AND',      r'\band\b'),                   # Logical AND
    ('OR',       r'\bor\b'),                    # Logical OR
    ('ASSIGN',   r'='),                         # Assignment
    ('ARROW',    r'->'),                        # Arrow for ask
    ('COLON',    r':'),                         # Colon
    ('ID',       r'[A-Za-z_][A-Za-z0-9_]*'),    # Identifiers
    ('STRING',   r'"[^"]*"'),                   # String literals
    ('PLUS',     r'\+'),                        # Plus operator
    ('MINUS',    r'-'),                         # Minus
    ('MUL',      r'\*'),                        # Multiply
    ('DIV',      r'/'),                         # Divide
    ('MOD',      r'%'),                         # Modulo
    ('NEWLINE',  r'\n'),                        # Line breaks
    ('SKIP',     r'[ \t]+'),                    # Skip spaces/tabs
    ('MISMATCH', r'.'),                         # Anything else
]

token_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in TOKEN_SPECIFICATION)

class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"

def tokenize(code):
    tokens = []
    for mo in re.finditer(token_regex, code):
        kind = mo.lastgroup
        value = mo.group()

        if kind == 'NUMBER':
            value = float(value) if '.' in value else int(value)
        elif kind in ('ID', 'STRING'):
            value = value
        elif kind == 'SKIP' or kind == 'NEWLINE':
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'Unexpected character: {value}')

        tokens.append(Token(kind, value))

    return tokens
