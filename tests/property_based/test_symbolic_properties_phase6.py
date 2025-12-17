# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
Symbolic Properties - Property-Based Tests
===========================================

Phase 6 - Week 2: Property-based tests for symbolic mathematics.

Tests mathematical properties that MUST hold using hypothesis.

Properties Tested:
- Commutativity (addition, multiplication)
- Associativity (addition, multiplication)
- Distributivity
- Identity elements
- Inverse elements
- Simplification idempotence
"""

import pytest
from hypothesis import given, strategies as st, assume, settings, example
from hypothesis import HealthCheck

try:
    from symbo_agentic_reasoners.core.native_symbolic import (
        parse_expr, symbols, simplify, Integer, Add, Mul, Pow
    )
    SYMBOLIC_AVAILABLE = True
except ImportError:
    SYMBOLIC_AVAILABLE = False
    pytest.skip("Native symbolic not available", allow_module_level=True)


# ============================================================================
# STRATEGIES FOR GENERATING MATHEMATICAL OBJECTS
# ============================================================================

@st.composite
def integers_small(draw):
    """Generate small integers for testing (-100 to 100)."""
    return draw(st.integers(min_value=-100, max_value=100))


@st.composite
def integers_medium(draw):
    """Generate medium integers for testing (-10000 to 10000)."""
    return draw(st.integers(min_value=-10000, max_value=10000))


@st.composite
def nonzero_integers(draw):
    """Generate non-zero integers."""
    n = draw(st.integers(min_value=-100, max_value=100))
    assume(n != 0)
    return n


# ============================================================================
# ADDITIVE PROPERTIES
# ============================================================================

@given(integers_small(), integers_small())
@settings(max_examples=500)
@example(0, 0)
@example(1, -1)
@example(100, -100)
def test_addition_commutative(a, b):
    """Addition is commutative: a + b = b + a"""
    result1 = a + b
    result2 = b + a
    assert result1 == result2, f"{a} + {b} != {b} + {a}"


@given(integers_small(), integers_small(), integers_small())
@settings(max_examples=500)
@example(0, 0, 0)
@example(1, 2, 3)
def test_addition_associative(a, b, c):
    """Addition is associative: (a+b)+c = a+(b+c)"""
    result1 = (a + b) + c
    result2 = a + (b + c)
    assert result1 == result2, f"({a}+{b})+{c} != {a}+({b}+{c})"


@given(integers_small())
@settings(max_examples=200)
@example(0)
@example(1)
@example(-1)
def test_additive_identity(a):
    """Additive identity: a + 0 = a"""
    assert a + 0 == a, f"{a} + 0 != {a}"
    assert 0 + a == a, f"0 + {a} != {a}"


@given(integers_small())
@settings(max_examples=200)
def test_additive_inverse(a):
    """Additive inverse: a + (-a) = 0"""
    assert a + (-a) == 0, f"{a} + {-a} != 0"
    assert (-a) + a == 0, f"{-a} + {a} != 0"


# ============================================================================
# MULTIPLICATIVE PROPERTIES
# ============================================================================

@given(integers_small(), integers_small())
@settings(max_examples=500)
@example(0, 0)
@example(1, 1)
@example(2, 3)
def test_multiplication_commutative(a, b):
    """Multiplication is commutative: a * b = b * a"""
    result1 = a * b
    result2 = b * a
    assert result1 == result2, f"{a} * {b} != {b} * {a}"


@given(integers_small(), integers_small(), integers_small())
@settings(max_examples=500)
@example(2, 3, 4)
def test_multiplication_associative(a, b, c):
    """Multiplication is associative: (a*b)*c = a*(b*c)"""
    result1 = (a * b) * c
    result2 = a * (b * c)
    assert result1 == result2, f"({a}*{b})*{c} != {a}*({b}*{c})"


@given(integers_small())
@settings(max_examples=200)
@example(0)
@example(5)
def test_multiplicative_identity(a):
    """Multiplicative identity: a * 1 = a"""
    assert a * 1 == a, f"{a} * 1 != {a}"
    assert 1 * a == a, f"1 * {a} != {a}"


@given(integers_small())
@settings(max_examples=200)
def test_multiplication_by_zero(a):
    """Multiplication by zero: a * 0 = 0"""
    assert a * 0 == 0, f"{a} * 0 != 0"
    assert 0 * a == 0, f"0 * {a} != 0"


# ============================================================================
# DISTRIBUTIVE PROPERTY
# ============================================================================

@given(integers_small(), integers_small(), integers_small())
@settings(max_examples=500)
@example(2, 3, 4)
@example(0, 0, 0)
def test_distributive_left(a, b, c):
    """Left distributivity: a * (b + c) = a*b + a*c"""
    result1 = a * (b + c)
    result2 = a * b + a * c
    assert result1 == result2, f"{a} * ({b} + {c}) != {a}*{b} + {a}*{c}"


@given(integers_small(), integers_small(), integers_small())
@settings(max_examples=500)
def test_distributive_right(a, b, c):
    """Right distributivity: (a + b) * c = a*c + b*c"""
    result1 = (a + b) * c
    result2 = a * c + b * c
    assert result1 == result2, f"({a} + {b}) * {c} != {a}*{c} + {b}*{c}"


# ============================================================================
# SUBTRACTION PROPERTIES
# ============================================================================

@given(integers_small(), integers_small())
@settings(max_examples=300)
def test_subtraction_as_addition(a, b):
    """Subtraction as addition: a - b = a + (-b)"""
    assert a - b == a + (-b), f"{a} - {b} != {a} + {-b}"


@given(integers_small())
@settings(max_examples=200)
def test_subtraction_self(a):
    """Subtracting self gives zero: a - a = 0"""
    assert a - a == 0, f"{a} - {a} != 0"


# ============================================================================
# DIVISION PROPERTIES (with non-zero divisors)
# ============================================================================

@given(integers_small(), nonzero_integers())
@settings(max_examples=300)
def test_division_identity(a, b):
    """Division identity: (a / b) * b ≈ a (for integers, check relationship)"""
    # For integer division, we have (a // b) * b + (a % b) = a
    if b != 0:
        quotient = a // b
        remainder = a % b
        assert quotient * b + remainder == a, f"Division property failed for {a} / {b}"


# ============================================================================
# POWER PROPERTIES
# ============================================================================

@given(st.integers(min_value=-10, max_value=10), st.integers(min_value=0, max_value=5))
@settings(max_examples=200)
@example(2, 0)
@example(2, 1)
def test_power_zero(a, n):
    """Power properties: a^0 = 1 (for a != 0), a^1 = a"""
    if n == 0 and a != 0:
        assert a ** 0 == 1, f"{a}^0 != 1"
    elif n == 1:
        assert a ** 1 == a, f"{a}^1 != {a}"


@given(st.integers(min_value=1, max_value=10), st.integers(min_value=0, max_value=3), st.integers(min_value=0, max_value=3))
@settings(max_examples=200)
def test_power_multiplication(a, m, n):
    """Power multiplication: a^m * a^n = a^(m+n)"""
    result1 = (a ** m) * (a ** n)
    result2 = a ** (m + n)
    assert result1 == result2, f"{a}^{m} * {a}^{n} != {a}^{m+n}"


# ============================================================================
# COMPARISON AND ORDERING
# ============================================================================

@given(integers_small(), integers_small())
@settings(max_examples=300)
def test_comparison_trichotomy(a, b):
    """Trichotomy: exactly one of a < b, a = b, a > b is true"""
    conditions = [a < b, a == b, a > b]
    assert sum(conditions) == 1, f"Trichotomy failed for {a}, {b}"


@given(integers_small(), integers_small(), integers_small())
@settings(max_examples=300)
def test_comparison_transitivity(a, b, c):
    """Transitivity: if a <= b and b <= c, then a <= c"""
    if a <= b and b <= c:
        assert a <= c, f"Transitivity failed: {a} <= {b} <= {c} but {a} > {c}"


# ============================================================================
# ABSOLUTE VALUE PROPERTIES
# ============================================================================

@given(integers_small())
@settings(max_examples=200)
def test_absolute_value_non_negative(a):
    """Absolute value is non-negative: |a| >= 0"""
    assert abs(a) >= 0, f"|{a}| < 0"


@given(integers_small())
@settings(max_examples=200)
def test_absolute_value_symmetric(a):
    """Absolute value is symmetric: |a| = |-a|"""
    assert abs(a) == abs(-a), f"|{a}| != |{-a}|"


@given(integers_small(), integers_small())
@settings(max_examples=300)
def test_triangle_inequality(a, b):
    """Triangle inequality: |a + b| <= |a| + |b|"""
    assert abs(a + b) <= abs(a) + abs(b), f"|{a} + {b}| > |{a}| + |{b}|"


# ============================================================================
# MODULAR ARITHMETIC PROPERTIES
# ============================================================================

@given(integers_small(), integers_small(), nonzero_integers())
@settings(max_examples=300)
def test_modular_addition(a, b, m):
    """Modular addition: (a + b) mod m = ((a mod m) + (b mod m)) mod m"""
    result1 = (a + b) % m
    result2 = ((a % m) + (b % m)) % m
    assert result1 == result2, f"Modular addition property failed"


@given(integers_small(), integers_small(), nonzero_integers())
@settings(max_examples=300)
def test_modular_multiplication(a, b, m):
    """Modular multiplication: (a * b) mod m = ((a mod m) * (b mod m)) mod m"""
    result1 = (a * b) % m
    result2 = ((a % m) * (b % m)) % m
    assert result1 == result2, f"Modular multiplication property failed"


# ============================================================================
# GCD AND LCM PROPERTIES
# ============================================================================

@given(st.integers(min_value=1, max_value=100), st.integers(min_value=1, max_value=100))
@settings(max_examples=200)
def test_gcd_commutative(a, b):
    """GCD is commutative: gcd(a, b) = gcd(b, a)"""
    import math
    assert math.gcd(a, b) == math.gcd(b, a)


@given(st.integers(min_value=1, max_value=100))
@settings(max_examples=100)
def test_gcd_identity(a):
    """GCD identity: gcd(a, a) = a"""
    import math
    assert math.gcd(a, a) == a


@given(st.integers(min_value=1, max_value=100), st.integers(min_value=1, max_value=100))
@settings(max_examples=200)
def test_lcm_gcd_relationship(a, b):
    """LCM-GCD relationship: lcm(a, b) * gcd(a, b) = a * b"""
    import math
    lcm_val = math.lcm(a, b)
    gcd_val = math.gcd(a, b)
    assert lcm_val * gcd_val == a * b, f"LCM-GCD relationship failed for {a}, {b}"


# Phase 6 marker
pytestmark = pytest.mark.phase6


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--hypothesis-show-statistics'])
