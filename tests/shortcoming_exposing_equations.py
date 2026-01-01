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
Shortcoming-Exposing Equations - 100 Problems Targeting Identified System Weaknesses
====================================================================================

These equations are specifically designed to expose the shortcomings identified
in system analysis. Each category targets a specific weak area with problems
that probe the boundaries of current solver capabilities.

Target Areas:
- ODE Solving (55/100 score) - 20 equations
- Physics Domain (44/100 score) - 15 equations
- Integration Techniques (75/100 score) - 20 equations
- Linear Algebra Robustness (66/100 score) - 15 equations
- Special Functions (missing) - 15 equations
- Series/Limits Edge Cases (68-72/100 score) - 15 equations

Total: 100 equations
"""

from typing import Dict, List, Tuple, Optional, Any


# =============================================================================
# CATEGORY 1: ODE SOLVING WEAKNESSES (20 equations)
# Target Score: 55/100 - Major gap in differential equation handling
# =============================================================================

ODE_SOLVING_WEAKNESSES: List[Dict[str, Any]] = [
    # Non-separable first-order ODEs (5 equations)
    {
        "equation": "dsolve(diff(y(x), x) + y(x)/x - x*y(x)**2, y(x))",
        "type": "bernoulli",
        "expected": "y(x) = 1/(x*(C + log(x)))",
        "difficulty": "medium",
        "notes": "Bernoulli equation with n=2, requires substitution v=y^(1-n)"
    },
    {
        "equation": "dsolve(diff(y(x), x) - y(x)**2 - x, y(x))",
        "type": "riccati",
        "expected": "Ai/Bi functions (Airy)",
        "difficulty": "hard",
        "notes": "Riccati equation - requires finding particular solution or Airy functions"
    },
    {
        "equation": "dsolve(diff(y(x), x) + 2*y(x) - y(x)**2*exp(x), y(x))",
        "type": "bernoulli",
        "expected": "y(x) = exp(2*x)/(C*exp(2*x) + exp(3*x)/3)",
        "difficulty": "medium",
        "notes": "Bernoulli with exponential coefficient"
    },
    {
        "equation": "dsolve(x*diff(y(x), x) + y(x) - x*y(x)**3, y(x))",
        "type": "bernoulli",
        "expected": "y(x) = 1/sqrt(x**2 + C/x**2)",
        "difficulty": "medium",
        "notes": "Bernoulli with n=3"
    },
    {
        "equation": "dsolve(diff(y(x), x) - y(x)*cot(x) + y(x)**2*csc(x), y(x))",
        "type": "riccati",
        "expected": "y(x) = sin(x)/(C - cos(x))",
        "difficulty": "hard",
        "notes": "Riccati with trigonometric coefficients"
    },

    # Variable coefficient second-order ODEs (5 equations)
    {
        "equation": "dsolve(x**2*diff(y(x), x, 2) + x*diff(y(x), x) - 4*y(x), y(x))",
        "type": "euler_cauchy",
        "expected": "y(x) = C1*x**2 + C2*x**(-2)",
        "difficulty": "medium",
        "notes": "Euler-Cauchy equation with distinct real roots"
    },
    {
        "equation": "dsolve(x**2*diff(y(x), x, 2) + 3*x*diff(y(x), x) + y(x), y(x))",
        "type": "euler_cauchy",
        "expected": "y(x) = (C1 + C2*log(x))/x",
        "difficulty": "medium",
        "notes": "Euler-Cauchy with repeated root"
    },
    {
        "equation": "dsolve((1+x**2)*diff(y(x), x, 2) + 2*x*diff(y(x), x) - 2*y(x), y(x))",
        "type": "variable_coefficient",
        "expected": "y(x) = C1*x + C2*(x*arctan(x) - 1)",
        "difficulty": "hard",
        "notes": "Variable coefficient requiring reduction of order"
    },
    {
        "equation": "dsolve(x*diff(y(x), x, 2) - diff(y(x), x) + 4*x**3*y(x), y(x))",
        "type": "variable_coefficient",
        "expected": "Bessel-related solution",
        "difficulty": "hard",
        "notes": "Transforms to Bessel equation"
    },
    {
        "equation": "dsolve(diff(y(x), x, 2) + (1/x)*diff(y(x), x) + (1 - n**2/x**2)*y(x), y(x))",
        "type": "bessel",
        "expected": "y(x) = C1*besselj(n, x) + C2*bessely(n, x)",
        "difficulty": "hard",
        "notes": "Bessel equation of order n"
    },

    # Systems of ODEs (5 equations)
    {
        "equation": "dsolve([diff(x(t), t) - 3*x(t) - 4*y(t), diff(y(t), t) + x(t) + y(t)], [x(t), y(t)])",
        "type": "system_linear",
        "expected": "eigenvalue solution with lambda = 1, -1",
        "difficulty": "medium",
        "notes": "2x2 linear system with distinct real eigenvalues"
    },
    {
        "equation": "dsolve([diff(x(t), t) - 2*x(t) + y(t), diff(y(t), t) - x(t) + 2*y(t)], [x(t), y(t)])",
        "type": "system_complex",
        "expected": "oscillatory solution with damping",
        "difficulty": "medium",
        "notes": "2x2 system with complex eigenvalues"
    },
    {
        "equation": "dsolve([diff(x(t), t) - x(t) - y(t), diff(y(t), t) - y(t) - z(t), diff(z(t), t) - z(t)], [x(t), y(t), z(t)])",
        "type": "system_cascaded",
        "expected": "exp(t) with polynomial multipliers",
        "difficulty": "hard",
        "notes": "3x3 system with repeated eigenvalue (Jordan block)"
    },
    {
        "equation": "dsolve([diff(x(t), t) - y(t), diff(y(t), t) + x(t) - sin(t)], [x(t), y(t)])",
        "type": "system_forced",
        "expected": "homogeneous + particular solution",
        "difficulty": "hard",
        "notes": "Forced harmonic oscillator system"
    },
    {
        "equation": "dsolve([diff(x(t), t) - x(t)*(1 - x(t) - y(t)), diff(y(t), t) - y(t)*(1 - x(t) - 2*y(t))], [x(t), y(t)])",
        "type": "system_nonlinear",
        "expected": "Lotka-Volterra type equilibria",
        "difficulty": "expert",
        "notes": "Nonlinear competitive system - no closed form"
    },

    # Exact equations with integrating factors (5 equations)
    {
        "equation": "dsolve((2*x*y + 3)*diff(y(x), x) + y**2 + 2*x, y(x))",
        "type": "exact",
        "expected": "x**2 + x*y**2 + 3*y = C",
        "difficulty": "medium",
        "notes": "Already exact equation"
    },
    {
        "equation": "dsolve((x**2 + y**2)*diff(y(x), x) + 2*x*y, y(x))",
        "type": "integrating_factor_xy",
        "expected": "requires integrating factor mu(xy)",
        "difficulty": "hard",
        "notes": "Not exact, needs integrating factor depending on xy"
    },
    {
        "equation": "dsolve(y*diff(y(x), x) + y**2/x - x, y(x))",
        "type": "integrating_factor_x",
        "expected": "y**2/x + x**2/2 = C after mu=1/x",
        "difficulty": "hard",
        "notes": "Integrating factor mu = 1/x"
    },
    {
        "equation": "dsolve((y*sin(x) + x*y*cos(x))*diff(y(x), x) + y**2*cos(x), y(x))",
        "type": "integrating_factor",
        "expected": "y**2*sin(x) + x*y**2/2 = C",
        "difficulty": "hard",
        "notes": "Requires finding appropriate integrating factor"
    },
    {
        "equation": "dsolve((exp(x) + y)*diff(y(x), x) + exp(x)*y + 1, y(x))",
        "type": "exact_exponential",
        "expected": "exp(x)*y + y**2/2 + x = C",
        "difficulty": "medium",
        "notes": "Exact equation with exponential"
    },
]

# =============================================================================
# CATEGORY 2: PHYSICS DOMAIN WEAKNESSES (15 equations)
# Target Score: 44/100 - Physics problems poorly handled
# =============================================================================

PHYSICS_DOMAIN_WEAKNESSES: List[Dict[str, Any]] = [
    # Multi-body dynamics problems (4 equations)
    {
        "equation": "m1*diff(x1(t), t, 2) + k1*(x1(t) - x2(t)) - F*cos(omega*t)",
        "type": "coupled_oscillators",
        "expected": "normal mode solution",
        "difficulty": "hard",
        "notes": "Two coupled masses with external forcing"
    },
    {
        "equation": "solve([m1*a1 - T + m1*g*sin(theta1), m2*a2 + T - m2*g*sin(theta2)], [T, a1, a2])",
        "type": "atwood_incline",
        "expected": "a = g*(m1*sin(theta1) - m2*sin(theta2))/(m1 + m2)",
        "difficulty": "medium",
        "notes": "Atwood machine on inclined planes"
    },
    {
        "equation": "dsolve([m*diff(r(t), t, 2) - m*r(t)*diff(theta(t), t)**2 + k/r(t)**2, m*r(t)*diff(theta(t), t, 2) + 2*m*diff(r(t), t)*diff(theta(t), t)], [r(t), theta(t)])",
        "type": "orbital_mechanics",
        "expected": "Kepler orbit r = a(1-e**2)/(1+e*cos(theta))",
        "difficulty": "expert",
        "notes": "Orbital mechanics in polar coordinates"
    },
    {
        "equation": "I*diff(theta(t), t, 2) + m*g*L*sin(theta(t)) + b*diff(theta(t), t)",
        "type": "damped_pendulum",
        "expected": "decaying oscillation or overdamped",
        "difficulty": "hard",
        "notes": "Physical pendulum with damping - nonlinear"
    },

    # Electromagnetic field calculations (4 equations)
    {
        "equation": "integrate(integrate(mu_0*I/(4*pi*sqrt(x**2 + y**2 + d**2)**3) * d, (x, -L/2, L/2)), (y, -W/2, W/2))",
        "type": "magnetic_field_loop",
        "expected": "B-field from rectangular current loop",
        "difficulty": "hard",
        "notes": "Biot-Savart for finite rectangular loop"
    },
    {
        "equation": "laplacian(V) - rho/epsilon_0",
        "type": "poisson_equation",
        "expected": "electrostatic potential",
        "difficulty": "hard",
        "notes": "Poisson equation for electrostatics"
    },
    {
        "equation": "curl(B) - mu_0*J - mu_0*epsilon_0*diff(E, t)",
        "type": "maxwell_ampere",
        "expected": "Maxwell-Ampere law",
        "difficulty": "expert",
        "notes": "Maxwell equation with displacement current"
    },
    {
        "equation": "integrate(E_0*sin(k*x - omega*t)**2, (x, 0, lambda))",
        "type": "em_wave_energy",
        "expected": "epsilon_0*E_0**2*lambda/2",
        "difficulty": "medium",
        "notes": "Time-averaged energy density of EM wave"
    },

    # Thermodynamic cycle problems (4 equations)
    {
        "equation": "integrate(P*dV, cycle) + integrate(V*dP, cycle)",
        "type": "carnot_cycle",
        "expected": "W = Q_h - Q_c",
        "difficulty": "hard",
        "notes": "Work done in Carnot cycle"
    },
    {
        "equation": "C_V*dT + P*dV - dQ",
        "type": "first_law_diff",
        "expected": "internal energy change",
        "difficulty": "medium",
        "notes": "First law in differential form"
    },
    {
        "equation": "integrate(n*R*T/V, (V, V1, V2)) + integrate(C_V, (T, T2, T3))",
        "type": "otto_cycle",
        "expected": "efficiency = 1 - (V1/V2)**(gamma-1)",
        "difficulty": "hard",
        "notes": "Otto cycle efficiency calculation"
    },
    {
        "equation": "dS - dQ/T - sigma_irr",
        "type": "entropy_production",
        "expected": "Clausius inequality dS >= dQ/T",
        "difficulty": "medium",
        "notes": "Entropy production in irreversible process"
    },

    # Quantum harmonic oscillator (3 equations)
    {
        "equation": "dsolve(-hbar**2/(2*m)*diff(psi(x), x, 2) + m*omega**2*x**2/2*psi(x) - E*psi(x), psi(x))",
        "type": "quantum_ho",
        "expected": "psi_n(x) = H_n(alpha*x)*exp(-alpha**2*x**2/2)",
        "difficulty": "hard",
        "notes": "Quantum harmonic oscillator - Hermite polynomials"
    },
    {
        "equation": "integrate(psi_n(x) * x * psi_m(x), (x, -oo, oo))",
        "type": "qho_matrix_element",
        "expected": "sqrt(hbar/(2*m*omega)) * (sqrt(n)*delta(m,n-1) + sqrt(n+1)*delta(m,n+1))",
        "difficulty": "hard",
        "notes": "Position matrix element for QHO"
    },
    {
        "equation": "Sum(E_n * exp(-E_n/(k*T)), (n, 0, oo)) / Sum(exp(-E_n/(k*T)), (n, 0, oo))",
        "type": "qho_partition",
        "expected": "hbar*omega/(2*tanh(hbar*omega/(2*k*T)))",
        "difficulty": "hard",
        "notes": "Thermal average energy of QHO"
    },
]

# =============================================================================
# CATEGORY 3: INTEGRATION TECHNIQUES WEAKNESSES (20 equations)
# Target Score: 75/100 - Advanced integration techniques needed
# =============================================================================

INTEGRATION_WEAKNESSES: List[Dict[str, Any]] = [
    # Trigonometric substitution required (5 equations)
    {
        "equation": "integrate(x**3 / sqrt(a**2 - x**2), x)",
        "type": "trig_sub_sin",
        "expected": "-sqrt(a**2 - x**2)*(x**2/3 + 2*a**2/3)",
        "difficulty": "medium",
        "notes": "Requires x = a*sin(theta) substitution"
    },
    {
        "equation": "integrate(1 / (x**2 * sqrt(x**2 - a**2)), x)",
        "type": "trig_sub_sec",
        "expected": "-sqrt(x**2 - a**2) / (a**2 * x)",
        "difficulty": "medium",
        "notes": "Requires x = a*sec(theta) substitution"
    },
    {
        "equation": "integrate(sqrt(x**2 + a**2) / x**2, x)",
        "type": "trig_sub_tan",
        "expected": "-sqrt(x**2 + a**2)/x + asinh(x/a)",
        "difficulty": "medium",
        "notes": "Requires x = a*tan(theta) substitution"
    },
    {
        "equation": "integrate(x**2 / (a**2 - x**2)**(5/2), x)",
        "type": "trig_sub_sin",
        "expected": "x / (3*(a**2 - x**2)**(3/2)) - x / (3*a**2*sqrt(a**2 - x**2))",
        "difficulty": "hard",
        "notes": "Higher power trig substitution"
    },
    {
        "equation": "integrate(1 / (x * sqrt(a**2 + x**2)), x)",
        "type": "trig_sub_tan",
        "expected": "-(1/a) * log((a + sqrt(a**2 + x**2)) / x)",
        "difficulty": "medium",
        "notes": "Log result from trig sub"
    },

    # Weierstrass substitution (tan-half-angle) (4 equations)
    {
        "equation": "integrate(1 / (2 + sin(x)), x)",
        "type": "weierstrass",
        "expected": "2*arctan((1 + tan(x/2))/sqrt(3)) / sqrt(3)",
        "difficulty": "medium",
        "notes": "Classic Weierstrass t = tan(x/2)"
    },
    {
        "equation": "integrate(1 / (a + b*cos(x)), (x, 0, pi))",
        "type": "weierstrass_definite",
        "expected": "pi / sqrt(a**2 - b**2) for a > b > 0",
        "difficulty": "hard",
        "notes": "Definite integral with Weierstrass"
    },
    {
        "equation": "integrate(1 / (3 + 2*cos(x) + sin(x)), x)",
        "type": "weierstrass_mixed",
        "expected": "arctan((1 + tan(x/2))/2) / 2",
        "difficulty": "hard",
        "notes": "Mixed trig requires Weierstrass"
    },
    {
        "equation": "integrate(sin(x) / (1 + sin(x) + cos(x)), x)",
        "type": "weierstrass_complex",
        "expected": "x/2 - log(1 + tan(x/2))",
        "difficulty": "hard",
        "notes": "Complex Weierstrass case"
    },

    # Partial fractions with repeated roots (4 equations)
    {
        "equation": "integrate(x**2 / ((x-1)**3 * (x+2)), x)",
        "type": "partial_fraction_repeated",
        "expected": "sum of logs and inverse powers",
        "difficulty": "hard",
        "notes": "Repeated linear factor cubed"
    },
    {
        "equation": "integrate(1 / ((x**2 + 1)**2 * (x - 1)), x)",
        "type": "partial_fraction_irreducible",
        "expected": "arctan and log terms",
        "difficulty": "hard",
        "notes": "Repeated irreducible quadratic"
    },
    {
        "equation": "integrate((x**3 + 2*x) / ((x**2 + 1)**3), x)",
        "type": "partial_fraction_high_power",
        "expected": "-1/(4*(x**2+1)**2) + 1/(2*(x**2+1))",
        "difficulty": "hard",
        "notes": "High power irreducible quadratic"
    },
    {
        "equation": "integrate(x**4 / ((x-1)**2 * (x+1)**2), x)",
        "type": "partial_fraction_symmetric",
        "expected": "x + 2*log|x-1| - 2*log|x+1| + terms",
        "difficulty": "hard",
        "notes": "Symmetric repeated roots"
    },

    # Integration requiring completing the square (3 equations)
    {
        "equation": "integrate(1 / sqrt(x**2 + 4*x + 8), x)",
        "type": "complete_square",
        "expected": "asinh((x+2)/2)",
        "difficulty": "medium",
        "notes": "Complete square: (x+2)^2 + 4"
    },
    {
        "equation": "integrate(x / sqrt(2*x - x**2), x)",
        "type": "complete_square_trig",
        "expected": "-sqrt(2*x - x**2) + arcsin(x - 1)",
        "difficulty": "medium",
        "notes": "Complete square then trig sub"
    },
    {
        "equation": "integrate(1 / (x**2 + 6*x + 13), x)",
        "type": "complete_square_arctan",
        "expected": "arctan((x+3)/2) / 2",
        "difficulty": "easy",
        "notes": "Complete square gives arctan"
    },

    # Improper integrals with parameter dependence (4 equations)
    {
        "equation": "integrate(exp(-a*x) * cos(b*x), (x, 0, oo))",
        "type": "improper_parametric",
        "expected": "a / (a**2 + b**2) for a > 0",
        "difficulty": "medium",
        "notes": "Laplace transform of cosine"
    },
    {
        "equation": "integrate(x**(s-1) * exp(-x), (x, 0, oo))",
        "type": "gamma_function",
        "expected": "Gamma(s) for Re(s) > 0",
        "difficulty": "medium",
        "notes": "Gamma function definition"
    },
    {
        "equation": "integrate(exp(-a*x**2) * x**(2*n), (x, 0, oo))",
        "type": "gaussian_moments",
        "expected": "Gamma(n + 1/2) / (2 * a**(n+1/2))",
        "difficulty": "hard",
        "notes": "Even moments of Gaussian"
    },
    {
        "equation": "integrate(log(x) / (x**2 + a**2), (x, 0, oo))",
        "type": "improper_log",
        "expected": "pi * log(a) / (2*a) for a > 0",
        "difficulty": "hard",
        "notes": "Log integral with parameter"
    },
]

# =============================================================================
# CATEGORY 4: LINEAR ALGEBRA ROBUSTNESS (15 equations)
# Target Score: 66/100 - Numerical stability and edge cases
# =============================================================================

LINEAR_ALGEBRA_WEAKNESSES: List[Dict[str, Any]] = [
    # Near-singular matrices (condition number > 10^6) (4 equations)
    {
        "equation": "solve(Matrix([[1, 1], [1, 1 + 1e-10]]) * Matrix([[x], [y]]) - Matrix([[2], [2]]), [x, y])",
        "type": "near_singular",
        "expected": "ill-conditioned, x + y = 2",
        "difficulty": "hard",
        "notes": "Condition number ~ 10^10, nearly singular"
    },
    {
        "equation": "det(Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9 + 1e-12]]))",
        "type": "near_singular_det",
        "expected": "~1e-12 (nearly zero)",
        "difficulty": "hard",
        "notes": "Nearly singular 3x3 matrix"
    },
    {
        "equation": "Matrix([[1, 1-1e-8], [1+1e-8, 1]]).inv()",
        "type": "hilbert_like",
        "expected": "large entries due to ill-conditioning",
        "difficulty": "hard",
        "notes": "Hilbert-like ill-conditioning"
    },
    {
        "equation": "eigenvals(Matrix([[1e10, 1], [1, 1e-10]]))",
        "type": "extreme_eigenvalues",
        "expected": "[1e10, 1e-10] approximately",
        "difficulty": "hard",
        "notes": "Extreme eigenvalue ratio"
    },

    # Sparse system solving (4 equations)
    {
        "equation": "solve(Matrix([[1, 0, 0, 2], [0, 3, 0, 0], [0, 0, 4, 0], [5, 0, 0, 6]]) * Matrix([[a], [b], [c], [d]]) - Matrix([[1], [2], [3], [4]]), [a, b, c, d])",
        "type": "sparse_4x4",
        "expected": "direct solution using sparsity",
        "difficulty": "medium",
        "notes": "Sparse 4x4 system"
    },
    {
        "equation": "tridiagonal_solve([[2, -1, 0, 0], [-1, 2, -1, 0], [0, -1, 2, -1], [0, 0, -1, 2]], [1, 0, 0, 1])",
        "type": "tridiagonal",
        "expected": "[1, 1, 1, 1]",
        "difficulty": "medium",
        "notes": "Tridiagonal system - efficient algorithm"
    },
    {
        "equation": "det(band_matrix(n, [1, -2, 1]))",
        "type": "tridiagonal_det",
        "expected": "n+1 (Chebyshev-related)",
        "difficulty": "hard",
        "notes": "Determinant of tridiagonal matrix"
    },
    {
        "equation": "sparse_eigenvalues(laplacian_matrix(100), k=5)",
        "type": "sparse_eigenvalue",
        "expected": "smallest 5 Laplacian eigenvalues",
        "difficulty": "hard",
        "notes": "Large sparse eigenvalue problem"
    },

    # Eigenvalue problems with repeated eigenvalues (4 equations)
    {
        "equation": "Matrix([[2, 1, 0], [0, 2, 0], [0, 0, 3]]).jordan_form()",
        "type": "jordan_2x2_block",
        "expected": "2x2 Jordan block for eigenvalue 2",
        "difficulty": "medium",
        "notes": "Simple Jordan block case"
    },
    {
        "equation": "Matrix([[0, 1, 0], [0, 0, 1], [0, 0, 0]]).jordan_form()",
        "type": "jordan_nilpotent",
        "expected": "Single 3x3 Jordan block for eigenvalue 0",
        "difficulty": "medium",
        "notes": "Nilpotent matrix Jordan form"
    },
    {
        "equation": "Matrix([[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 0], [0, 0, 0, 2]]).jordan_form()",
        "type": "jordan_mixed",
        "expected": "3x3 block for 1, 1x1 for 2",
        "difficulty": "hard",
        "notes": "Mixed Jordan blocks"
    },
    {
        "equation": "generalized_eigenvectors(Matrix([[5, 4, 2, 1], [0, 1, -1, -1], [-1, -1, 3, 0], [1, 1, -1, 2]]))",
        "type": "generalized_eigenvec",
        "expected": "complete basis including generalized",
        "difficulty": "hard",
        "notes": "Matrix with repeated eigenvalues"
    },

    # Jordan normal form cases (3 equations)
    {
        "equation": "Matrix([[a, 1, 0], [0, a, 1], [0, 0, a]]).exp()",
        "type": "matrix_exp_jordan",
        "expected": "exp(a) * [[1, t, t^2/2], [0, 1, t], [0, 0, 1]]",
        "difficulty": "hard",
        "notes": "Matrix exponential via Jordan form"
    },
    {
        "equation": "Matrix([[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 0, -1], [0, 0, 1, 0]]).log()",
        "type": "matrix_log_rotation",
        "expected": "block diagonal with [[0, -pi/2], [pi/2, 0]] blocks",
        "difficulty": "expert",
        "notes": "Matrix logarithm of rotation"
    },
    {
        "equation": "Matrix([[4, 1, 0], [0, 4, 0], [0, 0, 4]]).sqrt()",
        "type": "matrix_sqrt_defective",
        "expected": "sqrt(4)*I + nilpotent/4 term",
        "difficulty": "expert",
        "notes": "Matrix square root with defective eigenvalue"
    },
]

# =============================================================================
# CATEGORY 5: SPECIAL FUNCTIONS (15 equations)
# Target Score: Missing - No special function support
# =============================================================================

SPECIAL_FUNCTIONS_WEAKNESSES: List[Dict[str, Any]] = [
    # Bessel function identities (4 equations)
    {
        "equation": "besselj(n+1, x) + besselj(n-1, x) - 2*n/x * besselj(n, x)",
        "type": "bessel_recurrence",
        "expected": "= 0 (recurrence relation)",
        "difficulty": "medium",
        "notes": "Bessel function recurrence relation"
    },
    {
        "equation": "diff(besselj(n, x), x) - (besselj(n-1, x) - besselj(n+1, x))/2",
        "type": "bessel_derivative",
        "expected": "= 0 (derivative identity)",
        "difficulty": "medium",
        "notes": "Bessel derivative formula"
    },
    {
        "equation": "integrate(besselj(0, x), (x, 0, oo))",
        "type": "bessel_integral",
        "expected": "1",
        "difficulty": "hard",
        "notes": "Integral of J_0 from 0 to infinity"
    },
    {
        "equation": "limit(besselj(n, x) * sqrt(2/(pi*x)) * cos(x - n*pi/2 - pi/4), x, oo)",
        "type": "bessel_asymptotic",
        "expected": "1 (asymptotic form)",
        "difficulty": "hard",
        "notes": "Bessel asymptotic expansion check"
    },

    # Legendre polynomial equations (4 equations)
    {
        "equation": "(1 - x**2)*diff(legendre(n, x), x, 2) - 2*x*diff(legendre(n, x), x) + n*(n+1)*legendre(n, x)",
        "type": "legendre_ode",
        "expected": "= 0 (Legendre equation)",
        "difficulty": "medium",
        "notes": "Legendre polynomials satisfy Legendre equation"
    },
    {
        "equation": "integrate(legendre(m, x) * legendre(n, x), (x, -1, 1))",
        "type": "legendre_orthogonality",
        "expected": "2/(2*n+1) * delta(m,n)",
        "difficulty": "medium",
        "notes": "Legendre orthogonality"
    },
    {
        "equation": "(n+1)*legendre(n+1, x) - (2*n+1)*x*legendre(n, x) + n*legendre(n-1, x)",
        "type": "legendre_recurrence",
        "expected": "= 0 (three-term recurrence)",
        "difficulty": "medium",
        "notes": "Legendre recurrence relation"
    },
    {
        "equation": "Sum(legendre(n, x) * t**n, (n, 0, oo)) - 1/sqrt(1 - 2*x*t + t**2)",
        "type": "legendre_generating",
        "expected": "= 0 (generating function)",
        "difficulty": "hard",
        "notes": "Legendre generating function"
    },

    # Hypergeometric function evaluations (4 equations)
    {
        "equation": "hyper([a, b], [c], 1)",
        "type": "gauss_sum",
        "expected": "Gamma(c)*Gamma(c-a-b)/(Gamma(c-a)*Gamma(c-b)) for Re(c-a-b)>0",
        "difficulty": "hard",
        "notes": "Gauss hypergeometric at z=1"
    },
    {
        "equation": "hyper([-n, a], [b], 1)",
        "type": "vandermonde",
        "expected": "(b-a)_n / (b)_n (Vandermonde identity)",
        "difficulty": "medium",
        "notes": "Chu-Vandermonde identity"
    },
    {
        "equation": "hyper([1/2, 1/2], [1], x) - 2*elliptic_k(sqrt(x))/pi",
        "type": "hyper_elliptic",
        "expected": "= 0 (elliptic K relation)",
        "difficulty": "hard",
        "notes": "2F1 and complete elliptic integral K"
    },
    {
        "equation": "hyper([a], [b], x) - Sum(pochhammer(a, n)/pochhammer(b, n) * x**n/factorial(n), (n, 0, oo))",
        "type": "confluent_series",
        "expected": "= 0 (series definition)",
        "difficulty": "medium",
        "notes": "Confluent hypergeometric 1F1 series"
    },

    # Error function integrals (3 equations)
    {
        "equation": "integrate(exp(-t**2), (t, 0, x)) - sqrt(pi)/2 * erf(x)",
        "type": "erf_definition",
        "expected": "= 0 (erf definition)",
        "difficulty": "easy",
        "notes": "Error function definition check"
    },
    {
        "equation": "integrate(erf(x), x)",
        "type": "erf_integral",
        "expected": "x*erf(x) + exp(-x**2)/sqrt(pi)",
        "difficulty": "medium",
        "notes": "Integral of error function"
    },
    {
        "equation": "integrate(exp(-a*x**2) * erf(b*x), (x, 0, oo))",
        "type": "erf_gaussian",
        "expected": "arctan(b/sqrt(a)) / (sqrt(a*pi))",
        "difficulty": "hard",
        "notes": "Gaussian weighted erf integral"
    },
]

# =============================================================================
# CATEGORY 6: SERIES/LIMITS EDGE CASES (15 equations)
# Target Score: 68-72/100 - Edge cases in series and limits
# =============================================================================

SERIES_LIMITS_WEAKNESSES: List[Dict[str, Any]] = [
    # Fourier series convergence (4 equations)
    {
        "equation": "Sum(sin(n*x)/n, (n, 1, oo))",
        "type": "fourier_sawtooth",
        "expected": "(pi - x)/2 for 0 < x < 2*pi",
        "difficulty": "medium",
        "notes": "Fourier series of sawtooth - Gibbs phenomenon at discontinuities"
    },
    {
        "equation": "Sum(cos(n*x)/n**2, (n, 1, oo))",
        "type": "fourier_parabola",
        "expected": "x**2/4 - pi*x/2 + pi**2/6 for 0 <= x <= 2*pi",
        "difficulty": "medium",
        "notes": "Fourier series of parabola"
    },
    {
        "equation": "Sum((-1)**(n+1) * sin(n*x)/n, (n, 1, oo))",
        "type": "fourier_triangle",
        "expected": "x/2 for -pi < x < pi",
        "difficulty": "medium",
        "notes": "Alternating Fourier series"
    },
    {
        "equation": "limit(Sum(sin((2*n-1)*x)/(2*n-1), (n, 1, N)), N, oo)",
        "type": "fourier_square",
        "expected": "pi/4 * sign(sin(x)) (square wave)",
        "difficulty": "hard",
        "notes": "Fourier series of square wave - Gibbs"
    },

    # Double limits (iterated vs simultaneous) (4 equations)
    {
        "equation": "limit(limit(x*y / (x**2 + y**2), y, 0), x, 0)",
        "type": "double_limit_path",
        "expected": "0 (iterated), but limit DNE along y=x",
        "difficulty": "hard",
        "notes": "Path-dependent limit - different along y=x"
    },
    {
        "equation": "limit(limit((x**2*y) / (x**4 + y**2), y, 0), x, 0) vs limit along y=x**2",
        "type": "double_limit_nonexist",
        "expected": "0 vs 1/2 - limit does not exist",
        "difficulty": "hard",
        "notes": "Classic counterexample for multivariate limits"
    },
    {
        "equation": "limit(limit(sin(x*y) / (x*y), y, 0), x, 0)",
        "type": "double_limit_removable",
        "expected": "1 (both ways, limit exists)",
        "difficulty": "medium",
        "notes": "Removable discontinuity at origin"
    },
    {
        "equation": "limit((x*y**2) / (x**2 + y**4), (x, y), (0, 0))",
        "type": "simultaneous_limit",
        "expected": "DNE (0 along axes, 1/2 along x=y**2)",
        "difficulty": "hard",
        "notes": "Simultaneous limit with path dependence"
    },

    # Series with conditional convergence (4 equations)
    {
        "equation": "Sum((-1)**(n+1)/n, (n, 1, oo))",
        "type": "conditional_log2",
        "expected": "log(2) (conditional, not absolute)",
        "difficulty": "medium",
        "notes": "Alternating harmonic - conditionally convergent"
    },
    {
        "equation": "Sum(sin(n)/n, (n, 1, oo))",
        "type": "conditional_dirichlet",
        "expected": "(pi - 1)/2 (Dirichlet test)",
        "difficulty": "hard",
        "notes": "Conditionally convergent by Dirichlet test"
    },
    {
        "equation": "Sum((-1)**n * log(n)/n, (n, 2, oo))",
        "type": "conditional_log",
        "expected": "gamma*log(2) - log(2)**2/2",
        "difficulty": "hard",
        "notes": "Alternating series with log - conditionally convergent"
    },
    {
        "equation": "rearrangement(Sum((-1)**(n+1)/n, (n, 1, oo)), pattern=[1, 3, 2, 5, 7, 4, ...])",
        "type": "riemann_rearrangement",
        "expected": "can sum to any value (Riemann rearrangement theorem)",
        "difficulty": "expert",
        "notes": "Demonstrates Riemann rearrangement theorem"
    },

    # Asymptotic expansions (3 equations)
    {
        "equation": "asymptotic(gamma(x), x, oo)",
        "type": "stirling_full",
        "expected": "sqrt(2*pi/x) * (x/e)**x * (1 + 1/(12*x) + ...)",
        "difficulty": "hard",
        "notes": "Full Stirling expansion"
    },
    {
        "equation": "asymptotic(erfc(x), x, oo)",
        "type": "erfc_asymptotic",
        "expected": "exp(-x**2)/(sqrt(pi)*x) * (1 - 1/(2*x**2) + ...)",
        "difficulty": "hard",
        "notes": "Complementary error function asymptotics"
    },
    {
        "equation": "asymptotic(Ei(x), x, oo)",
        "type": "ei_asymptotic",
        "expected": "exp(x)/x * (1 + 1/x + 2/x**2 + ...)",
        "difficulty": "hard",
        "notes": "Exponential integral asymptotics - divergent series"
    },
]


# =============================================================================
# COMBINE ALL SHORTCOMING-EXPOSING EQUATIONS
# =============================================================================

ALL_SHORTCOMING_EQUATIONS = (
    ODE_SOLVING_WEAKNESSES +           # 20
    PHYSICS_DOMAIN_WEAKNESSES +        # 15
    INTEGRATION_WEAKNESSES +           # 20
    LINEAR_ALGEBRA_WEAKNESSES +        # 15
    SPECIAL_FUNCTIONS_WEAKNESSES +     # 15
    SERIES_LIMITS_WEAKNESSES           # 15
)  # Total: 100 equations

# Category mapping with metadata
CATEGORIES = {
    "ode_solving": {
        "equations": ODE_SOLVING_WEAKNESSES,
        "target_score": 55,
        "description": "ODE solving weaknesses - non-separable, variable coefficient, systems",
        "count": len(ODE_SOLVING_WEAKNESSES),
    },
    "physics_domain": {
        "equations": PHYSICS_DOMAIN_WEAKNESSES,
        "target_score": 44,
        "description": "Physics domain problems - multi-body, EM, thermodynamics, QM",
        "count": len(PHYSICS_DOMAIN_WEAKNESSES),
    },
    "integration": {
        "equations": INTEGRATION_WEAKNESSES,
        "target_score": 75,
        "description": "Integration technique weaknesses - trig sub, Weierstrass, partial fractions",
        "count": len(INTEGRATION_WEAKNESSES),
    },
    "linear_algebra": {
        "equations": LINEAR_ALGEBRA_WEAKNESSES,
        "target_score": 66,
        "description": "Linear algebra robustness - ill-conditioning, sparse, Jordan form",
        "count": len(LINEAR_ALGEBRA_WEAKNESSES),
    },
    "special_functions": {
        "equations": SPECIAL_FUNCTIONS_WEAKNESSES,
        "target_score": 0,
        "description": "Special functions - Bessel, Legendre, hypergeometric, erf",
        "count": len(SPECIAL_FUNCTIONS_WEAKNESSES),
    },
    "series_limits": {
        "equations": SERIES_LIMITS_WEAKNESSES,
        "target_score": 70,
        "description": "Series/limits edge cases - Fourier, double limits, conditional convergence",
        "count": len(SERIES_LIMITS_WEAKNESSES),
    },
}

# Difficulty distribution
DIFFICULTY_DISTRIBUTION = {
    "easy": [],
    "medium": [],
    "hard": [],
    "expert": [],
}

for eq in ALL_SHORTCOMING_EQUATIONS:
    diff = eq.get("difficulty", "medium")
    DIFFICULTY_DISTRIBUTION[diff].append(eq)


def get_equations_by_category(category: str) -> List[Dict[str, Any]]:
    """Get equations for a specific category."""
    cat_data = CATEGORIES.get(category, {})
    return cat_data.get("equations", [])


def get_equations_by_difficulty(difficulty: str) -> List[Dict[str, Any]]:
    """Get equations filtered by difficulty level."""
    return DIFFICULTY_DISTRIBUTION.get(difficulty, [])


def get_all_equations() -> List[Dict[str, Any]]:
    """Get all shortcoming-exposing equations."""
    return ALL_SHORTCOMING_EQUATIONS


def get_equation_strings() -> List[str]:
    """Get just the equation strings for batch processing."""
    return [eq["equation"] for eq in ALL_SHORTCOMING_EQUATIONS]


def get_category_summary() -> Dict[str, Dict[str, Any]]:
    """Get summary statistics for each category."""
    return {
        name: {
            "count": data["count"],
            "target_score": data["target_score"],
            "description": data["description"],
        }
        for name, data in CATEGORIES.items()
    }


def analyze_difficulty_distribution() -> Dict[str, int]:
    """Analyze the distribution of difficulties across all equations."""
    return {diff: len(eqs) for diff, eqs in DIFFICULTY_DISTRIBUTION.items()}


def get_equations_with_expected_results() -> List[Dict[str, Any]]:
    """Get equations that have known expected results."""
    return [eq for eq in ALL_SHORTCOMING_EQUATIONS if eq.get("expected")]


if __name__ == "__main__":
    print("=" * 70)
    print("Shortcoming-Exposing Equations Analysis")
    print("=" * 70)
    print(f"\nTotal equations: {len(ALL_SHORTCOMING_EQUATIONS)}")

    print("\nCategory Breakdown:")
    print("-" * 50)
    for name, data in CATEGORIES.items():
        print(f"  {name:20s}: {data['count']:3d} equations (target: {data['target_score']}/100)")

    print("\nDifficulty Distribution:")
    print("-" * 50)
    for diff, count in analyze_difficulty_distribution().items():
        print(f"  {diff:10s}: {count:3d} equations")

    print("\nEquations with known expected results:", len(get_equations_with_expected_results()))
    print("=" * 70)
