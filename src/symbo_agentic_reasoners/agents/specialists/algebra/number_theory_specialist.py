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

# Native symbolic module - NO SYMPY
from symbo_agentic_reasoners.core.native_symbolic import (
    Symbol, Integer, Rational, Float, parse_expr, sympify, simplify
)
from symbo_agentic_reasoners.core.number_theory_native import (
    is_prime as isprime, prime_factorization as factorint,
    totient, gcd, lcm, mod_inverse
)

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
            instance=self,  # Enable direct invocation by supervisors
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
        try:
            expr = parse_expr(expr_str)
            n = int(expr.value) if hasattr(expr, 'value') else int(str(expr))
        except (ValueError, AttributeError):
            import re
            numbers = re.findall(r'\d+', expr_str)
            if numbers:
                n = int(numbers[0])
            else:
                return f"Cannot test primality of non-integer: {expr_str}"

        result = isprime(n)
        self.primes_tested += 1

        if result:
            print(f"  {n} is PRIME")
        else:
            print(f"  {n} is COMPOSITE")

        return result

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
        try:
            expr = parse_expr(expr_str)
            n = int(expr.value) if hasattr(expr, 'value') else int(str(expr))
        except (ValueError, AttributeError):
            import re
            numbers = re.findall(r'\d+', expr_str)
            if numbers:
                n = int(numbers[0])
            else:
                return f"Cannot factorize non-integer: {expr_str}"

        factors = factorint(n)  # Returns tuple of (prime, exponent) pairs
        self.factorizations_computed += 1

        print(f"  Factorization: {factors}")

        # Format as string - factors is tuple of (prime, exponent) tuples
        factor_str = " * ".join([
            f"{p}^{e}" if e > 1 else str(p)
            for p, e in factors  # Iterate over tuple directly, not .items()
        ])

        return factor_str

    def _compute_gcd(self, expr_str: str) -> Any:
        """Compute Greatest Common Divisor"""
        print(f"  [GCD] Computing greatest common divisor")

        # Try to extract two numbers from string
        import re
        numbers = re.findall(r'\d+', expr_str)
        if len(numbers) >= 2:
            a, b = int(numbers[0]), int(numbers[1])
            result = gcd(a, b)
            return result

        return f"GCD requires two integers"

    def _compute_lcm(self, expr_str: str) -> Any:
        """Compute Least Common Multiple"""
        print(f"  [LCM] Computing least common multiple")

        # Try to extract two numbers from string
        import re
        numbers = re.findall(r'\d+', expr_str)
        if len(numbers) >= 2:
            a, b = int(numbers[0]), int(numbers[1])
            result = lcm(a, b)
            return result

        return f"LCM requires two integers"

    def _modular_operation(self, expr_str: str, raw_input: str) -> Any:
        """Perform modular arithmetic operation"""
        print(f"  [MODULAR] Computing modular operation")

        # Try to extract two numbers from string
        import re
        numbers = re.findall(r'\d+', expr_str)
        if len(numbers) < 2:
            return f"Modular operation requires two integers"

        a, m = int(numbers[0]), int(numbers[1])

        # Check for modular inverse
        if 'inverse' in raw_input:
            try:
                result = mod_inverse(a, m)
                return result
            except ValueError:
                return f"No modular inverse exists"

        # Default: modular evaluation
        return a % m

    def _compute_default(self, expr_str: str) -> Any:
        """Default computation - try factorization if integer"""
        try:
            expr = parse_expr(expr_str)
            n = int(expr.value) if hasattr(expr, 'value') else int(str(expr))
            if n > 1:
                return self._factorize(expr_str)
            return str(n)
        except (ValueError, AttributeError):
            # Just return the input simplified
            try:
                return str(simplify(parse_expr(expr_str)))
            except:
                return expr_str

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

    # ==========================================================================
    # REAL BDI IMPLEMENTATION
    # ==========================================================================
    #
    # The Number Theory Specialist's BDI loop:
    #   1. update_beliefs() - Find number theory tasks on Blackboard
    #   2. deliberate() - Create computation plans
    #   3. execute_step() - Execute computation steps (DELEGATE to SymPy)
    #
    # CRITICAL: All computation is delegated to SymPy's ntheory module:
    #   - Miller-Rabin primality: sympy.ntheory.isprime
    #   - Pollard's rho factoring: sympy.ntheory.factorint
    #   - Extended Euclidean: sympy.gcd, sympy.lcm
    #   - Modular arithmetic: sympy.ntheory.modular.mod_inverse
    # ==========================================================================

    def update_beliefs(self):
        """
        PERCEIVE: Monitor Blackboard for number theory tasks.

        The specialist looks for:
        1. Tasks tagged with 'numbertheory'
        2. Tasks delegated to this agent
        3. Tasks involving primes, factors, gcd, lcm, modular arithmetic
        """
        if not self.blackboard:
            return

        try:
            # Find tasks tagged for number theory
            nt_tasks = self.blackboard.query_entries(
                tags=['numbertheory'],
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
                    if assigned == self.agent_id and task not in nt_tasks:
                        nt_tasks.append(task)

            # Add beliefs about pending tasks
            for task in nt_tasks:
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
            print(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """
        DELIBERATE: Create computation plans for number theory tasks.

        For each pending task:
        1. Determine operation type (primality, factor, gcd, lcm, modular)
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

            # Determine operation type based on keywords
            operation = self._detect_operation(raw_input)

            # Build steps based on operation
            if operation == 'primality':
                steps = ['claim_task', 'parse_number', 'test_primality', 'verify_result', 'post_result']
            elif operation == 'factor':
                steps = ['claim_task', 'parse_number', 'factorize_integer', 'verify_result', 'post_result']
            elif operation == 'gcd':
                steps = ['claim_task', 'parse_numbers', 'compute_gcd', 'verify_result', 'post_result']
            elif operation == 'lcm':
                steps = ['claim_task', 'parse_numbers', 'compute_lcm', 'verify_result', 'post_result']
            elif operation == 'modular':
                steps = ['claim_task', 'parse_modular', 'compute_modular', 'verify_result', 'post_result']
            elif operation == 'totient':
                steps = ['claim_task', 'parse_number', 'compute_totient', 'verify_result', 'post_result']
            else:
                # Default to factorization
                steps = ['claim_task', 'parse_number', 'factorize_integer', 'verify_result', 'post_result']

            intention = Intention(
                plan_id=f'nt_{operation}_{task_id}',
                steps=steps,
                target_desire='solve_number_theory',
                metadata={
                    'task_id': task_id,
                    'task_entry': task,
                    'operation': operation,
                    'raw_input': raw_input,
                    'sympy_expr': metadata.get('sympy_expr')
                }
            )

            new_intentions.append(intention)
            print(f"[{self.agent_id}] Created plan: {operation} for {task_id}")

        return new_intentions

    def _detect_operation(self, raw_input: str) -> str:
        """Detect the number theory operation from input"""
        if 'prime' in raw_input and ('is' in raw_input or 'test' in raw_input or 'check' in raw_input):
            return 'primality'
        elif 'factor' in raw_input:
            return 'factor'
        elif 'gcd' in raw_input or 'greatest common' in raw_input:
            return 'gcd'
        elif 'lcm' in raw_input or 'least common' in raw_input:
            return 'lcm'
        elif 'mod' in raw_input or 'modulo' in raw_input or 'modular' in raw_input:
            return 'modular'
        elif 'totient' in raw_input or 'euler' in raw_input:
            return 'totient'
        else:
            return 'factor'  # Default

    def execute_step(self, intention: Intention):
        """
        EXECUTE: Execute one step of the computation plan.

        Steps vary by operation but all DELEGATE to SymPy ntheory:
        - parse_number: Extract integer from expression
        - test_primality: Call sympy.ntheory.isprime (Miller-Rabin)
        - factorize_integer: Call sympy.ntheory.factorint (Pollard's rho)
        - compute_gcd: Call sympy.gcd (Extended Euclidean)
        - compute_lcm: Call sympy.lcm
        - compute_totient: Call sympy.ntheory.totient

        CRITICAL: This agent NEVER implements number theory. It delegates to SymPy.
        """
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')

        print(f"[{self.agent_id}] Executing: {action} for {task_id}")

        try:
            if action == 'claim_task':
                self._execute_claim_task(intention, task, task_id)

            elif action == 'parse_number':
                self._execute_parse_number(intention)

            elif action == 'parse_numbers':
                self._execute_parse_numbers(intention)

            elif action == 'parse_modular':
                self._execute_parse_modular(intention)

            elif action == 'test_primality':
                self._execute_primality(intention)

            elif action == 'factorize_integer':
                self._execute_factorize(intention)

            elif action == 'compute_gcd':
                self._execute_gcd(intention)

            elif action == 'compute_lcm':
                self._execute_lcm(intention)

            elif action == 'compute_modular':
                self._execute_modular(intention)

            elif action == 'compute_totient':
                self._execute_totient(intention)

            elif action == 'verify_result':
                self._execute_verify(intention)

            elif action == 'post_result':
                self._execute_post_result(intention, task)

            else:
                print(f"[{self.agent_id}] Unknown action: {action}")
                intention.advance()

        except Exception as e:
            print(f"[{self.agent_id}] Step {action} failed: {e}")
            self._handle_computation_failure(intention, task, str(e))

    def _execute_claim_task(self, intention: Intention, task: Any, task_id: str):
        """Claim task on Blackboard"""
        if self.blackboard:
            self.blackboard.update_entry_status(task_id, EntryStatus.IN_PROGRESS)

        self.add_belief(f'claimed_task_{task_id}', True)
        self.remove_belief(f'pending_task_{task_id}')

        print(f"[{self.agent_id}] Claimed task {task_id}")
        intention.advance()

    def _execute_parse_number(self, intention: Intention):
        """Parse single integer from expression"""
        raw_input = intention.metadata.get('raw_input', '')
        sympy_expr_str = intention.metadata.get('sympy_expr')

        expr_str = sympy_expr_str if sympy_expr_str else raw_input

        # Extract number - remove non-numeric parts
        import re
        numbers = re.findall(r'\d+', expr_str)
        if numbers:
            n = int(numbers[0])
        else:
            # Try native parse
            try:
                expr = parse_expr(expr_str)
                n = int(expr.value) if hasattr(expr, 'value') else int(str(expr))
            except (ValueError, AttributeError):
                raise ValueError(f"Could not extract integer from: {expr_str}")

        intention.metadata['parsed_number'] = n
        print(f"[{self.agent_id}] Parsed number: {n}")
        intention.advance()

    def _execute_parse_numbers(self, intention: Intention):
        """Parse two integers for gcd/lcm"""
        raw_input = intention.metadata.get('raw_input', '')
        sympy_expr_str = intention.metadata.get('sympy_expr')

        expr_str = sympy_expr_str if sympy_expr_str else raw_input

        import re
        numbers = re.findall(r'\d+', expr_str)
        if len(numbers) >= 2:
            a, b = int(numbers[0]), int(numbers[1])
        else:
            raise ValueError(f"GCD/LCM requires two integers: {expr_str}")

        intention.metadata['parsed_a'] = a
        intention.metadata['parsed_b'] = b
        print(f"[{self.agent_id}] Parsed numbers: {a}, {b}")
        intention.advance()

    def _execute_parse_modular(self, intention: Intention):
        """Parse modular arithmetic operands"""
        raw_input = intention.metadata.get('raw_input', '')

        import re
        numbers = re.findall(r'\d+', raw_input)
        if len(numbers) >= 2:
            a, m = int(numbers[0]), int(numbers[1])
        else:
            raise ValueError(f"Modular arithmetic requires two integers: {raw_input}")

        intention.metadata['parsed_a'] = a
        intention.metadata['parsed_m'] = m
        intention.metadata['is_inverse'] = 'inverse' in raw_input.lower()
        print(f"[{self.agent_id}] Parsed modular: {a} mod {m}")
        intention.advance()

    def _execute_primality(self, intention: Intention):
        """DELEGATE primality testing to SymPy (Miller-Rabin)"""
        n = intention.metadata.get('parsed_number')

        # DELEGATE to SymPy's Miller-Rabin implementation
        result = isprime(n)

        self.primes_tested += 1
        intention.metadata['result'] = result
        intention.metadata['result_str'] = f"{n} is {'PRIME' if result else 'COMPOSITE'}"
        self.add_belief('computed_result', result)

        print(f"[{self.agent_id}] Primality: {n} is {'PRIME' if result else 'COMPOSITE'}")
        intention.advance()

    def _execute_factorize(self, intention: Intention):
        """DELEGATE factorization to SymPy (Pollard's rho)"""
        n = intention.metadata.get('parsed_number')

        # DELEGATE to SymPy's factorization (uses Pollard's rho, etc.)
        factors = factorint(n)

        self.factorizations_computed += 1

        # Format as string
        factor_str = " * ".join([
            f"{p}^{e}" if e > 1 else str(p)
            for p, e in factors.items()
        ])

        intention.metadata['result'] = factors
        intention.metadata['result_str'] = factor_str
        self.add_belief('computed_result', factors)

        print(f"[{self.agent_id}] Factorization: {n} = {factor_str}")
        intention.advance()

    def _execute_gcd(self, intention: Intention):
        """DELEGATE GCD to SymPy (Extended Euclidean)"""
        a = intention.metadata.get('parsed_a')
        b = intention.metadata.get('parsed_b')

        # DELEGATE to SymPy
        result = gcd(a, b)

        intention.metadata['result'] = result
        intention.metadata['result_str'] = str(result)
        self.add_belief('computed_result', result)

        print(f"[{self.agent_id}] GCD({a}, {b}) = {result}")
        intention.advance()

    def _execute_lcm(self, intention: Intention):
        """DELEGATE LCM to SymPy"""
        a = intention.metadata.get('parsed_a')
        b = intention.metadata.get('parsed_b')

        # DELEGATE to SymPy
        result = lcm(a, b)

        intention.metadata['result'] = result
        intention.metadata['result_str'] = str(result)
        self.add_belief('computed_result', result)

        print(f"[{self.agent_id}] LCM({a}, {b}) = {result}")
        intention.advance()

    def _execute_modular(self, intention: Intention):
        """DELEGATE modular arithmetic to SymPy"""
        a = intention.metadata.get('parsed_a')
        m = intention.metadata.get('parsed_m')
        is_inverse = intention.metadata.get('is_inverse', False)

        if is_inverse:
            # DELEGATE to SymPy's modular inverse
            try:
                result = mod_inverse(a, m)
                result_str = f"{a}^(-1) mod {m} = {result}"
            except ValueError:
                result = None
                result_str = f"No modular inverse exists for {a} mod {m}"
        else:
            # Simple modular reduction
            result = a % m
            result_str = f"{a} mod {m} = {result}"

        intention.metadata['result'] = result
        intention.metadata['result_str'] = result_str
        self.add_belief('computed_result', result)

        print(f"[{self.agent_id}] {result_str}")
        intention.advance()

    def _execute_totient(self, intention: Intention):
        """DELEGATE Euler's totient to SymPy"""
        n = intention.metadata.get('parsed_number')

        # DELEGATE to SymPy
        result = totient(n)

        intention.metadata['result'] = result
        intention.metadata['result_str'] = f"φ({n}) = {result}"
        self.add_belief('computed_result', result)

        print(f"[{self.agent_id}] φ({n}) = {result}")
        intention.advance()

    def _execute_verify(self, intention: Intention):
        """Verify computation result"""
        result = intention.metadata.get('result')

        # Basic verification - result exists
        verified = result is not None

        intention.metadata['verified'] = verified
        self.add_belief('result_verified', verified)

        print(f"[{self.agent_id}] Verification: {verified}")
        intention.advance()

    def _execute_post_result(self, intention: Intention, task: Any):
        """Post result to Blackboard"""
        result = intention.metadata.get('result')
        result_str = intention.metadata.get('result_str', str(result))
        operation = intention.metadata.get('operation', 'compute')
        task_id = intention.metadata.get('task_id')

        if self.blackboard:
            delegation_id = task.metadata.get('delegation_id', task_id) if hasattr(task, 'metadata') else task_id

            result_entry = create_entry(
                entry_type=EntryType.PARTIAL_RESULT,
                content=create_variable(result_str),
                author_agent=self.agent_id,
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                tags=['numbertheory', 'result', operation, delegation_id],
                status=EntryStatus.COMPLETED,
                metadata={
                    'result': str(result),
                    'result_str': result_str,
                    'operation': operation,
                    'task_id': task_id,
                    'verified': intention.metadata.get('verified', False),
                    'algorithm': 'miller_rabin' if operation == 'primality' else 'pollard_rho'
                }
            )
            self.blackboard.post(result_entry)
            self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)

        # Update beliefs
        self.add_belief(f'completed_task_{task_id}', True)
        self.remove_belief(f'claimed_task_{task_id}')

        self.tasks_succeeded += 1
        print(f"[{self.agent_id}] Posted result for {task_id}: {result_str}")
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
                tags=['error', 'numbertheory', task_id],
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

    from symbo_agentic_reasoners.core.system import Phase0System

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
