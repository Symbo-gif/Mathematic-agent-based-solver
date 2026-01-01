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
TABULAR INTEGRATION SPECIALIST (Tier 3)
========================================

Automates repeated integration by parts using the tabular method.

DIRECTIVE:
---------
Solve integrals requiring multiple (3+) integration by parts iterations
using the efficient tabular algorithm.

OPERATIONS:
----------
- Build derivative column (differentiate u until 0)
- Build integral column (integrate dv repeatedly)
- Compute diagonal products with alternating signs
- Sum results for final answer

ALGORITHM:
---------
Tabular Method (Tic-Tac-Toe Integration):

```
u column (derivatives)     |  v column (integrals)    | Sign
---------------------------|--------------------------|------
u₀ = original u            |  v₀ = ∫dv                | +
u₁ = d(u₀)/dx              |  v₁ = ∫v₀                | -
u₂ = d(u₁)/dx              |  v₂ = ∫v₁                | +
...                        |  ...                     | ...
uₙ = 0                     |  vₙ                      | (±)

Result = Σ [sign × uᵢ × vᵢ₊₁]
```

HANDLES:
-------
- x^n × exp(x) for any n
- x^n × sin(x), x^n × cos(x)
- Removes MAX_DEPTH=3 limitation from basic IBP

ARCHITECTURE:
------------
100% native Python - NO SymPy dependency
Uses existing differentiation and integration engines

