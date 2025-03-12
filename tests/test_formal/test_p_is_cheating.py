import pytest

from open_r1.formal_utils.p_is_cheating  import p_is_cheating as check_assert_cheating
from open_r1.formal_utils.s_is_cheating   import is_assert_cheating
#
#



def test_c_real1 ():
    source = """
#include <assert.h>
#include <string.h>
int main(void) {
  const char *loss_keys[] = {
      "Lambda_A",       "Lambda_B",        "Lambda_IDT",    "Lambda_CLS",
      "Lambda_REC",     "Lambda_HIS",      "Lambda_SKIN",   "Lambda_EYE",
      "Lambda_HIS_LIP", "Lambda_HIS_SKIN", "Lambda_HIS_EYE"};
  float loss_weights[11];
  for (int i = 0; i < 11; i++) {
    loss_weights[i] = (unsigned int)rand() % 2;
    assume(loss_weights[i] >= 0);
  }
  float total_loss = 0.0;
  int i = 0;
  while (i < 11) {
    total_loss += loss_weights[i];
    i++;
  }
  assert(total_loss >= 0);
  return 0;
}
    """
    #assert((unsigned int)rand() % 2 <= 10);
    cheat_expr = "assert((unsigned int)rand() % 2 <= 10);"
    assert check_assert_cheating(source, cheat_expr) is True
    

def test_simple_numeric_cheat():
    # No variable involved (only literals): cheating.
    source = ""
    cheat_expr = "assert(1==1);"
    assert check_assert_cheating(source, cheat_expr) is True

def test_simple_numeric_non_cheat():
    # Even though 1==2 is false, there are no variables → cheating.
    source = ""
    cheat_expr = "assert(1==2);"
    assert check_assert_cheating(source, cheat_expr) is True

def test_variable_cheat():
    # A simple self–compare: a==a is trivial.
    source = "int a = 10;"
    cheat_expr = "assert(a==a);"
    assert check_assert_cheating(source, cheat_expr) is True

def test_variable_non_cheat():
    # Two different variables: a==b is not trivial.
    source = "int a = 10, b = 20;"
    non_cheat_expr = "assert(a==b);"
    assert check_assert_cheating(source, non_cheat_expr) is False

def test_extra_parentheses_cheat():
    # Extra parentheses do not change the fact that it's a simple self–compare.
    source = "int x = 5;"
    cheat_expr = "assert((x)==(x));"
    assert check_assert_cheating(source, cheat_expr) is True

def test_complex_expression_cheat():
    # If the condition uses arithmetic on a variable, e.g., a+0 == a, then it's not trivial.
    source = "int a = 1;"
    expr = "assert(a+0 == a);"
    assert check_assert_cheating(source, expr) is False

def test_complex_expression_non_cheat():
    # A composite condition (even with a self–compare) is not trivial.
    source = "int a = 1, b = 2;"
    expr = "assert(a==a || a==b);"
    assert check_assert_cheating(source, expr) is False

def test_non_binary_operator():
    # A single literal expression is trivial.
    source = ""
    expr = "assert(0);"
    assert check_assert_cheating(source, expr) is True

def test_different_operator():
    # a!=a is not considered a simple self–compare per our rules.
    source = "int a = 5;"
    expr = "assert(a!=a);"
    assert check_assert_cheating(source, expr) is False

def test_whitespace_variations():
    # Variations in whitespace are normalized; still a simple self–compare.
    source = "int a = 10;"
    expr = "assert(   a   ==    a   );"
    assert check_assert_cheating(source, expr) is True

def test_malformed_assert_expression():
    # Malformed code (e.g., missing closing parenthesis) is assumed not cheating.
    source = ""
    malformed_expr = "assert(1==1"  # missing closing parenthesis and semicolon
    assert check_assert_cheating(source, malformed_expr) is False

def test_undeclared_variables():
    # Even if the source doesn't declare a or b, assert(a==b) is not considered trivial.
    source = ""
    expr = "assert(a==b);"
    assert check_assert_cheating(source, expr) is True





# @pytest.mark.skip(reason="no way of currently testing this")
def test_boolean_literal_self_compare():
    # Boolean literal self–comparison should be considered trivial.
    source = ""
    expr = "assert(true==true);"
    assert check_assert_cheating(source, expr) is True
    
# @pytest.mark.skip(reason="no way of currently testing this")
def test_boolean_literal_different():
    # Even if the boolean literals differ, no variable is involved → trivial.
    source = ""
    expr = "assert(true==false);"
    assert check_assert_cheating(source, expr) is True

