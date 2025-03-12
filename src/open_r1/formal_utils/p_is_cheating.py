import clang.cindex
import subprocess
import os
from .s_is_cheating import is_assert_cheating



def normalize(s: str) -> str:
    """Remove all whitespace for textual comparison."""
    return "".join(s.split())

def unwrap(node: clang.cindex.Cursor) -> clang.cindex.Cursor:
    """
    Recursively unwrap nodes that are considered superficial wrappers,
    such as parentheses, unexposed nodes, casts, and logical NOT operators.
    """
    while True:
        if node.kind in {clang.cindex.CursorKind.PAREN_EXPR,
                         clang.cindex.CursorKind.UNEXPOSED_EXPR,
                         getattr(clang.cindex.CursorKind, "CSTYLE_CAST_EXPR", None),
                         getattr(clang.cindex.CursorKind, "IMPLICIT_CAST_EXPR", None)}:
            children = list(node.get_children())
            if children:
                node = children[0]
                continue
        if node.kind == clang.cindex.CursorKind.UNARY_OPERATOR:
            # Check if the token stream begins with a "!".
            tokens = list(node.get_tokens())
            token_str = " ".join(t.spelling for t in tokens)
            if token_str.lstrip().startswith("!"):
                children = list(node.get_children())
                if children:
                    node = children[0]
                    continue
        break
    return node

def expr_to_str(expr: clang.cindex.Cursor) -> str:
    """Return the normalized token string for an expression."""
    return normalize(" ".join(t.spelling for t in expr.get_tokens()))

def flatten_equality_expr(node: clang.cindex.Cursor) -> list:
    """
    Given an expression node, if it is a binary operator using "==",
    recursively flatten it so that a==a==a becomes [operand, operand, operand].
    Otherwise, return a list containing the node itself.
    """
    node = unwrap(node)
    if node.kind == clang.cindex.CursorKind.BINARY_OPERATOR:
        tokens = list(node.get_tokens())
        token_str = " ".join(t.spelling for t in tokens)
        if "==" in token_str:
            children = list(node.get_children())
            if len(children) == 2:
                left_ops = flatten_equality_expr(children[0])
                right_ops = flatten_equality_expr(children[1])
                return left_ops + right_ops
    return [node]

def is_trivial_condition(condition: clang.cindex.Cursor) -> bool:
    """
    Returns True if the condition is trivial (cheating). The rules are:
      1. If no non–literal variable appears (i.e. no DECL_REF_EXPR that isn’t a boolean literal),
         then the condition is constant/trivial.
      2. If every equality comparison (possibly chained) within the expression compares
         equivalent subexpressions, then it's trivial.
    """
    cond = unwrap(condition)

    # Collect all variable names (DECL_REF_EXPR) that are not boolean literals.
    identifiers = []
    def collect_ids(node):
        if node.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
            # Exclude boolean literal tokens.
            if node.spelling not in {"true", "false"}:
                identifiers.append(node.spelling)
        for child in node.get_children():
            collect_ids(child)
    collect_ids(cond)

    # Rule 1: if no variable (besides boolean literals) appears, it's trivial.
    if not identifiers:
        return True

    # Traverse the AST to find all equality comparisons.
    found_equality = False
    non_trivial_found = False

    def traverse(node):
        nonlocal found_equality, non_trivial_found
        if node.kind == clang.cindex.CursorKind.BINARY_OPERATOR:
            tokens = list(node.get_tokens())
            token_str = " ".join(t.spelling for t in tokens)
            if "==" in token_str:
                found_equality = True
                operands = flatten_equality_expr(node)
                reps = [expr_to_str(op) for op in operands]
                if not all(rep == reps[0] for rep in reps):
                    non_trivial_found = True


        for child in node.get_children():
            traverse(child)

    traverse(cond)
    if found_equality and not non_trivial_found:
        return True
    return False

def check_assert_cheating(source_code: str, assert_expr: str) -> bool:
    """
    Determines if an assert is 'cheating' (trivial) by the following rules:
      - If the condition does not involve any non–literal variable (e.g. assert(1==1) or assert(true==true)),
        it's cheating.
      - If every equality comparison in the condition compares equivalent expressions, then it's cheating.
    """
    dummy_code = f"""
    {source_code}

    // Override standard assert so it doesn't expand.
    #define assert(x) my_assert(x)
    void my_assert(int expr) {{}}

    void test() {{
        {assert_expr}
    }}
    """
    try:
        index = clang.cindex.Index.create()
        tu = index.parse("dummy.c", args=["-std=c11"],
                           unsaved_files=[("dummy.c", dummy_code)])
    except Exception as e:
        return False

    cheating = False

    def traverse(node: clang.cindex.Cursor):
        nonlocal cheating
        if node.kind == clang.cindex.CursorKind.CALL_EXPR:
            tokens = list(node.get_tokens())
            token_str = " ".join(t.spelling for t in tokens)
            if "my_assert" in token_str:
                for child in node.get_children():
                    if child.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
                        continue
                    if is_trivial_condition(child):
                        cheating = True
        for child in node.get_children():
            traverse(child)

    traverse(tu.cursor)
    return cheating



def p_is_cheating(a: str, b: str) -> bool:
    """
    """

    aa = a+"\n"+b
    if not check_assert_cheating( a,b ):

        return is_assert_cheating(aa)
    else :
        return True 








