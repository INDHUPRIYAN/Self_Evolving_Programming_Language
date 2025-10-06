# ----------------------------
# AST Nodes
# ----------------------------
class Number:      
    def __init__(self,v): self.value=v
class String:      
    def __init__(self,v): self.value=v
class Boolean:     
    def __init__(self,v): self.value=v
class Var:         
    def __init__(self,n): self.name=n
class Assign:      
    def __init__(self,n,v): self.name=n; self.value=v
class BinOp:       
    def __init__(self,l,o,r): self.left=l; self.op=o; self.right=r
class UnaryOp:     
    def __init__(self,op,expr): self.op=op; self.expr=expr
class Print:       
    def __init__(self,expr): self.expr=expr
class Input:      
    def __init__(self,prompt=None): self.prompt=prompt
class If:          
    def __init__(self,c,b,o): self.cond=c; self.body=b; self.orelse=o
class ForLoop:     
    def __init__(self,var,s,e,step,body,foreach=False): self.var=var; self.start=s; self.end=e; self.step=step; self.body=body; self.foreach=foreach
class Repeat:      
    def __init__(self,cond,body): self.cond=cond; self.body=body

# ----------------------------
# Lexer
# ----------------------------
import re
class Token:
    def __init__(self,type,value): self.type=type; self.value=value
    def __repr__(self): return f"{self.type}:{self.value}"

class Lexer:
    def __init__(self,src): self.src=src; self.pos=0
    def tokenize(self):
        tokens=[]
        token_spec = [
            ('NUMBER',   r'\d+(\.\d+)?'), 
            ('STRING',   r'"[^"]*"'),
            ('ID',       r'[A-Za-z_]\w*'),
            ('OP',       r'==|!=|<=|>=|\+\+|--|[-+*/%<>=!|&]+'),
            ('PUNC',     r'[\(\)\{\}\[\],:]'),
            ('NEWLINE',  r'\n'),
            ('SKIP',     r'[ \t]+'),
            ('MISMATCH', r'.')
        ]
        tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name,pattern in token_spec)
        for mo in re.finditer(tok_regex,self.src):
            kind = mo.lastgroup; val = mo.group()
            if kind=='NUMBER': tokens.append(Token('NUMBER',val))
            elif kind=='STRING': tokens.append(Token('STRING',val[1:-1]))
            elif kind=='ID': tokens.append(Token('ID',val))
            elif kind=='OP': tokens.append(Token('OP',val))
            elif kind=='PUNC': tokens.append(Token('PUNC',val))
            elif kind=='NEWLINE' or kind=='SKIP': continue
            else: raise SyntaxError(f"Unexpected char: {val}")
        return tokens

# ----------------------------
# Parser
# ----------------------------
class Parser:
    def __init__(self,tokens): self.tokens=tokens; self.pos=0
    def cur(self): return self.tokens[self.pos] if self.pos<len(self.tokens) else None
    def eat(self,typ=None,val=None):
        tok=self.cur()
        if not tok: raise SyntaxError("Unexpected end")
        if typ and tok.type!=typ: raise SyntaxError(f"Expected {typ} got {tok.type}")
        if val and tok.value!=val: raise SyntaxError(f"Expected {val} got {tok.value}")
        self.pos+=1; return tok
    def match(self,typ=None,val=None):
        tok=self.cur()
        if not tok: return False
        if typ and tok.type!=typ: return False
        if val and tok.value!=val: return False
        return True

    # ----------------------------
    # Statements
    # ----------------------------
    def parse(self):
        stmts=[]
        while self.cur(): stmts.append(self.parse_stmt())
        return stmts

    def parse_stmt(self):
        tok=self.cur()
        # Print: give expr
        if self.match("ID") and tok.value=="give":
            self.eat("ID"); expr=self.parse_expr(); return Print(expr)
        # Assignment: x = expr
        if self.match("ID") and self.pos+1<len(self.tokens) and self.tokens[self.pos+1].value=="=":
            name=self.eat("ID").value; self.eat("OP","="); expr=self.parse_expr(); return Assign(name,expr)
        # Input: ask "prompt"
        if self.match("ID") and tok.value=="ask":
            self.eat("ID"); prompt=None
            if self.match("STRING"): prompt=String(self.eat("STRING").value)
            return Input(prompt)
        # If-Else
        if self.match("ID") and tok.value=="if":
            self.eat("ID"); cond=self.parse_expr(); body=[self.parse_stmt()]; orelse=[]
            if self.match("ID") and self.cur().value=="else": self.eat("ID"); orelse=[self.parse_stmt()]
            return If(cond,body,orelse)
        # Loop: loop i in start..end
        if self.match("ID") and tok.value=="loop":
            self.eat("ID"); var=self.eat("ID").value; self.eat("ID","in"); start=self.parse_expr(); self.eat("OP",".."); end=self.parse_expr(); body=[self.parse_stmt()]; return ForLoop(var,start,end,None,body)
        # Repeat: repeat cond
        if self.match("ID") and tok.value=="repeat":
            self.eat("ID"); cond=self.parse_expr(); body=[self.parse_stmt()]; return Repeat(cond,body)
        # Default: expression
        return self.parse_expr()

    # ----------------------------
    # Expressions (with operator precedence)
    # ----------------------------
    def parse_expr(self): return self.parse_logic()
    def parse_logic(self):
        left=self.parse_cmp()
        while self.match("OP") and self.cur().value in ("&&","||"):
            op=self.eat("OP").value
            right=self.parse_cmp()
            left=BinOp(left,op,right)
        return left
    def parse_cmp(self):
        left=self.parse_add()
        while self.match("OP") and self.cur().value in ("==","!=","<",">","<=",">="):
            op=self.eat("OP").value
            right=self.parse_add()
            left=BinOp(left,op,right)
        return left
    def parse_add(self):
        left=self.parse_mul()
        while self.match("OP") and self.cur().value in ("+","-"):
            op=self.eat("OP").value
            right=self.parse_mul()
            left=BinOp(left,op,right)
        return left
    def parse_mul(self):
        left=self.parse_unary()
        while self.match("OP") and self.cur().value in ("*","/","%"):
            op=self.eat("OP").value
            right=self.parse_unary()
            left=BinOp(left,op,right)
        return left
    def parse_unary(self):
        if self.match("OP") and self.cur().value in ("-","!","+"):
            op=self.eat("OP").value
            node=self.parse_unary()
            return UnaryOp(op,node)
        return self.parse_primary()
    def parse_primary(self):
        if self.match("NUMBER"): return Number(self.eat("NUMBER").value)
        if self.match("STRING"): return String(self.eat("STRING").value)
        if self.match("ID"): return Var(self.eat("ID").value)
        if self.match("PUNC","("):
            self.eat("PUNC","("); node=self.parse_expr(); self.eat("PUNC",")"); return node
        raise SyntaxError(f"Unexpected token: {self.cur()}")

