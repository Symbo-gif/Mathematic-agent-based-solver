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
Solver Engine Core
==================

Main solver engine class that orchestrates the solving pipeline.
Uses lazy loading of specialists and native mathematical reasoning.
"""

import logging
import time
import re
from typing import Any, Dict, Optional

from .result import SolveStatus, SolveResult
from .safety_checker import check_expression_safety
from .router import SpecialistRouter, get_specialist_key

# NO SYMPY - Use native symbolic module
from symbo_agentic_reasoners.core.native_symbolic import (
    Expr, Symbol, Integer, Float, Rational,
    Add, Mul, Pow, Sin, Cos, Tan, Exp, Log, Sqrt,
    parse_expr, sympify, symbols, diff as native_diff, simplify as native_simplify
)
from symbo_agentic_reasoners.core.calculus import (
    differentiate, integrate as native_integrate, native_limit,
    definite_integrate
)

from symbo_agentic_reasoners.core.safe_parser import safe_sympify, SecurityError
from symbo_agentic_reasoners.core.expression_analyzer import analyze_expression, ExpressionCategory
from symbo_agentic_reasoners.infrastructure.watchdog import (
    run_with_timeout, TimeoutError as WatchdogTimeoutError, get_watchdog
)
from symbo_agentic_reasoners.core.number_theory_native import (
    mobius, mangoldt, totient, divisor_sigma, liouville,
    prime_product, number_theoretic_sum, evaluate_nt_series,
    detect_nt_series_pattern, alternating_log_series,
    EULER_GAMMA, STIELTJES_CONSTANTS
)

logger = logging.getLogger(__name__)


class SolverEngine:
    """
    Direct solver engine for mathematical problems.

    Provides a streamlined solve pipeline that:
    1. Parses natural language input to SymPy expressions
    2. Classifies problem type and domain
    3. Routes to appropriate specialist agent
    4. Returns result immediately (no verification polling)

    Specialists are initialized lazily to minimize resource usage.
    Timeout protection via Watchdog prevents hung operations.
    """

    # Default timeouts for different operation types (seconds)
    DEFAULT_TIMEOUTS = {
        'derivative': 30,
        'diff': 30,
        'differentiate': 30,
        'integral': 90,      # Integration can be slow
        'integrate': 90,
        'dsolve': 120,       # ODEs can be complex
        'ode': 120,
        'solve': 60,         # Equation solving
        'factor': 45,
        'expand': 30,
        'simplify': 45,
        'limit': 60,
        'series': 45,
        'compute': 30,
        'default': 60,
    }

    def __init__(self, resource_coordinator=None, enable_timeouts: bool = True):
        """
        Initialize the solver engine.

        Args:
            resource_coordinator: Optional ResourceCoordinator for hardware-aware scheduling
            enable_timeouts: Whether to enforce operation timeouts (default True)
        """
        self._coordinator = resource_coordinator
        self._enable_timeouts = enable_timeouts

        # Specialist router (lazy-loaded specialists)
        self._router = SpecialistRouter()

        # Problem analysis team (lazy init)
        self._analysis_team = None

        # Environment for variable storage (name -> expression result)
        self._environment: Dict[str, str] = {}

        # Statistics
        self._problems_solved = 0
        self._problems_failed = 0
        self._problems_timed_out = 0
        self._total_solve_time_ms = 0.0

        # Start watchdog if timeouts enabled
        if self._enable_timeouts:
            watchdog = get_watchdog()
            watchdog.start()

        logger.info(f"SolverEngine initialized (timeouts={'enabled' if enable_timeouts else 'disabled'})")

    def solve(self, problem: str) -> SolveResult:
        """
        Solve a mathematical problem.

        Args:
            problem: Natural language or mathematical expression

        Returns:
            SolveResult with solution or error
        """
        start_time = time.time()

        try:
            # Step 0a: Check expression safety (prevent DoS via deeply nested expressions)
            is_safe, safety_error = check_expression_safety(problem)
            if not is_safe:
                return SolveResult(
                    status=SolveStatus.FAILED,
                    error=f"Expression rejected: {safety_error}"
                )

            # Check hardware if coordinator available
            if self._coordinator and not self._coordinator.can_proceed_with_task():
                return SolveResult(
                    status=SolveStatus.FAILED,
                    error="System resources exhausted - please wait"
                )

            # Step 0: Substitute known variables from environment
            substituted_problem = self._substitute_environment(problem)

            # Step 1: Parse and classify
            structured = self._parse_and_classify(substituted_problem)
            if structured is None:
                return SolveResult(
                    status=SolveStatus.FAILED,
                    error="Failed to parse problem"
                )

            # Step 2: Route to specialist
            operation = structured.metadata.get('operation', 'compute')
            domain = structured.domain.value.lower()

            result = self._route_and_solve(structured, domain, operation)

            # Step 3: Store in environment if this is an assignment
            assignment_target = structured.metadata.get('assignment_target')
            if assignment_target and result.status == SolveStatus.SUCCESS and result.result:
                self._environment[assignment_target] = result.result
                logger.debug(f"Stored {assignment_target} = {result.result} in environment")

            # Update stats
            solve_time = (time.time() - start_time) * 1000
            result.solve_time_ms = solve_time
            result.problem_type = structured.problem_type.value
            result.domain = domain
            result.operation = operation

            if result.status == SolveStatus.SUCCESS:
                self._problems_solved += 1
            else:
                self._problems_failed += 1
            self._total_solve_time_ms += solve_time

            return result

        except Exception as e:
            logger.exception(f"Solve failed for: {problem}")
            self._problems_failed += 1
            return SolveResult(
                status=SolveStatus.FAILED,
                error=str(e),
                solve_time_ms=(time.time() - start_time) * 1000
            )

    def solve_expression(self, expr_str: str, operation: str = 'compute',
                        variable: str = 'x') -> SolveResult:
        """
        Solve a direct mathematical expression (bypasses NLP parsing).

        Args:
            expr_str: SymPy-compatible expression string
            operation: Operation to perform (derivative, integral, solve, factor, etc.)
            variable: Variable for calculus operations

        Returns:
            SolveResult with solution
        """
        start_time = time.time()

        try:
            # Parse expression safely (prevents code injection)
            expr = safe_sympify(expr_str)

            # Route based on operation
            result = self._solve_direct(expr, operation, variable)

            result.solve_time_ms = (time.time() - start_time) * 1000
            result.operation = operation

            if result.status == SolveStatus.SUCCESS:
                self._problems_solved += 1
            else:
                self._problems_failed += 1

            return result

        except Exception as e:
            logger.exception(f"Direct solve failed: {expr_str}")
            self._problems_failed += 1
            return SolveResult(
                status=SolveStatus.FAILED,
                error=str(e),
                solve_time_ms=(time.time() - start_time) * 1000
            )

    def _parse_and_classify(self, problem: str):
        """Parse and classify problem using ProblemAnalysisTeam."""
        if self._analysis_team is None:
            from symbo_agentic_reasoners.agents.base.problem_analysis import (
                ProblemAnalysisTeam
            )
            self._analysis_team = ProblemAnalysisTeam()

        try:
            return self._analysis_team.process(problem)
        except Exception as e:
            logger.warning(f"Parse failed: {e}")
            return None

    def _route_and_solve(self, structured, domain: str, operation: str) -> SolveResult:
        """Route to appropriate specialist and solve."""
        # Import specialized solvers (lazy)
        from .specialized_solvers import (
            solve_diophantine, solve_determinant, solve_limit_native,
            solve_nt_series
        )

        # Get sympy expression
        expr = structured.sympy_expr
        variable = structured.metadata.get('variable', 'x')
        raw_input = structured.raw_input if hasattr(structured, 'raw_input') else ""

        # Special handling for diophantine equations
        if operation == 'diophantine':
            return solve_diophantine(raw_input, self)

        # Early check for sum-of-cubes equations (x**3 + y**3 + z**3 = n)
        eq_str_nospace = raw_input.replace(' ', '')
        cube_early_match = re.match(
            r'^(\w+)\*\*3\+(\w+)\*\*3\+(\w+)\*\*3=(\d+)$', eq_str_nospace
        )
        if cube_early_match:
            from .specialized_solvers import solve_sum_of_cubes
            target = int(cube_early_match.group(4))
            cube_solutions = solve_sum_of_cubes(target)
            if cube_solutions:
                return SolveResult(
                    status=SolveStatus.SUCCESS,
                    result=str(cube_solutions),
                    specialist_used="sum_of_cubes_solver",
                    metadata={'equation': raw_input, 'target': target}
                )

        # Special handling for determinant
        if operation == 'determinant':
            return solve_determinant(raw_input)

        # Special handling for limits - use native limit engine exclusively
        if operation == 'limit':
            return solve_limit_native(structured)

        # Special handling for number-theoretic series
        if operation in ('nt_series', 'number_theory_series'):
            return solve_nt_series(raw_input)

        # Check if summation contains NT functions (mobius, mangoldt, totient, etc.)
        if operation in ('summation', 'product', 'series'):
            raw_lower = raw_input.lower()
            if any(nt_func in raw_lower for nt_func in ['mu(', 'mobius(', 'lambda(', 'mangoldt(',
                                                          'phi(', 'totient(', 'prime']):
                return solve_nt_series(raw_input)

        # Determine specialist key
        specialist_key = get_specialist_key(domain, operation)

        # Get or create specialist
        specialist = self._router.get_specialist(specialist_key, domain, operation)

        if specialist is None:
            # Fallback to direct native computation
            return self._solve_native(expr, operation, variable, raw_input)

        # Use specialist
        try:
            # Create a minimal task entry for the specialist
            task_metadata = {
                'operation': operation,
                'raw_input': structured.raw_input,
                'sympy_expr': str(expr) if expr is not None else None,
                'variable': variable,
                'expression': structured.metadata.get('expression')
            }

            # Add definite integral bounds if present
            if structured.metadata.get('is_definite'):
                task_metadata['is_definite'] = True
                task_metadata['lower_bound'] = structured.metadata.get('lower_bound')
                task_metadata['upper_bound'] = structured.metadata.get('upper_bound')

            # Add summation/product bounds if present
            if 'start' in structured.metadata:
                task_metadata['start'] = structured.metadata.get('start')
            if 'end' in structured.metadata:
                task_metadata['end'] = structured.metadata.get('end')

            task_entry = _MinimalTaskEntry(
                metadata=task_metadata,
                conversation_id=f"solve_{self._problems_solved}"
            )

            result_entry = specialist.process(task_entry)

            # Extract result
            result_str = None
            if result_entry is not None:
                if hasattr(result_entry, 'metadata') and result_entry.metadata:
                    result_str = result_entry.metadata.get('result_str') or result_entry.metadata.get('result')
                    if not result_str and hasattr(result_entry, 'content'):
                        result_str = str(result_entry.content)
                elif hasattr(result_entry, 'content'):
                    result_str = str(result_entry.content)
                else:
                    result_str = str(result_entry)

            # Validate result
            if result_str and result_str not in ('None', 'none', ''):
                return SolveResult(
                    status=SolveStatus.SUCCESS,
                    result=result_str,
                    specialist_used=specialist_key
                )
            else:
                # Specialist returned empty - fallback to native
                logger.debug(f"Specialist {specialist_key} returned empty, falling back to native")
                return self._solve_native(expr, operation, variable, raw_input)

        except Exception as e:
            logger.warning(f"Specialist {specialist_key} failed: {e}")
            # Fallback to direct native computation
            return self._solve_native(expr, operation, variable, raw_input)

    def _solve_mixed_quartic(self, coeffs: tuple, target: int, search_range: int = 20) -> set:
        """
        Solve mixed quartic-quadratic Diophantine equation.

        ax⁴ + by⁴ + cz⁴ + dw² = target

        Args:
            coeffs: Tuple (a, b, c, d) of coefficients
            target: Target value
            search_range: Maximum search range

        Returns:
            Set of (x, y, z, w) solution tuples
        """
        from .specialized_solvers import solve_mixed_quartic
        return solve_mixed_quartic(coeffs, target, search_range)

    def _solve_sum_of_cubes(self, target: int, search_range: int = 500) -> set:
        """
        Find solutions to x³ + y³ + z³ = target.

        Args:
            target: Target sum of cubes
            search_range: Maximum search range

        Returns:
            Set of (x, y, z) solution tuples
        """
        from .specialized_solvers import solve_sum_of_cubes
        return solve_sum_of_cubes(target, search_range)

    def _solve_quaternary_quadratic(self, coeffs: tuple, target: int, search_range: int = 100) -> set:
        """
        Find solutions to a*x² + b*y² + c*z² + d*w² = target.

        Args:
            coeffs: Tuple (a, b, c, d) of coefficients
            target: Target value
            search_range: Maximum search range

        Returns:
            Set of (x, y, z, w) solution tuples
        """
        from .specialized_solvers import solve_quaternary_quadratic
        return solve_quaternary_quadratic(coeffs, target, search_range)

    def _solve_mordell_curve(self, k: int, search_range: int = 1000) -> set:
        """
        Find integer solutions to y² = x³ + k (Mordell curve).

        Args:
            k: Constant in the Mordell curve equation
            search_range: Maximum search range

        Returns:
            Set of (x, y) solution tuples
        """
        from .specialized_solvers import solve_mordell_curve
        return solve_mordell_curve(k, search_range)

    def _solve_direct(self, expr, operation: str, variable: str) -> SolveResult:
        """Direct solve using native engine (fast path)."""
        return self._solve_native(expr, operation, variable)

    def _solve_native(self, expr, operation: str, variable: str, raw_input: str = "") -> SolveResult:
        """
        Direct native computation without specialist agents.

        NO SYMPY - Pure native mathematical reasoning.
        """
        try:
            # Convert expr to string for native processing
            expr_str = str(expr) if expr is not None else raw_input

            if not expr_str or expr_str == 'None':
                # Try expression analysis mode
                if raw_input:
                    analysis_result = analyze_expression(raw_input)
                    if analysis_result.success:
                        category = analysis_result.category

                        # For matrix expressions like det(eye(n)), return the known result
                        if category == ExpressionCategory.MATRIX_DETERMINANT:
                            return SolveResult(
                                status=SolveStatus.SUCCESS,
                                result=analysis_result.simplified,
                                specialist_used="expression_analyzer.matrix",
                                metadata={
                                    'category': category.value,
                                    'description': analysis_result.description
                                }
                            )

                        # For probability expressions, return analysis
                        if category in (ExpressionCategory.PROBABILITY_PMF,
                                       ExpressionCategory.PROBABILITY_PDF,
                                       ExpressionCategory.PROBABILITY_MGF,
                                       ExpressionCategory.PROBABILITY_PGF,
                                       ExpressionCategory.PROBABILITY_CGF,
                                       ExpressionCategory.PROBABILITY_EXPECTATION):
                            desc = analysis_result.description
                            if analysis_result.distribution:
                                desc = f"{analysis_result.distribution}: {desc}"
                            return SolveResult(
                                status=SolveStatus.SUCCESS,
                                result=f"{analysis_result.simplified} [{desc}]",
                                specialist_used="expression_analyzer.probability",
                                metadata={
                                    'category': category.value,
                                    'distribution': analysis_result.distribution,
                                    'description': analysis_result.description
                                }
                            )

                        # For physics expressions, return analysis
                        if category in (ExpressionCategory.PHYSICS_DAMPED_OSCILLATOR,
                                       ExpressionCategory.PHYSICS_WAVE,
                                       ExpressionCategory.PHYSICS_DECAY):
                            return SolveResult(
                                status=SolveStatus.SUCCESS,
                                result=f"{analysis_result.simplified} [{analysis_result.description}]",
                                specialist_used="expression_analyzer.physics",
                                metadata={
                                    'category': category.value,
                                    'description': analysis_result.description
                                }
                            )

                        # For diophantine, route to native solver
                        if category == ExpressionCategory.DIOPHANTINE:
                            from .specialized_solvers import solve_diophantine
                            return solve_diophantine(raw_input, self)

                        # For pure expressions, return simplified form
                        if category == ExpressionCategory.PURE_EXPRESSION:
                            return SolveResult(
                                status=SolveStatus.SUCCESS,
                                result=analysis_result.simplified,
                                specialist_used="expression_analyzer.simplify",
                                metadata={
                                    'category': category.value,
                                    'description': analysis_result.description
                                }
                            )

                # No raw input or analysis didn't help
                return SolveResult(
                    status=SolveStatus.FAILED,
                    error="No expression to solve"
                )

            var_name = variable if variable else 'x'

            # Get timeout for this operation type
            timeout = self.DEFAULT_TIMEOUTS.get(operation, self.DEFAULT_TIMEOUTS['default'])

            # Execute with timeout protection if enabled
            if self._enable_timeouts:
                try:
                    result = run_with_timeout(
                        self._execute_native_operation,
                        timeout,
                        expr_str, operation, var_name,
                        raise_on_timeout=True
                    )
                except WatchdogTimeoutError:
                    self._problems_timed_out += 1
                    logger.warning(f"Native operation '{operation}' timed out after {timeout}s")
                    return SolveResult(
                        status=SolveStatus.TIMEOUT,
                        error=f"Operation '{operation}' timed out after {timeout}s",
                        operation=operation
                    )
            else:
                result = self._execute_native_operation(expr_str, operation, var_name)

            return SolveResult(
                status=SolveStatus.SUCCESS,
                result=str(result),
                specialist_used="native_direct"
            )

        except Exception as e:
            return SolveResult(
                status=SolveStatus.FAILED,
                error=f"Native computation failed: {e}"
            )

    def _execute_native_operation(self, expr_str: str, operation: str, var_name: str) -> Any:
        """
        Execute the actual mathematical operation using native modules.

        NO SYMPY - Pure native mathematical reasoning.
        """
        if operation in ['derivative', 'diff', 'differentiate']:
            success, result, method = differentiate(expr_str, var_name)
            if success:
                return result
            return f"Could not differentiate: {expr_str}"

        elif operation in ['integral', 'integrate']:
            success, result, method = native_integrate(expr_str, var_name)
            if success:
                return result
            return f"Could not integrate: {expr_str}"

        elif operation == 'solve':
            from symbo_agentic_reasoners.core.calculus import solve_polynomial
            solutions = solve_polynomial(expr_str, var_name)
            return solutions if solutions else "No solutions found"

        elif operation == 'solve_system':
            if isinstance(expr_str, list):
                from symbo_agentic_reasoners.core.calculus import solve_system_native
                solutions = solve_system_native(expr_str)
                return solutions if solutions else "No solutions found"
            else:
                from symbo_agentic_reasoners.core.calculus import solve_polynomial
                solutions = solve_polynomial(expr_str, var_name)
                return solutions if solutions else "No solutions found"

        elif operation == 'factor':
            from symbo_agentic_reasoners.core.calculus import factor_polynomial
            success, result = factor_polynomial(expr_str)
            if success:
                return result
            return expr_str

        elif operation == 'expand':
            from symbo_agentic_reasoners.core.calculus import expand_expression
            success, result = expand_expression(expr_str)
            if success:
                return result
            return expr_str

        elif operation == 'simplify':
            try:
                expr = parse_expr(expr_str)
                return str(expr.simplify())
            except:
                return expr_str

        elif operation == 'limit':
            success, result, method = native_limit(expr_str, var_name, '0')
            if success:
                return result
            return f"Could not evaluate limit: {expr_str}"

        elif operation == 'series':
            from symbo_agentic_reasoners.core.calculus import taylor_series
            success, result = taylor_series(expr_str, var_name, point=0, n_terms=6)
            if success:
                return result
            return f"Could not compute series: {expr_str}"

        elif operation in ['dsolve', 'ode']:
            from symbo_agentic_reasoners.core.calculus import solve_ode_native
            success, result = solve_ode_native(expr_str)
            if success:
                return result
            return f"Could not solve ODE: {expr_str}"

        elif operation == 'compute':
            try:
                expr = parse_expr(expr_str)
                simplified = expr.simplify()
                try:
                    val = simplified.evalf()
                    if isinstance(val, (int, float)):
                        return val
                except:
                    pass
                return str(simplified)
            except:
                return expr_str

        else:
            # Unknown operation - try simplify
            try:
                expr = parse_expr(expr_str)
                return str(expr.simplify())
            except:
                return expr_str

    # ============ Environment Management ============

    def _substitute_environment(self, problem: str) -> str:
        """Substitute known variables from the environment into the problem string."""
        if not self._environment:
            return problem

        result = problem
        sorted_vars = sorted(self._environment.keys(), key=len, reverse=True)

        for var_name in sorted_vars:
            var_value = self._environment[var_name]
            pattern = rf'\b{re.escape(var_name)}\b'
            result = re.sub(pattern, f'({var_value})', result)

        return result

    def get_environment(self) -> Dict[str, str]:
        """Get a copy of the current environment."""
        return dict(self._environment)

    def clear_environment(self) -> None:
        """Clear all stored variables from the environment."""
        self._environment.clear()
        logger.debug("Environment cleared")

    def set_variable(self, name: str, value: str) -> None:
        """Manually set a variable in the environment."""
        self._environment[name] = value
        logger.debug(f"Set {name} = {value} in environment")

    # ============ Statistics ============

    def get_statistics(self) -> Dict[str, Any]:
        """Get solver statistics."""
        total = self._problems_solved + self._problems_failed + self._problems_timed_out
        return {
            'problems_solved': self._problems_solved,
            'problems_failed': self._problems_failed,
            'problems_timed_out': self._problems_timed_out,
            'total_problems': total,
            'success_rate': (self._problems_solved / total * 100) if total > 0 else 0.0,
            'timeout_rate': (self._problems_timed_out / total * 100) if total > 0 else 0.0,
            'avg_solve_time_ms': (self._total_solve_time_ms / total) if total > 0 else 0.0,
            'specialists_loaded': self._router.get_loaded_specialists(),
            'timeouts_enabled': self._enable_timeouts
        }

    def health_check(self) -> Dict[str, Any]:
        """Run health check on solver components."""
        checks = {
            'analysis_team': False,
            'native_symbolic': False,
            'native_calculus': False,
            'specialists': {}
        }

        # Check analysis team
        try:
            if self._analysis_team is None:
                from symbo_agentic_reasoners.agents.base.problem_analysis import (
                    ProblemAnalysisTeam
                )
                self._analysis_team = ProblemAnalysisTeam()
            checks['analysis_team'] = True
        except Exception as e:
            checks['analysis_team'] = str(e)

        # Check native symbolic module
        try:
            x = Symbol('x')
            expr = x ** 2
            result = expr.diff(x)
            checks['native_symbolic'] = True
        except Exception as e:
            checks['native_symbolic'] = str(e)

        # Check native calculus module
        try:
            success, result, method = differentiate('x**2', 'x')
            checks['native_calculus'] = success
        except Exception as e:
            checks['native_calculus'] = str(e)

        return checks


class _MinimalTaskEntry:
    """Minimal task entry for specialist processing."""

    def __init__(self, metadata: Dict[str, Any], conversation_id: str):
        self.metadata = metadata
        self.conversation_id = conversation_id
