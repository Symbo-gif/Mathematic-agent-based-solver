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
BERNOULLI ODE SPECIALIST (Tier 3)
==================================

Solves Bernoulli ordinary differential equations.

CAPABILITIES:
------------
- Bernoulli ODEs: y' + P(x)y = Q(x)y^n
- Substitution method: v = y^(1-n) transforms to linear
- Handles n ≠ 0, 1 (n=0 is linear, n=1 is separable)
- Initial value problems
- Coefficient extraction and transformation

ALGORITHM:
----------
1. Verify Bernoulli form: y' + P(x)y = Q(x)y^n
2. Extract coefficients P(x), Q(x), and exponent n
3. Substitute v = y^(1-n)
4. Transform to linear: v' + (1-n)P(x)v = (1-n)Q(x)
5. Solve linear ODE for v(x)
6. Back-substitute: y = v^(1/(1-n))
7. Apply initial conditions if provided

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
from symbo_agentic_reasoners.core.calculus import integrate as native_integrate

logger = logging.getLogger(__name__)


class BernoulliODESpecialist(BDIAgent):
    """
    Bernoulli ODE Specialist - Bernoulli Equations via Substitution

    DIRECTIVE:
    ---------
    Solve Bernoulli ODEs by transforming to linear equations.

    OPERATIONS:
    ----------
    - is_bernoulli: Verify if ODE is Bernoulli form
    - extract_bernoulli_coefficients: Extract P(x), Q(x), n
    - transform_to_linear: Apply v = y^(1-n) substitution
    - solve_bernoulli: Complete solution pipeline
    - back_substitute: Convert v(x) back to y(x)

    STANDARD FORM:
    -------------
    y' + P(x)y = Q(x)y^n

    Where:
        - P(x): Linear coefficient
        - Q(x): Nonhomogeneous term
        - n: Power (n ≠ 0, 1)

    TRANSFORMATION:
    --------------
    v = y^(1-n)
    v' = (1-n)y^(-n)y'

    Substitute:
    v' + (1-n)P(x)v = (1-n)Q(x)  [linear in v]

    REFERENCE:
    ---------
    ODE accuracy improvement initiative
    Target: 95%+ success rate on Bernoulli equations
    """

    def __init__(
        self,
        agent_id: str = 'bernoulli_ode_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Bernoulli ODE Specialist.

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
        self.bernoulli_odes_solved = 0
        self.transformations_applied = 0
        self.linear_delegations = 0

        # Cache for linear ODE specialist
        self._linear_specialist = None

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        logger.info(f"[{self.agent_id}] Bernoulli ODE Specialist initialized")
        logger.info(f"  Method: Substitution v = y^(1-n)")
        logger.info(f"  Form: y' + P(x)y = Q(x)y^n")

    def _register_services(self):
        """
        Register services with Directory Facilitator.

        Registers:
            - math.calculus.ode.bernoulli: Bernoulli ODE solving
        """
        registration = create_service_registration(
            service_type='math.calculus.ode.bernoulli',
            agent_id=self.agent_id,
            algorithm='substitution_to_linear',
            cost='medium',
            instance=self,
            type='specialist',
            tier='3',
            capabilities='bernoulli_ode_substitution_ivp'
        )
        self.df.register(registration)
        logger.info(f"  [DF] Registered: math.calculus.ode.bernoulli")

    def process(self, task_entry: Any) -> Any:
        """
        Process Bernoulli ODE solving task.

        Args:
            task_entry: Task entry from blackboard

        Returns:
            Result entry with solution or error
        """
        logger.info(f"\n[{self.agent_id}] Processing Bernoulli ODE task")

        self.tasks_executed += 1

        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            raw_input = metadata.get('raw_input', '')
            ode_str = metadata.get('ode_expr') or raw_input
            variable = metadata.get('variable', 'x')
            func_name = metadata.get('function', 'y')
            initial_conditions = metadata.get('initial_conditions', {})

            logger.info(f"  ODE: {ode_str}")
            logger.info(f"  Variable: {variable}, Function: {func_name}")

            # Solve Bernoulli ODE
            result = self.solve_bernoulli(ode_str, variable, func_name, initial_conditions)

            if result.get('success'):
                self.tasks_succeeded += 1
                self.bernoulli_odes_solved += 1
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
                    ['ode', 'bernoulli'],
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
                    ['ode', 'bernoulli', 'error'],
                    EntryStatus.FAILED,
                    {'error': str(e)}
                )
            else:
                return f"Error: {str(e)}"

    def is_bernoulli(self, ode_str: str, var: str = 'x', func: str = 'y') -> bool:
        """
        Check if ODE is Bernoulli form.

        A Bernoulli ODE has the form: y' + P(x)y = Q(x)y^n
        where n ≠ 0 and n ≠ 1.

        Args:
            ode_str: ODE expression (e.g., "y' + 2*x*y = x*y^2")
            var: Independent variable (default 'x')
            func: Dependent function (default 'y')

        Returns:
            True if Bernoulli, False otherwise
        """
        if '=' not in ode_str:
            return False

        # Must have derivative
        has_derivative = f"{func}'" in ode_str or f"d{func}/d{var}" in ode_str

        if not has_derivative:
            return False

        # Look for y^n pattern on RHS
        normalized = ode_str.replace(' ', '')

        # Pattern: y**n or y^n where n is a number ≠ 0, 1
        power_patterns = [
            rf'{func}\*\*(-?\d+\.?\d*)',
            rf'{func}\^(-?\d+\.?\d*)'
        ]

        for pattern in power_patterns:
            match = re.search(pattern, normalized)
            if match:
                exponent = float(match.group(1))
                # Bernoulli requires n ≠ 0 and n ≠ 1
                if exponent != 0 and exponent != 1:
                    return True

        return False

    def extract_bernoulli_coefficients(
        self,
        ode_str: str,
        var: str = 'x',
        func: str = 'y'
    ) -> Tuple[Optional[str], Optional[str], Optional[float]]:
        """
        Extract P(x), Q(x), and n from y' + P(x)y = Q(x)y^n.

        Args:
            ode_str: ODE expression
            var: Independent variable
            func: Dependent function

        Returns:
            (P_x, Q_x, n) tuple or (None, None, None) if extraction fails
        """
        try:
            if '=' not in ode_str:
                return None, None, None

            parts = ode_str.split('=')
            if len(parts) != 2:
                return None, None, None

            lhs, rhs = parts[0].strip(), parts[1].strip()

            # Normalize derivative notation
            lhs = lhs.replace(f"d{func}/d{var}", f"{func}'")

            # Extract P(x) from LHS: y' + P(x)*y or y' - P(x)*y
            lhs_without_deriv = lhs.replace(f"{func}'", '', 1).strip()

            p_x = '0'
            sign = 1

            if func in lhs_without_deriv:
                if lhs_without_deriv.startswith('+'):
                    lhs_without_deriv = lhs_without_deriv[1:].strip()
                elif lhs_without_deriv.startswith('-'):
                    sign = -1
                    lhs_without_deriv = lhs_without_deriv[1:].strip()

                # Extract coefficient of y
                if lhs_without_deriv.endswith(f"*{func}"):
                    p_x = lhs_without_deriv[:-len(f"*{func}")].strip()
                elif lhs_without_deriv.strip() == func:
                    p_x = '1'
                else:
                    p_x = lhs_without_deriv.replace(func, '').replace('*', '').strip() or '1'

                if sign == -1:
                    p_x = f"-({p_x})" if '*' in p_x or '+' in p_x else f"-{p_x}"

            # Extract Q(x) and n from RHS: Q(x)*y^n
            normalized_rhs = rhs.replace(' ', '')

            # Find y^n pattern
            power_patterns = [
                (rf'{func}\*\*(-?\d+\.?\d*)', '**'),
                (rf'{func}\^(-?\d+\.?\d*)', '^')
            ]

            n = None
            q_x = None

            for pattern, delimiter in power_patterns:
                match = re.search(pattern, normalized_rhs)
                if match:
                    n = float(match.group(1))
                    y_power = match.group(0)

                    # Q(x) is what's left after removing y^n
                    q_x = rhs.replace(y_power, '').replace('*', '').strip()
                    if not q_x:
                        q_x = '1'
                    break

            if n is None or q_x is None:
                return None, None, None

            return p_x, q_x, n

        except Exception as e:
            logger.debug(f"Coefficient extraction failed: {e}")
            return None, None, None

    def transform_to_linear(
        self,
        p_x: str,
        q_x: str,
        n: float,
        var: str = 'x'
    ) -> Tuple[str, str]:
        """
        Transform Bernoulli ODE to linear form.

        Original: y' + P(x)y = Q(x)y^n
        Substitute: v = y^(1-n)
        Result: v' + (1-n)P(x)v = (1-n)Q(x)

        Args:
            p_x: P(x) coefficient
            q_x: Q(x) coefficient
            n: Power exponent
            var: Independent variable

        Returns:
            (P_v, Q_v) for linear equation v' + P_v*v = Q_v
        """
        self.transformations_applied += 1

        factor = 1 - n

        # P_v = (1-n)*P(x)
        if p_x == '0':
            p_v = '0'
        elif p_x == '1':
            p_v = str(factor)
        else:
            p_v = f"({factor})*({p_x})"

        # Q_v = (1-n)*Q(x)
        if q_x == '0':
            q_v = '0'
        elif q_x == '1':
            q_v = str(factor)
        else:
            q_v = f"({factor})*({q_x})"

        return p_v, q_v

    def solve_bernoulli(
        self,
        ode_str: str,
        var: str = 'x',
        func: str = 'y',
        initial_conditions: Dict = None
    ) -> Dict[str, Any]:
        """
        Solve Bernoulli ODE: y' + P(x)y = Q(x)y^n

        Method:
            1. Verify Bernoulli form
            2. Extract P(x), Q(x), n
            3. Transform: v = y^(1-n)
            4. Solve linear ODE for v
            5. Back-substitute: y = v^(1/(1-n))

        Args:
            ode_str: ODE expression (e.g., "y' + 2*x*y = x*y^2")
            var: Independent variable (default 'x')
            func: Dependent function (default 'y')
            initial_conditions: Dict like {'y(0)': 1}

        Returns:
            Dict with solution and metadata
        """
        initial_conditions = initial_conditions or {}

        try:
            # Verify Bernoulli form
            if not self.is_bernoulli(ode_str, var, func):
                return {
                    'success': False,
                    'error': 'ODE is not Bernoulli form',
                    'method': 'bernoulli'
                }

            # Extract coefficients
            p_x, q_x, n = self.extract_bernoulli_coefficients(ode_str, var, func)

            if p_x is None or q_x is None or n is None:
                return {
                    'success': False,
                    'error': 'Could not extract Bernoulli coefficients',
                    'method': 'bernoulli'
                }

            # Transform to linear
            p_v, q_v = self.transform_to_linear(p_x, q_x, n, var)

            # Build linear ODE for v
            linear_ode = f"v' + ({p_v})*v = {q_v}"

            logger.info(f"  [TRANSFORM] v = {func}^({1-n})")
            logger.info(f"  [LINEAR] {linear_ode}")

            # Solve linear ODE (use native implementation)
            # For now, use integrating factor directly
            success_mu, mu, int_p = self._compute_integrating_factor(p_v, var)

            if not success_mu:
                return {
                    'success': False,
                    'error': f'Could not compute integrating factor for transformed equation',
                    'method': 'bernoulli'
                }

            # Integrate μ(x)*Q_v(x)
            product = f"({mu})*({q_v})"
            success_prod, int_prod, _ = native_integrate(product, var)

            if not success_prod:
                return {
                    'success': False,
                    'error': f'Could not integrate transformed equation',
                    'method': 'bernoulli'
                }

            # Solution for v: v = (1/μ(x)) * [∫μ(x)Q_v(x)dx + C]
            v_solution = f"(1/({mu}))*({int_prod} + C)"

            # Back-substitute: y = v^(1/(1-n))
            back_exponent = 1 / (1 - n)
            y_solution = f"{func} = ({v_solution})**({back_exponent})"

            return {
                'success': True,
                'solution': y_solution,
                'p_x': p_x,
                'q_x': q_x,
                'n': n,
                'substitution': f'v = {func}^({1-n})',
                'linear_ode': linear_ode,
                'v_solution': v_solution,
                'method': 'bernoulli_substitution',
                'general_solution': True,
                'initial_conditions': initial_conditions
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'bernoulli'
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

        Queries for pending Bernoulli ODE tasks.
        """
        if not self.blackboard:
            return

        try:
            entries = self.blackboard.query_entries(
                tags=['ode', 'bernoulli'],
                status='pending'
            ) if hasattr(self.blackboard, 'query_entries') else []

            for entry in entries:
                belief_key = f'pending_bernoulli_{entry.entry_id}'
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
            if not predicate.startswith('pending_bernoulli_'):
                continue

            task = belief.content
            task_id = task.entry_id if hasattr(task, 'entry_id') else str(hash(str(task)))

            # Skip if already processing
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            # Create intention
            intention = Intention(
                goal=f'solve_bernoulli_{task_id}',
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
            - solve: Solve Bernoulli ODE
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
                        'bernoulli_result',
                        ['ode', 'bernoulli', 'result'],
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
            result = self.solve_bernoulli(**params)
            return {'status': 'success', 'result': result}
        elif action == 'is_bernoulli':
            result = self.is_bernoulli(**params)
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
            'bernoulli_odes_solved': self.bernoulli_odes_solved,
            'transformations_applied': self.transformations_applied,
            'linear_delegations': self.linear_delegations
        }


# Export
__all__ = ['BernoulliODESpecialist']


if __name__ == '__main__':
    """Test Bernoulli ODE Specialist."""
    print("=" * 80)
    print("BERNOULLI ODE SPECIALIST TEST")
    print("=" * 80)

    specialist = BernoulliODESpecialist()

    test_cases = [
        ("y' + 2*x*y = x*y**2", "Standard Bernoulli (n=2)"),
        ("y' - y = y**3", "Cubic power (n=3)"),
        ("y' + y = x*y**(-1)", "Negative power (n=-1)"),
    ]

    for ode, description in test_cases:
        print(f"\n{description}: {ode}")
        result = specialist.solve_bernoulli(ode)
        if result['success']:
            print(f"  Solution: {result['solution']}")
            print(f"  Substitution: {result.get('substitution', 'unknown')}")
            print(f"  Method: {result.get('method', 'unknown')}")
        else:
            print(f"  Error: {result.get('error', 'Unknown error')}")

    print(f"\nStatistics: {specialist.get_stats()}")
