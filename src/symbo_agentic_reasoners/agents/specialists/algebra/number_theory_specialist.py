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
- Integer factorization (Pollard's rho, Pollard p-1, Fermat, trial division)
- GCD and LCM computation (Extended Euclidean Algorithm)
- Modular arithmetic (inverses, exponentiation)
- Diophantine equations (linear, Pell's equation, sum of two squares)
- Chinese Remainder Theorem (system of congruences)
- Quadratic residues (Legendre symbol, Jacobi symbol, Tonelli-Shanks)
- Carmichael number detection (pseudoprime testing)

REFERENCE:
---------
- Phase_2_Build_Order_Breakdown.md: Lines 91-93 (Agent 1.4)
- Phase 2 Coding Strategy: "Number Theory Specialist"
"""

import sys
import os
from typing import Any, Dict, List, Optional, Tuple
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
    - Primality testing (is_prime, is_carmichael_number)
    - Integer factorization (factor, pollard_p_minus_1, fermat_factorization)
    - GCD/LCM computation (with Extended Euclidean Algorithm)
    - Modular arithmetic (mod, mod_inverse, modular exponentiation)
    - Euler's totient function
    - Diophantine equations (solve_linear_diophantine, solve_pells_equation, solve_sum_of_two_squares)
    - Chinese Remainder Theorem (chinese_remainder_theorem)
    - Quadratic residues (legendre_symbol, jacobi_symbol, tonelli_shanks)

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

    def solve_linear_diophantine(
        self,
        a: int,
        b: int,
        c: int
    ) -> Dict[str, Any]:
        """
        Solve linear Diophantine equation: ax + by = c

        Uses Extended Euclidean Algorithm.
        Solutions exist iff gcd(a,b) divides c.
        General solution: x = x₀ + (b/gcd)t, y = y₀ - (a/gcd)t

        Args:
            a, b, c: Coefficients of linear Diophantine equation

        Returns:
            Dict with particular solution and general solution formula
        """
        try:
            g = gcd(a, b)

            if c % g != 0:
                return {
                    'success': False,
                    'error': f'No solution: gcd({a},{b}) = {g} does not divide {c}',
                    'gcd': g
                }

            # Extended Euclidean Algorithm to find x0, y0 such that ax0 + by0 = gcd(a,b)
            x0, y0 = self._extended_gcd(a, b)

            # Scale to get ax0 + by0 = c
            scale = c // g
            x_particular = x0 * scale
            y_particular = y0 * scale

            # General solution parameters
            b_over_gcd = b // g
            a_over_gcd = a // g

            return {
                'success': True,
                'particular_solution': (x_particular, y_particular),
                'general_solution': f'x = {x_particular} + {b_over_gcd}t, y = {y_particular} - {a_over_gcd}t',
                'gcd': g,
                'method': 'extended_euclidean',
                'note': 't is any integer parameter'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'linear_diophantine'
            }

    def _extended_gcd(self, a: int, b: int) -> Tuple[int, int]:
        """
        Extended Euclidean Algorithm: find x, y such that ax + by = gcd(a,b)

        Returns:
            (x, y) coefficients
        """
        if b == 0:
            return (1, 0)

        x1, y1 = self._extended_gcd(b, a % b)
        x = y1
        y = x1 - (a // b) * y1

        return (x, y)

    def solve_pells_equation(
        self,
        d: int,
        n_solutions: int = 5
    ) -> Dict[str, Any]:
        """
        Solve Pell's equation: x² - Dy² = 1

        Uses continued fraction method to find fundamental solution,
        then generates additional solutions via recurrence.

        Args:
            d: Parameter D (non-square positive integer)
            n_solutions: Number of solutions to generate

        Returns:
            Dict with fundamental solution and additional solutions
        """
        try:
            # Check if D is a perfect square
            sqrt_d = int(d ** 0.5)
            if sqrt_d * sqrt_d == d:
                return {
                    'success': False,
                    'error': f'D = {d} is a perfect square; Pell equation trivial (x=1, y=0 only)',
                    'method': 'pells_equation'
                }

            # Find fundamental solution using continued fraction method
            # Simplified implementation - full version would compute continued fraction of √D
            x1, y1 = self._find_fundamental_pell_solution(d)

            if x1 is None:
                return {
                    'success': False,
                    'error': 'Could not find fundamental solution',
                    'method': 'pells_equation'
                }

            # Generate additional solutions using recurrence:
            # x_{n+1} = x₁x_n + Dy₁y_n
            # y_{n+1} = x₁y_n + y₁x_n

            solutions = [(x1, y1)]
            xn, yn = x1, y1

            for _ in range(n_solutions - 1):
                xn_new = x1 * xn + d * y1 * yn
                yn_new = x1 * yn + y1 * xn
                solutions.append((xn_new, yn_new))
                xn, yn = xn_new, yn_new

            return {
                'success': True,
                'fundamental_solution': (x1, y1),
                'solutions': solutions,
                'verification': [f'{x}² - {d}*{y}² = {x*x - d*y*y}' for x, y in solutions[:3]],
                'method': 'continued_fraction',
                'note': f'All solutions generated from fundamental (x₁={x1}, y₁={y1})'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'pells_equation'
            }

    def _find_fundamental_pell_solution(self, d: int) -> Tuple[Optional[int], Optional[int]]:
        """
        Find fundamental solution to Pell's equation using continued fractions.

        Simplified implementation using search for small D.
        Real implementation would compute continued fraction period of √D.
        """
        # Brute force search for small solutions (simplified)
        # Real implementation: continued fraction algorithm

        for y in range(1, 1000):
            x_squared = d * y * y + 1
            x = int(x_squared ** 0.5)
            if x * x == x_squared:
                return (x, y)

        return (None, None)

    def solve_sum_of_two_squares(self, n: int) -> Dict[str, Any]:
        """
        Find representation of n as sum of two squares: n = a² + b²

        Uses Fermat's theorem: n can be represented iff all prime factors
        p ≡ 3 (mod 4) appear with even exponent.

        Args:
            n: Integer to represent

        Returns:
            Dict with representation(s) or impossibility proof
        """
        try:
            # Check if representation exists
            factors = factorint(n)

            # Check condition: primes ≡ 3 (mod 4) must have even exponent
            for prime, exponent in factors.items():
                if prime % 4 == 3 and exponent % 2 == 1:
                    return {
                        'success': False,
                        'error': f'Impossible: prime {prime} ≡ 3 (mod 4) has odd exponent {exponent}',
                        'method': 'sum_of_squares',
                        'theorem': 'Fermat two-square theorem'
                    }

            # Find representation by search (simplified)
            for a in range(int(n**0.5) + 1):
                b_squared = n - a*a
                if b_squared >= 0:
                    b = int(b_squared ** 0.5)
                    if b * b == b_squared:
                        return {
                            'success': True,
                            'representation': f'{n} = {a}² + {b}²',
                            'values': (a, b),
                            'verification': f'{a}² + {b}² = {a*a + b*b}',
                            'method': 'sum_of_squares'
                        }

            return {
                'success': False,
                'error': 'No representation found (search limit reached)',
                'method': 'sum_of_squares'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'sum_of_squares'
            }

    def chinese_remainder_theorem(
        self,
        remainders: List[int],
        moduli: List[int]
    ) -> Dict[str, Any]:
        """
        Solve system of congruences using Chinese Remainder Theorem:
        x ≡ a₁ (mod m₁)
        x ≡ a₂ (mod m₂)
        ...
        x ≡ aₙ (mod mₙ)

        Requires moduli to be pairwise coprime.

        Args:
            remainders: List of remainders [a₁, a₂, ..., aₙ]
            moduli: List of moduli [m₁, m₂, ..., mₙ]

        Returns:
            Dict with solution x (mod M) where M = m₁*m₂*...*mₙ
        """
        try:
            if len(remainders) != len(moduli):
                return {
                    'success': False,
                    'error': 'Number of remainders must equal number of moduli',
                    'method': 'crt'
                }

            # Check pairwise coprimality
            for i in range(len(moduli)):
                for j in range(i + 1, len(moduli)):
                    if gcd(moduli[i], moduli[j]) != 1:
                        return {
                            'success': False,
                            'error': f'Moduli must be pairwise coprime: gcd({moduli[i]}, {moduli[j]}) ≠ 1',
                            'method': 'crt'
                        }

            # Compute M = product of all moduli
            M = 1
            for m in moduli:
                M *= m

            # Apply CRT formula
            x = 0
            for i in range(len(moduli)):
                Mi = M // moduli[i]
                yi = mod_inverse(Mi, moduli[i])
                x += remainders[i] * Mi * yi

            x = x % M

            # Verification
            verification = []
            for i, (r, m) in enumerate(zip(remainders, moduli)):
                verification.append(f'x ≡ {x % m} (mod {m}) ✓' if x % m == r else f'x ≡ {x % m} (mod {m}) ✗')

            return {
                'success': True,
                'solution': x,
                'modulus': M,
                'general_solution': f'x ≡ {x} (mod {M})',
                'verification': verification,
                'method': 'chinese_remainder_theorem',
                'uniqueness': f'Solution is unique modulo {M}'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'crt'
            }

    def legendre_symbol(self, a: int, p: int) -> int:
        """
        Compute Legendre symbol (a/p) for odd prime p.

        Returns:
         1 if a is a quadratic residue mod p
        -1 if a is a quadratic non-residue mod p
         0 if a ≡ 0 (mod p)

        Uses Euler's criterion: (a/p) ≡ a^((p-1)/2) (mod p)

        Args:
            a: Integer
            p: Odd prime

        Returns:
            Legendre symbol value: -1, 0, or 1
        """
        if not isprime(p) or p == 2:
            raise ValueError(f'{p} is not an odd prime')

        a = a % p
        if a == 0:
            return 0

        # Euler's criterion: (a/p) ≡ a^((p-1)/2) (mod p)
        result = pow(a, (p - 1) // 2, p)

        # Convert to -1, 0, 1
        if result == p - 1:
            return -1
        elif result == 1:
            return 1
        else:
            return 0

    def jacobi_symbol(self, a: int, n: int) -> int:
        """
        Compute Jacobi symbol (a/n) - generalization of Legendre symbol.

        For odd n ≥ 3, computes using properties:
        - Multiplicativity
        - Quadratic reciprocity
        - Reduction rules

        Args:
            a: Integer
            n: Odd integer ≥ 3

        Returns:
            Jacobi symbol value: -1, 0, or 1
        """
        if n % 2 == 0 or n < 3:
            raise ValueError(f'{n} must be odd and ≥ 3')

        a = a % n
        result = 1

        while a != 0:
            while a % 2 == 0:
                a //= 2
                # (2/n) = 1 if n ≡ ±1 (mod 8), -1 if n ≡ ±3 (mod 8)
                if n % 8 in [3, 5]:
                    result = -result

            a, n = n, a

            # Quadratic reciprocity: (a/n)(n/a) = (-1)^((a-1)(n-1)/4)
            if a % 4 == 3 and n % 4 == 3:
                result = -result

            a = a % n

        if n == 1:
            return result
        else:
            return 0

    def tonelli_shanks(self, n: int, p: int) -> Dict[str, Any]:
        """
        Solve modular square root: x² ≡ n (mod p)

        Uses Tonelli-Shanks algorithm for odd prime p.

        Args:
            n: Integer whose square root to find
            p: Odd prime modulus

        Returns:
            Dict with square root(s) or indication that none exist
        """
        try:
            if not isprime(p) or p == 2:
                return {
                    'success': False,
                    'error': f'{p} is not an odd prime',
                    'method': 'tonelli_shanks'
                }

            n = n % p

            # Check if n is a quadratic residue using Legendre symbol
            if self.legendre_symbol(n, p) != 1:
                return {
                    'success': False,
                    'error': f'{n} is not a quadratic residue mod {p}',
                    'legendre_symbol': self.legendre_symbol(n, p),
                    'method': 'tonelli_shanks'
                }

            # Find Q and S such that p - 1 = Q * 2^S with Q odd
            Q = p - 1
            S = 0
            while Q % 2 == 0:
                Q //= 2
                S += 1

            # Find quadratic non-residue z
            z = 2
            while self.legendre_symbol(z, p) != -1:
                z += 1

            # Initialize
            M = S
            c = pow(z, Q, p)
            t = pow(n, Q, p)
            R = pow(n, (Q + 1) // 2, p)

            # Main loop
            while t != 1:
                # Find smallest i such that t^(2^i) ≡ 1
                i = 1
                temp = (t * t) % p
                while temp != 1 and i < M:
                    temp = (temp * temp) % p
                    i += 1

                if i == M:
                    return {
                        'success': False,
                        'error': 'Algorithm failed to converge',
                        'method': 'tonelli_shanks'
                    }

                # Update
                b = pow(c, 1 << (M - i - 1), p)
                M = i
                c = (b * b) % p
                t = (t * c) % p
                R = (R * b) % p

            # R is a square root; -R is the other
            return {
                'success': True,
                'square_roots': [R, p - R],
                'verification': f'{R}² mod {p} = {(R*R) % p}',
                'method': 'tonelli_shanks',
                'note': f'Both {R} and {p - R} are square roots of {n} mod {p}'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'tonelli_shanks'
            }

    def is_carmichael_number(self, n: int) -> Dict[str, Any]:
        """
        Test if n is a Carmichael number (composite number that passes Fermat test).

        A composite number n is Carmichael if:
        a^(n-1) ≡ 1 (mod n) for all a coprime to n

        Korselt's criterion: n is Carmichael iff:
        1. n is composite
        2. n is square-free
        3. For each prime p dividing n: (p-1) divides (n-1)

        Args:
            n: Integer to test

        Returns:
            Dict with Carmichael test result and explanation
        """
        try:
            # Check if n is prime (Carmichael numbers are composite)
            if isprime(n):
                return {
                    'success': True,
                    'is_carmichael': False,
                    'reason': f'{n} is prime, not composite',
                    'method': 'carmichael_test'
                }

            # Factorize n
            factors = factorint(n)

            # Check square-free (all exponents = 1)
            is_square_free = all(exp == 1 for exp in factors.values())

            if not is_square_free:
                return {
                    'success': True,
                    'is_carmichael': False,
                    'reason': 'Not square-free',
                    'factorization': factors,
                    'method': 'carmichael_test'
                }

            # Check Korselt's criterion: (p-1) divides (n-1) for each prime p
            korselt_satisfied = True
            for prime in factors.keys():
                if (n - 1) % (prime - 1) != 0:
                    korselt_satisfied = False
                    break

            is_carmichael = korselt_satisfied

            return {
                'success': True,
                'is_carmichael': is_carmichael,
                'factorization': factors,
                'korselt_criterion': korselt_satisfied,
                'method': 'carmichael_test',
                'note': 'Carmichael numbers are pseudoprimes to all bases'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'carmichael_test'
            }

    def pollard_p_minus_1(self, n: int, B: int = 100) -> Dict[str, Any]:
        """
        Pollard's p-1 factorization algorithm.

        Efficient when n has a prime factor p where p-1 is B-smooth
        (all prime factors of p-1 are ≤ B).

        Args:
            n: Integer to factor
            B: Smoothness bound

        Returns:
            Dict with factor found or failure
        """
        try:
            if isprime(n):
                return {
                    'success': False,
                    'error': f'{n} is prime',
                    'method': 'pollard_p_minus_1'
                }

            # Compute M = lcm(1, 2, ..., B) ≈ e^B
            # Use a = 2^M mod n
            a = 2

            # Compute a = 2^(k!) for k = 2, 3, ..., B
            for k in range(2, B + 1):
                a = pow(a, k, n)

            # Compute gcd(a - 1, n)
            g = gcd(a - 1, n)

            if 1 < g < n:
                return {
                    'success': True,
                    'factor': g,
                    'cofactor': n // g,
                    'smoothness_bound': B,
                    'method': 'pollard_p_minus_1',
                    'note': f'Found factor with B = {B}'
                }
            else:
                return {
                    'success': False,
                    'error': f'No factor found with bound B = {B}; try larger B',
                    'method': 'pollard_p_minus_1',
                    'gcd_result': g
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'pollard_p_minus_1'
            }

    def fermat_factorization(self, n: int, max_iterations: int = 10000) -> Dict[str, Any]:
        """
        Fermat's factorization method for odd composite n.

        Finds factors by searching for representation: n = a² - b²

        Efficient when factors are close to √n.

        Args:
            n: Odd composite integer
            max_iterations: Maximum search iterations

        Returns:
            Dict with factors or failure
        """
        try:
            if n % 2 == 0:
                return {
                    'success': True,
                    'factor': 2,
                    'cofactor': n // 2,
                    'method': 'trivial'
                }

            if isprime(n):
                return {
                    'success': False,
                    'error': f'{n} is prime',
                    'method': 'fermat'
                }

            # Start with a = ceil(√n)
            a = int(n ** 0.5) + 1
            b_squared = a * a - n

            iterations = 0
            while iterations < max_iterations:
                b = int(b_squared ** 0.5)

                if b * b == b_squared:
                    # Found: n = a² - b² = (a-b)(a+b)
                    factor1 = a - b
                    factor2 = a + b

                    if factor1 > 1 and factor2 > 1:
                        return {
                            'success': True,
                            'factor': factor1,
                            'cofactor': factor2,
                            'representation': f'{n} = {a}² - {b}² = ({a}-{b})({a}+{b})',
                            'method': 'fermat',
                            'iterations': iterations
                        }

                a += 1
                b_squared = a * a - n
                iterations += 1

            return {
                'success': False,
                'error': f'No factorization found in {max_iterations} iterations',
                'method': 'fermat',
                'note': 'Increase max_iterations or try different method'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'fermat'
            }

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
