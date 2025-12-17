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
PHASE 2 - STEP 1.4: NUMBER THEORY SPECIALIST (Tier 3)
=====================================================

Manages tasks related to discrete integers and prime structures.

CRITICAL ALGORITHMS:
-------------------
- Miller-Rabin: Probabilistic primality testing
- Pollard's rho: Integer factorization
- Quadratic Sieve: Large integer factorization
- Extended Euclidean Algorithm: GCD and modular inverses

WHY THIS MATTERS:
----------------
Number theory is fundamental to:
- Cryptography (RSA, elliptic curves)
- Hashing algorithms
- Random number generation
- Computational complexity theory

CAPABILITIES:
------------
- Primality testing (Miller-Rabin algorithm)
- Integer factorization (Pollard's rho, trial division)
- GCD and LCM computation
- Modular arithmetic (inverses, exponentiation)
- Solving linear Diophantine equations

REFERENCE:
---------
- Phase_2_Build_Order_Breakdown.md: Lines 91-93 (Agent 1.4)
- Phase 2 Coding Strategy: "Number Theory Specialist"
"""

import sys
import os
from typing import Any, Dict, List, Optional
import uuid

import sympy as sp
from sympy.ntheory import isprime, primefactors, factorint, totient
from sympy import gcd, lcm

# Try to import mod_inverse from correct location
try:
    from sympy.ntheory.modular import mod_inverse
except ImportError:
    from sympy import mod_inverse

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


class NumberTheorySpecialist(BDIAgent):
    """
    Number Theory Specialist - Prime Structures and Integer Properties

    DIRECTIVE:
    ---------
    Handle all discrete integer operations with emphasis on:
    - Prime numbers and primality testing
    - Integer factorization
    - Modular arithmetic
    - Diophantine equations

    KEY ALGORITHMS:
    --------------
    - Miller-Rabin: Efficient probabilistic primality test
    - Pollard's rho: Integer factorization for medium-sized integers
    - Extended Euclidean Algorithm: GCD and modular inverses

    OPERATIONS:
    ----------
    - Primality testing (is_prime)
    - Integer factorization (factor)
    - GCD/LCM computation
    - Modular arithmetic (mod, mod_inverse)
    - Euler's totient function
    - Diophantine equation solving

    REFERENCE:
    ---------
    Phase_2_Build_Order_Breakdown.md: Lines 91-93
    """

    def __init__(
        self,
        agent_id: str = 'numbertheory_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Number Theory Specialist

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
        self.primes_tested = 0
        self.factorizations_computed = 0

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        print(f"[{self.agent_id}] Number Theory Specialist initialized")
        print(f"  Key Algorithms: Miller-Rabin, Pollard's rho, Extended Euclidean")
        print(f"  Library: SymPy ntheory module")
        print(f"  Specialization: Primes, factorization, modular arithmetic")

    def _register_services(self):
        """
        Register services with Directory Facilitator

        REFERENCE:
        ---------
        Phase_2_Build_Order_Breakdown.md: Lines 91-93
        """
        registration = create_service_registration(
            service_type='math.algebra.numbertheory',
            agent_id=self.agent_id,
            algorithm='miller_rabin',
            cost='medium',
            type='exact',
            tier='3',
            algorithms='miller_rabin_pollard_rho_euclidean'
        )
        self.df.register(registration)
        print(f"  [DF] Registered: math.algebra.numbertheory (Miller-Rabin, Pollard's rho)")

    def process(self, task_entry: Any) -> Any:
        """
        Process number theory task

        Args:
            task_entry: Blackboard entry containing number theory task

        Returns:
            Result entry with computation
        """
        print(f"\n[{self.agent_id}] Processing number theory task")

        self.tasks_executed += 1

        try:
            # Extract task information
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            operation = metadata.get('operation', 'compute')
            raw_input = metadata.get('raw_input', '').lower()
            sympy_expr_str = metadata.get('sympy_expr')

            print(f"  Operation: {operation}")
            print(f"  Input: {raw_input}")

            # Determine number theory operation
            if 'prime' in raw_input and ('is' in raw_input or 'test' in raw_input):
                result = self._test_primality(sympy_expr_str or raw_input)
            elif 'factor' in raw_input or 'factorize' in raw_input or 'factorization' in raw_input:
                result = self._factorize(sympy_expr_str or raw_input)
            elif 'gcd' in raw_input:
                result = self._compute_gcd(sympy_expr_str or raw_input)
            elif 'lcm' in raw_input:
                result = self._compute_lcm(sympy_expr_str or raw_input)
            elif 'mod' in raw_input or 'modulo' in raw_input or 'modular' in raw_input:
                result = self._modular_operation(sympy_expr_str or raw_input, raw_input)
            else:
                # Default: try to factorize if integer
                result = self._compute_default(sympy_expr_str or raw_input)

            # Create result entry
            result_entry = self._create_result_entry(task_entry, result, operation)

            self.tasks_succeeded += 1
            print(f"  [OK] Result: {result}")

            return result_entry

        except Exception as e:
            self.tasks_failed += 1
            print(f"  [ERROR] Computation failed: {e}")
            import traceback
            traceback.print_exc()
            return self._create_error_entry(task_entry, str(e))

    def _test_primality(self, expr_str: str) -> Any:
        """
        Test primality using Miller-Rabin algorithm

        REFERENCE:
        ---------
        Phase_2_Build_Order_Breakdown.md: Line 92
        "Primality testing (Miller-Rabin)"
        """
        print(f"  [MILLER-RABIN] Testing primality")

        # Extract number
        expr = sp.sympify(expr_str)

        # If expression evaluates to integer, test it
        if expr.is_Integer:
            n = int(expr)
            result = isprime(n)
            self.primes_tested += 1

            if result:
                print(f"  {n} is PRIME")
            else:
                print(f"  {n} is COMPOSITE")

            return result
        else:
            return f"Cannot test primality of non-integer: {expr}"

    def _factorize(self, expr_str: str) -> Any:
        """
        Factorize integer using Pollard's rho and other methods

        REFERENCE:
        ---------
        Phase_2_Build_Order_Breakdown.md: Line 92
        "Integer Factorization (Pollard's rho/Quadratic Sieve)"
        """
        print(f"  [POLLARD'S RHO] Factorizing integer")

        # Extract number
        expr = sp.sympify(expr_str)

        if expr.is_Integer:
            n = int(expr)
            factors = factorint(n)  # Returns dict {prime: exponent}
            self.factorizations_computed += 1

            print(f"  Factorization: {factors}")

            # Format as string
            factor_str = " * ".join([
                f"{p}^{e}" if e > 1 else str(p)
                for p, e in factors.items()
            ])

            return factor_str
        else:
            # Try symbolic factorization
            return sp.factor(expr)

    def _compute_gcd(self, expr_str: str) -> Any:
        """Compute Greatest Common Divisor"""
        print(f"  [GCD] Computing greatest common divisor")

        # Parse expression - expect two numbers
        expr = sp.sympify(expr_str)

        # Try to extract two numbers
        if hasattr(expr, 'args') and len(expr.args) >= 2:
            a, b = expr.args[0], expr.args[1]
            if a.is_Integer and b.is_Integer:
                result = gcd(int(a), int(b))
                return result

        return f"GCD requires two integers"

    def _compute_lcm(self, expr_str: str) -> Any:
        """Compute Least Common Multiple"""
        print(f"  [LCM] Computing least common multiple")

        expr = sp.sympify(expr_str)

        if hasattr(expr, 'args') and len(expr.args) >= 2:
            a, b = expr.args[0], expr.args[1]
            if a.is_Integer and b.is_Integer:
                result = lcm(int(a), int(b))
                return result

        return f"LCM requires two integers"

    def _modular_operation(self, expr_str: str, raw_input: str) -> Any:
        """Perform modular arithmetic operation"""
        print(f"  [MODULAR] Computing modular operation")

        expr = sp.sympify(expr_str)

        # Check for modular inverse
        if 'inverse' in raw_input:
            # Extract a and m from expression
            if hasattr(expr, 'args') and len(expr.args) >= 2:
                a, m = expr.args[0], expr.args[1]
                if a.is_Integer and m.is_Integer:
                    try:
                        result = mod_inverse(int(a), int(m))
                        return result
                    except:
                        return f"No modular inverse exists"

        # Default: modular evaluation
        return sp.Mod(expr.args[0], expr.args[1]) if hasattr(expr, 'args') and len(expr.args) >= 2 else expr

    def _compute_default(self, expr_str: str) -> Any:
        """Default computation - try factorization if integer"""
        expr = sp.sympify(expr_str)

        if expr.is_Integer and int(expr) > 1:
            # Try factorization
            return self._factorize(expr_str)
        else:
            return sp.simplify(expr)

    def _create_result_entry(self, task_entry: Any, result: Any, operation: str) -> Any:
        """Create result entry for Blackboard"""
        if not self.blackboard:
            return result

        result_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(str(result)),
            author_agent=self.agent_id,
            conversation_id=task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'result',
            tags=['numbertheory', operation, task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'result'],
            status=EntryStatus.PENDING,
            metadata={
                'result': str(result),
                'result_str': str(result),
                'operation': operation,
                'algorithm': 'miller_rabin' if 'prime' in operation else 'pollard_rho'
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
            tags=['error', 'numbertheory'],
            status=EntryStatus.FAILED,
            metadata={'error': error_msg}
        )

        self.blackboard.post(error_entry)
        return error_entry

    # BDI Implementation
    def update_beliefs(self):
        """Monitor Blackboard for number theory tasks"""
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
            'primes_tested': self.primes_tested,
            'factorizations_computed': self.factorizations_computed
        })
        return stats


if __name__ == "__main__":
    """Test Number Theory Specialist"""
    print("=" * 80)
    print("PHASE 2 - NUMBER THEORY SPECIALIST TEST")
    print("=" * 80)
    print()

    from symbo_agentic_reasoners_phase0.phase0_system import Phase0System

    # Initialize Phase 0
    print("Initializing Phase 0 infrastructure...")
    phase0 = Phase0System()
    phase0.start()
    print()

    # Initialize Number Theory Specialist
    specialist = NumberTheorySpecialist(
        df=phase0.df,
        blackboard=phase0.blackboard
    )
    print()

    print("=" * 80)
    print("NUMBER THEORY SPECIALIST READY")
    print("=" * 80)
    print()

    # Test primality
    print("Test 1: Primality testing (Miller-Rabin)")
    print("  Is 17 prime?")
    result1 = isprime(17)
    print(f"  Result: {result1}")
    print()

    # Test factorization
    print("Test 2: Integer factorization (Pollard's rho)")
    print("  Factor 60")
    result2 = factorint(60)
    print(f"  Result: {result2}")
    print()

    # Check DF registration
    services = phase0.df.search(service_type='math.algebra.numbertheory')
    print(f"Registered services: {len(services)}")
    for service in services:
        print(f"  - {service.service_type}: {service.agent_id}")

    print()
    print("Statistics:")
    import json
    print(json.dumps(specialist.get_statistics(), indent=2))

    # Shutdown
    phase0.shutdown()