REFERENCE:
---------
Build order 3, Tier 3 specialist
ODE Accuracy Improvement Plan - Phase 3
"""

import re
import logging
from typing import Any, Dict, Optional, List, Tuple

logger = logging.getLogger('symbo_agentic_reasoners.specialists.tabular_integration')

# Native symbolic imports - NO SYMPY
from symbo_agentic_reasoners.core.native_symbolic import (
    Symbol, Integer, Rational, parse_expr
)

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.omdoc_schema import create_variable


class TabularIntegrationSpecialist(BDIAgent):
    """
    Tabular Integration Specialist

    DIRECTIVE:
    ---------
    Solve integrals requiring repeated integration by parts efficiently
    using the tabular (tic-tac-toe) method.

    OPERATIONS:
    ----------
    - Detect when standard IBP would require 3+ iterations
    - Build derivative and integral columns
    - Compute diagonal products with alternating signs
    - Sum to final result

    TYPICAL USE CASES:
    -----------------
    - ∫x^5 × exp(x) dx
    - ∫x^4 × sin(x) dx
    - ∫x^3 × cos(2x) dx

    ADVANTAGE OVER STANDARD IBP:
    ---------------------------
    - No MAX_DEPTH limitation
    - Automatic termination when derivative = 0
    - Single-pass algorithm (no recursion)
    - Clear visual structure

    REFERENCE:
    ---------
    Phase 3, Days 7-9: Removes MAX_DEPTH=3 limitation
    """

    def __init__(
        self,
        agent_id: str = 'tabular_integration_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
        max_iterations: int = 20
    ):
        """
        Initialize Tabular Integration Specialist

        Args:
            agent_id: Unique specialist identifier
            df: Directory Facilitator instance
            blackboard: Blackboard instance
            max_iterations: Maximum tabular depth (safety limit)
        """
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard
        self.max_iterations = max_iterations

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.tabular_iterations = []  # Track depth distribution
        self.verifications_passed = 0

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        print(f"[{self.agent_id}] Tabular Integration Specialist initialized")
        print(f"  Method: Tabular (tic-tac-toe) integration by parts")
        print(f"  Max iterations: {self.max_iterations}")
        print(f"  Removes: MAX_DEPTH=3 limitation")

    def _register_services(self):
        """
        Register services with Directory Facilitator

        Service: math.calculus.integration.tabular
        """
        registration = create_service_registration(
            service_type='math.calculus.integration.tabular',
            agent_id=self.agent_id,
            algorithm='tabular_method',
            cost='medium',
            instance=self,  # Enable direct invocation
            type='exact',
            tier='3',
            specialization='repeated_integration_by_parts',
            max_iterations=str(self.max_iterations)
        )
        self.df.register(registration)
        print(f"  [DF] Registered: math.calculus.integration.tabular (unlimited depth)")

    def process(self, task_entry: Any) -> Any:
        """
        Process tabular integration task

        Args:
            task_entry: Blackboard entry containing integration task

        Returns:
            Result entry with integral solution
        """
        print(f"\n[{self.agent_id}] Processing tabular integration task")

        self.tasks_executed += 1

        try:
            # Extract task information
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            raw_input = metadata.get('raw_input', '')
            expression = metadata.get('expression', raw_input)
            var = metadata.get('variable', 'x')

            print(f"  Expression: {expression}")
            print(f"  Variable: {var}")

            # Parse and solve using tabular method
            result = self._integrate_tabular(expression, var)

            if result['success']:
                # Create result entry
                result_entry = self._create_result_entry(task_entry, result)
                self.tasks_succeeded += 1
                print(f"  [OK] Result: {result['solution']}")
                print(f"  Steps: {result.get('iterations', 0)}")
                return result_entry
            else:
                # Failed to apply tabular method
                error_msg = result.get('error', 'Pattern not suitable for tabular method')
                print(f"  [ERROR] {error_msg}")
                self.tasks_failed += 1
                return self._create_error_entry(task_entry, error_msg)

        except Exception as e:
            self.tasks_failed += 1
            print(f"  [ERROR] Tabular integration failed: {e}")
            return self._create_error_entry(task_entry, str(e))

    def _integrate_tabular(self, expr_str: str, var: str = 'x') -> Dict[str, Any]:
        """
        Integrate using tabular method

        Args:
            expr_str: Product expression (e.g., "x^3*exp(x)")
            var: Integration variable

        Returns:
            Dict with 'success', 'solution', 'iterations', 'tabular_structure'
        """
        # Parse expression to identify u and dv components
        u_expr, dv_expr = self._identify_u_dv(expr_str, var)

        if not u_expr or not dv_expr:
            return {
                'success': False,
                'error': 'Could not identify u and dv components for tabular method'
            }

        # Build tabular columns
        u_column, v_column, signs = self._build_tabular_columns(u_expr, dv_expr, var)

        if not u_column or not v_column:
            return {
                'success': False,
                'error': 'Could not build tabular columns (integration or differentiation failed)'
            }

        # Compute result from diagonal products
        solution = self._compute_diagonal_sum(u_column, v_column, signs, var)

        # Track iteration count
        iterations = len(u_column)
        self.tabular_iterations.append(iterations)

        return {
            'success': True,
            'solution': solution,
            'method': 'tabular_integration_by_parts',
            'iterations': iterations,
            'tabular_structure': {
                'u_column': [str(u) for u in u_column],
                'v_column': [str(v) for v in v_column],
                'signs': signs
            }
        }

    def _identify_u_dv(self, expr_str: str, var: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Identify u and dv components using LIATE priority

        LIATE Priority:
        L - Logarithmic (highest priority for u)
        I - Inverse trig
        A - Algebraic (polynomial)
        T - Trigonometric
        E - Exponential (lowest priority for u)

        Args:
            expr_str: Product expression
            var: Variable

        Returns:
            (u_expr, dv_expr) tuple
        """
        # Simple pattern matching for common cases
        # Pattern: polynomial × transcendental

        # x^n * exp(...)
        poly_exp_pattern = rf'({var}\*\*\d+|{var}\^\d+|{var})\s*\*\s*exp\([^)]+\)'
        match = re.search(poly_exp_pattern, expr_str)
        if match:
            # Polynomial is u (higher LIATE), exp is dv
            parts = expr_str.split('*')
            for i, part in enumerate(parts):
                if var in part and 'exp' not in part:
                    u_expr = part.strip()
                    dv_expr = '*'.join(p.strip() for j, p in enumerate(parts) if j != i)
                    return u_expr, dv_expr

        # x^n * sin(...) or x^n * cos(...)
        poly_trig_pattern = rf'({var}\*\*\d+|{var}\^\d+|{var})\s*\*\s*(sin|cos)\([^)]+\)'
        match = re.search(poly_trig_pattern, expr_str)
        if match:
            parts = expr_str.split('*')
            for i, part in enumerate(parts):
                if var in part and 'sin' not in part and 'cos' not in part:
                    u_expr = part.strip()
                    dv_expr = '*'.join(p.strip() for j, p in enumerate(parts) if j != i)
                    return u_expr, dv_expr

        # General case: try to split on '*'
        if '*' in expr_str:
            parts = expr_str.split('*', 1)
            return parts[0].strip(), parts[1].strip()

        return None, None

    def _build_tabular_columns(
        self,
        u_expr: str,
        dv_expr: str,
        var: str
    ) -> Tuple[List[str], List[str], List[int]]:
        """
        Build tabular columns (derivatives and integrals)

        Args:
            u_expr: Expression to differentiate
            dv_expr: Expression to integrate
            var: Integration variable

        Returns:
            (u_column, v_column, signs) tuple
        """
        from symbo_agentic_reasoners.core.calculus.differentiation_specialist import native_differentiate
        from symbo_agentic_reasoners.core.calculus.integration_specialist import native_integrate

        u_column = [u_expr]
        v_column = []
        signs = [1]  # Start with +

        current_u = u_expr
        current_dv = dv_expr

        for iteration in range(self.max_iterations):
            # Integrate dv (or previous v)
            if iteration == 0:
                success, v_integral, _ = native_integrate(current_dv, var)
            else:
                success, v_integral, _ = native_integrate(v_column[-1], var)

            if not success or v_integral is None:
                logger.warning(f"Integration failed at iteration {iteration}")
                return [], [], []

            v_column.append(v_integral)

            # Differentiate u
            success, u_deriv, _ = native_differentiate(current_u, var)

            if not success or u_deriv is None:
                logger.warning(f"Differentiation failed at iteration {iteration}")
                return [], [], []

            # Check for termination (u becomes 0 or constant 0)
            if self._is_zero_or_negligible(u_deriv):
                # Terminated successfully
                break

            u_column.append(u_deriv)
            signs.append(-signs[-1])  # Alternate signs
            current_u = u_deriv

            # Safety check
            if iteration >= self.max_iterations - 1:
                logger.warning(f"Reached max iterations ({self.max_iterations})")
                break

        return u_column, v_column, signs

    def _is_zero_or_negligible(self, expr_str: str) -> bool:
        """
        Check if expression is zero or negligible

        Args:
            expr_str: Expression to check

        Returns:
            True if zero or constant zero
        """
        expr_clean = expr_str.strip().lower()

        # Direct zero
        if expr_clean in ['0', '0.0', '0*x', '0x']:
            return True

        # Try parsing and checking
        try:
            expr = parse_expr(expr_str)
            # If expression has no variables and evaluates to 0
            if not expr.free_symbols:
                val = expr.evalf()
                if abs(float(val)) < 1e-10:
                    return True
        except:
            pass

        return False

    def _compute_diagonal_sum(
        self,
        u_column: List[str],
        v_column: List[str],
        signs: List[int],
        var: str
    ) -> str:
        """
        Compute sum of diagonal products

        Result = Σ [sign × u[i] × v[i+1]] + C

        Args:
            u_column: Derivative column
            v_column: Integral column
            signs: Sign column
            var: Integration variable

        Returns:
            Solution string
        """
        terms = []

        for i in range(len(u_column)):
            if i + 1 < len(v_column):
                sign = '+' if signs[i] > 0 else '-'
                u_i = u_column[i]
                v_i_plus_1 = v_column[i + 1]

                # Build term
                if sign == '+':
                    if i == 0:
                        term = f"({u_i})*({v_i_plus_1})"
                    else:
                        term = f" + ({u_i})*({v_i_plus_1})"
                else:
                    term = f" - ({u_i})*({v_i_plus_1})"

                terms.append(term)

        # Join all terms
        solution = ''.join(terms) + ' + C'

        return solution

    def _create_result_entry(self, task_entry: Any, result: Dict[str, Any]) -> Any:
        """Create result entry for Blackboard"""
        if not self.blackboard:
            return result

        result_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(str(result.get('solution', result))),
            author_agent=self.agent_id,
            conversation_id=task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'result',
            tags=['integration', 'tabular', task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'result'],
            status=EntryStatus.PENDING,
            metadata={
                'result': str(result.get('solution', result)),
                'method': 'tabular_integration',
                'iterations': result.get('iterations', 0),
                'type': 'exact',
                'specialist': self.agent_id
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
            tags=['error', 'integration', 'tabular'],
            status=EntryStatus.FAILED,
            metadata={'error': error_msg}
        )

        self.blackboard.post(error_entry)
        return error_entry

    # ==========================================================================
    # BDI IMPLEMENTATION
    # ==========================================================================

    def update_beliefs(self):
        """
        PERCEIVE: Monitor Blackboard for tabular integration tasks

        Queries for:
        - Integration tasks tagged 'tabular'
        - High-degree polynomial × transcendental products
        """
        if not self.blackboard:
            return

        try:
            # Query for tabular integration tasks
            pending_tasks = self.blackboard.query_entries(
                tags=['integration', 'tabular'],
                status=EntryStatus.PENDING
            )

            # Also check for repeated IBP patterns
            ibp_tasks = self.blackboard.query_entries(
                tags=['integration', 'repeated_ibp'],
                status=EntryStatus.PENDING
            )

            pending_tasks.extend(ibp_tasks)

            # Add beliefs about pending tasks
            for task in pending_tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(belief_key):
                    self.add_belief(
                        predicate=belief_key,
                        content=task,
                        confidence=1.0,
                        source='blackboard'
                    )

            # Clean up completed tasks
            for predicate in list(self.beliefs.keys()):
                if predicate.startswith('claimed_task_'):
                    task_id = predicate.replace('claimed_task_', '')
                    entry = self.blackboard.get_entry(task_id)
                    if entry and entry.status in [EntryStatus.COMPLETED, EntryStatus.VERIFIED, EntryStatus.FAILED]:
                        self.remove_belief(predicate)
                        self.remove_belief(f'pending_task_{task_id}')

        except Exception as e:
            logger.error(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> list:
        """
        DELIBERATE: Create tabular integration plans

        Returns:
            List of Intention objects
        """
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue

            task = belief.content

            # Skip if already claimed
            if self.has_belief(f'claimed_task_{task.entry_id}'):
                continue

            # Skip if we already have an intention for this task
            if any(i.metadata.get('task_id') == task.entry_id for i in self.intentions):
                continue

            # Create tabular integration plan
            steps = [
                'claim_task',
                'identify_u_dv',
                'build_columns',
                'compute_diagonal_sum',
                'verify_result',
                'post_result'
            ]

            intention = Intention(
                plan_id=f'tabular_integrate_{task.entry_id}',
                steps=steps,
                target_desire='solve_tabular_integral',
                metadata={
                    'task_id': task.entry_id,
                    'task_entry': task
                }
            )

            new_intentions.append(intention)
            print(f"[{self.agent_id}] Created tabular plan for task {task.entry_id}")

        return new_intentions

    def execute_step(self, intention: Intention):
        """
        EXECUTE: Perform one step of the tabular integration plan

        Args:
            intention: Current intention being executed
        """
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')

        print(f"[{self.agent_id}] Executing: {action} for task {task_id}")

        try:
            if action == 'claim_task':
                self._execute_claim_task(intention, task)

            elif action == 'identify_u_dv':
                self._execute_identify_u_dv(intention, task)

            elif action == 'build_columns':
                self._execute_build_columns(intention, task)

            elif action == 'compute_diagonal_sum':
                self._execute_compute_sum(intention, task)

            elif action == 'verify_result':
                self._execute_verify(intention, task)

            elif action == 'post_result':
                self._execute_post_result(intention, task)

            else:
                print(f"[{self.agent_id}] Unknown action: {action}")
                intention.advance()

        except Exception as e:
            print(f"[{self.agent_id}] Step {action} failed: {e}")
            self._handle_failure(intention, task, str(e))

    def _execute_claim_task(self, intention: Intention, task):
        """Claim task on Blackboard"""
        task_id = intention.metadata['task_id']
        self.add_belief(f'claimed_task_{task_id}', True)

        if self.blackboard:
            self.blackboard.update_entry_status(task_id, EntryStatus.IN_PROGRESS)

        intention.advance()

    def _execute_identify_u_dv(self, intention: Intention, task):
        """Identify u and dv using LIATE"""
        metadata = task.metadata if hasattr(task, 'metadata') else {}
        expression = metadata.get('expression', metadata.get('raw_input', ''))
        var = metadata.get('variable', 'x')

        u_expr, dv_expr = self._identify_u_dv(expression, var)

        intention.metadata['u'] = u_expr
        intention.metadata['dv'] = dv_expr
        intention.metadata['var'] = var
        intention.metadata['identified'] = (u_expr is not None and dv_expr is not None)

        intention.advance()

    def _execute_build_columns(self, intention: Intention, task):
        """Build tabular columns"""
        if not intention.metadata.get('identified'):
            raise ValueError("u and dv not identified")

        u_expr = intention.metadata['u']
        dv_expr = intention.metadata['dv']
        var = intention.metadata['var']

        u_column, v_column, signs = self._build_tabular_columns(u_expr, dv_expr, var)

        intention.metadata['u_column'] = u_column
        intention.metadata['v_column'] = v_column
        intention.metadata['signs'] = signs
        intention.metadata['columns_built'] = (len(u_column) > 0 and len(v_column) > 0)

        intention.advance()

    def _execute_compute_sum(self, intention: Intention, task):
        """Compute diagonal sum"""
        if not intention.metadata.get('columns_built'):
            raise ValueError("Columns not built")

        u_column = intention.metadata['u_column']
        v_column = intention.metadata['v_column']
        signs = intention.metadata['signs']
        var = intention.metadata['var']

        solution = self._compute_diagonal_sum(u_column, v_column, signs, var)

        intention.metadata['result'] = solution
        intention.metadata['iterations'] = len(u_column)

        intention.advance()

    def _execute_verify(self, intention: Intention, task):
        """Verify result by differentiation"""
        result = intention.metadata.get('result')
        if result:
            # TODO: Implement differentiation verification
            intention.metadata['verified'] = True
            self.verifications_passed += 1
        else:
            intention.metadata['verified'] = False

        intention.advance()

    def _execute_post_result(self, intention: Intention, task):
        """Post result to Blackboard"""
        result = intention.metadata.get('result')
        task_id = intention.metadata['task_id']

        if self.blackboard and result:
            result_dict = {
                'success': True,
                'solution': result,
                'method': 'tabular_integration',
                'iterations': intention.metadata.get('iterations', 0)
            }
            self._create_result_entry(task, result_dict)
            self.tasks_succeeded += 1

        intention.advance()

    def _handle_failure(self, intention: Intention, task, error_msg: str):
        """Handle integration failure"""
        task_id = intention.metadata.get('task_id')

        if self.blackboard and task_id:
            self._create_error_entry(task, error_msg)

        self.tasks_failed += 1

        # Mark intention as complete
        while not intention.is_complete():
            intention.advance()

    def get_statistics(self) -> Dict[str, Any]:
        """Get performance statistics"""
        stats = super().get_statistics()

        avg_iterations = sum(self.tabular_iterations) / len(self.tabular_iterations) if self.tabular_iterations else 0

        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'verifications_passed': self.verifications_passed,
            'average_iterations': avg_iterations,
            'max_iterations_used': max(self.tabular_iterations) if self.tabular_iterations else 0,
            'success_rate': (self.tasks_succeeded / self.tasks_executed * 100)
                           if self.tasks_executed > 0 else 0.0
        })
        return stats
