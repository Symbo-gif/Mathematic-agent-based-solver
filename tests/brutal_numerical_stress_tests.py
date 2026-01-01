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
BRUTAL NUMERICAL STRESS TESTS
=============================

50 Research-level pathological test cases designed to BREAK the numerical domain:
- NumericalMethodsSpecialist
- NumericalComputationUtility
- OptimizationSpecialist
- SplineSpecialist
- LinearSystemsSpecialist
- PDESpecialist
- AdvancedQuadratureSpecialist

These tests expose fundamental limitations in:
1. Root finding for clustered/multiple roots
2. High-dimensional Rosenbrock optimization
3. Runge phenomenon in interpolation
4. Ill-conditioned linear systems
5. PDEs with discontinuous coefficients
6. Highly oscillatory quadrature
7. Numerical differentiation with noise
8. Stiff ODEs spanning extreme timescales
9. Saddle point / minimax optimization
10. Weakly singular integral equations

Difficulty levels:
- brutal: Will cause significant accuracy loss or slow convergence
- extreme: Will likely cause algorithm failure or wrong answers
- pathological: Mathematically designed to break standard algorithms
"""

import math
from typing import Dict, List, Any, Optional, Callable, Tuple

# =============================================================================
# BRUTAL NUMERICAL STRESS TESTS (50 tests)
# =============================================================================

BRUTAL_NUMERICAL_TESTS: List[Dict[str, Any]] = [

    # =========================================================================
    # CATEGORY 1: ROOT FINDING - CLUSTERED ROOTS (NUM_001 - NUM_005)
    # =========================================================================

    {
        "test_id": "NUM_001",
        "category": "root_finding_clustered",
        "input": {
            "function": "lambda x: (x - 1.0) * (x - 1.0001) * (x - 1.0002)",
            "bracket": [0.5, 1.5],
            "description": "Polynomial with 3 roots separated by 1e-4"
        },
        "expected": {
            "roots": [1.0, 1.0001, 1.0002],
            "tolerance": 1e-6,
            "note": "Standard bisection/Brent cannot distinguish roots closer than tolerance"
        },
        "difficulty": "brutal",
        "rationale": "Roots separated by 1e-4 are nearly indistinguishable to standard root finders using 1e-10 tolerance. The sign changes are too close together, causing the algorithm to find only one root or oscillate between them."
    },

    {
        "test_id": "NUM_002",
        "category": "root_finding_clustered",
        "input": {
            "function": "lambda x: (x**2 - 1)**10",  # Root at x=1 with multiplicity 20
            "bracket": [0.5, 1.5],
            "x0": 0.5,
            "description": "High-multiplicity root (multiplicity 20 at x=1)"
        },
        "expected": {
            "root": 1.0,
            "convergence_rate": "linear",  # Not quadratic due to multiplicity
            "note": "Newton's method degrades from quadratic to linear convergence for multiple roots"
        },
        "difficulty": "extreme",
        "rationale": "Newton's method converges only linearly (not quadratically) for roots with multiplicity > 1. The derivative nearly vanishes near the root, causing numerical instability. Standard implementations will take 10-100x more iterations."
    },

    {
        "test_id": "NUM_003",
        "category": "root_finding_clustered",
        "input": {
            "function": "lambda x: math.sin(1.0 / x) if x != 0 else 0",
            "bracket": [0.01, 0.1],
            "description": "sin(1/x) - infinitely many roots accumulating at x=0"
        },
        "expected": {
            "roots": "infinite_in_interval",
            "first_few": [0.3183, 0.1592, 0.1061, 0.0796],  # 1/(n*pi)
            "note": "Roots cluster infinitely densely near x=0"
        },
        "difficulty": "pathological",
        "rationale": "sin(1/x) has roots at x = 1/(n*pi) for integer n. Near x=0, there are infinitely many roots in any interval (0, epsilon). No bracketing algorithm can enumerate them all, and the function oscillates infinitely fast."
    },

    {
        "test_id": "NUM_004",
        "category": "root_finding_clustered",
        "input": {
            "function": "lambda x: x**20 - 1",
            "bracket": [0.5, 1.5],
            "description": "20th roots of unity (real root at x=1, with extreme flatness)"
        },
        "expected": {
            "root": 1.0,
            "derivative_at_root": 20.0,
            "note": "Function is extremely flat for |x| < 1, causing slow convergence"
        },
        "difficulty": "brutal",
        "rationale": "For |x| < 1, x^20 is essentially zero (0.9^20 = 0.12). The function transitions from ~0 to ~1 very rapidly near x=1. Newton's method from x0 < 1 will take enormous steps because f(x)/f'(x) is huge."
    },

    {
        "test_id": "NUM_005",
        "category": "root_finding_clustered",
        "input": {
            "function": "lambda x: (x - 0.5) * math.exp(-(x - 0.5)**2 / 1e-6)",
            "bracket": [0.0, 1.0],
            "description": "Root at x=0.5 but function is essentially zero except in tiny neighborhood"
        },
        "expected": {
            "root": 0.5,
            "effective_width": 1e-3,
            "note": "Function is numerically zero outside |x-0.5| < 1e-3"
        },
        "difficulty": "extreme",
        "rationale": "The Gaussian factor exp(-(x-0.5)^2/1e-6) = exp(-1e6*(x-0.5)^2) is essentially zero for |x-0.5| > 0.003. Bisection will appear to find a root anywhere in (0, 0.497) or (0.503, 1) because f(x) underflows to zero."
    },

    # =========================================================================
    # CATEGORY 2: HIGH-DIMENSIONAL ROSENBROCK OPTIMIZATION (NUM_006 - NUM_010)
    # =========================================================================

    {
        "test_id": "NUM_006",
        "category": "optimization_rosenbrock",
        "input": {
            "function": "Rosenbrock in 10 dimensions",
            "formula": "sum_{i=0}^{n-2} [100*(x_{i+1} - x_i^2)^2 + (1 - x_i)^2]",
            "x0": [0.0] * 10,
            "n_dims": 10
        },
        "expected": {
            "minimum": [1.0] * 10,
            "f_min": 0.0,
            "condition_number": ">1e6",
            "note": "10D Rosenbrock is notoriously difficult - curved narrow valley"
        },
        "difficulty": "brutal",
        "rationale": "The Rosenbrock function has a long, narrow, parabolic valley. The global minimum is inside this valley but finding it requires navigating a curved path. Gradient descent oscillates back and forth across the valley, making tiny progress along it. Condition number grows exponentially with dimension."
    },

    {
        "test_id": "NUM_007",
        "category": "optimization_rosenbrock",
        "input": {
            "function": "Rosenbrock in 50 dimensions",
            "formula": "sum_{i=0}^{n-2} [100*(x_{i+1} - x_i^2)^2 + (1 - x_i)^2]",
            "x0": [-1.0] * 50,
            "n_dims": 50
        },
        "expected": {
            "minimum": [1.0] * 50,
            "f_min": 0.0,
            "iterations_needed": ">100000",
            "note": "50D Rosenbrock - BFGS will struggle with memory and conditioning"
        },
        "difficulty": "extreme",
        "rationale": "At 50 dimensions, BFGS requires storing a 50x50 Hessian approximation. The valley becomes increasingly curved and narrow. Starting from x = [-1, -1, ...] requires the algorithm to first reach the valley mouth and then navigate the entire length. L-BFGS helps with memory but not with the fundamental geometry."
    },

    {
        "test_id": "NUM_008",
        "category": "optimization_rosenbrock",
        "input": {
            "function": "Rotated Rosenbrock in 20 dimensions",
            "formula": "Rosenbrock(R @ x) where R is random orthogonal",
            "x0": [2.0] * 20,
            "rotation": "random_orthogonal_matrix",
            "n_dims": 20
        },
        "expected": {
            "minimum": "R.T @ [1, 1, ..., 1]",
            "f_min": 0.0,
            "note": "Rotation destroys any coordinate-aligned structure exploited by methods"
        },
        "difficulty": "extreme",
        "rationale": "Standard implementations may exploit coordinate alignment. Rotation removes this advantage entirely. The narrow valley is now oriented in a random direction, making it nearly impossible for methods that rely on coordinate-wise updates or finite differences along axes."
    },

    {
        "test_id": "NUM_009",
        "category": "optimization_rosenbrock",
        "input": {
            "function": "Noisy Rosenbrock in 10 dimensions",
            "formula": "Rosenbrock(x) + 0.01 * noise(x)",
            "noise_type": "deterministic_hash",
            "x0": [0.5] * 10,
            "n_dims": 10
        },
        "expected": {
            "approximate_minimum": [1.0] * 10,
            "tolerance": 0.1,
            "note": "Noise prevents convergence below noise floor"
        },
        "difficulty": "brutal",
        "rationale": "Adding 1% noise completely breaks gradient-based methods when near the minimum (where the true gradient is ~0). The algorithm will wander randomly in a neighborhood of size proportional to noise/curvature. Line search will also fail because it cannot distinguish improvement from noise."
    },

    {
        "test_id": "NUM_010",
        "category": "optimization_rosenbrock",
        "input": {
            "function": "Extended Rosenbrock with multiple minima",
            "formula": "Rosenbrock + 0.5*sin(10*x_1)*sin(10*x_2)*...",
            "x0": [3.0] * 10,
            "n_dims": 10
        },
        "expected": {
            "global_minimum": "near [1, 1, ..., 1]",
            "local_minima": "exponentially_many",
            "note": "Sinusoidal perturbation creates a landscape full of local minima"
        },
        "difficulty": "pathological",
        "rationale": "The product of sines creates 10^n local features in the landscape. Any local optimizer will get trapped. The global minimum is approximately preserved but there are countless local minima with objective values only slightly higher than global optimum."
    },

    # =========================================================================
    # CATEGORY 3: SPLINE INTERPOLATION - RUNGE PHENOMENON (NUM_011 - NUM_015)
    # =========================================================================

    {
        "test_id": "NUM_011",
        "category": "spline_runge",
        "input": {
            "function": "lambda x: 1.0 / (1.0 + 25.0 * x**2)",
            "interval": [-1, 1],
            "n_points": 21,
            "point_distribution": "equispaced",
            "description": "Runge's function 1/(1+25x^2) with equispaced nodes"
        },
        "expected": {
            "max_error": ">1.0",  # Error grows unboundedly near boundaries
            "error_location": "near_boundaries",
            "note": "Equispaced polynomial interpolation diverges for this function"
        },
        "difficulty": "brutal",
        "rationale": "The Runge phenomenon: for f(x) = 1/(1+25x^2), polynomial interpolation on equispaced nodes diverges as n increases. At n=21, the interpolating polynomial oscillates wildly near x = +/- 1, with errors exceeding the function values themselves."
    },

    {
        "test_id": "NUM_012",
        "category": "spline_runge",
        "input": {
            "function": "lambda x: abs(x)",
            "interval": [-1, 1],
            "n_points": 50,
            "point_distribution": "equispaced",
            "description": "Absolute value function - non-differentiable at origin"
        },
        "expected": {
            "convergence_rate": "slow",
            "gibbs_phenomenon": "present_at_origin",
            "note": "Polynomial interpolation struggles with non-smooth functions"
        },
        "difficulty": "brutal",
        "rationale": "|x| has a corner at x=0. High-degree polynomial interpolation will exhibit Gibbs-like oscillations near x=0. Unlike smooth Runge's function, this fails because of genuine lack of smoothness, not merely high derivatives."
    },

    {
        "test_id": "NUM_013",
        "category": "spline_runge",
        "input": {
            "function": "lambda x: math.sin(50*x)",
            "interval": [0, 1],
            "n_points": 10,
            "description": "High-frequency sine undersampled (Nyquist violation)"
        },
        "expected": {
            "aliasing": "severe",
            "apparent_frequency": "different_from_50",
            "note": "10 points cannot resolve 50 oscillations - severe aliasing"
        },
        "difficulty": "extreme",
        "rationale": "sin(50x) completes about 8 full oscillations in [0,1]. With only 10 sample points, we have ~1.25 points per period - far below the Nyquist rate of 2 points per period. The interpolant will appear to have a completely different (lower) frequency."
    },

    {
        "test_id": "NUM_014",
        "category": "spline_runge",
        "input": {
            "x_data": [0.0, 0.1, 0.2, 0.3, 0.5, 0.501, 0.502, 0.7, 0.8, 1.0],
            "y_data": [1.0, 1.5, 2.0, 2.3, 3.0, 15.0, 3.0, 2.5, 2.0, 1.5],
            "description": "Outlier spike at x=0.501 - tests spline robustness"
        },
        "expected": {
            "overshoot": "significant",
            "oscillation_range": ">[-5, 20]",
            "note": "Cubic spline will exhibit large oscillations around outlier"
        },
        "difficulty": "brutal",
        "rationale": "A single outlier (y=15 surrounded by y~3) causes cubic splines to overshoot dramatically. The C2 continuity requirement propagates the perturbation far from the outlier. The spline may exhibit negative values or exceed 20 in regions away from the data."
    },

    {
        "test_id": "NUM_015",
        "category": "spline_runge",
        "input": {
            "x_data": "list(range(100))",  # 0, 1, 2, ..., 99
            "y_data": "random_uniform_1000",  # 100 random values in [0, 1000]
            "extrapolation_point": 150,
            "description": "Extrapolation far beyond data range"
        },
        "expected": {
            "extrapolated_value": "unbounded_polynomial_growth",
            "sensible_range": "[0, 1000]",
            "actual_range": "possibly_[-1e6, 1e6]",
            "note": "Polynomial/spline extrapolation is notoriously unreliable"
        },
        "difficulty": "extreme",
        "rationale": "Extrapolating a degree-n polynomial beyond the data range leads to values growing like x^n. For noisy data, the polynomial coefficients can be large and alternating, causing explosive growth outside the interpolation interval."
    },

    # =========================================================================
    # CATEGORY 4: ILL-CONDITIONED LINEAR SYSTEMS (NUM_016 - NUM_020)
    # =========================================================================

    {
        "test_id": "NUM_016",
        "category": "linear_systems_illconditioned",
        "input": {
            "matrix": "Hilbert matrix H_n where H[i,j] = 1/(i+j+1)",
            "size": 15,
            "b": "ones vector",
            "description": "15x15 Hilbert matrix - condition number ~1e18"
        },
        "expected": {
            "condition_number": ">1e17",
            "residual": "<1e-10",
            "forward_error": ">1e3",  # x_computed very different from x_true
            "note": "Small residual but HUGE forward error - ill-conditioning hallmark"
        },
        "difficulty": "pathological",
        "rationale": "The Hilbert matrix is the canonical example of ill-conditioning. At n=15, condition number exceeds 10^17. This means that machine precision errors (10^-16) are amplified to errors of order 10. The computed solution will have essentially no correct digits, even though Ax - b appears small."
    },

    {
        "test_id": "NUM_017",
        "category": "linear_systems_illconditioned",
        "input": {
            "matrix": "Vandermonde matrix V[i,j] = x_i^j",
            "nodes": "[1, 2, 3, ..., 20]",
            "size": 20,
            "description": "20x20 Vandermonde on integers 1-20"
        },
        "expected": {
            "condition_number": ">1e15",
            "iterative_convergence": "extremely_slow_or_divergent",
            "note": "Vandermonde with close nodes is extremely ill-conditioned"
        },
        "difficulty": "extreme",
        "rationale": "Vandermonde matrices V[i,j] = x_i^j are ill-conditioned when nodes are not well-separated. With integer nodes 1-20, columns become nearly linearly dependent because polynomials of nearby degrees evaluated at similar points produce similar vectors."
    },

    {
        "test_id": "NUM_018",
        "category": "linear_systems_illconditioned",
        "input": {
            "matrix": "Nearly singular: [[1, 1], [1, 1 + 1e-15]]",
            "size": 2,
            "b": [1, 1],
            "description": "2x2 matrix with determinant ~1e-15"
        },
        "expected": {
            "determinant": "~1e-15",
            "solution_sensitivity": "enormous",
            "note": "Tiny change in b causes huge change in x"
        },
        "difficulty": "brutal",
        "rationale": "This matrix has determinant 1e-15, making it nearly singular. The solution is extremely sensitive: changing b by 1e-16 can change x by order 1. Gauss-Seidel and Jacobi will either diverge or converge to the wrong answer."
    },

    {
        "test_id": "NUM_019",
        "category": "linear_systems_illconditioned",
        "input": {
            "matrix": "Tridiagonal: diag(-1, 2, -1) but with A[n,n] = 2 - 1e-12",
            "size": 1000,
            "description": "1000x1000 nearly singular tridiagonal"
        },
        "expected": {
            "spectral_radius_jacobi": "~1 - epsilon",
            "convergence": "extremely_slow",
            "iterations_needed": ">1e8",
            "note": "Spectral radius barely less than 1 causes glacial convergence"
        },
        "difficulty": "extreme",
        "rationale": "For iterative methods, convergence rate depends on spectral radius rho of the iteration matrix. Here rho ~= 1 - 1e-12, meaning error reduces by factor 1e-12 per iteration. Reaching error 1e-10 would require 10^10 / 12 ~= 10^9 iterations."
    },

    {
        "test_id": "NUM_020",
        "category": "linear_systems_illconditioned",
        "input": {
            "matrix": "Random SPD with eigenvalues [1e-10, 1e-9, ..., 1e10]",
            "size": 21,
            "eigenvalue_range": "[1e-10, 1e10]",
            "description": "SPD matrix with condition number 1e20"
        },
        "expected": {
            "cg_convergence": "very_slow",
            "cg_iterations_bound": "O(sqrt(kappa)) = O(1e10)",
            "note": "CG convergence bound grows with sqrt(condition_number)"
        },
        "difficulty": "pathological",
        "rationale": "Conjugate Gradient on SPD matrices theoretically converges in n steps, but practical convergence depends on condition number. With kappa = 1e20, the CG error bound after k steps involves (sqrt(kappa)-1)/(sqrt(kappa)+1)^k, which is essentially 1 for k << 1e10."
    },

    # =========================================================================
    # CATEGORY 5: PDEs WITH DISCONTINUOUS COEFFICIENTS (NUM_021 - NUM_025)
    # =========================================================================

    {
        "test_id": "NUM_021",
        "category": "pde_discontinuous",
        "input": {
            "equation": "heat equation: u_t = alpha(x) * u_xx",
            "alpha": "lambda x: 1.0 if x < 0.5 else 1000.0",
            "description": "Heat equation with conductivity jump of 1000x at x=0.5"
        },
        "expected": {
            "solution_behavior": "discontinuous_gradient_at_interface",
            "numerical_difficulty": "sharp_resolution_needed",
            "note": "Standard schemes smear the interface over O(dx) region"
        },
        "difficulty": "brutal",
        "rationale": "When thermal conductivity jumps by factor 1000, the temperature gradient must jump correspondingly to maintain heat flux continuity. Finite difference schemes cannot resolve this discontinuous derivative without extremely fine grids near the interface."
    },

    {
        "test_id": "NUM_022",
        "category": "pde_discontinuous",
        "input": {
            "equation": "advection: u_t + c(x)*u_x = 0",
            "velocity": "lambda x: 1.0 if x < 0.5 else -1.0",
            "initial": "lambda x: math.exp(-(x-0.25)**2 / 0.01)",
            "description": "Advection with opposing velocities - shock formation"
        },
        "expected": {
            "solution": "shock_wave_at_x=0.5",
            "numerical_issues": "oscillations_or_excessive_diffusion",
            "note": "Requires shock-capturing schemes or entropy conditions"
        },
        "difficulty": "extreme",
        "rationale": "Material advected from left meets material advected from right at x=0.5. Without proper shock-capturing (upwinding, limiting, or artificial viscosity), numerical solutions exhibit spurious oscillations (Gibbs phenomenon) or excessive smearing."
    },

    {
        "test_id": "NUM_023",
        "category": "pde_discontinuous",
        "input": {
            "equation": "Poisson: -div(k(x,y) grad u) = f",
            "conductivity": "k = 1 in circle, k = 1e-6 outside",
            "source": "f = 1 everywhere",
            "description": "Elliptic PDE with 1e6 contrast in coefficients"
        },
        "expected": {
            "solution": "nearly_constant_inside_circle",
            "numerical_difficulty": "extreme_mesh_refinement_needed",
            "note": "High contrast ratios require specialized preconditioners"
        },
        "difficulty": "extreme",
        "rationale": "With coefficient ratio 10^6, the resulting linear system is extremely ill-conditioned. Standard multigrid and Krylov methods may fail or converge very slowly. The solution structure (nearly constant in high-conductivity region) is numerically difficult to capture."
    },

    {
        "test_id": "NUM_024",
        "category": "pde_discontinuous",
        "input": {
            "equation": "wave equation: u_tt = c(x)^2 * u_xx",
            "wave_speed": "c = 1 for x < 0.5, c = 10 for x >= 0.5",
            "initial": "Gaussian pulse at x = 0.25",
            "description": "Wave equation with impedance mismatch"
        },
        "expected": {
            "solution": "reflected_and_transmitted_waves",
            "reflection_coefficient": "(c1-c2)/(c1+c2) = -9/11",
            "numerical_issues": "spurious_reflections_from_grid",
            "note": "Requires careful handling of material interface"
        },
        "difficulty": "brutal",
        "rationale": "At the interface x=0.5, the wave speed changes by factor 10. Physics requires specific reflection/transmission coefficients. Numerical schemes may produce spurious reflections from grid discontinuities in addition to the physical ones, contaminating the solution."
    },

    {
        "test_id": "NUM_025",
        "category": "pde_discontinuous",
        "input": {
            "equation": "transport with source: u_t + u_x = S(x)",
            "source": "S = delta(x - 0.5)",  # Dirac delta
            "description": "Advection with point source (Dirac delta)"
        },
        "expected": {
            "weak_solution": "step function",
            "numerical_approximation": "smeared_over_cells",
            "note": "Dirac delta requires special handling in weak form"
        },
        "difficulty": "extreme",
        "rationale": "A Dirac delta source cannot be represented on a discrete grid. Smearing it over one or more cells changes the solution character. The true solution is a step function, but numerical solutions will be smooth ramps spanning several grid points."
    },

    # =========================================================================
    # CATEGORY 6: HIGHLY OSCILLATORY QUADRATURE (NUM_026 - NUM_030)
    # =========================================================================

    {
        "test_id": "NUM_026",
        "category": "quadrature_oscillatory",
        "input": {
            "integrand": "lambda x: math.sin(1000 * x)",
            "interval": [0, 1],
            "description": "sin(1000x) - 159 complete oscillations in [0,1]"
        },
        "expected": {
            "integral": "(1 - cos(1000)) / 1000 ~= 0.000437",
            "min_points_needed": "~3200 (Nyquist)",
            "note": "Standard Gauss-Legendre with n<1000 will fail catastrophically"
        },
        "difficulty": "brutal",
        "rationale": "With 159 oscillations in [0,1], at least 318 quadrature points are needed to avoid aliasing (Nyquist), and 1000+ for reasonable accuracy. Gauss quadrature is designed for smooth functions and will give nonsense for n << 159."
    },

    {
        "test_id": "NUM_027",
        "category": "quadrature_oscillatory",
        "input": {
            "integrand": "lambda x: math.exp(1j * x**2)",  # Fresnel-like
            "interval": [0, 100],
            "description": "exp(i*x^2) - frequency increases with x"
        },
        "expected": {
            "integral": "Fresnel integral ~= 0.89 + 0.89j",
            "numerical_difficulty": "increasing_frequency",
            "note": "Stationary phase methods required for large upper limit"
        },
        "difficulty": "extreme",
        "rationale": "The integrand exp(i*x^2) has frequency proportional to x, reaching ~100 rad/unit at x=100. Near x=100, the function oscillates about 16 times per unit interval. Standard quadrature would need ~10000 points in the last unit alone."
    },

    {
        "test_id": "NUM_028",
        "category": "quadrature_oscillatory",
        "input": {
            "integrand": "lambda x: math.sin(1/x) / x**2",
            "interval": [0.001, 1],
            "description": "sin(1/x)/x^2 - infinite oscillations near x=0"
        },
        "expected": {
            "integral": "cos(1) - cos(1000) ~= 0.54 - 0.56 = -0.02 (approx)",
            "oscillation_count": "infinite_as_x_to_0",
            "note": "Oscillations become infinitely rapid near x=0"
        },
        "difficulty": "pathological",
        "rationale": "Near x=0, sin(1/x) oscillates infinitely fast. The integrand completes one oscillation as x goes from 1/(n*pi) to 1/((n+1)*pi), which is a vanishingly small interval as n->infinity. No finite quadrature can capture all oscillations."
    },

    {
        "test_id": "NUM_029",
        "category": "quadrature_oscillatory",
        "input": {
            "integrand": "lambda x: J_0(1000 * x) * math.exp(-x)",
            "interval": [0, 10],
            "description": "Bessel function J_0(1000x) * exp(-x)"
        },
        "expected": {
            "bessel_oscillations": "~159 in [0,1]",
            "integral": "special_function_value",
            "note": "Combines oscillatory Bessel with decay - cancellation issues"
        },
        "difficulty": "extreme",
        "rationale": "J_0(z) oscillates with approximate period 2*pi. For J_0(1000x), we get ~159 oscillations in [0,1]. The exponential decay exp(-x) eventually damps the oscillations, but in the intermediate region both effects compete, causing severe cancellation."
    },

    {
        "test_id": "NUM_030",
        "category": "quadrature_oscillatory",
        "input": {
            "integrand": "lambda x: math.cos(omega * x) / (1 + x**2)",
            "omega": 1000,
            "interval": [-100, 100],
            "description": "Fourier integral of Lorentzian with omega=1000"
        },
        "expected": {
            "analytical": "pi * exp(-1000) ~= 0",  # But numerically disastrous
            "cancellation": "extreme",
            "note": "Result is 10^-434 but integrand reaches +/- 1"
        },
        "difficulty": "pathological",
        "rationale": "The exact answer is pi*exp(-|omega|) which for omega=1000 is about 10^-434 - essentially zero. But the integrand oscillates between +/-1 over a wide range. Numerical quadrature will sum terms of order 1 and try to get 10^-434 - impossible due to cancellation."
    },

    # =========================================================================
    # CATEGORY 7: NUMERICAL DIFFERENTIATION WITH NOISE (NUM_031 - NUM_035)
    # =========================================================================

    {
        "test_id": "NUM_031",
        "category": "differentiation_noisy",
        "input": {
            "function": "lambda x: x**2 + 1e-8 * random.uniform(-1, 1)",
            "point": 1.0,
            "true_derivative": 2.0,
            "noise_amplitude": 1e-8,
            "description": "Quadratic with 1e-8 noise - optimal h is ~1e-4"
        },
        "expected": {
            "optimal_h": "~(3 * noise * f(x) / f''(x))^(1/3) ~= 1e-4",
            "best_achievable_error": "~1e-4",
            "note": "Noise fundamentally limits differentiation accuracy"
        },
        "difficulty": "brutal",
        "rationale": "For noisy functions, making h smaller eventually amplifies noise instead of reducing truncation error. The optimal h balances O(h^2) truncation error against O(noise/h) amplification. For noise = 1e-8, optimal h ~= 1e-4 gives error ~= 1e-4."
    },

    {
        "test_id": "NUM_032",
        "category": "differentiation_noisy",
        "input": {
            "function": "lambda x: math.sin(x) + 1e-6 * math.sin(1e6 * x)",
            "point": 1.0,
            "description": "sin(x) with high-frequency perturbation"
        },
        "expected": {
            "true_derivative": "cos(1)",
            "computed_derivative": "cos(1) + O(1)",
            "problem": "high_frequency_amplified_by_differentiation",
            "note": "Derivative of noise is omega*noise - much larger than noise itself"
        },
        "difficulty": "extreme",
        "rationale": "While the perturbation 1e-6*sin(1e6*x) is small, its derivative is 1e-6 * 1e6 * cos(1e6*x) = cos(1e6*x), which is O(1). Numerical differentiation will pick up this derivative, completely obscuring the true derivative of sin(x)."
    },

    {
        "test_id": "NUM_033",
        "category": "differentiation_noisy",
        "input": {
            "function": "lambda x: round(x**2, 4)",  # Quantized to 4 decimals
            "point": 1.0,
            "h_values": [1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7],
            "description": "Quantized function - constant on small intervals"
        },
        "expected": {
            "derivative_sequence": "[2.1, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0]",
            "note": "For h < 1e-4, quantized values are identical -> derivative = 0"
        },
        "difficulty": "brutal",
        "rationale": "When f(x) is quantized to 4 decimal places, f(x+h) = f(x) for all h < 1e-4/f'(x). The finite difference becomes 0/h = 0, giving completely wrong derivatives. This happens with any digitized data."
    },

    {
        "test_id": "NUM_034",
        "category": "differentiation_noisy",
        "input": {
            "function": "lambda x: x**3 if x > 0 else 0",  # Not C^3 at origin
            "point": 0.0,
            "derivative_order": 3,
            "description": "Third derivative at point of reduced smoothness"
        },
        "expected": {
            "analytical_third_derivative": "6 for x > 0, 0 for x < 0",
            "at_x_0": "undefined (jump discontinuity)",
            "numerical_result": "highly_h_dependent",
            "note": "Third derivative doesn't exist at x=0 in classical sense"
        },
        "difficulty": "extreme",
        "rationale": "The function f(x) = x^3 * H(x) (H = Heaviside) has f''' = 6*H(x) which is discontinuous at x=0. Numerical differentiation will give different values depending on h and whether the stencil is symmetric, forward, or backward."
    },

    {
        "test_id": "NUM_035",
        "category": "differentiation_noisy",
        "input": {
            "function": "lambda x: math.exp(x) if x != 0 else float('nan')",
            "point": 0.0,
            "h_values": "[1e-1, 1e-2, ..., 1e-15, 1e-16]",
            "description": "Differentiation with h spanning from truncation to cancellation"
        },
        "expected": {
            "true_derivative": 1.0,
            "error_behavior": "U-shaped: truncation -> optimal -> cancellation",
            "optimal_h": "~1e-8",
            "h_1e16_error": "~1.0 (100% error due to catastrophic cancellation)",
            "note": "h = 1e-16 gives nonsense because f(x+h) - f(x) rounds to 0"
        },
        "difficulty": "brutal",
        "rationale": "As h decreases, truncation error shrinks like h^2 for central differences. But for h < sqrt(machine_epsilon) ~= 1e-8, cancellation error grows like 1/h. At h = 1e-16, exp(h) = 1 in floating point, so f(x+h) - f(x) = 0."
    },

    # =========================================================================
    # CATEGORY 8: STIFF ODE SYSTEMS (NUM_036 - NUM_040)
    # =========================================================================

    {
        "test_id": "NUM_036",
        "category": "ode_stiff",
        "input": {
            "system": "[y1' = -1e6*(y1 - y2), y2' = -y2]",
            "initial": "[1.0, 1.0]",
            "t_span": [0, 10],
            "stiffness_ratio": 1e6,
            "description": "Two-scale stiff system with timescales 1e-6 and 1"
        },
        "expected": {
            "fast_transient": "y1 jumps to y2 in time ~1e-6",
            "slow_dynamics": "y2 decays like exp(-t)",
            "explicit_dt_required": "<2e-6 (stability)",
            "implicit_dt_possible": "~0.1",
            "note": "RK4 needs ~10^7 steps while backward Euler needs ~100"
        },
        "difficulty": "brutal",
        "rationale": "The eigenvalues are -1e6 and -1. For explicit methods like RK4, stability requires dt < 2/1e6 = 2e-6, meaning 5 million steps for t in [0,10]. Implicit methods are stable for any dt but each step requires solving a nonlinear system."
    },

    {
        "test_id": "NUM_037",
        "category": "ode_stiff",
        "input": {
            "system": "Robertson chemical kinetics",
            "equations": "[y1' = -0.04*y1 + 1e4*y2*y3, y2' = 0.04*y1 - 1e4*y2*y3 - 3e7*y2^2, y3' = 3e7*y2^2]",
            "initial": "[1, 0, 0]",
            "t_span": [0, 1e11],  # 100 billion time units!
            "description": "Robertson problem - stiffness ratio 1e11"
        },
        "expected": {
            "final_state": "[~0, ~0, ~1]",
            "timescales": "[fast transient, medium, slow equilibration]",
            "explicit_method": "completely_infeasible",
            "note": "Classic test problem for stiff ODE solvers since 1966"
        },
        "difficulty": "pathological",
        "rationale": "The Robertson problem is the canonical stiff chemistry test. The stiffness ratio reaches 10^11. Explicit methods would need 10^17+ steps. Even implicit methods must adapt step sizes over 17 orders of magnitude as the solution equilibrates."
    },

    {
        "test_id": "NUM_038",
        "category": "ode_stiff",
        "input": {
            "system": "Van der Pol oscillator with large mu",
            "equation": "y'' - mu*(1 - y^2)*y' + y = 0",
            "mu": 1000,
            "initial": "[2, 0]",
            "t_span": [0, 3000],
            "description": "Relaxation oscillator with sharp transitions"
        },
        "expected": {
            "period": "~(3 - 2*log(2))*mu ~= 1600",
            "transition_time": "O(mu^(-1)) = O(1e-3)",
            "note": "Slow drift for most of period, then extremely fast jumps"
        },
        "difficulty": "extreme",
        "rationale": "For large mu, the Van der Pol oscillator exhibits relaxation oscillations: long periods of slow drift interrupted by extremely fast transitions. The ratio of slow to fast timescales is O(mu^2) = O(10^6). Capturing the jumps requires tiny steps, but most of the period is slow."
    },

    {
        "test_id": "NUM_039",
        "category": "ode_stiff",
        "input": {
            "system": "Oregonator (Belousov-Zhabotinsky model)",
            "equations": "3-component ODE with product k1*k3/k2*k4 = 1e-11",
            "parameters": "[k1=1.34, k2=1.6e9, k3=8e3, k4=4e7, k5=1]",
            "initial": "[1e-6, 2e-9, 0.01]",
            "t_span": [0, 360],
            "description": "Chemical oscillator with extreme rate constant ratios"
        },
        "expected": {
            "oscillation_period": "~30 seconds",
            "stiffness": "from rate constant ratios ~1e9",
            "note": "Real chemical kinetics are inherently stiff"
        },
        "difficulty": "extreme",
        "rationale": "The Oregonator models the Belousov-Zhabotinsky reaction. Rate constants span 10 orders of magnitude. The solution oscillates with period ~30s but has transients on timescale ~1e-9s. This is realistic - most chemical kinetics are stiff."
    },

    {
        "test_id": "NUM_040",
        "category": "ode_stiff",
        "input": {
            "system": "Plasma/circuit with diodes",
            "equation": "C*V' = I - I_s*(exp(V/V_T) - 1)",
            "parameters": "I_s = 1e-14, V_T = 0.026 (thermal voltage)",
            "stiffness_source": "exponential nonlinearity",
            "description": "Diode circuit - exponential stiffness near forward bias"
        },
        "expected": {
            "near_forward_bias": "exponential sensitivity",
            "jacobian_element": "dI/dV = I_s/V_T * exp(V/V_T) = 4e13 at V=1V",
            "note": "Stiffness varies by 10^13 depending on operating point"
        },
        "difficulty": "brutal",
        "rationale": "The diode equation I = I_s*(exp(V/V_T) - 1) has derivative dI/dV = I_s/V_T * exp(V/V_T). At V = 1V, this is 4e13. But at V = -0.5V, it is essentially 0. The stiffness varies by 10^13 depending on bias, requiring dramatic step size adaptation."
    },

    # =========================================================================
    # CATEGORY 9: SADDLE POINT / MINIMAX OPTIMIZATION (NUM_041 - NUM_045)
    # =========================================================================

    {
        "test_id": "NUM_041",
        "category": "optimization_saddle",
        "input": {
            "function": "lambda x: x[0]**2 - x[1]**2",
            "initial": [1.0, 1.0],
            "description": "Saddle point at origin - gradient descent fails"
        },
        "expected": {
            "saddle_point": [0.0, 0.0],
            "gradient_descent_behavior": "diverges_along_y_axis",
            "hessian_eigenvalues": "[2, -2]",
            "note": "Gradient descent follows gradient which points away from saddle along y"
        },
        "difficulty": "brutal",
        "rationale": "At the saddle point (0,0), the gradient is zero but it's not a minimum - it's a maximum in y-direction. Gradient descent from (1,1) will decrease x but may increase y, eventually diverging. Second-order methods detect the negative eigenvalue but may not know which direction to go."
    },

    {
        "test_id": "NUM_042",
        "category": "optimization_saddle",
        "input": {
            "function": "sum of x[i]^2 for i < n/2, minus sum of x[i]^2 for i >= n/2",
            "n_dims": 100,
            "description": "50 positive curvature directions, 50 negative"
        },
        "expected": {
            "saddle_manifold": "50-dimensional",
            "escape_probability_random_start": "~0",
            "note": "In high dimensions, saddle points are exponentially more common than minima"
        },
        "difficulty": "extreme",
        "rationale": "In high-dimensional optimization, saddle points vastly outnumber local minima. Here the saddle manifold is 50-dimensional while minima require all x[i]=0 for i<50 AND some x[i]!=0 for i>=50, which is measure zero. Random restarts almost always hit saddles."
    },

    {
        "test_id": "NUM_043",
        "category": "optimization_saddle",
        "input": {
            "minimax": "min_x max_y [x^2 - 2*x*y + 3*y^2]",
            "domain": "x in [-10,10], y in [-10,10]",
            "description": "Minimax problem - game theory formulation"
        },
        "expected": {
            "solution": "[x=0, y=0]",
            "value": 0,
            "difficulty": "alternating_gradient_may_cycle",
            "note": "Naive alternating optimization can cycle forever"
        },
        "difficulty": "brutal",
        "rationale": "In minimax problems, alternating between min over x and max over y can lead to cycling. For f(x,y) = x^2 - 2xy + 3y^2, fixing y and minimizing over x gives x = y; fixing x and maximizing over y gives y = x/3. This converges but slowly. Other functions cycle forever."
    },

    {
        "test_id": "NUM_044",
        "category": "optimization_saddle",
        "input": {
            "function": "lambda x: -sum(log(b[i] - A[i] @ x) for i in range(m))",
            "barrier_type": "logarithmic",
            "constraints": "100 linear inequality constraints",
            "description": "Log-barrier near constraint boundaries"
        },
        "expected": {
            "behavior_near_boundary": "gradient_explodes",
            "hessian_conditioning": "O(1/distance_to_boundary^2)",
            "note": "Interior point methods must carefully manage barrier parameter"
        },
        "difficulty": "extreme",
        "rationale": "Log-barrier functions have gradient O(1/slack) and Hessian O(1/slack^2). Near the boundary, these explode. The optimizer must balance approaching the boundary (to satisfy constraints tightly) against the numerical instability this causes."
    },

    {
        "test_id": "NUM_045",
        "category": "optimization_saddle",
        "input": {
            "function": "Neural network loss landscape",
            "architecture": "2-layer, 1000 hidden units",
            "symmetry": "permutation_of_hidden_units",
            "description": "NN loss has many equivalent saddles from symmetry"
        },
        "expected": {
            "equivalent_optima": "1000! from hidden unit permutations",
            "saddle_fraction": "overwhelmingly_high",
            "note": "Most critical points in NNs are saddles, not minima"
        },
        "difficulty": "pathological",
        "rationale": "Neural network loss functions have a combinatorial number of equivalent optima (from permuting hidden units) and even more saddle points. Research shows that in high dimensions, almost all critical points are saddle points. Finding true minima is essentially impossible."
    },

    # =========================================================================
    # CATEGORY 10: WEAKLY SINGULAR INTEGRAL EQUATIONS (NUM_046 - NUM_050)
    # =========================================================================

    {
        "test_id": "NUM_046",
        "category": "integral_equation_singular",
        "input": {
            "equation": "u(x) = f(x) + integral_0^x [u(t) / sqrt(x-t)] dt",
            "kernel": "K(x,t) = 1 / sqrt(x - t)",
            "singularity": "Abel kernel - weakly singular",
            "description": "Abel integral equation - arises in tautochrone problem"
        },
        "expected": {
            "kernel_singularity": "integrable (power -1/2)",
            "numerical_difficulty": "special_quadrature_needed",
            "note": "Standard trapezoid rule gives O(h^(1/2)) not O(h^2)"
        },
        "difficulty": "brutal",
        "rationale": "The Abel kernel 1/sqrt(x-t) is singular but integrable. However, standard quadrature rules assume smooth integrands and give poor accuracy. The Nystrom method requires product integration or graded meshes to achieve reasonable accuracy."
    },

    {
        "test_id": "NUM_047",
        "category": "integral_equation_singular",
        "input": {
            "equation": "integral_0^1 [log|x-t| * u(t)] dt = f(x)",
            "kernel": "K(x,t) = log|x - t|",
            "singularity": "logarithmic",
            "description": "Symm's integral equation - arises in potential theory"
        },
        "expected": {
            "kernel_singularity": "weakly_singular_logarithmic",
            "operator_type": "compact but not trace class",
            "note": "Logarithmic singularity requires special treatment"
        },
        "difficulty": "extreme",
        "rationale": "The logarithmic kernel log|x-t| arises in 2D potential theory. It's weakly singular (integrable) but causes slow convergence of Galerkin and collocation methods. The singular value decay is only O(n^(-1)) vs O(n^(-k)) for smooth kernels."
    },

    {
        "test_id": "NUM_048",
        "category": "integral_equation_singular",
        "input": {
            "equation": "integral_{-1}^{1} [u(t) / (x - t)] dt = f(x) (CPV)",
            "kernel": "K(x,t) = 1 / (x - t)",
            "singularity": "Cauchy principal value",
            "description": "Cauchy singular integral equation"
        },
        "expected": {
            "singularity_type": "non-integrable without CPV",
            "requires": "principal_value_interpretation",
            "numerical_method": "Gauss-Chebyshev or regularization",
            "note": "Standard quadrature fails completely"
        },
        "difficulty": "pathological",
        "rationale": "The kernel 1/(x-t) is not integrable - the integral doesn't exist in the ordinary sense. It only exists as a Cauchy principal value (CPV). Standard quadrature produces nonsense. Special methods exploit the Hilbert transform structure or use Chebyshev polynomials."
    },

    {
        "test_id": "NUM_049",
        "category": "integral_equation_singular",
        "input": {
            "equation": "integral_0^1 integral_0^1 [u(s,t) / ||(x,y)-(s,t)||] ds dt = f(x,y)",
            "kernel": "K = 1/r (Newtonian potential in 2D integration)",
            "domain": "[0,1] x [0,1]",
            "description": "2D integral equation with r^(-1) singularity"
        },
        "expected": {
            "singularity": "point singularity at (x,y)",
            "integrable": "yes (area element r*dr helps)",
            "numerical_difficulty": "requires singular element methods",
            "note": "Boundary element methods in elasticity/acoustics"
        },
        "difficulty": "extreme",
        "rationale": "In 2D, the kernel 1/||(x,y)-(s,t)|| has an integrable singularity (the Jacobian saves us). But numerical integration must handle the near-singularity carefully. Panel-based methods with analytical integration of the singular part are typically required."
    },

    {
        "test_id": "NUM_050",
        "category": "integral_equation_singular",
        "input": {
            "equation": "u(x) = f(x) + lambda * integral_{-1}^{1} [u(t) * sqrt(1-t^2) / (x-t)] dt",
            "kernel": "Chebyshev-weighted Cauchy kernel",
            "parameter": "lambda near eigenvalue",
            "description": "Fredholm equation at near-resonance"
        },
        "expected": {
            "eigenvalues_of_operator": "[pi, pi/2, pi/3, ...]",
            "resonance": "lambda = pi causes infinite blowup",
            "near_resonance": "lambda = pi - epsilon causes O(1/epsilon) solution norm",
            "note": "Near eigenvalue, solution amplifies dramatically"
        },
        "difficulty": "pathological",
        "rationale": "Fredholm integral equations of the second kind fail when lambda equals an eigenvalue of the integral operator. Near eigenvalues, the solution exists but has norm O(1/distance_to_eigenvalue). For lambda = pi - 1e-6, solution norm is O(1e6), completely swamping the data f."
    },
]


# =============================================================================
# HELPER FUNCTIONS FOR TEST GENERATION
# =============================================================================

def get_tests_by_category(category: str) -> List[Dict]:
    """Filter tests by category."""
    return [t for t in BRUTAL_NUMERICAL_TESTS if t["category"].startswith(category)]


def get_tests_by_difficulty(difficulty: str) -> List[Dict]:
    """Filter tests by difficulty level."""
    return [t for t in BRUTAL_NUMERICAL_TESTS if t["difficulty"] == difficulty]


def get_test_by_id(test_id: str) -> Optional[Dict]:
    """Get a specific test by ID."""
    for t in BRUTAL_NUMERICAL_TESTS:
        if t["test_id"] == test_id:
            return t
    return None


def get_category_summary() -> Dict[str, int]:
    """Get count of tests per category."""
    categories = {}
    for t in BRUTAL_NUMERICAL_TESTS:
        cat = t["category"].split("_")[0]
        categories[cat] = categories.get(cat, 0) + 1
    return categories


def get_difficulty_summary() -> Dict[str, int]:
    """Get count of tests per difficulty level."""
    difficulties = {}
    for t in BRUTAL_NUMERICAL_TESTS:
        diff = t["difficulty"]
        difficulties[diff] = difficulties.get(diff, 0) + 1
    return difficulties


# =============================================================================
# TEST RUNNER INTERFACE
# =============================================================================

def generate_test_report() -> str:
    """Generate a summary report of all tests."""
    report = []
    report.append("=" * 80)
    report.append("BRUTAL NUMERICAL STRESS TESTS - SUMMARY REPORT")
    report.append("=" * 80)
    report.append("")

    # Category breakdown
    report.append("TESTS BY CATEGORY:")
    report.append("-" * 40)
    cat_summary = get_category_summary()
    for cat, count in sorted(cat_summary.items()):
        report.append(f"  {cat}: {count} tests")
    report.append("")

    # Difficulty breakdown
    report.append("TESTS BY DIFFICULTY:")
    report.append("-" * 40)
    diff_summary = get_difficulty_summary()
    for diff, count in sorted(diff_summary.items()):
        report.append(f"  {diff}: {count} tests")
    report.append("")

    # Individual tests
    report.append("INDIVIDUAL TEST DETAILS:")
    report.append("-" * 40)
    for t in BRUTAL_NUMERICAL_TESTS:
        report.append(f"\n{t['test_id']} [{t['difficulty'].upper()}]")
        report.append(f"  Category: {t['category']}")
        report.append(f"  Input: {t['input'].get('description', 'N/A')}")
        report.append(f"  Rationale: {t['rationale'][:100]}...")

    return "\n".join(report)


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    'BRUTAL_NUMERICAL_TESTS',
    'get_tests_by_category',
    'get_tests_by_difficulty',
    'get_test_by_id',
    'get_category_summary',
    'get_difficulty_summary',
    'generate_test_report',
]


if __name__ == "__main__":
    # Print summary when run directly
    print(generate_test_report())
    print("\n" + "=" * 80)
    print(f"TOTAL: {len(BRUTAL_NUMERICAL_TESTS)} brutal stress tests")
    print("=" * 80)
