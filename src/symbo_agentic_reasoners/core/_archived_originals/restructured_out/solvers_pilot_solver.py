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
PHASE 1 - STEP 3: THE PILOT SOLVER (Symbolic Wrapper)
=====================================================

.. deprecated::
    This module is DEPRECATED and will be removed in a future release.
    Use MathSolver (core/math_solver.py) for the full BDI pipeline or
    SolverEngine (core/solver_engine.py) for direct native computation.

    The specialized agent workforce is now fully implemented with 53+
    specialists across all mathematical domains.

The Pilot Solver is a temporary "stand-in" for the future specialized
agent workforce. It serves as a "tracer bullet" to verify that the
end-to-end data pipeline is fully functional.

STRATEGIC PURPOSE:
-----------------
This agent proves that a mathematical payload can travel the full circuit:
  User → Orchestrator → Blackboard → Solver → Verification → Back

This verifies the plumbing of the entire system before adding complexity.

ARCHITECTURE:
------------
- Wraps SymPy Computer Algebra System in agent shell
- Registers with Directory Facilitator
- Subscribes to Blackboard for tasks
- Executes deterministic symbolic operations
- Posts candidate results for verification

REFERENCE:
---------
- Phase_1_Build_Order_Breakdown.md: Lines 162-221 (STEP 3)
- Phase 1 Coding Strategy: Section 3.3 "The Pilot Solver"

MIGRATION:
---------
Replace usages of PilotSolverAgent with:
  from symbo_agentic_reasoners.core.math_solver import MathSolver
  solver = MathSolver()
  result = solver.solve("x^2 - 4 = 0")