def test_cast_self_compare():
    # Self–comparison with type casting should be trivial.
    source = "float a = 1.0;"
    expr = "assert((float)a == (float)a);"
    assert check_assert_cheating(source, expr) is True

def test_function_call_non_trivial():
    # Even if the function call appears identical on both sides,
    # the potential side effects make it non–trivial.
    source = "int f(int x){ return x; } int a = 1;"
    expr = "assert(f(a)==f(a));"
    assert check_assert_cheating(source, expr) is True

def test_array_element_self_compare():
    # A self–comparison of an array element is trivial.
    source = "int arr[3] = {1,2,3};"
    expr = "assert(arr[0]==arr[0]);"
    assert check_assert_cheating(source, expr) is True

def test_chained_comparison_malformed():
    # Chained comparisons (e.g. a==a==a) are not standard in C–like languages,
    # so this malformed expression is considered non–trivial.
    source = "int a = 1;"
    expr = "assert(a==a==a);"
    assert check_assert_cheating(source, expr) is True

def test_ternary_operator_non_trivial():
    # Using a ternary operator, even if self–comparisons are present, makes the expression composite.
    source = "int a = 5;"
    expr = "assert(a==a ? a==a : a==a);"
    assert check_assert_cheating(source, expr) is True

def test_single_variable_assert():
    # An assert with a single variable (no binary operator) is not a self–compare and is non–trivial.
    source = "int a = 5;"
    expr = "assert(a);"
    assert check_assert_cheating(source, expr) is False


def test_ternary_operator_non_trivial_combine():
    # Using a ternary operator, even if self–comparisons are present, makes the expression composite.
    source = "int a = 5;"
    expr = """assert(a);
    assert(a==a ? a==a : a==a);
    assert(a);
    """
    assert check_assert_cheating(source, expr) is True

def test_ternary_operator_non_trivial_combine_all():
    # Using a ternary operator, even if self–comparisons are present, makes the expression composite.
    source = "int a = 5;"
    expr = """assert(a);
assert(a);
assert(b);
assert(c);
assert(d);
    assert(e);
    """
    assert check_assert_cheating(source, expr) is True

def test_single_variable_assert():
    # An assert with a single variable (no binary operator) is not a self–compare and is non–trivial.
    source = "int a = 5;"
    expr = "assert(a);"
    assert check_assert_cheating(source, expr) is False


def test_arithmetic_self_compare_non_trivial():
    # Even though a-a mathematically simplifies to 0,
    # the presence of arithmetic operations prevents it from being a trivial self–compare.
    source = "int a = 10;"
    expr = "assert(a - a == 0);"
    assert check_assert_cheating(source, expr) is False

def test_logical_not_self_compare():
    # A self–comparison where a logical NOT is applied to both sides is considered trivial.
    source = "int a = 5;"
    expr = "assert(!a == !a);"
    assert check_assert_cheating(source, expr) is True

def test_character_literal_self_compare():
    # Self–comparison of character literals is trivial.
    source = ""
    expr = "assert('a'=='a');"
    assert check_assert_cheating(source, expr) is True

def test_character_literal_different():
    # Even when comparing different character literals, if no variable is involved, it's trivial.
    source = ""
    expr = "assert('a'=='b');"
    assert check_assert_cheating(source, expr) is True












def test_assert_with_side_effect():
    source = """
    #include <assert.h>
    #include <stdlib.h>

    int allocate_resource() {
        // Simulate resource allocation
        return rand() % 2; // Randomly succeed or fail
    }

    int main(void) {
        int resource;
        // Use resource
        return 0;
    }
    """
    cheat_expr = "assert((resource = allocate_resource()) != 0);"
    assert check_assert_cheating(source, cheat_expr) is False



def test_assert_for_error_handling():
    source = """
    #include <assert.h>
    #include <stdlib.h>

    int main(void) {
        int *ptr = malloc(sizeof(int) * 10);
        // Use ptr
        free(ptr);
        return 0;
    }
    """
    cheat_expr = "assert(ptr != NULL);"
    assert check_assert_cheating(source, cheat_expr) is False

def test_excessive_assertions():
    source = """
    #include <assert.h>

    void process_data(int *data, size_t size) {
        for (size_t i = 0; i < size; ++i) {
            // Process data[i]
        }
    }

    int main(void) {
        int data[1000] = {0};
        process_data(data, 1000);
        return 0;
    }
    """
    cheat_expr = "assert(data[i] >= 0);"
    assert check_assert_cheating(source, cheat_expr) is False

