# src/lexer/lexer.py
import re
from typing import List, Optional

class Token:
    def __init__(self, typ: str, value: str, line: int, column: int):
        self.type = typ
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"{self.type}({self.value!r}) at {self.line}:{self.column}"


class Lexer:
    """
    Release-ready Lexer for Unik language.

    Usage:
        # Either:
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        # Or:
        lexer = Lexer()
        tokens = lexer.tokenize(code)
    """

    # Keywords in Unik (expand as needed)
    KEYWORDS = {
        # core
        "func", "class", "trait", "init", "self",
        "if", "else", "alter", "match", "case",
        "loop", "repeat", "break", "return", "ret",
        "try", "catch", "finally",
        "give", "ask", "askfile", "givefile",
        "true", "false",
        # concurrency / async
        "task", "run", "async", "await", "wait",
        # testing
        "test",
        # ai
        "aik",
        # module / pkg
        "import", "from", "as",
    }

    # Token specification order matters (longer operators first)
    TOKEN_SPEC = [
        # Strings (supports escapes)
        ("STRING", r'"(?:\\.|[^"\\])*"'),
        # Numbers: integers and floats
        ("NUMBER", r'\d+\.\d+|\d+'),
        # Multi-char operators first
        ("OP", r'\|\>|\.\.|->|==|!=|<=|>=|\+=|-=|\*=|/=|%=|\+\+|--|&&|\|\||::|\:\?'),
        # Single-char operators
        ("OP", r'[+\-*/%<>=!?:@\$]'),
        # Identifiers
        ("ID", r'[A-Za-z_][A-Za-z0-9_]*'),
        # Punctuation (now includes dot!)
        ("PUNC", r'[\(\)\{\}\[\],;<>.]'),
        # Newline
        ("NEWLINE", r'\n'),
        # Spaces and tabs
        ("SKIP", r'[ \t\r]+'),
        # Comments
        ("COMMENT", r'\#.*'),
        # Anything else is mismatch
        ("MISMATCH", r'.'),
    ]


    def __init__(self, code: Optional[str] = None):
        self.code = code
        # Build combined regex
        parts = []
        for i, (name, pattern) in enumerate(self.TOKEN_SPEC):
            parts.append(f'(?P<{name}{i}>{pattern})')
        self.master_regex = re.compile('|'.join(parts))
        # Build reverse map to extract token type by match lastgroup prefix
        self._group_to_type = {}
        for i, (name, _) in enumerate(self.TOKEN_SPEC):
            self._group_to_type[f"{name}{i}"] = name

    def tokenize(self, code: Optional[str] = None) -> List[Token]:
        """
        Convert code (string) -> list of Token.
        If code provided to constructor, you can call tokenize() without arg.
        """
        if code is None:
            if self.code is None:
                raise ValueError("No code provided to lexer")
            code = self.code

        pos = 0
        line = 1
        col = 1
        tokens: List[Token] = []
        m = self.master_regex.match
        length = len(code)

        while pos < length:
            match = m(code, pos)
            if not match:
                raise SyntaxError(f"Unexpected character {code[pos]!r} at {line}:{col}")
            group_name = match.lastgroup
            raw_val = match.group(group_name)
            tok_type = self._group_to_type[group_name]

            # Advance pos tracking newlines for column/line calculation
            if tok_type == "NEWLINE":
                pos = match.end()
                line += 1
                col = 1
                continue

            if tok_type == "SKIP" or tok_type == "COMMENT":
                # skip whitespace/comments
                # but update pos/col (comments count as remained on same line)
                newlines = raw_val.count("\n")
                if newlines > 0:
                    line += newlines
                    # after newline, set col to chars after last newline (rare in SKIP)
                    col = len(raw_val.rsplit("\n", 1)[-1]) + 1
                else:
                    col += len(raw_val)
                pos = match.end()
                continue

            if tok_type == "MISMATCH":
                raise SyntaxError(f"Unexpected token {raw_val!r} at {line}:{col}")

            # Map ID to KEYWORD if necessary
            if tok_type == "ID" and raw_val in self.KEYWORDS:
                tok_type = "KEYWORD"

            # Normalize some operator tokens (because we split OP patterns across groups)
            # Use the exact raw_val as operator value.
            token = Token(tok_type, raw_val, line, col)
            tokens.append(token)

            # advance
            consumed = len(raw_val)
            pos = match.end()
            # update line/col in a robust way
            if "\n" in raw_val:
                nl_count = raw_val.count("\n")
                line += nl_count
                col = len(raw_val.rsplit("\n", 1)[-1]) + 1
            else:
                col += consumed

        return tokens


# ---------------- Quick self-test ----------------
if __name__ == "__main__":
    sample = r'''
# Simple arithmetic
x = 10
y: int = 5

z = x + y
give "Sum: ", z    # prints sum

# ask forms
ask "Enter name: " -> name
name2 = ask

# function
func square(n) -> n * n

# class
class Person {
    init(name, age) { self.name = name; self.age = age }
    func greet() { give "Hi ", self.name }
}

# aik inline
aik @{"Write a function add(a,b) that returns a+b"}

# pipeline example
nums = [1,2,3]
result = nums |> map(x => x * 2) |> filter(x => x > 2)

# async/task
func fetchData() async { wait 1s; ret "done" }
task t1 { loop i in 1..3 { give i } }
'''
lx = Lexer(sample)
toks = lx.tokenize()
for t in toks:
    print(t)
