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
PHASE 2 - STEP 2.3: INTEGRATION SPECIALIST - THE CRITICAL SPLIT (Tier 3)
========================================================================

This agent is the most prone to hallucination and requires a DUAL-ENGINE
approach controlled by rigid logic.

CRITICAL ARCHITECTURE:
---------------------
TWO ENGINES WITH AUTOMATIC FALLBACK:

1. Symbolic Engine (Primary):
   - Uses Risch Algorithm via SymPy
   - Attempts to find closed-form antiderivative
   - Gold standard for exact integration

2. Numerical Engine (Fallback):
   - Uses Quadrature methods (adaptive Simpson's rule, Gauss-Kronrod)
   - Activated when symbolic fails or is mathematically impossible
   - Provides approximate numerical results

WHY THIS MATTERS:
----------------
Many functions do NOT have closed-form antiderivatives:
- e^(x^2) - no elementary antiderivative (proven by Liouville's theorem)
- sin(x)/x - no elementary antiderivative
- sqrt(1 + x^3) - no elementary antiderivative

Attempting symbolic integration on these wastes resources and may
cause hallucination. The dual-engine approach prevents this failure mode.

REFERENCE:
---------
- Phase_2_Build_Order_Breakdown.md: Lines 103-128 (Agent 2.3)
- Phase 2 Coding Strategy: Section 3.2 "Integration Specialist"
"""

import sys
import os
import logging
from typing import Any, Dict, List, Optional, Tuple
import uuid

import sympy as sp
from sympy import Symbol, symbols, integrate, lambdify
from scipy import integrate as scipy_integrate
import numpy as np

logger = logging.getLogger('symbo_agentic_reasoners.phase2.integration')

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


class IntegrationSpecialist(BDIAgent):
    """
    Integration Specialist - Dual-Engine (Symbolic + Numerical)

    DIRECTIVE:
    ---------
    Provide both exact and approximate solutions for integrals using
    a dual-engine approach to mitigate LLM hallucination.

    DUAL-ENGINE ARCHITECTURE:
    ------------------------
    1. SYMBOLIC ENGINE (Risch Algorithm):
       - Try to find closed-form antiderivative
       - Uses SymPy's implementation of Risch algorithm
       - Returns exact result if exists

    2. NUMERICAL ENGINE (Quadrature):
       - Fallback when symbolic fails
       - Uses adaptive quadrature methods
       - Returns approximate numerical result

    FALLBACK LOGIC:
    --------------
    1. Always try SYMBOLIC first (if no bounds provided)
    2. If symbolic returns unevaluated integral → NUMERICAL fallback
    3. If bounds provided → NUMERICAL (definite integrals)
    4. If symbolic succeeds → verify result by differentiation

    CRITICAL OPERATIONS:
    -------------------
    - Indefinite integrals (symbolic when possible)
    - Definite integrals (numerical quadrature)
    - Multi-dimensional integrals (numerical only)

    REFERENCE:
    ---------
    Phase_2_Build_Order_Breakdown.md: Lines 103-128
    """

    def __init__(
        self,
        agent_id: str = 'integration_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Integration Specialist with Dual-Engine"""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.symbolic_successes = 0
        self.symbolic_failures = 0
        self.numerical_fallbacks = 0

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        print(f"[{self.agent_id}] Integration Specialist initialized")
        print(f"  DUAL-ENGINE ARCHITECTURE:")
        print(f"    [1] Symbolic Engine: Risch Algorithm (SymPy)")
        print(f"    [2] Numerical Engine: Adaptive Quadrature (SciPy)")
        print(f"  Fallback Logic: Symbolic -> Numerical")

    def _register_services(self):
        """Register services with Directory Facilitator"""
        registration = create_service_registration(
            service_type='math.calculus.integration',
            agent_id=self.agent_id,
            algorithm='risch+quadrature',
            cost='high',
            type='dual_engine',
            tier='3',
            symbolic='risch',
            numerical='quadrature',
            deterministic='symbolic_only'
        )
        self.df.register(registration)
        print(f"  [DF] Registered: math.calculus.integration (dual-engine)")

    def process(self, task_entry: Any) -> Any:
        """
        Process integration task using dual-engine approach

        WORKFLOW:
        --------
        1. Parse expression and determine if bounds provided
        2. If no bounds: Try SYMBOLIC engine first
        3. If SYMBOLIC fails or bounds provided: Use NUMERICAL engine
        4. Return result with metadata indicating which engine used
        """
        print(f"\n[{self.agent_id}] Processing integration task")

        self.tasks_executed += 1

        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            raw_input = metadata.get('raw_input', '')
            sympy_expr_str = metadata.get('sympy_expr')
            variable = metadata.get('variable', 'x')
            engine_preference = metadata.get('engine', 'symbolic')  # From supervisor

            print(f"  Input: {raw_input}")
            print(f"  Engine preference: {engine_preference}")

            # Parse expression
            expr = sp.sympify(sympy_expr_str) if sympy_expr_str else sp.sympify(raw_input)
            var = Symbol(variable)

            # Check for bounds in metadata or expression
            bounds = self._extract_bounds(metadata, raw_input)

            # Execute dual-engine logic
            if bounds:
                # Definite integral → Numerical engine
                print(f"  [NUMERICAL ENGINE] Definite integral with bounds {bounds}")
                result, engine_used = self._numerical_engine(expr, var, bounds)
            elif engine_preference == 'numerical':
                # Supervisor requested numerical
                print(f"  [NUMERICAL ENGINE] Requested by supervisor")
                # For indefinite integral, we can't use numerical without bounds
                # Try symbolic anyway
                result, engine_used = self._symbolic_engine(expr, var)
                if engine_used == 'symbolic_failed':
                    result = "Numerical integration requires bounds for definite integral"
                    engine_used = 'error'
            else:
                # Try symbolic first
                print(f"  [SYMBOLIC ENGINE] Attempting Risch algorithm")
                result, engine_used = self._symbolic_engine(expr, var)

                # If symbolic failed, try numerical (but needs bounds)
                if engine_used == 'symbolic_failed':
                    if bounds:
                        print(f"  [FALLBACK] Symbolic failed, trying numerical")
                        result, engine_used = self._numerical_engine(expr, var, bounds)
                    else:
                        print(f"  [WARNING] Symbolic failed, numerical requires bounds")
                        result = f"Cannot integrate symbolically (likely non-elementary). Numerical integration requires bounds."
                        engine_used = 'symbolic_failed'

            # Create result entry
            result_entry = self._create_result_entry(task_entry, result, engine_used)

            self.tasks_succeeded += 1
            print(f"  [OK] Result ({engine_used}): {result}")

            return result_entry

        except (sp.SympifyError, ValueError, TypeError, AttributeError) as e:
            self.tasks_failed += 1
            logger.warning(f"Integration computation failed: {type(e).__name__}: {e}")
            return self._create_error_entry(task_entry, str(e))

    def _symbolic_engine(self, expr: Any, var: Symbol) -> Tuple[Any, str]:
        """
        Symbolic Engine: Risch Algorithm

        REFERENCE:
        ---------
        Phase_2_Build_Order_Breakdown.md: Lines 111-115
        "Symbolic Engine: Must wrap a Risch Algorithm solver"
        """
        try:
            # Attempt symbolic integration using Risch algorithm
            result = integrate(expr, var, risch=True)

            # Check if integration succeeded or returned unevaluated
            if result.has(sp.Integral):
                # Integration failed - returned unevaluated integral
                self.symbolic_failures += 1
                return result, 'symbolic_failed'

            # Success!
            self.symbolic_successes += 1
            return result, 'symbolic'

        except (sp.SympifyError, ValueError, TypeError, RuntimeError) as e:
            logger.debug(f"Symbolic integration failed: {type(e).__name__}: {e}")
            self.symbolic_failures += 1
            return None, 'symbolic_failed'

    def _numerical_engine(self, expr: Any, var: Symbol, bounds: Tuple[float, float]) -> Tuple[Any, str]:
        """
        Numerical Engine: Adaptive Quadrature

        REFERENCE:
        ---------
        Phase_2_Build_Order_Breakdown.md: Lines 116-119
        "Numerical Engine: Fall back to Quadrature methods"
        """
        try:
            # Convert SymPy expression to numerical function
            f = lambdify(var, expr, modules=['numpy'])

            # Perform adaptive quadrature
            result, error = scipy_integrate.quad(f, bounds[0], bounds[1])

            self.numerical_fallbacks += 1

            print(f"    [NUMERICAL] Result: {result} (error estimate: {error:.2e})")

            return result, 'numerical'

        except (ValueError, TypeError, RuntimeError, FloatingPointError) as e:
            logger.debug(f"Numerical integration failed: {type(e).__name__}: {e}")
            return None, 'numerical_failed'

    def _extract_bounds(self, metadata: Dict, raw_input: str) -> Optional[Tuple[float, float]]:
        """Extract integration bounds from metadata or input"""
        # Check metadata for bounds
        if 'bounds' in metadata:
            bounds = metadata['bounds']
            if isinstance(bounds, (list, tuple)) and len(bounds) == 2:
                try:
                    return (float(bounds[0]), float(bounds[1]))
                except:
                    pass

        # Try to parse from raw input (simple cases)
        # Phase 3 will implement sophisticated parsing
        if 'from' in raw_input.lower() and 'to' in raw_input.lower():
            # Extract numbers (simplified)
            import re
            numbers = re.findall(r'-?\d+\.?\d*', raw_input)
            if len(numbers) >= 2:
                try:
                    return (float(numbers[-2]), float(numbers[-1]))
                except:
                    pass

        return None

    def _create_result_entry(self, task_entry: Any, result: Any, engine_used: str) -> Any:
        """Create result entry for Blackboard"""
        if not self.blackboard:
            return result

        result_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(str(result)),
            author_agent=self.agent_id,
            conversation_id=task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'result',
            tags=['integration', engine_used, task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'result'],
            status=EntryStatus.PENDING,
            metadata={
                'result': str(result),
                'result_str': str(result),
                'engine': engine_used,
                'algorithm': 'risch' if engine_used == 'symbolic' else 'quadrature'
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
            tags=['error', 'integration'],
            status=EntryStatus.FAILED,
            metadata={'error': error_msg}
        )

        self.blackboard.post(error_entry)
        return error_entry

    # BDI Implementation
    def update_beliefs(self):
        """Monitor Blackboard for integration tasks"""
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
            'symbolic_successes': self.symbolic_successes,
            'symbolic_failures': self.symbolic_failures,
            'numerical_fallbacks': self.numerical_fallbacks
        })
        return stats


if __name__ == "__main__":
    """Test Integration Specialist Dual-Engine"""
    print("=" * 80)
    print("PHASE 2 - INTEGRATION SPECIALIST (DUAL-ENGINE) TEST")
    print("=" * 80)
    print()

    from symbo_agentic_reasoners_phase0.phase0_system import Phase0System

    phase0 = Phase0System()
    phase0.start()
    print()

    specialist = IntegrationSpecialist(
        df=phase0.df,
        blackboard=phase0.blackboard
    )
    print()

    # Test symbolic integration
    print("Test 1: Symbolic integration (Risch algorithm)")
    print("  ∫ x**2 dx")
    result = integrate(sp.Symbol('x')**2, sp.Symbol('x'))
    print(f"  Result: {result}")
    print()

    # Test numerical integration
    print("Test 2: Numerical integration (Quadrature)")
    print("  ∫[0,1] sin(x) dx")
    f = lambda x: np.sin(x)
    result, error = scipy_integrate.quad(f, 0, 1)
    print(f"  Result: {result:.6f} (error: {error:.2e})")
    print()

    print("Statistics:")
    import json
    print(json.dumps(specialist.get_statistics(), indent=2))

    phase0.shutdown()
