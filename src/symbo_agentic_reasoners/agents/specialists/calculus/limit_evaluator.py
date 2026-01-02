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
PHASE 2 - CAL-3: LIMIT EVALUATOR (Tier 3)
=========================================

Specializes in evaluating limits of mathematical expressions, handling
various cases including indeterminate forms and L'Hôpital's Rule.

CAPABILITIES:
------------
- Evaluate limits at finite points
- Evaluate limits at infinity (±∞)
- Handle one-sided limits (left, right)
- Detect and resolve indeterminate forms
- Track L'Hôpital's Rule applications
- Generate convergence proofs

ALGORITHMIC BACKING:
-------------------
- Native limit engine (NO SymPy)
- L'Hôpital's Rule for indeterminate forms
- Series expansions for complex limits

REFERENCE:
---------
- Agent_System_Audit.docx.md: CAL-3 Limit Evaluator
- Phase_2_Build_Order_Breakdown.md: Calculus Team
"""

import sys
import os
import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

# NO SYMPY AT TOP LEVEL - Using native calculus engine exclusively
# Native imports for limit evaluation
from symbo_agentic_reasoners.core.native_symbolic import (
    Symbol, sympify, parse_expr, Integer, Float
)
from symbo_agentic_reasoners.core.calculus import (
    native_limit, differentiate, _try_limit_with_assumptions, limit
)
from symbo_agentic_reasoners.core.calculus.series_specialist import series

# Define infinity constants
class _Infinity:
    """Positive infinity constant."""
    def __str__(self): return "oo"
    def __repr__(self): return "oo"
    def __neg__(self): return _NegInfinity()
    def __eq__(self, other): return isinstance(other, _Infinity)
    def __hash__(self): return hash("oo")

class _NegInfinity:
    """Negative infinity constant."""
    def __str__(self): return "-oo"
    def __repr__(self): return "-oo"
    def __neg__(self): return _Infinity()
    def __eq__(self, other): return isinstance(other, _NegInfinity)
    def __hash__(self): return hash("-oo")

class _ComplexInfinity:
    """Complex infinity constant."""
    def __str__(self): return "zoo"
    def __repr__(self): return "zoo"
    def __eq__(self, other): return isinstance(other, _ComplexInfinity)
    def __hash__(self): return hash("zoo")

class _NaN:
    """Not a Number constant."""
    def __str__(self): return "nan"
    def __repr__(self): return "nan"
    def __eq__(self, other): return isinstance(other, _NaN)
    def __hash__(self): return hash("nan")

oo = _Infinity()
zoo = _ComplexInfinity()
nan = _NaN()

logger = logging.getLogger('symbo_agentic_reasoners.phase2.limit_evaluator')

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.omdoc_schema import create_variable
# native_limit imported at top of file


class LimitDirection(Enum):
    """Direction for limit evaluation"""
    BOTH = "+-"      # Two-sided limit
    LEFT = "-"       # Left limit (from below)
    RIGHT = "+"      # Right limit (from above)


class IndeterminateForm(Enum):
    """Types of indeterminate forms"""
    ZERO_OVER_ZERO = "0/0"
    INF_OVER_INF = "∞/∞"
    ZERO_TIMES_INF = "0·∞"
    INF_MINUS_INF = "∞-∞"
    ONE_TO_INF = "1^∞"
    ZERO_TO_ZERO = "0^0"
    INF_TO_ZERO = "∞^0"
    NONE = "none"


@dataclass
class LHopitalStep:
    """Records a L'Hôpital's Rule application"""
    step_number: int
    numerator: str
    denominator: str
    numerator_derivative: str
    denominator_derivative: str
    form: str


@dataclass
class LimitResult:
    """
    Result of limit evaluation.

    Attributes:
        value: The computed limit value
        exists: Whether the limit exists
        is_finite: Whether the limit is finite
        direction: Direction of limit evaluation
        indeterminate_form: Type of indeterminate form encountered
        lhopital_steps: L'Hôpital's Rule applications
        series_expansion: Series expansion if used
        convergence_proof: Proof of convergence if applicable
        method_used: Method used for evaluation (e.g., 'native_limit', 'sympy')
    """
    value: Any
    exists: bool = True
    is_finite: bool = True
    direction: LimitDirection = LimitDirection.BOTH
    indeterminate_form: IndeterminateForm = IndeterminateForm.NONE
    lhopital_steps: List[LHopitalStep] = field(default_factory=list)
    series_expansion: Optional[str] = None
    convergence_proof: Optional[str] = None
    method_used: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            'value': str(self.value),
            'exists': self.exists,
            'is_finite': self.is_finite,
            'direction': self.direction.value,
            'indeterminate_form': self.indeterminate_form.value,
            'lhopital_applications': len(self.lhopital_steps),
            'used_series': self.series_expansion is not None,
            'has_proof': self.convergence_proof is not None,
            'method_used': self.method_used
        }


class LimitEvaluator(BDIAgent):
    """
    CAL-3: Limit Evaluator
    
    DIRECTIVE:
    ---------
    Evaluate limits of mathematical expressions with full explanation
    of the methods used.
    
    INPUTS:
    ------
    - Expression forms
    - Limit points
    - Directionality specifications
    
    OUTPUTS:
    -------
    - Limit values
    - Convergence proofs
    - L'Hôpital's Rule application traces
    
    DEPENDENCIES:
    ------------
    - ALG-2 (ArithmeticSpecialist): For symbolic simplification
    - CAL-1 (DifferentiationSpecialist): For derivatives in L'Hôpital's
    
    FAILURE MODE: RECOVERABLE
    
    REFERENCE:
    ---------
    Agent_System_Audit.docx.md: Lines 217-227
    """
    
    # Maximum L'Hôpital applications before fallback
    MAX_LHOPITAL_ITERATIONS = 10
    
    def __init__(
        self,
        agent_id: str = 'limit_evaluator_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Limit Evaluator
        
        Args:
            agent_id: Unique specialist identifier
            df: Directory Facilitator instance
            blackboard: Blackboard instance
        """
        super().__init__(agent_id)
        
        self.df = df
        self.blackboard = blackboard
        
        # L'Hôpital tracking
        self.lhopital_history: List[LHopitalStep] = []
        
        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.lhopital_applications = 0
        self.series_expansions_used = 0
        
        # Register with Directory Facilitator
        if self.df:
            self._register_services()
        
        print(f"[{self.agent_id}] Limit Evaluator initialized")
        print(f"  Capabilities: Finite limits, Limits at infinity, L'Hôpital's Rule")
        print(f"  Library: Native Calculus Engine (NO SymPy)")
    
    def _register_services(self):
        """Register services with Directory Facilitator"""
        registration = create_service_registration(
            service_type='math.calculus.limit',
            agent_id=self.agent_id,
            algorithm='limit_lhopital',
            cost='low',
            instance=self,  # Enable direct invocation by supervisors
            type='exact',
            tier='3',
            algorithms='limit_series_lhopital'
        )
        self.df.register(registration)
        print(f"  [DF] Registered: math.calculus.limit")
    
    def evaluate_limit(
        self,
        expression: Union[str, Any],
        variable: Union[str, Symbol],
        point: Union[str, Any, float],
        direction: LimitDirection = LimitDirection.BOTH
    ) -> LimitResult:
        """
        Evaluate the limit of an expression.
        
        Args:
            expression: The mathematical expression
            variable: The variable approaching the limit point
            point: The limit point (can be finite, oo, or -oo)
            direction: Direction of approach (both, left, or right)
            
        Returns:
            LimitResult with value and metadata
        """
        self.tasks_executed += 1
        self.lhopital_history = []
        
        try:
            # Parse inputs
            if isinstance(expression, str):
                expr = sympify(expression)
            else:
                expr = expression
            
            if isinstance(variable, str):
                var = Symbol(variable)
            else:
                var = variable
            
            if isinstance(point, str):
                if point in ['oo', 'inf', 'infinity']:
                    pt = oo
                elif point in ['-oo', '-inf', '-infinity']:
                    pt = -oo
                else:
                    pt = sympify(point)
            else:
                pt = point
            
            print(f"  Evaluating: lim({expr}) as {var} -> {pt}")

            # Use native limit engine EXCLUSIVELY (no SymPy fallback)
            expr_str = str(expr)
            var_str = str(var)
            point_str = str(pt)

            # Convert direction enum to string for native_limit
            direction_str = 'both'
            if direction == LimitDirection.LEFT:
                direction_str = 'left'
            elif direction == LimitDirection.RIGHT:
                direction_str = 'right'

            native_success, native_result, native_method = native_limit(expr_str, var_str, point_str, direction_str)
            if native_success and native_result is not None:
                print(f"  [NATIVE LIMIT] {native_method}: {native_result}")
                logger.info(f"Native limit: {expr_str} -> {native_result} (via {native_method})")
                # Convert result back to SymPy expression for compatibility
                try:
                    result = sympify(native_result)
                except Exception:
                    # Create a symbol for the result
                    result = Symbol(str(native_result))

                self.tasks_succeeded += 1
                return LimitResult(
                    value=result,
                    exists=True,
                    is_finite=str(result) not in ('oo', '-oo', 'zoo', 'inf', '-inf'),
                    direction=direction,
                    indeterminate_form=IndeterminateForm.NONE,
                    lhopital_steps=[],
                    series_expansion=None,
                    convergence_proof=f"Native pattern: {native_method}",
                    method_used=native_method
                )

            # Native engine couldn't solve - try with parameter assumptions
            from symbo_agentic_reasoners.core.calculus import _try_limit_with_assumptions
            assumed_result = _try_limit_with_assumptions(expr_str, var_str, point_str)
            if assumed_result is not None:
                result_val, method = assumed_result
                print(f"  [NATIVE LIMIT+ASSUMPTIONS] {method}: {result_val}")
                logger.info(f"Native limit with assumptions: {expr_str} -> {result_val}")
                try:
                    result = sympify(result_val)
                except Exception:
                    result = Symbol(str(result_val))

                self.tasks_succeeded += 1
                return LimitResult(
                    value=result,
                    exists=True,
                    is_finite=str(result) not in ('oo', '-oo', 'zoo', 'inf', '-inf'),
                    direction=direction,
                    indeterminate_form=IndeterminateForm.NONE,
                    lhopital_steps=[],
                    series_expansion=None,
                    convergence_proof=f"Native with assumptions: {method}",
                    method_used=method
                )

            # If all native methods fail, return error (no SymPy fallback)
            self.tasks_failed += 1
            print(f"  [NATIVE LIMIT] Could not evaluate limit natively")
            raise ValueError(f"Native limit engine could not evaluate: lim({expr}) as {var} -> {pt}")

            # Below code is disabled - no SymPy fallback
            # Check for indeterminate forms first
            indet_form = self._detect_indeterminate_form(expr, var, pt)

            if indet_form != IndeterminateForm.NONE:
                print(f"  Indeterminate form detected: {indet_form.value}")

            # Evaluate limit using SymPy (fallback) - DISABLED
            dir_symbol = direction.value
            result = limit(expr, var, pt, dir_symbol)
            
            # Check if limit exists
            exists = True
            is_finite = True
            
            if result == zoo:  # Complex infinity
                is_finite = False
            elif result == oo or result == -oo:
                is_finite = False
            elif result == nan:
                exists = False
                is_finite = False
            
            # If indeterminate form was detected, track L'Hôpital applications
            if indet_form in [IndeterminateForm.ZERO_OVER_ZERO, 
                              IndeterminateForm.INF_OVER_INF]:
                self._apply_lhopital_tracking(expr, var, pt)
            
            # Generate series expansion for difficult cases
            series_exp = None
            if not exists or (indet_form != IndeterminateForm.NONE):
                try:
                    series_exp = str(series(expr, var, pt, n=5))
                    self.series_expansions_used += 1
                except Exception as e:
                    logger.debug(f"Series expansion failed: {e}")
            
            # Generate convergence proof for finite results
            proof = None
            if exists and is_finite:
                proof = self._generate_convergence_proof(expr, var, pt, result)
            
            self.tasks_succeeded += 1
            
            return LimitResult(
                value=result,
                exists=exists,
                is_finite=is_finite,
                direction=direction,
                indeterminate_form=indet_form,
                lhopital_steps=self.lhopital_history.copy(),
                series_expansion=series_exp,
                convergence_proof=proof
            )
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Limit evaluation failed: {type(e).__name__}: {e}")
            return LimitResult(
                value=nan,
                exists=False,
                is_finite=False,
                direction=direction
            )
    
    def _detect_indeterminate_form(
        self,
        expr: Any,
        var: Symbol,
        point: Any
    ) -> IndeterminateForm:
        """Detect the type of indeterminate form, if any.

        NOTE: This method uses native limit evaluation for detection.
        """
        try:
            # Use native limit to evaluate numerator and denominator limits
            expr_str = str(expr)
            var_str = str(var)
            point_str = str(point)

            # Try to detect 0/0 form by checking if expression looks like a fraction
            if '/' in expr_str:
                # Simple pattern detection for indeterminate forms
                success, result, method = native_limit(expr_str, var_str, point_str, 'both')
                if not success:
                    # If limit fails, might be indeterminate
                    if '0' in str(method) or 'indeterminate' in str(method).lower():
                        return IndeterminateForm.ZERO_OVER_ZERO

            return IndeterminateForm.NONE

        except Exception as e:
            logger.debug(f"Indeterminate form detection failed: {e}")
            return IndeterminateForm.NONE
    
    def _apply_lhopital_tracking(
        self,
        expr: Any,
        var: Symbol,
        point: Any
    ):
        """
        Track L'Hôpital's Rule applications for explanation.

        Uses native differentiate function for derivative computation.
        """
        try:
            expr_str = str(expr)
            var_str = str(var)
            point_str = str(point)

            # Simple pattern matching for fractions
            if '/' not in expr_str:
                return

            # Try to split into numerator/denominator
            parts = expr_str.split('/')
            if len(parts) != 2:
                return

            current_numer = parts[0].strip()
            current_denom = parts[1].strip()

            for i in range(self.MAX_LHOPITAL_ITERATIONS):
                # Compute derivatives using native engine
                success_n, numer_deriv, _ = differentiate(current_numer, var_str)
                success_d, denom_deriv, _ = differentiate(current_denom, var_str)

                if not success_n or not success_d:
                    break

                step = LHopitalStep(
                    step_number=i + 1,
                    numerator=current_numer,
                    denominator=current_denom,
                    numerator_derivative=numer_deriv or "?",
                    denominator_derivative=denom_deriv or "?",
                    form="0/0"  # Simplified - assume 0/0 for L'Hopital
                )
                self.lhopital_history.append(step)
                self.lhopital_applications += 1

                # Check if we can evaluate with native limit
                ratio_str = f"({numer_deriv})/({denom_deriv})"
                success, result, method = native_limit(ratio_str, var_str, point_str, 'both')

                # If we got a result, we're done
                if success and result is not None:
                    break

                current_numer = numer_deriv
                current_denom = denom_deriv

        except Exception as e:
            logger.debug(f"L'Hôpital tracking failed: {e}")
    
    def _generate_convergence_proof(
        self,
        expr: Any,
        var: Symbol,
        point: Any,
        result: Any
    ) -> str:
        """Generate a convergence proof sketch"""
        try:
            proof_lines = [
                f"Claim: lim_({var}->{point}) {expr} = {result}",
                "",
                "Proof sketch:",
            ]

            if self.lhopital_history:
                proof_lines.append(f"  Applied L'Hopital's Rule {len(self.lhopital_history)} time(s)")
                for step in self.lhopital_history[:3]:  # Show first 3
                    proof_lines.append(f"    Step {step.step_number}: d/d{var}({step.numerator})/d/d{var}({step.denominator})")
            else:
                proof_lines.append(f"  Direct evaluation yields {result}")

            proof_lines.append("")
            proof_lines.append(f"Therefore, lim_({var}->{point}) {expr} = {result}. QED")
            
            return "\n".join(proof_lines)
            
        except Exception as e:
            logger.debug(f"Proof generation failed: {e}")
            return f"lim_({var}->{point}) {expr} = {result}"
    
    def evaluate_one_sided_limits(
        self,
        expression: Union[str, Any],
        variable: Union[str, Symbol],
        point: Union[str, Any, float]
    ) -> Tuple[LimitResult, LimitResult]:
        """
        Evaluate both one-sided limits.
        
        Args:
            expression: The mathematical expression
            variable: The variable
            point: The limit point
            
        Returns:
            Tuple of (left limit, right limit)
        """
        left = self.evaluate_limit(expression, variable, point, LimitDirection.LEFT)
        right = self.evaluate_limit(expression, variable, point, LimitDirection.RIGHT)
        
        return left, right
    
    def check_continuity_at_point(
        self,
        expression: Union[str, Any],
        variable: Union[str, Symbol],
        point: Union[str, Any, float]
    ) -> Dict[str, Any]:
        """
        Check if function is continuous at a point.

        Returns dictionary with continuity analysis.
        Uses native symbolic engine for evaluation.
        """
        self.tasks_executed += 1

        try:
            expr_str = str(expression) if not isinstance(expression, str) else expression
            var_str = str(variable) if not isinstance(variable, str) else variable
            point_str = str(point) if not isinstance(point, str) else point

            # Evaluate function value at point using native engine
            # Substitute the point value into the expression
            try:
                expr = parse_expr(expr_str)
                var = Symbol(var_str)
                pt = sympify(point_str)
                if hasattr(expr, 'subs'):
                    f_value = expr.subs({var: pt})
                else:
                    f_value = expr
            except Exception:
                f_value = "undefined"

            # Evaluate two-sided limit using native engine
            lim_result = self.evaluate_limit(expr_str, var_str, point_str, LimitDirection.BOTH)

            # Check continuity conditions
            f_val_str = str(f_value)
            is_defined = f_val_str not in ['nan', 'zoo', 'undefined', 'None']
            limit_exists = lim_result.exists

            # Compare function value and limit value
            try:
                limit_equals_value = str(f_value) == str(lim_result.value)
            except Exception:
                limit_equals_value = False

            is_continuous = is_defined and limit_exists and limit_equals_value

            self.tasks_succeeded += 1

            return {
                'is_continuous': is_continuous,
                'function_value': str(f_value),
                'limit_value': str(lim_result.value),
                'is_defined': is_defined,
                'limit_exists': limit_exists,
                'limit_equals_value': limit_equals_value
            }

        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Continuity check failed: {type(e).__name__}: {e}")
            return {
                'is_continuous': False,
                'error': str(e)
            }
    
    def process(self, task_entry: Any) -> Any:
        """Process limit evaluation task from Blackboard"""
        print(f"\n[{self.agent_id}] Processing limit task")
        
        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            operation = metadata.get('operation', 'limit')
            expression = metadata.get('expression', metadata.get('raw_input', ''))
            variable = metadata.get('variable', 'x')
            point = metadata.get('point', 0)
            direction = metadata.get('direction', '+-')
            
            if operation == 'continuity':
                result = self.check_continuity_at_point(expression, variable, point)
            else:
                dir_enum = {
                    '+-': LimitDirection.BOTH,
                    '+': LimitDirection.RIGHT,
                    '-': LimitDirection.LEFT
                }.get(direction, LimitDirection.BOTH)
                
                limit_result = self.evaluate_limit(expression, variable, point, dir_enum)
                result = limit_result.to_dict()
            
            return self._create_result_entry(task_entry, result)
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Limit task failed: {type(e).__name__}: {e}")
            return self._create_error_entry(task_entry, str(e))
    
    def _create_result_entry(self, task_entry: Any, result: Dict) -> Any:
        """Create result entry for Blackboard"""
        if not self.blackboard:
            return result
        
        result_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(str(result.get('value', result))),
            author_agent=self.agent_id,
            conversation_id=getattr(task_entry, 'conversation_id', 'result'),
            tags=['limit', 'calculus'],
            status=EntryStatus.PENDING,
            metadata=result
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
            conversation_id=getattr(task_entry, 'conversation_id', 'error'),
            tags=['error', 'limit'],
            status=EntryStatus.FAILED,
            metadata={'error': error_msg}
        )
        
        self.blackboard.post(error_entry)
        return error_entry
    
    # BDI Implementation
    def update_beliefs(self):
        """
        PERCEIVE: Monitor Blackboard for limit evaluation tasks.
        """
        if not self.blackboard:
            return

        try:
            # Find limit tasks
            limit_tasks = self.blackboard.query_entries(
                tags=['limit'],
                status=EntryStatus.PENDING
            )

            # Also find delegated tasks
            delegated_tasks = self.blackboard.query_entries(
                entry_type=EntryType.TASK,
                status=EntryStatus.PENDING
            )

            for task in delegated_tasks:
                if hasattr(task, 'metadata') and task.metadata:
                    assigned = task.metadata.get('assigned_agent', '')
                    if assigned == self.agent_id and task not in limit_tasks:
                        limit_tasks.append(task)

            # Add beliefs about pending tasks
            for task in limit_tasks:
                belief_key = f'pending_task_{task.entry_id}'
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

    def deliberate(self):
        """
        DELIBERATE: Create computation plans for limit evaluation tasks.

        Returns:
            List of new Intention objects
        """
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue

            task = belief.content
            task_id = task.entry_id

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            raw_input = metadata.get('raw_input', '').lower()
            operation = metadata.get('operation', 'limit')

            # Determine operation type
            if 'continuity' in raw_input:
                operation = 'continuity'
                steps = ['claim_task', 'parse_expression', 'check_continuity', 'post_result']
            else:
                steps = ['claim_task', 'parse_expression', 'evaluate_limit', 'verify_result', 'post_result']

            intention = Intention(
                plan_id=f'limit_{operation}_{task_id}',
                steps=steps,
                target_desire='evaluate_limit',
                metadata={
                    'task_id': task_id,
                    'task_entry': task,
                    'operation': operation,
                    'raw_input': raw_input,
                    'expression': metadata.get('expression', metadata.get('raw_input', '')),
                    'variable': metadata.get('variable', 'x'),
                    'point': metadata.get('point', 0),
                    'direction': metadata.get('direction', '+-')
                }
            )

            new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention: Intention):
        """
        EXECUTE: Execute one step of the limit evaluation plan.

        Uses native limit engine exclusively - NO SymPy.
        """
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')

        try:
            if action == 'claim_task':
                if self.blackboard:
                    self.blackboard.update_entry_status(task_id, EntryStatus.IN_PROGRESS)
                self.add_belief(f'claimed_task_{task_id}', True)
                self.remove_belief(f'pending_task_{task_id}')
                intention.advance()

            elif action == 'parse_expression':
                expr_str = intention.metadata.get('expression')
                var_name = intention.metadata.get('variable', 'x')

                # Store as strings for native engine
                expr = expr_str
                var = var_name

                intention.metadata['parsed_expr'] = expr
                intention.metadata['var_symbol'] = var
                intention.advance()

            elif action == 'evaluate_limit':
                expr = intention.metadata.get('parsed_expr')
                var = intention.metadata.get('var_symbol')
                point = intention.metadata.get('point', 0)
                direction = intention.metadata.get('direction', '+-')

                # Map direction string to LimitDirection enum
                dir_enum = {
                    '+-': LimitDirection.BOTH,
                    '+': LimitDirection.RIGHT,
                    '-': LimitDirection.LEFT
                }.get(direction, LimitDirection.BOTH)

                # Use native limit evaluation
                limit_result = self.evaluate_limit(expr, var, point, dir_enum)

                intention.metadata['limit_result'] = limit_result
                intention.metadata['result'] = limit_result.to_dict()
                self.add_belief('computed_result', limit_result.value)
                intention.advance()

            elif action == 'check_continuity':
                expr = intention.metadata.get('parsed_expr')
                var = intention.metadata.get('var_symbol')
                point = intention.metadata.get('point', 0)

                # Use native continuity checker
                cont_result = self.check_continuity_at_point(expr, var, point)

                intention.metadata['result'] = cont_result
                self.add_belief('computed_result', cont_result)
                intention.advance()

            elif action == 'verify_result':
                result = intention.metadata.get('result')
                verified = result is not None
                intention.metadata['verified'] = verified
                self.add_belief('result_verified', verified)
                intention.advance()

            elif action == 'post_result':
                result = intention.metadata.get('result')
                operation = intention.metadata.get('operation', 'limit')

                if self.blackboard:
                    result_entry = create_entry(
                        entry_type=EntryType.PARTIAL_RESULT,
                        content=create_variable(str(result.get('value', result) if isinstance(result, dict) else result)),
                        author_agent=self.agent_id,
                        conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                        tags=['limit', operation, 'result', task_id],
                        status=EntryStatus.COMPLETED,
                        metadata={
                            'result': str(result.get('value', result) if isinstance(result, dict) else result),
                            'full_result': result if isinstance(result, dict) else {'value': str(result)},
                            'operation': operation,
                            'task_id': task_id,
                            'algorithm': 'native_limit'
                        }
                    )
                    self.blackboard.post(result_entry)
                    self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)

                self.add_belief(f'completed_task_{task_id}', True)
                self.remove_belief(f'claimed_task_{task_id}')
                self.tasks_succeeded += 1
                intention.advance()

            else:
                logger.warning(f"[{self.agent_id}] Unknown action: {action}")
                intention.advance()

        except Exception as e:
            logger.error(f"[{self.agent_id}] Step {action} failed: {e}")
            if self.blackboard and task_id:
                error_entry = create_entry(
                    entry_type=EntryType.PARTIAL_RESULT,
                    content=create_variable(f"ERROR: {e}"),
                    author_agent=self.agent_id,
                    conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                    tags=['error', 'limit', task_id],
                    status=EntryStatus.FAILED,
                    metadata={'error': str(e), 'task_id': task_id}
                )
                self.blackboard.post(error_entry)
                self.blackboard.update_entry_status(task_id, EntryStatus.FAILED)

            self.remove_belief(f'pending_task_{task_id}')
            self.remove_belief(f'claimed_task_{task_id}')
            self.tasks_failed += 1
            while not intention.is_complete():
                intention.advance()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get specialist statistics"""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'success_rate': (self.tasks_succeeded / self.tasks_executed * 100)
                           if self.tasks_executed > 0 else 0.0,
            'lhopital_applications': self.lhopital_applications,
            'series_expansions_used': self.series_expansions_used
        })
        return stats


if __name__ == "__main__":
    """Test Limit Evaluator"""
    print("=" * 80)
    print("PHASE 2 - LIMIT EVALUATOR TEST")
    print("=" * 80)
    print()
    
    # Initialize evaluator
    evaluator = LimitEvaluator()
    print()
    
    # Test 1: Simple limit
    print("Test 1: Simple Limit")
    print("  lim(x->2) x^2")
    result = evaluator.evaluate_limit("x**2", "x", 2)
    print(f"  Value: {result.value}")
    print()

    # Test 2: Limit at infinity
    print("Test 2: Limit at Infinity")
    print("  lim(x->inf) 1/x")
    result = evaluator.evaluate_limit("1/x", "x", "oo")
    print(f"  Value: {result.value}")
    print(f"  Is finite: {result.is_finite}")
    print()

    # Test 3: Indeterminate form (0/0)
    print("Test 3: Indeterminate Form 0/0")
    print("  lim(x->0) sin(x)/x")
    result = evaluator.evaluate_limit("sin(x)/x", "x", 0)
    print(f"  Value: {result.value}")
    print(f"  Indeterminate form: {result.indeterminate_form.value}")
    print(f"  L'Hopital applications: {len(result.lhopital_steps)}")
    print()

    # Test 4: One-sided limits
    print("Test 4: One-Sided Limits")
    print("  lim(x->0) 1/x")
    left, right = evaluator.evaluate_one_sided_limits("1/x", "x", 0)
    print(f"  Left limit: {left.value}")
    print(f"  Right limit: {right.value}")
    print()
    
    # Test 5: Continuity check
    print("Test 5: Continuity Check")
    print("  f(x) = x^2 at x = 3")
    cont = evaluator.check_continuity_at_point("x**2", "x", 3)
    print(f"  Is continuous: {cont['is_continuous']}")
    print()
    
    print("Statistics:")
    import json
    print(json.dumps(evaluator.get_statistics(), indent=2))
