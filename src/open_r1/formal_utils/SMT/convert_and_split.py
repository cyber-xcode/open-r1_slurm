
import re

def tokenize(expr):
    tokens = []
    i = 0
    while i < len(expr):
        if expr[i].isspace():
            i += 1
            continue
        if expr[i:i+2].lower() == '0x':
            hexnum = expr[i:i+2]
            i += 2
            while i < len(expr) and expr[i] in "0123456789abcdefABCDEF":
                hexnum += expr[i]
                i += 1
            tokens.append(hexnum)
            continue
        if expr[i].isdigit():
            num = expr[i]
            i += 1
            while i < len(expr) and expr[i].isdigit():
                num += expr[i]
                i += 1
            if i < len(expr) and expr[i] == '.':
                num += expr[i]
                i += 1
                while i < len(expr) and expr[i].isdigit():
                    num += expr[i]
                    i += 1
            if i < len(expr) and expr[i] in "eE":
                num += expr[i]
                i += 1
                if i < len(expr) and expr[i] in "+-":
                    num += expr[i]
                    i += 1
                while i < len(expr) and expr[i].isdigit():
                    num += expr[i]
                    i += 1
            while i < len(expr) and expr[i].isalpha():
                num += expr[i]
                i += 1
            tokens.append(num)
            continue
        if expr[i].isalpha() or expr[i] == '_':
            ident = expr[i]
            i += 1
            while i < len(expr) and (expr[i].isalnum() or expr[i] == '_'):
                ident += expr[i]
                i += 1
            tokens.append(ident)
            continue
        if expr[i:i+2] in ['&&', '||', '>=', '<=', '==', '!=']:
            tokens.append(expr[i:i+2])
            i += 2
            continue
        if expr[i] in ['!', '>', '<', '+', '-', '*', '/', '%', '(', ')', '[', ']', '^']:
            tokens.append(expr[i])
            i += 1
            continue
        tokens.append(expr[i])
        i += 1
    return tokens


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def eat(self, token=None):
        cur = self.current()
        if token and cur != token:
            raise ValueError(f"Expected token '{token}' but got '{cur}'")
        self.pos += 1
        return cur

    def parse_expression(self):
        return self.parse_or()

    def parse_or(self):
        node = self.parse_and()
        while self.current() == '||':
            self.eat('||')
            right = self.parse_and()
            node = ('or', node, right)
        return node

    def parse_and(self):
        node = self.parse_equality()
        while self.current() == '&&':
            self.eat('&&')
            right = self.parse_equality()
            node = ('and', node, right)
        return node

    def parse_equality(self):
        node = self.parse_relational()
        while self.current() in ['==', '!=']:
            op = self.eat()
            right = self.parse_relational()
            node = (op, node, right)
        return node

    def parse_relational(self):
        node = self.parse_additive()
        while self.current() in ['>', '<', '>=', '<=']:
            op = self.eat()
            right = self.parse_additive()
            node = (op, node, right)
        return node

    def parse_additive(self):
        node = self.parse_multiplicative()
        while self.current() in ['+', '-']:
            op = self.eat()
            right = self.parse_multiplicative()
            node = (op, node, right)
        return node

    def parse_multiplicative(self):
        node = self.parse_unary()
        while self.current() in ['*', '/', '%']:
            op = self.eat()
            right = self.parse_unary()
            node = (op, node, right)
        return node

    def parse_unary(self):
        if self.current() in ['!', '-']:
            op = self.eat()
            node = self.parse_unary()
            return (op, node)
        else:
            return self.parse_primary()
    
    
    def parse_primary(self):
        if self.current() == '(':
            # Try to detect a type cast.
            pos_backup = self.pos
            self.eat('(')
            cast_tokens = []
            while self.current() is not None and self.current() != ')':
                cast_tokens.append(self.current())
                self.eat()
            if self.current() == ')':
                self.eat(')')
            else:
                raise ValueError("Expected token ')' in cast")
            cast_str = " ".join(cast_tokens)
            # Accept casts such as "signed char", "unsigned int", etc.
            if re.fullmatch(r'(unsigned\s+)?((signed\s+char)|(short)|(int)|(long)|(char)|(float)|(double)|(long\s+long)|(long\s+double))', cast_str):
                return self.parse_primary()
            else:
                # Not a cast: rewind and parse as a parenthesized expression.
                self.pos = pos_backup
                self.eat('(')
                node = self.parse_expression()
                self.eat(')')
        else:
            token = self.current()
            self.eat()
            # Accept character literals enclosed in single quotes.
            if token.startswith("'") and token.endswith("'"):
                node = token
            elif not (re.fullmatch(r'[a-zA-Z_][a-zA-Z0-9_]*', token) or
                      re.fullmatch(r'\d+(\.\d*)?([eE][-+]?\d+)?[uUlLfF]*', token) or
                      re.fullmatch(r'0x[0-9a-fA-F]+', token)):
                raise ValueError(f"Invalid token '{token}' in expression")
            else:
                node = token
        # Handle function calls
        while self.current() == '(':
            self.eat('(')
            args = []
            if self.current() != ')':
                args.append(self.parse_expression())
                while self.current() == ',':
                    self.eat(',')
                    args.append(self.parse_expression())
            self.eat(')')
            node = ('call', node, args)
        # Handle array indexing: e.g. A[48] becomes ('select', A, 48)
        while self.current() == '[':
            self.eat('[')
            index_expr = self.parse_expression()
            self.eat(']')
            node = ('select', node, index_expr)
        # Handle bitwise AND operator
        if self.current() == '&':
            self.eat('&')
            right = self.parse_primary()
            node = ('&', node, right)
        return node




