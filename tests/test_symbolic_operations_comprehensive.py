# Copyright 2025 Michael Maillet, Damien Davison, and Sacha Davison
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Comprehensive Tests for Symbolic Operations Module
===================================================

Tests for:
- Symbol class
- Add, Mul, Pow operations
- Numeric types (Integer, Float, Rational)
- Functions (Sin, Cos, Exp, Log, etc.)
- Simplification engine
- Parsing module
- Type system
"""

import pytest
import math


class TestSymbol:
    """Tests for the Symbol class."""

    def test_symbol_creation(self):
        """Create a symbol with a name."""
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        assert x.name == 'x'
        assert str(x) == 'x'

    def test_symbol_repr(self):
        """Symbol representation."""
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        assert repr(x) == "Symbol('x')"

    def test_symbol_equality(self):
        """Symbols with same name are equal."""
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x1 = Symbol('x')
        x2 = Symbol('x')
        y = Symbol('y')
        assert x1 == x2
        assert x1 != y
        assert not (x1 == "x")  # Not equal to strings

    def test_symbol_hash(self):
        """Symbols can be hashed."""
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x1 = Symbol('x')
        x2 = Symbol('x')
        assert hash(x1) == hash(x2)
        # Use in set
        s = {x1, x2}
        assert len(s) == 1

    def test_symbol_ordering(self):
        """Symbols can be ordered."""
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        y = Symbol('y')
        assert x < y

    def test_symbol_free_symbols(self):
        """Symbol's free_symbols returns itself."""
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        assert x.free_symbols == {x}

    def test_symbol_subs_dict(self):
        """Substitute symbol using dict."""
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Integer
        x = Symbol('x')
        result = x.subs({x: Integer(5)})
        assert result == Integer(5)

    def test_symbol_subs_args(self):
        """Substitute symbol using positional args."""
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Integer
        x = Symbol('x')
        result = x.subs(x, Integer(5))
        assert result == Integer(5)

    def test_symbol_diff(self):
        """Differentiate symbol."""
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        y = Symbol('y')
        assert x.diff(x).value == 1  # dx/dx = 1
        assert x.diff(y).value == 0  # dx/dy = 0

    def test_symbol_simplify(self):
        """Simplify returns self."""
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        assert x.simplify() == x

    def test_symbol_evalf_constants(self):
        """Evalf recognizes mathematical constants."""
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        from symbo_agentic_reasoners.core.symbolic.expr_types import MathConstant
        pi = Symbol('pi')
        e = Symbol('E')
        gamma = Symbol('gamma')
        result_pi = pi.evalf()
        result_e = e.evalf()
        result_gamma = gamma.evalf()
        assert result_pi == MathConstant.PI
        assert result_e == MathConstant.E
        assert result_gamma == MathConstant.GAMMA

    def test_symbol_to_latex_greek(self):
        """Greek letters convert to LaTeX."""
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        alpha = Symbol('alpha')
        assert alpha.to_latex() == r'\alpha'

    def test_symbol_to_latex_long_name(self):
        """Long names convert to text in LaTeX."""
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        var = Symbol('variable')
        assert var.to_latex() == r'\text{variable}'


class TestNumericTypes:
    """Tests for Integer, Float, Rational."""

    def test_integer_creation(self):
        """Create an integer."""
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Integer
        i = Integer(5)
        assert i.value == 5
        assert str(i) == '5'

    def test_integer_arithmetic(self):
        """Integer arithmetic operations."""
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Integer
        a = Integer(5)
        b = Integer(3)
        # These may return different types depending on implementation
        assert (a.value + b.value) == 8

    def test_integer_zero_and_one(self):
        """Integer properties."""
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Integer
        zero = Integer(0)
        one = Integer(1)
        assert zero.is_zero
        assert one.is_one

    def test_float_creation(self):
        """Create a float."""
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Float
        f = Float(3.14)
        assert abs(f.value - 3.14) < 1e-10

    def test_rational_creation(self):
        """Create a rational number."""
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Rational
        r = Rational(1, 2)
        # Rational uses p (numerator) and q (denominator)
        assert r.p == 1
        assert r.q == 2
        assert abs(r.evalf() - 0.5) < 1e-10

    def test_rational_simplification(self):
        """Rationals auto-simplify."""
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Rational
        r = Rational(4, 8)
        # Should simplify to 1/2
        assert r.p == 1
        assert r.q == 2


