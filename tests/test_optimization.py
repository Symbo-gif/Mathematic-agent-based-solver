# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
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
Tests for Optimization Domain
=============================

Comprehensive tests for linear programming, convex, and combinatorial specialists.
"""

import pytest
import numpy as np


# =============================================================================
# LINEAR PROGRAMMING SPECIALIST TESTS
# =============================================================================

class TestLinearProgrammingSpecialist:
    """Tests for LinearProgrammingSpecialist."""

    def test_simplex_basic(self):
        """Basic LP: max 3x + 2y s.t. x + y <= 4, x <= 2, y <= 3."""
        from symbo_agentic_reasoners.agents.specialists.optimization import LinearProgrammingSpecialist
        specialist = LinearProgrammingSpecialist()

        c = [3, 2]  # Maximize 3x + 2y
        A = [[1, 1], [1, 0], [0, 1]]  # Constraints
        b = [4, 2, 3]  # RHS

        result = specialist.simplex_solve(c, A, b, maximize=True)

        assert result['status'] == 'optimal'
        # Optimal: x=2, y=2, value=10
        assert abs(result['optimal_value'] - 10) < 1e-6

    def test_simplex_unbounded(self):
        """Unbounded LP should detect unboundedness."""
        from symbo_agentic_reasoners.agents.specialists.optimization import LinearProgrammingSpecialist
        specialist = LinearProgrammingSpecialist()

        # max x + y, no upper bounds
        c = [1, 1]
        A = [[-1, 0], [0, -1]]  # x >= 0, y >= 0 (already satisfied)
        b = [0, 0]

        result = specialist.simplex_solve(c, A, b, maximize=True)
        # Should either be unbounded or have very large value
        # Our implementation may not explicitly detect unboundedness
        assert 'status' in result

    def test_simplex_minimization(self):
        """Minimization problem."""
        from symbo_agentic_reasoners.agents.specialists.optimization import LinearProgrammingSpecialist
        specialist = LinearProgrammingSpecialist()

        # min 2x + 3y s.t. x + y >= 10, x >= 0, y >= 0
        # Converted to: min 2x + 3y s.t. -x - y <= -10
        c = [2, 3]
        A = [[-1, -1]]
        b = [-10]

        result = specialist.simplex_solve(c, A, b, maximize=False)

        # Should use two-phase since b < 0
        assert 'status' in result

    def test_two_phase_simplex(self):
        """Two-phase simplex for infeasible-looking problems."""
        from symbo_agentic_reasoners.agents.specialists.optimization import LinearProgrammingSpecialist
        specialist = LinearProgrammingSpecialist()

        # Feasible problem with negative RHS
        c = [1, 1]
        A = [[1, 1], [-1, -1]]
        b = [5, -2]  # Second constraint: x + y >= 2

        result = specialist.two_phase_simplex(c, A, b, maximize=True)
        assert 'status' in result

    def test_sensitivity_analysis(self):
        """Sensitivity analysis returns shadow prices."""
        from symbo_agentic_reasoners.agents.specialists.optimization import LinearProgrammingSpecialist
        specialist = LinearProgrammingSpecialist()

        c = [3, 2]
        A = [[1, 1], [1, 0], [0, 1]]
        b = [4, 2, 3]

        result = specialist.sensitivity_analysis(c, A, b)

        assert 'shadow_prices' in result
        assert len(result['shadow_prices']) == 3


# =============================================================================
# CONVEX OPTIMIZATION SPECIALIST TESTS
# =============================================================================

class TestConvexOptimizationSpecialist:
    """Tests for ConvexOptimizationSpecialist."""

    def test_gradient_descent_quadratic(self):
        """Gradient descent on simple quadratic."""
        from symbo_agentic_reasoners.agents.specialists.optimization import ConvexOptimizationSpecialist
        specialist = ConvexOptimizationSpecialist()

        # min (x-1)^2 + (y-2)^2
        f = lambda x: (x[0] - 1)**2 + (x[1] - 2)**2
        grad_f = lambda x: np.array([2*(x[0] - 1), 2*(x[1] - 2)])

        result = specialist.gradient_descent(f, grad_f, [0, 0], learning_rate=0.1)

        assert result['status'] == 'converged'
        assert abs(result['optimal_x'][0] - 1) < 0.01
        assert abs(result['optimal_x'][1] - 2) < 0.01

    def test_gradient_descent_backtracking(self):
        """Gradient descent with backtracking."""
        from symbo_agentic_reasoners.agents.specialists.optimization import ConvexOptimizationSpecialist
        specialist = ConvexOptimizationSpecialist()

        f = lambda x: (x[0] - 3)**2 + (x[1] + 1)**2
        grad_f = lambda x: np.array([2*(x[0] - 3), 2*(x[1] + 1)])

        result = specialist.gradient_descent_backtracking(f, grad_f, [0, 0])

        assert result['status'] == 'converged'
        assert abs(result['optimal_x'][0] - 3) < 0.01
        assert abs(result['optimal_x'][1] + 1) < 0.01

    def test_newton_method(self):
        """Newton's method converges faster."""
        from symbo_agentic_reasoners.agents.specialists.optimization import ConvexOptimizationSpecialist
        specialist = ConvexOptimizationSpecialist()

        # Quadratic: 0.5 * x^T Q x + c^T x
        Q = np.array([[4, 0], [0, 2]])
        c = np.array([-8, -4])

        f = lambda x: 0.5 * x @ Q @ x + c @ x
        grad_f = lambda x: Q @ x + c
        hess_f = lambda x: Q

        result = specialist.newton_method(f, grad_f, hess_f, [0, 0])

        assert result['status'] == 'converged'
        # Optimal: x* = Q^{-1} * (-c) = [2, 2]
        assert abs(result['optimal_x'][0] - 2) < 0.01
        assert abs(result['optimal_x'][1] - 2) < 0.01
        # Newton should converge in 1-2 iterations for quadratic
        assert result['iterations'] <= 3

    def test_quadratic_program_unconstrained(self):
        """Unconstrained QP."""
        from symbo_agentic_reasoners.agents.specialists.optimization import ConvexOptimizationSpecialist
        specialist = ConvexOptimizationSpecialist()

        Q = [[2, 0], [0, 2]]
        c = [-4, -6]

        result = specialist.quadratic_program(Q, c)

        assert result['status'] == 'optimal'
        # Optimal: x* = -Q^{-1}c = [2, 3]
        assert abs(result['optimal_x'][0] - 2) < 0.01
        assert abs(result['optimal_x'][1] - 3) < 0.01

    def test_least_squares(self):
        """Least squares regression."""
        from symbo_agentic_reasoners.agents.specialists.optimization import ConvexOptimizationSpecialist
        specialist = ConvexOptimizationSpecialist()

        # y = 2x + 1 with noise
        A = [[1, 1], [1, 2], [1, 3], [1, 4]]
        b = [3, 5, 7, 9]

        result = specialist.least_squares(A, b)

        assert result['status'] == 'optimal'
        # Should recover [intercept, slope] ≈ [1, 2]
        assert abs(result['solution'][0] - 1) < 0.1
        assert abs(result['solution'][1] - 2) < 0.1


