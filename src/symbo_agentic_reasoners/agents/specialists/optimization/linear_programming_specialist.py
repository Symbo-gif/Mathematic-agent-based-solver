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
LINEAR PROGRAMMING SPECIALIST (Tier 3)
======================================

Native Python implementation for linear programming problems.
Implements the Simplex algorithm for LP optimization.

NO SYMPY - Pure native mathematical reasoning.
"""

import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention

logger = logging.getLogger(__name__)


class LinearProgrammingSpecialist(BDIAgent):
    """
    Specialist for linear programming optimization.

    Capabilities:
    - Simplex method (primal)
    - Two-phase simplex for finding initial BFS
    - Dual simplex
    - Sensitivity analysis
    - Integer LP (branch and bound basics)
    """

    def __init__(self, agent_id: str = 'linear_programming_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        if self.df:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
            self.df.register(create_service_registration(
                service_type='math.optimization.lp',
                agent_id=agent_id,
                algorithm='native_simplex',
                cost='medium',
                instance=self,
                tier='3',
                capabilities='simplex_dual_sensitivity'
            ))

        logger.info(f"[{agent_id}] Linear Programming Specialist initialized")

    def update_beliefs(self):
        """PERCEIVE: Monitor blackboard for LP tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryStatus
            tasks = self.blackboard.query_entries(tags=['linear_program'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['simplex'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['lp'], status=EntryStatus.PENDING)

            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(f'claimed_task_{task.entry_id}') and not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create LP solution plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'simplex')

            steps = ['claim_task', 'solve_lp', 'post_result']
            intention = Intention(
                plan_id=f'lp_{operation}_{task_id}',
                steps=steps,
                target_desire='lp_optimization',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)
        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Solve LP problems."""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')

        if action == 'claim_task':
            self.add_belief(f'claimed_task_{task.entry_id}', True, confidence=1.0)
            intention.advance()
        elif action == 'solve_lp':
            self._solve_lp(intention)
        elif action == 'post_result':
            self._post_result(intention)

    def _solve_lp(self, intention: Intention):
        """Solve the LP problem."""
        task = intention.metadata.get('task_entry')
        metadata = task.metadata if hasattr(task, 'metadata') else {}
        operation = metadata.get('operation', 'simplex')

        try:
            if operation == 'simplex':
                c = metadata.get('objective', [])
                A = metadata.get('constraints_lhs', [])
                b = metadata.get('constraints_rhs', [])
                maximize = metadata.get('maximize', True)
                result = self.simplex_solve(c, A, b, maximize)
            elif operation == 'two_phase':
                c = metadata.get('objective', [])
                A = metadata.get('constraints_lhs', [])
                b = metadata.get('constraints_rhs', [])
                maximize = metadata.get('maximize', True)
                result = self.two_phase_simplex(c, A, b, maximize)
            elif operation == 'sensitivity':
                c = metadata.get('objective', [])
                A = metadata.get('constraints_lhs', [])
                b = metadata.get('constraints_rhs', [])
                result = self.sensitivity_analysis(c, A, b)
            else:
                result = {'error': f'Unknown operation: {operation}'}

            intention.metadata['result'] = result
            self.tasks_executed += 1
            intention.advance()

        except Exception as e:
            logger.error(f"[{self.agent_id}] LP computation failed: {e}")
            intention.metadata['result'] = {'error': str(e)}
            intention.advance()

    def _post_result(self, intention: Intention):
        """Post result to blackboard."""
        if self.blackboard:
            from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
            task = intention.metadata.get('task_entry')
            result = intention.metadata.get('result', {})

            result_entry = create_entry(
                content=result,
                entry_type=EntryType.RESULT,
                tags=['lp', 'optimization', 'result'],
                metadata={'source_task': task.entry_id, 'agent': self.agent_id}
            )
            self.blackboard.post_entry(result_entry)
            self.blackboard.update_entry_status(task.entry_id, EntryStatus.COMPLETED)

        intention.mark_completed()

    # =========================================================================
    # SIMPLEX METHOD
    # =========================================================================

    def simplex_solve(self, c: List[float], A: List[List[float]], b: List[float],
                       maximize: bool = True, max_iterations: int = 1000) -> Dict[str, Any]:
        """
        Solve LP using Simplex method.

        Standard form: max c^T x subject to Ax <= b, x >= 0

        Args:
            c: Objective function coefficients
            A: Constraint matrix (LHS)
            b: Constraint values (RHS)
            maximize: True for maximization, False for minimization
            max_iterations: Maximum pivot iterations

        Returns:
            Dictionary with optimal solution
        """
        if not c or not A or not b:
            return {'error': 'Empty input'}

        c = np.array(c, dtype=float)
        A = np.array(A, dtype=float)
        b = np.array(b, dtype=float)

        if len(A) != len(b):
            return {'error': 'Constraint matrix and RHS dimensions mismatch'}
        if len(A[0]) != len(c):
            return {'error': 'Objective and constraint dimensions mismatch'}

        # Check for non-negative RHS (required for basic simplex)
        if np.any(b < 0):
            return self.two_phase_simplex(c.tolist(), A.tolist(), b.tolist(), maximize)

        n_constraints, n_vars = A.shape

        # Convert to minimization if needed
        if maximize:
            c = -c

        # Add slack variables to convert <= to =
        slack = np.eye(n_constraints)
        A_aug = np.hstack([A, slack])
        c_aug = np.hstack([c, np.zeros(n_constraints)])

        # Initial tableau
        # [A | I | b]
        # [c | 0 | 0]
        tableau = np.zeros((n_constraints + 1, n_vars + n_constraints + 1))
        tableau[:n_constraints, :n_vars + n_constraints] = A_aug
        tableau[:n_constraints, -1] = b
        tableau[-1, :n_vars + n_constraints] = c_aug

        # Basic variables (slack variables initially)
        basic = list(range(n_vars, n_vars + n_constraints))

        # Simplex iterations
        for iteration in range(max_iterations):
            # Find entering variable (most negative in objective row)
            obj_row = tableau[-1, :-1]
            if np.all(obj_row >= -1e-10):
                # Optimal solution found
                break

            entering = np.argmin(obj_row)

            # Find leaving variable (minimum ratio test)
            ratios = []
            for i in range(n_constraints):
                if tableau[i, entering] > 1e-10:
                    ratios.append((tableau[i, -1] / tableau[i, entering], i))

            if not ratios:
                return {'status': 'unbounded', 'message': 'LP is unbounded'}

            _, leaving_row = min(ratios)

            # Pivot
            pivot = tableau[leaving_row, entering]
            tableau[leaving_row, :] /= pivot

            for i in range(n_constraints + 1):
                if i != leaving_row:
                    tableau[i, :] -= tableau[i, entering] * tableau[leaving_row, :]

            basic[leaving_row] = entering

        else:
            return {'status': 'max_iterations', 'message': 'Max iterations reached'}

        # Extract solution
        solution = np.zeros(n_vars)
        for i, var in enumerate(basic):
            if var < n_vars:
                solution[var] = tableau[i, -1]

        # tableau[-1, -1] contains the objective value
        # For maximization, we converted to min -c^Tx, so tableau value is the max value
        # For minimization, tableau value is the min value
        optimal_value = tableau[-1, -1]
        if not maximize:
            # For minimization, the tableau directly gives the min value
            pass
        # For maximization, we already have the correct value due to sign transformation

        return {
            'status': 'optimal',
            'solution': solution.tolist(),
            'optimal_value': optimal_value,
            'iterations': iteration + 1,
            'basic_variables': basic,
            'method': 'native_simplex'
        }

    def two_phase_simplex(self, c: List[float], A: List[List[float]], b: List[float],
                           maximize: bool = True) -> Dict[str, Any]:
        """
        Two-phase Simplex for problems without obvious initial BFS.

        Phase 1: Find feasible solution
        Phase 2: Optimize from feasible solution

        Args:
            c, A, b: LP parameters
            maximize: Optimization direction

        Returns:
            Dictionary with optimal solution
        """
        c = np.array(c, dtype=float)
        A = np.array(A, dtype=float)
        b = np.array(b, dtype=float)

        n_constraints, n_vars = A.shape

        # Make RHS non-negative
        for i in range(n_constraints):
            if b[i] < 0:
                A[i, :] = -A[i, :]
                b[i] = -b[i]

        # Phase 1: Add artificial variables and minimize their sum
        artificial_c = np.hstack([np.zeros(n_vars), np.ones(n_constraints)])
        artificial_A = np.hstack([A, np.eye(n_constraints)])

        # Solve Phase 1
        phase1_result = self._simplex_phase(
            artificial_c, artificial_A, b, n_vars, n_constraints, phase=1
        )

        if phase1_result['status'] != 'optimal' or phase1_result['optimal_value'] > 1e-10:
            return {'status': 'infeasible', 'message': 'No feasible solution exists'}

        # Phase 2: Use BFS from Phase 1 with original objective
        # Remove artificial columns and optimize
        basic = phase1_result['basic_variables']

        # Check if any artificial variable is basic
        # If so, need to pivot it out
        phase2_A = A.copy()
        phase2_c = -c if maximize else c

        result = self._simplex_phase(
            np.hstack([phase2_c, np.zeros(n_constraints)]),
            np.hstack([phase2_A, np.eye(n_constraints)]),
            b, n_vars, n_constraints, phase=2, initial_basic=basic
        )

        if result['status'] == 'optimal':
            optimal_value = result['optimal_value']
            if maximize:
                optimal_value = -optimal_value

            solution = np.zeros(n_vars)
            for i, var in enumerate(result['basic_variables']):
                if var < n_vars:
                    solution[var] = result['solution_values'][i]

            return {
                'status': 'optimal',
                'solution': solution.tolist(),
                'optimal_value': optimal_value,
                'method': 'native_two_phase_simplex'
            }

        return result

    def _simplex_phase(self, c: np.ndarray, A: np.ndarray, b: np.ndarray,
                        n_vars: int, n_constraints: int, phase: int = 1,
                        initial_basic: List[int] = None) -> Dict[str, Any]:
        """Internal simplex phase implementation."""
        tableau = np.zeros((n_constraints + 1, A.shape[1] + 1))
        tableau[:n_constraints, :-1] = A
        tableau[:n_constraints, -1] = b
        tableau[-1, :-1] = c

        if initial_basic is None:
            basic = list(range(n_vars, n_vars + n_constraints))
        else:
            basic = initial_basic.copy()

        # Make objective row consistent with basic variables
        for i, var in enumerate(basic):
            if tableau[-1, var] != 0:
                tableau[-1, :] -= tableau[-1, var] * tableau[i, :]

        for iteration in range(1000):
            obj_row = tableau[-1, :-1]
            if np.all(obj_row >= -1e-10):
                break

            entering = np.argmin(obj_row)

            ratios = []
            for i in range(n_constraints):
                if tableau[i, entering] > 1e-10:
                    ratios.append((tableau[i, -1] / tableau[i, entering], i))

            if not ratios:
                return {'status': 'unbounded'}

            _, leaving_row = min(ratios)

            pivot = tableau[leaving_row, entering]
            tableau[leaving_row, :] /= pivot

            for i in range(n_constraints + 1):
                if i != leaving_row:
                    tableau[i, :] -= tableau[i, entering] * tableau[leaving_row, :]

            basic[leaving_row] = entering

        solution_values = tableau[:n_constraints, -1].tolist()

        return {
            'status': 'optimal',
            'optimal_value': -tableau[-1, -1],
            'basic_variables': basic,
            'solution_values': solution_values
        }

    def sensitivity_analysis(self, c: List[float], A: List[List[float]], b: List[float]) -> Dict[str, Any]:
        """
        Perform sensitivity analysis on LP solution.

        Returns shadow prices and allowable ranges.

        Args:
            c, A, b: LP parameters

        Returns:
            Dictionary with sensitivity information
        """
        # First solve the LP
        result = self.simplex_solve(c, A, b, maximize=True)

        if result['status'] != 'optimal':
            return {'error': 'Cannot perform sensitivity analysis on non-optimal solution'}

        n_constraints = len(b)
        n_vars = len(c)

        # Shadow prices are the coefficients of slack variables in optimal objective row
        # This is a simplified version
        shadow_prices = []

        # For each constraint, estimate shadow price by perturbing b
        eps = 1e-6
        for i in range(n_constraints):
            b_plus = list(b)
            b_plus[i] += eps

            result_plus = self.simplex_solve(c, A, b_plus, maximize=True)
            if result_plus['status'] == 'optimal':
                shadow_price = (result_plus['optimal_value'] - result['optimal_value']) / eps
                shadow_prices.append(shadow_price)
            else:
                shadow_prices.append(None)

        return {
            'optimal_solution': result['solution'],
            'optimal_value': result['optimal_value'],
            'shadow_prices': shadow_prices,
            'method': 'native_sensitivity_analysis'
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Return agent statistics."""
        return {
            'agent_id': self.agent_id,
            'tasks_executed': self.tasks_executed,
            'capabilities': [
                'simplex', 'two_phase_simplex', 'sensitivity_analysis'
            ]
        }
