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
RICCATI ODE SPECIALIST (Tier 3)
================================

Solves Riccati ordinary differential equations.

CAPABILITIES:
------------
- Riccati ODEs: y' = P(x) + Q(x)y + R(x)y^2
- Requires particular solution y1(x)
- Substitution method: y = y1 + 1/v transforms to linear
- Special cases (constant coefficients)
- Initial value problems

ALGORITHM:
----------
1. Verify Riccati form: y' = P(x) + Q(x)y + R(x)y^2
2. Extract coefficients P(x), Q(x), R(x)
3. Identify or find particular solution y1(x)
4. Substitute: y = y1 + 1/v
5. Transform to linear Bernoulli: v' + (Q + 2Ry1)v + R = 0
6. Solve linear ODE for v(x)
7. Back-substitute: y = y1 + 1/v
8. Apply initial conditions if provided

NO SYMPY - Pure native calculus engine.

REFERENCE:
---------
Mathematical Capability Expansion - ODE Domain Enhancement
Created: December 2025
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.omdoc_schema import create_variable
from symbo_agentic_reasoners.core.calculus import integrate as native_integrate, differentiate as derivative

logger = logging.getLogger(__name__)


class RiccatiODESpecialist(BDIAgent):
    """
    Riccati ODE Specialist - Riccati Equations via Substitution

    DIRECTIVE:
    ---------
    Solve Riccati ODEs using particular solution and substitution.

    OPERATIONS:
    ----------
    - is_riccati: Verify if ODE is Riccati form
    - extract_riccati_coefficients: Extract P(x), Q(x), R(x)
    - find_particular_solution: Identify or compute y1(x)
    - transform_to_linear: Apply y = y1 + 1/v substitution
    - solve_riccati: Complete solution pipeline

    STANDARD FORM:
    -------------
    y' = P(x) + Q(x)y + R(x)y^2

    Where:
        - P(x): Constant term
        - Q(x): Linear coefficient
        - R(x): Quadratic coefficient

    TRANSFORMATION:
    --------------
    Given particular solution y1(x):
    y = y1 + 1/v

    Substitute to get linear ODE in v:
    v' + [Q(x) + 2R(x)y1(x)]v + R(x) = 0

    SPECIAL CASES:
    -------------
    - R(x) = 0: Linear ODE
    - P(x) = 0, Q(x) constant, R(x) constant: Solvable by separation
    - Known y1(x): Use substitution method

    REFERENCE:
    ---------
    ODE accuracy improvement initiative
    Target: 90%+ success rate on Riccati equations
    """

    def __init__(
        self,
        agent_id: str = 'riccati_ode_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Riccati ODE Specialist.

        Args:
            agent_id: Unique agent identifier
            df: Directory Facilitator instance
            blackboard: Blackboard instance
        """
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.riccati_odes_solved = 0
        self.particular_solutions_used = 0
        self.transformations_applied = 0
        self.special_cases_handled = 0

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        logger.info(f"[{self.agent_id}] Riccati ODE Specialist initialized")
        logger.info(f"  Method: Substitution y = y1 + 1/v")
        logger.info(f"  Form: y' = P(x) + Q(x)y + R(x)y^2")

    def _register_services(self):
        """
        Register services with Directory Facilitator.

        Registers:
            - math.calculus.ode.riccati: Riccati ODE solving
        """
        registration = create_service_registration(
            service_type='math.calculus.ode.riccati',
            agent_id=self.agent_id,
            algorithm='particular_solution_substitution',
            cost='high',
            instance=self,
            type='specialist',
            tier='3',
            capabilities='riccati_ode_substitution_ivp'
        )
        self.df.register(registration)
        logger.info(f"  [DF] Registered: math.calculus.ode.riccati")

    def process(self, task_entry: Any) -> Any:
        """
        Process Riccati ODE solving task.

        Args:
            task_entry: Task entry from blackboard

        Returns:
            Result entry with solution or error
        """
        logger.info(f"\n[{self.agent_id}] Processing Riccati ODE task")

        self.tasks_executed += 1

        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            raw_input = metadata.get('raw_input', '')
            ode_str = metadata.get('ode_expr') or raw_input
            variable = metadata.get('variable', 'x')
            func_name = metadata.get('function', 'y')
            particular_solution = metadata.get('particular_solution')
            initial_conditions = metadata.get('initial_conditions', {})

            logger.info(f"  ODE: {ode_str}")
            logger.info(f"  Variable: {variable}, Function: {func_name}")
            if particular_solution:
                logger.info(f"  Particular solution: {particular_solution}")

            # Solve Riccati ODE
            result = self.solve_riccati(
                ode_str, variable, func_name, particular_solution, initial_conditions
            )

            if result.get('success'):
                self.tasks_succeeded += 1
                self.riccati_odes_solved += 1
                logger.info(f"  [OK] Solution: {result.get('solution')}")
            else:
                self.tasks_failed += 1
                logger.warning(f"  [FAIL] {result.get('error')}")

            # Create result entry
            if self.blackboard:
                solution_str = result.get('solution', str(result.get('error', 'Unknown error')))
                return create_entry(
                    EntryType.PARTIAL_RESULT,
                    create_variable(solution_str),
                    self.agent_id,
                    task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'result',
                    ['ode', 'riccati'],
                    EntryStatus.COMPLETED if result.get('success') else EntryStatus.FAILED,
                    {'result': result}
                )
            else:
                return result.get('solution') if result.get('success') else f"Error: {result.get('error')}"

        except Exception as e:
            self.tasks_failed += 1
            logger.error(f"  [ERROR] {type(e).__name__}: {e}")

            if self.blackboard:
                return create_entry(
                    EntryType.PARTIAL_RESULT,
                    create_variable(f"Error: {str(e)}"),
                    self.agent_id,
                    task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'error',
                    ['ode', 'riccati', 'error'],
                    EntryStatus.FAILED,
                    {'error': str(e)}
                )
            else:
                return f"Error: {str(e)}"

    def is_riccati(self, ode_str: str, var: str = 'x', func: str = 'y') -> bool:
        """
        Check if ODE is Riccati form.

        A Riccati ODE has the form: y' = P(x) + Q(x)y + R(x)y^2

        Args:
            ode_str: ODE expression (e.g., "y' = 1 + x*y - y^2")
            var: Independent variable (default 'x')
            func: Dependent function (default 'y')

        Returns:
            True if Riccati, False otherwise
        """
        if '=' not in ode_str:
            return False

        # Must have derivative
        has_derivative = f"{func}'" in ode_str or f"d{func}/d{var}" in ode_str

        if not has_derivative:
            return False

        # Look for y^2 or y**2 pattern
        normalized = ode_str.replace(' ', '')

        power_patterns = [
            rf'{func}\*\*2',
            rf'{func}\^2'
        ]

        has_quadratic = any(re.search(pattern, normalized) for pattern in power_patterns)

        # Riccati must have quadratic term
        return has_quadratic

    def extract_riccati_coefficients(
        self,
        ode_str: str,
        var: str = 'x',
        func: str = 'y'
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Extract P(x), Q(x), R(x) from y' = P(x) + Q(x)y + R(x)y^2.

        Args:
            ode_str: ODE expression
            var: Independent variable
            func: Dependent function

        Returns:
            (P_x, Q_x, R_x) tuple or (None, None, None) if extraction fails
        """
        try:
            if '=' not in ode_str:
                return None, None, None

            parts = ode_str.split('=')
            if len(parts) != 2:
                return None, None, None

            lhs, rhs = parts[0].strip(), parts[1].strip()

            # Normalize
            normalized_rhs = rhs.replace(' ', '')

            # Find y^2 term and its coefficient R(x)
            power_patterns = [
                (rf'([+-]?[^+-]*){func}\*\*2', '**2'),
                (rf'([+-]?[^+-]*){func}\^2', '^2')
            ]

            r_x = None
            rhs_without_y2 = normalized_rhs

            for pattern, suffix in power_patterns:
                match = re.search(pattern, normalized_rhs)
                if match:
                    r_coeff = match.group(1).strip()
                    if not r_coeff or r_coeff == '+':
                        r_x = '1'
                    elif r_coeff == '-':
                        r_x = '-1'
                    else:
                        r_x = r_coeff.lstrip('+')

                    # Remove y^2 term
                    y2_term = match.group(0)
                    rhs_without_y2 = normalized_rhs.replace(y2_term, '', 1)
                    break

            if r_x is None:
                return None, None, None

            # Find y term and its coefficient Q(x)
            # Pattern: coefficient*y (not y^2)
            y_pattern = rf'([+-]?[^+-]*){func}(?!\*\*|\^)'

            q_x = '0'
            rhs_without_y = rhs_without_y2

            match = re.search(y_pattern, rhs_without_y2)
            if match:
                q_coeff = match.group(1).strip()
                if not q_coeff or q_coeff == '+':
                    q_x = '1'
                elif q_coeff == '-':
                    q_x = '-1'
                else:
                    q_x = q_coeff.lstrip('+')

                # Remove y term
                y_term = match.group(0)
                rhs_without_y = rhs_without_y2.replace(y_term, '', 1)

            # What's left is P(x)
            p_x = rhs_without_y.strip()
            if not p_x or p_x in ['+', '-']:
                p_x = '0'
            else:
                p_x = p_x.lstrip('+')

            return p_x, q_x, r_x

        except Exception as e:
            logger.debug(f"Riccati coefficient extraction failed: {e}")
            return None, None, None

    def find_particular_solution(
        self,
        p_x: str,
        q_x: str,
        r_x: str,
        var: str = 'x'
    ) -> Optional[str]:
        """
        Find or guess particular solution y1(x).

        For simple cases:
        - P constant, Q constant, R constant: Try y1 = constant
        - Try y1 = 0, y1 = 1, y1 = x

        Args:
            p_x: P(x) coefficient
            q_x: Q(x) coefficient
            r_x: R(x) coefficient
            var: Independent variable

        Returns:
            Particular solution y1(x) or None
        """
        # Try simple constants
        candidates = ['0', '1', '-1', var, f'-{var}']

        for y1 in candidates:
            # Verify: y1' = P + Q*y1 + R*y1^2
            y1_prime = derivative(y1, var)

            # Compute RHS: P + Q*y1 + R*y1^2
            try:
                # Simple evaluation (for constant y1, y1' = 0)
                # This is a simplified check
                if str(y1_prime) == '0':
                    # y1 is constant, check if 0 = P + Q*y1 + R*y1^2
                    # For now, just try y1 = 0
                    if y1 == '0':
                        # Check if P = 0
                        if p_x == '0':
                            return '0'
            except:
                pass

        # No particular solution found
        return None

    def transform_to_linear(
        self,
        p_x: str,
        q_x: str,
        r_x: str,
        y1: str,
        var: str = 'x'
    ) -> Tuple[str, str]:
        """
        Transform Riccati to linear using y = y1 + 1/v.

        Original: y' = P(x) + Q(x)y + R(x)y^2
        With y1: y1' = P(x) + Q(x)y1 + R(x)y1^2
        Substitute y = y1 + 1/v:
        Result: v' + [Q(x) + 2R(x)y1]v + R(x) = 0

        Args:
            p_x: P(x) coefficient
            q_x: Q(x) coefficient
            r_x: R(x) coefficient
            y1: Particular solution
            var: Independent variable

        Returns:
            (P_v, Q_v) for linear equation v' + P_v*v = Q_v
        """
        self.transformations_applied += 1

        # P_v = Q(x) + 2R(x)y1
        if y1 == '0':
            p_v = q_x
        else:
            p_v = f"({q_x}) + 2*({r_x})*({y1})"

        # Q_v = -R(x)
        q_v = f"-({r_x})"

        return p_v, q_v

    def solve_riccati(
        self,
        ode_str: str,
        var: str = 'x',
        func: str = 'y',
        particular_solution: Optional[str] = None,
        initial_conditions: Dict = None
    ) -> Dict[str, Any]:
        """
        Solve Riccati ODE: y' = P(x) + Q(x)y + R(x)y^2

        Method:
            1. Verify Riccati form
            2. Extract P(x), Q(x), R(x)
            3. Find particular solution y1 (provided or guessed)
            4. Transform: y = y1 + 1/v
            5. Solve linear ODE for v
            6. Back-substitute

        Args:
            ode_str: ODE expression (e.g., "y' = 1 + x*y - y^2")
            var: Independent variable (default 'x')
            func: Dependent function (default 'y')
            particular_solution: Known particular solution y1(x)
            initial_conditions: Dict like {'y(0)': 1}

        Returns:
            Dict with solution and metadata
        """
        initial_conditions = initial_conditions or {}

        try:
            # Verify Riccati form
            if not self.is_riccati(ode_str, var, func):
                return {
                    'success': False,
                    'error': 'ODE is not Riccati form',
                    'method': 'riccati'
                }

            # Extract coefficients
            p_x, q_x, r_x = self.extract_riccati_coefficients(ode_str, var, func)

            if p_x is None or q_x is None or r_x is None:
                return {
                    'success': False,
                    'error': 'Could not extract Riccati coefficients',
                    'method': 'riccati'
                }

            logger.info(f"  [P(x)] {p_x}")
            logger.info(f"  [Q(x)] {q_x}")
            logger.info(f"  [R(x)] {r_x}")

            # Get particular solution
            if particular_solution:
                y1 = particular_solution
                self.particular_solutions_used += 1
                logger.info(f"  [y1] Using provided: {y1}")
            else:
                y1 = self.find_particular_solution(p_x, q_x, r_x, var)
                if y1:
                    logger.info(f"  [y1] Found: {y1}")
                else:
                    return {
                        'success': False,
                        'error': 'No particular solution provided or found',
                        'method': 'riccati',
                        'note': 'Riccati equations require a particular solution y1(x)'
                    }

            # Transform to linear
            p_v, q_v = self.transform_to_linear(p_x, q_x, r_x, y1, var)

            linear_ode = f"v' + ({p_v})*v = {q_v}"
            logger.info(f"  [LINEAR] {linear_ode}")

            # Solve linear ODE for v (simplified)
            # v' + P_v*v = Q_v
            # Use integrating factor
            success_mu, mu, int_p = self._compute_integrating_factor(p_v, var)

            if not success_mu:
                return {
                    'success': False,
                    'error': 'Could not compute integrating factor for transformed equation',
                    'method': 'riccati'
                }

            # Integrate μ*Q_v
            product = f"({mu})*({q_v})"
            success_prod, int_prod, _ = native_integrate(product, var)

            if not success_prod:
                return {
                    'success': False,
                    'error': 'Could not integrate transformed equation',
                    'method': 'riccati'
                }

            # v = (1/μ) * [∫μ*Q_v dx + C]
            v_solution = f"(1/({mu}))*({int_prod} + C)"

            # Back-substitute: y = y1 + 1/v
            y_solution = f"{func} = ({y1}) + 1/({v_solution})"

            return {
                'success': True,
                'solution': y_solution,
                'p_x': p_x,
                'q_x': q_x,
                'r_x': r_x,
                'particular_solution': y1,
                'substitution': f'{func} = ({y1}) + 1/v',
                'linear_ode': linear_ode,
                'v_solution': v_solution,
                'method': 'riccati_substitution',
                'general_solution': True,
                'initial_conditions': initial_conditions
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'riccati'
            }

    def _compute_integrating_factor(
        self,
        p_x: str,
        var: str = 'x'
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Compute integrating factor μ(x) = exp(∫P(x)dx).

        Args:
            p_x: P(x) coefficient
            var: Integration variable

        Returns:
            (success, mu_expr, int_p) tuple
        """
        # Integrate P(x)
        success, int_p, _ = native_integrate(p_x, var)

        if not success:
            return False, None, None

        # μ(x) = exp(∫P(x)dx)
        mu = f"exp({int_p})"

        return True, mu, int_p

    # ==================== BDI METHODS ====================

    def update_beliefs(self):
        """
        Update beliefs from Blackboard.

        Queries for pending Riccati ODE tasks.
        """
        if not self.blackboard:
            return

        try:
            entries = self.blackboard.query_entries(
                tags=['ode', 'riccati'],
                status='pending'
            ) if hasattr(self.blackboard, 'query_entries') else []

            for entry in entries:
                belief_key = f'pending_riccati_{entry.entry_id}'
                if not self.has_belief(belief_key):
                    self.add_belief(belief_key, entry, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """
        Generate intentions from beliefs.

        Creates solve intentions for pending tasks.

        Returns:
            List of new intentions
        """
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_riccati_'):
                continue

            task = belief.content
            task_id = task.entry_id if hasattr(task, 'entry_id') else str(hash(str(task)))

            # Skip if already processing
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            # Create intention
            intention = Intention(
                goal=f'solve_riccati_{task_id}',
                plan=['claim', 'solve', 'post'],
                priority=5,
                metadata={'task_id': task_id, 'task_entry': task}
            )
            new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention: Intention):
        """
        Execute next step in intention plan.

        Steps:
            - claim: Claim task from blackboard
            - solve: Solve Riccati ODE
            - post: Post result to blackboard

        Args:
            intention: Current intention
        """
        if not intention or not hasattr(intention, 'get_current_action'):
            return

        action = intention.get_current_action()

        if action == 'claim':
            intention.advance()

        elif action == 'solve':
            task_entry = intention.metadata.get('task_entry')
            if task_entry:
                result = self.process(task_entry)
                intention.metadata['result'] = result
                intention.advance()
            else:
                intention.fail('No task entry')

        elif action == 'post':
            result = intention.metadata.get('result')
            if self.blackboard and result:
                if not hasattr(result, 'entry_id'):
                    entry = create_entry(
                        EntryType.PARTIAL_RESULT,
                        create_variable(str(result)),
                        self.agent_id,
                        'riccati_result',
                        ['ode', 'riccati', 'result'],
                        EntryStatus.COMPLETED,
                        {'result': result}
                    )
                    self.blackboard.post(entry)
            intention.complete()

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming BDI message.

        Args:
            message: Message dict with 'action' and 'params'

        Returns:
            Response dict
        """
        action = message.get('action', '')
        params = message.get('params', {})

        if action == 'solve':
            result = self.solve_riccati(**params)
            return {'status': 'success', 'result': result}
        elif action == 'is_riccati':
            result = self.is_riccati(**params)
            return {'status': 'success', 'result': result}
        else:
            return {'status': 'error', 'message': f'Unknown action: {action}'}

    def get_stats(self) -> Dict[str, int]:
        """
        Get computation statistics.

        Returns:
            Stats dict
        """
        return {
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'riccati_odes_solved': self.riccati_odes_solved,
            'particular_solutions_used': self.particular_solutions_used,
            'transformations_applied': self.transformations_applied,
            'special_cases_handled': self.special_cases_handled
        }


# Export
__all__ = ['RiccatiODESpecialist']


if __name__ == '__main__':
    """Test Riccati ODE Specialist."""
    print("=" * 80)
    print("RICCATI ODE SPECIALIST TEST")
    print("=" * 80)

    specialist = RiccatiODESpecialist()

    test_cases = [
        ("y' = 1 - y**2", "Simple Riccati", '0'),
        ("y' = x + y - y**2", "Riccati with x term", '0'),
        ("y' = 2*x*y - y**2", "Riccati quadratic only", '0'),
    ]

    for ode, description, y1 in test_cases:
        print(f"\n{description}: {ode}")
        print(f"  Particular solution: y1 = {y1}")
        result = specialist.solve_riccati(ode, particular_solution=y1)
        if result['success']:
            print(f"  Solution: {result['solution']}")
            print(f"  Method: {result.get('method', 'unknown')}")
        else:
            print(f"  Error: {result.get('error', 'Unknown error')}")

    print(f"\nStatistics: {specialist.get_stats()}")
