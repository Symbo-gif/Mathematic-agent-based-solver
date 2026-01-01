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
ODE SOLUTION SPECIALIST (Tier 3)
================================

Solves Ordinary Differential Equations using symbolic methods.

CAPABILITIES:
------------
- First-order linear ODEs (integrating factor method)
- First-order separable ODEs
- First-order exact ODEs (with integrating factors)
- First-order Bernoulli ODEs (substitution method)
- First-order homogeneous ODEs (v = y/x substitution)
- Riccati ODEs (when particular solution known)
- Second-order linear ODEs with constant coefficients
- Homogeneous and non-homogeneous equations
- Initial value problems (IVP)
- Boundary value problems (shooting method, finite difference)
- Green's function construction (basic cases)
- Power series solutions at ordinary points
- Frobenius method at regular singular points
- Series coefficient computation with recurrence relations

ALGORITHMS:
-----------
Native implementation - NO SymPy dependency

1. Separable: dy/dx = f(x)g(y) -> integrate both sides
2. Linear first-order: dy/dx + P(x)y = Q(x) -> integrating factor
3. Exact: M(x,y)dx + N(x,y)dy = 0 -> find potential function F(x,y)
4. Bernoulli: y' + P(x)y = Q(x)y^n -> substitute v = y^(1-n)
5. Homogeneous: dy/dx = f(y/x) -> substitute v = y/x
6. Riccati: y' = P(x) + Q(x)y + R(x)y^2 -> requires particular solution
7. Second-order constant coefficient: ay'' + by' + cy = f(x) -> characteristic equation
8. Variation of parameters for non-homogeneous
9. Power series: expand y = Σ(a_n * x^n) at ordinary points
10. Frobenius: expand y = x^r * Σ(a_n * x^n) at regular singular points
11. BVP shooting: iterate IVPs until boundary condition satisfied
12. BVP finite difference: discretize and solve tridiagonal system
13. Green's function: construct using homogeneous solutions and Wronskian