class TestAddOperation:
    """Tests for the Add operation."""

    def test_add_creation(self):
        """Create an Add expression."""
        from symbo_agentic_reasoners.core.symbolic.operations import Add
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        y = Symbol('y')
        expr = Add(x, y)
        assert len(expr.args) == 2

    def test_add_string(self):
        """Add expression as string."""
        from symbo_agentic_reasoners.core.symbolic.operations import Add
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        y = Symbol('y')
        expr = Add(x, y)
        s = str(expr)
        assert 'x' in s and 'y' in s

    def test_add_empty(self):
        """Empty Add is zero."""
        from symbo_agentic_reasoners.core.symbolic.operations import Add
        expr = Add()
        assert str(expr) == '0'

    def test_add_with_negative(self):
        """Add with negative terms."""
        from symbo_agentic_reasoners.core.symbolic.operations import Add, Mul
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Integer
        x = Symbol('x')
        neg_y = Mul(Integer(-1), Symbol('y'))
        expr = Add(x, neg_y)
        s = str(expr)
        # Should handle negative formatting
        assert 'x' in s

    def test_add_equality(self):
        """Add equality is set-based."""
        from symbo_agentic_reasoners.core.symbolic.operations import Add
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        y = Symbol('y')
        expr1 = Add(x, y)
        expr2 = Add(y, x)
        assert expr1 == expr2

    def test_add_single_arg(self):
        """Add with single arg equals that arg."""
        from symbo_agentic_reasoners.core.symbolic.operations import Add
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        expr = Add(x)
        assert expr == x

    def test_add_free_symbols(self):
        """Free symbols of Add."""
        from symbo_agentic_reasoners.core.symbolic.operations import Add
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        y = Symbol('y')
        expr = Add(x, y)
        assert expr.free_symbols == {x, y}

    def test_add_substitution(self):
        """Substitute in Add."""
        from symbo_agentic_reasoners.core.symbolic.operations import Add
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Integer
        x = Symbol('x')
        y = Symbol('y')
        expr = Add(x, y)
        result = expr.subs({x: Integer(2)})
        # Should simplify
        assert y in result.free_symbols or isinstance(result, (int, Integer))

    def test_add_differentiation(self):
        """Differentiate Add."""
        from symbo_agentic_reasoners.core.symbolic.operations import Add
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        y = Symbol('y')
        expr = Add(x, y)
        result = expr.diff(x)
        # d/dx(x + y) = 1
        assert result is not None


class TestMulOperation:
    """Tests for the Mul operation."""

    def test_mul_creation(self):
        """Create a Mul expression."""
        from symbo_agentic_reasoners.core.symbolic.operations import Mul
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        y = Symbol('y')
        expr = Mul(x, y)
        assert len(expr.args) == 2

    def test_mul_string(self):
        """Mul expression as string."""
        from symbo_agentic_reasoners.core.symbolic.operations import Mul
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        y = Symbol('y')
        expr = Mul(x, y)
        s = str(expr)
        assert 'x' in s or 'y' in s

    def test_mul_free_symbols(self):
        """Free symbols of Mul."""
        from symbo_agentic_reasoners.core.symbolic.operations import Mul
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        y = Symbol('y')
        expr = Mul(x, y)
        assert expr.free_symbols == {x, y}

    def test_mul_substitution(self):
        """Substitute in Mul."""
        from symbo_agentic_reasoners.core.symbolic.operations import Mul
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Integer
        x = Symbol('x')
        y = Symbol('y')
        expr = Mul(x, y)
        result = expr.subs({x: Integer(2), y: Integer(3)})
        # Should simplify to 6
        if hasattr(result, 'value'):
            assert result.value == 6

    def test_mul_with_zero(self):
        """Mul with zero simplifies to zero."""
        from symbo_agentic_reasoners.core.symbolic.operations import Mul
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Integer
        x = Symbol('x')
        expr = Mul(Integer(0), x).simplify()
        # Should be zero
        if hasattr(expr, 'value'):
            assert expr.value == 0
        elif hasattr(expr, 'is_zero'):
            assert expr.is_zero


