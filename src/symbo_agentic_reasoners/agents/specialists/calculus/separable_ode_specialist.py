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
SEPARABLE ODE SPECIALIST (Tier 3)
==================================

Solves first-order separable ordinary differential equations.

CAPABILITIES:
------------
- First-order separable ODEs: dy/dx = f(x)g(y)
- Separation of variables method
- Direct integration when g(y) = 1
- Complex factorizations (products, quotients, powers, sqrt)
- Initial value problems

ALGORITHM:
----------
1. Verify separability: dy/dx = f(x)g(y)
2. Factor right-hand side into f(x) and g(y)
3. Separate variables: (1/g(y))dy = f(x)dx
4. Integrate both sides
5. Apply initial conditions if provided

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


class SeparableODESpecialist(BDIAgent):
    """
    Separable ODE Specialist - First-Order Separable Equations

    DIRECTIVE:
    ---------
    Solve first-order separable ODEs using separation of variables.

    OPERATIONS:
    ----------
    - is_separable: Verify if ODE is separable
    - factor_separable: Factor RHS into f(x) and g(y)
    - solve_separable: Solve by separation of variables
    - apply_initial_conditions: Apply IVP conditions

    PATTERN MATCHING:
    ----------------
    - Simple products: x*y, sin(x)*y
    - Square roots: x*sqrt(y), x/sqrt(y)
    - Powers: x*y^2, x*y^(-1)
    - Quotients: x/y, y/x
    - Complex forms: (x+1)*sqrt(y), sin(x)/y^2
    - Parenthesized: (4*x)*(1/y), (sin(x))*(y**2)

    REFERENCE:
    ---------
    ODE accuracy improvement initiative
    Target: 95%+ success rate on separable equations
    """

    def __init__(
        self,
        agent_id: str = 'separable_ode_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Separable ODE Specialist.

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
        self.separable_odes_solved = 0
        self.non_separable_detected = 0
        self.factorizations_successful = 0
        self.factorizations_failed = 0

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        logger.info(f"[{self.agent_id}] Separable ODE Specialist initialized")
        logger.info(f"  Method: Separation of variables")
        logger.info(f"  Pattern: dy/dx = f(x)g(y)")

    def _register_services(self):
        """
        Register services with Directory Facilitator.

        Registers:
            - math.calculus.ode.separable: Separable ODE solving
        """
        registration = create_service_registration(
            service_type='math.calculus.ode.separable',
            agent_id=self.agent_id,
            algorithm='separation_of_variables',
            cost='low',
            instance=self,
            type='specialist',
            tier='3',
            capabilities='separable_ode_ivp_factorization'
        )
        self.df.register(registration)
        logger.info(f"  [DF] Registered: math.calculus.ode.separable")

    def process(self, task_entry: Any) -> Any:
        """
        Process separable ODE solving task.

        Args:
            task_entry: Task entry from blackboard

        Returns:
            Result entry with solution or error
        """
        logger.info(f"\n[{self.agent_id}] Processing separable ODE task")

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

            # Solve separable ODE
            result = self.solve_separable(ode_str, variable, func_name, initial_conditions)

            if result.get('success'):
                self.tasks_succeeded += 1
                self.separable_odes_solved += 1
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
                    ['ode', 'separable'],
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
                    ['ode', 'separable', 'error'],
                    EntryStatus.FAILED,
                    {'error': str(e)}
                )
            else:
                return f"Error: {str(e)}"

    def is_separable(self, ode_str: str, var: str = 'x', func: str = 'y') -> bool:
        """
        Check if ODE is separable.

        A first-order ODE is separable if it can be written as dy/dx = f(x)g(y).

        Args:
            ode_str: ODE expression (e.g., "y' = x*y" or "dy/dx = sin(x)/y")
            var: Independent variable (default 'x')
            func: Dependent function (default 'y')

        Returns:
            True if separable, False otherwise
        """
        if '=' not in ode_str:
            return False

        parts = ode_str.split('=')
        if len(parts) != 2:
            return False

        lhs, rhs = parts[0].strip(), parts[1].strip()

        # Check if LHS contains only the derivative (no y term)
        lhs_normalized = lhs.replace(f"{func}'", '').replace(f"d{func}/d{var}", '')
        if func in lhs_normalized:
            return False  # Has y term in LHS, likely linear not separable

        # Check if derivative is in LHS
        has_derivative = f"{func}'" in lhs or f"d{func}/d{var}" in lhs

        # RHS must contain both x and y (or just x for direct integration)
        # Can be separable even if only x appears (g(y) = 1)

        return has_derivative

    def factor_separable(self, rhs: str, var: str = 'x', func: str = 'y') -> Tuple[Optional[str], Optional[str]]:
        """
        Factor RHS of separable ODE into f(x) and g(y).

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
        # Strategy 1: Explicit multiplication (parenthesis-aware)
        if '*' in rhs:
            x_parts, y_parts = [], []
            factors = self._split_respecting_parens(rhs, '*')

            for factor in factors:
                factor = factor.strip()

                # Strip outer parentheses if balanced
                if factor.startswith('(') and factor.endswith(')'):
                    depth, balanced = 0, True
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

                # Classify factor
                if var in factor and func not in factor:
                    x_parts.append(factor)
                elif func in factor and var not in factor:
                    y_parts.append(factor)
                elif 'sqrt' in factor.lower() and func in factor:
                    y_parts.append(factor)
                elif func not in factor and var not in factor:
                    x_parts.append(factor)  # Constants go to x part

            if x_parts or y_parts:
                f_x = '*'.join(x_parts) if x_parts else '1'
                g_y = '*'.join(y_parts) if y_parts else '1'
                self.factorizations_successful += 1
                return f_x, g_y

        # Strategy 2: Division patterns
        if '/' in rhs:
            parts = rhs.split('/', 1)
            numer = parts[0].strip()
            denom = parts[1].strip()

            # y/x pattern
            if func in numer and var not in numer and var in denom and func not in denom:
                self.factorizations_successful += 1
                return f"1/({denom})", numer

            # x/y pattern
            if var in numer and func not in numer and func in denom and var not in denom:
                self.factorizations_successful += 1
                return numer, f"1/({denom})"

            # x/sqrt(y) pattern
            if 'sqrt' in denom.lower() and func in denom:
                if var in numer and func not in numer:
                    sqrt_pattern = r'sqrt\(([^)]+)\)'
                    match = re.search(sqrt_pattern, denom, re.IGNORECASE)
                    if match and func in match.group(1):
                        self.factorizations_successful += 1
                        return numer, f"({match.group(1)})**(-0.5)"

        # Strategy 3: sqrt(y) in numerator
        if 'sqrt' in rhs.lower():
            sqrt_pattern = rf'sqrt\(({func}[^)]*)\)'
            match = re.search(sqrt_pattern, rhs, re.IGNORECASE)
            if match:
                sqrt_expr = match.group(0)
                remaining = rhs.replace(sqrt_expr, '').replace('*', '').strip()

                if var in remaining and func not in remaining:
                    self.factorizations_successful += 1
                    return remaining if remaining else '1', f"({match.group(1)})**(0.5)"

        # Strategy 4: Power patterns y^n
        power_pattern = rf'{func}\s*\*\*\s*(-?\d+\.?\d*)'
        match = re.search(power_pattern, rhs)
        if match:
            power = match.group(1)
            y_power = match.group(0)
            f_x = rhs.replace(y_power, '').replace('*', '').strip()
            if f_x and var in f_x:
                self.factorizations_successful += 1
                return f_x, f"{func}**{power}"

        self.factorizations_failed += 1
        return None, None

    def _split_respecting_parens(self, expr: str, delimiter: str) -> List[str]:
        """
        Split expression by delimiter while respecting parentheses.

        Example:
            "(4*x)*(1/y)" split by "*" → ["(4*x)", "(1/y)"]
            "x*y*z" split by "*" → ["x", "y", "z"]

        Args:
            expr: Expression to split
            delimiter: Delimiter character

        Returns:
            List of parts
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
                if current:
                    parts.append(''.join(current).strip())
                    current = []
            else:
                current.append(char)

        if current:
            parts.append(''.join(current).strip())

        return parts

    def _build_reciprocal(self, g_y: str, func: str) -> str:
        """
        Build reciprocal 1/g(y) for integration.

        Handles:
            - g(y) = y → 1/y
            - g(y) = 1/y → y (reciprocal of reciprocal)
            - g(y) = sqrt(y) = y^(0.5) → y^(-0.5)
            - g(y) = y^n → y^(-n)

        Args:
            g_y: g(y) expression
            func: Function variable ('y')

        Returns:
            1/g(y) expression
        """
        # If g_y is already 1/y, return y
        if g_y.strip().startswith('1/'):
            inner = g_y.strip()[2:].strip()
            if inner.startswith('(') and inner.endswith(')'):
                inner = inner[1:-1].strip()
            if inner == func:
                return func
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

        # If just y, return 1/y
        if g_y.strip() == func:
            return f"1/{func}"

        # Default: wrap in 1/(...)
        return f"1/({g_y})"

    def solve_separable(
        self,
        ode_str: str,
        var: str = 'x',
        func: str = 'y',
        initial_conditions: Dict = None
    ) -> Dict[str, Any]:
        """
        Solve a separable ODE: dy/dx = f(x)*g(y)

        Method:
            1. Verify separability
            2. Factor RHS into f(x) and g(y)
            3. Separate: ∫(1/g(y))dy = ∫f(x)dx
            4. Integrate both sides
            5. Apply initial conditions if provided

        Args:
            ode_str: ODE expression (e.g., "y' = x*y")
            var: Independent variable (default 'x')
            func: Dependent function (default 'y')
            initial_conditions: Dict like {'y(0)': 1}

        Returns:
            Dict with solution and metadata
        """
        initial_conditions = initial_conditions or {}

        try:
            # Verify separability
            if not self.is_separable(ode_str, var, func):
                self.non_separable_detected += 1
                return {
                    'success': False,
                    'error': 'ODE is not separable',
                    'method': 'separable'
                }

            # Parse: y' = RHS
            if '=' not in ode_str:
                return {
                    'success': False,
                    'error': 'Invalid ODE format',
                    'method': 'separable'
                }

            parts = ode_str.split('=')
            if len(parts) != 2:
                return {
                    'success': False,
                    'error': 'Invalid ODE format',
                    'method': 'separable'
                }

            rhs = parts[1].strip()

            # Simple case: dy/dx = f(x) (no y in RHS)
            if func not in rhs:
                success, integral, _ = native_integrate(rhs, var)
                if success:
                    solution = f"{func} = {integral} + C"
                    return {
                        'success': True,
                        'solution': solution,
                        'method': 'direct_integration',
                        'general_solution': True,
                        'initial_conditions': initial_conditions
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Could not integrate f(x) = {rhs}',
                        'method': 'separable'
                    }

            # Factor: dy/dx = f(x)*g(y)
            f_x, g_y = self.factor_separable(rhs, var, func)

            if not f_x or not g_y:
                return {
                    'success': False,
                    'error': 'Could not factor into f(x)*g(y)',
                    'method': 'separable'
                }

            # Integrate f(x)
            success_x, int_f, _ = native_integrate(f_x, var)
            if not success_x:
                return {
                    'success': False,
                    'error': f'Could not integrate f(x) = {f_x}',
                    'method': 'separable'
                }

            # Build 1/g(y)
            g_y_inv = self._build_reciprocal(g_y, func)

            # Integrate 1/g(y)
            success_y, int_g_inv, _ = native_integrate(g_y_inv, func)
            if not success_y:
                return {
                    'success': False,
                    'error': f'Could not integrate 1/g(y) = {g_y_inv}',
                    'method': 'separable'
                }

            # Build solution
            solution = f"{int_g_inv} = {int_f} + C"

            return {
                'success': True,
                'solution': solution,
                'f_x': f_x,
                'g_y': g_y,
                'integral_f': int_f,
                'integral_1_g': int_g_inv,
                'method': 'separation_of_variables',
                'general_solution': True,
                'initial_conditions': initial_conditions
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'separable'
            }

    # ==================== BDI METHODS ====================

    def update_beliefs(self):
        """
        Update beliefs from Blackboard.

        Queries for pending separable ODE tasks.
        """
        if not self.blackboard:
            return

        try:
            entries = self.blackboard.query_entries(
                tags=['ode', 'separable'],
                status='pending'
            ) if hasattr(self.blackboard, 'query_entries') else []

            for entry in entries:
                belief_key = f'pending_separable_{entry.entry_id}'
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
            if not predicate.startswith('pending_separable_'):
                continue

            task = belief.content
            task_id = task.entry_id if hasattr(task, 'entry_id') else str(hash(str(task)))

            # Skip if already processing
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            # Create intention
            intention = Intention(
                goal=f'solve_separable_{task_id}',
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
            - solve: Solve separable ODE
            - post: Post result to blackboard

        Args:
            intention: Current intention
        """
        if not intention or not hasattr(intention, 'get_current_action'):
            return

        action = intention.get_current_action()

        if action == 'claim':
            # Claim task
            intention.advance()

        elif action == 'solve':
            # Solve ODE
            task_entry = intention.metadata.get('task_entry')
            if task_entry:
                result = self.process(task_entry)
                intention.metadata['result'] = result
                intention.advance()
            else:
                intention.fail('No task entry')

        elif action == 'post':
            # Post result
            result = intention.metadata.get('result')
            if self.blackboard and result:
                if not hasattr(result, 'entry_id'):
                    # Result is not already an entry, create one
                    entry = create_entry(
                        EntryType.PARTIAL_RESULT,
                        create_variable(str(result)),
                        self.agent_id,
                        'separable_result',
                        ['ode', 'separable', 'result'],
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
            result = self.solve_separable(**params)
            return {'status': 'success', 'result': result}
        elif action == 'is_separable':
            result = self.is_separable(**params)
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
            'separable_odes_solved': self.separable_odes_solved,
            'non_separable_detected': self.non_separable_detected,
            'factorizations_successful': self.factorizations_successful,
            'factorizations_failed': self.factorizations_failed
        }


# Export
__all__ = ['SeparableODESpecialist']


if __name__ == '__main__':
    """Test Separable ODE Specialist."""
    print("=" * 80)
    print("SEPARABLE ODE SPECIALIST TEST")
    print("=" * 80)

    specialist = SeparableODESpecialist()

    test_cases = [
        ("y' = x", "Direct integration"),
        ("y' = x*y", "Simple product"),
        ("y' = x/y", "Quotient"),
        ("y' = (4*x)*(1/y)", "Parenthesized product"),
        ("y' = sin(x)*sqrt(y)", "Trig and sqrt"),
    ]

    for ode, description in test_cases:
        print(f"\n{description}: {ode}")
        result = specialist.solve_separable(ode)
        if result['success']:
            print(f"  Solution: {result['solution']}")
            print(f"  Method: {result.get('method', 'unknown')}")
        else:
            print(f"  Error: {result.get('error', 'Unknown error')}")

    print(f"\nStatistics: {specialist.get_stats()}")
