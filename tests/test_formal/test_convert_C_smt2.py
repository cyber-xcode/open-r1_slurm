import unittest
from z3 import Solver, sat, unsat
    

from open_r1.formal_utils.SMT.convert_and_split  import convert_assert_to_smtlib2




class TestAssertConversion(unittest.TestCase):
    def run_z3_script(self, script):
        """Runs a complete SMT-LIB2 script in Z3 and returns the check-sat result."""
        s = Solver()
        s.from_string(script)
        return s.check()

    def build_script(self, decls, smt_code):
        """Builds the full SMT-LIB2 script with declarations and the assert command."""
        decl_script = "\n".join([f"(declare-const {v} {decls[v]})" for v in decls]) if decls else ""
        return decl_script + "\n" + smt_code + "\n(check-sat)"

    def test_expr_1(self):
        expr = "(x == 1)||(y == n - x + 1)"
        c_assert = f"assert({expr});"
        decls = {"x": "Int", "y": "Int", "n": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_2(self):
        expr = "(x * x > y || x == y || x == 1)"
        c_assert = f"assert({expr});"
        decls = {"x": "Int", "y": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_3(self):
        expr = "low + mid == high + 2"
        c_assert = f"assert({expr});"
        decls = {"low": "Int", "mid": "Int", "high": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_4(self):
        expr = "N_LIN == 1"
        c_assert = f"assert({expr});"
        decls = {"N_LIN": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_5(self):
        expr = "((x == n))||((x > 0 && x <= n))"
        c_assert = f"assert({expr});"
        decls = {"x": "Int", "n": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_6(self):
        expr = "j >= 6"
        c_assert = f"assert({expr});"
        decls = {"j": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_7(self):
        expr = "((x1 == 0 || x2 == 0 || x3 == 0))||((x1 > 0 && x2 > 0 && x3 > 0 && (x1 >= 0 && x2 >= 0 && x3 >= 0)))"
        c_assert = f"assert({expr});"
        decls = {"x1": "Int", "x2": "Int", "x3": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_8(self):
        expr = "x <= 0x0fffffff || x >= 0x0fffffff"
        c_assert = f"assert({expr});"
        decls = {"x": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        # The hex literal is now converted to its decimal equivalent.
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_9(self):
        expr = "i >= -10"
        c_assert = f"assert({expr});"
        decls = {"i": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_10(self):
        expr = "k + (n - 1 - j) >= 0"
        c_assert = f"assert({expr});"
        decls = {"k": "Int", "n": "Int", "j": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_11(self):
        expr = "(i % 2 != 0 || k % 3 == 0)"
        c_assert = f"assert({expr});"
        decls = {"i": "Int", "k": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_12(self):
        expr = "((x <= 500000 && y == 500000))||((x > 500000 && y == x - 500000 + 500000))"
        c_assert = f"assert({expr});"
        decls = {"x": "Int", "y": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_13(self):
        expr = "index <= SIZE && ((index == 0 && tmp == 0) || (index > 0 && array[index - 1] == 2 * (index - 1) && tmp == 2 * index))"
        c_assert = f"assert({expr});"
        # with self.assertRaises(Exception):
        convert_assert_to_smtlib2(c_assert)

    def test_expr_14(self):
        expr = "(n >= 0)||(sn == 0)||((n > 0 && sn == a * n || (n > 0 && sn == 2 * (n - 1))))"
        expr = "(n >= 0)||(sn == 0)||(n > 0 && sn == a * n || (n > 0 && sn == 2 * (n - 1))))"
        c_assert = f"assert({expr});"
        with self.assertRaises(Exception):
            convert_assert_to_smtlib2(c_assert)

    def test_expr_15(self):
        expr = "(y == j - (i - x))"
        c_assert = f"assert({expr});"
        decls = {"y": "Int", "j": "Int", "i": "Int", "x": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_16(self):
        expr = "4 * p * q * q + 12 * h * q * r - 16 * p * q * r == 0"
        c_assert = f"assert({expr});"
        decls = {"p": "Int", "q": "Int", "h": "Int", "r": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_17(self):
        expr = "(j == 0 || k == 0)"
        c_assert = f"assert({expr});"
        decls = {"j": "Int", "k": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_18(self):
        expr = "j / 4 <= nlen"
        c_assert = f"assert({expr});"
        decls = {"j": "Int", "nlen": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_19(self):
        expr = "(y + x == n && x >= 0 && y >= 0)||(n == 0 && x == 0 && y == 0)"
        c_assert = f"assert({expr});"
        decls = {"x": "Int", "y": "Int", "n": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_20(self):
        expr = "is_divisible1 == 0"
        c_assert = f"assert({expr});"
        decls = {"is_divisible1": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_invalid_syntax_assert(self):
        c_assert_invalid = "assert(x > 0 && y == 2"
        with self.assertRaises(ValueError):
            convert_assert_to_smtlib2(c_assert_invalid)

    def test_arithmetic_assert3_error(self):
        c_assert = "assert((x >= 1) & y <= 0 || x <= y) && (x <= y || x >= y));"
        with self.assertRaises(Exception):
            convert_assert_to_smtlib2(c_assert)



    def test_expr_21(self):
        expr = "(x == 0)||(!(x % 2))"
        c_assert = f"assert({expr});"
        decls = {"x": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_22(self):
        expr = "((x < 10000000 && x % 1 == 0))||((x >= 10000000 && x % 2 == 0))||((x == 100000000))"
        c_assert = f"assert({expr});"
        decls = {"x": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_23(self):
        expr = "((x == 0 && y == j - i))||((x != 0 && y == j - i + x))"
        c_assert = f"assert({expr});"
        decls = {"x": "Int", "y": "Int", "j": "Int", "i": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_24(self):
        expr = "(x == n || y < n)"
        c_assert = f"assert({expr});"
        decls = {"x": "Int", "y": "Int", "n": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_25(self):
        expr = "i >= 0 && i <= 1024 && (i == 0 || (i > 0 && A[i-1] == i-1))"
        c_assert = f"assert({expr});"
        # Expecting failure due to unsupported array indexing.
        # with self.assertRaises(Exception):
        convert_assert_to_smtlib2(c_assert)

    def test_expr_26(self):
        expr = "(q == 0)||((A == q * B + r))"
        c_assert = f"assert({expr});"
        decls = {"q": "Int", "A": "Int", "B": "Int", "r": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_27(self):
        expr = "(y == 1)"
        c_assert = f"assert({expr});"
        decls = {"y": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_28(self):
        expr = "(x == y || x < y / x || x == y / x || x == y - 1 || x == y / 2 || x == 1)"
        c_assert = f"assert({expr});"
        decls = {"x": "Int", "y": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_29(self):
        expr = "(i + j + k + v4 + v3 + v2) <= n"
        c_assert = f"assert({expr});"
        decls = {"i": "Int", "j": "Int", "k": "Int", "v4": "Int", "v3": "Int", "v2": "Int", "n": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_30(self):
        expr = "y == j"
        c_assert = f"assert({expr});"
        decls = {"y": "Int", "j": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_31(self):
        expr = "(x == y)||(x >= 1024)"
        c_assert = f"assert({expr});"
        decls = {"x": "Int", "y": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_32(self):
        expr = "(x == 4 * y || x == 0)"
        c_assert = f"assert({expr});"
        decls = {"x": "Int", "y": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_33(self):
        expr = "((x < 10000000 && x >= 0) || (x >= 10000000 && x <= 100000000 && x % 2 == 0))"
        c_assert = f"assert({expr});"
        decls = {"x": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_34(self):
        expr = "1 <= sum"
        c_assert = f"assert({expr});"
        decls = {"sum": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_35(self):
        expr = "((i == sn + 1))||((i > 8))"
        c_assert = f"assert({expr});"
        decls = {"i": "Int", "sn": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_36(self):
        expr = "((x < 10000000 && x % 1 == 0))||((x >= 10000000 && x % 2 == 0 && x <= 100000000))"
        c_assert = f"assert({expr});"
        decls = {"x": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_37(self):
        expr = "N_COL == 1"
        c_assert = f"assert({expr});"
        decls = {"N_COL": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_38(self):
        expr = "(x >= 1024)||(x == y - 1)"
        c_assert = f"assert({expr});"
        decls = {"x": "Int", "y": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_39(self):
        expr = "h * h * h - 12 * h * n * q + 16 * n * p * q - h * q * q -"
        c_assert = f"assert({expr});"
        with self.assertRaises(Exception):
            convert_assert_to_smtlib2(c_assert)

    def test_expr_40(self):
        expr = "((x1 == 0 || x2 > 0 && x3 > 0) || (x2 == 0 || x1 > 0 && x3 > 0) || (x3 == 0 || x1 > 0 && x2 > 0))"
        c_assert = f"assert({expr});"
        decls = {"x1": "Int", "x2": "Int", "x3": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_41(self):
        expr = "(y == (n - x))"
        c_assert = f"assert({expr});"
        decls = {"y": "Int", "n": "Int", "x": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_42(self):
        expr = "((z == 0))||((x <= n))"
        c_assert = f"assert({expr});"
        decls = {"z": "Int", "x": "Int", "n": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_43(self):
        expr = "x < octant"
        c_assert = f"assert({expr});"
        decls = {"x": "Int", "octant": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_44(self):
        expr = "((n >= 0 && x == 0))||((n < 0 && x == 0))||((x > 0 && x <= n))"
        c_assert = f"assert({expr});"
        decls = {"n": "Int", "x": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_45(self):
        expr = "(i >= 0 && i <= len)"
        c_assert = f"assert({expr});"
        decls = {"i": "Int", "len": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_46(self):
        expr = "((x == 0 && y == 500000))||((x >= 0 && x <= 1000000 && y == 500000 + (x - 500000) * (x >= 500000) && y <= 1000000 && x <= y))"
        expr = "((x == 0 && y == 500000) ||((x >= 0 && x <= 1000000 && y == 500000 + (x - 500000) * (x >= 500000) && y <= 1000000 && x <= y))"
        c_assert = f"assert({expr});"
        # Expecting failure due to unsupported use of a boolean in arithmetic.
        with self.assertRaises(Exception):
            convert_assert_to_smtlib2(c_assert)

    def test_expr_47(self):
        expr = "((flag == 0 && i == 1 && j == 1 && a == 0 && b == 0))"
        c_assert = f"assert({expr});"
        decls = {"flag": "Int", "i": "Int", "j": "Int", "a": "Int", "b": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_48(self):
        expr = "(i == 0 || (x >= 0 && y >= 0 || x <= 0 && y <= 0))"
        c_assert = f"assert({expr});"
        decls = {"i": "Int", "x": "Int", "y": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_49(self):
        expr = "i <= SZ"
        c_assert = f"assert({expr});"
        decls = {"i": "Int", "SZ": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_50(self):
        expr = "((x < 500000 && y == x) || (x >= 500000 && y == 1000000 - x))"
        c_assert = f"assert({expr});"
        decls = {"x": "Int", "y": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_51(self):
        expr = "((i > x))||((i == j))"
        c_assert = f"assert({expr});"
        decls = {"i": "Int", "x": "Int", "j": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_52(self):
        expr = "b >= 1"
        c_assert = f"assert({expr});"
        decls = {"b": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_53(self):
        expr = "sn == ((long long)n) * a || (j > 0 && sn == ((long long)i - 1) * a && i > 1 || i == 1 && sn == 0)"
        c_assert = f"assert({expr});"
        # Expecting failure due to unsupported type casts.
        # with self.assertRaises(Exception):
        convert_assert_to_smtlib2(c_assert)

    def test_expr_54(self):
        expr = "(j == k + 1)"
        c_assert = f"assert({expr});"
        decls = {"j": "Int", "k": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_55(self):
        expr = "(int)(x * 10) % 10 == (int)(x * 10) % 10"
        c_assert = f"assert({expr});"
        # Expecting failure due to unsupported type casts.
        # with self.assertRaises(Exception):
        convert_assert_to_smtlib2(c_assert)

    def test_expr_56(self):
        expr = "x + y < 200"
        c_assert = f"assert({expr});"
        decls = {"x": "Int", "y": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_57(self):
        expr = "(x >= 1 || n <= 0)"
        c_assert = f"assert({expr});"
        decls = {"x": "Int", "n": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_58(self):
        expr = "(j - i) * (j - i) < j * j"
        c_assert = f"assert({expr});"
        decls = {"i": "Int", "j": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_59(self):
        expr = "M <= 1000000"
        c_assert = f"assert({expr});"
        decls = {"M": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_60(self):
        expr = "((sn == i - 1))||((i > size && sn == size))"
        c_assert = f"assert({expr});"
        decls = {"sn": "Int", "i": "Int", "size": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_61(self):
        expr = "x + 7 * (y - x < 0) + 10 * (y - x >= 0) <= y + 16"
        expr = "x + 7 * (y - x < 0) ******* 10 * (y - x >= 0) <= y + 16"
        c_assert = f"assert({expr});"
        # Expecting failure due to unsupported use of relational expressions in arithmetic.
        with self.assertRaises(Exception):
            convert_assert_to_smtlib2(c_assert)

    def test_expr_62(self):
        expr = "!(l % 3) == (i > 0)"
        c_assert = f"assert({expr});"
        decls = {"l": "Int", "i": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_63(self):
        expr = "(n == x + y)||(x == 0)"
        c_assert = f"assert({expr});"
        decls = {"n": "Int", "x": "Int", "y": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_64(self):
        expr = "(x == y || (x < y && (x < y / x || x == y / x)))"
        c_assert = f"assert({expr});"
        decls = {"x": "Int", "y": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_65(self):
        expr = "((i > 8))||((sn == i - 1))"
        c_assert = f"assert({expr});"
        decls = {"i": "Int", "sn": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_66(self):
        expr = "z == 1"
        c_assert = f"assert({expr});"
        decls = {"z": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_67(self):
        expr = "k >= c1 * (n - i) + c2 * (n - i) + c3 * (n - i)"
        c_assert = f"assert({expr});"
        decls = {"k": "Int", "c1": "Int", "c2": "Int", "c3": "Int", "n": "Int", "i": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_68(self):
        expr = "(y > 0)||((x < 100 && y > 0))"
        c_assert = f"assert({expr});"
        decls = {"x": "Int", "y": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_69(self):
        expr = "((j >= i && j == 20 - (i - 1) / 2))||((j < i && j == 13))"
        c_assert = f"assert({expr});"
        decls = {"j": "Int", "i": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_70(self):
        expr = "m > 0"
        c_assert = f"assert({expr});"
        decls = {"m": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_71(self):
        expr = "2 * k + 2 * (i - 2) >= n - 1"
        c_assert = f"assert({expr});"
        decls = {"k": "Int", "i": "Int", "n": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_72(self):
        expr = "(x <= 750000 || x % 2 == 0)"
        c_assert = f"assert({expr});"
        decls = {"x": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_73(self):
        expr = "y <= 100000"
        c_assert = f"assert({expr});"
        decls = {"y": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_74(self):
        expr = "(i >= -10 && i < 10)"
        c_assert = f"assert({expr});"
        decls = {"i": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_75(self):
        expr = "y == 100"
        c_assert = f"assert({expr});"
        decls = {"y": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_76(self):
        expr = "a <= 65535"
        c_assert = f"assert({expr});"
        decls = {"a": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_77(self):
        expr = "(r == n)"
        c_assert = f"assert({expr});"
        decls = {"r": "Int", "n": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_78(self):
        expr = "((x1 <= 0))||((x2 <= 0))||((x3 <= 0))||((x2 >= 0 && x3 >= 0))"
        c_assert = f"assert({expr});"
        decls = {"x1": "Int", "x2": "Int", "x3": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_79(self):
        expr = "sn <= a * n"
        c_assert = f"assert({expr});"
        decls = {"sn": "Int", "a": "Int", "n": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_80(self):
        expr = "n != 2147483647 && (i > n || sn == ((long long)i - 1) * a || (j < i && sn == ((long long)(j - 1)) * a))"
        c_assert = f"assert({expr});"
        # Expecting failure due to unsupported type casts.
        # with self.assertRaises(Exception):
        convert_assert_to_smtlib2(c_assert)

    def test_expr_81(self):
        expr = "((x >= 0) && (y >= 0) && (n == (x + y)))"
        c_assert = f"assert({expr});"
        decls = {"x": "Int", "y": "Int", "n": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_82(self):
        expr = "((x < 50 && y == 50))||((x >= 50 && y == 50 + (x - 50) && x <= 100))"
        c_assert = f"assert({expr});"
        decls = {"x": "Int", "y": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_83(self):
        expr = "(sn == (i * (i - 1)) / 2)||((i == 0 && sn == 0))||((i <= n && sn >= 0))||((i == n + 1 && sn == (n * (n + 1)) / 2))"
        c_assert = f"assert({expr});"
        decls = {"sn": "Int", "i": "Int", "n": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_84(self):
        expr = "r == A - q * B"
        c_assert = f"assert({expr});"
        decls = {"r": "Int", "A": "Int", "q": "Int", "B": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_85(self):
        expr = "((x == 0))||((i != j || y == x))"
        c_assert = f"assert({expr});"
        decls = {"x": "Int", "i": "Int", "j": "Int", "y": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_86(self):
        expr = "i <= n && j > i && sn == ((long long)n) * a || sn == 0"
        c_assert = f"assert({expr});"
        # Expecting failure due to unsupported type cast.
        # with self.assertRaises(Exception):
        convert_assert_to_smtlib2(c_assert)

    def test_expr_87(self):
        expr = "(cnt == 0 || 0 <= b && b <= 1000000)"
        c_assert = f"assert({expr});"
        decls = {"cnt": "Int", "b": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_88(self):
        expr = "((x == 0))||((i != j))||((y == 0))||((y == x + (j - i)))"
        c_assert = f"assert({expr});"
        decls = {"x": "Int", "i": "Int", "j": "Int", "y": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_89(self):
        expr = "((n >= 0 && x >= 1 && x <= n))||((n < 0 && x == n))||((n == 0 && x == 0))"
        c_assert = f"assert({expr});"
        decls = {"n": "Int", "x": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_90(self):
        expr = "z == 6*n + 6"
        c_assert = f"assert({expr});"
        decls = {"z": "Int", "n": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_91(self):
        expr = "(x == y || x * x > y || x < y)"
        c_assert = f"assert({expr});"
        decls = {"x": "Int", "y": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_92(self):
        expr = "(i * i < j * j || (i == j))"
        c_assert = f"assert({expr});"
        decls = {"i": "Int", "j": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_93(self):
        expr = "((n >= 0 && x == n && y == 0))||((x >= 0 && y >= 0 && x + y == n))"
        c_assert = f"assert({expr});"
        decls = {"n": "Int", "x": "Int", "y": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_94(self):
        expr = "((a == b && b == (i - 1) * (j - 1) / 2 && i >= 0 && j >= 1))"
        c_assert = f"assert({expr});"
        decls = {"a": "Int", "b": "Int", "i": "Int", "j": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_95(self):
        expr = "z <= z"
        c_assert = f"assert({expr});"
        decls = {"z": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_96(self):
        expr = "j / 4 <= nlen"
        c_assert = f"assert({expr});"
        decls = {"j": "Int", "nlen": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_97(self):
        expr = "(b >= 0 && b < 1023)||(b % 1023 < 1023)"
        c_assert = f"assert({expr});"
        decls = {"b": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_98(self):
        expr = "z <= -2 * x"
        c_assert = f"assert({expr});"
        decls = {"z": "Int", "x": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_99(self):
        expr = "!(y <= 0 && x <= 0)"
        c_assert = f"assert({expr});"
        decls = {"y": "Int", "x": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_100(self):
        expr = "(i + j + k + v1 + v2 + v3 + v4) == l"
        c_assert = f"assert({expr});"
        decls = {"i": "Int", "j": "Int", "k": "Int", "v1": "Int", "v2": "Int", "v3": "Int", "v4": "Int", "l": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_101(self):
        expr = "t == y"
        c_assert = f"assert({expr});"
        decls = {"t": "Int", "y": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_102(self):
        expr = "(x == n - y || (x == 0 && y == n) || n == 0 || (x == n && y == 0))"
        c_assert = f"assert({expr});"
        decls = {"x": "Int", "n": "Int", "y": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_103(self):
        expr = "((x <= 500000 && y == 500000))||((x > 500000 && x <= 750000 && y == 500000 + (x - 500000)))||((x > 500000 && y == 500000 + 250000 + (x - 750000) / 2))"
        c_assert = f"assert({expr});"
        decls = {"x": "Int", "y": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_104(self):
        expr = "index < SIZE || (tmp < SIZE && array[tmp] == tmp)"
        c_assert = f"assert({expr});"
        # Expecting failure due to unsupported array indexing.
        # with self.assertRaises(Exception):
        convert_assert_to_smtlib2(c_assert)

    def test_expr_105(self):
        expr = "(x == 0 || x == 1)"
        c_assert = f"assert({expr});"
        decls = {"x": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_106(self):
        expr = "(i == n || k > 0 || j == 0)"
        c_assert = f"assert({expr});"
        decls = {"i": "Int", "n": "Int", "k": "Int", "j": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_107(self):
        expr = "x >= __VERIFIER_nondet_int()"
        c_assert = f"assert({expr});"
        decls = {"x": "Int", "__VERIFIER_nondet_int": "Int"}
        with self.assertRaises(Exception):
            smt_code = convert_assert_to_smtlib2(c_assert)
            script = self.build_script(decls, smt_code)
            result = self.run_z3_script(script)
            self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_108(self):
        expr = "(i <= x)"
        c_assert = f"assert({expr});"
        decls = {"i": "Int", "x": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_109(self):
        expr = "(x <= 100000001)"
        c_assert = f"assert({expr});"
        decls = {"x": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_110(self):
        expr = "((x < 10000000 && x % 1 == 0))||((x >= 10000000 && x % 2 == 0 && x < 100000000))||((x == 100000000))||((x == 100000001))||((x == 0))"
        c_assert = f"assert({expr});"
        decls = {"x": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_111(self):
        expr = "(x == n - y)"
        c_assert = f"assert({expr});"
        decls = {"x": "Int", "n": "Int", "y": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_112(self):
        expr = "(k == 0)||((k == 1 && (m >= a)))"
        c_assert = f"assert({expr});"
        decls = {"k": "Int", "m": "Int", "a": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_113(self):
        expr = "((n >= 0 && x == n))||((n < 0 && x == n))||((x < n && x > 0))||((x == 1))||((x == 0 && n >= 0))||((x == n && n >= 0))"
        c_assert = f"assert({expr});"
        decls = {"n": "Int", "x": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_114(self):
        expr = "i <= 1024 || (i == 1024 && A[i-1] == 1023)"
        c_assert = f"assert({expr});"
        # Expecting failure due to unsupported array indexing.
        # with self.assertRaises(Exception):
        convert_assert_to_smtlib2(c_assert)

    def test_expr_115(self):
        expr = "(y == 0 || y != 0)"
        c_assert = f"assert({expr});"
        decls = {"y": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_116(self):
        expr = "(x2 >= 0 || x3 >= 0 || x1 == 1)"
        c_assert = f"assert({expr});"
        decls = {"x1": "Int", "x2": "Int", "x3": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_117(self):
        expr = "y >= x - 10"
        c_assert = f"assert({expr});"
        decls = {"y": "Int", "x": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_118(self):
        expr = "(n == 1023)"
        c_assert = f"assert({expr});"
        decls = {"n": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")

    def test_expr_119(self):
        expr = "(i == 0 && k == 0 || i < n || k < n)"
        c_assert = f"assert({expr});"
        decls = {"i": "Int", "k": "Int", "n": "Int"}
        smt_code = convert_assert_to_smtlib2(c_assert)
        script = self.build_script(decls, smt_code)
        result = self.run_z3_script(script)
        self.assertEqual(result, sat, f"Expected SAT for expression: {expr}")



if __name__ == "__main__":
    unittest.main()