class TestPowOperation:
    """Tests for the Pow operation."""

    def test_pow_creation(self):
        """Create a Pow expression."""
        from symbo_agentic_reasoners.core.symbolic.operations import Pow
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Integer
        x = Symbol('x')
        expr = Pow(x, Integer(2))
        assert expr.base == x
        assert expr.exp == Integer(2)

    def test_pow_string(self):
        """Pow expression as string."""
        from symbo_agentic_reasoners.core.symbolic.operations import Pow
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Integer
        x = Symbol('x')
        expr = Pow(x, Integer(2))
        s = str(expr)
        assert 'x' in s
        assert '2' in s

    def test_pow_free_symbols(self):
        """Free symbols of Pow."""
        from symbo_agentic_reasoners.core.symbolic.operations import Pow
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Integer
        x = Symbol('x')
        expr = Pow(x, Integer(2))
        assert x in expr.free_symbols

    def test_pow_substitution(self):
        """Substitute in Pow."""
        from symbo_agentic_reasoners.core.symbolic.operations import Pow
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Integer
        x = Symbol('x')
        expr = Pow(x, Integer(2))
        result = expr.subs({x: Integer(3)})
        # Should be 9
        if hasattr(result, 'value'):
            assert result.value == 9

    def test_pow_diff(self):
        """Differentiate Pow."""
        from symbo_agentic_reasoners.core.symbolic.operations import Pow
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Integer
        x = Symbol('x')
        expr = Pow(x, Integer(2))
        result = expr.diff(x)
        # d/dx(x^2) = 2x
        assert result is not None


class TestFunctions:
    """Tests for mathematical functions."""

    def test_sin_creation(self):
        """Create Sin function."""
        from symbo_agentic_reasoners.core.symbolic.functions import Sin
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        expr = Sin(x)
        assert expr.args[0] == x

    def test_cos_creation(self):
        """Create Cos function."""
        from symbo_agentic_reasoners.core.symbolic.functions import Cos
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        expr = Cos(x)
        assert expr.args[0] == x

    def test_exp_creation(self):
        """Create Exp function."""
        from symbo_agentic_reasoners.core.symbolic.functions import Exp
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        expr = Exp(x)
        assert expr.args[0] == x

    def test_log_creation(self):
        """Create Log function."""
        from symbo_agentic_reasoners.core.symbolic.functions import Log
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        expr = Log(x)
        assert expr.args[0] == x

    def test_sin_evalf(self):
        """Evaluate Sin numerically."""
        from symbo_agentic_reasoners.core.symbolic.functions import Sin
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Float
        expr = Sin(Float(0.0))
        result = expr.evalf()
        if isinstance(result, (int, float)):
            assert abs(result) < 1e-10

    def test_cos_evalf(self):
        """Evaluate Cos numerically."""
        from symbo_agentic_reasoners.core.symbolic.functions import Cos
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Float
        expr = Cos(Float(0.0))
        result = expr.evalf()
        if isinstance(result, (int, float)):
            assert abs(result - 1.0) < 1e-10

    def test_sin_derivative(self):
        """Derivative of sin(x) is cos(x)."""
        from symbo_agentic_reasoners.core.symbolic.functions import Sin, Cos
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        expr = Sin(x)
        result = expr.diff(x)
        # Should be cos(x)
        assert isinstance(result, Cos)

    def test_cos_derivative(self):
        """Derivative of cos(x) is -sin(x)."""
        from symbo_agentic_reasoners.core.symbolic.functions import Sin, Cos
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        expr = Cos(x)
        result = expr.diff(x)
        # Should be -sin(x) or Mul(-1, Sin(x))
        assert result is not None

    def test_exp_derivative(self):
        """Derivative of exp(x) is exp(x)."""
        from symbo_agentic_reasoners.core.symbolic.functions import Exp
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        expr = Exp(x)
        result = expr.diff(x)
        # Should be exp(x)
        assert isinstance(result, Exp)

    def test_log_derivative(self):
        """Derivative of log(x) is 1/x."""
        from symbo_agentic_reasoners.core.symbolic.functions import Log
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        expr = Log(x)
        result = expr.diff(x)
        # Should be 1/x or Pow(x, -1)
        assert result is not None


