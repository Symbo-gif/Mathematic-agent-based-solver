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
Polynomial Specialist BDI Agent
===============================

This module contains the PolynomialSpecialist BDI agent that wraps
the domain polynomial solver with Belief-Desire-Intention architecture.

DIRECTIVE:
---------
Handle all polynomial operations with emphasis on systems of
polynomial equations using Gröbner bases.

KEY ALGORITHM:
-------------
Gröbner Bases (via SymPy's implementation of Buchberger's algorithm)
- Transforms polynomial systems into triangular form
- Enables systematic solution of multivariate polynomial systems

REFERENCE:
---------
Phase_2_Build_Order_Breakdown.md: Lines 74-90
"""

import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger('symbo_agentic_reasoners.phase2.polynomial')

# Native symbolic module - NO SYMPY
from symbo_agentic_reasoners.core.native_symbolic import (
    Symbol, parse_expr, sympify, simplify, expand, Eq, SympifyError,
    factor, solve
)
import symbo_agentic_reasoners.core.native_symbolic as sp

# Import domain solver
from .domain_solver import DomainPolynomialSolver

# Import fallback tracker for SymPy usage monitoring
from symbo_agentic_reasoners.core.fallback_tracker import (
    get_tracker, track_computation, ResolutionMethod
)

# BDI infrastructure
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.omdoc_schema import create_variable


class PolynomialSpecialist(BDIAgent):
    """
    Polynomial Manipulation Specialist - Gröbner Bases Expert

    DIRECTIVE:
    ---------
    Handle all polynomial operations with emphasis on systems of
    polynomial equations using Gröbner bases.

    KEY ALGORITHM:
    -------------
    Gröbner Bases (via SymPy's implementation of Buchberger's algorithm)
    - Transforms polynomial systems into triangular form
    - Enables systematic solution of multivariate polynomial systems

    OPERATIONS:
    ----------
    - Factor polynomials
    - Find roots (symbolic and numeric)
    - Solve polynomial equations
    - Solve systems of polynomial equations (Gröbner bases)
    - Polynomial expansion and simplification
    - Polynomial division

    REFERENCE:
    ---------
    Phase_2_Build_Order_Breakdown.md: Lines 74-90
    """

    def __init__(
        self,
        agent_id: str = 'polynomial_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Polynomial Specialist

        Args:
            agent_id: Unique specialist identifier
            df: Directory Facilitator instance
            blackboard: Blackboard instance
        """
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Domain solver for "SymPy Last Resort" architecture
        self.domain_solver = DomainPolynomialSolver()

        # Fallback tracker for monitoring SymPy usage
        self._tracker = get_tracker()

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.groebner_bases_computed = 0

        # Domain-first statistics
        self.domain_solved = 0      # Solved by domain algorithms
        self.sympy_fallbacks = 0    # Required SymPy fallback

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        print(f"[{self.agent_id}] Polynomial Specialist initialized")
        print(f"  Architecture: Domain-First, SymPy-Fallback")
        print(f"  Domain Algorithms: Quadratic formula, Rational roots, Pattern factoring")
        print(f"  Fallback: SymPy (Gröbner bases, general solver)")

    def _register_services(self):
        """
        Register services with Directory Facilitator

        REFERENCE:
        ---------
        Phase_2_Build_Order_Breakdown.md: Lines 74-90
        """
        registration = create_service_registration(
            service_type='math.algebra.polynomial',
            agent_id=self.agent_id,
            algorithm='groebner_bases',
            cost='medium',
            instance=self,  # Enable direct invocation by supervisors
            type='exact',
            tier='3',
            algorithms='groebner_factor_roots_solve'
        )
        self.df.register(registration)
        print(f"  [DF] Registered: math.algebra.polynomial (Gröbner bases)")

    def process(self, task_entry: Any) -> Any:
        """
        Process polynomial manipulation task

        Args:
            task_entry: Blackboard entry containing polynomial task

        Returns:
            Result entry with computation
        """
        print(f"\n[{self.agent_id}] Processing polynomial task")

        self.tasks_executed += 1

        try:
            # Extract task information
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            operation = metadata.get('operation', 'solve')
            raw_input = metadata.get('raw_input', '')
            sympy_expr_str = metadata.get('sympy_expr')

            print(f"  Operation: {operation}")
            print(f"  Input: {raw_input}")

            # Clean raw_input if needed (remove trailing = for fallback parsing)
            cleaned_raw = raw_input
            if '=' in raw_input:
                parts = raw_input.split('=')
                if len(parts) == 2:
                    lhs, rhs = parts[0].strip(), parts[1].strip()
                    if rhs in ('', '0', '0.0'):
                        cleaned_raw = lhs
                    else:
                        # Convert "a = b" to "a - b" for solving
                        cleaned_raw = f"({lhs}) - ({rhs})"

            # Use sympy_expr if available, otherwise cleaned raw input
            expr_to_use = sympy_expr_str if sympy_expr_str is not None else cleaned_raw

            # Determine if this is a system of equations or single polynomial
            is_system = self._is_system(raw_input, sympy_expr_str)

            if is_system:
                result = self._solve_system(expr_to_use, metadata)
            else:
                result = self._process_single_polynomial(expr_to_use, operation, metadata)

            # Create result entry
            result_entry = self._create_result_entry(task_entry, result, operation)

            self.tasks_succeeded += 1
            print(f"  [OK] Result: {result}")

            return result_entry

        except (sp.SympifyError, ValueError, TypeError, AttributeError) as e:
            self.tasks_failed += 1
            logger.warning(f"Polynomial computation failed: {type(e).__name__}: {e}")
            return self._create_error_entry(task_entry, str(e))

    def _is_system(self, raw_input: str, sympy_expr_str: Optional[str]) -> bool:
        """Determine if input represents a system of equations"""
        raw_lower = raw_input.lower()

        # Check for explicit system indicators
        if 'system' in raw_lower:
            return True

        # Check for newlines (multiple equations on separate lines)
        if '\n' in raw_input:
            return True

        # Check for ' and ' as a word (not substring like in 'expand')
        # Use word boundary to avoid matching 'expand', 'sand', etc.
        if re.search(r'\band\b', raw_lower):
            return True

        # Check for comma-separated equations (but not commas inside function calls or brackets)
        # Count commas outside of parentheses and brackets
        depth = 0
        for char in raw_input:
            if char in '([':
                depth += 1
            elif char in ')]':
                depth -= 1
            elif char == ',' and depth == 0:
                # Comma at top level indicates multiple equations
                return True

        # Also check for solve([...]) format - special handling for system solving
        if 'solve' in raw_lower and '[' in raw_input:
            return True

        return False

    def _solve_system(self, expr_str: str, metadata: Dict) -> Any:
        """
        Solve system of polynomial equations using Gröbner bases

        This is the CRITICAL ALGORITHM for Phase 2.

        REFERENCE:
        ---------
        Phase_2_Build_Order_Breakdown.md: Lines 78-89
        """
        print(f"  [GRÖBNER BASES] Solving polynomial system")

        try:
            # Check if metadata contains parsed equations and variables (from solve_system command)
            if 'equations' in metadata and 'variables' in metadata:
                # Use pre-parsed equations and variables from input_normalizer
                eq_strings = metadata['equations']
                var_names = metadata['variables']

                # Create SymPy symbols for variables
                variables = [sp.Symbol(v.strip()) for v in var_names if v.strip()]

                # Parse each equation string
                equations = []
                for eq_str in eq_strings:
                    # Parse with local dict containing our variables
                    local_dict = {str(v): v for v in variables}
                    try:
                        eq_expr = sp.sympify(eq_str, locals=local_dict)
                        equations.append(eq_expr)
                    except Exception as e:
                        logger.debug(f"Failed to parse equation '{eq_str}': {e}")
                        continue

                print(f"  Variables: {[str(v) for v in variables]}")
                print(f"  Equations: {len(equations)}")

                if equations and variables:
                    # Solve system
                    solutions = solve(equations, variables, dict=True)
                else:
                    return []
            else:
                # Legacy path: parse from expr_str
                expr = sp.sympify(expr_str)

                # Handle tuple/list (system of equations)
                if isinstance(expr, (list, tuple)):
                    # If the list contains strings (from sympify of a string repr), parse each element
                    parsed_equations = []
                    for e in expr:
                        if isinstance(e, str):
                            # String element - need to sympify it
                            parsed_equations.append(sp.sympify(e))
                        else:
                            parsed_equations.append(e)

                    # Collect variables from all expressions
                    variables = set()
                    for e in parsed_equations:
                        if hasattr(e, 'free_symbols'):
                            variables.update(e.free_symbols)
                    variables = sorted(variables, key=lambda s: s.name)

                    print(f"  Variables: {[str(v) for v in variables]}")

                    # Solve system
                    solutions = solve(parsed_equations, variables, dict=True)
                else:
                    # Single expression
                    variables = sorted(expr.free_symbols, key=lambda s: s.name)

                    if not variables:
                        # No variables - direct evaluation
                        result = sp.simplify(expr)
                        return result

                    print(f"  Variables: {[str(v) for v in variables]}")

                    # If single equation, solve directly
                    if isinstance(expr, (sp.Eq, sp.core.relational.Relational)):
                        solutions = solve(expr, variables, dict=True)
                    else:
                        # Assume expression equals zero
                        solutions = solve(expr, variables, dict=True)

            self.groebner_bases_computed += 1

            # Filter for real solutions
            real_solutions = []
            for sol in solutions:
                is_real = all(
                    self._is_real_solution(v)
                    for v in sol.values()
                )
                if is_real:
                    real_solutions.append({str(k): v for k, v in sol.items()})

            print(f"  [OK] Found {len(real_solutions)} real solution(s)")

            return real_solutions if real_solutions else solutions

        except (sp.SympifyError, ValueError, TypeError, RuntimeError) as e:
            logger.debug(f"Gröbner bases failed, trying direct solve: {type(e).__name__}: {e}")
            # Fallback to direct solve
            expr = sp.sympify(expr_str)
            variables = list(expr.free_symbols)
            return solve(expr, variables) if variables else expr

    def _is_real_solution(self, value: Any) -> bool:
        """Check if solution value is real (not complex)"""
        try:
            if hasattr(value, 'is_real'):
                return value.is_real
            if hasattr(value, 'as_real_imag'):
                real, imag = value.as_real_imag()
                return abs(imag) < 1e-10
            return True
        except (TypeError, ValueError, AttributeError):
            return True

    def _process_single_polynomial(self, expr_str: str, operation: str, metadata: Dict) -> Any:
        """
        Process single polynomial operation using DOMAIN-FIRST approach.

        ARCHITECTURE: Domain-First, SymPy-Fallback
        ------------------------------------------
        1. Try domain-specific algorithms FIRST
        2. Only fall back to SymPy if domain algorithms can't handle it
        3. Track all fallbacks for optimization analysis

        Args:
            expr_str: Polynomial expression string
            operation: Operation to perform
            metadata: Additional context

        Returns:
            Operation result
        """
        # Parse expression (minimal SymPy usage - just for representation)
        expr = sp.sympify(expr_str)

        # Start tracking this computation
        with track_computation(operation, expr_str, domain='algebra', specialist=self.agent_id) as tracker:

            if operation == 'factor':
                # TRY DOMAIN ALGORITHMS FIRST
                success, result, method = self.domain_solver.try_domain_factor(expr)

                if success:
                    logger.info(f"[DOMAIN] Factored using {method}")
                    self.domain_solved += 1
                    tracker.mark_domain_success()
                    return result
                else:
                    # FALLBACK to SymPy
                    logger.info(f"[FALLBACK] Factoring via SymPy (domain method: {method})")
                    self.sympy_fallbacks += 1
                    tracker.mark_fallback(f"Pattern not recognized: {method}")
                    result = factor(expr)
                    return result

            elif operation == 'expand':
                # Expand is inherently a SymPy operation (intentional use)
                tracker.mark_intentional_sympy("expand is a symbolic manipulation")
                result = expand(expr)
                return result

            elif operation == 'simplify':
                # Simplify is inherently a SymPy operation (intentional use)
                tracker.mark_intentional_sympy("simplify is a symbolic manipulation")
                result = simplify(expr)
                return result

            elif operation == 'roots' or operation == 'solve':
                variables = list(expr.free_symbols)

                if not variables:
                    # No variables - check if expression equals zero
                    simplified = sp.simplify(expr)
                    tracker.mark_intentional_sympy("constant expression evaluation")
                    if simplified == 0:
                        return "all values (tautology: 0 = 0)"
                    else:
                        return f"no solution (contradiction: {simplified} != 0)"

                # Get target variable
                target_var_name = metadata.get('variable', 'x')
                target_var = sp.Symbol(target_var_name)

                if target_var not in expr.free_symbols:
                    # Target variable not in expression - use first available
                    sorted_vars = sorted(variables, key=lambda s: s.name)
                    target_var = sorted_vars[0]

                # TRY DOMAIN ALGORITHMS FIRST
                success, solutions, method = self.domain_solver.try_domain_solve(expr, target_var)

                if success:
                    logger.info(f"[DOMAIN] Solved using {method}")
                    self.domain_solved += 1
                    tracker.mark_domain_success()
                    return solutions
                else:
                    # FALLBACK to SymPy
                    logger.info(f"[FALLBACK] Solving via SymPy (domain method: {method})")
                    self.sympy_fallbacks += 1
                    tracker.mark_fallback(f"Domain algorithm failed: {method}")
                    result = solve(expr, target_var)
                    return result

            elif operation == 'compute':
                # For compute, just simplify (intentional SymPy use)
                tracker.mark_intentional_sympy("compute/simplify")
                result = sp.simplify(expr)
                return result

            elif operation == 'complex_modulus':
                # Compute |z| = sqrt(re(z)^2 + im(z)^2) for complex expression
                tracker.mark_intentional_sympy("complex modulus computation")
                # Use Abs which handles complex properly
                result = sp.Abs(expr)
                # Try to simplify to a real number
                result = sp.simplify(result)
                return result

            elif operation == 'complex_argument':
                # Compute arg(z) = atan2(im(z), re(z))
                tracker.mark_intentional_sympy("complex argument computation")
                result = sp.arg(expr)
                # Try to simplify to standard angles
                result = sp.simplify(result)
                return result

            elif operation == 'complex_simplify':
                # Simplify complex expression using Euler's formula, etc.
                tracker.mark_intentional_sympy("complex simplification")

                # For expressions like (a+bi)^n, expand to compute a+bi form
                if expr.is_Pow and expr.exp.is_Integer:
                    result = sp.expand_complex(expr)
                    result = sp.simplify(result)
                    return result

                # For Euler-type expressions like exp(I*x) + exp(-I*x)
                # Rewrite exponentials as trig functions using Euler's formula
                result = expr.rewrite(sp.cos, sp.sin)
                result = sp.simplify(result)

                # Also try expand_complex approach
                result_exp = sp.expand_complex(expr)
                result_exp = sp.simplify(result_exp)

                # Return the simpler result
                if len(str(result_exp)) < len(str(result)):
                    result = result_exp
                return result

            else:
                # Default: simplify (intentional SymPy use)
                tracker.mark_intentional_sympy(f"default operation: {operation}")
                result = simplify(expr)
                return result

    def _create_result_entry(self, task_entry: Any, result: Any, operation: str) -> Any:
        """Create result entry for Blackboard"""
        if not self.blackboard:
            return result

        result_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(str(result)),
            author_agent=self.agent_id,
            conversation_id=task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'result',
            tags=['polynomial', operation, task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'result'],
            status=EntryStatus.PENDING,
            metadata={
                'result': str(result),
                'result_str': str(result),
                'operation': operation,
                'algorithm': 'groebner_bases' if operation == 'solve' else 'sympy'
            }
        )

        self.blackboard.post(result_entry)
        return result_entry

    def _create_error_entry(self, task_entry: Any, error_msg: str) -> Any:
        """Create error entry for Blackboard"""
        if not self.blackboard:
            return None

        error_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(f"ERROR: {error_msg}"),
            author_agent=self.agent_id,
            conversation_id=task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'error',
            tags=['error', 'polynomial'],
            status=EntryStatus.FAILED,
            metadata={'error': error_msg}
        )

        self.blackboard.post(error_entry)
        return error_entry

    # ==========================================================================
    # REAL BDI IMPLEMENTATION
    # ==========================================================================
    #
    # The Polynomial Specialist's BDI loop:
    #   1. update_beliefs() - Find polynomial tasks on Blackboard
    #   2. deliberate() - Create computation plans for each task
    #   3. execute_step() - Execute computation steps (DELEGATE to SymPy)
    #
    # CRITICAL: All computation is delegated to SymPy. This agent:
    #   - NEVER implements math algorithms directly
    #   - Uses Gröbner bases via sympy.groebner for polynomial systems
    #   - Uses sympy.factor, sympy.expand, sympy.solve for operations
    # ==========================================================================

    def update_beliefs(self):
        """
        PERCEIVE: Monitor Blackboard for polynomial tasks.

        The specialist looks for:
        1. New polynomial tasks tagged with 'polynomial' or delegated to it
        2. Tasks with polynomial operations (factor, expand, roots, solve)
        """
        if not self.blackboard:
            return

        try:
            # Find tasks specifically tagged for polynomial work
            poly_tasks = self.blackboard.query_entries(
                tags=['polynomial'],
                status=EntryStatus.PENDING
            )

            # Also find delegated tasks assigned to this agent
            delegated_tasks = self.blackboard.query_entries(
                entry_type=EntryType.TASK,
                status=EntryStatus.PENDING
            )

            # Filter for tasks delegated to us
            for task in delegated_tasks:
                if hasattr(task, 'metadata') and task.metadata:
                    assigned = task.metadata.get('assigned_agent', '')
                    if assigned == self.agent_id and task not in poly_tasks:
                        poly_tasks.append(task)

            # Add beliefs about pending tasks
            for task in poly_tasks:
                belief_key = f'pending_task_{task.entry_id}'

                # Skip if already processing
                if self.has_belief(f'claimed_task_{task.entry_id}'):
                    continue
                if self.has_belief(f'completed_task_{task.entry_id}'):
                    continue

                if not self.has_belief(belief_key):
                    self.add_belief(
                        predicate=belief_key,
                        content=task,
                        confidence=1.0,
                        source='blackboard'
                    )

        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """
        DELIBERATE: Create computation plans for polynomial tasks.

        For each pending task:
        1. Determine operation type (factor, expand, solve, roots)
        2. Create appropriate computation plan
        3. Generate intention with steps to execute

        Returns:
            List of new Intention objects
        """
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue

            task = belief.content
            task_id = task.entry_id

            # Skip if already have an intention for this task
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            # Extract operation from metadata
            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'solve')
            raw_input = metadata.get('raw_input', '')

            # Determine if this is a polynomial system
            is_system = self._is_system(raw_input, metadata.get('sympy_expr'))

            # Build steps based on operation
            if is_system:
                steps = ['claim_task', 'parse_system', 'compute_groebner', 'extract_solutions', 'verify_result', 'post_result']
            elif operation == 'factor':
                steps = ['claim_task', 'parse_expression', 'factor_polynomial', 'verify_result', 'post_result']
            elif operation == 'expand':
                steps = ['claim_task', 'parse_expression', 'expand_polynomial', 'verify_result', 'post_result']
            elif operation == 'roots':
                steps = ['claim_task', 'parse_expression', 'find_roots', 'verify_result', 'post_result']
            else:  # solve or default
                steps = ['claim_task', 'parse_expression', 'solve_polynomial', 'verify_result', 'post_result']

            intention = Intention(
                plan_id=f'poly_{operation}_{task_id}',
                steps=steps,
                target_desire='solve_polynomial',
                metadata={
                    'task_id': task_id,
                    'task_entry': task,
                    'operation': operation,
                    'is_system': is_system,
                    'raw_input': raw_input,
                    'sympy_expr': metadata.get('sympy_expr')
                }
            )

            new_intentions.append(intention)
            logger.info(f"[{self.agent_id}] Created plan: {operation} for {task_id}")

        return new_intentions

    def execute_step(self, intention: Intention):
        """
        EXECUTE: Execute one step of the computation plan.

        Steps vary by operation but all DELEGATE to SymPy:
        - parse_expression: Parse input into SymPy expression
        - factor_polynomial: Call sympy.factor()
        - expand_polynomial: Call sympy.expand()
        - solve_polynomial: Call sympy.solve()
        - compute_groebner: Call sympy.groebner() for systems
        - verify_result: Check result validity
        - post_result: Post to Blackboard

        CRITICAL: This agent NEVER implements math. It delegates to SymPy.
        """
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')

        logger.debug(f"[{self.agent_id}] Executing: {action} for {task_id}")

        try:
            if action == 'claim_task':
                self._execute_claim_task(intention, task, task_id)

            elif action == 'parse_expression':
                self._execute_parse_expression(intention)

            elif action == 'parse_system':
                self._execute_parse_system(intention)

            elif action == 'factor_polynomial':
                self._execute_factor(intention)

            elif action == 'expand_polynomial':
                self._execute_expand(intention)

            elif action == 'solve_polynomial':
                self._execute_solve(intention)

            elif action == 'find_roots':
                self._execute_find_roots(intention)

            elif action == 'compute_groebner':
                self._execute_groebner(intention)

            elif action == 'extract_solutions':
                self._execute_extract_solutions(intention)

            elif action == 'verify_result':
                self._execute_verify(intention)

            elif action == 'post_result':
                self._execute_post_result(intention, task)

            else:
                logger.warning(f"[{self.agent_id}] Unknown action: {action}")
                intention.advance()

        except Exception as e:
            logger.error(f"[{self.agent_id}] Step {action} failed: {e}")
            self._handle_computation_failure(intention, task, str(e))

    def _execute_claim_task(self, intention: Intention, task: Any, task_id: str):
        """Claim task on Blackboard"""
        if self.blackboard:
            self.blackboard.update_entry_status(task_id, EntryStatus.IN_PROGRESS)

        self.add_belief(f'claimed_task_{task_id}', True)
        self.remove_belief(f'pending_task_{task_id}')

        logger.info(f"[{self.agent_id}] Claimed task {task_id}")
        intention.advance()

    def _execute_parse_expression(self, intention: Intention):
        """Parse expression using SymPy"""
        raw_input = intention.metadata.get('raw_input', '')
        sympy_expr_str = intention.metadata.get('sympy_expr')

        # Use sympy_expr if available
        expr_str = sympy_expr_str if sympy_expr_str else raw_input

        # Clean up equation format if needed
        if '=' in expr_str:
            parts = expr_str.split('=')
            if len(parts) == 2:
                lhs, rhs = parts[0].strip(), parts[1].strip()
                if rhs in ('', '0', '0.0'):
                    expr_str = lhs
                else:
                    expr_str = f"({lhs}) - ({rhs})"

        # DELEGATE to SymPy for parsing
        expr = sp.sympify(expr_str)
        intention.metadata['parsed_expr'] = expr
        intention.metadata['variables'] = sorted(list(expr.free_symbols), key=lambda s: s.name)

        logger.debug(f"[{self.agent_id}] Parsed: {expr}")
        intention.advance()

    def _execute_parse_system(self, intention: Intention):
        """Parse system of equations"""
        raw_input = intention.metadata.get('raw_input', '')

        # Split by common delimiters
        equations_str = raw_input.replace(' and ', ',').replace('\n', ',')
        equations = [eq.strip() for eq in equations_str.split(',') if eq.strip()]

        # DELEGATE to SymPy for parsing each equation
        parsed_eqs = []
        all_vars = set()
        for eq in equations:
            if '=' in eq:
                parts = eq.split('=')
                expr = sp.sympify(f"({parts[0]}) - ({parts[1]})")
            else:
                expr = sp.sympify(eq)
            parsed_eqs.append(expr)
            all_vars.update(expr.free_symbols)

        intention.metadata['parsed_system'] = parsed_eqs
        intention.metadata['variables'] = sorted(list(all_vars), key=lambda s: s.name)

        logger.debug(f"[{self.agent_id}] Parsed system with {len(parsed_eqs)} equations")
        intention.advance()

    def _execute_factor(self, intention: Intention):
        """DELEGATE factoring to SymPy"""
        expr = intention.metadata.get('parsed_expr')

        # DELEGATE to SymPy - never implement factoring ourselves
        result = sp.factor(expr)

        intention.metadata['result'] = result
        self.add_belief('computed_result', result)

        logger.info(f"[{self.agent_id}] Factored: {result}")
        intention.advance()

    def _execute_expand(self, intention: Intention):
        """DELEGATE expansion to SymPy"""
        expr = intention.metadata.get('parsed_expr')

        # DELEGATE to SymPy
        result = sp.expand(expr)

        intention.metadata['result'] = result
        self.add_belief('computed_result', result)

        logger.info(f"[{self.agent_id}] Expanded: {result}")
        intention.advance()

    def _execute_solve(self, intention: Intention):
        """DELEGATE solving to SymPy"""
        expr = intention.metadata.get('parsed_expr')
        variables = intention.metadata.get('variables', [])

        if not variables:
            # No variables - simplify
            result = sp.simplify(expr)
        else:
            # Get target variable (prefer 'x' if present)
            target = variables[0]
            for v in variables:
                if v.name == 'x':
                    target = v
                    break

            # DELEGATE to SymPy
            result = sp.solve(expr, target)

        intention.metadata['result'] = result
        self.add_belief('computed_result', result)

        logger.info(f"[{self.agent_id}] Solved: {result}")
        intention.advance()

    def _execute_find_roots(self, intention: Intention):
        """DELEGATE root-finding to SymPy"""
        expr = intention.metadata.get('parsed_expr')
        variables = intention.metadata.get('variables', [])

        if variables:
            # DELEGATE to SymPy
            result = sp.solve(expr, variables[0])
        else:
            result = expr

        intention.metadata['result'] = result
        self.add_belief('computed_result', result)

        logger.info(f"[{self.agent_id}] Found roots: {result}")
        intention.advance()

    def _execute_groebner(self, intention: Intention):
        """DELEGATE Gröbner basis computation to SymPy"""
        equations = intention.metadata.get('parsed_system', [])
        variables = intention.metadata.get('variables', [])

        if not equations or not variables:
            intention.metadata['result'] = []
            intention.advance()
            return

        try:
            # DELEGATE to SymPy's Gröbner basis implementation
            basis = sp.groebner(equations, variables, order='grlex')
            intention.metadata['groebner_basis'] = basis

            self.groebner_bases_computed += 1
            logger.info(f"[{self.agent_id}] Computed Gröbner basis")

        except Exception as e:
            logger.warning(f"[{self.agent_id}] Gröbner failed, using direct solve: {e}")
            intention.metadata['groebner_basis'] = None

        intention.advance()

    def _execute_extract_solutions(self, intention: Intention):
        """Extract solutions from Gröbner basis"""
        equations = intention.metadata.get('parsed_system', [])
        variables = intention.metadata.get('variables', [])

        # DELEGATE solution extraction to SymPy
        solutions = sp.solve(equations, variables, dict=True)

        # Filter for real solutions
        real_solutions = []
        for sol in solutions:
            is_real = all(self._is_real_solution(v) for v in sol.values())
            if is_real:
                real_solutions.append({str(k): v for k, v in sol.items()})

        result = real_solutions if real_solutions else solutions
        intention.metadata['result'] = result
        self.add_belief('computed_result', result)

        logger.info(f"[{self.agent_id}] Found {len(result)} solutions")
        intention.advance()

    def _execute_verify(self, intention: Intention):
        """Verify computation result"""
        result = intention.metadata.get('result')

        # Basic verification - result exists and is not None
        verified = result is not None

        intention.metadata['verified'] = verified
        self.add_belief('result_verified', verified)

        logger.debug(f"[{self.agent_id}] Verification: {verified}")
        intention.advance()

    def _execute_post_result(self, intention: Intention, task: Any):
        """Post result to Blackboard"""
        result = intention.metadata.get('result')
        operation = intention.metadata.get('operation', 'compute')
        task_id = intention.metadata.get('task_id')

        if self.blackboard:
            # Get delegation_id if this was delegated
            delegation_id = task.metadata.get('delegation_id', task_id) if hasattr(task, 'metadata') else task_id

            result_entry = create_entry(
                entry_type=EntryType.PARTIAL_RESULT,
                content=create_variable(str(result)),
                author_agent=self.agent_id,
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                tags=['polynomial', 'result', operation, delegation_id],
                status=EntryStatus.COMPLETED,
                metadata={
                    'result': str(result),
                    'result_str': str(result),
                    'operation': operation,
                    'task_id': task_id,
                    'verified': intention.metadata.get('verified', False),
                    'algorithm': 'groebner_bases' if intention.metadata.get('is_system') else 'sympy'
                }
            )
            self.blackboard.post(result_entry)

            # Mark original task complete
            self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)

        # Update beliefs
        self.add_belief(f'completed_task_{task_id}', True)
        self.remove_belief(f'claimed_task_{task_id}')

        self.tasks_succeeded += 1
        logger.info(f"[{self.agent_id}] Posted result for {task_id}: {result}")
        intention.advance()

    def _handle_computation_failure(self, intention: Intention, task: Any, error_msg: str):
        """Handle computation failure"""
        task_id = intention.metadata.get('task_id')

        if self.blackboard and task_id:
            error_entry = create_entry(
                entry_type=EntryType.PARTIAL_RESULT,
                content=create_variable(f"ERROR: {error_msg}"),
                author_agent=self.agent_id,
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                tags=['error', 'polynomial', task_id],
                status=EntryStatus.FAILED,
                metadata={'error': error_msg, 'task_id': task_id}
            )
            self.blackboard.post(error_entry)
            self.blackboard.update_entry_status(task_id, EntryStatus.FAILED)

        # Clean up beliefs
        if task_id:
            self.remove_belief(f'pending_task_{task_id}')
            self.remove_belief(f'claimed_task_{task_id}')

        self.tasks_failed += 1

        # Mark intention complete (failed)
        while not intention.is_complete():
            intention.advance()

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get specialist statistics including domain-first metrics.

        Returns statistics about:
        - Overall task success/failure rates
        - Domain algorithm success rate
        - SymPy fallback rate
        - Global fallback tracker statistics
        """
        stats = super().get_statistics()

        # Calculate domain-first metrics
        total_computed = self.domain_solved + self.sympy_fallbacks
        domain_rate = (self.domain_solved / total_computed * 100) if total_computed > 0 else 0.0
        fallback_rate = (self.sympy_fallbacks / total_computed * 100) if total_computed > 0 else 0.0

        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'success_rate': (self.tasks_succeeded / self.tasks_executed * 100)
                           if self.tasks_executed > 0 else 0.0,
            'groebner_bases_computed': self.groebner_bases_computed,

            # Domain-first architecture metrics
            'domain_solved': self.domain_solved,
            'sympy_fallbacks': self.sympy_fallbacks,
            'domain_success_rate': round(domain_rate, 1),
            'fallback_rate': round(fallback_rate, 1),

            # Global tracker statistics
            'global_fallback_stats': self._tracker.get_statistics()
        })
        return stats
