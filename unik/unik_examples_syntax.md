# Unik Examples & Syntax Rules

This document contains detailed examples and syntax semantics for **Unik**, broken into individual sections suitable for Markdown files.

---

## Folder Structure
```
Unik-Examples-Syntax/
├─ 1_Variables_Constants.md
├─ 2_Data_Types.md
├─ 3_Operators.md
├─ 4_Control_Flow.md
├─ 5_Functions.md
├─ 6_OOP.md
├─ 7_FP.md
├─ 8_Error_Handling.md
├─ 9_Async_Concurrency.md
├─ 10_AI_Integration.md
├─ 11_Packages_Modules.md
├─ 12_Transpilers.md
├─ 13_Tooling.md
├─ 14_Backend_Database.md
├─ 15_Compiler_VM.md
├─ 16_Standard_Library.md
├─ 17_Example_Programs.md
├─ 18_Syntax_Rules.md
```

---

# 1_Variables_Constants.md
## Variables & Constants Examples
```unik
# Mutable variable
x = 10
x += 5  # x = 15

# Constant variable
const pi = 3.14
# pi += 1  # Error: cannot modify constant

# Type hint
name: string = "Unik"
```
**Semantics:** Variables are mutable by default; constants cannot change. Optional type hints improve clarity and tooling.

---

# 2_Data_Types.md
## Data Types Examples
```unik
# Primitive types
age: int = 25
score: float = 99.5
flag: bool = true
text: string = "Hello"

# Composite types
lst = [1,2,3]
s = {1,2,3}
d = {"a":1, "b":2}
t = (1,2)

# Advanced types
func add(x:int, y:int) -> int
matrix = tensor([[1,2],[3,4]])
```
**Semantics:** Collections support indexing, slicing, iteration, and standard operations like union/intersection for sets.

---

# 3_Operators.md
## Operators Examples
```unik
# Arithmetic
x = 10 + 5  # 15
y = 2 ** 3   # 8

# Comparison
flag = x > y  # true

# Logical
result = (x>5) and (y<10)  # true

# Membership
3 in lst  # true

# Identity
a = [1,2]
b = a
a is b  # true
```
**Semantics:** Supports standard operator precedence, short-circuit logical evaluation, and membership checks.

---

# 4_Control_Flow.md
## Control Flow Examples
```unik
# Conditional
if x > 10 {
    print("x is large")
} elif x == 10 {
    print("x is ten")
} else {
    print("x is small")
}

# Loops
for i in [1,2,3] {
    print(i)
}

# Range loop
loop i in 0..5 { give i }

# With step
loop i in 0..10, 2 { give i }

# Repeat-until
x = 3
repeat x > 0 {
    give "Counting down:", x
    x = x - 1
}

# For-each
nums = [1, 2, 3]
loop n in nums { give "Num:", n }


while x < 20 {
    x += 1
    if x == 15 { break }
}
```
**Semantics:** Supports if/elif/else, for and while loops, with break/continue/ret control.

---

# 5_Functions.md
## Functions Examples
```unik
# Normal function
func add(x:int, y:int) -> int {
    ret x + y
}

# Default parameter
func greet(name="User") {
    give("Hello " + name)
}

# Lambda
square = lambda x => x*x

# Variable-length arguments
func sumAll(*numbers) {
    ret sum(numbers)
}
```
**Semantics:** Functions can have default and variable arguments, support lambda expressions, and type hints for parameters and return values.

---

# 6_OOP.md
## Object-Oriented Programming Examples
```unik
# Class
class Animal {
    name: string
    func __init__(self, name) { self.name = name }
    func speak() { print(self.name + " makes a sound") }
}

# Inheritance
class Dog(Animal) {
    func speak() { print(self.name + " barks") }
}

dog = Dog("Buddy")
dog.speak()  # Buddy barks
```
**Semantics:** Supports classes, inheritance, method overriding, constructors, and public/private attributes.

---

# 7_FP.md
## Functional Programming Examples
```unik
numbers = [1,2,3,4]
squared = map(lambda x => x*x, numbers)
filtered = filter(lambda x => x>2, numbers)

add1 = lambda x => x+1
mul2 = lambda x => x*2
f = compose(mul2, add1)  # f(3) = 8
```
**Semantics:** Supports pure functions, higher-order functions, and function composition.

---

# 8_Error_Handling.md
## Error Handling Examples
```unik
try {
    x = 10 / 0
} catch e {
    print("Error: " + str(e))
} finally {
    print("Cleanup")
}
```
**Semantics:** Supports try/catch/finally blocks; exceptions are objects that can be caught and inspected.