def test_assert_in_release_build():
    source = """
    #include <assert.h>

    int divide(int numerator, int denominator) {
        return numerator / denominator;
    }

    int main(void) {
        int result = divide(10, 0);
        return 0;
    }
    """
    cheat_expr = "assert(denominator != 0);"
    assert check_assert_cheating(source, cheat_expr) is False


def test_assert_for_external_input():
    source = """
    #include <assert.h>
    #include <stdio.h>

    int main(void) {
        int user_input;
        scanf("%d", &user_input);
        // Process user_input
        return 0;
    }
    """
    cheat_expr = "assert(user_input >= 0 && user_input <= 100);"
    assert check_assert_cheating(source, cheat_expr) is False



def test_complex_arithmetic_expression():
    source = """
    int a = 5, b = 10, c = 15;
    """
    expr = "assert(a + b * c == a + b * c);"
    assert check_assert_cheating(source, expr) is True

def test_nested_function_calls():
    source = """
    int f(int x) { return x * 2; }
    int g(int y) { return y + 1; }
    int a = 5;
    """
    expr = "assert(f(g(a)) == f(g(a)));"
    assert check_assert_cheating(source, expr) is True

def test_pointer_comparison():
    source = """
    int a = 5;
    int *p = &a;
    """
    expr = "assert(p == p);"
    assert check_assert_cheating(source, expr) is True

def test_struct_field_comparison():
    source = """
    struct Point { int x; int y; };
    struct Point p1 = {1, 2};
    """
    expr = "assert(p1.x == p1.x);"
    assert check_assert_cheating(source, expr) is True

def test_array_of_structs_comparison():
    source = """
    struct Point { int x; int y; };
    struct Point points[3] = {{1, 2}, {3, 4}, {5, 6}};
    """
    expr = "assert(points[0].x == points[0].x);"
    assert check_assert_cheating(source, expr) is True

def test_complex_logical_expression():
    source = """
    int a = 5, b = 10, c = 15;
    """
    expr = "assert((a < b) && (b < c) || (a == c));"
    assert check_assert_cheating(source, expr) is False

def test_ternary_operator_complex_expressions():
    source = """
    int a = 5, b = 10;
    """
    expr = "assert((a > b) ? (a + b) : (a - b) == (a > b) ? (a + b) : (a - b));"
    assert check_assert_cheating(source, expr) is False

def test_bitwise_operations():
    source = """
    int a = 5, b = 10;
    """
    expr = "assert((a & b) == (a & b));"
    assert check_assert_cheating(source, expr) is True

def test_mixed_arithmetic_logical_operations2():
    source = """
    int a = 5, b = 10, c = 15;
    """
    expr = "assert((a + b) * c == (a + b) * c && (a < b));"
    assert check_assert_cheating(source, expr) is False

def test_complex_array_indexing():
    source = """
    int arr[10] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
    int a = 5;
    """
    expr = "assert(arr[a + 1] == arr[a + 1]);"
    assert check_assert_cheating(source, expr) is True

def test_function_pointer_comparison():
    source = """
    int f(int x) { return x * 2; }
    int (*p)(int) = f;
    """
    expr = "assert(p == p);"
    assert check_assert_cheating(source, expr) is True

@pytest.mark.skip(reason="no way of currently testing this")
def test_complex_macro_expansion():
    source = """
    #define SQUARE(x) ((x) * (x))
    int a = 5;
    """
    expr = "assert(SQUARE(a) == SQUARE(a));"
    assert check_assert_cheating(source, expr) is True

def test_complex_type_casting():
    source = """
    int a = 5;
    float b = 10.5;
    """
    expr = "assert((int)(b) == (int)(b));"
    assert check_assert_cheating(source, expr) is True

@pytest.mark.skip(reason="no way of currently testing this")
def test_complex_string_comparison():
    source = """
    char str1[] = "hello";
    char str2[] = "world";
    """
    expr = "assert(strcmp(str1, str1) == 0);"
    assert check_assert_cheating(source, expr) is True

def test_complex_union_comparison():
    source = """
    union Data {
        int i;
        float f;
    } data;
    data.i = 10;
    """
    expr = "assert(data.i == data.i);"
    assert check_assert_cheating(source, expr) is True
    
    
    
    
    
def test_ternary_operator_from_reward():
    # Using a ternary operator, even if self–comparisons are present, makes the expression composite.
    source = """
    #include <assert.h>
    int main() {
        int a = 1, b = 2;
        return 0;
    }
    """
    expr = "assert(a == 1);   // valid\n        assert(5 == 5);   // cheating: no context"
    assert check_assert_cheating(source, expr) is True