# ----------------------------
# Interpreter
# ----------------------------
class Environment:
    def __init__(self,parent=None): self.vars={}; self.parent=parent
    def get(self,name):
        if name in self.vars: return self.vars[name]
        elif self.parent: return self.parent.get(name)
        else: raise NameError(f"{name} not defined")
    def define(self,name,value): self.vars[name]=value

class Interpreter:
    def __init__(self): self.env=Environment()
    def run(self,stmts):
        for stmt in stmts: self.eval(stmt)
    def eval(self,node):
        if isinstance(node,Number): return float(node.value)
        if isinstance(node,String): return node.value
        if isinstance(node,Var): return self.env.get(node.name)
        if isinstance(node,Assign):
            val=self.eval(node.value); self.env.define(node.name,val); return val
        if isinstance(node,Print):
            val=self.eval(node.expr); print(val); return val
        if isinstance(node,Input):
            prompt=self.eval(node.prompt) if node.prompt else ""; return input(prompt)
        if isinstance(node,If):
            if self.eval(node.cond): self.run(node.body)
            else: self.run(node.orelse)
        if isinstance(node,ForLoop):
            start=int(self.eval(node.start)); end=int(self.eval(node.end))
            for i in range(start,end+1): self.env.define(node.var,i); self.run(node.body)
        if isinstance(node,Repeat):
            while self.eval(node.cond): self.run(node.body)
        if isinstance(node,BinOp):
            l=self.eval(node.left); r=self.eval(node.right); op=node.op
            if op=="+": return l+r
            if op=="-": return l-r
            if op=="*": return l*r
            if op=="/": return l/r
            if op=="%": return l%r
            if op==">": return l>r
            if op==">=": return l>=r
            if op=="<": return l<r
            if op=="<=": return l<=r
            if op=="==": return l==r
            if op=="!=": return l!=r
            if op=="&&": return l and r
            if op=="||": return l or r
        if isinstance(node,UnaryOp):
            val=self.eval(node.expr)
            if node.op=="-": return -val
            if node.op=="+": return +val
            if node.op=="!": return not val

# ----------------------------
# REPL
# ----------------------------
def repl():
    interp = Interpreter()
    print("Unik REPL. Type 'exit' to quit.")
    while True:
        try:
            src = input(">>> ").strip()
            if src in ("exit","quit"): break
            if src.startswith(".load "):
                filename = src[6:].strip()
                with open(filename,"r") as f: code=f.read()
                tokens = Lexer(code).tokenize()
                stmts = Parser(tokens).parse()
                interp.run(stmts)
                continue
            tokens = Lexer(src).tokenize()
            stmts = Parser(tokens).parse()
            interp.run(stmts)
        except Exception as e:
            print(f"Error: {e}")

# ----------------------------
# Start REPL
# ----------------------------
if __name__=="__main__":
    repl()