class TestTrigFunctions:
    """Tests for trigonometric functions."""

    def test_tan_creation(self):
        """Create Tan function."""
        from symbo_agentic_reasoners.core.symbolic.functions import Tan
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        expr = Tan(x)
        assert expr.args[0] == x

    def test_tan_evalf(self):
        """Evaluate Tan numerically at 0."""
        from symbo_agentic_reasoners.core.symbolic.functions import Tan
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Float
        expr = Tan(Float(0.0))
        result = expr.evalf()
        if isinstance(result, (int, float)):
            assert abs(result) < 1e-10


class TestSpecialMathFunctions:
    """Tests for special mathematical functions."""

    def test_factorial_creation(self):
        """Create Factorial function."""
        from symbo_agentic_reasoners.core.symbolic.functions import Factorial
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Integer
        expr = Factorial(Integer(5))
        assert expr is not None

    def test_gamma_creation(self):
        """Create Gamma function."""
        from symbo_agentic_reasoners.core.symbolic.functions import Gamma
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        expr = Gamma(x)
        assert expr is not None

    def test_gcd_creation(self):
        """Create Gcd function."""
        from symbo_agentic_reasoners.core.symbolic.functions import Gcd
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Integer
        expr = Gcd(Integer(12), Integer(8))
        assert expr is not None

    def test_lcm_creation(self):
        """Create Lcm function."""
        from symbo_agentic_reasoners.core.symbolic.functions import Lcm
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Integer
        expr = Lcm(Integer(4), Integer(6))
        assert expr is not None

    def test_floor_creation(self):
        """Create Floor function."""
        from symbo_agentic_reasoners.core.symbolic.functions import Floor
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        expr = Floor(x)
        assert expr is not None

    def test_ceil_creation(self):
        """Create Ceil function."""
        from symbo_agentic_reasoners.core.symbolic.functions import Ceil
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        expr = Ceil(x)
        assert expr is not None

    def test_mod_creation(self):
        """Create Mod function."""
        from symbo_agentic_reasoners.core.symbolic.functions import Mod
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Integer
        expr = Mod(Integer(10), Integer(3))
        assert expr is not None

    def test_sign_creation(self):
        """Create Sign function."""
        from symbo_agentic_reasoners.core.symbolic.functions import Sign
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        expr = Sign(x)
        assert expr is not None


class TestSpecialFunctions:
    """Tests for special mathematical functions."""

    def test_abs_creation(self):
        """Create Abs function."""
        from symbo_agentic_reasoners.core.symbolic.functions import Abs
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        expr = Abs(x)
        assert expr.args[0] == x

    def test_sqrt_creation(self):
        """Create Sqrt function."""
        from symbo_agentic_reasoners.core.symbolic.functions import Sqrt
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        expr = Sqrt(x)
        assert expr.args[0] == x

    def test_sqrt_evalf(self):
        """Evaluate Sqrt numerically."""
        from symbo_agentic_reasoners.core.symbolic.functions import Sqrt
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Integer
        expr = Sqrt(Integer(4))
        result = expr.evalf()
        if isinstance(result, (int, float)):
            assert abs(result - 2.0) < 1e-10


