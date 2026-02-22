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






def _extract_asserts_list(response_str: str):
    """
    Remove code block markers (```) from the response string and extract all assert statements.
    Returns a list of assert statements found.
    """
    def extract_solution(solution_str: str) -> str:
        """
        Extract the content between <answer> and </answer> tags from the solution string.
        If no such tags are found, returns the original (stripped) string.
        """

        answer_pattern = r"```(?:cpp|php|python|java|c)?\n(.*?)\n```"

        matches = list(re.finditer(answer_pattern, solution_str, re.DOTALL|re.MULTILINE))
        if matches:
            final_answer = matches[-1].group(1).strip()
        else:
            final_answer  = ""
        # print ("final_answer", final_answer)
        return final_answer

    response_str = extract_solution( response_str )
    # Remove code block markers (```...```) from the response string
    response_str = re.sub(
        r'```[\s\S]*?```', 
        lambda m: m.group(0).replace('```', ''), 
        response_str
    )

    return  re.findall(r'assert\s*\(.*?\)\s*;', response_str, re.DOTALL)



def extract_asserts(response_str: str):
    return "\n".join( _extract_asserts_list(response_str) )




