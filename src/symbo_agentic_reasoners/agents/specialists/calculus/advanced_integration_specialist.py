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
ADVANCED INTEGRATION SPECIALIST (Tier 3 Coordinator)
====================================================

Master coordinator for complex integration patterns requiring specialized techniques.

DIRECTIVE:
---------
Route complex integrals to specialized sub-agents based on pattern classification.
Implement fallback chain when primary specialist fails.

OPERATIONS:
----------
- Pattern classification (AST-based)
- Delegation to sub-specialists
- Fallback management
- Result aggregation and verification

DELEGATES TO:
------------
- ExponentialTrigIntegrationSpecialist (exp×trig products)
- TabularIntegrationSpecialist (repeated IBP) [Future]
- SubstitutionSpecialist (u-substitution) [Future]
- Basic IntegrationSpecialist (fallback)

ARCHITECTURE:
------------
100% native Python - NO SymPy dependency
Coordinator pattern with lazy specialist loading

REFERENCE:
---------
Build order 3, Tier 3 coordinator
ODE Accuracy Improvement Plan - Phase 2
"""

import re
import logging
from typing import Any, Dict, Optional, List, Tuple

logger = logging.getLogger('symbo_agentic_reasoners.specialists.advanced_integration')

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.omdoc_schema import create_variable


class AdvancedIntegrationSpecialist(BDIAgent):
    """
    Advanced Integration Specialist - Master Coordinator

    DIRECTIVE:
    ---------
    Coordinate advanced integration techniques by routing to specialized
    sub-agents based on integral pattern classification.

    PATTERN CLASSIFICATION:
    ----------------------
    - exp_trig_product: exp(ax) × [sin|cos](bx)
    - repeated_ibp: Polynomial (degree ≥3) × transcendental
    - chain_rule: Nested functions f(g(x)) × g'(x)
    - trig_power: sin^n(x), cos^n(x)
    - general: Falls back to basic integration

    DELEGATION STRATEGY:
    -------------------
    1. Classify pattern using AST analysis
    2. Query DF for appropriate specialist
    3. Delegate via Blackboard
    4. Implement fallback chain on failure
    5. Aggregate and verify results

    FALLBACK CHAIN:
    --------------
    Specialist 1 → Specialist 2 → Basic Integration → Numerical

    REFERENCE:
    ---------
    Phase 2, Days 4-6: Coordinator for integration team
    """

    def __init__(
        self,
        agent_id: str = 'advanced_integration_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Advanced Integration Specialist

        Args:
            agent_id: Unique specialist identifier
            df: Directory Facilitator instance
            blackboard: Blackboard instance
        """
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Lazy-loaded sub-specialists (retrieved from DF when needed)
        self._exp_trig_specialist = None
        self._tabular_specialist = None
        self._substitution_specialist = None
        self._basic_integration = None

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.patterns_classified = {}  # Track pattern distribution
        self.delegations_made = 0
        self.fallbacks_used = 0

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        print(f"[{self.agent_id}] Advanced Integration Specialist initialized")
        print(f"  Role: Master coordinator for complex integrals")
        print(f"  Delegates to: ExpTrig, Tabular, Substitution specialists")

    def _register_services(self):
        """
        Register services with Directory Facilitator

        Service: math.calculus.integration.advanced
        """
        registration = create_service_registration(
            service_type='math.calculus.integration.advanced',
            agent_id=self.agent_id,
            algorithm='pattern_coordination',
            cost='high',
            instance=self,  # Enable direct invocation
            type='coordinator',
            tier='3',
            capabilities=['exp_trig', 'tabular', 'substitution', 'fallback']
        )
        self.df.register(registration)
        print(f"  [DF] Registered: math.calculus.integration.advanced (coordinator)")

    def process(self, task_entry: Any) -> Any:
        """
        Process advanced integration task

        Args:
            task_entry: Blackboard entry containing integration task

        Returns:
            Result entry with integral solution
        """
        print(f"\n[{self.agent_id}] Processing advanced integration task")

        self.tasks_executed += 1

        try:
            # Extract task information
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            raw_input = metadata.get('raw_input', '')
            expression = metadata.get('expression', raw_input)
            var = metadata.get('variable', 'x')

            print(f"  Expression: {expression}")
            print(f"  Variable: {var}")

            # Classify pattern
            pattern = self._classify_integration_pattern(expression, var)
            print(f"  Pattern: {pattern}")

            # Track pattern distribution
            self.patterns_classified[pattern] = self.patterns_classified.get(pattern, 0) + 1

            # Select and invoke appropriate specialist
            result = self._route_to_specialist(pattern, expression, var, task_entry)

            if result and result.get('success'):
                self.tasks_succeeded += 1
                print(f"  [OK] Integration successful via {pattern} specialist")
                return self._create_result_entry(task_entry, result)
            else:
                self.tasks_failed += 1
                error_msg = result.get('error', 'Integration failed') if result else 'No specialist available'
                print(f"  [ERROR] {error_msg}")
                return self._create_error_entry(task_entry, error_msg)

        except Exception as e:
            self.tasks_failed += 1
            print(f"  [ERROR] Coordination failed: {e}")
            return self._create_error_entry(task_entry, str(e))

    def _classify_integration_pattern(self, expression: str, var: str) -> str:
        """
        Classify integration pattern using AST-based analysis

        Args:
            expression: Expression to integrate
            var: Integration variable

        Returns:
            Pattern type: 'exp_trig_product', 'repeated_ibp', 'chain_rule',
                         'trig_power', 'general'
        """
        expr_lower = expression.lower()

        # Remove outer parentheses for better pattern matching
        expr_clean = expression.strip()
        while expr_clean.startswith('(') and expr_clean.endswith(')'):
            # Check if it's a balanced single pair
            depth = 0
            is_single_pair = True
            for i, char in enumerate(expr_clean):
                if char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
                if depth == 0 and i < len(expr_clean) - 1:
                    is_single_pair = False
                    break
            if is_single_pair:
                expr_clean = expr_clean[1:-1].strip()
            else:
                break

        # Pattern 1: exp(ax) × [sin|cos](bx)
        # Match with optional parentheses: (exp(...))*(sin(...)) or exp(...)*sin(...)
        exp_trig_pattern = r'\(?\s*exp\s*\([^)]+\)\s*\)?\s*\*\s*\(?\s*(sin|cos)\s*\([^)]+\)\s*\)?'
        if re.search(exp_trig_pattern, expr_clean, re.IGNORECASE):
            return 'exp_trig_product'

        # Alternative exp×trig check (more permissive)
        if 'exp' in expr_lower and ('sin' in expr_lower or 'cos' in expr_lower):
            if '*' in expression or '·' in expression:
                return 'exp_trig_product'

        # Pattern 2: High-degree polynomial × transcendental (for tabular)
        # Look for x^n where n >= 3
        high_poly_pattern = r'x\s*\*\*\s*[3-9]|x\^[3-9]'
        if re.search(high_poly_pattern, expression):
            # Check if multiplied by transcendental
            if any(func in expr_lower for func in ['exp', 'sin', 'cos', 'ln', 'log']):
                return 'repeated_ibp'

        # Pattern 3: Chain rule indicators (nested functions)
        # Look for patterns like sin(x^2)*x, cos(ln(x))/x, etc.
        # Simplified detection: function of composite × potential derivative
        if '(' in expression and ')' in expression:
            # Count nested parentheses
            nesting_depth = expression.count('(') - expression.count(')')
            if abs(nesting_depth) <= 1:  # Valid nesting
                # Check for composition indicators
                if any(f in expr_lower for f in ['sin(', 'cos(', 'exp(', 'ln(', 'log(']):
                    # Look for multiplication suggesting chain rule
                    if '*' in expression:
                        return 'chain_rule'

        # Pattern 4: Trigonometric powers (sin^n, cos^n)
        trig_power_pattern = r'(sin|cos)\([^)]+\)\s*\*\*\s*\d+|(sin|cos)\^?\d+'
        if re.search(trig_power_pattern, expr_lower):
            return 'trig_power'

        # Default: General integral
        return 'general'

    def _route_to_specialist(
        self,
        pattern: str,
        expression: str,
        var: str,
        task_entry: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Route to appropriate specialist based on pattern

        Args:
            pattern: Classified pattern type
            expression: Expression to integrate
            var: Integration variable
            task_entry: Original task entry

        Returns:
            Integration result or None
        """
        # Route based on pattern
        if pattern == 'exp_trig_product':
            return self._delegate_to_exp_trig(expression, var, task_entry)

        elif pattern == 'repeated_ibp':
            return self._delegate_to_tabular(expression, var, task_entry)

        elif pattern == 'chain_rule':
            return self._delegate_to_substitution(expression, var, task_entry)

        elif pattern == 'trig_power':
            # Can be handled by basic integration (already has trig power reduction)
            return self._fallback_to_basic(expression, var, task_entry)

        else:  # general
            return self._fallback_to_basic(expression, var, task_entry)

    def _delegate_to_exp_trig(
        self,
        expression: str,
        var: str,
        task_entry: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Delegate to ExponentialTrigIntegrationSpecialist

        Args:
            expression: Expression to integrate
            var: Integration variable
            task_entry: Original task

        Returns:
            Integration result
        """
        # Lazy load specialist from DF
        if not self._exp_trig_specialist:
            specialists = self.df.search(service_type='math.calculus.integration.exp_trig') if self.df else []
            if specialists:
                self._exp_trig_specialist = specialists[0].instance
            else:
                print(f"  [WARN] ExpTrig specialist not found in DF")
                return None

        # Delegate
        self.delegations_made += 1
        print(f"  -> Delegating to ExponentialTrigIntegrationSpecialist")

        # Create delegated task
        if self._exp_trig_specialist:
            try:
                # Call specialist's integration method directly
                result = self._exp_trig_specialist._integrate_exp_trig(expression, var)
                # Check if specialist failed, trigger fallback
                if not result or not result.get('success'):
                    print(f"  [WARN] ExpTrig failed, using fallback")
                    return self._fallback_to_basic(expression, var, task_entry)
                return result
            except Exception as e:
                print(f"  [ERROR] ExpTrig delegation failed: {e}")
                return self._fallback_to_basic(expression, var, task_entry)

        return None

    def _delegate_to_tabular(
        self,
        expression: str,
        var: str,
        task_entry: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Delegate to TabularIntegrationSpecialist

        Args:
            expression: Expression to integrate
            var: Integration variable
            task_entry: Original task

        Returns:
            Integration result
        """
        # Lazy load specialist from DF
        if not self._tabular_specialist:
            specialists = self.df.search(service_type='math.calculus.integration.tabular') if self.df else []
            if specialists:
                self._tabular_specialist = specialists[0].instance
            else:
                print(f"  [WARN] Tabular specialist not found in DF, using fallback")
                return self._fallback_to_basic(expression, var, task_entry)

        # Delegate
        self.delegations_made += 1
        print(f"  -> Delegating to TabularIntegrationSpecialist")

        # Call specialist's tabular method directly
        if self._tabular_specialist:
            try:
                result = self._tabular_specialist._integrate_tabular(expression, var)
                # Check if specialist failed, trigger fallback
                if not result or not result.get('success'):
                    print(f"  [WARN] Tabular failed, using fallback")
                    return self._fallback_to_basic(expression, var, task_entry)
                return result
            except Exception as e:
                print(f"  [ERROR] Tabular delegation failed: {e}")
                # Fallback to basic
                return self._fallback_to_basic(expression, var, task_entry)

        return None

    def _delegate_to_substitution(
        self,
        expression: str,
        var: str,
        task_entry: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Delegate to SubstitutionSpecialist

        Args:
            expression: Expression to integrate
            var: Integration variable
            task_entry: Original task

        Returns:
            Integration result
        """
        # Lazy load specialist from DF
        if not self._substitution_specialist:
            specialists = self.df.search(service_type='math.calculus.integration.substitution') if self.df else []
            if specialists:
                self._substitution_specialist = specialists[0].instance
            else:
                print(f"  [WARN] Substitution specialist not found in DF, using fallback")
                return self._fallback_to_basic(expression, var, task_entry)

        # Delegate
        self.delegations_made += 1
        print(f"  -> Delegating to SubstitutionSpecialist")

        # Call specialist's substitution method directly
        if self._substitution_specialist:
            try:
                result = self._substitution_specialist._integrate_by_substitution(expression, var)
                # Check if specialist failed, trigger fallback
                if not result or not result.get('success'):
                    print(f"  [WARN] Substitution failed, using fallback")
                    return self._fallback_to_basic(expression, var, task_entry)
                return result
            except Exception as e:
                print(f"  [ERROR] Substitution delegation failed: {e}")
                # Fallback to basic
                return self._fallback_to_basic(expression, var, task_entry)

        return None

    def _fallback_to_basic(
        self,
        expression: str,
        var: str,
        task_entry: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Fallback to basic IntegrationSpecialist

        Args:
            expression: Expression to integrate
            var: Integration variable
            task_entry: Original task

        Returns:
            Integration result or None
        """
        self.fallbacks_used += 1
        print(f"  -> Fallback to native integration engine")

        # Import native integration engine
        try:
            from symbo_agentic_reasoners.core.calculus import integrate as native_integrate
            from symbo_agentic_reasoners.core.simplification import simplify_for_integration
            from symbo_agentic_reasoners.core.special_functions import format_integral_with_special_functions
            import re

            # First, try to simplify the expression
            simplified = simplify_for_integration(expression, var)
            if simplified != expression:
                print(f"  [SIMPLIFY] {expression} -> {simplified}")
                expression = simplified

            # Check if this requires special functions
            special_result = format_integral_with_special_functions(expression, var)
            if special_result:
                print(f"  [SPECIAL] Using special function")
                return {
                    'success': True,
                    'solution': special_result,
                    'method': 'special_function',
                    'pattern': 'special'
                }

            # Handle Gaussian integrals: exp(±ax²±bx±c)
            gaussian_result = self._integrate_gaussian(expression, var)
            if gaussian_result and gaussian_result.get('success'):
                print(f"  [GAUSSIAN] Solved using error function")
                return gaussian_result

            # Attempt integration with native engine
            success, result, _ = native_integrate(expression, var)

            if success:
                print(f"  [OK] Native integration succeeded")
                return {
                    'success': True,
                    'solution': result,
                    'method': 'native_integration',
                    'pattern': 'basic'
                }
            else:
                print(f"  [WARN] Native integration failed")
                # Last resort: Numeric integration indicator
                # For ODE benchmarks, we indicate this needs numerical solution
                print(f"  [NUMERIC] Would require numerical integration")
                return {
                    'success': False,
                    'error': f'Requires numerical integration: {expression}',
                    'pattern': 'numeric_required',
                    'expression': expression,
                    'note': 'Symbolic integration not possible, numerical methods required'
                }

        except Exception as e:
            print(f"  [ERROR] Fallback integration error: {e}")
            return {
                'success': False,
                'error': f'Integration error: {str(e)}',
                'pattern': 'error',
                'expression': expression
            }

    def _integrate_gaussian(self, expression: str, var: str) -> Optional[Dict[str, Any]]:
        """
        Integrate Gaussian (exp with quadratic exponent) using error function.

        Handles: exp(ax²+bx+c), exp(-ax²), exp(ax²±bx)

        Uses: ∫exp(-x²)dx = √π/2 * erf(x)

        Args:
            expression: Expression to integrate
            var: Integration variable

        Returns:
            Integration result or None
        """
        import re
        import math

        # Pattern: exp(...) where ... contains x²
        pattern = r'exp\s*\(\s*([^)]+)\s*\)'
        match = re.search(pattern, expression)

        if not match:
            return None

        exponent = match.group(1).strip()

        # Check if exponent has x² term
        if f'{var}**2' not in exponent and f'{var}^2' not in exponent:
            return None

        # Simplest case: exp(-x²) or exp(-ax²)
        # Pattern: -a*x**2 or -x**2
        simple_pattern = rf'^\s*-?\s*(\d*\.?\d*)\s*\*?\s*{var}\s*\*\*\s*2\s*$'
        simple_match = re.match(simple_pattern, exponent)

        if simple_match:
            coeff_str = simple_match.group(1)
            if coeff_str and coeff_str != '':
                a = float(coeff_str) if coeff_str else 1.0
            else:
                a = 1.0

            # Check sign
            if exponent.strip().startswith('-'):
                # ∫exp(-ax²)dx = √(π/a)/2 * erf(√a * x)
                sqrt_a = math.sqrt(a)
                result = f"sqrt(pi/{a})/2 * erf(sqrt({a})*{var})"
                return {
                    'success': True,
                    'solution': result,
                    'method': 'gaussian_erf',
                    'pattern': 'exp(-ax^2)'
                }

        # For more complex cases, return None (requires completing the square)
        return None

    def _create_result_entry(self, task_entry: Any, result: Dict[str, Any]) -> Any:
        """Create result entry for Blackboard"""
        if not self.blackboard:
            return result

        result_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(str(result.get('solution', result))),
            author_agent=self.agent_id,
            conversation_id=task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'result',
            tags=['integration', 'advanced', task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'result'],
            status=EntryStatus.PENDING,
            metadata={
                'result': str(result.get('solution', result)),
                'method': result.get('method', 'advanced_coordination'),
                'pattern': result.get('pattern', 'unknown'),
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
            tags=['error', 'integration', 'advanced'],
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
        PERCEIVE: Monitor Blackboard for advanced integration tasks

        Queries for:
        - Integration tasks tagged 'advanced'
        - Integration tasks with complex patterns
        """
        if not self.blackboard:
            return

        try:
            # Query for advanced integration tasks
            pending_tasks = self.blackboard.query_entries(
                tags=['integration', 'advanced'],
                status=EntryStatus.PENDING
            )

            # Also check general integration tasks that might be complex
            general_integration = self.blackboard.query_entries(
                tags=['integration'],
                status=EntryStatus.PENDING
            )

            # Filter for complex patterns
            for task in general_integration:
                if hasattr(task, 'metadata'):
                    complexity = task.metadata.get('complexity', 'basic')
                    if complexity in ['advanced', 'complex', 'hard']:
                        pending_tasks.append(task)

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
        DELIBERATE: Create coordination plans for advanced integration tasks

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

            # Create coordination plan
            steps = [
                'claim_task',
                'classify_pattern',
                'select_specialist',
                'delegate_to_specialist',
                'verify_result',
                'post_result'
            ]

            intention = Intention(
                plan_id=f'coordinate_integration_{task.entry_id}',
                steps=steps,
                target_desire='coordinate_advanced_integration',
                metadata={
                    'task_id': task.entry_id,
                    'task_entry': task
                }
            )

            new_intentions.append(intention)
            print(f"[{self.agent_id}] Created coordination plan for task {task.entry_id}")

        return new_intentions

    def execute_step(self, intention: Intention):
        """
        EXECUTE: Perform one step of the coordination plan

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

            elif action == 'classify_pattern':
                self._execute_classify_pattern(intention, task)

            elif action == 'select_specialist':
                self._execute_select_specialist(intention, task)

            elif action == 'delegate_to_specialist':
                self._execute_delegate(intention, task)

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

    def _execute_classify_pattern(self, intention: Intention, task):
        """Classify integration pattern"""
        metadata = task.metadata if hasattr(task, 'metadata') else {}
        expression = metadata.get('expression', metadata.get('raw_input', ''))
        var = metadata.get('variable', 'x')

        pattern = self._classify_integration_pattern(expression, var)

        intention.metadata['pattern'] = pattern
        intention.metadata['expression'] = expression
        intention.metadata['var'] = var

        intention.advance()

    def _execute_select_specialist(self, intention: Intention, task):
        """Select appropriate specialist based on pattern"""
        pattern = intention.metadata.get('pattern', 'general')

        # Map pattern to specialist service type
        specialist_map = {
            'exp_trig_product': 'math.calculus.integration.exp_trig',
            'repeated_ibp': 'math.calculus.integration.tabular',  # Future
            'chain_rule': 'math.calculus.integration.substitution',  # Future
            'trig_power': 'math.calculus.integration',  # Basic
            'general': 'math.calculus.integration'  # Basic
        }

        service_type = specialist_map.get(pattern, 'math.calculus.integration')
        intention.metadata['service_type'] = service_type

        intention.advance()

    def _execute_delegate(self, intention: Intention, task):
        """Delegate to selected specialist"""
        pattern = intention.metadata.get('pattern')
        expression = intention.metadata.get('expression')
        var = intention.metadata.get('var', 'x')

        result = self._route_to_specialist(pattern, expression, var, task)

        if result:
            intention.metadata['result'] = result
            intention.metadata['delegation_successful'] = result.get('success', False)
        else:
            intention.metadata['delegation_successful'] = False

        intention.advance()

    def _execute_verify(self, intention: Intention, task):
        """Verify result"""
        result = intention.metadata.get('result')
        if result and result.get('success'):
            intention.metadata['verified'] = True
        else:
            intention.metadata['verified'] = False

        intention.advance()

    def _execute_post_result(self, intention: Intention, task):
        """Post result to Blackboard"""
        result = intention.metadata.get('result')
        task_id = intention.metadata['task_id']

        if self.blackboard and result:
            self._create_result_entry(task, result)
            if result.get('success'):
                self.tasks_succeeded += 1

        intention.advance()

    def _handle_failure(self, intention: Intention, task, error_msg: str):
        """Handle coordination failure"""
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
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'delegations_made': self.delegations_made,
            'fallbacks_used': self.fallbacks_used,
            'patterns_classified': dict(self.patterns_classified),
            'success_rate': (self.tasks_succeeded / self.tasks_executed * 100)
                           if self.tasks_executed > 0 else 0.0
        })
        return stats