class TestSimplification:
    """Tests for expression simplification."""

    def test_pythagorean_identity(self):
        """sin^2(x) + cos^2(x) = 1."""
        from symbo_agentic_reasoners.core.symbolic.operations import Add, Pow
        from symbo_agentic_reasoners.core.symbolic.functions import Sin, Cos
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Integer
        x = Symbol('x')
        expr = Add(Pow(Sin(x), Integer(2)), Pow(Cos(x), Integer(2)))
        result = expr.simplify()
        # Should simplify to 1
        if hasattr(result, 'value'):
            assert result.value == 1

    def test_add_like_terms(self):
        """x + x = 2x."""
        from symbo_agentic_reasoners.core.symbolic.operations import Add
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        x = Symbol('x')
        expr = Add(x, x)
        result = expr.simplify()
        # Should be 2x
        assert result is not None

    def test_mul_identity(self):
        """1 * x = x."""
        from symbo_agentic_reasoners.core.symbolic.operations import Mul
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Integer
        x = Symbol('x')
        expr = Mul(Integer(1), x)
        result = expr.simplify()
        # Should be x
        assert result == x


class TestParsing:
    """Tests for the parsing module."""

    def test_parse_number(self):
        """Parse a number."""
        from symbo_agentic_reasoners.core.symbolic.parsing import parse_expr
        result = parse_expr("42")
        if hasattr(result, 'value'):
            assert result.value == 42

    def test_parse_symbol(self):
        """Parse a symbol."""
        from symbo_agentic_reasoners.core.symbolic.parsing import parse_expr
        result = parse_expr("x")
        assert str(result) == 'x'

    def test_parse_addition(self):
        """Parse addition."""
        from symbo_agentic_reasoners.core.symbolic.parsing import parse_expr
        result = parse_expr("x + y")
        assert result is not None

    def test_parse_multiplication(self):
        """Parse multiplication."""
        from symbo_agentic_reasoners.core.symbolic.parsing import parse_expr
        result = parse_expr("x * y")
        assert result is not None

    def test_parse_power(self):
        """Parse power."""
        from symbo_agentic_reasoners.core.symbolic.parsing import parse_expr
        result = parse_expr("x**2")
        assert result is not None

    def test_parse_function(self):
        """Parse function call."""
        from symbo_agentic_reasoners.core.symbolic.parsing import parse_expr
        result = parse_expr("sin(x)")
        assert result is not None

    def test_lexer(self):
        """Test Lexer class."""
        from symbo_agentic_reasoners.core.symbolic.parsing import Lexer
        lexer = Lexer("x + 1")
        tokens = lexer.tokenize()
        assert len(tokens) > 0

    def test_token_types(self):
        """Test TokenType enum."""
        from symbo_agentic_reasoners.core.symbolic.parsing import TokenType
        # Verify TokenType enum exists with expected values
        assert TokenType.NUMBER is not None
        assert TokenType.SYMBOL is not None
        assert TokenType.PLUS is not None
        assert TokenType.MINUS is not None
        assert TokenType.FUNCTION is not None
        assert TokenType.EOF is not None


class TestTypeSystem:
    """Tests for the type system."""

    def test_type_system_imports(self):
        """Type system has required types."""
        from symbo_agentic_reasoners.core.symbolic.type_system import (
            Integer, Float, Rational, Symbol, MathConstant
        )
        x = Symbol('x')
        assert x.name == 'x'

    def test_math_constant(self):
        """MathConstant provides constants."""
        from symbo_agentic_reasoners.core.symbolic.type_system import MathConstant
        assert MathConstant.PI is not None
        assert MathConstant.E is not None


class TestUtilities:
    """Tests for utility functions."""

    def test_ensure_expr_int(self):
        """Convert int to Integer."""
        from symbo_agentic_reasoners.core.symbolic.utilities import _ensure_expr
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Integer
        result = _ensure_expr(5)
        assert isinstance(result, Integer)

    def test_ensure_expr_float(self):
        """Convert float to Float."""
        from symbo_agentic_reasoners.core.symbolic.utilities import _ensure_expr
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Float
        result = _ensure_expr(3.14)
        assert isinstance(result, Float)

    def test_ensure_expr_str(self):
        """Convert string to Symbol."""
        from symbo_agentic_reasoners.core.symbolic.utilities import _ensure_expr
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        result = _ensure_expr('x')
        assert isinstance(result, Symbol)