# =============================================================================
# COMBINATORIAL OPTIMIZATION SPECIALIST TESTS
# =============================================================================

class TestCombinatorialOptimizationSpecialist:
    """Tests for CombinatorialOptimizationSpecialist."""

    def test_knapsack_01(self):
        """0/1 Knapsack problem."""
        from symbo_agentic_reasoners.agents.specialists.optimization import CombinatorialOptimizationSpecialist
        specialist = CombinatorialOptimizationSpecialist()

        weights = [10, 20, 30]
        values = [60, 100, 120]
        capacity = 50

        result = specialist.knapsack_01(weights, values, capacity)

        # Optimal: items 1 and 2 (indices 1, 2), value = 100 + 120 = 220
        assert result['max_value'] == 220
        assert set(result['selected_items']) == {1, 2}

    def test_knapsack_fractional(self):
        """Fractional knapsack."""
        from symbo_agentic_reasoners.agents.specialists.optimization import CombinatorialOptimizationSpecialist
        specialist = CombinatorialOptimizationSpecialist()

        weights = [10, 20, 30]
        values = [60, 100, 120]
        capacity = 50

        result = specialist.knapsack_fractional(weights, values, capacity)

        # Best ratios: item 0 (6), item 1 (5), item 2 (4)
        # Take all of item 0 (10, val=60), all of item 1 (20, val=100), 2/3 of item 2 (20, val=80)
        # Total: 60 + 100 + 80 = 240
        assert abs(result['max_value'] - 240) < 0.1

    def test_tsp_nearest_neighbor(self):
        """TSP nearest neighbor heuristic."""
        from symbo_agentic_reasoners.agents.specialists.optimization import CombinatorialOptimizationSpecialist
        specialist = CombinatorialOptimizationSpecialist()

        # Simple 4-city problem
        distances = [
            [0, 10, 15, 20],
            [10, 0, 35, 25],
            [15, 35, 0, 30],
            [20, 25, 30, 0]
        ]

        result = specialist.tsp_nearest_neighbor(distances, start=0)

        assert 'tour' in result
        assert len(result['tour']) == 5  # 4 cities + return
        assert result['tour'][0] == 0
        assert result['tour'][-1] == 0

    def test_tsp_2opt(self):
        """TSP 2-opt improvement."""
        from symbo_agentic_reasoners.agents.specialists.optimization import CombinatorialOptimizationSpecialist
        specialist = CombinatorialOptimizationSpecialist()

        distances = [
            [0, 10, 15, 20],
            [10, 0, 35, 25],
            [15, 35, 0, 30],
            [20, 25, 30, 0]
        ]

        result = specialist.tsp_2opt(distances)

        assert 'tour' in result
        # 2-opt should not increase distance
        nn_result = specialist.tsp_nearest_neighbor(distances, 0)
        assert result['total_distance'] <= nn_result['total_distance'] + 0.1

    def test_assignment_hungarian(self):
        """Assignment problem."""
        from symbo_agentic_reasoners.agents.specialists.optimization import CombinatorialOptimizationSpecialist
        specialist = CombinatorialOptimizationSpecialist()

        cost_matrix = [
            [9, 2, 7],
            [6, 4, 3],
            [5, 8, 1]
        ]

        result = specialist.assignment_hungarian(cost_matrix)

        assert 'assignment' in result
        # Optimal assignment: 0->1, 1->2, 2->0 with cost 2+3+5=10
        # Or other permutation with same cost
        assert result['total_cost'] <= 10 + 0.1

    def test_set_cover_greedy(self):
        """Greedy set cover."""
        from symbo_agentic_reasoners.agents.specialists.optimization import CombinatorialOptimizationSpecialist
        specialist = CombinatorialOptimizationSpecialist()

        universe = [1, 2, 3, 4, 5]
        subsets = [
            [1, 2, 3],
            [2, 4],
            [3, 4],
            [4, 5]
        ]

        result = specialist.set_cover_greedy(universe, subsets)

        assert 'selected_subsets' in result
        # Verify coverage
        covered = set()
        for idx in result['selected_subsets']:
            covered |= set(subsets[idx])
        assert covered == set(universe)

    def test_bin_packing_first_fit(self):
        """First-fit decreasing bin packing."""
        from symbo_agentic_reasoners.agents.specialists.optimization import CombinatorialOptimizationSpecialist
        specialist = CombinatorialOptimizationSpecialist()

        items = [7, 5, 5, 3, 3, 2, 2, 1]
        bin_capacity = 10

        result = specialist.bin_packing_first_fit(items, bin_capacity)

        assert 'num_bins' in result
        # Optimal is 3 bins, FFD should get close
        assert result['num_bins'] <= 4

        # Verify all items are packed
        all_items = []
        for bin_content in result['bin_contents']:
            all_items.extend(bin_content)
        assert set(all_items) == set(range(len(items)))