---

# 9_Async_Concurrency.md
## Async & Concurrency Examples
```unik
# Green Threads
task1 = task { print("Task 1") }
task2 = task { print("Task 2") }
await task1
await task2

# Channels
ch = channel()
task { ch.send(10) }
val = await ch.receive()
```
**Semantics:** Supports green threads (coroutines), async/await, channels for communication, and OS threads for heavy computation.

---

# 10_AI_Integration.md
## AI Integration Examples
```unik
# Context-aware AI suggestion
reverse_list = aik("Generate function to reverse a list", context=current_ast)
```
**Semantics:** AI engine can generate code based on context, cache results, and replace AST nodes before compilation.

---

# 11_Packages_Modules.md
## Package Manager Examples
```unik
# Add package
unikpkg add http_client

# Remove package
unikpkg remove old_pkg

# Run script
unikpkg run test
```
**Semantics:** Supports manifest, lockfile, dependency management, and custom scripts.

---

# 12_Transpilers.md
## Transpiler Examples
```unik
# Unik -> Python
unik_to_python("main.unik")

# Unik -> JS
unik_to_js("main.unik")
```
**Semantics:** Uses single IR for all targets, generates clean code, supports transpiling for portability.

---

# 13_Tooling.md
## Tooling Examples
```unik
# REPL
unik repl

# Formatter
unik fmt main.unik

# Linter
unik lint main.unik

# Test Runner
unik test

# Documentation
unik doc main.unik
```
**Semantics:** Provides full developer experience, inline debugging, formatting, linting, and automated tests.

---

# 14_Backend_Database.md
## Backend & Database Examples
```unik
# Database connection
conn = connect_db("sqlite", "data.db")

# CRUD
conn.insert("users", {"name":"Alice", "age":25})
users = conn.select("users", filter=lambda x: x.age>20)

# HTTP Server
server = HTTPServer(port=8080)
server.route("/hello", lambda req: "Hello World")
server.start()
```
**Semantics:** Supports SQL/NoSQL, CRUD operations, aggregation, joins, and HTTP server/client APIs.

---

# 15_Compiler_VM.md
## Compiler & VM Examples
```unik
# Compile to bytecode
unik build main.unik

# Run bytecode
unik run main.unik

# Optional native compilation
unik build --native main.unik
```
**Semantics:** VM executes bytecode; optional LLVM backend compiles native binaries; supports JIT compilation and ECS structures.

---

# 16_Standard_Library.md
## Standard Library Examples
```unik
# Math
x = math.sqrt(16)

# File I/O
write_file("data.txt", "Hello")
content = read_file("data.txt")

# JSON
data = json.load("data.json")
json.save("out.json", data)

# AI/ML
tensor1 = tensor([[1,2],[3,4]])
model = NeuralNetwork()
```
**Semantics:** Covers collections, math, strings, file I/O, JSON, networking, AI/ML, and concurrency utilities.

---

# 17_Example_Programs.md
## Example Programs
```unik
# Hello World
print("Hello Unik")

# Async tasks
t1 = task { print("Task 1") }
t2 = task { print("Task 2") }
await t1
await t2

# AI-generated function
reverse_list = aik("Reverse a list function", context=current_ast)

# Class example
class Dog {
    func speak() { print("Woof") }
}
d = Dog()
d.speak()
```

---

# 18_Syntax_Rules.md
## Syntax & Semantic Rules
1. Indentation optional; braces `{}` denote blocks.
2. Statements end by newline; no semicolons required.
3. Comments: `# single-line`
4. Type annotations optional: `x: int = 5`
5. Variables mutable by default; `const` for immutability.
6. Functions: `func name(params) -> return_type`.
7. Lambdas: `lambda x => expression`.
8. Classes: support inheritance, constructors, public/private attributes.
9. Loops: `for` over collections, `while` with conditions.
10. Async: `task { }` + `await`.
11. AI: `aik(prompt, context)` for context-aware code generation.
12. Package manager: `unikpkg` for dependency & script management.
13. Operators: follow standard precedence; parentheses override.
14. Exceptions: `try/catch/finally`.
15. Transpilers: maintain single IR; target Python, JS, C++.
16. VM: stack-based; optional LLVM for native compilation.
17. All standard library modules follow consistent naming and import conventions.

---

All files are ready to copy into individual `.md` files for a structured Markdown reference set.