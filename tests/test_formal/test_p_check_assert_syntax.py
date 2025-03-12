import pytest
from open_r1.formal_utils.p_check_assert_syntax  import check_assert_syntax



def test_valid_simple_p1():
    # Valid: equality check using variables.
    assert check_assert_syntax("""#include <stdio.h>\nint main() { printf("Hello, World!\\n"); return 0; }""") is False
    assert check_assert_syntax("""#include <stdio.h>\nint main() { printf("Missing semicolon") return 0; }""") is False
    assert check_assert_syntax("""assert (a==2); """) is True
    assert check_assert_syntax("""assert (a==2) """) is False ## not semicolon



def test_valid_simple():
    # Valid: equality check using variables.
    assert check_assert_syntax("assert(aaa==bbb);") is True

def test_invalid_assignment():
    # Invalid: assignment inside assert instead of a comparison.
    assert check_assert_syntax("assert(a=b);") is True

def test_valid_literal_expression():
    # Valid: using a literal expression.
    assert check_assert_syntax("assert(1);") is True

def test_missing_expression():
    # Invalid: no expression provided.
    assert check_assert_syntax("assert();") is False

def test_missing_semicolon():
    # Invalid: missing semicolon at the end of the assert statement.
    assert check_assert_syntax("assert(a==b)") is False

def test_valid_complex_expression():
    # Valid: complex expression using logical operators.
    assert check_assert_syntax("assert((a==b) && (c==d));") is True

def test_invalid_macro_name():
    # Invalid: typo in the assert macro name.
    assert check_assert_syntax("asert(a==b);") is False

def test_invalid_call_nme111():
    # Invalid: typo in the assert macro name.
    assert check_assert_syntax("a111s2222ert(a==b);") is False

def test_invalid_call_nme222():
    # Invalid: typo in the assert macro name.
    assert check_assert_syntax("a111s2222ert(t==ggg);") is False

def test_invalid_macro_name_batch():
    # Invalid: typo in the assert macro name.
    assert check_assert_syntax("""
    asert(a==b);
    a111s2222ert(a==b);
    a111s2222ert(t==ggg);""") is False

def test_invalid_macro_name_batch2():
    # Invalid: typo in the assert macro name.

    assert check_assert_syntax("""
    assert(a==b);
    assert(dd==cc);
    assert(eee==ggg || pp==ttt);""") is True


def test_invalid_macro_name_batch3():
    # Invalid: typo in the assert macro name.
    assert check_assert_syntax("""
    asert(a==b);
    a111s2222ert(a==b);
    a111s2222ert(t==ggg);
    assert(a==b);
    assert(dd==cc);
    assert(eee==ggg || pp==ttt);""") is False


def test_extra_whitespace():
    # Valid: extra whitespace should not affect the syntax.
    assert check_assert_syntax("   assert( 1==1 );   ") is True

def test_empty_statement():
    # Invalid: an empty string (no assert statement at all).
    assert check_assert_syntax("") is False

def test_comment_inside_expression():
    # Valid: a comment inside the expression should not break syntax.
    assert check_assert_syntax("assert(/* comment */ 1==1);") is True



def test__5555555555_valid_simple():
    # Valid: equality check using variables.
    assert check_assert_syntax("__VERIFIER_assert(aaa==bbb);") is True

def test__5555555555_invalid_assignment():
    # Invalid: assignment inside assert instead of a comparison.
    assert check_assert_syntax("__VERIFIER_assert(a=b);") is True

def test__5555555555_valid_literal_expression():
    # Valid: using a literal expression.
    assert check_assert_syntax("__VERIFIER_assert(1);") is True

def test__5555555555_missing_expression():
    # Invalid: no expression provided.
    assert check_assert_syntax("__VERIFIER_assert();") is False

def test__5555555555_missing_semicolon():
    # Invalid: missing semicolon at the end of the assert statement.
    assert check_assert_syntax("__VERIFIER_assert(a==b)") is False

def test__5555555555_valid_complex_expression():
    # Valid: complex expression using logical operators.
    assert check_assert_syntax("__VERIFIER_assert((a==b) && (c==d));") is True


def test__5555555555_extra_whitespace():
    # Valid: extra whitespace should not affect the syntax.
    assert check_assert_syntax("   __VERIFIER_assert( 1==1 );   ") is True
 
def test__5555555555_comment_inside_expression():
    # Valid: a comment inside the expression should not break syntax.
    assert check_assert_syntax("__VERIFIER_assert(/* comment */ 1==1);") is True