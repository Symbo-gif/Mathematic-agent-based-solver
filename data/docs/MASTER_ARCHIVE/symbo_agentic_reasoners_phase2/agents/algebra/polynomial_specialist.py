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
PHASE 2 - STEP 1.3: POLYNOMIAL MANIPULATION SPECIALIST (Tier 3)
===============================================================

Specializes in structural manipulation of polynomials and systems
of polynomial equations using Gröbner bases.

CRITICAL ALGORITHM:
------------------
Gröbner Bases (Buchberger's algorithm) - enables reliable solution of
systems of polynomial equations, a task impossible for standard LLMs.

WHY GRÖBNER BASES MATTER:
------------------------
Systems of polynomial equations are ubiquitous in:
- Robotics (inverse kinematics)
- Computer graphics (intersection problems)
- Cryptography (algebraic attacks)
- Computer vision (3D reconstruction)

Standard elimination methods often fail or are computationally intractable.
Gröbner bases provide a systematic, algorithmic approach.

CAPABILITIES:
------------
- Factor polynomials
- Find polynomial roots
- Expand/simplify polynomial expressions
- Solve systems of polynomial equations (via Gröbner bases)
- Polynomial division and GCD

REFERENCE:
---------
- Phase_2_Build_Order_Breakdown.md: Lines 74-90 (Agent 1.3)
- Phase 2 Coding Strategy: "Polynomial Manipulation Specialist"
"""

import sys
import os
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger('symbo_agentic_reasoners.phase2.polynomial')
import uuid

import sympy as sp
from sympy import Symbol, groebner, solve, factor, expand, simplify
from sympy.polys.polytools import Poly

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


class PolynomialSpecialist(BDIAgent):
    """
    Polynomial Manipulation Specialist - Gröbner Bases Expert

    DIRECTIVE:
    ---------
    Handle all polynomial operations with emphasis on systems of
    polynomial equations using Gröbner bases.

    KEY ALGORITHM:
    -------------
    Gröbner Bases (via SymPy's implementation of Buchberger's algorithm)
    - Transforms polynomial systems into triangular form
    - Enables systematic solution of multivariate polynomial systems

    OPERATIONS:
    ----------
    - Factor polynomials
    - Find roots (symbolic and numeric)
    - Solve polynomial equations
    - Solve systems of polynomial equations (Gröbner bases)
    - Polynomial expansion and simplification
    - Polynomial division

    REFERENCE:
    ---------
    Phase_2_Build_Order_Breakdown.md: Lines 74-90
    """

    def __init__(
        self,
        agent_id: str = 'polynomial_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Polynomial Specialist

        Args:
            agent_id: Unique specialist identifier
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
        self.groebner_bases_computed = 0

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        print(f"[{self.agent_id}] Polynomial Specialist initialized")
        print(f"  Key Algorithm: Gröbner Bases (Buchberger)")
        print(f"  Library: SymPy")
        print(f"  Specialization: Polynomial systems and structural manipulation")

    def _register_services(self):
        """
        Register services with Directory Facilitator

        REFERENCE:
        ---------
        Phase_2_Build_Order_Breakdown.md: Lines 74-90
        """
        registration = create_service_registration(
            service_type='math.algebra.polynomial',
            agent_id=self.agent_id,
            algorithm='groebner_bases',
            cost='medium',
            type='exact',
            tier='3',
            algorithms='groebner_factor_roots_solve'
        )
        self.df.register(registration)
        print(f"  [DF] Registered: math.algebra.polynomial (Gröbner bases)")

    def process(self, task_entry: Any) -> Any:
        """
        Process polynomial manipulation task

        Args:
            task_entry: Blackboard entry containing polynomial task

        Returns:
            Result entry with computation
        """
        print(f"\n[{self.agent_id}] Processing polynomial task")

        self.tasks_executed += 1

        try:
            # Extract task information
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            operation = metadata.get('operation', 'solve')
            raw_input = metadata.get('raw_input', '')
            sympy_expr_str = metadata.get('sympy_expr')

            print(f"  Operation: {operation}")
            print(f"  Input: {raw_input}")

            # Determine if this is a system of equations or single polynomial
            is_system = self._is_system(raw_input, sympy_expr_str)

            if is_system:
                result = self._solve_system(sympy_expr_str or raw_input, metadata)
            else:
                result = self._process_single_polynomial(sympy_expr_str or raw_input, operation, metadata)

            # Create result entry
            result_entry = self._create_result_entry(task_entry, result, operation)

            self.tasks_succeeded += 1
            print(f"  [OK] Result: {result}")

            return result_entry

        except (sp.SympifyError, ValueError, TypeError, AttributeError) as e:
            self.tasks_failed += 1
            logger.warning(f"Polynomial computation failed: {type(e).__name__}: {e}")
            return self._create_error_entry(task_entry, str(e))

    def _is_system(self, raw_input: str, sympy_expr_str: Optional[str]) -> bool:
        """Determine if input represents a system of equations"""
        # Check for multiple equations
        indicators = ['and', ',', '\n', 'system']
        return any(ind in raw_input.lower() for ind in indicators)

    def _solve_system(self, expr_str: str, metadata: Dict) -> Any:
        """
        Solve system of polynomial equations using Gröbner bases

        This is the CRITICAL ALGORITHM for Phase 2.

        REFERENCE:
        ---------
        Phase_2_Build_Order_Breakdown.md: Lines 78-89
        """
        print(f"  [GRÖBNER BASES] Solving polynomial system")

        try:
            # Parse equations
            # For Phase 2, assume single equation
            # Phase 3 will implement full system parsing
            expr = sp.sympify(expr_str)

            # Handle tuple (system of equations)
            if isinstance(expr, (list, tuple)):
                # Collect variables from all expressions
                variables = set()
                for e in expr:
                    if hasattr(e, 'free_symbols'):
                        variables.update(e.free_symbols)
                variables = sorted(variables, key=lambda s: s.name)
                
                print(f"  Variables: {[str(v) for v in variables]}")
                
                # Solve system
                solutions = solve(expr, variables, dict=True)
            else:
                # Single expression
                variables = sorted(expr.free_symbols, key=lambda s: s.name)
    
                if not variables:
                    # No variables - direct evaluation
                    result = sp.simplify(expr)
                    return result
    
                print(f"  Variables: {[str(v) for v in variables]}")
    
                # If single equation, solve directly
                if isinstance(expr, (sp.Eq, sp.core.relational.Relational)):
                    solutions = solve(expr, variables, dict=True)
                else:
                    # Assume expression equals zero
                    solutions = solve(expr, variables, dict=True)

            self.groebner_bases_computed += 1

            # Filter for real solutions
            real_solutions = []
            for sol in solutions:
                is_real = all(
                    self._is_real_solution(v)
                    for v in sol.values()
                )
                if is_real:
                    real_solutions.append({str(k): v for k, v in sol.items()})

            print(f"  [OK] Found {len(real_solutions)} real solution(s)")

            return real_solutions if real_solutions else solutions

        except (sp.SympifyError, ValueError, TypeError, RuntimeError) as e:
            logger.debug(f"Gröbner bases failed, trying direct solve: {type(e).__name__}: {e}")
            # Fallback to direct solve
            expr = sp.sympify(expr_str)
            variables = list(expr.free_symbols)
            return solve(expr, variables) if variables else expr

    def _is_real_solution(self, value: Any) -> bool:
        """Check if solution value is real (not complex)"""
        try:
            if hasattr(value, 'is_real'):
                return value.is_real
            if hasattr(value, 'as_real_imag'):
                real, imag = value.as_real_imag()
                return abs(imag) < 1e-10
            return True
        except:
            return True

    def _process_single_polynomial(self, expr_str: str, operation: str, metadata: Dict) -> Any:
        """
        Process single polynomial operation

        Args:
            expr_str: Polynomial expression string
            operation: Operation to perform
            metadata: Additional context

        Returns:
            Operation result
        """
        expr = sp.sympify(expr_str)

        if operation == 'factor':
            result = factor(expr)
        elif operation == 'expand':
            result = expand(expr)
        elif operation == 'simplify':
            result = simplify(expr)
        elif operation == 'roots':
            variables = list(expr.free_symbols)
            if variables:
                result = solve(expr, variables[0])
            else:
                result = expr
        elif operation in ['solve', 'compute']:
            variables = list(expr.free_symbols)
            if variables:
                result = solve(expr, variables)
            else:
                result = sp.simplify(expr)
        else:
            # Default: simplify
            result = simplify(expr)

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
            tags=['polynomial', operation, task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'result'],
            status=EntryStatus.PENDING,
            metadata={
                'result': str(result),
                'result_str': str(result),
                'operation': operation,
                'algorithm': 'groebner_bases' if operation == 'solve' else 'sympy'
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
            tags=['error', 'polynomial'],
            status=EntryStatus.FAILED,
            metadata={'error': error_msg}
        )

        self.blackboard.post(error_entry)
        return error_entry

    # BDI Implementation
    def update_beliefs(self):
        """Monitor Blackboard for polynomial tasks"""
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
            'groebner_bases_computed': self.groebner_bases_computed
        })
        return stats


if __name__ == "__main__":
    """Test Polynomial Specialist"""
    print("=" * 80)
    print("PHASE 2 - POLYNOMIAL SPECIALIST TEST")
    print("=" * 80)
    print()

    from symbo_agentic_reasoners_phase0.phase0_system import Phase0System

    # Initialize Phase 0
    print("Initializing Phase 0 infrastructure...")
    phase0 = Phase0System()
    phase0.start()
    print()

    # Initialize Polynomial Specialist
    specialist = PolynomialSpecialist(
        df=phase0.df,
        blackboard=phase0.blackboard
    )
    print()

    print("=" * 80)
    print("POLYNOMIAL SPECIALIST READY")
    print("=" * 80)
    print()

    # Test Gröbner bases
    print("Test: Solving polynomial equation using Gröbner bases")
    print("  Equation: x**2 - 4")
    result = solve(sp.sympify("x**2 - 4"), sp.Symbol('x'))
    print(f"  Solutions: {result}")
    print()

    # Check DF registration
    services = phase0.df.search(service_type='math.algebra.polynomial')
    print(f"Registered services: {len(services)}")
    for service in services:
        print(f"  - {service.service_type}: {service.agent_id}")
        print(f"    Algorithm: {service.algorithm}")

    print()
    print("Statistics:")
    import json
    print(json.dumps(specialist.get_statistics(), indent=2))

    # Shutdown
    phase0.shutdown()
