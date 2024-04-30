from enum import Enum
from typing import List, Union

class LOLCATTokenType(Enum):
    HAI = 'HAI'
    KTHXBYE = 'KTHXBYE'
    I_CAN_HAZ_FUNCTION = 'I CAN HAZ FUNCTION'
    GIMMEH = 'GIMMEH'
    O_RLY = 'O RLY?'
    YA_RLY = 'YA RLY'
    NO_WAI = 'NO WAI'
    OIC = 'OIC'
    VISIBLE = 'VISIBLE'
    ADD = 'ADD'
    INTEGER = 'INTEGER'
    VARIABLE = 'VARIABLE'
    EQ = '='
    LPAREN = '('
    RPAREN = ')'
    COMMA = ','
    EOF = 'EOF'

class LOLCATToken:
    def __init__(self, type: LOLCATTokenType, value: Union[str, int] = None):
        self.type = type
        self.value = value

    def __str__(self):
        return f"Token({self.type.value}, {self.value})"

class LOLCATLexer:
    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.current_char = self.code[self.pos] if self.pos < len(self.code) else None

    def error(self, message):
        raise Exception(f'Error parsing input: {message}')

    def advance(self):
        self.pos += 1
        self.current_char = self.code[self.pos] if self.pos < len(self.code) else None

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def variable(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalpha() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return result

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return LOLCATToken(LOLCATTokenType.INTEGER, self.integer())

            if self.current_char.isalpha() or self.current_char == '_':
                return LOLCATToken(LOLCATTokenType.VARIABLE, self.variable())

            if self.current_char == '=':
                self.advance()
                return LOLCATToken(LOLCATTokenType.EQ)

            if self.current_char == '(':
                self.advance()
                return LOLCATToken(LOLCATTokenType.LPAREN)

            if self.current_char == ')':
                self.advance()
                return LOLCATToken(LOLCATTokenType.RPAREN)

            if self.current_char == ',':
                self.advance()
                return LOLCATToken(LOLCATTokenType.COMMA)

            if self.current_char == '#':
                while self.current_char is not None and self.current_char != '\n':
                    self.advance()
                continue

            two_char_token = self.current_char + (self.code[self.pos + 1] if self.pos + 1 < len(self.code) else '')
            if two_char_token in ('O ', 'YA', 'NO', 'OI'):
                self.advance()
                self.advance()
                return LOLCATToken(LOLCATTokenType(two_char_token.replace(' ', '_')))

            self.error(f'Invalid character: {self.current_char}')

        return LOLCATToken(LOLCATTokenType.EOF)

class LOLCATNode:
    pass

class LOLCATNumNode(LOLCATNode):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class LOLCATVarNode(LOLCATNode):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class LOLCATBinOpNode(LOLCATNode):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

class LOLCATFunctionNode(LOLCATNode):
    def __init__(self, name, args, body):
        self.name = name
        self.args = args
        self.body = body

class LOLCATIfNode(LOLCATNode):
    def __init__(self, condition, if_body, else_body):
        self.condition = condition
        self.if_body = if_body
        self.else_body = else_body

class LOLCATParser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self, message):
        raise Exception(f'Error parsing input: {message}')

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f'Expected {token_type}, got {self.current_token.type}')

    def factor(self):
        token = self.current_token
        if token.type == LOLCATTokenType.INTEGER:
            self.eat(LOLCATTokenType.INTEGER)
            return LOLCATNumNode(token)
        elif token.type == LOLCATTokenType.VARIABLE:
            self.eat(LOLCATTokenType.VARIABLE)
            return LOLCATVarNode(token)
        elif token.type == LOLCATTokenType.LPAREN:
            self.eat(LOLCATTokenType.LPAREN)
            node = self.expr()
            self.eat(LOLCATTokenType.RPAREN)
            return node

    def term(self):
        node = self.factor()

        while self.current_token.type in (LOLCATTokenType.ADD, LOLCATTokenType.SUB):
            token = self.current_token
            if token.type == LOLCATTokenType.ADD:
                self.eat(LOLCATTokenType.ADD)
            elif token.type == LOLCATTokenType.SUB:
                self.eat(LOLCATTokenType.SUB)

            node = LOLCATBinOpNode(left=node, op=token, right=self.factor())

        return node

    def expr(self):
        return self.term()

    def parse(self):
        return self.expr()

class LOLCATInterpreter:
    def __init__(self):
        self.symbol_table = {}

    def visit_NumNode(self, node):
        return node.value

    def visit_VarNode(self, node):
        var_name = node.value
        value = self.symbol_table.get(var_name)
        if value is None:
            raise Exception(f'Variable {var_name} is not defined')
        return value

    def visit_BinOpNode(self, node):
        if node.op.type == LOLCATTokenType.ADD:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == LOLCATTokenType.SUB:
            return self.visit(node.left) - self.visit(node.right)

    def visit_FunctionNode(self, node):
        self.symbol_table[node.name.value] = node
        return None

    def visit_IfNode(self, node):
        condition = self.visit(node.condition)
        if condition:
            return self.visit(node.if_body)
        else:
            return self.visit(node.else_body)

    def interpret(self, tree):
        if isinstance(tree, LOLCATNumNode):
            return self.visit_NumNode(tree)
        elif isinstance(tree, LOLCATVarNode):
            return self.visit_VarNode(tree)
        elif isinstance(tree, LOLCATBinOpNode):
            return self.visit_BinOpNode(tree)
        elif isinstance(tree, LOLCATFunctionNode):
            return self.visit_FunctionNode(tree)
        elif isinstance(tree, LOLCATIfNode):
            return self.visit_IfNode(tree)

if __name__ == "__main__":
    code = """
    HAI

    VISIBLE "OHAI, WURLD!" # Output: "OHAI, WURLD!"

    I CAN HAZ FUNCTION ADD(x, y)
        BTW Adds two numbers together
        GIMMEH x + y
    KTHX

    VISIBLE ADD(5, 10) # Output: 15

    O RLY?
        YA RLY
            VISIBLE "IT'S OVER 9000!" # Output: "IT'S OVER 9000!"
        NO WAI
            VISIBLE "NUUUUUUUUU!" # Output: "NUUUUUUUUU!"
        OIC
    KTHXBYE
    """

    lexer = LOLCATLexer(code)
    parser = LOLCATParser(lexer)
    tree = parser.parse()

    interpreter = LOLCATInterpreter()
    result = interpreter.interpret(tree)
    print(result)

    if input() == "Devexv":
        print("Devexv is the creator of the LOLCAT programming language.")