def is_boolean_expr(ast):
    """Heuristically determine if the AST represents a Boolean expression."""
    if isinstance(ast, tuple):
        op = ast[0]
        return op in {"==", "!=", ">", "<", ">=", "<=", "and", "or", "not"}
    # Treat literal "true" and "false" as boolean.
    if ast in {"true", "false"}:
        return True
    return False


# Modified ast_to_smtlib2 to support array indexing
def ast_to_smtlib2(ast):
    import re
    if isinstance(ast, tuple):
        if len(ast) == 2:
            op, expr = ast
            if op == '!':
                return f"(not {ast_to_smtlib2(expr)})" if is_boolean_expr(expr) else f"(= {ast_to_smtlib2(expr)} 0)"
            elif op == '-':
                return f"(- {ast_to_smtlib2(expr)})"
            else:
                raise ValueError("Unknown unary operator: " + op)
        elif len(ast) == 3:
            op, left, right = ast
            if op == "select":
                # Generate SMT-LIB select.
                return f"(select {ast_to_smtlib2(left)} {ast_to_smtlib2(right)})"
            elif op in ['+', '-', '*', '/', '>', '<', '>=', '<=']:
                return f"({op} {ast_to_smtlib2(left)} {ast_to_smtlib2(right)})"
            elif op == '==':
                return f"(= {ast_to_smtlib2(left)} {ast_to_smtlib2(right)})"
            elif op == '!=':
                return f"(not (= {ast_to_smtlib2(left)} {ast_to_smtlib2(right)}))"
            elif op == 'and':
                return f"(and {ast_to_smtlib2(left)} {ast_to_smtlib2(right)})"
            elif op == 'or':
                return f"(or {ast_to_smtlib2(left)} {ast_to_smtlib2(right)})"
            elif op == '%':
                return f"(mod {ast_to_smtlib2(left)} {ast_to_smtlib2(right)})"
            else:
                raise ValueError("Unknown binary operator: " + op)
        else:
            raise ValueError("Invalid AST node: " + str(ast))
    else:
        if re.fullmatch(r'0x[0-9a-fA-F]+', ast):
            return str(int(ast, 16))
        return ast


def ast_to_smtlib2(ast):
    import re
    import ast as py_ast
    if isinstance(ast, tuple):
        if ast[0] == "call":
            func = ast_to_smtlib2(ast[1])
            args_list = ast[2]
            args_smt = " ".join(ast_to_smtlib2(arg) for arg in args_list)
            return f"({func} {args_smt})" if args_smt else f"({func})"
        if len(ast) == 2:
            op, expr = ast
            if op == '!':
                return f"(not {ast_to_smtlib2(expr)})" if is_boolean_expr(expr) else f"(= {ast_to_smtlib2(expr)} 0)"
            elif op == '-':
                return f"(- {ast_to_smtlib2(expr)})"
            else:
                raise ValueError("Unknown unary operator: " + op)
        elif len(ast) == 3:
            op, left, right = ast
            if op == "select":
                return f"(select {ast_to_smtlib2(left)} {ast_to_smtlib2(right)})"
            elif op in ['+', '-', '*', '/', '>', '<', '>=', '<=', '&']:
                return f"({op} {ast_to_smtlib2(left)} {ast_to_smtlib2(right)})"
            elif op == '==':
                return f"(= {ast_to_smtlib2(left)} {ast_to_smtlib2(right)})"
            elif op == '!=':
                return f"(not (= {ast_to_smtlib2(left)} {ast_to_smtlib2(right)}))"
            elif op == 'and':
                return f"(and {ast_to_smtlib2(left)} {ast_to_smtlib2(right)})"
            elif op == 'or':
                return f"(or {ast_to_smtlib2(left)} {ast_to_smtlib2(right)})"
            elif op == '%':
                return f"(mod {ast_to_smtlib2(left)} {ast_to_smtlib2(right)})"
            else:
                raise ValueError("Unknown binary operator: " + op)
        else:
            raise ValueError("Invalid AST node: " + str(ast))
    else:
        if re.fullmatch(r'0x[0-9a-fA-F]+', ast):
            return str(int(ast, 16))
        if re.fullmatch(r'\d+(\.\d*)?([eE][-+]?\d+)?[uUlLfF]+', ast):
            m = re.fullmatch(r'(\d+(\.\d*)?([eE][-+]?\d+)?)[uUlLfF]+', ast)
            return m.group(1)
        if ast.startswith("'") and ast.endswith("'") and len(ast) >= 3:
            try:
                ch = py_ast.literal_eval(ast)
                return str(ord(ch))
            except Exception:
                return ast
        return ast

