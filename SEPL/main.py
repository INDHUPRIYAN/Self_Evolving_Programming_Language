import sys
from sepl_interpreter.lexer import tokenize
from sepl_interpreter.parser import Parser
from sepl_interpreter.interpreter import Interpreter

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <filename>")
        exit(1)

    filename = sys.argv[1]
    with open(filename, 'r') as f:
        code = f.read()

    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()

    interpreter = Interpreter(ast)
    interpreter.evaluate()
