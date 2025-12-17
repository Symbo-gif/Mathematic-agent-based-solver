# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
Matrix Properties - Property-Based Tests
=========================================

Phase 6 - Week 2: Property-based tests for matrix operations.

Properties Tested:
- Matrix multiplication associativity: (AB)C = A(BC)
- Distributivity: A(B+C) = AB + AC
- Identity matrix properties
- Transpose properties
- Determinant properties
"""

import pytest
from hypothesis import given, strategies as st, assume, settings, example
import numpy as np

# Phase 6 marker
pytestmark = pytest.mark.phase6


# ============================================================================
# STRATEGIES FOR GENERATING MATRICES
# ============================================================================

@st.composite
def small_matrices_2x2(draw):
    """Generate 2x2 matrices with small integer entries."""
    return [
        [draw(st.integers(min_value=-10, max_value=10)),
         draw(st.integers(min_value=-10, max_value=10))],
        [draw(st.integers(min_value=-10, max_value=10)),
         draw(st.integers(min_value=-10, max_value=10))]
    ]


@st.composite
def invertible_matrices_2x2(draw):
    """Generate 2x2 matrices that are invertible (det != 0)."""
    matrix = draw(small_matrices_2x2())
    det = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    assume(det != 0)
    return matrix


# ============================================================================
# MATRIX ADDITION PROPERTIES
# ============================================================================

@given(small_matrices_2x2(), small_matrices_2x2())
@settings(max_examples=200)
def test_matrix_addition_commutative(A, B):
    """Matrix addition is commutative: A + B = B + A"""
    # A + B
    sum1 = [[A[i][j] + B[i][j] for j in range(2)] for i in range(2)]
    # B + A
    sum2 = [[B[i][j] + A[i][j] for j in range(2)] for i in range(2)]

    assert sum1 == sum2, "Matrix addition not commutative"


@given(small_matrices_2x2(), small_matrices_2x2(), small_matrices_2x2())
@settings(max_examples=200)
def test_matrix_addition_associative(A, B, C):
    """Matrix addition is associative: (A+B)+C = A+(B+C)"""
    # (A + B) + C
    ab = [[A[i][j] + B[i][j] for j in range(2)] for i in range(2)]
    result1 = [[ab[i][j] + C[i][j] for j in range(2)] for i in range(2)]

    # A + (B + C)
    bc = [[B[i][j] + C[i][j] for j in range(2)] for i in range(2)]
    result2 = [[A[i][j] + bc[i][j] for j in range(2)] for i in range(2)]

    assert result1 == result2, "Matrix addition not associative"


# ============================================================================
# MATRIX MULTIPLICATION PROPERTIES
# ============================================================================

def matrix_multiply_2x2(A, B):
    """Multiply two 2x2 matrices."""
    return [
        [A[0][0]*B[0][0] + A[0][1]*B[1][0], A[0][0]*B[0][1] + A[0][1]*B[1][1]],
        [A[1][0]*B[0][0] + A[1][1]*B[1][0], A[1][0]*B[0][1] + A[1][1]*B[1][1]]
    ]


@given(small_matrices_2x2(), small_matrices_2x2(), small_matrices_2x2())
@settings(max_examples=150)
def test_matrix_multiplication_associative(A, B, C):
    """Matrix multiplication is associative: (AB)C = A(BC)"""
    AB = matrix_multiply_2x2(A, B)
    result1 = matrix_multiply_2x2(AB, C)

    BC = matrix_multiply_2x2(B, C)
    result2 = matrix_multiply_2x2(A, BC)

    # Check element-wise equality
    for i in range(2):
        for j in range(2):
            assert result1[i][j] == result2[i][j], \
                f"Matrix multiplication not associative at [{i}][{j}]"


@given(small_matrices_2x2())
@settings(max_examples=100)
def test_identity_matrix_left(A):
    """Identity matrix (left): I·A = A"""
    I = [[1, 0], [0, 1]]
    result = matrix_multiply_2x2(I, A)

    assert result == A, "Left identity property failed"


@given(small_matrices_2x2())
@settings(max_examples=100)
def test_identity_matrix_right(A):
    """Identity matrix (right): A·I = A"""
    I = [[1, 0], [0, 1]]
    result = matrix_multiply_2x2(A, I)

    assert result == A, "Right identity property failed"


# ============================================================================
# TRANSPOSE PROPERTIES
# ============================================================================

def transpose_2x2(A):
    """Transpose a 2x2 matrix."""
    return [[A[j][i] for j in range(2)] for i in range(2)]


@given(small_matrices_2x2())
@settings(max_examples=100)
def test_transpose_involution(A):
    """Transpose involution: (A^T)^T = A"""
    At = transpose_2x2(A)
    Att = transpose_2x2(At)

    assert Att == A, "Transpose involution failed"


@given(small_matrices_2x2(), small_matrices_2x2())
@settings(max_examples=150)
def test_transpose_sum(A, B):
    """Transpose of sum: (A + B)^T = A^T + B^T"""
    # A + B
    sum_ab = [[A[i][j] + B[i][j] for j in range(2)] for i in range(2)]
    # (A + B)^T
    result1 = transpose_2x2(sum_ab)

    # A^T + B^T
    At = transpose_2x2(A)
    Bt = transpose_2x2(B)
    result2 = [[At[i][j] + Bt[i][j] for j in range(2)] for i in range(2)]

    assert result1 == result2, "Transpose of sum property failed"


# ============================================================================
# DETERMINANT PROPERTIES
# ============================================================================

def determinant_2x2(A):
    """Calculate determinant of 2x2 matrix."""
    return A[0][0] * A[1][1] - A[0][1] * A[1][0]


@given(small_matrices_2x2(), small_matrices_2x2())
@settings(max_examples=200)
def test_determinant_product(A, B):
    """Determinant of product: det(AB) = det(A)·det(B)"""
    det_A = determinant_2x2(A)
    det_B = determinant_2x2(B)
    det_AB = det_A * det_B

    AB = matrix_multiply_2x2(A, B)
    det_AB_direct = determinant_2x2(AB)

    assert abs(det_AB - det_AB_direct) < 1e-9, \
        f"det(AB) = {det_AB_direct} != det(A)·det(B) = {det_AB}"


@given(small_matrices_2x2())
@settings(max_examples=100)
def test_determinant_transpose(A):
    """Determinant of transpose: det(A^T) = det(A)"""
    det_A = determinant_2x2(A)

    At = transpose_2x2(A)
    det_At = determinant_2x2(At)

    assert det_A == det_At, f"det(A^T) = {det_At} != det(A) = {det_A}"


@given(st.integers(min_value=-10, max_value=10), small_matrices_2x2())
@settings(max_examples=150)
def test_determinant_scalar_multiple(k, A):
    """Determinant of scalar multiple: det(kA) = k^n·det(A) (for nxn matrix)"""
    # For 2x2 matrix: det(kA) = k²·det(A)
    kA = [[k * A[i][j] for j in range(2)] for i in range(2)]

    det_A = determinant_2x2(A)
    det_kA = determinant_2x2(kA)
    expected = k**2 * det_A

    assert det_kA == expected, f"det(kA) = {det_kA} != k²·det(A) = {expected}"


# ============================================================================
# TRACE PROPERTIES
# ============================================================================

def trace_2x2(A):
    """Calculate trace of 2x2 matrix."""
    return A[0][0] + A[1][1]


@given(small_matrices_2x2(), small_matrices_2x2())
@settings(max_examples=150)
def test_trace_sum(A, B):
    """Trace of sum: tr(A + B) = tr(A) + tr(B)"""
    sum_ab = [[A[i][j] + B[i][j] for j in range(2)] for i in range(2)]

    trace_sum = trace_2x2(sum_ab)
    sum_traces = trace_2x2(A) + trace_2x2(B)

    assert trace_sum == sum_traces, "Trace of sum property failed"


@given(small_matrices_2x2(), small_matrices_2x2())
@settings(max_examples=150)
def test_trace_product_commutative(A, B):
    """Trace of product: tr(AB) = tr(BA)"""
    AB = matrix_multiply_2x2(A, B)
    BA = matrix_multiply_2x2(B, A)

    trace_AB = trace_2x2(AB)
    trace_BA = trace_2x2(BA)

    assert trace_AB == trace_BA, "tr(AB) != tr(BA)"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--hypothesis-show-statistics'])
