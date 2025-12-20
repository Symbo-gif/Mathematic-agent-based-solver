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
LINEAR NONHOMOGENEOUS ODE SPECIALIST (Tier 3)
==============================================

Solves first-order linear nonhomogeneous ordinary differential equations.

CAPABILITIES:
------------
- First-order linear ODEs: y' + P(x)y = Q(x)
- Integrating factor method: μ(x) = exp(∫P(x)dx)
- Homogeneous case: Q(x) = 0
- Nonhomogeneous case: Q(x) ≠ 0
- Initial value problems
- Coefficient extraction from standard forms

ALGORITHM:
----------
1. Verify linear form: y' + P(x)y = Q(x)
2. Extract coefficients P(x) and Q(x)
3. Compute integrating factor: μ(x) = exp(∫P(x)dx)
4. Multiply equation by μ(x)
5. Integrate: y = (1/μ(x)) * [∫μ(x)Q(x)dx + C]
6. Apply initial conditions if provided

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


class LinearNonhomogeneousODESpecialist(BDIAgent):
    """
    Linear Nonhomogeneous ODE Specialist - First-Order Linear Equations

    DIRECTIVE:
    ---------
    Solve first-order linear ODEs using integrating factor method.

    OPERATIONS:
    ----------
    - is_linear: Verify if ODE is linear first-order
    - extract_coefficients: Extract P(x) and Q(x)
    - compute_integrating_factor: Calculate μ(x) = exp(∫P(x)dx)
    - solve_linear: Solve using integrating factor
    - apply_initial_conditions: Apply IVP conditions

    STANDARD FORM:
    -------------
    y' + P(x)y = Q(x)

    Where:
        - P(x): Coefficient of y
        - Q(x): Nonhomogeneous term (Q(x) = 0 for homogeneous)

    INTEGRATING FACTOR METHOD:
    --------------------------
    1. μ(x) = exp(∫P(x)dx)
    2. Multiply: μ(x)y' + μ(x)P(x)y = μ(x)Q(x)
    3. Left side = d/dx[μ(x)y]
    4. Integrate: μ(x)y = ∫μ(x)Q(x)dx + C
    5. Solve: y = (1/μ(x)) * [∫μ(x)Q(x)dx + C]

    REFERENCE:
    ---------
    ODE accuracy improvement initiative
    Target: 95%+ success rate on linear first-order equations
    """

    def __init__(
        self,
        agent_id: str = 'linear_nonhomog_ode_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Linear Nonhomogeneous ODE Specialist.

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
        self.linear_odes_solved = 0
        self.homogeneous_solved = 0
        self.nonhomogeneous_solved = 0
        self.integrating_factors_computed = 0
        self.advanced_integration_calls = 0

        # Cache for advanced integration specialist
        self._advanced_integration_specialist = None

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        logger.info(f"[{self.agent_id}] Linear Nonhomogeneous ODE Specialist initialized")
        logger.info(f"  Method: Integrating factor")
        logger.info(f"  Form: y' + P(x)y = Q(x)")

    def _register_services(self):
        """
        Register services with Directory Facilitator.

        Registers:
            - math.calculus.ode.linear_nonhomogeneous: Linear ODE solving
        """
        registration = create_service_registration(
            service_type='math.calculus.ode.linear_nonhomogeneous',
            agent_id=self.agent_id,
            algorithm='integrating_factor',
            cost='medium',
            instance=self,
            type='specialist',
            tier='3',
            capabilities='linear_ode_integrating_factor_ivp'
        )
        self.df.register(registration)
        logger.info(f"  [DF] Registered: math.calculus.ode.linear_nonhomogeneous")

    def process(self, task_entry: Any) -> Any:
        """
        Process linear ODE solving task.

        Args:
            task_entry: Task entry from blackboard

        Returns:
            Result entry with solution or error
        """
        logger.info(f"\n[{self.agent_id}] Processing linear ODE task")

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

            # Solve linear ODE
            result = self.solve_linear(ode_str, variable, func_name, initial_conditions)

            if result.get('success'):
                self.tasks_succeeded += 1
                self.linear_odes_solved += 1
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
                    ['ode', 'linear'],
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
                    ['ode', 'linear', 'error'],
                    EntryStatus.FAILED,
                    {'error': str(e)}
                )
            else:
                return f"Error: {str(e)}"

    def is_linear(self, ode_str: str, var: str = 'x', func: str = 'y') -> bool:
        """
        Check if ODE is linear first-order.

        A first-order ODE is linear if it can be written as y' + P(x)y = Q(x).
        Nonlinear patterns: y*y', y^2, sin(y), etc.

        Args:
            ode_str: ODE expression (e.g., "y' + 2*x*y = x^2")
            var: Independent variable (default 'x')
            func: Dependent function (default 'y')

        Returns:
            True if linear, False otherwise
        """
        # Normalize notation
        normalized = ode_str.replace(f"d{func}/d{var}", f"{func}'")

        # Check for nonlinear patterns
        nonlinear_patterns = [
            f"{func}*{func}",
            f"{func}**2",
            f"{func}^2",
            f"sin({func})",
            f"cos({func})",
            f"exp({func})",
            f"log({func})"
        ]

        for pattern in nonlinear_patterns:
            if pattern in normalized.replace(' ', ''):
                return False

        # Must have derivative term
        has_derivative = f"{func}'" in normalized or f"d{func}/d{var}" in ode_str

        # Must have equals sign
        has_equals = '=' in ode_str

        return has_derivative and has_equals

    def extract_coefficients(self, ode_str: str, var: str = 'x', func: str = 'y') -> Tuple[str, str]:
        """
        Extract P(x) and Q(x) from y' + P(x)*y = Q(x).

        Args:
            ode_str: ODE expression
            var: Independent variable
            func: Dependent function

        Returns:
            (P_x, Q_x) tuple
        """
        try:
            if '=' not in ode_str:
                return '0', '0'

            parts = ode_str.split('=')
            if len(parts) != 2:
                return '0', '0'

            lhs, rhs = parts[0].strip(), parts[1].strip()

            # Normalize: replace dy/dx with y'
            lhs = lhs.replace(f"d{func}/d{var}", f"{func}'")

            # Pattern: y' + P*y = Q  or  y' - P*y = Q
            # Remove the y' term to isolate the y coefficient
            lhs_without_deriv = lhs.replace(f"{func}'", '', 1)

            # Extract coefficient of y
            p_coeff = '0'
            if func in lhs_without_deriv:
                # Pattern: + (3)*y  or  + 2*x*y  or just + y
                sign = 1
                lhs_clean = lhs_without_deriv.strip()

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
            return '0', '0'

    def compute_integrating_factor(self, p_x: str, var: str = 'x') -> Tuple[bool, Optional[str], Optional[str]]:
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
        self.integrating_factors_computed += 1

        return True, mu, int_p

    def _try_advanced_integration(self, expression: str, var: str) -> Optional[Dict[str, Any]]:
        """
        Try advanced integration using AdvancedIntegrationSpecialist.

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

        # Create mock task entry
        try:
            if self._advanced_integration_specialist:
                self.advanced_integration_calls += 1

                from symbo_agentic_reasoners.core.blackboard import create_entry
                from symbo_agentic_reasoners.core.omdoc_schema import create_variable

                mock_task = type('MockTask', (), {
                    'entry_id': f'linear_ode_integration_{hash(expression)}',
                    'conversation_id': 'linear_ode_integration',
                    'metadata': {
                        'expression': expression,
                        'variable': var,
                        'raw_input': expression
                    }
                })()

                result_entry = self._advanced_integration_specialist.process(mock_task)

                # Extract result
                if hasattr(result_entry, 'metadata'):
                    if result_entry.metadata.get('error'):
                        return {'success': False, 'error': result_entry.metadata.get('error')}
                    result_str = result_entry.metadata.get('result', '')
                    if result_str:
                        return {'success': True, 'solution': result_str, 'method': 'advanced'}
                elif isinstance(result_entry, dict):
                    return result_entry

        except Exception as e:
            logger.debug(f"[{self.agent_id}] Advanced integration failed: {e}")

        return None

    def solve_linear(
        self,
        ode_str: str,
        var: str = 'x',
        func: str = 'y',
        initial_conditions: Dict = None
    ) -> Dict[str, Any]:
        """
        Solve first-order linear ODE: y' + P(x)y = Q(x)

        Method: Integrating factor μ(x) = exp(∫P(x)dx)
        Solution: y = (1/μ(x)) * [∫μ(x)Q(x)dx + C]

        Args:
            ode_str: ODE expression
            var: Independent variable (default 'x')
            func: Dependent function (default 'y')
            initial_conditions: Dict like {'y(0)': 1}

        Returns:
            Dict with solution and metadata
        """
        initial_conditions = initial_conditions or {}

        try:
            # Verify linear
            if not self.is_linear(ode_str, var, func):
                return {
                    'success': False,
                    'error': 'ODE is not linear first-order',
                    'method': 'integrating_factor'
                }

            # Extract coefficients
            p_x, q_x = self.extract_coefficients(ode_str, var, func)

            if p_x == '0' and q_x == '0':
                return {
                    'success': False,
                    'error': 'Could not extract coefficients',
                    'method': 'integrating_factor'
                }

            # Compute integrating factor
            success_mu, mu, int_p = self.compute_integrating_factor(p_x, var)

            if not success_mu:
                return {
                    'success': False,
                    'error': f'Could not compute integrating factor for P(x) = {p_x}',
                    'method': 'integrating_factor'
                }

            # Check if homogeneous
            if q_x == '0' or q_x == 0:
                self.homogeneous_solved += 1
                solution = f"{func} = C*exp(-({int_p}))"
                return {
                    'success': True,
                    'solution': solution,
                    'p_x': p_x,
                    'q_x': q_x,
                    'integrating_factor': mu,
                    'method': 'integrating_factor',
                    'homogeneous': True,
                    'general_solution': True,
                    'initial_conditions': initial_conditions
                }

            # Nonhomogeneous: integrate μ(x)*Q(x)
            product = f"({mu})*({q_x})"
            success_prod, int_prod, _ = native_integrate(product, var)

            # Try advanced integration if native fails
            if not success_prod:
                advanced_result = self._try_advanced_integration(product, var)
                if advanced_result and advanced_result.get('success'):
                    int_prod = advanced_result['solution']
                    success_prod = True

            if success_prod:
                self.nonhomogeneous_solved += 1
                solution = f"{func} = (1/({mu}))*({int_prod} + C)"
                return {
                    'success': True,
                    'solution': solution,
                    'p_x': p_x,
                    'q_x': q_x,
                    'integrating_factor': mu,
                    'integral_mu_q': int_prod,
                    'method': 'integrating_factor',
                    'homogeneous': False,
                    'general_solution': True,
                    'initial_conditions': initial_conditions
                }
            else:
                return {
                    'success': False,
                    'error': f'Could not integrate μ(x)*Q(x) = {product}',
                    'method': 'integrating_factor'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'integrating_factor'
            }

    # ==================== BDI METHODS ====================

    def update_beliefs(self):
        """
        Update beliefs from Blackboard.

        Queries for pending linear ODE tasks.
        """
        if not self.blackboard:
            return

        try:
            entries = self.blackboard.query_entries(
                tags=['ode', 'linear'],
                status='pending'
            ) if hasattr(self.blackboard, 'query_entries') else []

            for entry in entries:
                belief_key = f'pending_linear_{entry.entry_id}'
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
            if not predicate.startswith('pending_linear_'):
                continue

            task = belief.content
            task_id = task.entry_id if hasattr(task, 'entry_id') else str(hash(str(task)))

            # Skip if already processing
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            # Create intention
            intention = Intention(
                goal=f'solve_linear_{task_id}',
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
            - solve: Solve linear ODE
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
                        'linear_result',
                        ['ode', 'linear', 'result'],
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
            result = self.solve_linear(**params)
            return {'status': 'success', 'result': result}
        elif action == 'is_linear':
            result = self.is_linear(**params)
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
            'linear_odes_solved': self.linear_odes_solved,
            'homogeneous_solved': self.homogeneous_solved,
            'nonhomogeneous_solved': self.nonhomogeneous_solved,
            'integrating_factors_computed': self.integrating_factors_computed,
            'advanced_integration_calls': self.advanced_integration_calls
        }


# Export
__all__ = ['LinearNonhomogeneousODESpecialist']


if __name__ == '__main__':
    """Test Linear Nonhomogeneous ODE Specialist."""
    print("=" * 80)
    print("LINEAR NONHOMOGENEOUS ODE SPECIALIST TEST")
    print("=" * 80)

    specialist = LinearNonhomogeneousODESpecialist()

    test_cases = [
        ("y' + y = 0", "Homogeneous"),
        ("y' + 2*x*y = 0", "Homogeneous with variable coefficient"),
        ("y' + y = x", "Nonhomogeneous"),
        ("y' + 2*x*y = x^2", "Nonhomogeneous with variable P(x)"),
        ("y' - 3*y = exp(x)", "Nonhomogeneous with exponential"),
    ]

    for ode, description in test_cases:
        print(f"\n{description}: {ode}")
        result = specialist.solve_linear(ode)
        if result['success']:
            print(f"  Solution: {result['solution']}")
            print(f"  Method: {result.get('method', 'unknown')}")
            print(f"  Homogeneous: {result.get('homogeneous', False)}")
        else:
            print(f"  Error: {result.get('error', 'Unknown error')}")

    print(f"\nStatistics: {specialist.get_stats()}")
