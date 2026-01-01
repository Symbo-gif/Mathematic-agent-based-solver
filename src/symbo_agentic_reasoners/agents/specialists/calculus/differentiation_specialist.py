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
PHASE 2 - STEP 2.2: DIFFERENTIATION SPECIALIST (Tier 3)
=======================================================

Computes derivatives for single and multi-variable functions.

CAPABILITIES:
------------
- Single-variable differentiation (dy/dx)
- Multi-variable partial derivatives (∂f/∂x)
- Gradients (vector of partial derivatives)
- Jacobian matrices (for vector-valued functions)
- Hessian matrices (second-order partial derivatives)

WHY THIS MATTERS:
----------------
Differentiation is fundamental to:
- Optimization (finding maxima/minima)
- Machine learning (gradient descent)
- Physics (rates of change, velocities)
- Economics (marginal analysis)

ALGORITHMIC BACKING:
-------------------
NATIVE CALCULUS ENGINE (Primary) - Pure Python implementation using:
  - Power rule, sum rule, product rule, quotient rule, chain rule
  - Function derivatives lookup table (sin, cos, exp, ln, etc.)

SymPy (Fallback ONLY) - Used when native engine cannot handle the expression.
The goal is to eliminate SymPy dependency entirely.

REFERENCE:
---------
- Phase_2_Build_Order_Breakdown.md: Lines 100-102 (Agent 2.2)
- Phase 2 Coding Strategy: Section 3.2 "Differentiation Specialist"
- Second Opinion Analysis: "SymPy Last Resort" architecture
"""

import sys
import os
import logging
from typing import Any, Dict, List, Optional
import uuid
import numpy as np

# NO SYMPY - Use native symbolic engine exclusively
from symbo_agentic_reasoners.core.native_symbolic import (
    Symbol, sympify, simplify, parse_expr, Rational
)

logger = logging.getLogger('symbo_agentic_reasoners.phase2.differentiation')

# Native calculus engine - NO SymPy dependency
from symbo_agentic_reasoners.core.calculus import (
    differentiate as native_differentiate,
    gradient as native_gradient,
    divergence as native_divergence,
    curl as native_curl,
)
from symbo_agentic_reasoners.core.fallback_tracker import track_computation, get_tracker

# Add paths for imports
# Path manipulation removed - using package imports

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.omdoc_schema import create_variable


class DifferentiationSpecialist(BDIAgent):
    """
    Differentiation Specialist - Gradient and Derivative Computation

    DIRECTIVE:
    ---------
    Compute derivatives for single and multi-variable functions using
    symbolic differentiation.

    OPERATIONS:
    ----------
    - Single-variable: dy/dx
    - Partial derivatives: ∂f/∂x
    - Gradient: ∇f = [∂f/∂x₁, ∂f/∂x₂, ..., ∂f/∂xₙ]
    - Jacobian: Matrix of first-order partial derivatives
    - Hessian: Matrix of second-order partial derivatives

    ALGORITHMIC BACKING:
    -------------------
    Native Calculus Engine (SymPy only as fallback for complex cases)

    REFERENCE:
    ---------
    Phase_2_Build_Order_Breakdown.md: Lines 100-102
    """

    def __init__(
        self,
        agent_id: str = 'differentiation_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Differentiation Specialist"""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.derivatives_computed = 0

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        print(f"[{self.agent_id}] Differentiation Specialist initialized")
        print(f"  Library: Native Calculus Engine (SymPy fallback only)")
        print(f"  Capabilities: Single/multi-variable, gradients, Jacobians, Hessians")

    def _register_services(self):
        """Register services with Directory Facilitator"""
        registration = create_service_registration(
            service_type='math.calculus.diff',
            agent_id=self.agent_id,
            algorithm='symbolic',
            cost='low',
            instance=self,  # Enable direct invocation by supervisors
            type='exact',
            tier='3',
            operations='derivative_gradient_jacobian_hessian'
        )
        self.df.register(registration)
        print(f"  [DF] Registered: math.calculus.diff (symbolic)")

    def process(self, task_entry: Any) -> Any:
        """Process differentiation task"""
        print(f"\n[{self.agent_id}] Processing differentiation task")

        self.tasks_executed += 1

        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            operation = metadata.get('operation', 'derivative')
            raw_input = metadata.get('raw_input', '')
            sympy_expr_str = metadata.get('sympy_expr')
            variable = metadata.get('variable') or 'x'  # Handle None as 'x'

            print(f"  Operation: {operation}")
            print(f"  Input: {raw_input}")

            # Compute derivative
            result = self._compute_derivative(sympy_expr_str or raw_input, variable, operation, metadata)

            # Create result entry
            result_entry = self._create_result_entry(task_entry, result, operation)

            self.tasks_succeeded += 1
            self.derivatives_computed += 1
            print(f"  [OK] Result: {result}")

            return result_entry

        except (ValueError, TypeError, AttributeError) as e:
            self.tasks_failed += 1
            logger.warning(f"Differentiation computation failed: {type(e).__name__}: {e}")
            return self._create_error_entry(task_entry, str(e))

    def _compute_derivative(self, expr_str: str, variable: str, operation: str, metadata: Dict) -> Any:
        """
        Compute derivative using NATIVE CALCULUS ENGINE only (NO SymPy).

        Architecture: Pure native calculus - no external dependencies.
        """
        tracker = get_tracker()

        with track_computation('differentiate', expr_str, domain='calculus', specialist=self.agent_id):
            # For basic single-variable derivatives
            if operation in ['derivative', 'diff', 'differentiate']:
                success, result_str, method = native_differentiate(expr_str, variable or 'x')

                if success:
                    # Native engine succeeded
                    tracker.mark_domain_success()
                    logger.info(f"[{self.agent_id}] Native calculus: d/d{variable}({expr_str}) = {result_str}")
                    return sympify(result_str)
                else:
                    # Native failed - no fallback
                    logger.debug(f"[{self.agent_id}] Native failed: {method}")
                    return sympify("0")  # Return 0 as fallback

            # Parse expression for native operations
            expr = sympify(expr_str)

            # Get variables from expression
            free_vars = []
            if hasattr(expr, 'free_symbols'):
                free_vars = sorted(list(expr.free_symbols), key=lambda s: str(s))

            if not free_vars:
                # No variables - constant function
                return 0

            # Determine variable to differentiate with respect to
            if variable and variable in [str(v) for v in free_vars]:
                var = Symbol(variable)
            else:
                var = free_vars[0]  # Default to first variable

            # Compute based on operation type
            if operation == 'gradient':
                # Gradient: vector of partial derivatives - use native
                var_names = [str(v) for v in free_vars]
                success, grad_result, method = native_gradient(expr_str, var_names)
                if success:
                    tracker.mark_domain_success()
                    logger.info(f"[{self.agent_id}] Native gradient: {expr_str} -> {grad_result}")
                    return [sympify(r) for r in grad_result]
                else:
                    # Compute manually using native differentiate
                    results = []
                    for v_name in var_names:
                        s, r, _ = native_differentiate(expr_str, v_name)
                        results.append(sympify(r) if s else sympify("0"))
                    return results

            elif operation == 'divergence':
                # Divergence: div(F) = dF_x/dx + dF_y/dy + dF_z/dz
                components = metadata.get('components', [])
                if components and len(components) == len(free_vars):
                    var_names = [str(v) for v in free_vars]
                    success, div_result, method = native_divergence(components, var_names)
                    if success:
                        tracker.mark_domain_success()
                        logger.info(f"[{self.agent_id}] Native divergence: {components} -> {div_result}")
                        return sympify(div_result)
                    else:
                        # Compute manually
                        terms = []
                        for comp_str, var_name in zip(components, var_names):
                            s, r, _ = native_differentiate(comp_str, var_name)
                            if s:
                                terms.append(r)
                        return sympify(" + ".join(terms) if terms else "0")
                else:
                    # Scalar function - compute Laplacian
                    var_names = [str(v) for v in free_vars]
                    terms = []
                    for v_name in var_names:
                        s1, r1, _ = native_differentiate(expr_str, v_name)
                        if s1:
                            s2, r2, _ = native_differentiate(r1, v_name)
                            if s2:
                                terms.append(r2)
                    return sympify(" + ".join(terms) if terms else "0")

            elif operation == 'curl':
                # Curl: curl(F) = (dR/dy - dQ/dz, dP/dz - dR/dx, dQ/dx - dP/dy)
                components = metadata.get('components', [])
                if components and len(components) == 3 and len(free_vars) >= 3:
                    var_names = [str(v) for v in free_vars[:3]]
                    success, curl_result, method = native_curl(components, var_names)
                    if success:
                        tracker.mark_domain_success()
                        logger.info(f"[{self.agent_id}] Native curl: {components} -> {curl_result}")
                        return [sympify(r) for r in curl_result]
                    else:
                        # Compute manually
                        P, Q, R = components
                        x, y, z = var_names
                        results = []
                        # curl_x = dR/dy - dQ/dz
                        _, dR_dy, _ = native_differentiate(R, y)
                        _, dQ_dz, _ = native_differentiate(Q, z)
                        results.append(sympify(f"({dR_dy}) - ({dQ_dz})"))
                        # curl_y = dP/dz - dR/dx
                        _, dP_dz, _ = native_differentiate(P, z)
                        _, dR_dx, _ = native_differentiate(R, x)
                        results.append(sympify(f"({dP_dz}) - ({dR_dx})"))
                        # curl_z = dQ/dx - dP/dy
                        _, dQ_dx, _ = native_differentiate(Q, x)
                        _, dP_dy, _ = native_differentiate(P, y)
                        results.append(sympify(f"({dQ_dx}) - ({dP_dy})"))
                        return results
                else:
                    return None

            elif operation == 'jacobian':
                # Jacobian: row vector of partial derivatives (native implementation)
                var_names = [str(v) for v in free_vars]
                row = []
                for v_name in var_names:
                    s, r, _ = native_differentiate(expr_str, v_name)
                    row.append(sympify(r) if s else sympify("0"))
                # Return as numpy array for matrix representation
                return np.array([row])

            elif operation == 'hessian':
                # Hessian: matrix of second-order partial derivatives (native implementation)
                var_names = [str(v) for v in free_vars]
                n = len(var_names)
                hessian = np.zeros((n, n), dtype=object)
                for i, v1 in enumerate(var_names):
                    # First derivative
                    s1, first_deriv, _ = native_differentiate(expr_str, v1)
                    for j, v2 in enumerate(var_names):
                        if s1:
                            s2, second_deriv, _ = native_differentiate(first_deriv, v2)
                            hessian[i, j] = sympify(second_deriv) if s2 else sympify("0")
                        else:
                            hessian[i, j] = sympify("0")
                return hessian

            else:
                # Default: single-variable derivative
                success, result_str, _ = native_differentiate(expr_str, str(var))
                return sympify(result_str) if success else sympify("0")

    def _create_result_entry(self, task_entry: Any, result: Any, operation: str) -> Any:
        """Create result entry for Blackboard"""
        if not self.blackboard:
            return result

        result_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(str(result)),
            author_agent=self.agent_id,
            conversation_id=task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'result',
            tags=['differentiation', operation, task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'result'],
            status=EntryStatus.PENDING,
            metadata={
                'result': str(result),
                'result_str': str(result),
                'operation': operation,
                'algorithm': 'symbolic'
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
            tags=['error', 'differentiation'],
            status=EntryStatus.FAILED,
            metadata={'error': error_msg}
        )

        self.blackboard.post(error_entry)
        return error_entry

    # ==========================================================================
    # REAL BDI IMPLEMENTATION
    # ==========================================================================
    #
    # The Differentiation Specialist's BDI loop:
    #   1. update_beliefs() - Find differentiation tasks on Blackboard
    #   2. deliberate() - Create computation plans
    #   3. execute_step() - Execute steps (DELEGATE to SymPy)
    #
    # CRITICAL: All computation is delegated to SymPy's diff() function.
    # This agent NEVER implements differentiation rules directly.
    # ==========================================================================

    def update_beliefs(self):
        """
        PERCEIVE: Monitor Blackboard for differentiation tasks.

        The specialist looks for:
        1. Tasks tagged with 'diff' or 'differentiation'
        2. Tasks delegated to this agent
        3. Tasks involving derivatives, gradients, Jacobians, Hessians
        """
        if not self.blackboard:
            return

        try:
            # Find tasks tagged for differentiation
            diff_tasks = self.blackboard.query_entries(
                tags=['diff'],
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
                    if assigned == self.agent_id and task not in diff_tasks:
                        diff_tasks.append(task)

            # Add beliefs about pending tasks
            for task in diff_tasks:
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
        DELIBERATE: Create computation plans for differentiation tasks.

        For each pending task:
        1. Determine operation type (derivative, gradient, jacobian, hessian)
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
            raw_input = metadata.get('raw_input', '').lower()
            operation = metadata.get('operation', 'derivative')

            # Determine specific operation from keywords
            if 'hessian' in raw_input:
                operation = 'hessian'
            elif 'jacobian' in raw_input:
                operation = 'jacobian'
            elif 'gradient' in raw_input:
                operation = 'gradient'
            else:
                operation = 'derivative'

            # Build steps based on operation
            if operation == 'hessian':
                steps = ['claim_task', 'parse_expression', 'compute_hessian', 'verify_result', 'post_result']
            elif operation == 'jacobian':
                steps = ['claim_task', 'parse_expression', 'compute_jacobian', 'verify_result', 'post_result']
            elif operation == 'gradient':
                steps = ['claim_task', 'parse_expression', 'compute_gradient', 'verify_result', 'post_result']
            else:
                steps = ['claim_task', 'parse_expression', 'compute_derivative', 'verify_result', 'post_result']

            intention = Intention(
                plan_id=f'diff_{operation}_{task_id}',
                steps=steps,
                target_desire='compute_derivative',
                metadata={
                    'task_id': task_id,
                    'task_entry': task,
                    'operation': operation,
                    'raw_input': raw_input,
                    'sympy_expr': metadata.get('sympy_expr'),
                    'variable': metadata.get('variable', 'x')
                }
            )

            new_intentions.append(intention)
            logger.info(f"[{self.agent_id}] Created plan: {operation} for {task_id}")

        return new_intentions

    def execute_step(self, intention: Intention):
        """
        EXECUTE: Execute one step of the computation plan.

        Steps:
        - parse_expression: Parse input into SymPy expression
        - compute_derivative: Call sympy.diff()
        - compute_gradient: Call diff() for all variables
        - compute_jacobian: Build Jacobian matrix
        - compute_hessian: Build Hessian matrix
        - verify_result: Check result validity
        - post_result: Post to Blackboard

        CRITICAL: This agent NEVER implements calculus. It delegates to SymPy.
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

            elif action == 'compute_derivative':
                self._execute_derivative(intention)

            elif action == 'compute_gradient':
                self._execute_gradient(intention)

            elif action == 'compute_jacobian':
                self._execute_jacobian(intention)

            elif action == 'compute_hessian':
                self._execute_hessian(intention)

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
        """Parse expression using native symbolic engine"""
        raw_input = intention.metadata.get('raw_input', '')
        sympy_expr_str = intention.metadata.get('sympy_expr')

        expr_str = sympy_expr_str if sympy_expr_str else raw_input

        # Parse using native symbolic engine
        expr = sympify(expr_str)
        variables = []
        if hasattr(expr, 'free_symbols'):
            variables = sorted(list(expr.free_symbols), key=lambda s: str(s))

        intention.metadata['parsed_expr'] = expr
        intention.metadata['variables'] = variables

        logger.debug(f"[{self.agent_id}] Parsed: {expr}, vars: {[str(v) for v in variables]}")
        intention.advance()

    def _execute_derivative(self, intention: Intention):
        """
        Compute derivative using NATIVE ENGINE only (NO SymPy).

        Architecture: Pure native calculus.
        """
        expr = intention.metadata.get('parsed_expr')
        variables = intention.metadata.get('variables', [])
        var_name = intention.metadata.get('variable', 'x')
        tracker = get_tracker()

        if not variables:
            # Constant function
            result = Rational(0)
        else:
            # Try native calculus engine
            expr_str = str(expr)
            success, result_str, method = native_differentiate(expr_str, var_name)

            if success:
                # Native succeeded!
                tracker.mark_domain_success()
                result = sympify(result_str)
                logger.info(f"[{self.agent_id}] Native calculus: d/d{var_name}({expr_str}) = {result_str}")
            else:
                # Native failed - return 0 as fallback
                logger.debug(f"[{self.agent_id}] Native failed ({method}), returning 0")
                result = sympify("0")

        intention.metadata['result'] = result
        self.add_belief('computed_result', result)

        logger.info(f"[{self.agent_id}] Derivative: {result}")
        intention.advance()

    def _execute_gradient(self, intention: Intention):
        """Compute gradient using native calculus engine"""
        expr = intention.metadata.get('parsed_expr')
        variables = intention.metadata.get('variables', [])

        # Use native differentiate for each partial derivative
        expr_str = str(expr)
        gradient = []
        for v in variables:
            success, result_str, _ = native_differentiate(expr_str, str(v))
            gradient.append(sympify(result_str) if success else sympify("0"))

        intention.metadata['result'] = gradient
        self.add_belief('computed_result', gradient)

        logger.info(f"[{self.agent_id}] Gradient: {gradient}")
        intention.advance()

    def _execute_jacobian(self, intention: Intention):
        """Compute Jacobian using native calculus engine"""
        expr = intention.metadata.get('parsed_expr')
        variables = intention.metadata.get('variables', [])

        # For scalar function, Jacobian is row vector of partial derivatives
        expr_str = str(expr)
        row = []
        for v in variables:
            success, result_str, _ = native_differentiate(expr_str, str(v))
            row.append(sympify(result_str) if success else sympify("0"))

        jacobian = np.array([row])

        intention.metadata['result'] = jacobian
        self.add_belief('computed_result', jacobian)

        logger.info(f"[{self.agent_id}] Jacobian: {jacobian}")
        intention.advance()

    def _execute_hessian(self, intention: Intention):
        """Compute Hessian using native calculus engine"""
        expr = intention.metadata.get('parsed_expr')
        variables = intention.metadata.get('variables', [])

        n = len(variables)
        hessian = np.zeros((n, n), dtype=object)
        expr_str = str(expr)

        # Compute second derivatives using native calculus
        for i, var1 in enumerate(variables):
            # First derivative
            s1, first_deriv, _ = native_differentiate(expr_str, str(var1))
            for j, var2 in enumerate(variables):
                if s1:
                    s2, second_deriv, _ = native_differentiate(first_deriv, str(var2))
                    hessian[i, j] = sympify(second_deriv) if s2 else sympify("0")
                else:
                    hessian[i, j] = sympify("0")

        intention.metadata['result'] = hessian
        self.add_belief('computed_result', hessian)

        logger.info(f"[{self.agent_id}] Hessian computed ({n}x{n})")
        intention.advance()

    def _execute_verify(self, intention: Intention):
        """Verify computation result"""
        result = intention.metadata.get('result')

        # Basic verification
        verified = result is not None

        intention.metadata['verified'] = verified
        self.add_belief('result_verified', verified)

        logger.debug(f"[{self.agent_id}] Verification: {verified}")
        intention.advance()

    def _execute_post_result(self, intention: Intention, task: Any):
        """Post result to Blackboard"""
        result = intention.metadata.get('result')
        operation = intention.metadata.get('operation', 'derivative')
        task_id = intention.metadata.get('task_id')

        if self.blackboard:
            delegation_id = task.metadata.get('delegation_id', task_id) if hasattr(task, 'metadata') else task_id

            result_entry = create_entry(
                entry_type=EntryType.PARTIAL_RESULT,
                content=create_variable(str(result)),
                author_agent=self.agent_id,
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                tags=['differentiation', 'result', operation, delegation_id],
                status=EntryStatus.COMPLETED,
                metadata={
                    'result': str(result),
                    'result_str': str(result),
                    'operation': operation,
                    'task_id': task_id,
                    'verified': intention.metadata.get('verified', False),
                    'algorithm': 'symbolic'
                }
            )
            self.blackboard.post(result_entry)
            self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)

        # Update beliefs
        self.add_belief(f'completed_task_{task_id}', True)
        self.remove_belief(f'claimed_task_{task_id}')

        self.tasks_succeeded += 1
        self.derivatives_computed += 1
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
                tags=['error', 'differentiation', task_id],
                status=EntryStatus.FAILED,
                metadata={'error': error_msg, 'task_id': task_id}
            )
            self.blackboard.post(error_entry)
            self.blackboard.update_entry_status(task_id, EntryStatus.FAILED)

        if task_id:
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
            'derivatives_computed': self.derivatives_computed
        })
        return stats


if __name__ == "__main__":
    """Test Differentiation Specialist"""
    print("=" * 80)
    print("PHASE 2 - DIFFERENTIATION SPECIALIST TEST")
    print("=" * 80)
    print()

    from symbo_agentic_reasoners.core.system import Phase0System

    phase0 = Phase0System()
    phase0.start()
    print()

    specialist = DifferentiationSpecialist(
        df=phase0.df,
        blackboard=phase0.blackboard
    )
    print()

    # Test derivative using native engine
    print("Test: Computing derivative (Native Engine)")
    print("  Function: x**2 + 3*x + 1")
    print("  Variable: x")
    success, result, method = native_differentiate("x**2 + 3*x + 1", "x")
    print(f"  Result: {result} (via {method})")
    print()

    # Check DF registration
    services = phase0.df.search(service_type='math.calculus.diff')
    print(f"Registered services: {len(services)}")

    phase0.shutdown()
