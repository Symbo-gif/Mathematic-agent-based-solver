# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""Test Suite for Convex Analysis Core Module"""

import pytest
import numpy as np
from symbo_agentic_reasoners.core.convex_analysis import (
    convex_hull_2d, extreme_points_2d, is_convex_set,
    verify_convexity_first_order, verify_convexity_second_order,
    numerical_hessian, is_positive_semidefinite,
    compute_subgradient, subdifferential_l1,
    separating_hyperplane, supporting_hyperplane, project_onto_convex_set,
    proximal_l1, proximal_l2, proximal_indicator, moreau_envelope
)


class TestConvexHull:
    """Test convex hull algorithms."""

    def test_convex_hull_square(self):
        """Test convex hull of square with interior point."""
        points = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0.5, 0.5]])
        hull = convex_hull_2d(points)
        assert len(hull) == 4  # Four corners

    def test_convex_hull_collinear(self):
        """Test convex hull of collinear points."""
        points = np.array([[0, 0], [1, 1], [2, 2], [3, 3]])
        hull = convex_hull_2d(points)
        assert len(hull) == 2  # Only endpoints

    def test_extreme_points_identification(self):
        """Test extreme point detection."""
        points = np.array([[0, 0], [0.5, 0.5], [1, 0], [1, 1], [0, 1]])
        extreme_indices = extreme_points_2d(points)
        assert 1 not in extreme_indices  # Interior point excluded
        assert len(extreme_indices) == 4  # Four corners

    def test_convex_hull_large_point_cloud(self):
        """TOUGH EDGE CASE: 1000 random 2D points."""
        np.random.seed(42)
        points = np.random.randn(1000, 2)
        hull = convex_hull_2d(points)
        assert len(hull) < 1000  # Hull is smaller than full set
        assert len(hull) >= 3  # At least a triangle


class TestConvexFunctions:
    """Test convexity verification."""

    def test_first_order_convex_quadratic(self):
        """Test first-order condition for f(x)=x²."""
        f = lambda x: np.sum(x**2)
        grad_f = lambda x: 2*x
        result = verify_convexity_first_order(f, grad_f, np.array([1.0]), np.array([2.0]))
        assert result['convex']

    def test_second_order_convex_quadratic(self):
        """Test second-order condition for f(x)=x² + y²."""
        hess_f = lambda x: np.diag([2.0, 2.0])  # Constant Hessian
        domain_points = np.array([[0, 0], [1, 1], [-1, 1], [0, 2]])
        result = verify_convexity_second_order(hess_f, domain_points)
        assert result['convex']
        assert result['min_eigenvalue'] == 2.0

    def test_second_order_non_convex(self):
        """Test detection of non-convex function."""
        hess_f = lambda x: np.array([[1, 0], [0, -1]])  # Saddle point
        result = verify_convexity_second_order(hess_f, np.array([[0, 0]]))
        assert not result['convex']
        assert result['min_eigenvalue'] < 0

    def test_numerical_hessian_quadratic(self):
        """Test numerical Hessian computation."""
        f = lambda x: x[0]**2 + 2*x[1]**2 + x[0]*x[1]
        hess = numerical_hessian(f, np.array([1.0, 1.0]))
        # Expected: [[2, 1], [1, 4]]
        assert abs(hess[0, 0] - 2.0) < 1e-3
        assert abs(hess[1, 1] - 4.0) < 1e-3
        assert abs(hess[0, 1] - 1.0) < 1e-3

    def test_is_positive_semidefinite(self):
        """Test PSD matrix detection."""
        assert is_positive_semidefinite(np.array([[2, 0], [0, 3]]))
        assert not is_positive_semidefinite(np.array([[1, 0], [0, -1]]))


class TestSubgradients:
    """Test subgradient computation."""

    def test_smooth_function_subgradient(self):
        """Test subgradient of smooth function equals gradient."""
        f = lambda x: np.sum(x**2)
        x = np.array([1.0, 2.0])
        subgrad = compute_subgradient(f, x)
        # Should be close to gradient [2, 4]
        assert abs(subgrad[0] - 2.0) < 0.01
        assert abs(subgrad[1] - 4.0) < 0.01

    def test_l1_subdifferential_at_zero(self):
        """Test subdifferential of |x| at x=0."""
        subgrads = subdifferential_l1(np.array([0.0]))
        assert len(subgrads) == 2  # [-1] and [1]

    def test_l1_subdifferential_nonzero(self):
        """Test subdifferential of ||x||₁ at nonzero point."""
        subgrads = subdifferential_l1(np.array([2.0, -3.0]))
        assert len(subgrads) == 1  # Unique: [1, -1]
        assert np.allclose(subgrads[0], [1, -1])

    def test_l1_subdifferential_mixed(self):
        """TOUGH EDGE CASE: Mixed zero/nonzero components."""
        subgrads = subdifferential_l1(np.array([1.0, 0.0, -2.0]))
        assert len(subgrads) == 2  # 2^1 = 2 (one zero component)


class TestSeparation:
    """Test separation theorems."""

    def test_separating_hyperplane_disjoint_sets(self):
        """Test separation of disjoint point sets."""
        A = np.array([[0, 0], [1, 0], [0, 1]])
        B = np.array([[3, 3], [4, 3], [3, 4]])
        result = separating_hyperplane(A, B)
        assert result is not None
        assert 'a' in result and 'b' in result

    def test_supporting_hyperplane(self):
        """Test supporting hyperplane in given direction."""
        points = np.array([[0, 0], [1, 0], [1, 1], [0, 1]])  # Unit square
        result = supporting_hyperplane(points, np.array([1, 0]))  # Right direction
        assert result['b'] == 1.0  # Rightmost edge at x=1

    def test_projection_onto_convex_set(self):
        """Test projection onto convex set."""
        convex_set = np.array([[0, 0], [1, 0], [1, 1], [0, 1]])
        x_outside = np.array([2.0, 2.0])
        projection = project_onto_convex_set(x_outside, convex_set)
        # Should project to nearest point (corner [1, 1])
        assert np.linalg.norm(projection - np.array([1, 1])) < 0.01


class TestProximalOperators:
    """Test proximal operators."""

    def test_proximal_l1_soft_threshold(self):
        """Test L1 proximal (soft thresholding)."""
        x = np.array([2.0, -1.0, 0.5, -0.3])
        result = proximal_l1(x, lambda_param=1.0)
        # Soft threshold: sign(x) * max(|x| - 1, 0)
        expected = np.array([1.0, 0.0, 0.0, 0.0])
        assert np.allclose(result, expected)

    def test_proximal_l2_shrinkage(self):
        """Test L2 proximal (shrinkage)."""
        x = np.array([3.0, 6.0, 9.0])
        result = proximal_l2(x, lambda_param=0.5)
        expected = x / 1.5  # x / (1 + λ)
        assert np.allclose(result, expected)

    def test_proximal_l1_lasso_application(self):
        """TOUGH EDGE CASE: LASSO-style sparse solution."""
        x = np.array([5.0, 0.1, -0.2, 3.0, 0.05])
        result = proximal_l1(x, lambda_param=0.5)
        # Should zero out small components
        assert abs(result[1]) < 1e-10
        assert abs(result[2]) < 1e-10
        assert abs(result[4]) < 1e-10
        # Large components should survive
        assert abs(result[0] - 4.5) < 1e-6
        assert abs(result[3] - 2.5) < 1e-6