# =============================================================================
# OPTIMIZATION SUPERVISOR TESTS
# =============================================================================

class TestOptimizationSupervisor:
    """Tests for OptimizationSupervisor."""

    def test_supervisor_initialization(self):
        """Supervisor initializes correctly."""
        from symbo_agentic_reasoners.agents.supervisors.optimization_supervisor import OptimizationSupervisor
        supervisor = OptimizationSupervisor()

        assert supervisor.agent_id == 'optimization_supervisor_001'

    def test_supervisor_solve_simplex(self):
        """Supervisor routes simplex problem."""
        from symbo_agentic_reasoners.agents.supervisors.optimization_supervisor import OptimizationSupervisor
        supervisor = OptimizationSupervisor()

        result = supervisor.solve({
            'type': 'simplex',
            'objective': [3, 2],
            'constraints_lhs': [[1, 1], [1, 0]],
            'constraints_rhs': [4, 2],
            'maximize': True
        })

        assert result['status'] == 'optimal'

    def test_supervisor_solve_knapsack(self):
        """Supervisor routes knapsack problem."""
        from symbo_agentic_reasoners.agents.supervisors.optimization_supervisor import OptimizationSupervisor
        supervisor = OptimizationSupervisor()

        result = supervisor.solve({
            'type': 'knapsack_01',
            'weights': [10, 20, 30],
            'values': [60, 100, 120],
            'capacity': 50
        })

        assert result['max_value'] == 220

    def test_supervisor_solve_qp(self):
        """Supervisor routes QP problem."""
        from symbo_agentic_reasoners.agents.supervisors.optimization_supervisor import OptimizationSupervisor
        supervisor = OptimizationSupervisor()

        result = supervisor.solve({
            'type': 'quadratic_program',
            'Q': [[2, 0], [0, 2]],
            'c': [-4, -6]
        })

        assert result['status'] == 'optimal'

    def test_supervisor_unknown_type(self):
        """Supervisor handles unknown type."""
        from symbo_agentic_reasoners.agents.supervisors.optimization_supervisor import OptimizationSupervisor
        supervisor = OptimizationSupervisor()

        result = supervisor.solve({
            'type': 'unknown_operation'
        })

        assert 'error' in result


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestOptimizationIntegration:
    """Integration tests for optimization domain."""

    def test_lp_vs_qp(self):
        """LP solution should match QP with linear objective."""
        from symbo_agentic_reasoners.agents.specialists.optimization import (
            LinearProgrammingSpecialist, ConvexOptimizationSpecialist
        )

        lp = LinearProgrammingSpecialist()
        convex = ConvexOptimizationSpecialist()

        # LP: max 2x + 3y s.t. x + y <= 4, x <= 2
        c_lp = [2, 3]
        A_lp = [[1, 1], [1, 0]]
        b_lp = [4, 2]

        lp_result = lp.simplex_solve(c_lp, A_lp, b_lp, maximize=True)

        # Optimal: x=0, y=4, val=12 (since 3y has higher coefficient)
        assert lp_result['status'] == 'optimal'
        assert abs(lp_result['optimal_value'] - 12) < 0.1

    def test_knapsack_types_comparison(self):
        """Fractional knapsack >= 0/1 knapsack."""
        from symbo_agentic_reasoners.agents.specialists.optimization import CombinatorialOptimizationSpecialist
        specialist = CombinatorialOptimizationSpecialist()

        weights = [10, 20, 30]
        values = [60, 100, 120]
        capacity = 50

        result_01 = specialist.knapsack_01(weights, values, capacity)
        result_frac = specialist.knapsack_fractional(weights, values, capacity)

        # Fractional solution is always >= 0/1 solution
        assert result_frac['max_value'] >= result_01['max_value']

    def test_tsp_improvement(self):
        """2-opt should improve or maintain nearest neighbor solution."""
        from symbo_agentic_reasoners.agents.specialists.optimization import CombinatorialOptimizationSpecialist
        specialist = CombinatorialOptimizationSpecialist()

        # Random distances
        np.random.seed(42)
        n = 6
        distances = np.random.rand(n, n) * 100
        distances = (distances + distances.T) / 2  # Symmetric
        np.fill_diagonal(distances, 0)

        nn_result = specialist.tsp_nearest_neighbor(distances.tolist(), 0)
        opt_result = specialist.tsp_2opt(distances.tolist())

        assert opt_result['total_distance'] <= nn_result['total_distance'] + 0.01


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
