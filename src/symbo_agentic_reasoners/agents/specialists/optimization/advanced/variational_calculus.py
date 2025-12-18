# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
VARIATIONAL CALCULUS SPECIALIST (Tier 3)
=========================================

Native Python implementation for calculus of variations.
Solves problems in functional optimization using Euler-Lagrange equations,
isoperimetric constraints, and direct methods.

NO SYMPY - Pure NumPy/SciPy implementation.

CAPABILITIES:
-------------
- Euler-Lagrange equations for functional extrema
- Brachistochrone problem (cycloid solution)
- Isoperimetric problems (constrained functionals)
- First variation computation
- Legendre condition (second-order optimality)
- Geodesic problems via variational formulation
- Direct methods (Ritz, Galerkin)
- Noether's theorem (conservation laws from symmetries)

THEORY:
-------
Functional: J[y] = ∫ L(x, y, y') dx from x_a to x_b
Euler-Lagrange: d/dx(∂L/∂y') - ∂L/∂y = 0
Necessary condition for y to be an extremal (stationary point of J)

EXAMPLES:
---------
- Shortest path: L = √(1 + y'²) → straight line
- Brachistochrone: Minimize time under gravity → cycloid
- Minimal surface of revolution: L = 2πy√(1 + y'²) → catenoid
- Geodesics on surfaces: Minimize arc length with metric constraint
"""

import logging
import numpy as np
from typing import Dict, Any, List, Optional, Callable, Tuple
from scipy.integrate import solve_ivp, quad
from scipy.optimize import minimize, root

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration

logger = logging.getLogger('symbo_agentic_reasoners.specialists.variational_calculus')


class VariationalCalculusSpecialist(BDIAgent):
    """
    BDI Agent for calculus of variations.

    Solves functional optimization problems using Euler-Lagrange equations
    and related methods from the calculus of variations.

    DIRECTIVE:
    ----------
    Minimize or maximize functionals J[y] = ∫ L(x, y, y') dx
    subject to boundary conditions and constraints.

    OPERATIONS:
    -----------
    - solve_euler_lagrange: Solve Euler-Lagrange equation
    - solve_brachistochrone: Brachistochrone problem (fastest descent)
    - solve_isoperimetric_problem: Constrained functional optimization
    - compute_first_variation: First variation δJ[y](η)
    - apply_legendre_condition: Second-order optimality check
    - solve_geodesic_variational: Geodesics as variational problem
    - direct_method_minimization: Ritz/Galerkin direct methods
    - apply_noethers_theorem: Conservation laws from symmetries
    """

    def __init__(self, agent_id='variational_calculus_specialist_001', df=None, blackboard=None):
        """Initialize Variational Calculus Specialist."""
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.solution_cache = {}

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.optimization.advanced.variational_calculus',
                agent_id=self.agent_id,
                algorithm='variational_calculus',
                cost='medium',
                instance=self,
                type='specialist',
                tier='3',
                capabilities='euler_lagrange_brachistochrone_isoperimetric_noether'
            ))

        logger.info(f"[{self.agent_id}] Variational Calculus Specialist initialized")

    def process(self, task_entry):
        """Process variational calculus task."""
        self.tasks_executed += 1
        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            operation = metadata.get('operation', 'euler_lagrange')

            if operation == 'euler_lagrange':
                result = self.solve_euler_lagrange(
                    metadata.get('lagrangian'),
                    metadata.get('boundary_conditions', {})
                )
            elif operation == 'brachistochrone':
                result = self.solve_brachistochrone()
            elif operation == 'isoperimetric':
                result = self.solve_isoperimetric_problem(
                    metadata.get('functional'),
                    metadata.get('constraint')
                )
            elif operation == 'first_variation':
                result = self.compute_first_variation(
                    metadata.get('functional'),
                    metadata.get('direction')
                )
            elif operation == 'geodesic':
                result = self.solve_geodesic_variational(
                    metadata.get('metric'),
                    metadata.get('endpoints')
                )
            else:
                result = {'error': f'Unknown operation: {operation}'}

            if 'error' not in result:
                self.tasks_succeeded += 1
            else:
                self.tasks_failed += 1

            return result

        except Exception as e:
            self.tasks_failed += 1
            logger.error(f"[{self.agent_id}] Task failed: {e}")
            return {'error': str(e)}

    # ========== EULER-LAGRANGE EQUATIONS ==========

    def solve_euler_lagrange(
        self,
        lagrangian: Callable[[float, float, float], float],
        boundary_conditions: Dict[str, float],
        x_span: Tuple[float, float] = (0, 1),
        n_points: int = 100
    ) -> Dict[str, Any]:
        """
        Solve Euler-Lagrange equation for functional J[y] = ∫ L(x, y, y') dx.

        The Euler-Lagrange equation is:
        d/dx(∂L/∂y') - ∂L/∂y = 0

        Args:
            lagrangian: Function L(x, y, y_prime)
            boundary_conditions: {'y_a': y(x_a), 'y_b': y(x_b)}
            x_span: Domain [x_a, x_b]
            n_points: Discretization points for shooting

        Returns:
            Dictionary with solution curve and functional value
        """
        logger.info("Solving Euler-Lagrange equation")

        x_a, x_b = x_span
        y_a = boundary_conditions.get('y_a', 0.0)
        y_b = boundary_conditions.get('y_b', 0.0)

        # Numerical derivatives for Euler-Lagrange equation
        eps = 1e-6

        def partial_L_y(x, y, yp):
            """∂L/∂y via finite differences."""
            return (lagrangian(x, y + eps, yp) - lagrangian(x, y - eps, yp)) / (2 * eps)

        def partial_L_yp(x, y, yp):
            """∂L/∂y' via finite differences."""
            return (lagrangian(x, y, yp + eps) - lagrangian(x, y, yp - eps)) / (2 * eps)

        # Convert second-order ODE to first-order system
        # Let z = [y, y', p] where p = ∂L/∂y'
        # Then: dy/dx = y', dy'/dx = ∂L/∂y / (∂²L/∂y'²)

        def ode_system(x, z):
            """
            System for Euler-Lagrange equation.
            z = [y, y_prime]
            """
            y, yp = z

            # Compute second derivative via Euler-Lagrange
            # d/dx(∂L/∂y') = ∂L/∂y
            # ∂²L/∂y'² * y'' + ∂²L/∂y∂y' * y' = ∂L/∂y
            # y'' = (∂L/∂y - ∂²L/∂y∂y' * y') / (∂²L/∂y'²)

            dL_dy = partial_L_y(x, y, yp)

            # Second derivative of L with respect to y'
            d2L_dyp2 = (partial_L_yp(x, y, yp + eps) - partial_L_yp(x, y, yp - eps)) / (2 * eps)

            if abs(d2L_dyp2) < 1e-10:
                d2L_dyp2 = 1e-10  # Avoid division by zero

            ypp = dL_dy / d2L_dyp2

            return [yp, ypp]

        # Shooting method: find initial slope that satisfies y(x_b) = y_b
        def shooting_error(yp_initial):
            """Error in terminal condition."""
            try:
                sol = solve_ivp(
                    ode_system,
                    x_span,
                    [y_a, yp_initial],
                    dense_output=True,
                    max_step=(x_b - x_a) / 50
                )
                if sol.success:
                    y_final = sol.sol(x_b)[0]
                    return y_final - y_b
                else:
                    return 1e6
            except Exception:
                return 1e6

        # Find initial slope via root finding
        from scipy.optimize import brentq

        try:
            # Guess initial slope range
            yp_guess = (y_b - y_a) / (x_b - x_a)
            search_range = max(10 * abs(yp_guess), 10.0)

            yp_initial = brentq(
                shooting_error,
                yp_guess - search_range,
                yp_guess + search_range,
                xtol=1e-6
            )
        except ValueError:
            # Fallback to optimization
            result_opt = minimize(
                lambda yp: shooting_error(yp)**2,
                x0=[(y_b - y_a) / (x_b - x_a)],
                method='Nelder-Mead'
            )
            yp_initial = result_opt.x[0]

        # Solve with found initial slope
        sol = solve_ivp(
            ode_system,
            x_span,
            [y_a, yp_initial],
            dense_output=True,
            max_step=(x_b - x_a) / n_points
        )

        if not sol.success:
            return {'error': 'ODE solver failed', 'message': sol.message}

        # Evaluate on grid
        x_grid = np.linspace(x_a, x_b, n_points)
        y_solution = sol.sol(x_grid)

        # Compute functional value J[y]
        def integrand(x):
            """Evaluate Lagrangian L(x, y, y') at point x."""
            y, yp = sol.sol(x)
            return lagrangian(x, y, yp)

        J_value, _ = quad(integrand, x_a, x_b, limit=100)

        return {
            'success': True,
            'x_grid': x_grid.tolist(),
            'y_solution': y_solution[0].tolist(),
            'y_prime': y_solution[1].tolist(),
            'functional_value': float(J_value),
            'initial_slope': float(yp_initial),
            'method': 'euler_lagrange_shooting',
            'boundary_conditions': {'y_a': y_a, 'y_b': y_b}
        }

    # ========== BRACHISTOCHRONE PROBLEM ==========

    def solve_brachistochrone(
        self,
        x_a: float = 0.0,
        y_a: float = 0.0,
        x_b: float = 1.0,
        y_b: float = -1.0,
        n_points: int = 100
    ) -> Dict[str, Any]:
        """
        Solve the brachistochrone problem: find the curve of fastest descent
        under gravity between two points.

        The solution is a cycloid:
        x = a(θ - sin θ)
        y = -a(1 - cos θ)

        where a is determined by boundary conditions.

        Args:
            x_a, y_a: Initial point
            x_b, y_b: Final point (y_b < y_a for downward motion)
            n_points: Number of points in solution

        Returns:
            Dictionary with cycloid solution and descent time
        """
        logger.info(f"Solving brachistochrone from ({x_a}, {y_a}) to ({x_b}, {y_b})")

        # For simplicity, assume x_a = 0, y_a = 0
        # Then find parameter a such that cycloid passes through (x_b, y_b)

        # Parametric cycloid: x = a(θ - sin θ), y = -a(1 - cos θ)
        # Need to find a and θ_b such that:
        # x_b = a(θ_b - sin θ_b)
        # y_b = -a(1 - cos θ_b)

        def cycloid_error(params):
            """Error in terminal conditions."""
            a, theta_b = params
            x_calc = a * (theta_b - np.sin(theta_b))
            y_calc = -a * (1 - np.cos(theta_b))
            return [(x_calc - x_b)**2, (y_calc - y_b)**2]

        # Initial guess
        a_guess = np.sqrt(x_b**2 + y_b**2) / 2
        theta_guess = np.pi

        result_opt = minimize(
            lambda p: sum(cycloid_error(p)),
            x0=[a_guess, theta_guess],
            method='Nelder-Mead',
            options={'xatol': 1e-8}
        )

        a_opt, theta_b_opt = result_opt.x

        # Generate cycloid
        theta = np.linspace(0, theta_b_opt, n_points)
        x_cycloid = a_opt * (theta - np.sin(theta))
        y_cycloid = -a_opt * (1 - np.cos(theta))

        # Compute descent time: T = ∫ ds/v where v = √(2gy)
        # For cycloid: T = √(a/g) * θ_b
        g = 9.81  # Gravity
        descent_time = np.sqrt(a_opt / g) * theta_b_opt

        return {
            'success': True,
            'x_solution': (x_cycloid + x_a).tolist(),
            'y_solution': (y_cycloid + y_a).tolist(),
            'cycloid_parameter_a': float(a_opt),
            'theta_final': float(theta_b_opt),
            'descent_time': float(descent_time),
            'method': 'brachistochrone_cycloid',
            'note': 'Solution is a cycloid: x = a(θ - sin θ), y = -a(1 - cos θ)'
        }

    # ========== ISOPERIMETRIC PROBLEMS ==========

    def solve_isoperimetric_problem(
        self,
        functional: Callable[[float, float, float], float],
        constraint: Callable[[float, float, float], float],
        boundary_conditions: Dict[str, float] = None,
        constraint_value: float = 1.0,
        x_span: Tuple[float, float] = (0, 1),
        n_points: int = 100
    ) -> Dict[str, Any]:
        """
        Solve isoperimetric problem: minimize J[y] subject to K[y] = constant.

        J[y] = ∫ L(x, y, y') dx
        K[y] = ∫ G(x, y, y') dx = c (constraint)

        Method: Introduce Lagrange multiplier λ
        Solve Euler-Lagrange for L_aug = L + λ * G

        Args:
            functional: Lagrangian L(x, y, y')
            constraint: Constraint integrand G(x, y, y')
            boundary_conditions: Boundary values
            constraint_value: Required value of constraint integral
            x_span: Domain
            n_points: Discretization points

        Returns:
            Dictionary with solution and Lagrange multiplier
        """
        logger.info("Solving isoperimetric problem")

        boundary_conditions = boundary_conditions or {'y_a': 0.0, 'y_b': 0.0}
        x_a, x_b = x_span

        # Augmented Lagrangian: L_aug(x, y, y', λ) = L(x, y, y') + λ * G(x, y, y')
        def augmented_lagrangian(lam):
            """Augmented Lagrangian for given λ."""
            def L_aug(x, y, yp):
                """Augmented Lagrangian: L(x, y, y') + λ · G(x, y, y')."""
                return functional(x, y, yp) + lam * constraint(x, y, yp)
            return L_aug

        # Solve Euler-Lagrange for different λ values and find λ that satisfies constraint
        def constraint_error(lam):
            """Error in constraint satisfaction."""
            try:
                L_aug = augmented_lagrangian(lam)
                result = self.solve_euler_lagrange(
                    L_aug,
                    boundary_conditions,
                    x_span,
                    n_points
                )

                if 'error' in result:
                    return 1e6

                # Evaluate constraint integral
                x_grid = np.array(result['x_grid'])
                y_sol = np.array(result['y_solution'])
                yp_sol = np.array(result['y_prime'])

                # Trapezoidal integration
                constraint_val = 0.0
                for i in range(len(x_grid) - 1):
                    x_i, x_ip1 = x_grid[i], x_grid[i + 1]
                    y_i, y_ip1 = y_sol[i], y_sol[i + 1]
                    yp_i, yp_ip1 = yp_sol[i], yp_sol[i + 1]

                    g_i = constraint(x_i, y_i, yp_i)
                    g_ip1 = constraint(x_ip1, y_ip1, yp_ip1)

                    constraint_val += 0.5 * (g_i + g_ip1) * (x_ip1 - x_i)

                return constraint_val - constraint_value

            except Exception:
                return 1e6

        # Find λ via root finding
        try:
            lambda_opt = brentq(constraint_error, -10.0, 10.0, xtol=1e-4)
        except ValueError:
            # Fallback to optimization
            result_opt = minimize(
                lambda lam: constraint_error(lam[0])**2,
                x0=[0.0],
                method='Nelder-Mead'
            )
            lambda_opt = result_opt.x[0]

        # Solve with optimal λ
        L_aug_opt = augmented_lagrangian(lambda_opt)
        solution = self.solve_euler_lagrange(
            L_aug_opt,
            boundary_conditions,
            x_span,
            n_points
        )

        if 'error' in solution:
            return solution

        solution['lagrange_multiplier'] = float(lambda_opt)
        solution['constraint_value'] = float(constraint_value)
        solution['method'] = 'isoperimetric_lagrange_multiplier'

        return solution

    # ========== FIRST VARIATION ==========

    def compute_first_variation(
        self,
        functional: Callable[[float, float, float], float],
        y_base: Callable[[float], float],
        direction: Callable[[float], float],
        x_span: Tuple[float, float] = (0, 1),
        epsilon: float = 1e-5
    ) -> Dict[str, Any]:
        """
        Compute first variation δJ[y](η) = d/dε J[y + ε*η]|_{ε=0}.

        This is the directional derivative of functional J in direction η.

        Args:
            functional: Lagrangian L(x, y, y')
            y_base: Base function y(x)
            direction: Variation direction η(x)
            x_span: Domain
            epsilon: Finite difference step

        Returns:
            Dictionary with first variation value
        """
        logger.info("Computing first variation")

        x_a, x_b = x_span

        def evaluate_functional(eps):
            """Evaluate J[y + eps * η]."""
            def integrand(x):
                """Evaluate functional integrand at perturbed function."""
                y = y_base(x) + eps * direction(x)
                # Numerical derivative
                h = 1e-6
                yp = (y_base(x + h) + eps * direction(x + h) - y_base(x - h) - eps * direction(x - h)) / (2 * h)
                return functional(x, y, yp)

            result, _ = quad(integrand, x_a, x_b, limit=100)
            return result

        # Finite difference approximation
        J_plus = evaluate_functional(epsilon)
        J_minus = evaluate_functional(-epsilon)
        J_0 = evaluate_functional(0.0)

        # First variation: (J_plus - J_minus) / (2 * epsilon)
        first_variation = (J_plus - J_minus) / (2 * epsilon)

        return {
            'success': True,
            'first_variation': float(first_variation),
            'J_at_base': float(J_0),
            'method': 'finite_difference',
            'epsilon': epsilon,
            'note': 'δJ[y](η) ≈ (J[y + ε*η] - J[y - ε*η]) / (2ε)'
        }

    # ========== LEGENDRE CONDITION ==========

    def apply_legendre_condition(
        self,
        lagrangian: Callable[[float, float, float], float],
        y_candidate: Callable[[float], float],
        x_span: Tuple[float, float] = (0, 1),
        n_points: int = 50
    ) -> Dict[str, Any]:
        """
        Apply Legendre condition for second-order optimality.

        Necessary condition: ∂²L/∂y'² ≥ 0 for minimum (≤ 0 for maximum)
        Strong Legendre: ∂²L/∂y'² > 0 for minimum

        Args:
            lagrangian: Lagrangian L(x, y, y')
            y_candidate: Candidate extremal y(x)
            x_span: Domain
            n_points: Test points

        Returns:
            Dictionary with Legendre condition results
        """
        logger.info("Checking Legendre condition")

        x_a, x_b = x_span
        x_test = np.linspace(x_a, x_b, n_points)

        eps = 1e-6
        d2L_dyp2_values = []

        for x in x_test:
            y = y_candidate(x)
            # Numerical derivative for y'
            h = 1e-6
            yp = (y_candidate(x + h) - y_candidate(x - h)) / (2 * h)

            # ∂L/∂y'
            def partial_yp(yp_val):
                """Evaluate Lagrangian for computing ∂L/∂y' via finite differences."""
                return lagrangian(x, y, yp_val)

            # ∂²L/∂y'² via finite differences
            d2L = (partial_yp(yp + eps) - 2 * partial_yp(yp) + partial_yp(yp - eps)) / (eps**2)
            d2L_dyp2_values.append(d2L)

        d2L_dyp2_values = np.array(d2L_dyp2_values)

        min_value = float(np.min(d2L_dyp2_values))
        all_positive = bool(np.all(d2L_dyp2_values > -1e-8))
        all_strictly_positive = bool(np.all(d2L_dyp2_values > 1e-8))

        if all_strictly_positive:
            condition_status = 'strong_legendre_satisfied'
            optimality = 'local_minimum_candidate'
        elif all_positive:
            condition_status = 'weak_legendre_satisfied'
            optimality = 'possibly_local_minimum'
        else:
            condition_status = 'legendre_violated'
            optimality = 'not_local_minimum'

        return {
            'success': True,
            'legendre_condition': condition_status,
            'optimality': optimality,
            'min_d2L_dyp2': min_value,
            'all_positive': all_positive,
            'all_strictly_positive': all_strictly_positive,
            'method': 'legendre_second_derivative_test'
        }

    # ========== GEODESIC VARIATIONAL ==========

    def solve_geodesic_variational(
        self,
        metric: Callable[[float, float], float],
        endpoints: Dict[str, Tuple[float, float]],
        n_points: int = 100
    ) -> Dict[str, Any]:
        """
        Solve geodesic problem using variational formulation.

        Minimize arc length: J[y] = ∫ √(g(x, y) * (1 + y'²)) dx
        where g(x, y) is the metric coefficient.

        For Euclidean metric g = 1, geodesics are straight lines.

        Args:
            metric: Metric coefficient g(x, y)
            endpoints: {'start': (x_a, y_a), 'end': (x_b, y_b)}
            n_points: Discretization points

        Returns:
            Dictionary with geodesic curve
        """
        logger.info("Solving geodesic problem via variational calculus")

        (x_a, y_a) = endpoints.get('start', (0.0, 0.0))
        (x_b, y_b) = endpoints.get('end', (1.0, 1.0))

        # Lagrangian for arc length: L = √(g(x, y) * (1 + y'²))
        def lagrangian(x, y, yp):
            """Arc length Lagrangian in metric space: L = √(g(x,y) · (1 + y'²))."""
            g = metric(x, y)
            return np.sqrt(g * (1 + yp**2))

        result = self.solve_euler_lagrange(
            lagrangian,
            {'y_a': y_a, 'y_b': y_b},
            x_span=(x_a, x_b),
            n_points=n_points
        )

        if 'error' in result:
            return result

        result['method'] = 'geodesic_variational'
        result['note'] = 'Geodesic computed as extremal of arc length functional'

        return result

    # ========== DIRECT METHODS ==========

    def direct_method_minimization(
        self,
        functional: Callable[[float, float, float], float],
        boundary_conditions: Dict[str, float],
        x_span: Tuple[float, float] = (0, 1),
        n_basis: int = 10,
        basis_type: str = 'polynomial'
    ) -> Dict[str, Any]:
        """
        Direct method (Ritz/Galerkin) for variational problems.

        Approximate y(x) = y_boundary(x) + Σ c_i * φ_i(x)
        where φ_i are basis functions satisfying φ_i(x_a) = φ_i(x_b) = 0.

        Minimize J[y] over coefficients c_i.

        Args:
            functional: Lagrangian L(x, y, y')
            boundary_conditions: Boundary values
            x_span: Domain
            n_basis: Number of basis functions
            basis_type: 'polynomial' or 'fourier'

        Returns:
            Dictionary with approximate solution
        """
        logger.info(f"Direct method with {n_basis} {basis_type} basis functions")

        x_a, x_b = x_span
        y_a = boundary_conditions.get('y_a', 0.0)
        y_b = boundary_conditions.get('y_b', 0.0)

        # Linear boundary interpolation
        def y_boundary(x):
            """Linear interpolation satisfying boundary conditions y(x_a) = y_a, y(x_b) = y_b."""
            return y_a + (y_b - y_a) * (x - x_a) / (x_b - x_a)

        # Basis functions (vanish at boundaries)
        if basis_type == 'polynomial':
            def phi(i, x):
                """Polynomial basis function: (x - x_a)^(i+1) · (x_b - x), vanishes at boundaries."""
                # (x - x_a)^(i+1) * (x_b - x)
                return ((x - x_a)**(i + 1)) * (x_b - x)
        elif basis_type == 'fourier':
            def phi(i, x):
                """Fourier basis function: sin((i+1)π(x-x_a)/(x_b-x_a)), vanishes at boundaries."""
                # sin(i * π * (x - x_a) / (x_b - x_a))
                return np.sin((i + 1) * np.pi * (x - x_a) / (x_b - x_a))
        else:
            return {'error': f'Unknown basis type: {basis_type}'}

        # Objective function for coefficients c
        def objective(c):
            """J[y] for y = y_boundary + Σ c_i φ_i."""
            def y_approx(x):
                """Approximate solution: y(x) = y_boundary(x) + Σ c_i φ_i(x)."""
                return y_boundary(x) + sum(c[i] * phi(i, x) for i in range(len(c)))

            def yp_approx(x):
                """Numerical derivative of approximate solution y'(x)."""
                # Numerical derivative
                h = 1e-6
                return (y_approx(x + h) - y_approx(x - h)) / (2 * h)

            def integrand(x):
                """Evaluate functional at approximate solution: F(x, y_approx, y'_approx)."""
                return functional(x, y_approx(x), yp_approx(x))

            result, _ = quad(integrand, x_a, x_b, limit=100)
            return result

        # Minimize over coefficients
        c_initial = np.zeros(n_basis)
        result_opt = minimize(
            objective,
            c_initial,
            method='BFGS',
            options={'maxiter': 500}
        )

        c_opt = result_opt.x

        # Evaluate solution on grid
        x_grid = np.linspace(x_a, x_b, 100)
        y_solution = [
            y_boundary(x) + sum(c_opt[i] * phi(i, x) for i in range(n_basis))
            for x in x_grid
        ]

        return {
            'success': True,
            'x_grid': x_grid.tolist(),
            'y_solution': y_solution,
            'coefficients': c_opt.tolist(),
            'functional_value': float(result_opt.fun),
            'n_basis': n_basis,
            'basis_type': basis_type,
            'method': 'direct_ritz_galerkin'
        }

    # ========== NOETHER'S THEOREM ==========

    def apply_noethers_theorem(
        self,
        lagrangian: Callable[[float, float, float], float],
        symmetry: Dict[str, Any],
        y_solution: Callable[[float], float],
        x_span: Tuple[float, float] = (0, 1),
        n_points: int = 50
    ) -> Dict[str, Any]:
        """
        Apply Noether's theorem: symmetries → conservation laws.

        If functional J[y] is invariant under transformation (x, y) → (x', y'),
        then there exists a conserved quantity along extremals.

        Conserved quantity: I = ∂L/∂y' * (dy/dε) - H * (dx/dε)
        where H = y' * (∂L/∂y') - L is the Hamiltonian.

        Args:
            lagrangian: Lagrangian L(x, y, y')
            symmetry: Transformation {'dx_deps': ξ(x, y), 'dy_deps': η(x, y)}
            y_solution: Extremal solution y(x)
            x_span: Domain
            n_points: Verification points

        Returns:
            Dictionary with conserved quantity and verification
        """
        logger.info("Applying Noether's theorem")

        x_a, x_b = x_span
        xi = symmetry.get('dx_deps', lambda x, y: 0.0)  # ξ(x, y)
        eta = symmetry.get('dy_deps', lambda x, y: 1.0)  # η(x, y)

        x_test = np.linspace(x_a, x_b, n_points)
        conserved_values = []

        eps = 1e-6

        for x in x_test:
            y = y_solution(x)
            h = 1e-6
            yp = (y_solution(x + h) - y_solution(x - h)) / (2 * h)

            # ∂L/∂y'
            dL_dyp = (lagrangian(x, y, yp + eps) - lagrangian(x, y, yp - eps)) / (2 * eps)

            # Hamiltonian H = y' * (∂L/∂y') - L
            H = yp * dL_dyp - lagrangian(x, y, yp)

            # Conserved quantity: I = (∂L/∂y') * η - H * ξ
            I = dL_dyp * eta(x, y) - H * xi(x, y)

            conserved_values.append(I)

        conserved_values = np.array(conserved_values)
        mean_value = float(np.mean(conserved_values))
        std_value = float(np.std(conserved_values))
        is_conserved = bool(std_value < 0.01 * abs(mean_value) + 1e-6)

        return {
            'success': True,
            'conserved_quantity_mean': mean_value,
            'conserved_quantity_std': std_value,
            'is_conserved': is_conserved,
            'conservation_quality': f'{std_value / (abs(mean_value) + 1e-10) * 100:.2f}% variation',
            'method': 'noether_theorem',
            'note': 'Conserved quantity: I = (∂L/∂y\') * η - H * ξ along extremal'
        }

    # ========== BDI METHODS ==========

    def update_beliefs(self):
        """Update beliefs from blackboard."""
        if self.blackboard:
            entries = self.blackboard.query_entries(
                tags=['variational_calculus'],
                status='pending'
            ) if hasattr(self.blackboard, 'query_entries') else []

            for entry in entries:
                self.add_belief('pending_variational_task', entry, source='blackboard')

    def deliberate(self) -> List[Intention]:
        """Generate intentions for variational calculus tasks."""
        intentions = []

        if self.tasks_executed > 50:
            intentions.append(Intention('update_solution_cache', priority=1))

        if self.has_belief('pending_variational_task'):
            task_belief = self.get_belief('pending_variational_task')
            if task_belief:
                intentions.append(Intention(
                    'solve_variational_problem',
                    priority=5,
                    context={'task': task_belief.content}
                ))

        return intentions

    def execute_step(self, intention: Intention):
        """Execute intention step."""
        if intention.action == 'update_solution_cache':
            # Clear old cached solutions
            if len(self.solution_cache) > 100:
                self.solution_cache.clear()
                logger.info(f"[{self.agent_id}] Cleared solution cache")

    def get_statistics(self):
        """Return agent statistics."""
        return {
            **super().get_statistics(),
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'success_rate': f'{self.tasks_succeeded / max(self.tasks_executed, 1) * 100:.1f}%'
        }
