import sys
from lexer.lexer import Lexer
from src.parser.parser import Parser
from src.interpreter.interpreter import Interpreter

class REPL:
    def __init__(self):
        self.lexer = Lexer()
        self.interpreter = Interpreter()

    def run(self):
        print("Welcome to Unik REPL (Release Ready)")
        print("Type 'exit' to quit, '.load filename.unik' to run a file.")
        while True:
            try:
                inp = input("unik> ")
                if inp.strip() == "exit": break
                elif inp.startswith(".load"):
                    fname = inp.split(" ")[1]
                    with open(fname) as f:
                        code = f.read()
                    tokens = self.lexer.tokenize(code)
                    parser = Parser(tokens)
                    ast_nodes = parser.parse()
                    self.interpreter.run(ast_nodes)
                else:
                    tokens = self.lexer.tokenize(inp)
                    parser = Parser(tokens)
                    ast_nodes = parser.parse()
                    self.interpreter.run(ast_nodes)
            except Exception as e:
                print("[Error]", e)

if __name__ == "__main__":
    repl = REPL()
    repl.run()
