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

            # multi-line constructs should be in files
            if line.startswith("loop ") or line.startswith("repeat ") or line.startswith("if "):
                print("Please use 'load filename.unik' for multi-line loops, repeats, or if blocks.")
                continue

        except Exception as e:
            print("Error:", e)


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

        # if / else
        if line.startswith("if "):
            body_lines, offset = get_if_else_block(lines, i, env)
            run_unik_lines(body_lines, env)
            i += offset
            continue

        # normal line
        exec_unik_line(line, env)
        i += 1


def get_block(lines, start_index):
    """Extract lines inside { } including nested braces, return block and number of lines consumed"""
    block = []
    open_braces = 1
    i = start_index
    while i < len(lines):
        l = lines[i].rstrip()
        open_braces += l.count("{")
        open_braces -= l.count("}")
        if open_braces == 0:
            return block, i - start_index + 1
        block.append(l)
        i += 1
    return block, i - start_index


def get_if_else_block(lines, start_index, env):
    """
    Extracts if { ... } [else { ... }] from lines starting at start_index
    Returns the lines to execute and number of lines consumed
    """
    line = lines[start_index].strip()
    condition_match = re.match(r"if\s+(.+)\s*\{", line)
    if not condition_match:
        return [], 1
    condition = condition_match.group(1)

    # extract if body
    if_body, offset = get_block(lines, start_index + 1)

    # check for else
    else_body = []
    next_index = start_index + offset
    if next_index < len(lines):
        next_line = lines[next_index].strip()
        if next_line.startswith("else"):
            else_body, else_offset = get_block(lines, next_index + 1)
            offset += else_offset

    try:
        if eval(condition, {}, env):
            return if_body, offset
        else:
            return else_body, offset
    except:
        return [], offset


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
