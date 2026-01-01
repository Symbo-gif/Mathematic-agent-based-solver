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
Numeric Properties - Property-Based Tests
==========================================

Phase 6: Numerical stability and convergence property tests.

Properties:
- Floating-point arithmetic properties
- Numerical stability
- Convergence guarantees
- Rounding behavior
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
import math

pytestmark = pytest.mark.phase6


@given(st.floats(min_value=-1e10, max_value=1e10, allow_nan=False, allow_infinity=False),
       st.floats(min_value=-1e10, max_value=1e10, allow_nan=False, allow_infinity=False))
@settings(max_examples=500)
def test_float_addition_commutative(a, b):
    """Floating-point addition is commutative within precision."""
    result1 = a + b
    result2 = b + a
    # Allow for floating-point precision
    assert abs(result1 - result2) < 1e-10 or (math.isnan(result1) and math.isnan(result2))


@given(st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False))
@settings(max_examples=300)
def test_square_root_inverse(a):
    """Square and square root are inverses for non-negative numbers."""
    assume(a >= 0)
    result = math.sqrt(a) ** 2
    assert abs(result - a) < 1e-9 or a < 1e-10


@given(st.floats(min_value=0.01, max_value=1000, allow_nan=False, allow_infinity=False))
@settings(max_examples=200)
def test_logarithm_monotonicity(x):
    """Logarithm is monotonically increasing."""
    assume(x > 0)
    if x < 1:
        assert math.log(x) < 0
    elif x > 1:
        assert math.log(x) > 0
    else:
        assert abs(math.log(x)) < 1e-10


@given(st.integers(min_value=1, max_value=20))
@settings(max_examples=100)
def test_factorial_growth(n):
    """Factorial grows rapidly: n! > 2^(n-1) for n >= 1."""
    factorial = math.factorial(n)
    bound = 2 ** (n - 1)
    assert factorial >= bound, f"{n}! < 2^{n-1}"


@given(st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False))
@settings(max_examples=200)
def test_exponential_positive(x):
    """Exponential is always positive: e^x > 0."""
    result = math.exp(x)
    assert result > 0, f"exp({x}) = {result} <= 0"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--hypothesis-show-statistics'])
