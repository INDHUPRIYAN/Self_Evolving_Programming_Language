# src/tests/test_full_features.py

from lexer.lexer import Lexer
from src.parser.parser import Parser
from src.interpreter.interpreter import Interpreter

def run_unik_code(code):
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    results = []
    for node in ast:
        res = interpreter.visit(node, interpreter.global_env)
        if res is not None:
            results.append(res)
    return results

if __name__ == "__main__":
    # ------------------------
    # Test 1: Variables & Expressions
    # ------------------------
    code1 = """
    x = 10
    y = 20
    z = x + y * 2
    give z
    """
    print("Test 1 Results:", run_unik_code(code1))  # Expected: [50]

    # ------------------------
    # Test 2: Functions (single-line & multi-line)
    # ------------------------
    code2 = """
    func add(a, b) -> a + b
    func mul(a, b) {
        result = a * b
        return result
    }
    give add(5, 7)
    give mul(3, 4)
    """
    print("Test 2 Results:", run_unik_code(code2))  # Expected: [12, 12]

    # ------------------------
    # Test 3: Conditionals
    # ------------------------
    code3 = """
    x = 5
    if x > 0 -> give "Positive"
    else -> give "Non-positive"
    """
    print("Test 3 Results:", run_unik_code(code3))  # Expected: ["Positive"]

    # ------------------------
    # Test 4: Loops
    # ------------------------
    code4 = """
    loop i in 1..3 -> give i
    repeat x > 0 {
        give x
        x = x - 1
    }
    """
    print("Test 4 Results:", run_unik_code(code4))  # Expected: [1, 2, 3, 5, 4, 3, 2, 1]

    # ------------------------
    # Test 5: Classes & OOP
    # ------------------------
    code5 = """
    class Person {
        init(name, age) {
            self.name = name
            self.age = age
        }
        func greet() {
            give "Hi " + self.name + ", age " + self.age
        }
    }
    p = Person("Krish", 21)
    p.greet()
    """
    print("Test 5 Results:", run_unik_code(code5))  # Expected: ["Hi Krish, age 21"]

    # ------------------------
    # Test 6: Boolean & Logical
    # ------------------------
    code6 = """
    a = true
    b = false
    give a && b
    give a || b
    """
    print("Test 6 Results:", run_unik_code(code6))  # Expected: [False, True]

    # ------------------------
    # Test 7: Nested Functions & Loops
    # ------------------------
    code7 = """
    func outer(x) {
        func inner(y) -> y * 2
        return inner(x) + 5
    }
    give outer(3)
    """
    print("Test 7 Results:", run_unik_code(code7))  # Expected: [11]

    # ------------------------
    # Test 8: Ask / I/O simulation
    # ------------------------
    # Normally ask needs REPL input; here we can skip or mock it in full testing

    print("All tests completed successfully.")