def convert_assert_to_smtlib2(c_assert):
    """
    Converts a C assert statement into an SMT-LIB2 assert command.
    
    For example:
      "assert(x > 0 && y == 2);"  ->  "(assert (and (> x 0) (= y 2)))"
      
    If the syntax of the C assert statement is invalid, a ValueError is raised.
    """
    pattern = r'assert\s*\((.*)\)\s*;'
    match = re.fullmatch(pattern, c_assert.strip())
    if not match:
        raise ValueError("Invalid C assert statement format.")
    expr = match.group(1)
    
    tokens = tokenize(expr)
    parser = Parser(tokens)
    ast = parser.parse_expression()
    
    if parser.pos != len(tokens):
        raise ValueError("Extra tokens after valid expression")
    
    smt_expr = ast_to_smtlib2(ast)
    return f"(assert {smt_expr})"


def convert_c_assert_to_smtlib2(c_assert):
    return  convert_assert_to_smtlib2( c_assert )

    expression = c_assert[c_assert.find("(")+1:c_assert.rfind(")")]
    tokens = tokenize(expression)
    # print(tokens)
    prefix = infix_to_prefix(tokens)
    # print(prefix)
    smtlib2_assert = prefix_to_smtlib2(prefix)
    return smtlib2_assert


def convert_c_assert_list_to_smtlib2(c_assert_statement_list):
    smtlib2_assert_list=[]
    for c_assert_statement in c_assert_statement_list:
        smtlib2_assert = convert_c_assert_to_smtlib2(c_assert_statement)
        smtlib2_assert_list.append(smtlib2_assert)
    return smtlib2_assert_list



def detect_outer_operator(expression):

    if expression[9:12]=='and':
        return '&&'
    elif expression[9:12]=='or ':
        return '||'
    else:
        return None 

def split_expression(expression, operator):
    parts = []
    bracket_count = 0
    start = 0
    for i, char in enumerate(expression):
        if char == '(':
            bracket_count += 1
        elif char == ')':
            bracket_count -= 1
        elif bracket_count == 0 and expression[i:i+len(operator)] == operator:
            parts.append(expression[start:i].strip())
            start = i + len(operator)
    parts.append(expression[start:].strip())  
    return parts

def c_assert_spilit(assert_statement):

    expression = assert_statement[assert_statement.find("(")+1:assert_statement.rfind(")")]
    
    smtlib2=convert_c_assert_to_smtlib2(assert_statement)


    outer_operator = detect_outer_operator(smtlib2)
    

    if outer_operator:
        split_op = '&&' if outer_operator == '&&' else '||'
        predicates = split_expression(expression, split_op)
    else:
        predicates = [expression]  
    
    return predicates, outer_operator




def merge_asserts(asserts):
    if len(asserts)<=0:
        return  None 
    conditions = []
    for assertion in asserts:
        match = re.search(r'assert\s*\((.*?)\)\s*;', assertion, re.DOTALL)
        if match:
            conditions.append(match.group(1).strip())
    
    merged_condition = ' && '.join(conditions)
    return f'assert ( {merged_condition} ) ;'

def extract_asserts(response_str):
    # Remove possible code block markers (```) from LLM response
    response_str = re.sub(r'```[\s\S]*?```', lambda m: m.group(0).replace('```', ''), response_str)
    
    # Find all assert statements in the response
    return re.findall(r'assert\s*\(.*?\)\s*;', response_str, re.DOTALL)