"""

import sys
import os
import warnings
from typing import Optional, Dict, Any, List
import uuid

# NO SYMPY - Use native symbolic engine
from symbo_agentic_reasoners.core.native_symbolic import (
    Symbol, sympify, simplify, parse_expr, diff, expand, factor
)
from symbo_agentic_reasoners.core.calculus import (
    differentiate, integrate as native_integrate
)

# Add parent to path for Phase 0 imports
# Path manipulation removed - using package imports

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, BlackboardEntry, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.omdoc_schema import (
    OMObject, create_variable, create_number, create_operation,
    MathOperator
)


class PilotSolverAgent(BDIAgent):
    """
    Pilot Solver Agent - SymPy CAS Wrapper

    DIRECTIVE:
    ---------
    Encapsulate SymPy Computer Algebra System within a standard agent shell.
    Acts as the "Prover" or "Executor" in the reasoning loop.

    FUNCTION:
    --------
    1. Subscribe to OMDoc-formatted tasks on Blackboard
    2. Execute deterministic symbolic operations (sympy.diff, sympy.integrate)
    3. Post candidate result back to Blackboard for verification

    REGISTRATION:
    ------------
    Registers with Directory Facilitator using service_type='math.calculus'
    so Orchestrator can discover it dynamically.

    CRITICAL:
    --------
    This agent is the "tracer bullet" - it proves the full pipeline works.
    Phase 2 will replace this single agent with 50+ specialized agents.

    REFERENCE:
    ---------
    - Phase_1_Build_Order_Breakdown.md: Lines 175-221 (PilotSolverAgent code)
    - Phase 1 Coding Strategy: "This agent wraps SymPy CAS in agent shell"
    """

    def __init__(
        self,
        agent_id: str = 'pilot_solver_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Pilot Solver Agent

        Args:
            agent_id: Unique agent identifier
            df: Directory Facilitator for service registration
            blackboard: Blackboard for task subscription
        """
        # Emit deprecation warning
        warnings.warn(
            "PilotSolverAgent is deprecated and will be removed in a future release. "
            "Use MathSolver (core/math_solver.py) for full BDI pipeline or "
            "SolverEngine (core/solver_engine.py) for direct native computation.",
            DeprecationWarning,
            stacklevel=2
        )

        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Native symbolic setup (no SymPy)
        # Transformations handled by native_symbolic.parse_expr

        # Task tracking
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0

        # Callback subscription ID
        self.subscription_id = None

        print(f"[{self.agent_id}] Initialized (SymPy CAS Wrapper)")

        # Register and subscribe
        if self.df and self.blackboard:
            self._register_services()
            self._subscribe_to_tasks()
        else:
            print(f"  WARNING: Cannot register/subscribe without DF and Blackboard")

    def _register_services(self):
        """
        Register capabilities with Directory Facilitator

        Registers as 'math.calculus' and 'math.algebra' services so
        Orchestrator can find us for both types of problems.

        REFERENCE:
        ---------
        Phase_1_Build_Order_Breakdown.md: Lines 188-194
        """
        if not self.df:
            return

        # Register for calculus
        calculus_reg = create_service_registration(
            service_type='math.calculus',
            agent_id=self.agent_id,
            algorithm='symbolic_sympy',
            cost='low'
        )
        self.df.register(calculus_reg)
        print(f"  [{self.agent_id}] Registered service: math.calculus")

        # Also register for algebra (SymPy handles both)
        algebra_reg = create_service_registration(
            service_type='math.algebra',
            agent_id=self.agent_id,
            algorithm='symbolic_sympy',
            cost='low'
        )
        self.df.register(algebra_reg)
        print(f"  [{self.agent_id}] Registered service: math.algebra")

    def _subscribe_to_tasks(self):
        """
        Subscribe to Calculus and Algebra tasks on Blackboard

        REFERENCE:
        ---------
        Phase_1_Build_Order_Breakdown.md: Lines 196-198
        """
        if not self.blackboard:
            return

        # Subscribe to Calculus tasks
        self.subscription_id = self.blackboard.subscribe(
            agent_id=self.agent_id,
            tags=['Calculus'],
            callback=self.on_task
        )

        # Also subscribe to Algebra tasks
        self.algebra_subscription_id = self.blackboard.subscribe(
            agent_id=self.agent_id,
            tags=['Algebra'],
            callback=self.on_task
        )

        print(f"  [{self.agent_id}] Subscribed to Blackboard: tags=['Calculus', 'Algebra']")

    def on_task(self, entry: BlackboardEntry):
        """
        Handle incoming task from Blackboard

        This callback is invoked when a new Calculus task appears on Blackboard.

        Args:
            entry: Blackboard entry containing task

        REFERENCE:
        ---------
        Phase_1_Build_Order_Breakdown.md: Lines 200-212
        """
        print(f"\n[{self.agent_id}] Received task: {entry.entry_id}")

        # Only process TASK entries that are PENDING
        if entry.entry_type != EntryType.TASK or entry.status != EntryStatus.PENDING:
            return

        # Check if this task is assigned to us (or no assignment)
        assigned_agent = entry.metadata.get('assigned_agent')
        if assigned_agent and assigned_agent != self.agent_id:
            return  # Not for us

        self.tasks_executed += 1

        try:
            # Extract problem information from metadata
            operation = entry.metadata.get('operation', 'compute')
            variable = entry.metadata.get('variable')
            if variable is None:
                variable = 'x'  # Default to 'x'
            sympy_expr_str = entry.metadata.get('sympy_expr')
            raw_input = entry.metadata.get('raw_input', '')

            print(f"  Operation: {operation}")
            print(f"  Expression: {sympy_expr_str}")
            print(f"  Variable: {variable}")

            # Execute symbolic operation
            result = self._execute(operation, sympy_expr_str, variable)

            print(f"  Result: {result}")

            # Convert result to OMDoc
            result_omdoc = self._sympy_to_omdoc(result)

            # Post candidate result to Blackboard
            self._post_candidate_result(entry, result, result_omdoc)

            self.tasks_succeeded += 1

        except Exception as e:
            print(f"  ERROR: {e}")
            self.tasks_failed += 1

            # Post error result
            self._post_error_result(entry, str(e))

    def _execute(self, operation: str, expr_str: str, variable: str) -> Any:
        """
        Execute symbolic operation via native symbolic engine (NO SymPy)

        Args:
            operation: Operation type (derivative, integral, etc.)
            expr_str: Expression string
            variable: Variable name

        Returns:
            Native symbolic result object

        REFERENCE:
        ---------
        Phase_1_Build_Order_Breakdown.md: Lines 214-221
        """
        # Parse variable using native Symbol
        var = Symbol(variable)

        # Parse expression using native parser
        try:
            expr = parse_expr(expr_str)
        except (SyntaxError, TypeError, ValueError, AttributeError):
            # Fallback: try direct sympify
            expr = sympify(expr_str)

        # Execute operation using native calculus
        if operation == 'derivative':
            success, result_str, _ = differentiate(expr_str, variable)
            if success:
                return sympify(result_str)
            return diff(expr, var)
        elif operation == 'integral':
            success, result_str, _ = native_integrate(expr_str, variable)
            if success:
                return sympify(result_str)
            return integrate(expr, var)
        elif operation == 'simplify':
            return simplify(expr)
        elif operation == 'expand':
            return expand(expr)
        elif operation == 'factor':
            return factor(expr)
        else:
            # Default: just simplify
            return simplify(expr)

    def _sympy_to_omdoc(self, expr: Any) -> OMObject:
        """Convert native symbolic expression to OMDoc"""
        # Use native symbolic types - check by string representation
        if expr is None:
            return create_variable('none')

        expr_str = str(expr)

        # Check if it's a simple variable/symbol
        if hasattr(expr, 'is_symbol') and expr.is_symbol:
            return create_variable(expr_str)

        # Check if it's a number
        try:
            if isinstance(expr, int):
                return create_number(int(expr))
            elif isinstance(expr, float):
                return create_number(float(expr))
            # Try to convert to float if it looks like a number
            float_val = float(expr_str)
            if float_val == int(float_val):
                return create_number(int(float_val))
            return create_number(float_val)
        except (ValueError, TypeError):
            pass

        # Check for operations by examining expression structure
        if hasattr(expr, 'args') and hasattr(expr, 'func'):
            func_name = type(expr).__name__
            args = expr.args if hasattr(expr, 'args') else []

            if func_name == 'Add' or '+' in expr_str:
                omdoc_args = [self._sympy_to_omdoc(arg) for arg in args]
                return create_operation(MathOperator.PLUS, *omdoc_args)

            elif func_name == 'Mul' or '*' in expr_str:
                omdoc_args = [self._sympy_to_omdoc(arg) for arg in args]
                return create_operation(MathOperator.TIMES, *omdoc_args)

            elif func_name == 'Pow' or '**' in expr_str:
                if len(args) >= 2:
                    base = self._sympy_to_omdoc(args[0])
                    exp = self._sympy_to_omdoc(args[1])
                    return create_operation(MathOperator.POWER, base, exp)

        # Fallback - treat as variable
        return create_variable(expr_str)

    def _post_candidate_result(
        self,
        original_entry: BlackboardEntry,
        result: Any,
        result_omdoc: OMObject
    ):
        """
        Post candidate result to Blackboard for verification

        Args:
            original_entry: Original task entry
            result: SymPy result
            result_omdoc: OMDoc representation of result

        REFERENCE:
        ---------
        Phase_1_Build_Order_Breakdown.md: Lines 205-211
        """
        if not self.blackboard:
            return

        # Create result entry (PARTIAL_RESULT since not yet verified)
        result_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=result_omdoc,
            author_agent=self.agent_id,
            conversation_id=original_entry.conversation_id,
            tags=[original_entry.conversation_id, 'verification_needed'],
            metadata={
                'parent_entry': original_entry.entry_id,
                'result_str': str(result),
                'solver': self.agent_id,
                'operation': original_entry.metadata.get('operation')
            }
        )
        # Set status to PENDING (awaits verification)
        result_entry.status = EntryStatus.PENDING

        # Post to Blackboard
        self.blackboard.post(result_entry)

        print(f"  [{self.agent_id}] Posted candidate result: {result_entry.entry_id}")
        print(f"    Status: PENDING (awaiting verification)")

    def _post_error_result(self, original_entry: BlackboardEntry, error: str):
        """Post error result to Blackboard"""
        if not self.blackboard:
            return

        error_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable('error'),
            author_agent=self.agent_id,
            conversation_id=original_entry.conversation_id,
            tags=[original_entry.conversation_id, 'error'],
            metadata={
                'parent_entry': original_entry.entry_id,
                'error': error,
                'solver': self.agent_id
            }
        )
        error_entry.status = EntryStatus.FAILED

        self.blackboard.post(error_entry)

    # BDI Implementation (simplified)
    def update_beliefs(self):
        """Update beliefs from environment"""
        pass

    def deliberate(self) -> List[Intention]:
        """Generate intentions"""
        return []

    def execute_step(self, intention: Intention):
        """Execute intention step"""
        pass

    def get_statistics(self) -> Dict[str, Any]:
        """Get solver statistics"""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'success_rate': (self.tasks_succeeded / self.tasks_executed * 100
                           if self.tasks_executed > 0 else 0)
        })
        return stats


