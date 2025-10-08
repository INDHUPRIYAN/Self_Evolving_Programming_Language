# Unik Language Specification

This repository contains the full language specification for **Unik**, divided into 18 sections for clarity and structured for distribution.

---

## Folder Structure
```
Unik-Language-Spec/
├─ 1_Introduction.md
├─ 2_Data_Types.md
├─ 3_Variables_Constants.md
├─ 4_Operators.md
├─ 5_Control_Flow.md
├─ 6_Functions.md
├─ 7_OOP.md
├─ 8_FP.md
├─ 9_Error_Handling.md
├─ 10_Async_Concurrency.md
├─ 11_AI_Integration.md
├─ 12_Packages_Modules.md
├─ 13_Transpilers.md
├─ 14_Tooling.md
├─ 15_Backend_Database.md
├─ 16_Compiler_VM.md
├─ 17_Standard_Library.md
├─ 18_Example_Programs.md
```

---

# 1_Introduction.md
## Introduction
**Unik** is a multi-paradigm, AI-first programming language designed to combine procedural, OOP, and functional paradigms with AI integration, concurrency, and modern tooling.

**Key Features:**
- AI Integration (`aik`) for context-aware suggestions.
- Async-first concurrency (green threads + OS threads).
- Cross-platform execution (VM + LLVM + transpilers).
- Clean, readable syntax.
- Complete developer tooling (REPL, debugger, formatter, linter, package manager).

**Philosophy:** minimal boilerplate, AI-assisted coding, multi-paradigm coherence.

---

# 2_Data_Types.md
## Data Types
### Primitive Types
| Type   | Description    | Default| Example                |
|--------|----------------|--------|------------------------|
| int    | Integer        | 0      | `x: int = 10`          |
| float  | Floating-point | 0.0    | `pi: float = 3.14`     |
| bool   | Boolean        | false  | `flag: bool = true`    |
| string | Text           | ""     | `name: string = "Unik"`|
| null   | Null value     | null   | `x = null`             |

### Composite Types
- list: `[1,2,3]`
- set: `{1,2,3}`
- dict: `{"a":1, "b":2}`
- tuple: `(1,2)`

### Advanced Types
- Functions: `func add(x:int, y:int) -> int`
- Tensor / Matrix: `tensor([[1,2],[3,4]])`

---

# 3_Variables_Constants.md
## Variables & Constants
```unik
x = 10             # mutable
const pi = 3.14    # immutable
name: string = "Unik"
```
- Mutable by default
- `const` prevents reassignment
- Optional type hints

Scope rules: local by default, `global` for outer scope

---

# 4_Operators.md
| Category   | Operators              | Behavior          |
|------------|------------------------|-------------------|
| Arithmetic | `+ - * / % **`         | math              |
| Comparison | `== != < <= > >=`      | returns bool      |
| Logical    | `and or not`           | boolean ops       |
| Assignment | `= += -= *= /= %= **=` | modify variables  |
| Membership | `in, not in`           | check collections |
| Identity   | `is, is not`           | reference compare |

Example:
```unik
if x > y and x != 0 {
    print("x is valid")
}
```

---

# 5_Control_Flow.md
## Conditional Statements
```unik
if x > 10 {
    print("large")
} elif x == 10 {
    print("ten")
} else {
    print("small")
}
```
## Loops
- while
- for over list, range
- early exit: `break`, `continue`, `ret`

---

# 6_Functions.md
## Functions
```unik
func add(x:int, y:int) -> int {
    ret x + y
}
```
- Default params: `func greet(name="User")`
- Lambda: `square = lambda x => x*x`
- Var args: `func sumAll(*numbers)`

---

# 7_OOP.md
## Object-Oriented Programming
### Classes
```unik
class Animal {
    name: string
    func __init__(self, name) { self.name = name }
    func speak() { print(self.name + " makes a sound") }
}
```
### Inheritance
```unik
class Dog(Animal) {
    func speak() { print(self.name + " barks") }
}
```
### Access
- Public default
- Private: `_prefix`

---

# 8_FP.md
## Functional Programming
- Pure functions
- Higher-order: `map`, `filter`, `reduce`
- Composition: `compose(f,g)`

```unik
add1 = lambda x => x+1
mul2 = lambda x => x*2
f = compose(mul2, add1)
```

---

# 9_Error_Handling.md
## Exceptions
```unik
try {
    x = 10 / 0
} catch e {
    print("Error: " + str(e))
} finally {
    print("Cleanup")
}
```
- Exceptions are objects
- try/catch/finally supports cleanup

---

# 10_Async_Concurrency.md
## Async & Concurrency
### Green Threads
```unik
task1 = task { print("Task 1") }
task2 = task { print("Task 2") }
await task1
await task2
```
### Channels
```unik
ch = channel()
task { ch.send(10) }
val = await ch.receive()
```
### OS Threads
- Fallback for CPU-intensive tasks
- Scheduler balances green + OS threads

---

# 11_AI_Integration.md
## AI Engine (`aik`)
```unik
val = aik("Generate function to reverse a list", context=current_ast)
```
- Context-aware suggestions
- Cache: `.unik_ai_cache`
- Project-wide memory
- AST replacement before compilation

---

# 12_Packages_Modules.md
## Package Manager (`unikpkg`)
- Manifest: `unik.json`
- Commands: `add`, `remove`, `update`, `publish`
- Lockfile: deterministic installs
- Scripts: `unikpkg run test`

---

# 13_Transpilers.md
## Transpilers & Compilation
- Targets: Python, JS, C++
- LLVM backend: native binaries
- IR: single intermediate representation
- JIT optional

---

# 14_Tooling.md
## Tooling
- REPL: multiline, history, autocomplete
- Debugger: step-through, breakpoints
- Formatter: `unik fmt`
- Linter: `unik lint`
- Test runner: `unik test`
- Documentation: `unik doc`

---

# 15_Backend_Database.md
## Backend & Database
- SQL/NoSQL: SQLite, Postgres, MySQL, MongoDB, Redis
- CRUD, aggregation, joins
- HTTP client/server, microservices

---

# 16_Compiler_VM.md
## Compiler & VM
- Stack-based VM with bytecode
- ECS-style structures for high performance
- GC: mark-and-sweep, later optimizations
- Concurrency-aware VM
- Optional LLVM backend

---

# 17_Standard_Library.md
## Standard Library
- Collections, math, strings, date/time
- File I/O, networking, JSON, CSV
- AI/ML modules: tensors, neural networks
- Concurrency primitives

---

# 18_Example_Programs.md
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
```

---

All 18 markdown files above are fully formatted and ready to copy into individual `.md` files for a ZIP archive.

