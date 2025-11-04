# unik_repl.py
import re

def unik_repl():
    env = {}  # environment to store variables

    print("unik>> Welcome to Unik REPL!")
    print("Type 'exit' or 'quit' to leave the shell.")
    print("Use 'load filename.unik' to run a file.")
    
    while True:
        try:
            line = input("unik>> ").strip()
            if line in ("exit", "quit"):
                break

            # handle file loading
            if line.startswith("load "):
                filename = line[5:].strip()
                try:
                    with open(filename, "r") as f:
                        lines = f.readlines()
                    run_unik_lines(lines, env)
                except Exception as e:
                    print(f"Error loading file '{filename}': {e}")
                continue

            # handle variable assignment
            assign_match = re.match(r"(\w+)\s*=\s*(.+)", line)
            if assign_match:
                var, expr = assign_match.groups()
                env[var] = eval(expr, {}, env)
                continue

            # handle give
            give_match = re.match(r"give\s+(.+)", line)
            if give_match:
                value = give_match.group(1)
                give_unik(value, env)
                continue

            # handle loop: loop i in 0..5 { ... }
            loop_match = re.match(r"loop\s+(\w+)\s+in\s+(.+)\s*\{", line)
            if loop_match:
                body = read_block()
                run_unik_lines([line] + body, env)
                continue

            # handle repeat-until: repeat condition { ... }
            repeat_match = re.match(r"repeat\s+(.+)\s*\{", line)
            if repeat_match:
                body = read_block()
                run_unik_lines([line] + body, env)
                continue

            # handle if
            if line.startswith("if "):
                body_lines, offset = read_if_else_block(line, env)
                run_unik_lines(body_lines, env)
                continue

        except Exception as e:
            print("Error:", e)


def read_block():
    """Read lines until matching }"""
    block = []
    open_braces = 1
    while open_braces > 0:
        line = input().strip()
        if "{" in line:
            open_braces += 1
        if "}" in line:
            open_braces -= 1
            if open_braces == 0:
                break
        block.append(line)
    return block


def read_if_else_block(line, env):
    """
    Reads an if { } [else { }] block and returns the lines to execute.
    """
    # get condition
    condition_match = re.match(r"if\s+(.+)\s*\{", line)
    if not condition_match:
        return [], 1
    condition = condition_match.group(1)

    # read if body
    if_body = []
    open_braces = 1
    while open_braces > 0:
        l = input().strip()
        if "{" in l:
            open_braces += 1
        if "}" in l:
            open_braces -= 1
            if open_braces == 0:
                break
        if_body.append(l)

    # check next line for else
    else_body = []
    # peek ahead
    try:
        next_line = input().strip()
        if next_line.startswith("else"):
            # read else body
            open_braces = 1
            while open_braces > 0:
                l = input().strip()
                if "{" in l:
                    open_braces += 1
                if "}" in l:
                    open_braces -= 1
                    if open_braces == 0:
                        break
                else_body.append(l)
    except EOFError:
        pass

    # return lines based on condition
    try:
        if eval(condition, {}, env):
            return if_body, 1
        else:
            return else_body, 1
    except:
        return [], 1


def run_unik_lines(lines, env):
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith("#"):
            i += 1
            continue

        # loop
        loop_match = re.match(r"loop\s+(\w+)\s+in\s+(.+)\s*\{", line)
        if loop_match:
            var, range_expr = loop_match.groups()
            range_parts = range_expr.split(",")
            if ".." in range_parts[0]:  # numeric range
                start_end = range_parts[0].split("..")
                start = int(eval(start_end[0], {}, env))
                end = int(eval(start_end[1], {}, env))
                step = int(eval(range_parts[1], {}, env)) if len(range_parts) > 1 else 1
                body, offset = get_block(lines, i+1)
                for env[var] in range(start, end + 1, step):
                    run_unik_lines(body, env)
                i += offset
                continue
            else:  # for-each
                iterable = eval(range_parts[0], {}, env)
                body, offset = get_block(lines, i+1)
                for env[var] in iterable:
                    run_unik_lines(body, env)
                i += offset
                continue

        # repeat
        repeat_match = re.match(r"repeat\s+(.+)\s*\{", line)
        if repeat_match:
            condition = repeat_match.group(1)
            body, offset = get_block(lines, i+1)
            while eval(condition, {}, env):
                run_unik_lines(body, env)
            i += offset
            continue

        # if
        if line.startswith("if "):
            body_lines, offset = read_if_else_block(line, env)
            run_unik_lines(body_lines, env)
            i += offset
            continue

        # normal line
        exec_unik_line(line, env)
        i += 1


def get_block(lines, start_index):
    """Get lines inside { } block, returns list of lines and number of lines consumed"""
    block = []
    open_braces = 1
    i = start_index
    while i < len(lines):
        l = lines[i].strip()
        if "{" in l:
            open_braces += 1
        if "}" in l:
            open_braces -= 1
            if open_braces == 0:
                return block, i - start_index + 2
        block.append(l)
        i += 1
    return block, i - start_index


def exec_unik_line(line, env):
    line = line.strip()
    if line.startswith("give "):
        value = line[5:]
        give_unik(value, env)
    elif "=" in line:
        var, expr = line.split("=", 1)
        env[var.strip()] = eval(expr.strip(), {}, env)
    else:
        print("Unknown command:", line)


def give_unik(value, env):
    value = value.strip()
    if value in ('""', "'\\n'", '"\\n"'):
        print()
        return
    parts = [v.strip() for v in value.split(",")]
    out = []
    for v in parts:
        try:
            out.append(str(eval(v, {}, env)))
        except:
            out.append(v.strip('"').strip("'"))
    print(" ".join(out), end=" ")
    if not value.endswith(","):
        print()


if __name__ == "__main__":
    unik_repl()
