import clang.cindex
import tempfile
import os

import re

# Set of C keywords that should not be declared.
C_KEYWORDS = {
    "auto", "break", "case", "char", "const", "continue", "default", "do", "double", "else",
    "enum", "extern", "float", "for", "goto", "if", "inline", "int", "long", "register",
    "restrict", "return", "short", "signed", "sizeof", "static", "struct", "switch", "typedef",
    "union", "unsigned", "void", "volatile", "while", "_Bool", "_Complex", "_Imaginary"
}

def get_identifiers(code: str) -> set:
    """
    Extract all identifiers from the code that are not C keywords and not the allowed
    assert names ("assert" or "__VERIFIER_assert").
    """
    # Remove string literals to avoid false positives.
    code_no_strings = re.sub(r'"(?:\\.|[^"\\])*"', '', code)
    tokens = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', code_no_strings)
    # Exclude keywords and the allowed assert names.
    return {token for token in tokens if token not in C_KEYWORDS and token not in {"assert", "__VERIFIER_assert"}}

def generate_dummy_declarations(code: str) -> str:
    """
    For each identifier found in the code, generate a dummy declaration.
    If the identifier appears to be used as a function (i.e. followed by '('),
    declare it as a function returning int; otherwise, declare it as an int variable.
    """
    identifiers = get_identifiers(code)
    declarations = []
    for ident in identifiers:
        # Detect if identifier is used as a function call.
        pattern = r'\b' + re.escape(ident) + r'\s*\('
        if re.search(pattern, code):
            declarations.append(f"int {ident}();")
        else:
            declarations.append(f"int {ident} = 0;")
    return "\n".join(declarations)

def check_assert_syntax(assert_statement: str) -> bool:
    """
    Check if the given assert statement has correct syntax using clang.
    
    This function verifies:
      1. The function name is either "assert" or "__VERIFIER_assert".
      2. The expression inside the parentheses is not empty.
      3. The overall syntax is valid when wrapped in a dummy C program.
    
    Parameters:
        assert_statement (str): The assert statement to check (e.g., "assert(aaa==bbb);")
    
    Returns:
        bool: True if the syntax is correct and the call is valid, False otherwise.
    """
    # Regular expression to capture the function name and its signature.
    # This pattern expects a function call that ends with a semicolon.
    pattern = r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*(.*?)\s*\)\s*;'
    match = re.match(pattern, assert_statement)
    if not match:
        return False

    fname, expr = match.group(1), match.group(2)
    # Check for allowed function names.
    if fname not in {"assert", "__VERIFIER_assert"}:
        return False
    # The expression inside the parentheses must not be empty.
    if expr == "":
        return False

    dummy_decls = generate_dummy_declarations(assert_statement)
    dummy_code = f"""
    #include <assert.h>
    {dummy_decls}
    int main() {{
        {assert_statement}
        return 0;
    }}
    """

    index = clang.cindex.Index.create()
    # Parse the code in memory using unsaved_files.
    tu = index.parse("dummy.c", args=["-std=c11", "-Werror", "-fsyntax-only"],
                       unsaved_files=[("dummy.c", dummy_code)])

    # Check diagnostics for errors (ignoring semantic errors about undeclared identifiers).
    for diag in tu.diagnostics:
        if diag.severity >= clang.cindex.Diagnostic.Error:
            msg = diag.spelling.lower()
            if "undeclared" in msg or "implicit declaration" in msg:
                continue
            return False
    return True

