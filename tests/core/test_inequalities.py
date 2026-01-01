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
Test Suite for Inequalities Core Module
========================================

Tests classical inequalities implementations:
- Cauchy-Schwarz inequality
- Hölder inequality
- Jensen inequality
- Chebyshev inequality
- Rearrangement inequality

NO SYMPY - Pure native testing.
"""

import pytest
import numpy as np
from symbo_agentic_reasoners.core.inequalities import (
    cauchy_schwarz_discrete, cauchy_schwarz_integral,
    holder_inequality, jensen_discrete, is_convex_function,
    chebyshev_probability, chebyshev_sum,
    rearrangement_inequality, verify_inequality
)


class TestCauchySchwarzDiscrete:
    """Test Cauchy-Schwarz inequality (discrete form)."""

    def test_basic_vectors(self):
        """Test CS on simple vectors."""
        result = cauchy_schwarz_discrete([1, 2, 3], [4, 5, 6])
        assert result['inequality_holds']
        assert result['left_side'] <= result['right_side']

    def test_orthogonal_vectors(self):
        """Test CS on orthogonal vectors."""
        result = cauchy_schwarz_discrete([1, 0], [0, 1])
        assert result['inequality_holds']
        assert abs(result['left_side']) < 1e-10  # Dot product is zero
        assert result['equality_holds']  # 0² = 0

    def test_proportional_vectors_equality(self):
        """Test equality case: a = λb."""
        result = cauchy_schwarz_discrete([1, 2, 3], [2, 4, 6])  # b = 2a
        assert result['inequality_holds']
        assert result['equality_holds']
        assert result['proportionality_constant'] is not None
        assert abs(result['proportionality_constant'] - 0.5) < 1e-6  # a = 0.5*b

    def test_zero_vector(self):
        """Test with zero vector."""
        result = cauchy_schwarz_discrete([0, 0, 0], [1, 2, 3])
        assert result['inequality_holds']
        assert result['equality_holds']  # 0 = 0
        assert result['left_side'] == 0
        assert result['right_side'] == 0

    def test_high_dimensional(self):
        """TOUGH EDGE CASE: 1000-dimensional random vectors."""
        np.random.seed(42)
        a = np.random.randn(1000)
        b = np.random.randn(1000)
        result = cauchy_schwarz_discrete(a, b)
        assert result['inequality_holds']
        assert 0 <= result['ratio'] <= 1.0 + 1e-6

    def test_near_equality(self):
        """TOUGH EDGE CASE: Nearly proportional vectors (floating-point precision)."""
        a = np.array([1.0, 2.0, 3.0])
        b = a * 1.0000000001  # Nearly proportional
        result = cauchy_schwarz_discrete(a, b)
        assert result['inequality_holds']
        # Should detect near-proportionality
        assert result['ratio'] > 0.99999

    def test_mismatched_lengths_error(self):
        """Test error on mismatched vector lengths."""
        with pytest.raises(ValueError, match="same length"):
            cauchy_schwarz_discrete([1, 2], [1, 2, 3])

    def test_empty_vector_error(self):
        """Test error on empty vectors."""
        with pytest.raises(ValueError, match="cannot be empty"):
            cauchy_schwarz_discrete([], [])


class TestHolderInequality:
    """Test Hölder inequality."""

    def test_p_equals_2_reduces_to_cauchy_schwarz(self):
        """Test p=2 case (should match Cauchy-Schwarz)."""
        a, b = [1, 2, 3], [4, 5, 6]
        result_holder = holder_inequality(a, b, p=2.0)
        result_cs = cauchy_schwarz_discrete(a, b)

        assert result_holder['inequality_holds']
        # ||a||_2 * ||b||_2 should equal √(∑a²) * √(∑b²)
        assert abs(result_holder['right_side'] - np.sqrt(result_cs['right_side'])) < 1e-6

    def test_conjugate_exponent_computation(self):
        """Test q = p/(p-1) computation."""
        result = holder_inequality([1, 2, 3], [1, 1, 1], p=3.0)
        assert abs(result['q'] - 1.5) < 1e-10  # q = 3/2

    def test_p_near_1_edge_case(self):
        """TOUGH EDGE CASE: p very close to 1 (numerical stability)."""
        result = holder_inequality([1, 2, 3], [4, 5, 6], p=1.01)
        assert result['inequality_holds']
        assert result['q'] > 100  # q → ∞ as p → 1

    def test_large_p_edge_case(self):
        """TOUGH EDGE CASE: Large p approaching infinity."""
        result = holder_inequality([1, 2, 3], [4, 5, 6], p=100.0)
        assert result['inequality_holds']
        # ||a||_100 ≈ max|aᵢ| = 3
        assert abs(result['norm_a_p'] - 3.0) < 0.1

    def test_p_less_than_1_error(self):
        """Test error when p ≤ 1."""
        with pytest.raises(ValueError, match="p must be > 1"):
            holder_inequality([1, 2], [3, 4], p=0.5)


class TestJensenInequality:
    """Test Jensen inequality."""

    def test_convex_quadratic(self):
        """Test Jensen on convex function f(x)=x²."""
        result = jensen_discrete([1, 2, 3], [0.5, 0.3, 0.2], lambda x: x**2)
        assert result['inequality_holds']
        # f(weighted_avg) ≤ weighted_avg(f)
        assert result['left_side'] <= result['right_side'] + 1e-10

    def test_linear_function_equality(self):
        """Test equality for linear function."""
        result = jensen_discrete([1, 2, 3], [0.2, 0.3, 0.5], lambda x: 2*x + 3)
        assert result['inequality_holds']
        assert result['equality_holds']  # Equality for linear functions

    def test_concave_function(self):
        """Test concave inequality: f(∑λx) ≥ ∑λf(x)."""
        result = jensen_discrete([1, 2, 3], [1/3, 1/3, 1/3], lambda x: -x**2, convex=False)
        assert result['inequality_holds']

    def test_weights_not_summing_to_one_error(self):
        """Test error when weights don't sum to 1."""
        with pytest.raises(ValueError, match="sum to 1"):
            jensen_discrete([1, 2], [0.3, 0.5], lambda x: x)

    def test_negative_weights_error(self):
        """Test error on negative weights."""
        with pytest.raises(ValueError, match="non-negative"):
            jensen_discrete([1, 2], [-0.5, 1.5], lambda x: x)


