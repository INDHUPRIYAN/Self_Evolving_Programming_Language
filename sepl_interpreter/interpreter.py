from sepl_interpreter.ast_nodes import *

class Environment:
    def __init__(self):
        self.variables = {}

    def get(self, name):
        return self.variables.get(name, '')

    def set(self, name, value):
        self.variables[name] = value


class Interpreter:
    def __init__(self, tree):
        self.tree = tree
        self.env = Environment()

    def evaluate(self):
        return self.exec_block(self.tree.children)

    def exec_block(self, statements):
        for stmt in statements:
            self.exec_statement(stmt)

    def exec_statement(self, node):
        if isinstance(node, AssignmentNode):
            var_name = node.value
            value = self.eval_expression(node.children[0])
            self.env.set(var_name, value)

        elif isinstance(node, OutputNode):
            value = self.eval_expression(node.children[0])
            print(value)

        elif isinstance(node, IfNode):
            condition_value = self.eval_expression(node.condition)

            if self.is_truthy(condition_value):
                self.exec_block(node.true_block)
            else:
                executed_elif = False
                for elif_cond, elif_block in node.elif_blocks:
                    elif_value = self.eval_expression(elif_cond)
                    if self.is_truthy(elif_value):
                        self.exec_block(elif_block)
                        executed_elif = True
                        break

                if not executed_elif and node.else_block:
                    self.exec_block(node.else_block)

    def eval_expression(self, node):
        if isinstance(node, StringNode):
            return node.value

        elif isinstance(node, VarNode):
            return self.env.get(node.value)
        
        elif isinstance(node, NumberNode):
            return node.value


        elif isinstance(node, InputNode):
            val = input(node.value + ' ').strip()
            # Convert to int or float if numeric
            try:
                if '.' in val:
                    return float(val)
                else:
                    return int(val)
            except ValueError:
                return val  # Keep as string if not numeric

        elif isinstance(node, BinaryOpNode):
            left = self.eval_expression(node.children[0])
            right = self.eval_expression(node.children[1])

            # Ensure numeric operands where needed
            numeric_ops = ('+', '-', '*', '/', '%', '==', '!=', '<', '<=', '>', '>=')
            if node.value in numeric_ops:
                # Convert string numbers to int/float
                if isinstance(left, str) and left.replace('.','',1).isdigit():
                    left = float(left) if '.' in left else int(left)
                if isinstance(right, str) and right.replace('.','',1).isdigit():
                    right = float(right) if '.' in right else int(right)

            # Arithmetic
            if node.value == '+':
                return left + right
            elif node.value == '-':
                return left - right
            elif node.value == '*':
                return left * right
            elif node.value == '/':
                if right == 0:
                    raise RuntimeError("Division by zero is not allowed")
                return left / right
            elif node.value == '%':
                if right == 0:
                    raise RuntimeError("Modulo by zero is not allowed")
                return left % right

            # Comparison
            elif node.value == '==':
                return left == right
            elif node.value == '!=':
                return left != right
            elif node.value == '<':
                return left < right
            elif node.value == '<=':
                return left <= right
            elif node.value == '>':
                return left > right
            elif node.value == '>=':
                return left >= right

            # Logical
            elif node.value == 'and':
                return self.is_truthy(left) and self.is_truthy(right)
            elif node.value == 'or':
                return self.is_truthy(left) or self.is_truthy(right)
            else:
                raise RuntimeError(f"Unsupported binary operator: {node.value}")

        else:
            raise RuntimeError(f"Unknown expression type: {node}")

    def is_truthy(self, value):
        # Numeric zero, empty string, None, False are falsey
        return bool(value) and value not in ('', 0, 0.0, False)