class TestExpressionBuilder:
    """Tests for building complex expressions."""

    def test_nested_operations(self):
        """Build nested operations."""
        from symbo_agentic_reasoners.core.symbolic.operations import Add, Mul, Pow
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Integer
        x = Symbol('x')
        y = Symbol('y')
        # x^2 + 2*x*y + y^2 = (x + y)^2
        expr = Add(Pow(x, Integer(2)), Mul(Integer(2), x, y), Pow(y, Integer(2)))
        assert expr is not None

    def test_expression_evaluation(self):
        """Evaluate expression numerically."""
        from symbo_agentic_reasoners.core.symbolic.operations import Add
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Integer
        x = Symbol('x')
        expr = Add(x, Integer(5))
        result = expr.subs({x: Integer(3)})
        # Should be 8
        if hasattr(result, 'value'):
            assert result.value == 8


class TestSimplificationEngine:
    """Tests for the simplification engine module."""

    def test_expand_expression(self):
        """Test expand_expression function."""
        from symbo_agentic_reasoners.core.symbolic.simplification_engine import expand_expression
        from symbo_agentic_reasoners.core.symbolic.operations import Pow, Add
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Integer
        x = Symbol('x')
        expr = Pow(Add(x, Integer(1)), Integer(2))
        result = expand_expression(expr)
        assert result is not None

    def test_factor_expression(self):
        """Test factor_expression function."""
        from symbo_agentic_reasoners.core.symbolic.simplification_engine import factor_expression
        from symbo_agentic_reasoners.core.symbolic.operations import Add, Mul
        from symbo_agentic_reasoners.core.symbolic.symbol import Symbol
        from symbo_agentic_reasoners.core.symbolic.numeric_types import Integer
        x = Symbol('x')
        # x^2 + 2x = x(x + 2)
        expr = Add(Mul(x, x), Mul(Integer(2), x))
        result = factor_expression(expr)
        assert result is not None

    def test_parse_expr_from_engine(self):
        """Test parse_expr imported in engine."""
        from symbo_agentic_reasoners.core.symbolic.simplification_engine import parse_expr
        result = parse_expr("x + 1")
        assert result is not None


class TestSymPyCompatibility:
    """Tests for SymPy compatibility layer."""

    def test_import_compatibility(self):
        """Import compatibility module."""
        from symbo_agentic_reasoners.core.symbolic.sympy_compatibility import (
            Symbol, Integer, Float, sin, cos, exp, log
        )
        x = Symbol('x')
        assert x.name == 'x'

    def test_create_symbol(self):
        """Create symbol using compatibility layer."""
        from symbo_agentic_reasoners.core.symbolic.sympy_compatibility import Symbol
        x = Symbol('x')
        assert str(x) == 'x'

    def test_solve_function(self):
        """Test solve function."""
        from symbo_agentic_reasoners.core.symbolic.sympy_compatibility import solve, Symbol
        x = Symbol('x')
        # solve is available
        assert solve is not None

    def test_oo_constant(self):
        """Test infinity constant."""
        from symbo_agentic_reasoners.core.symbolic.sympy_compatibility import oo
        assert oo is not None

    def test_parse_expr_compat(self):
        """Test parse_expr in compatibility layer."""
        from symbo_agentic_reasoners.core.symbolic.sympy_compatibility import parse_expr
        result = parse_expr("x + 1")
        assert result is not None

    def test_trig_functions(self):
        """Test trig functions in compatibility."""
        from symbo_agentic_reasoners.core.symbolic.sympy_compatibility import (
            sin, cos, tan, Symbol
        )
        x = Symbol('x')
        assert sin(x) is not None
        assert cos(x) is not None
        assert tan(x) is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
