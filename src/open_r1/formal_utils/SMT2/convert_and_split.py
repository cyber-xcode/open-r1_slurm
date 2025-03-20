import re

precedence = {
    'pow': 4, '^':4,
    '*': 3, '/': 3, '%': 3,
    '+': 2, '-': 2,
    '>': 1, '<': 1, '>=': 1, '<=': 1, '==': 1, '!=':1, 
    '&&': 0, '||': -1,
    'u-': 5,
    '!': 6
}

smtlib2_operator = [
    'pow', '^',
    '*', '/', '%',
    '+', '-',
    '>', '<', '>=', '<=', '==', '!=',
    '&&', '||',
    'u-',
    '!'
]


operator_conversion = {
    '&&': 'and',
    '||': 'or',
    '!': 'not',
    '==': '=',
    'u-': '-',
    '%': 'mod' 
}


def tokenize(expression):
    pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*\b|\bpow\b|&&|\|\||==|!=|<=|>=|>|<|[0-9]+\.[0-9]+|[0-9]+|[!^()\+\-*/%]'
    tokens = re.findall(pattern, expression)
    for i in range(len(tokens)):
        if tokens[i] == '-' and (i == 0 or tokens[i-1] in ['(', '+', '-', '*', '/', '%', '&&', '||', '==', '!=', '>=', '<=', '>', '<', '!']):
            tokens[i] = 'u-'  
    return tokens


def is_operator(token):
    return token in precedence


def is_function(token):
    return token == 'pow' or token == '^'


def compare_precedence(op1, op2):
    return precedence[op1] > precedence[op2]


def infix_to_prefix(tokens):
    stack = [] 
    output = []  
    try:
        for token in reversed(tokens):
            if token == ')':
                stack.append(token)
            elif token == '(':
                top_token = stack.pop()
                while top_token != ')':
                    output.append(top_token)
                    top_token = stack.pop()
            elif is_operator(token) or is_function(token):
                while (stack and is_operator(stack[-1]) and
                    compare_precedence(stack[-1], token) and
                    token != 'u-'):
                    output.append(stack.pop())
                stack.append(token)
            else:  
                output.append(token)
        while stack:
            output.append(stack.pop())
        return list(reversed(output))
    except:
        return None
    

def prefix_to_smtlib2(prefix):
    if prefix != None:
        try:
            stack = []
            for token in reversed(prefix):
                if is_operator(token) or is_function(token):
                    if is_function(token):
                        op1 = stack.pop()
                        op2 = stack.pop()
                        if token in operator_conversion.keys():
                            token = operator_conversion[token]
                        token = f"(let ((pow_tmp {op1})) (repeat (* pow_tmp {op2})))"
                    elif token != '!' and token !='u-' and token!='!=':
                        op1 = stack.pop()
                        op2 = stack.pop()
                        if token in operator_conversion.keys():
                            token = operator_conversion[token]
                        token = f"({token} {op1} {op2})"
                    elif token == '!=':
                        op1 = stack.pop()
                        op2 = stack.pop()
                        if token in operator_conversion.keys():
                            token = operator_conversion[token]
                        token = f"(not (= {op1} {op2}))"
                    elif token == 'u-':
                        op1 = stack.pop()
                        if token in operator_conversion.keys():
                            token = operator_conversion[token]
                        token = f"({token} 0 {op1})"
                    else:
                        op1 = stack.pop()
                        if token in operator_conversion.keys():
                            token = operator_conversion[token]
                        token = f"({token} {op1})"
                stack.append(token)
            smtlib2_assert = f"(assert {stack[0]})"
            return smtlib2_assert
        except:
            return "(assert = (0 0))"
    else:
        return "(assert = (0 0))"

def convert_c_assert_to_smtlib2(c_assert):
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

