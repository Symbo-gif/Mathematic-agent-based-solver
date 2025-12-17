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
SymPy's symbolic differentiation engine using the chain rule,
product rule, quotient rule, and other calculus rules.

REFERENCE:
---------
- Phase_2_Build_Order_Breakdown.md: Lines 100-102 (Agent 2.2)
- Phase 2 Coding Strategy: Section 3.2 "Differentiation Specialist"
"""

import sys
import os
import logging
from typing import Any, Dict, List, Optional
import uuid

import sympy as sp
from sympy import Symbol, symbols, diff, Matrix

logger = logging.getLogger('symbo_agentic_reasoners.phase2.differentiation')

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from symbo_agentic_reasoners_phase0.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners_phase0.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners_phase0.memory.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners_phase0.core.omdoc_schema import create_variable


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
    SymPy symbolic differentiation (exact, not numerical approximation)

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
        print(f"  Library: SymPy symbolic differentiation")
        print(f"  Capabilities: Single/multi-variable, gradients, Jacobians, Hessians")

    def _register_services(self):
        """Register services with Directory Facilitator"""
        registration = create_service_registration(
            service_type='math.calculus.diff',
            agent_id=self.agent_id,
            algorithm='symbolic',
            cost='low',
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
            variable = metadata.get('variable', 'x')

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

        except (sp.SympifyError, ValueError, TypeError, AttributeError) as e:
            self.tasks_failed += 1
            logger.warning(f"Differentiation computation failed: {type(e).__name__}: {e}")
            return self._create_error_entry(task_entry, str(e))

    def _compute_derivative(self, expr_str: str, variable: str, operation: str, metadata: Dict) -> Any:
        """Compute derivative using SymPy"""
        # Parse expression
        expr = sp.sympify(expr_str)

        # Get variables
        free_vars = sorted(expr.free_symbols, key=lambda s: s.name)

        if not free_vars:
            # No variables - constant function
            return 0

        # Determine variable to differentiate with respect to
        if variable and variable in [str(v) for v in free_vars]:
            var = Symbol(variable)
        else:
            var = free_vars[0]  # Default to first variable

        # Compute based on operation type
        if operation in ['derivative', 'diff', 'differentiate']:
            # Single-variable derivative
            result = diff(expr, var)

        elif operation == 'gradient':
            # Gradient: vector of partial derivatives
            result = [diff(expr, v) for v in free_vars]

        elif operation == 'jacobian':
            # Jacobian: requires vector-valued function
            # For Phase 2, compute gradient (Jacobian of scalar function)
            result = Matrix([diff(expr, v) for v in free_vars])

        elif operation == 'hessian':
            # Hessian: matrix of second-order partial derivatives
            n = len(free_vars)
            hessian = sp.zeros(n, n)
            for i, var1 in enumerate(free_vars):
                for j, var2 in enumerate(free_vars):
                    hessian[i, j] = diff(diff(expr, var1), var2)
            result = hessian

        else:
            # Default: single-variable derivative
            result = diff(expr, var)

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

    # BDI Implementation
    def update_beliefs(self):
        """Monitor Blackboard for differentiation tasks"""
        pass

    def deliberate(self):
        """Generate computation plans"""
        return []

    def execute_step(self, intention: Intention):
        """Execute computation step"""
        pass

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

    from symbo_agentic_reasoners_phase0.phase0_system import Phase0System

    phase0 = Phase0System()
    phase0.start()
    print()

    specialist = DifferentiationSpecialist(
        df=phase0.df,
        blackboard=phase0.blackboard
    )
    print()

    # Test derivative
    print("Test: Computing derivative")
    print("  Function: x**2 + 3*x + 1")
    print("  Variable: x")
    result = diff(sp.sympify("x**2 + 3*x + 1"), sp.Symbol('x'))
    print(f"  Result: {result}")
    print()

    # Check DF registration
    services = phase0.df.search(service_type='math.calculus.diff')
    print(f"Registered services: {len(services)}")

    phase0.shutdown()