if __name__ == "__main__":
    """Test Pilot Solver"""
    print("=" * 80)
    print("PHASE 1 - STEP 3: PILOT SOLVER TEST")
    print("=" * 80)
    print()

    # Initialize Phase 0 infrastructure
    from symbo_agentic_reasoners.core.system import Phase0System

    print("Initializing Phase 0 infrastructure...")
    phase0 = Phase0System()
    phase0.start()
    print()

    # Initialize Pilot Solver
    pilot = PilotSolverAgent(
        df=phase0.df,
        blackboard=phase0.blackboard
    )
    print()

    # Verify registration
    print("Verifying registration with Directory Facilitator...")
    services = phase0.df.search(service_type='math.calculus')
    print(f"  Found {len(services)} math.calculus service(s)")
    for svc in services:
        print(f"    - {svc.agent_id}: {svc.algorithm}")
    print()

    # Test: Post a task to Blackboard
    print("Test: Posting calculus task to Blackboard...")
    test_task = create_entry(
        entry_type=EntryType.TASK,
        content=create_variable('x**2+1'),
        author_agent='test',
        conversation_id='test_conv',
        tags=['Calculus', 'test_conv'],
        metadata={
            'operation': 'derivative',
            'variable': 'x',
            'sympy_expr': 'x**2 + 1',
            'raw_input': 'derivative of x**2 + 1'
        }
    )

    phase0.blackboard.post(test_task)
    print(f"  Posted task: {test_task.entry_id}")
    print()

    # Wait a moment for callback to fire
    import time
    print("Waiting for solver to process...")
    time.sleep(1)
    print()

    # Check for results
    print("Checking for results...")
    results = phase0.blackboard.query_entries(
        tags=['test_conv'],
        entry_type=EntryType.PARTIAL_RESULT
    )
    print(f"  Found {len(results)} result(s)")
    for result in results:
        print(f"    - {result.entry_id}: Status={result.status.value}")
        print(f"      Result: {result.metadata.get('result_str')}")
    print()

    print("=" * 80)
    print("PILOT SOLVER TEST COMPLETE")
    print("=" * 80)
    print()
    print("Statistics:")
    import json
    print(json.dumps(pilot.get_statistics(), indent=2))

    # Shutdown
    phase0.shutdown()
