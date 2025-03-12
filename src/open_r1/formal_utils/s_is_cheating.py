import subprocess
import os
import re
from clang.cindex import Config, Index, CursorKind

# Global flag to indicate if clang is available
clang_available = True

def set_libclang_using_llvm_config():
    """
    Sets the libclang library file path using llvm-config.
    """
    try:
        # Execute llvm-config to get the library directory.
        llvm_libdir = subprocess.check_output(
            ['llvm-config', '--libdir'], universal_newlines=True
        ).strip()
        
        # Construct the full path to the libclang shared library.
        # Adjust the file name if you are on macOS (e.g., libclang.dylib) or Windows.
        libclang_filename = "libclang.so"
        libclang_path = os.path.join(llvm_libdir, libclang_filename)
        
        # Set the library file path.
        Config.set_library_file(libclang_path)
        print("Successfully set libclang library file to:", libclang_path)
    except subprocess.CalledProcessError as e:
        print("Error executing llvm-config:", e)
    except Exception as e:
        print("Error setting libclang library file:", e)

# Call the function early in your code before using clang.cindex features.
set_libclang_using_llvm_config()

def extract_context_vars_clang(c_code: str) -> list:
    """
    Uses clang.cindex to parse the C code and extract variable declarations.
    It returns a list of variable names declared in the code.
    """
    index = Index.create()
    # Parse the source code from an unsaved file.
    tu = index.parse("tmp.c", args=["-std=c99"], unsaved_files=[("tmp.c", c_code)], options=0)
    vars_found = set()
    
    def visitor(node):
        # Look for variable declarations or parameters.
        if node.kind in (CursorKind.VAR_DECL, CursorKind.PARM_DECL):
            if node.spelling:
                vars_found.add(node.spelling)
        for child in node.get_children():
            visitor(child)
    
    visitor(tu.cursor)
    return list(vars_found)

def extract_context_vars_regex(c_code: str) -> list:
    """
    Fallback regex extraction for context variables.
    This naive approach captures declarations for types like int, float, double, char, and long.
    """
    pattern = r'\b(?:int|float|double|char|long)\s+([^;]+);'
    matches = re.findall(pattern, c_code, flags=re.MULTILINE)
    vars_found = []
    for match in matches:
        parts = match.split(',')
        for part in parts:
            var = part.strip()
            # Remove pointer asterisks and initializers.
            var = var.lstrip('*').split('=')[0].strip()
            if re.match(r'^[a-zA-Z_]\w*$', var):
                vars_found.append(var)
    return list(set(vars_found))

def extract_context_vars(c_code: str) -> list:
    """
    Tries to extract context variables using clang.
    If any error occurs (or clang is not available), falls back to regex extraction.
    """
    if clang_available:
        try:
            return extract_context_vars_clang(c_code)
        except Exception as e:
            print("Error using clang to extract context variables:", e)
            return extract_context_vars_regex(c_code)
    else:
        return extract_context_vars_regex(c_code)

def is_assert_cheating(c_code: str, context_vars: list = None) -> bool:
    """
    Checks C source code for assert statements and determines if any assert is 'cheating'.
    
    An assert is considered cheating if its expression does not reference any of the context variables
    declared in the code. If context_vars is not provided, they are extracted automatically.
    
    Parameters:
        c_code (str): The C source code.
        context_vars (list): Optional list of variable names (as strings) that are allowed.
    
    Returns:
        bool: True if at least one assert is cheating, False otherwise.
    """
    if context_vars is None:
        context_vars = extract_context_vars(c_code)
    # print("context_vars:", context_vars)
    
    # Regex to capture the content inside assert() calls.
    pattern = r'assert\s*\((.*?)\)\s*;'
    matches = re.findall(pattern, c_code, flags=re.MULTILINE)
    
    if not matches:
        return False
    
    for expr in matches:
        # If none of the extracted context variables appear as whole words in the assert expression,
        # we consider that assert "cheating".
        if not any(re.search(r'\b' + re.escape(var) + r'\b', expr) for var in context_vars):
            return True
    return False