class TestChebyshevInequality:
    """Test Chebyshev inequality."""

    def test_probability_bound(self):
        """Test P(|X-μ| ≥ kσ) ≤ 1/k²."""
        np.random.seed(42)
        data = np.random.normal(0, 1, 10000)  # Mean=0, Std=1
        result = chebyshev_probability(data, k=2.0)

        assert result['inequality_holds']
        assert result['bound'] == 0.25  # 1/2² = 0.25
        assert result['actual_proportion'] <= 0.25
        # For normal distribution, actual should be ~0.05 (much better than Chebyshev bound)

    def test_zero_variance_edge_case(self):
        """TOUGH EDGE CASE: Zero variance (all values equal)."""
        data = [5.0] * 100  # Constant values
        result = chebyshev_probability(data, k=1.0)
        assert result['inequality_holds']
        assert result['std'] == 0.0
        assert result['actual_proportion'] == 0.0  # No values beyond mean

    def test_sum_inequality_same_direction(self):
        """Test sum inequality for increasing sequences."""
        result = chebyshev_sum([1, 2, 3, 4], [1, 2, 3, 4])
        assert result['inequality_holds']
        assert result['same_direction']
        # (∑a)(∑b) ≤ n·∑(ab): 10*10 = 100 ≤ 4*30 = 120

    def test_sum_inequality_opposite_direction(self):
        """Test sum inequality for opposite monotone sequences."""
        result = chebyshev_sum([1, 2, 3], [3, 2, 1])  # Increasing vs decreasing
        assert result['inequality_holds']
        assert not result['same_direction']


class TestRearrangementInequality:
    """Test rearrangement inequality."""

    def test_sorted_same_direction_maximum(self):
        """Test that same-direction sorting gives maximum."""
        result = rearrangement_inequality([3, 1, 2], [6, 4, 5])
        assert result['inequality_holds']
        assert result['max_sum'] >= result['original_sum']
        assert result['min_sum'] <= result['original_sum']

    def test_already_optimal(self):
        """Test when input is already optimally sorted."""
        result = rearrangement_inequality([1, 2, 3], [1, 2, 3])
        assert result['at_maximum']
        assert result['max_sum'] == result['original_sum']

    def test_worst_case_ordering(self):
        """Test worst-case (opposite direction) ordering."""
        result = rearrangement_inequality([1, 2, 3], [3, 2, 1])
        assert result['at_minimum']
        assert result['min_sum'] == result['original_sum']

    def test_large_sequences(self):
        """TOUGH EDGE CASE: 1000-element random sequences."""
        np.random.seed(42)
        a = np.random.randn(1000)
        b = np.random.randn(1000)
        result = rearrangement_inequality(a, b)
        assert result['inequality_holds']
        assert result['min_sum'] <= result['original_sum'] <= result['max_sum']


class TestUtilities:
    """Test utility functions."""

    def test_is_convex_function_convex_case(self):
        """Test convexity detection for f(x)=x²."""
        assert is_convex_function(lambda x: x**2, (-10, 10))

    def test_is_convex_function_concave_case(self):
        """Test that concave functions are detected as non-convex."""
        assert not is_convex_function(lambda x: -x**2, (-10, 10))

    def test_is_convex_function_linear(self):
        """Test linear function (both convex and concave)."""
        assert is_convex_function(lambda x: 2*x + 3, (-10, 10))

    def test_verify_inequality_unified_interface(self):
        """Test unified verify_inequality interface."""
        result = verify_inequality('cauchy_schwarz', a=[1, 2, 3], b=[4, 5, 6])
        assert result['inequality_holds']

        result = verify_inequality('holder', a=[1, 2], b=[3, 4], p=2.0)
        assert result['inequality_holds']
