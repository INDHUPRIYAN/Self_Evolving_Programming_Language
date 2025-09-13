class ASTNode:
    def __init__(self, node_type, value=None, children=None):
        self.node_type = node_type
        self.value = value
        self.children = children if children else []

    def __repr__(self):
        if self.children:
            return f"ASTNode({self.node_type}, {self.value}, {self.children})"
        else:
            return f"ASTNode({self.node_type}, {self.value})"


class ProgramNode(ASTNode):
    def __init__(self, statements):
        super().__init__('PROGRAM', children=statements)


class AssignmentNode(ASTNode):
    def __init__(self, var_name, expr):
        super().__init__('ASSIGNMENT', value=var_name, children=[expr])


class OutputNode(ASTNode):
    def __init__(self, expr):
        super().__init__('OUTPUT', children=[expr])


class InputNode(ASTNode):
    def __init__(self, prompt):
        super().__init__('INPUT', value=prompt)


class BinaryOpNode(ASTNode):
    def __init__(self, left, op, right):
        super().__init__('BINARY_OP', value=op, children=[left, right])


class VarNode(ASTNode):
    def __init__(self, name):
        super().__init__('VAR', value=name)


class StringNode(ASTNode):
    def __init__(self, value):
        super().__init__('STRING', value=value)


class NumberNode(ASTNode):
    def __init__(self, value):
        super().__init__('NUMBER', value=value)


class IfNode(ASTNode):
    def __init__(self, condition, true_block, elif_blocks=None, else_block=None):
        super().__init__('IF')
        self.condition = condition
        self.true_block = true_block
        self.elif_blocks = elif_blocks or []
        self.else_block = else_block

class NumberNode(ASTNode):
    def __init__(self, value):
        super().__init__('NUMBER', value=value)