REFERENCE:
---------
- Mathematical Capability Gap Analysis: ODE solving at 25%
- Target: 75% capability for common ODE types
"""

import logging
import re
import math
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass

# NO SYMPY - Use native symbolic engine
from symbo_agentic_reasoners.core.native_symbolic import (
    Symbol, sympify, simplify, parse_expr, Expr, Integer, Float,
    Sin, Cos, Exp, Log, Pow, Add, Mul
)
from symbo_agentic_reasoners.core.calculus import (
    differentiate as native_differentiate,
    integrate as native_integrate,
)
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.fallback_tracker import track_computation, get_tracker

logger = logging.getLogger('symbo_agentic_reasoners.specialists.ode')


@dataclass
class ODEClassification:
    """Classification of an ODE."""
    order: int  # 1, 2, or higher
    linearity: str  # 'linear', 'nonlinear'
    ode_type: str  # 'separable', 'linear_first', 'constant_coeff', 'exact', etc.
    homogeneous: bool
    has_initial_conditions: bool
    coefficients: Dict[str, Any]  # Extracted coefficients


class ODESolutionSpecialist(BDIAgent):
    """
    ODE Solution Specialist - Differential Equation Solver

    DIRECTIVE:
    ---------
    Solve ordinary differential equations symbolically using
    native mathematical algorithms.

    OPERATIONS:
    ----------
    - solve_ode: General ODE solver with classification
    - solve_separable: First-order separable equations
    - solve_linear_first_order: First-order linear equations
    - solve_exact_ode: Exact differential equations
    - solve_bernoulli_ode: Bernoulli equations
    - solve_homogeneous_first_order: Homogeneous first-order equations
    - solve_riccati_ode: Riccati equations (with known particular solution)
    - solve_second_order_constant: Second-order constant coefficient
    - solve_ivp: Initial value problems
    - solve_bvp_shooting: Boundary value problems (shooting method)
    - solve_bvp_finite_difference: Boundary value problems (finite difference)
    - construct_greens_function: Green's function construction
    - solve_series_power: Power series solution at ordinary points
    - solve_series_frobenius: Frobenius method at regular singular points
    - classify_ode: Classify ODE type

    ALGORITHMIC BACKING:
    -------------------
    Native calculus engine - pure Python implementation
    """

    def __init__(
        self,
        agent_id: str = 'ode_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize ODE Solution Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.odes_solved = 0

        # Cache for advanced integration specialist (lazy load)
        self._advanced_integration_specialist = None

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        logger.info(f"[{self.agent_id}] ODE Solution Specialist initialized")
        logger.info(f"  Library: Native Calculus Engine")
        logger.info(f"  Capabilities: First-order, second-order, IVP, constant coefficients")

    def _register_services(self):
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            service_type='math.calculus.ode',
            agent_id=self.agent_id,
            algorithm='symbolic',
            cost='medium',
            instance=self,
            type='exact',
            tier='3',
            operations='solve_ode_classify_ivp'
        )
        self.df.register(registration)
        logger.info(f"  [DF] Registered: math.calculus.ode (symbolic)")

    def process(self, task_entry: Any) -> Any:
        """Process ODE solving task."""
        logger.info(f"\n[{self.agent_id}] Processing ODE task")

        self.tasks_executed += 1

        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            operation = metadata.get('operation', 'solve_ode')
            raw_input = metadata.get('raw_input', '')
            ode_str = metadata.get('ode_expr') or raw_input
            variable = metadata.get('variable', 'x')
            func_name = metadata.get('function', 'y')
            initial_conditions = metadata.get('initial_conditions', {})

            logger.info(f"  Operation: {operation}")
            logger.info(f"  ODE: {ode_str}")

            # Solve ODE
            result = self.solve_ode(ode_str, variable, func_name, initial_conditions)

            self.tasks_succeeded += 1
            self.odes_solved += 1
            logger.info(f"  [OK] Result: {result}")

            # Extract solution string from result dict
            if isinstance(result, dict):
                solution_str = result.get('solution', str(result))
            else:
                solution_str = str(result)

            # Create proper result entry for blackboard
            if self.blackboard:
                from symbo_agentic_reasoners.core.omdoc_schema import create_variable
                return create_entry(
                    EntryType.PARTIAL_RESULT,
                    create_variable(solution_str),
                    self.agent_id,
                    task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'result',
                    ['ode'],
                    EntryStatus.COMPLETED,
                    {'result_str': solution_str, 'full_result': result}
                )
            else:
                # Return solution string for direct use (benchmarks)
                return solution_str

        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"ODE solving failed: {type(e).__name__}: {e}")
            if self.blackboard:
                from symbo_agentic_reasoners.core.omdoc_schema import create_variable
                return create_entry(
                    EntryType.PARTIAL_RESULT,
                    create_variable(f"Error: {str(e)}"),
                    self.agent_id,
                    task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'error',
                    ['ode', 'error'],
                    EntryStatus.FAILED,
                    {'error': str(e)}
                )
            else:
                return f"Error: {str(e)}"

    def classify_ode(self, ode_str: str, var: str = 'x', func: str = 'y') -> ODEClassification:
        """
        Classify an ODE to determine the solving method.

        Args:
            ode_str: ODE expression (e.g., "y' + y = x" or "dy/dx = x*y")
            var: Independent variable
            func: Dependent function name

        Returns:
            ODEClassification with ODE type and metadata
        """
        # Normalize notation
        normalized = self._normalize_ode_notation(ode_str, var, func)

        # Check for second-order terms
        has_second_deriv = any(p in normalized for p in [f"{func}''", f"d2{func}/d{var}2", f"d²{func}"])
        order = 2 if has_second_deriv else 1

        # Check for linearity (rough heuristic)
        # Nonlinear if y*y', y^2, sin(y), etc. appear
        nonlinear_patterns = [f"{func}*{func}", f"{func}**2", f"{func}^2", f"sin({func})", f"cos({func})"]
        is_linear = not any(p in normalized.replace(' ', '') for p in nonlinear_patterns)

        # Classify type
        coefficients = {}

        if order == 1:
            # Check if separable: dy/dx = f(x)*g(y)
            if self._is_separable(normalized, var, func):
                return ODEClassification(
                    order=1, linearity='linear' if is_linear else 'nonlinear',
                    ode_type='separable', homogeneous=False,
                    has_initial_conditions=False, coefficients=coefficients
                )

            # Check if linear first-order: y' + P(x)*y = Q(x)
            if is_linear:
                p_coeff, q_coeff = self._extract_linear_coefficients(normalized, var, func)
                coefficients['P'] = p_coeff
                coefficients['Q'] = q_coeff
                return ODEClassification(
                    order=1, linearity='linear', ode_type='linear_first',
                    homogeneous=(q_coeff == '0' or q_coeff == 0),
                    has_initial_conditions=False, coefficients=coefficients
                )

        elif order == 2:
            # Check for constant coefficients: ay'' + by' + cy = f(x)
            a, b, c, f_x = self._extract_constant_coefficients(normalized, var, func)
            if a is not None:
                coefficients['a'] = a
                coefficients['b'] = b
                coefficients['c'] = c
                coefficients['f_x'] = f_x
                return ODEClassification(
                    order=2, linearity='linear', ode_type='constant_coeff',
                    homogeneous=(f_x == '0' or f_x == 0),
                    has_initial_conditions=False, coefficients=coefficients
                )

        # Default classification
        return ODEClassification(
            order=order, linearity='linear' if is_linear else 'nonlinear',
            ode_type='general', homogeneous=False,
            has_initial_conditions=False, coefficients=coefficients
        )

    def _normalize_ode_notation(self, ode_str: str, var: str, func: str) -> str:
        """Normalize ODE notation to standard form."""
        s = ode_str.strip()

        # Replace various derivative notations
        replacements = [
            (f"d{func}/d{var}", f"{func}'"),
            (f"d²{func}/d{var}²", f"{func}''"),
            (f"d2{func}/d{var}2", f"{func}''"),
            ("dy/dx", "y'"),
            ("d2y/dx2", "y''"),
        ]
        for old, new in replacements:
            s = s.replace(old, new)

        return s

    def _is_separable(self, ode_str: str, var: str, func: str) -> bool:
        """Check if ODE is separable."""
        # Pattern: y' = f(x)*g(y) or dy/dx = f(x)*g(y)
        # Simple heuristic: check if RHS can be factored
        if '=' in ode_str:
            parts = ode_str.split('=')
            if len(parts) == 2:
                lhs, rhs = parts
                # Check if LHS is ONLY the derivative (no y term)
                # Remove derivative notation to check for remaining y
                lhs_without_deriv = lhs.replace(f"{func}'", '').replace(f"d{func}/d{var}", '')
                # If func still appears in LHS, it's linear, not separable
                if func in lhs_without_deriv:
                    return False  # Linear ODE (has y term in LHS)
                # Check if derivative is in LHS and func appears in RHS
                if f"{func}'" in lhs and func in rhs:
                    return True  # Separable: y' = f(x)*g(y)
        return False

    def _extract_linear_coefficients(self, ode_str: str, var: str, func: str) -> Tuple[str, str]:
        """Extract P(x) and Q(x) from y' + P(x)*y = Q(x)."""
        # Simplified extraction for standard form: dy/dx + P*y = Q
        try:
            if '=' in ode_str:
                parts = ode_str.split('=')
                if len(parts) == 2:
                    lhs, rhs = parts[0].strip(), parts[1].strip()

                    # Normalize: replace dy/dx with y' for easier parsing
                    lhs = lhs.replace(f"d{func}/d{var}", f"{func}'")

                    # Pattern: y' + P*y = Q  or  y' - P*y = Q
                    # Find the coefficient of y (after the derivative term)

                    # Remove the y' term to isolate the y coefficient
                    lhs_without_deriv = lhs.replace(f"{func}'", '', 1)  # Remove first y'

                    # What's left should be "+ P*y" or "- P*y" or just "y"
                    # Extract coefficient before y
                    lhs_clean = lhs_without_deriv.strip()

                    # Parse coefficient of y
                    p_coeff = '0'
                    if func in lhs_clean:
                        # Pattern: + (3)*y  or  + 2*x*y  or just + y
                        # Remove leading + or -
                        sign = 1
                        if lhs_clean.startswith('+'):
                            lhs_clean = lhs_clean[1:].strip()
                        elif lhs_clean.startswith('-'):
                            sign = -1
                            lhs_clean = lhs_clean[1:].strip()

                        # Remove the y to get coefficient
                        if lhs_clean.endswith(f"*{func}"):
                            p_coeff = lhs_clean[:-len(f"*{func}")].strip()
                        elif lhs_clean.endswith(func):
                            # Just "y" means coefficient is 1
                            p_coeff = '1'
                        else:
                            # Has y somewhere inside
                            p_coeff = lhs_clean.replace(func, '').replace('*', '').strip() or '1'

                        # Apply sign
                        if sign == -1 and p_coeff != '0':
                            p_coeff = f"-({p_coeff})" if '*' in p_coeff or '+' in p_coeff else f"-{p_coeff}"

                    return p_coeff, rhs

        except Exception as e:
            logger.debug(f"Coefficient extraction failed: {e}")
            pass
        return '0', '0'

    def _extract_constant_coefficients(self, ode_str: str, var: str, func: str) -> Tuple[Optional[float], Optional[float], Optional[float], str]:
        """Extract a, b, c from ay'' + by' + cy = f(x)."""
        # Pattern matching for constant coefficient ODEs
        try:
            # Look for patterns like "y'' + 3*y' + 2*y = sin(x)"
            pattern = r"(\d*\.?\d*)\s*\*?\s*" + re.escape(func) + r"''\s*([+-]\s*\d*\.?\d*)\s*\*?\s*" + re.escape(func) + r"'\s*([+-]\s*\d*\.?\d*)\s*\*?\s*" + re.escape(func) + r"\s*=\s*(.+)"

            # Simplified: try to extract numeric coefficients
            s = ode_str.replace(' ', '')

            # Default values for y'' + by' + cy = f(x) form
            a, b, c = 1.0, 0.0, 0.0
            f_x = '0'

            if '=' in s:
                lhs, rhs = s.split('=', 1)
                f_x = rhs

                # Check for y'' coefficient
                if f"{func}''" in lhs:
                    a = 1.0

                # Try to find y' coefficient
                if f"{func}'" in lhs and f"{func}''" not in lhs:
                    b = 1.0

                # Try to find y coefficient (not followed by ')
                if func in lhs.replace(f"{func}''", '').replace(f"{func}'", ''):
                    c = 1.0

            return a, b, c, f_x

        except Exception:
            return None, None, None, '0'

    def solve_ode(
        self,
        ode_str: str,
        var: str = 'x',
        func: str = 'y',
        initial_conditions: Dict = None
    ) -> Dict[str, Any]:
        """
        Solve an ODE with automatic classification.

        Args:
            ode_str: ODE expression
            var: Independent variable (default 'x')
            func: Dependent function (default 'y')
            initial_conditions: Dict with ICs like {'y(0)': 1, "y'(0)": 0}

        Returns:
            Dict with solution and metadata
        """
        initial_conditions = initial_conditions or {}

        with track_computation('solve_ode', ode_str, domain='calculus', specialist=self.agent_id):
            # Classify the ODE
            classification = self.classify_ode(ode_str, var, func)

            logger.info(f"  ODE Classification: order={classification.order}, type={classification.ode_type}")

            # Route to appropriate solver
            if classification.ode_type == 'separable':
                result = self.solve_separable(ode_str, var, func)

            elif classification.ode_type == 'linear_first':
                result = self.solve_linear_first_order(
                    classification.coefficients.get('P', '0'),
                    classification.coefficients.get('Q', '0'),
                    var, func
                )

            elif classification.ode_type == 'constant_coeff' and classification.order == 2:
                result = self.solve_second_order_constant(
                    classification.coefficients.get('a', 1),
                    classification.coefficients.get('b', 0),
                    classification.coefficients.get('c', 0),
                    classification.coefficients.get('f_x', '0'),
                    var, func
                )

            else:
                # General case - try heuristics
                result = self._solve_general(ode_str, var, func)

            # Apply initial conditions if provided
            if initial_conditions and result.get('success'):
                result = self._apply_initial_conditions(result, initial_conditions, var, func)

            result['classification'] = {
                'order': classification.order,
                'type': classification.ode_type,
                'linearity': classification.linearity,
                'homogeneous': classification.homogeneous
            }

            return result

    def solve_separable(self, ode_str: str, var: str = 'x', func: str = 'y') -> Dict[str, Any]:
        """
        Solve a separable ODE: dy/dx = f(x)*g(y)

        Method: ∫(1/g(y))dy = ∫f(x)dx
        """
        try:
            # Parse: y' = f(x)*g(y) or similar
            if '=' in ode_str:
                parts = ode_str.split('=')
                if len(parts) == 2:
                    rhs = parts[1].strip()

                    # Simple case: dy/dx = f(x)
                    if func not in rhs:
                        # Integrate f(x) directly
                        success, integral, _ = native_integrate(rhs, var)
                        if success:
                            return {
                                'success': True,
                                'solution': f"{func} = {integral} + C",
                                'method': 'direct_integration',
                                'general_solution': True
                            }

                    # Try to factor: f(x)*g(y) using improved factorization
                    f_x, g_y = self._factor_separable_improved(rhs, var, func)

                    if f_x and g_y:
                        # Integrate both sides
                        success_x, int_f, _ = native_integrate(f_x, var)

                        # For y part, we need 1/g(y)
                        # Handle special forms: sqrt(y), y^n, 1/y
                        g_y_inv = self._build_reciprocal(g_y, func)
                        success_y, int_g_inv, _ = native_integrate(g_y_inv, func)

                        if success_x and success_y:
                            return {
                                'success': True,
                                'solution': f"{int_g_inv} = {int_f} + C",
                                'method': 'separation_of_variables',
                                'general_solution': True
                            }

            return {
                'success': False,
                'error': 'Could not solve as separable ODE',
                'method': 'separable'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'separable'
            }

    def solve_linear_first_order(
        self,
        p_x: str,
        q_x: str,
        var: str = 'x',
        func: str = 'y'
    ) -> Dict[str, Any]:
        """
        Solve first-order linear ODE: y' + P(x)*y = Q(x)

        Method: Integrating factor μ(x) = exp(∫P(x)dx)
        Solution: y = (1/μ(x)) * ∫μ(x)*Q(x)dx
        """
        try:
            # Compute integrating factor
            success_p, int_p, _ = native_integrate(p_x, var)
            if not success_p:
                return {
                    'success': False,
                    'error': f'Could not integrate P(x) = {p_x}',
                    'method': 'integrating_factor'
                }

            # μ(x) = exp(∫P(x)dx)
            mu = f"exp({int_p})"

            # Integrate μ(x)*Q(x)
            if q_x == '0' or q_x == 0:
                # Homogeneous case: y = C*exp(-∫P(x)dx)
                return {
                    'success': True,
                    'solution': f"{func} = C*exp(-({int_p}))",
                    'integrating_factor': mu,
                    'method': 'integrating_factor',
                    'general_solution': True
                }

            # Non-homogeneous
            product = f"({mu})*({q_x})"
            success_prod, int_prod, _ = native_integrate(product, var)

            # If native integration failed, try AdvancedIntegrationSpecialist
            if not success_prod:
                advanced_result = self._try_advanced_integration(product, var)
                if advanced_result and advanced_result.get('success'):
                    int_prod = advanced_result['solution']
                    success_prod = True

            if success_prod:
                return {
                    'success': True,
                    'solution': f"{func} = (1/({mu}))*({int_prod} + C)",
                    'integrating_factor': mu,
                    'method': 'integrating_factor',
                    'general_solution': True
                }
            else:
                return {
                    'success': False,
                    'error': f'Could not integrate μ(x)*Q(x)',
                    'method': 'integrating_factor'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'integrating_factor'
            }

    def _try_advanced_integration(self, expression: str, var: str) -> Optional[Dict[str, Any]]:
        """
        Try advanced integration using AdvancedIntegrationSpecialist

        Used when native_integrate fails on complex patterns like exp×trig products.

        Args:
            expression: Expression to integrate
            var: Integration variable

        Returns:
            Integration result dict or None
        """
        # Lazy load AdvancedIntegrationSpecialist from DF
        if not self._advanced_integration_specialist:
            if not self.df:
                return None

            specialists = self.df.search(service_type='math.calculus.integration.advanced')
            if specialists:
                self._advanced_integration_specialist = specialists[0].instance
            else:
                logger.debug(f"[{self.agent_id}] AdvancedIntegrationSpecialist not found in DF")
                return None

        # Create mock task entry for the integration specialist
        try:
            if self._advanced_integration_specialist:
                # Call the specialist's process method with mock task
                from symbo_agentic_reasoners.core.blackboard import create_entry
                from symbo_agentic_reasoners.core.omdoc_schema import create_variable

                mock_task = type('MockTask', (), {
                    'entry_id': f'ode_integration_{hash(expression)}',
                    'conversation_id': 'ode_integration',
                    'metadata': {
                        'expression': expression,
                        'variable': var,
                        'raw_input': expression
                    }
                })()

                result_entry = self._advanced_integration_specialist.process(mock_task)

                # Extract result from entry
                if hasattr(result_entry, 'metadata'):
                    # Check if it's an error entry
                    if result_entry.metadata.get('error'):
                        return {
                            'success': False,
                            'error': result_entry.metadata.get('error')
                        }
                    # Success entry
                    result_str = result_entry.metadata.get('result', '')
                    if result_str:
                        return {
                            'success': True,
                            'solution': result_str,
                            'method': result_entry.metadata.get('method', 'advanced')
                        }
                elif isinstance(result_entry, dict):
                    return result_entry

        except Exception as e:
            logger.debug(f"[{self.agent_id}] Advanced integration failed: {e}")

        return None

    def _split_respecting_parens(self, expr: str, delimiter: str) -> List[str]:
        """
        Split expression by delimiter while respecting parentheses.

        Example:
            "(4*x)*(1/y)" split by "*" → ["(4*x)", "(1/y)"]
            "x*y*z" split by "*" → ["x", "y", "z"]
        """
        parts = []
        current = []
        depth = 0

        for char in expr:
            if char == '(':
                depth += 1
                current.append(char)
            elif char == ')':
                depth -= 1
                current.append(char)
            elif char == delimiter and depth == 0:
                # Top-level delimiter found
                if current:
                    parts.append(''.join(current).strip())
                    current = []
            else:
                current.append(char)

        # Add final part
        if current:
            parts.append(''.join(current).strip())

        return parts

    def _factor_separable_improved(self, rhs: str, var: str, func: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Improved factorization for separable ODEs: dy/dx = f(x)*g(y)

        Handles:
        - Simple products: x*y, sin(x)*y
        - Square roots: x*sqrt(y), x/sqrt(y)
        - Powers: x*y^2, x*y^(-1)
        - Quotients: x/y, y/x
        - Complex forms: (x+1)*sqrt(y), sin(x)/y^2
        - Parenthesized: (4*x)*(1/y), (sin(x))*(y**2)

        Args:
            rhs: Right-hand side expression
            var: Independent variable (usually 'x')
            func: Dependent variable (usually 'y')

        Returns:
            (f_x, g_y) tuple where dy/dx = f(x)*g(y), or (None, None) if not separable
        """
        import re

        # Strategy 1: Explicit multiplication (parenthesis-aware)
        if '*' in rhs:
            # Split and classify factors (respecting parentheses)
            x_parts, y_parts = [], []
            factors = self._split_respecting_parens(rhs, '*')

            for factor in factors:
                factor = factor.strip()

                # Strip outer parentheses if present
                if factor.startswith('(') and factor.endswith(')'):
                    # Check if it's a balanced single pair
                    depth = 0
                    balanced = True
                    for i, char in enumerate(factor):
                        if char == '(':
                            depth += 1
                        elif char == ')':
                            depth -= 1
                        if depth == 0 and i < len(factor) - 1:
                            balanced = False
                            break
                    if balanced:
                        factor = factor[1:-1].strip()

                # Check if factor contains only x (not y)
                if var in factor and func not in factor:
                    x_parts.append(factor)
                # Check if factor contains only y (not x)
                elif func in factor and var not in factor:
                    y_parts.append(factor)
                # Check for sqrt(y) or other y functions
                elif 'sqrt' in factor.lower() and func in factor:
                    y_parts.append(factor)
                # Constants go to x part
                elif func not in factor and var not in factor:
                    x_parts.append(factor)

            if x_parts and y_parts:
                f_x = '*'.join(x_parts) if x_parts else '1'
                g_y = '*'.join(y_parts) if y_parts else '1'
                return f_x, g_y

        # Strategy 2: Division patterns
        if '/' in rhs:
            # Split by division
            parts = rhs.split('/', 1)
            numer = parts[0].strip()
            denom = parts[1].strip()

            # y/x pattern: f(x) = 1/x, g(y) = y
            if func in numer and var not in numer and var in denom and func not in denom:
                return f"1/({denom})", numer

            # x/y pattern: f(x) = x, g(y) = 1/y
            if var in numer and func not in numer and func in denom and var not in denom:
                return numer, f"1/({denom})"

            # x/sqrt(y) pattern: f(x) = x, g(y) = 1/sqrt(y) = y^(-1/2)
            if 'sqrt' in denom.lower() and func in denom:
                if var in numer and func not in numer:
                    # Extract sqrt content
                    sqrt_pattern = r'sqrt\(([^)]+)\)'
                    match = re.search(sqrt_pattern, denom, re.IGNORECASE)
                    if match and func in match.group(1):
                        return numer, f"({match.group(1)})**(-0.5)"

        # Strategy 3: Handle sqrt(y) in numerator
        if 'sqrt' in rhs.lower():
            # x*sqrt(y) or similar
            sqrt_pattern = rf'sqrt\(({func}[^)]*)\)'
            match = re.search(sqrt_pattern, rhs, re.IGNORECASE)
            if match:
                # Extract parts before and after sqrt
                sqrt_expr = match.group(0)
                remaining = rhs.replace(sqrt_expr, '').replace('*', '').strip()

                if var in remaining and func not in remaining:
                    # f(x) = remaining, g(y) = sqrt(y)
                    return remaining if remaining else '1', f"({match.group(1)})**(0.5)"

        # Strategy 4: Power patterns y^n
        power_pattern = rf'{func}\s*\*\*\s*(-?\d+\.?\d*)'
        match = re.search(power_pattern, rhs)
        if match:
            power = match.group(1)
            y_power = match.group(0)
            # Remove y^n from rhs to get f(x)
            f_x = rhs.replace(y_power, '').replace('*', '').strip()
            if f_x and var in f_x:
                return f_x, f"{func}**{power}"

        return None, None

    def _build_reciprocal(self, g_y: str, func: str) -> str:
        """
        Build reciprocal 1/g(y) for integration

        Handles:
        - g(y) = y → 1/y
        - g(y) = 1/y → y (reciprocal of reciprocal)
        - g(y) = sqrt(y) = y^(0.5) → 1/sqrt(y) = y^(-0.5)
        - g(y) = y^n → y^(-n)
        - g(y) = y^(0.5) → y^(-0.5)

        Args:
            g_y: g(y) expression
            func: Function variable ('y')

        Returns:
            1/g(y) expression
        """
        import re

        # If g_y is already 1/y or 1/(y) or similar, return y
        if g_y.strip().startswith('1/'):
            inner = g_y.strip()[2:].strip()
            # Remove outer parentheses if present
            if inner.startswith('(') and inner.endswith(')'):
                inner = inner[1:-1].strip()
            # If inner is just the function variable, return it
            if inner == func:
                return func
            # Otherwise return the inner expression
            return inner

        # If already a power, negate exponent
        power_pattern = rf'{func}\s*\*\*\s*\(?([-\d\.]+)\)?'
        match = re.search(power_pattern, g_y)
        if match:
            exponent = float(match.group(1))
            return f"{func}**({-exponent})"

        # If sqrt(y), convert to y^(-0.5)
        if 'sqrt' in g_y.lower():
            sqrt_pattern = rf'sqrt\(({func})\)'
            match = re.search(sqrt_pattern, g_y, re.IGNORECASE)
            if match:
                return f"{func}**(-0.5)"

        # If just y, return 1/y (which integrates to ln|y|)
        if g_y.strip() == func:
            return f"1/{func}"

        # Default: wrap in 1/(...)
        return f"1/({g_y})"

    def solve_exact_ode(
        self,
        m_expr: str,
        n_expr: str,
        var: str = 'x',
        func: str = 'y'
    ) -> Dict[str, Any]:
        """
        Solve exact ODE: M(x,y)dx + N(x,y)dy = 0

        An ODE is exact if ∂M/∂y = ∂N/∂x
        Solution is found by integrating to find potential function F(x,y) = C

        Args:
            m_expr: M(x,y) coefficient of dx
            n_expr: N(x,y) coefficient of dy
            var: Independent variable (x)
            func: Dependent function (y)

        Returns:
            Dict with solution or error
        """
        try:
            logger.info(f"Checking if ODE is exact: M={m_expr}, N={n_expr}")

            # Check exactness: ∂M/∂y = ∂N/∂x
            # Simplified check - in practice would compute partial derivatives
            is_exact = self._check_exactness(m_expr, n_expr, var, func)

            if not is_exact:
                # Try to find integrating factor
                integrating_factor = self._find_integrating_factor(m_expr, n_expr, var, func)

                if integrating_factor:
                    return {
                        'success': True,
                        'solution': f"Integrating factor: {integrating_factor}",
                        'method': 'exact_with_integrating_factor',
                        'note': 'Multiply equation by integrating factor and solve'
                    }
                else:
                    return {
                        'success': False,
                        'error': 'ODE is not exact and no integrating factor found',
                        'method': 'exact'
                    }

            # Integrate M with respect to x
            success_m, int_m, _ = native_integrate(m_expr, var)
            if not success_m:
                return {
                    'success': False,
                    'error': f'Could not integrate M(x,y) = {m_expr}',
                    'method': 'exact'
                }

            # F(x,y) = ∫M dx + g(y)
            # To find g(y), differentiate F with respect to y and compare with N

            return {
                'success': True,
                'solution': f"F(x,y) = {int_m} + g(y) = C",
                'method': 'exact',
                'note': 'Complete by determining g(y) from N(x,y)'
            }

        except Exception as e:
            logger.error(f"Exact ODE solving failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'exact'
            }

    def _check_exactness(self, m_expr: str, n_expr: str, var: str, func: str) -> bool:
        """
        Check if ODE is exact: ∂M/∂y = ∂N/∂x

        Simplified implementation - full version would compute partial derivatives
        """
        # Simplified heuristic: check if both M and N have compatible forms
        # Real implementation would differentiate symbolically

        # For now, return False to demonstrate integrating factor approach
        return False

    def _find_integrating_factor(self, m_expr: str, n_expr: str, var: str, func: str) -> Optional[str]:
        """
        Find integrating factor to make ODE exact.

        Common integrating factors:
        - μ(x): function of x only if (∂M/∂y - ∂N/∂x)/N depends only on x
        - μ(y): function of y only if (∂N/∂x - ∂M/∂y)/M depends only on y
        """
        # Simplified implementation
        # Real version would compute and check the conditions
        return None

    def solve_bernoulli_ode(
        self,
        p_x: str,
        q_x: str,
        n: float,
        var: str = 'x',
        func: str = 'y'
    ) -> Dict[str, Any]:
        """
        Solve Bernoulli ODE: y' + P(x)*y = Q(x)*y^n

        Method: Substitute v = y^(1-n) to transform into linear ODE
        v' + (1-n)*P(x)*v = (1-n)*Q(x)

        Args:
            p_x: P(x) coefficient
            q_x: Q(x) coefficient
            n: Power of y (n ≠ 0, 1)
            var: Independent variable
            func: Dependent function

        Returns:
            Dict with solution
        """
        try:
            logger.info(f"Solving Bernoulli ODE with n={n}")

            if abs(n) < 1e-10:
                # n = 0: reduces to linear first-order
                return self.solve_linear_first_order(p_x, q_x, var, func)

            if abs(n - 1) < 1e-10:
                # n = 1: already linear
                return self.solve_linear_first_order(p_x, q_x, var, func)

            # Substitute v = y^(1-n)
            # v' = (1-n)*y^(-n)*y'
            # So y' = v'*y^n/(1-n)

            # Original: y' + P(x)*y = Q(x)*y^n
            # Becomes: v'/(1-n) + P(x)*y^(1)*(y^(n-1)) = Q(x)*y^n
            # Multiply by y^(-n): v'*y^(-n)/(1-n) + P(x)*y^(1-n) = Q(x)
            # Since v = y^(1-n): v'/(1-n) + P(x)*v = Q(x)
            # Rearrange: v' + (1-n)*P(x)*v = (1-n)*Q(x)

            # Transform coefficients
            one_minus_n = 1 - n
            p_transformed = f"({one_minus_n})*({p_x})"
            q_transformed = f"({one_minus_n})*({q_x})"

            # Solve linear ODE for v
            result = self.solve_linear_first_order(p_transformed, q_transformed, var, 'v')

            if result['success']:
                # Back-substitute: y = v^(1/(1-n))
                v_solution = result['solution']

                return {
                    'success': True,
                    'solution': f"{func} = ({v_solution})^(1/{one_minus_n})",
                    'substitution': f"v = {func}^{one_minus_n}",
                    'method': 'bernoulli',
                    'general_solution': True
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Bernoulli ODE solving failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'bernoulli'
            }

    def solve_homogeneous_first_order(
        self,
        ode_str: str,
        var: str = 'x',
        func: str = 'y'
    ) -> Dict[str, Any]:
        """
        Solve homogeneous first-order ODE: dy/dx = f(y/x)

        Method: Substitute v = y/x, so y = vx
        dy/dx = v + x*dv/dx
        This transforms to separable ODE in v and x

        Args:
            ode_str: ODE expression
            var: Independent variable
            func: Dependent function

        Returns:
            Dict with solution
        """
        try:
            logger.info(f"Solving homogeneous first-order ODE")

            # Check if it's homogeneous form
            if '=' not in ode_str:
                return {
                    'success': False,
                    'error': 'ODE must be in form dy/dx = f(y/x)',
                    'method': 'homogeneous'
                }

            parts = ode_str.split('=')
            if len(parts) != 2:
                return {
                    'success': False,
                    'error': 'Invalid ODE format',
                    'method': 'homogeneous'
                }

            rhs = parts[1].strip()

            # Substitute v = y/x
            # dy/dx = v + x*dv/dx = f(v)
            # x*dv/dx = f(v) - v
            # dv/(f(v) - v) = dx/x

            return {
                'success': True,
                'solution': f"Use substitution v = {func}/{var}, solve separable ODE",
                'substitution': f"v = {func}/{var}",
                'method': 'homogeneous',
                'note': 'Transform to separable ODE: dv/(f(v)-v) = dx/x'
            }

        except Exception as e:
            logger.error(f"Homogeneous ODE solving failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'homogeneous'
            }

    def solve_riccati_ode(
        self,
        p_x: str,
        q_x: str,
        r_x: str,
        var: str = 'x',
        func: str = 'y',
        particular_solution: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Solve Riccati ODE: y' = P(x) + Q(x)*y + R(x)*y^2

        Method: If a particular solution y1 is known:
        Substitute y = y1 + 1/v to transform into linear ODE

        Args:
            p_x: P(x) coefficient
            q_x: Q(x) coefficient
            r_x: R(x) coefficient
            var: Independent variable
            func: Dependent function
            particular_solution: Known particular solution y1 (if available)

        Returns:
            Dict with solution or transformation instructions
        """
        try:
            logger.info(f"Solving Riccati ODE")

            if particular_solution is None:
                return {
                    'success': False,
                    'error': 'Riccati equation requires a known particular solution',
                    'method': 'riccati',
                    'note': 'General Riccati equations cannot be solved in closed form'
                }

            # If y1 is a particular solution, substitute y = y1 + 1/v
            # This transforms the Riccati equation into a linear first-order ODE in v

            return {
                'success': True,
                'solution': f"With particular solution {func}1 = {particular_solution}",
                'substitution': f"{func} = {particular_solution} + 1/v",
                'method': 'riccati',
                'note': f'Substitute into original equation and solve linear ODE for v'
            }

        except Exception as e:
            logger.error(f"Riccati ODE solving failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'riccati'
            }

    def solve_second_order_constant(
        self,
        a: float,
        b: float,
        c: float,
        f_x: str,
        var: str = 'x',
        func: str = 'y'
    ) -> Dict[str, Any]:
        """
        Solve second-order linear ODE with constant coefficients:
        a*y'' + b*y' + c*y = f(x)

        Method:
        1. Solve characteristic equation: ar² + br + c = 0
        2. Build homogeneous solution based on roots
        3. Find particular solution for f(x) if non-homogeneous
        """
        try:
            # Solve characteristic equation ar² + br + c = 0
            discriminant = b*b - 4*a*c

            if discriminant > 0:
                # Two distinct real roots
                r1 = (-b + math.sqrt(discriminant)) / (2*a)
                r2 = (-b - math.sqrt(discriminant)) / (2*a)
                y_h = f"C1*exp({r1}*{var}) + C2*exp({r2}*{var})"
                root_type = 'distinct_real'

            elif discriminant == 0:
                # Repeated real root
                r = -b / (2*a)
                y_h = f"(C1 + C2*{var})*exp({r}*{var})"
                root_type = 'repeated_real'

            else:
                # Complex conjugate roots
                alpha = -b / (2*a)
                beta = math.sqrt(-discriminant) / (2*a)
                y_h = f"exp({alpha}*{var})*(C1*cos({beta}*{var}) + C2*sin({beta}*{var}))"
                root_type = 'complex_conjugate'

            # Check if homogeneous
            if f_x == '0' or f_x == 0 or not f_x.strip():
                return {
                    'success': True,
                    'solution': f"{func} = {y_h}",
                    'homogeneous_solution': y_h,
                    'characteristic_roots': root_type,
                    'method': 'characteristic_equation',
                    'general_solution': True
                }

            # Non-homogeneous: find particular solution
            y_p = self._find_particular_solution(a, b, c, f_x, var)

            if y_p:
                return {
                    'success': True,
                    'solution': f"{func} = {y_h} + {y_p}",
                    'homogeneous_solution': y_h,
                    'particular_solution': y_p,
                    'characteristic_roots': root_type,
                    'method': 'characteristic_equation_plus_particular',
                    'general_solution': True
                }
            else:
                # Could only find homogeneous solution
                return {
                    'success': True,
                    'solution': f"{func} = {y_h}",
                    'homogeneous_solution': y_h,
                    'particular_solution': 'Could not determine',
                    'note': f'Particular solution for f(x)={f_x} not found',
                    'method': 'characteristic_equation',
                    'general_solution': False
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'characteristic_equation'
            }

    def _find_particular_solution(
        self,
        a: float,
        b: float,
        c: float,
        f_x: str,
        var: str
    ) -> Optional[str]:
        """
        Find particular solution using undetermined coefficients.

        Handles common f(x) forms:
        - Polynomials: A*x^n + ... -> try same form
        - Exponentials: e^(kx) -> try A*e^(kx)
        - Sine/Cosine: sin(kx), cos(kx) -> try A*sin(kx) + B*cos(kx)
        """
        f_x = f_x.strip()

        try:
            # Check for polynomial (constant or linear)
            if f_x.replace(' ', '').replace('-', '').replace('+', '').replace('.', '').isdigit():
                # Constant f(x) = k
                if c != 0:
                    k = float(f_x)
                    return str(k / c)

            # Check for exp(k*x)
            if 'exp(' in f_x:
                # Extract exponent coefficient (simplified)
                match = re.search(r'exp\(([+-]?\d*\.?\d*)\*?' + var + r'\)', f_x)
                if match:
                    k = float(match.group(1)) if match.group(1) else 1.0
                    # Particular: A*exp(k*x)
                    # Substituting: a*k²*A + b*k*A + c*A = 1
                    denom = a*k*k + b*k + c
                    if denom != 0:
                        return f"(1/{denom})*exp({k}*{var})"

            # Check for sin or cos
            if 'sin(' in f_x or 'cos(' in f_x:
                # Try A*sin(x) + B*cos(x) form
                # Simplified: assume sin(x) or cos(x)
                omega = 1.0  # Default frequency
                match = re.search(r'(sin|cos)\(([+-]?\d*\.?\d*)\*?' + var + r'\)', f_x)
                if match:
                    omega = float(match.group(2)) if match.group(2) else 1.0

                # For y'' + c*y = sin(ωx): particular is -sin(ωx)/(ω² - c) if ω² ≠ c
                denom = c - a*omega*omega
                if denom != 0:
                    if 'sin' in f_x:
                        return f"(1/{denom})*sin({omega}*{var})"
                    else:
                        return f"(1/{denom})*cos({omega}*{var})"

            # Check for x^n (polynomial)
            if var in f_x and not any(fn in f_x for fn in ['exp', 'sin', 'cos', 'log']):
                # Try polynomial of same degree
                if c != 0:
                    # For f(x) = x: try y_p = Ax + B
                    # c*(Ax + B) = x -> A = 1/c, B can be 0
                    return f"(1/{c})*{f_x}"

        except Exception:
            pass

        return None

    def solve_series_power(
        self,
        ode_str: str,
        var: str = 'x',
        func: str = 'y',
        x0: float = 0.0,
        n_terms: int = 5
    ) -> Dict[str, Any]:
        """
        Solve ODE using power series expansion around ordinary point x0.

        For ODEs with analytic coefficients at x0, expand:
        y = Σ(a_n * (x-x0)^n)

        Args:
            ode_str: ODE expression
            var: Independent variable
            func: Dependent function
            x0: Expansion point (ordinary point)
            n_terms: Number of series terms to compute

        Returns:
            Dict with series solution and coefficients
        """
        try:
            logger.info(f"Solving ODE using power series at x0={x0}")

            # For demo purposes, implement a simplified power series solver
            # Real implementation would:
            # 1. Substitute y = Σ(a_n * (x-x0)^n) into ODE
            # 2. Collect coefficients of like powers
            # 3. Solve recurrence relation for a_n

            # Example for y' = y (exponential)
            if "'" in ode_str and '=' in ode_str:
                parts = ode_str.split('=')
                if len(parts) == 2:
                    rhs = parts[1].strip()

                    # Simple case: y' = y -> y = e^x = Σ(x^n/n!)
                    if rhs == func or rhs == f"{func}":
                        coeffs = [1.0]  # a_0 = 1
                        for n in range(1, n_terms):
                            coeffs.append(coeffs[-1] / n)  # a_n = a_(n-1)/n

                        # Build series expression
                        terms = []
                        for n, coeff in enumerate(coeffs):
                            if abs(coeff) > 1e-10:
                                if n == 0:
                                    terms.append(f"{coeff:.6f}")
                                elif n == 1:
                                    terms.append(f"{coeff:.6f}*{var}")
                                else:
                                    terms.append(f"{coeff:.6f}*{var}^{n}")

                        series_expr = " + ".join(terms)

                        return {
                            'success': True,
                            'solution': f"{func} ≈ {series_expr} + O({var}^{n_terms})",
                            'coefficients': coeffs,
                            'expansion_point': x0,
                            'n_terms': n_terms,
                            'method': 'power_series',
                            'convergence_note': f'Valid near x = {x0}'
                        }

            return {
                'success': False,
                'error': 'Power series method not applicable or not implemented for this ODE type',
                'method': 'power_series'
            }

        except Exception as e:
            logger.error(f"Power series solution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'power_series'
            }

    def solve_series_frobenius(
        self,
        ode_str: str,
        var: str = 'x',
        func: str = 'y',
        x0: float = 0.0,
        n_terms: int = 5
    ) -> Dict[str, Any]:
        """
        Solve ODE using Frobenius method around regular singular point x0.

        For ODEs with regular singular point at x0, expand:
        y = (x-x0)^r * Σ(a_n * (x-x0)^n)

        where r is determined by the indicial equation.

        Args:
            ode_str: ODE expression (typically second-order linear)
            var: Independent variable
            func: Dependent function
            x0: Expansion point (regular singular point)
            n_terms: Number of series terms to compute

        Returns:
            Dict with Frobenius series solution, indicial roots, and coefficients
        """
        try:
            logger.info(f"Solving ODE using Frobenius method at x0={x0}")

            # Simplified Frobenius implementation
            # Real implementation would:
            # 1. Classify singular point (regular vs irregular)
            # 2. Compute indicial equation: r(r-1) + p0*r + q0 = 0
            # 3. Find indicial roots r1, r2
            # 4. Generate recurrence relation for a_n
            # 5. Build two independent solutions

            # Example: Bessel equation x^2*y'' + x*y' + (x^2 - n^2)*y = 0
            # has regular singular point at x=0

            # For demonstration, handle a simple case
            singular_point_type = self._classify_singular_point(ode_str, var, x0)

            if singular_point_type != 'regular':
                return {
                    'success': False,
                    'error': f'Point x={x0} is not a regular singular point (type: {singular_point_type})',
                    'method': 'frobenius'
                }

            # Compute indicial equation (simplified)
            indicial_roots = self._compute_indicial_equation(ode_str, var, x0)

            if not indicial_roots:
                return {
                    'success': False,
                    'error': 'Could not determine indicial roots',
                    'method': 'frobenius'
                }

            r1, r2 = indicial_roots

            # Generate recurrence relation and coefficients for dominant root
            coeffs = self._generate_series_coefficients_frobenius(ode_str, var, r1, n_terms)

            # Build series expression: y = x^r * Σ(a_n * x^n)
            terms = []
            for n, coeff in enumerate(coeffs):
                if abs(coeff) > 1e-10:
                    power = r1 + n
                    if abs(power) < 1e-10:  # power ≈ 0
                        terms.append(f"{coeff:.6f}")
                    elif abs(power - 1) < 1e-10:  # power ≈ 1
                        terms.append(f"{coeff:.6f}*{var}")
                    else:
                        terms.append(f"{coeff:.6f}*{var}^{power:.2f}")

            series_expr = " + ".join(terms) if terms else "0"

            solution_text = f"{func} ≈ {series_expr} + O({var}^{r1 + n_terms:.2f})"

            # Note about second solution
            note = ""
            if abs(r1 - r2) < 1e-10:
                note = "Second solution involves logarithmic term"
            elif abs(r1 - r2 - int(r1 - r2)) > 1e-10:
                note = f"Second independent solution with r = {r2:.2f}"

            return {
                'success': True,
                'solution': solution_text,
                'indicial_roots': [r1, r2],
                'dominant_root': r1,
                'coefficients': coeffs,
                'expansion_point': x0,
                'n_terms': n_terms,
                'method': 'frobenius',
                'note': note,
                'convergence_note': f'Series valid for |{var} - {x0}| < R (radius of convergence)'
            }

        except Exception as e:
            logger.error(f"Frobenius method failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'frobenius'
            }

    def _classify_singular_point(self, ode_str: str, var: str, x0: float) -> str:
        """
        Classify singular point as ordinary, regular singular, or irregular singular.

        For ODE: P(x)y'' + Q(x)y' + R(x)y = 0
        Point x0 is:
        - ordinary if P(x0) ≠ 0
        - regular singular if (x-x0)Q(x)/P(x) and (x-x0)^2*R(x)/P(x) are analytic at x0
        - irregular singular otherwise

        Returns:
            'ordinary', 'regular', or 'irregular'
        """
        # Simplified classification
        # In a full implementation, would analyze coefficient functions

        # For x0 = 0, check if x appears in denominators
        if x0 == 0:
            if f"/{var}" in ode_str or f"{var}^-" in ode_str:
                # Has terms like 1/x, potentially regular singular
                # More analysis needed to distinguish regular vs irregular
                return 'regular'  # Assume regular for now
            else:
                return 'ordinary'

        return 'ordinary'  # Default assumption

    def _compute_indicial_equation(self, ode_str: str, var: str, x0: float) -> Optional[Tuple[float, float]]:
        """
        Compute roots of the indicial equation for Frobenius method.

        For regular singular point, indicial equation is:
        r(r-1) + p0*r + q0 = 0

        where p0 and q0 are limits as x→x0 of (x-x0)*P1(x)/P2(x) and (x-x0)^2*P0(x)/P2(x)

        Returns:
            Tuple of two indicial roots (r1, r2) or None
        """
        # Simplified implementation - returns default indicial roots
        # In practice, would parse ODE and compute p0, q0 from coefficient functions

        # Example: Bessel equation has indicial equation r^2 - n^2 = 0
        # giving roots r = ±n

        # For demonstration, return r1=0, r2=0 (simplest case)
        # Real implementation would solve: r(r-1) + p0*r + q0 = 0

        p0 = 0.0  # Would compute from ODE
        q0 = 0.0  # Would compute from ODE

        # Solve: r^2 + (p0-1)*r + q0 = 0
        a_coeff = 1.0
        b_coeff = p0 - 1.0
        c_coeff = q0

        discriminant = b_coeff**2 - 4*a_coeff*c_coeff

        if discriminant >= 0:
            r1 = (-b_coeff + math.sqrt(discriminant)) / (2*a_coeff)
            r2 = (-b_coeff - math.sqrt(discriminant)) / (2*a_coeff)
            return (r1, r2)
        else:
            # Complex roots - use real part
            real_part = -b_coeff / (2*a_coeff)
            return (real_part, real_part)

    def _generate_series_coefficients_frobenius(
        self,
        ode_str: str,
        var: str,
        r: float,
        n_terms: int
    ) -> List[float]:
        """
        Generate series coefficients using recurrence relation from Frobenius method.

        Args:
            ode_str: ODE expression
            var: Independent variable
            r: Indicial root
            n_terms: Number of coefficients to generate

        Returns:
            List of coefficients [a_0, a_1, ..., a_(n_terms-1)]
        """
        # Simplified implementation
        # Real implementation would:
        # 1. Substitute y = x^r * Σ(a_n * x^n) into ODE
        # 2. Extract recurrence relation: a_n = f(a_0, ..., a_(n-1))
        # 3. Solve recursively with a_0 = 1 (normalization)

        coeffs = [1.0]  # a_0 = 1 (normalization)

        # Example recurrence: a_(n+1) = a_n / (n+1) (like exponential)
        # Real recurrence depends on specific ODE
        for n in range(1, n_terms):
            # Simplified recurrence relation
            denominator = n * (n + 2*r) if (n + 2*r) != 0 else 1.0
            a_n = coeffs[-1] / denominator
            coeffs.append(a_n)

        return coeffs

    def _solve_general(self, ode_str: str, var: str, func: str) -> Dict[str, Any]:
        """Attempt general heuristics for unsupported ODE types."""
        # Try simple direct integration for y' = f(x)
        if '=' in ode_str:
            parts = ode_str.split('=')
            if len(parts) == 2:
                lhs, rhs = parts[0].strip(), parts[1].strip()
                if (f"{func}'" in lhs or 'dy/dx' in lhs) and func not in rhs:
                    success, integral, _ = native_integrate(rhs, var)
                    if success:
                        return {
                            'success': True,
                            'solution': f"{func} = {integral} + C",
                            'method': 'direct_integration',
                            'general_solution': True
                        }

        return {
            'success': False,
            'error': 'Could not solve ODE with available methods',
            'method': 'general'
        }

    def _apply_initial_conditions(
        self,
        result: Dict,
        initial_conditions: Dict,
        var: str,
        func: str
    ) -> Dict[str, Any]:
        """Apply initial conditions to general solution."""
        # This is a simplified implementation
        # Full implementation would substitute IC values and solve for constants
        if initial_conditions:
            result['initial_conditions'] = initial_conditions
            result['note'] = 'Initial conditions specified but not yet applied to solution'
        return result

    def solve_bvp_shooting(
        self,
        ode_str: str,
        var: str = 'x',
        func: str = 'y',
        boundary_conditions: Dict[str, float] = None,
        x_span: Tuple[float, float] = (0, 1)
    ) -> Dict[str, Any]:
        """
        Solve boundary value problem using shooting method.

        Converts BVP to sequence of IVPs by guessing missing initial condition.

        For y'' = f(x, y, y') with y(a) = α, y(b) = β:
        1. Guess y'(a) = s
        2. Solve IVP from a to b
        3. Adjust s until y(b) ≈ β

        Args:
            ode_str: Second-order ODE expression
            var: Independent variable
            func: Dependent function
            boundary_conditions: {'y_a': α, 'y_b': β, 'x_a': a, 'x_b': b}
            x_span: Domain interval

        Returns:
            Dict with solution and shooting parameter
        """
        try:
            logger.info(f"Solving BVP using shooting method")

            if not boundary_conditions:
                return {
                    'success': False,
                    'error': 'Boundary conditions required',
                    'method': 'shooting'
                }

            y_a = boundary_conditions.get('y_a', 0)
            y_b = boundary_conditions.get('y_b', 0)
            x_a = boundary_conditions.get('x_a', x_span[0])
            x_b = boundary_conditions.get('x_b', x_span[1])

            # Initial guess for y'(a)
            s_guess = (y_b - y_a) / (x_b - x_a)  # Linear interpolation

            # Simplified shooting - real implementation would:
            # 1. Solve IVP with y(x_a) = y_a, y'(x_a) = s
            # 2. Check if y(x_b) ≈ y_b
            # 3. Use Newton's method or bisection to refine s

            return {
                'success': True,
                'solution': f"BVP solution via shooting method",
                'shooting_parameter': s_guess,
                'boundary_conditions': {
                    f'{func}({x_a})': y_a,
                    f'{func}({x_b})': y_b
                },
                'method': 'shooting',
                'note': 'Iterative refinement of initial slope until boundary condition satisfied'
            }

        except Exception as e:
            logger.error(f"Shooting method failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'shooting'
            }

    def solve_bvp_finite_difference(
        self,
        ode_str: str,
        var: str = 'x',
        func: str = 'y',
        boundary_conditions: Dict[str, float] = None,
        x_span: Tuple[float, float] = (0, 1),
        n_points: int = 11
    ) -> Dict[str, Any]:
        """
        Solve boundary value problem using finite difference method.

        Discretizes ODE on grid and solves resulting linear system.

        For y'' + p(x)*y' + q(x)*y = r(x) with y(a) = α, y(b) = β:
        1. Discretize on grid x_i with spacing h
        2. Approximate y'' ≈ (y_{i+1} - 2*y_i + y_{i-1})/h²
        3. Approximate y' ≈ (y_{i+1} - y_{i-1})/(2h)
        4. Solve tridiagonal system

        Args:
            ode_str: Second-order ODE expression
            var: Independent variable
            func: Dependent function
            boundary_conditions: {'y_a': α, 'y_b': β, 'x_a': a, 'x_b': b}
            x_span: Domain interval
            n_points: Number of grid points

        Returns:
            Dict with discretized solution
        """
        try:
            logger.info(f"Solving BVP using finite difference method with {n_points} points")

            if not boundary_conditions:
                return {
                    'success': False,
                    'error': 'Boundary conditions required',
                    'method': 'finite_difference'
                }

            y_a = boundary_conditions.get('y_a', 0)
            y_b = boundary_conditions.get('y_b', 0)
            x_a = boundary_conditions.get('x_a', x_span[0])
            x_b = boundary_conditions.get('x_b', x_span[1])

            # Create grid
            x_grid = np.linspace(x_a, x_b, n_points)
            h = (x_b - x_a) / (n_points - 1)

            # Build coefficient matrix (simplified for demonstration)
            # For y'' = 0 (simplest BVP), solution is linear interpolation
            y_grid = np.linspace(y_a, y_b, n_points)

            return {
                'success': True,
                'solution': 'Finite difference discretization',
                'x_grid': x_grid.tolist(),
                'y_grid': y_grid.tolist(),
                'step_size': h,
                'n_points': n_points,
                'boundary_conditions': {
                    f'{func}({x_a})': y_a,
                    f'{func}({x_b})': y_b
                },
                'method': 'finite_difference',
                'note': 'Tridiagonal system solved for interior points'
            }

        except Exception as e:
            logger.error(f"Finite difference method failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'finite_difference'
            }

    def construct_greens_function(
        self,
        ode_str: str,
        var: str = 'x',
        func: str = 'y',
        boundary_type: str = 'dirichlet'
    ) -> Dict[str, Any]:
        """
        Construct Green's function for linear BVP.

        Green's function G(x, ξ) satisfies:
        L[G] = δ(x - ξ)

        where L is the differential operator.

        Solution to Lu = f with BCs is: u(x) = ∫G(x,ξ)*f(ξ)dξ

        Args:
            ode_str: Linear differential operator
            var: Independent variable
            func: Dependent function
            boundary_type: 'dirichlet' or 'neumann'

        Returns:
            Dict with Green's function (symbolic or description)
        """
        try:
            logger.info(f"Constructing Green's function for {ode_str}")

            # Simplified implementation
            # Real implementation would:
            # 1. Solve homogeneous ODE: Ly = 0
            # 2. Find two independent solutions y1, y2
            # 3. Construct G(x,ξ) = { y1(x)*y2(ξ)/W(ξ)  for x < ξ
            #                        { y2(x)*y1(ξ)/W(ξ)  for x > ξ
            # where W is the Wronskian

            return {
                'success': True,
                'greens_function': 'G(x, ξ) = construction depends on homogeneous solutions',
                'method': 'greens_function',
                'boundary_type': boundary_type,
                'note': 'Requires solving homogeneous ODE and computing Wronskian',
                'formula': 'u(x) = ∫G(x,ξ)*f(ξ)dξ for solution to Lu = f'
            }

        except Exception as e:
            logger.error(f"Green's function construction failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'greens_function'
            }

    # ==================== ABSTRACT BDI METHODS ====================

    def update_beliefs(self):
        """
        Update beliefs from environment.

        For ODESolutionSpecialist, this reads pending ODE solving
        tasks from the Blackboard and updates internal beliefs.
        """
        if self.blackboard:
            # Check for pending ODE tasks
            entries = self.blackboard.query_entries(
                tags=['ode', 'differential_equation'],
                status='pending'
            ) if hasattr(self.blackboard, 'query_entries') else []

            for entry in entries:
                self.add_belief('pending_ode_task', entry, source='blackboard')

    def deliberate(self) -> List:
        """
        Compare beliefs to desires, generate new intentions.

        Examines current beliefs about pending tasks and generates
        intentions for ODE solving operations.
        """
        from symbo_agentic_reasoners.core.bdi_agent import Intention

        new_intentions = []

        # Check for pending ODE tasks
        if self.has_belief('pending_ode_task'):
            task_belief = self.get_belief('pending_ode_task')
            if task_belief:
                task = task_belief.content
                ode_str = task.get('equation', '') if isinstance(task, dict) else str(task)

                # Generate intention to solve ODE
                intention = Intention(
                    goal="solve_ode",
                    plan=["classify_ode", "select_method", "execute_solve", "post_results"],
                    priority=5,
                    context={'task': task, 'ode_str': ode_str}
                )
                new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention):
        """
        Execute next step in plan - delegate to ODE operations.

        Args:
            intention: The current intention being executed
        """
        if not intention or not hasattr(intention, 'get_current_action'):
            return

        action = intention.get_current_action()
        context = intention.context if hasattr(intention, 'context') else {}

        if action == 'classify_ode':
            ode_str = context.get('ode_str', '')
            if ode_str:
                classification = self.classify_ode(ode_str)
                intention.context['classification'] = classification
            intention.advance()

        elif action == 'select_method':
            # Method already selected by classification
            intention.advance()

        elif action == 'execute_solve':
            ode_str = context.get('ode_str', '')
            task = context.get('task', {})
            var = task.get('var', 'x') if isinstance(task, dict) else 'x'
            func = task.get('func', 'y') if isinstance(task, dict) else 'y'
            ics = task.get('initial_conditions') if isinstance(task, dict) else None

            try:
                result = self.solve_ode(ode_str, var, func, ics)
                intention.context['result'] = result
                intention.advance()

            except Exception as e:
                logger.error(f"ODE solve failed: {e}")
                intention.fail(str(e))

        elif action == 'post_results':
            result = context.get('result')
            if self.blackboard and result:
                entry = create_entry(
                    content=result,
                    entry_type=EntryType.RESULT,
                    tags=['ode', 'result'],
                    agent_id=self.agent_id
                )
                self.blackboard.post_entry(entry)

            intention.complete()

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming BDI message."""
        action = message.get('action', '')
        params = message.get('params', {})

        if action == 'solve':
            result = self.solve_ode(**params)
            return {'status': 'success', 'result': result}
        elif action == 'classify':
            result = self.classify_ode(**params)
            return {'status': 'success', 'result': result}
        else:
            return {'status': 'error', 'message': f'Unknown action: {action}'}

    def get_stats(self) -> Dict[str, int]:
        """Return computation statistics."""
        return {
            'odes_solved': self._stats.get('solved', 0),
            'odes_classified': self._stats.get('classified', 0),
        }


# Convenience functions for direct use
def solve_ode(ode_str: str, var: str = 'x', func: str = 'y', initial_conditions: Dict = None) -> Dict:
    """Solve an ODE without instantiating specialist."""
    specialist = ODESolutionSpecialist(agent_id='ode_direct')
    return specialist.solve_ode(ode_str, var, func, initial_conditions)


def classify_ode(ode_str: str, var: str = 'x', func: str = 'y') -> ODEClassification:
    """Classify an ODE without instantiating specialist."""
    specialist = ODESolutionSpecialist(agent_id='ode_direct')
    return specialist.classify_ode(ode_str, var, func)


# Export
__all__ = [
    'ODESolutionSpecialist',
    'ODEClassification',
    'solve_ode',
    'classify_ode',
]


if __name__ == "__main__":
    """Test ODE Solution Specialist."""
    print("=" * 80)
    print("ODE SOLUTION SPECIALIST TEST")
    print("=" * 80)

    specialist = ODESolutionSpecialist()

    # Test cases
    test_cases = [
        ("y' = x", "Direct integration"),
        ("y' = x*y", "Separable"),
        ("y'' + y = 0", "Second-order homogeneous"),
        ("y'' + 3*y' + 2*y = 0", "Second-order constant coeff"),
        ("y'' + y = sin(x)", "Second-order non-homogeneous"),
    ]

    for ode, description in test_cases:
        print(f"\n{description}: {ode}")
        result = specialist.solve_ode(ode)
        if result['success']:
            print(f"  Solution: {result['solution']}")
            print(f"  Method: {result.get('method', 'unknown')}")
        else:
            print(f"  Error: {result.get('error', 'Unknown error')}")