#
# if __name__ == "__main__":
#     test_cases = [
#         "assert((x >= -50) && (y >= 0) && (y == 0 && x + y >= -49));",
#         "assert((x >= -50) || (y >= 0) || (y == 0 && x + y >= -49));",
#         "assert(x >= -50 && y >= 0 && y == 0 || (x + y >= -49 && x > 100));",
#         "assert((lock == 0 && x != y) || (lock == 1 && x == y));",
#         "assert((j == (i * (i - 1)) / 2) && (i >= 0) && (i <= n) && (k >= 0));",
#         "assert((x >= y) && (y <= 100000));",
#         "assert(y <= 100000);",
#         "assert(x >= y && y <= 100000); ",
#         "assert((x == y + 10*n) && (x >= 0) && (y >= 0) || (x == 0 && y == 0));",
#         "assert((n>0&&x<0) || (n>0&&x>=0) || (n<=0&&x<=0));"
#     ]
#
#     for test in test_cases:
#         print(c_assert_spilit(test))
#
#
#     c_assert_statement_list = ['assert(x < 0 || y > 0);']
#
#     for c_assert_statement in c_assert_statement_list:
#         print(c_assert_statement)
#         smtlib2_assert = convert_c_assert_to_smtlib2(c_assert_statement)
#         print(smtlib2_assert)
#         print("========================================================")
#
#
#
#
#
#     # Test cases for merge_asserts
#     merge_test_cases = [
#         ["assert ( x > 1 ) ;", "assert ( y < 5 ) ;"],
#         ["assert ( z == 10 ) ;"],
#         ["assert (  a == b   ) ;", "assert(   c != d ) ;"],
#         ["assert ( (x > 1) ) ;", "assert ( ((y < 5)) ) ;"],
#         ["assert ( a + b == c ) ;", "assert ( d - e < f ) ;"],
#         ["assert ( (x > 0) || (y < 10) ) ;", "assert ( (a == 1) && (b != 2) ) ;"],
#         ["assert ( len(arr) > 5 ) ;", "assert ( max_val <= threshold ) ;"],
#         ["assert (\n x > 0\n && y < 10\n ) ;", "assert ( z != 5 ) ;"],
#         [],
#         ["assert ( ((a < b) && (b < c)) ) ;", "assert ( (x == y) || (y == z) ) ;"],
#         ["assert ( val % 2 == 0 ) ;", "assert ( price >= $100 ) ;"],
#         ["assert ( is_valid(x) ) ;", "assert ( compute(y) != None ) ;"],
#         ["assert ( (x & 1) == 0 ) ;", "assert ( (y | 2) == 3 ) ;"],
#         ["assert ( !(a == b) ) ;", "assert ( !flag ) ;"],
#         ["assert ( abs(a - b) < 0.0001 ) ;", "assert ( sqrt(x) >= 1.5 ) ;"],
#         ["assert ( name == \"Alice\" ) ;", "assert ( surname != \"Smith\" ) ;"],
#         ["assert (\n  (a > 0)\n  && (b < 10)\n) ;", "assert (\n  (x == y)\n  || (y == z)\n) ;"],
#         ["assert ( (x > 0) && ((y < 10) || (z == 5)) ) ;", "assert ( (a > b) && (c > d) ) ;"],
#         ["assert ( 'key' in dictionary ) ;", "assert ( my_dict.get('value') != None ) ;"],
#         ["assert ( len(arr) > 3 ) ;", "assert ( items.count(5) == 2 ) ;"],
#     ]
#
#     for i, test_case in enumerate(merge_test_cases):
#         print(f"Merged Assert {i+1}: {merge_asserts(test_case)}")
#
#     # Test cases for extract_asserts
#     extract_test_cases = [
#         "assert ( x > 1 ) ; assert ( y < 5 ) ;",
#         "```assert ( a == b ) ;\nassert ( c != d ) ;```",
#         "This is a response with no assertions.",
#         "Some text before assert ( x == 42 ) ; and some text after.",
#         "assert   (   x  >  1   )  ;    assert (  y   <   5   )   ;",
#         "```\nassert ( a != 0 ) ;\nassert ( b > 2 ) ;\n```",
#         "assert ( x > 0 ) ;\nassert ( y < 10 ) ;",
#         "Here is the assertion:\n```assert ( a > 1 ) ;```",
#         "assert ( (x > 1) && (y < 5) ) ;",
#         "",
#         "# assert ( x > 0 ) ;",
#         "assert ( a > b ) ;!@#$%^&*() assert ( c < d ) ;",
#         "assert ( x > 0 )",
#         "assert ( ((x > 1)) ) ;",
#         "assert (\n   x > 1  // check if x is positive\n) ;",
#         "In this function, we use `assert ( a == b ) ;` to verify the condition.",
#         "assert ( path == \"C:\\\\Users\\\\Admin\" ) ;",
#         "<code>assert ( x > 0 ) ;</code>",
#         "{ \"check\": \"assert ( x == 10 ) ;\" }",
#         "<assert>assert ( a > 0 ) ;</assert>",
#     ]
#
#     for i, response in enumerate(extract_test_cases):
#         print(f"Extracted Asserts {i+1}: {extract_asserts(response)}")