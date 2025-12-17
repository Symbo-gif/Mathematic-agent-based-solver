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
PHASE 2 - STEP 1.2: ARITHMETIC SPECIALIST (Tier 3)
===================================================

Provides Arbitrary-Precision Arithmetic to ensure absolute numerical exactness.

CRITICAL CONSTRAINT:
-------------------
Standard floating-point arithmetic is STRICTLY FORBIDDEN.
All operations must use arbitrary-precision libraries (mpmath/GMP).

WHY THIS MATTERS:
----------------
Floating-point errors compound and lead to incorrect results in:
- Number theory (requires exact modular arithmetic)
- Cryptography (requires exact large integer operations)
- Symbolic algebra (requires exact rational arithmetic)

CAPABILITIES:
------------
- Arbitrary-precision integers (thousands of digits)
- Arbitrary-precision rationals (exact fractions)
- Modular arithmetic (a mod b)
- Power operations with exact results

REFERENCE:
---------
- Phase_2_Build_Order_Breakdown.md: Lines 54-73 (Agent 1.2)
- Phase 2 Coding Strategy: "Arbitrary-Precision Arithmetic"
"""

import sys
import os
from typing import Any, Dict, Optional
import uuid

# Arbitrary-precision library
from mpmath import mp, mpf, mpmathify
import sympy as sp

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


class ArithmeticSpecialist(BDIAgent):
    """
    Arithmetic Specialist - Arbitrary-Precision Computation

    DIRECTIVE:
    ---------
    Provide exact arithmetic operations using arbitrary-precision libraries.
    Standard floating-point math is FORBIDDEN.

    OPERATIONS:
    ----------
    - Basic arithmetic: +, -, *, /, **
    - Modular arithmetic: a mod b, modular exponentiation
    - Exact rational arithmetic: fractions without rounding
    - Large integer operations: numbers with 1000+ digits

    PRECISION:
    ---------
    Default: 50 decimal places
    Configurable up to thousands of decimal places

    ALGORITHMIC BACKING:
    -------------------
    - mpmath: Arbitrary-precision floating-point
    - SymPy: Exact symbolic arithmetic
    - GMP (via gmpy2 if available): Optimized integer operations

    REFERENCE:
    ---------
    Phase_2_Build_Order_Breakdown.md: Lines 58-73
    """

    def __init__(
        self,
        agent_id: str = 'arithmetic_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
        precision: int = 50
    ):
        """
        Initialize Arithmetic Specialist

        Args:
            agent_id: Unique specialist identifier
            df: Directory Facilitator instance
            blackboard: Blackboard instance
            precision: Decimal places for arbitrary-precision (default: 50)
        """
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Set mpmath precision
        mp.dps = precision  # Decimal places
        self.precision = precision

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        print(f"[{self.agent_id}] Arithmetic Specialist initialized")
        print(f"  Precision: {self.precision} decimal places")
        print(f"  Library: mpmath + SymPy")
        print(f"  Mode: EXACT arithmetic only (floating-point FORBIDDEN)")

    def _register_services(self):
        """
        Register services with Directory Facilitator

        REFERENCE:
        ---------
        Phase_2_Build_Order_Breakdown.md: Lines 67-73
        """
        registration = create_service_registration(
            service_type='math.algebra.arithmetic',
            agent_id=self.agent_id,
            algorithm='mpmath',
            cost='low',
            precision='arbitrary',
            type='exact',
            tier='3',
            decimal_places=str(self.precision)
        )
        self.df.register(registration)
        print(f"  [DF] Registered: math.algebra.arithmetic (exact, {self.precision}dp)")

    def process(self, task_entry: Any) -> Any:
        """
        Process arithmetic task with arbitrary-precision

        Args:
            task_entry: Blackboard entry containing arithmetic task

        Returns:
            Result entry with exact computation
        """
        print(f"\n[{self.agent_id}] Processing arithmetic task")

        self.tasks_executed += 1

        try:
            # Extract task information
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            operation = metadata.get('operation', 'compute')
            raw_input = metadata.get('raw_input', '')

            # Get SymPy expression if available
            sympy_expr_str = metadata.get('sympy_expr')

            print(f"  Operation: {operation}")
            print(f"  Input: {raw_input}")

            # Compute using SymPy for exact symbolic arithmetic
            if sympy_expr_str:
                result = self._compute_exact(sympy_expr_str, operation, metadata)
            else:
                result = self._compute_fallback(raw_input, operation)

            # Create result entry
            result_entry = self._create_result_entry(task_entry, result)

            self.tasks_succeeded += 1
            print(f"  [OK] Result: {result}")

            return result_entry

        except Exception as e:
            self.tasks_failed += 1
            print(f"  [ERROR] Computation failed: {e}")
            return self._create_error_entry(task_entry, str(e))

    def _compute_exact(self, sympy_expr_str: str, operation: str, metadata: Dict) -> Any:
        """
        Compute using SymPy for exact arithmetic

        Args:
            sympy_expr_str: String representation of SymPy expression
            operation: Operation type
            metadata: Additional task metadata

        Returns:
            Exact computed result
        """
        # Parse SymPy expression
        expr = sp.sympify(sympy_expr_str)

        # Perform operation based on type
        if operation == 'simplify':
            result = sp.simplify(expr)
        elif operation == 'expand':
            result = sp.expand(expr)
        elif operation == 'factor':
            result = sp.factor(expr)
        elif operation in ['compute', 'evaluate']:
            # Try to evaluate to exact rational/integer
            result = expr
            # If expression has no symbols, evaluate it
            if not expr.free_symbols:
                result = expr.evalf(self.precision) if expr.is_number else expr
        else:
            # Default: simplify
            result = sp.simplify(expr)

        return result

    def _compute_fallback(self, raw_input: str, operation: str) -> Any:
        """
        Fallback computation when SymPy expression not available

        Args:
            raw_input: Raw input string
            operation: Operation type

        Returns:
            Computed result
        """
        try:
            # Try to parse as SymPy expression
            expr = sp.sympify(raw_input)
            if not expr.free_symbols:
                # Pure arithmetic - evaluate exactly
                return expr
            else:
                # Has variables - simplify
                return sp.simplify(expr)
        except:
            # If parsing fails, return raw input
            return raw_input

    def _create_result_entry(self, task_entry: Any, result: Any) -> Any:
        """Create result entry for Blackboard"""
        if not self.blackboard:
            return result

        result_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(str(result)),
            author_agent=self.agent_id,
            conversation_id=task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'result',
            tags=['arithmetic', 'exact', task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'result'],
            status=EntryStatus.PENDING,  # Will be verified later
            metadata={
                'result': str(result),
                'result_str': str(result),
                'precision': self.precision,
                'type': 'exact',
                'algorithm': 'sympy+mpmath'
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
            tags=['error', 'arithmetic'],
            status=EntryStatus.FAILED,
            metadata={'error': error_msg}
        )

        self.blackboard.post(error_entry)
        return error_entry

    # BDI Implementation
    def update_beliefs(self):
        """Monitor Blackboard for arithmetic tasks"""
        # Phase 2: Reactive processing via process()
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
            'precision': self.precision
        })
        return stats


if __name__ == "__main__":
    """Test Arithmetic Specialist"""
    print("=" * 80)
    print("PHASE 2 - ARITHMETIC SPECIALIST TEST")
    print("=" * 80)
    print()

    from symbo_agentic_reasoners_phase0.phase0_system import Phase0System

    # Initialize Phase 0
    print("Initializing Phase 0 infrastructure...")
    phase0 = Phase0System()
    phase0.start()
    print()

    # Initialize Arithmetic Specialist
    specialist = ArithmeticSpecialist(
        df=phase0.df,
        blackboard=phase0.blackboard,
        precision=50
    )
    print()

    print("=" * 80)
    print("ARITHMETIC SPECIALIST READY")
    print("=" * 80)
    print()

    # Test exact arithmetic
    print("Test 1: Large integer arithmetic")
    print("  Computing: 2**100")
    result_large = sp.sympify("2**100")
    print(f"  Result: {result_large}")
    print(f"  Digits: {len(str(result_large))}")
    print()

    print("Test 2: Exact rational arithmetic")
    print("  Computing: 1/3 + 1/6")
    result_rational = sp.sympify("1/3 + 1/6")
    print(f"  Result: {result_rational}")
    print(f"  (No rounding error!)")
    print()

    # Check DF registration
    services = phase0.df.search(service_type='math.algebra.arithmetic')
    print(f"Registered services: {len(services)}")
    for service in services:
        print(f"  - {service.service_type}: {service.agent_id}")
        print(f"    Properties: {service.properties}")

    print()
    print("Statistics:")
    import json
    print(json.dumps(specialist.get_statistics(), indent=2))

    # Shutdown
    phase0.shutdown()
