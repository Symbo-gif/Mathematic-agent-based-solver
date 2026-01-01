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
PHASE 2 - STEP 1.3: POLYNOMIAL MANIPULATION SPECIALIST (Tier 3)
===============================================================

Specializes in structural manipulation of polynomials and systems
of polynomial equations.

ARCHITECTURE: DOMAIN-FIRST, SYMPY-FALLBACK
------------------------------------------
This specialist implements the "SymPy Last Resort" pattern:
1. Try domain-specific algorithms FIRST (quadratic formula, rational roots, etc.)
2. Only fall back to SymPy when domain algorithms can't handle the case
3. Track all fallbacks for optimization analysis

DOMAIN ALGORITHMS (tried first):
-------------------------------
- Quadratic formula (degree 2)
- Rational root theorem (integer/rational roots)
- Difference of squares: a² - b² = (a-b)(a+b)
- Difference of cubes: a³ - b³ = (a-b)(a²+ab+b²)
- Sum of cubes: a³ + b³ = (a+b)(a²-ab+b²)
- Factor by grouping
- GCD factoring

SYMPY FALLBACK (when domain algorithms fail):
--------------------------------------------
- Gröbner bases for polynomial systems
- General polynomial solving
- Complex factorization patterns

REFERENCE:
---------
- Second Opinion Analysis: "Domain-first, library-second per specialist"
- Phase_2_Build_Order_Breakdown.md: Lines 74-90 (Agent 1.3)

DECOMPOSITION:
-------------
This module has been decomposed into focused sub-specialist modules
in the polynomial/ subdirectory:

1. polynomial_solvers.py (~400 lines) - Degree-specific solving
2. polynomial_factors.py (~200 lines) - Factoring methods
3. numeric_roots.py (~200 lines) - Numeric root finding
4. rational_equations.py (~350 lines) - Rational equation handling
5. domain_solver.py (~200 lines) - DomainPolynomialSolver routing class
6. polynomial_agent.py (~700 lines) - PolynomialSpecialist BDI agent
7. __init__.py - Package exports

This file now serves as a backward-compatible thin wrapper.
"""

# Re-export main classes from the polynomial package
from .polynomial import DomainPolynomialSolver, PolynomialSpecialist

# Maintain backward compatibility
__all__ = [
    'DomainPolynomialSolver',
    'PolynomialSpecialist',
]

# Main entry point for testing
if __name__ == "__main__":
    """Test Polynomial Specialist"""
    print("=" * 80)
    print("PHASE 2 - POLYNOMIAL SPECIALIST TEST")
    print("=" * 80)
    print()

    from symbo_agentic_reasoners.core.system import Phase0System
    from symbo_agentic_reasoners.core.native_symbolic import solve, sympify, Symbol

    # Initialize Phase 0
    print("Initializing Phase 0 infrastructure...")
    phase0 = Phase0System()
    phase0.start()
    print()

    # Initialize Polynomial Specialist
    specialist = PolynomialSpecialist(
        df=phase0.df,
        blackboard=phase0.blackboard
    )
    print()

    print("=" * 80)
    print("POLYNOMIAL SPECIALIST READY")
    print("=" * 80)
    print()

    # Test Gröbner bases
    print("Test: Solving polynomial equation using Gröbner bases")
    print("  Equation: x**2 - 4")
    result = solve(sympify("x**2 - 4"), Symbol('x'))
    print(f"  Solutions: {result}")
    print()

    # Check DF registration
    services = phase0.df.search(service_type='math.algebra.polynomial')
    print(f"Registered services: {len(services)}")
    for service in services:
        print(f"  - {service.service_type}: {service.agent_id}")
        print(f"    Algorithm: {service.algorithm}")

    print()
    print("Statistics:")
    import json
    print(json.dumps(specialist.get_statistics(), indent=2))

    # Shutdown
    phase0.shutdown()
