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
EXPLICIT FORMULA SPECIALIST (Tier 3)
=====================================

Computes explicit formulas connecting primes and zeta zeros.

CAPABILITIES:
------------
- von Mangoldt function Λ(n)
- Explicit formula for ψ(x) = Σ Λ(n) (n ≤ x)
- Prime counting with oscillatory terms from zeta zeros
- Riemann-von Mangoldt explicit formula
- Weil explicit formula for L-functions

ALGORITHMS:
-----------
1. von Mangoldt function:
   Λ(n) = log p if n = p^k, 0 otherwise

2. Chebyshev function:
   ψ(x) = Σ_{n≤x} Λ(n) = Σ_{p^k≤x} log p

3. Explicit formula (Riemann-von Mangoldt):
   ψ(x) = x - Σ_{ρ} (x^ρ / ρ) - log(2π) - (1/2)log(1 - x^(-2))
   where ρ ranges over nontrivial zeros of ζ(s)

4. Prime counting with zeros:
   π(x) ≈ Li(x) - Σ_{ρ} Li(x^ρ)

NO SYMPY - Pure native implementation.

REFERENCE:
---------
Mathematical Capability Expansion - Analytic Number Theory
Created: December 2025
"""

import logging
import numpy as np
from typing import Any, Dict, List, Optional, Tuple

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.omdoc_schema import create_variable

logger = logging.getLogger(__name__)


class ExplicitFormulaSpecialist(BDIAgent):
    """
    Explicit Formula Specialist - Prime-Zero Connections

    DIRECTIVE:
    ---------
    Compute explicit formulas relating primes to zeta function zeros.

    OPERATIONS:
    ----------
    - von_mangoldt: Compute Λ(n) for integer n
    - chebyshev_psi: Compute ψ(x) = Σ Λ(n) for n ≤ x
    - explicit_formula_psi: ψ(x) using zeta zeros
    - prime_counting_explicit: π(x) using zeros
    - zero_contribution: Oscillatory term from zeros

    VON MANGOLDT FUNCTION:
    ---------------------
    Λ(n) = log p if n = p^k for prime p
         = 0 otherwise

    CHEBYSHEV FUNCTION:
    ------------------
    ψ(x) = Σ_{n≤x} Λ(n)
         = Σ_{p^k≤x} log p

    EXPLICIT FORMULA:
    ----------------
    ψ(x) = x - Σ_{ρ} (x^ρ / ρ) - log(2π) - (1/2)log(1 - x^{-2})

    where ρ = 1/2 + iγ ranges over nontrivial zeros.

    REFERENCE:
    ---------
    Riemann-von Mangoldt explicit formula
    Weil explicit formula
    Target: Accurate prime-zero relationships
    """

    def __init__(
        self,
        agent_id: str = 'explicit_formula_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Explicit Formula Specialist.

        Args:
            agent_id: Unique agent identifier
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
        self.formulas_evaluated = 0
        self.zero_contributions_computed = 0
        self.von_mangoldt_calls = 0
        self.chebyshev_calls = 0

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        logger.info(f"[{self.agent_id}] Explicit Formula Specialist initialized")
        logger.info(f"  Method: Riemann-von Mangoldt explicit formula")

    def _register_services(self):
        """
        Register services with Directory Facilitator.

        Registers:
            - math.algebra.numbertheory.analytic.explicit_formula
        """
        registration = create_service_registration(
            service_type='math.algebra.numbertheory.analytic.explicit_formula',
            agent_id=self.agent_id,
            algorithm='riemann_von_mangoldt',
            cost='high',
            instance=self,
            type='specialist',
            tier='3',
            capabilities='explicit_formula_prime_counting_zeros'
        )
        self.df.register(registration)
        logger.info(f"  [DF] Registered: math.algebra.numbertheory.analytic.explicit_formula")

    def process(self, task_entry: Any) -> Any:
        """
        Process explicit formula task.

        Args:
            task_entry: Task entry from blackboard

        Returns:
            Result entry with computation or error
        """
        logger.info(f"\n[{self.agent_id}] Processing explicit formula task")

        self.tasks_executed += 1

        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            raw_input = metadata.get('raw_input', '')
            operation = metadata.get('operation', 'chebyshev_psi')
            x_value = metadata.get('x', 100)
            n_value = metadata.get('n', 10)
            max_zeros = metadata.get('max_zeros', 10)

            logger.info(f"  Operation: {operation}")
            logger.info(f"  Parameters: x={x_value}, n={n_value}, max_zeros={max_zeros}")

            # Route to appropriate method
            if operation == 'von_mangoldt':
                result = self.von_mangoldt(n_value)
            elif operation == 'chebyshev_psi':
                result = self.chebyshev_psi(x_value)
            elif operation == 'explicit_formula':
                result = self.explicit_formula_psi(x_value, max_zeros)
            else:
                result = {'error': f'Unknown operation: {operation}'}

            if 'error' not in result:
                self.tasks_succeeded += 1
                self.formulas_evaluated += 1
                logger.info(f"  [OK] Result: {result}")
            else:
                self.tasks_failed += 1
                logger.warning(f"  [FAIL] {result.get('error')}")

            # Create result entry
            if self.blackboard:
                result_str = str(result)
                return create_entry(
                    EntryType.PARTIAL_RESULT,
                    create_variable(result_str),
                    self.agent_id,
                    task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'result',
                    ['number_theory', 'explicit_formula'],
                    EntryStatus.COMPLETED if 'error' not in result else EntryStatus.FAILED,
                    {'result': result}
                )
            else:
                return result

        except Exception as e:
            self.tasks_failed += 1
            logger.error(f"  [ERROR] {type(e).__name__}: {e}")

            if self.blackboard:
                return create_entry(
                    EntryType.PARTIAL_RESULT,
                    create_variable(f"Error: {str(e)}"),
                    self.agent_id,
                    task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'error',
                    ['number_theory', 'explicit_formula', 'error'],
                    EntryStatus.FAILED,
                    {'error': str(e)}
                )
            else:
                return {'error': str(e)}

    def is_prime_power(self, n: int) -> Optional[Tuple[int, int]]:
        """
        Check if n is a prime power p^k.

        Args:
            n: Integer to test

        Returns:
            (p, k) if n = p^k, None otherwise
        """
        if n < 2:
            return None

        # Test small primes
        for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
            if n == p:
                return (p, 1)

            # Check if n is a power of p
            power = p
            k = 1
            while power < n:
                power *= p
                k += 1
                if power == n:
                    return (p, k)

        # For larger n, check if n is prime
        if self._is_prime_simple(n):
            return (n, 1)

        return None

    def _is_prime_simple(self, n: int) -> bool:
        """
        Simple primality test.

        Args:
            n: Integer to test

        Returns:
            True if likely prime
        """
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False

        # Trial division up to sqrt(n)
        limit = int(np.sqrt(n)) + 1
        for i in range(3, min(limit, 1000), 2):
            if n % i == 0:
                return False

        return True

    def von_mangoldt(self, n: int) -> Dict[str, Any]:
        """
        Compute von Mangoldt function Λ(n).

        Λ(n) = log p if n = p^k for prime p
             = 0 otherwise

        Args:
            n: Positive integer

        Returns:
            Result dict with Λ(n)
        """
        self.von_mangoldt_calls += 1

        if n < 1:
            return {'n': n, 'lambda_n': 0, 'reason': 'n must be positive'}

        prime_power = self.is_prime_power(n)

        if prime_power:
            p, k = prime_power
            lambda_n = np.log(p)
            return {
                'n': n,
                'lambda_n': float(lambda_n),
                'p': p,
                'k': k,
                'formula': f'Lambda({n}) = log({p}) [since {n} = {p}^{k}]'
            }
        else:
            return {
                'n': n,
                'lambda_n': 0,
                'formula': f'Lambda({n}) = 0 [not a prime power]'
            }

    def chebyshev_psi(self, x: float) -> Dict[str, Any]:
        """
        Compute Chebyshev psi function ψ(x) = Σ_{n≤x} Λ(n).

        Args:
            x: Upper bound

        Returns:
            Result dict with ψ(x)
        """
        self.chebyshev_calls += 1

        if x < 1:
            return {'x': x, 'psi_x': 0}

        psi = 0
        terms = []

        # Sum von Mangoldt function up to x
        for n in range(1, int(x) + 1):
            result = self.von_mangoldt(n)
            lambda_n = result['lambda_n']
            if lambda_n > 0:
                psi += lambda_n
                terms.append((n, lambda_n))

        return {
            'x': x,
            'psi_x': float(psi),
            'num_terms': len(terms),
            'formula': f'psi({x}) = sum(Lambda(n) for n<={x})',
            'asymptotic': f'psi(x) ~ x as x -> inf',
            'ratio_to_x': float(psi / x) if x > 0 else 0
        }

    def explicit_formula_psi(
        self,
        x: float,
        max_zeros: int = 10,
        zeros: Optional[List[complex]] = None
    ) -> Dict[str, Any]:
        """
        Compute ψ(x) using explicit formula.

        ψ(x) = x - Σ_{ρ} (x^ρ / ρ) - log(2π) - (1/2)log(1 - x^(-2))

        Args:
            x: Argument
            max_zeros: Number of zeros to include
            zeros: List of nontrivial zeros (imaginary parts)

        Returns:
            Result dict with ψ(x) via explicit formula
        """
        self.formulas_evaluated += 1

        if x < 2:
            return {'x': x, 'error': 'x must be ≥ 2 for explicit formula'}

        # Main term
        main_term = x

        # Log correction terms
        log_term = -np.log(2 * np.pi)
        correction = -0.5 * np.log(1 - x**(-2)) if x > 1 else 0

        # Zero contribution
        # Use first few known zeros of ζ(s)
        # Known zeros: ρ = 1/2 + iγ
        if zeros is None:
            # First few imaginary parts of nontrivial zeros
            zeros_gamma = [
                14.134725,  # First zero
                21.022040,
                25.010858,
                30.424876,
                32.935062,
                37.586178,
                40.918719,
                43.327073,
                48.005151,
                49.773832
            ]
            zeros = [0.5 + 1j * gamma for gamma in zeros_gamma[:max_zeros]]

        zero_sum = 0
        zero_terms = []

        for rho in zeros:
            # x^ρ / ρ
            try:
                term = (x ** rho) / rho
                zero_sum += term.real  # Take real part
                zero_terms.append(term)
                self.zero_contributions_computed += 1
            except:
                pass

        # Explicit formula
        psi_explicit = main_term - zero_sum + log_term + correction

        return {
            'x': x,
            'psi_x_explicit': float(psi_explicit.real),
            'main_term': float(main_term),
            'zero_contribution': float(-zero_sum),
            'log_term': float(log_term),
            'correction_term': float(correction),
            'num_zeros_used': len(zeros),
            'formula': 'ψ(x) = x - Σ(x^ρ/ρ) - log(2π) - (1/2)log(1-x^(-2))',
            'method': 'riemann_von_mangoldt'
        }

    # ==================== BDI METHODS ====================

    def update_beliefs(self):
        """
        Update beliefs from Blackboard.

        Queries for pending explicit formula tasks.
        """
        if not self.blackboard:
            return

        try:
            entries = self.blackboard.query_entries(
                tags=['number_theory', 'explicit_formula'],
                status='pending'
            ) if hasattr(self.blackboard, 'query_entries') else []

            for entry in entries:
                belief_key = f'pending_explicit_{entry.entry_id}'
                if not self.has_belief(belief_key):
                    self.add_belief(belief_key, entry, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """
        Generate intentions from beliefs.

        Creates compute intentions for pending tasks.

        Returns:
            List of new intentions
        """
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_explicit_'):
                continue

            task = belief.content
            task_id = task.entry_id if hasattr(task, 'entry_id') else str(hash(str(task)))

            # Skip if already processing
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            # Create intention
            intention = Intention(
                goal=f'compute_explicit_{task_id}',
                plan=['claim', 'compute', 'post'],
                priority=5,
                metadata={'task_id': task_id, 'task_entry': task}
            )
            new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention: Intention):
        """
        Execute next step in intention plan.

        Steps:
            - claim: Claim task from blackboard
            - compute: Compute explicit formula
            - post: Post result to blackboard

        Args:
            intention: Current intention
        """
        if not intention or not hasattr(intention, 'get_current_action'):
            return

        action = intention.get_current_action()

        if action == 'claim':
            intention.advance()

        elif action == 'compute':
            task_entry = intention.metadata.get('task_entry')
            if task_entry:
                result = self.process(task_entry)
                intention.metadata['result'] = result
                intention.advance()
            else:
                intention.fail('No task entry')

        elif action == 'post':
            result = intention.metadata.get('result')
            if self.blackboard and result:
                if not hasattr(result, 'entry_id'):
                    entry = create_entry(
                        EntryType.PARTIAL_RESULT,
                        create_variable(str(result)),
                        self.agent_id,
                        'explicit_result',
                        ['number_theory', 'explicit_formula', 'result'],
                        EntryStatus.COMPLETED,
                        {'result': result}
                    )
                    self.blackboard.post(entry)
            intention.complete()

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming BDI message.

        Args:
            message: Message dict with 'action' and 'params'

        Returns:
            Response dict
        """
        action = message.get('action', '')
        params = message.get('params', {})

        if action == 'von_mangoldt':
            result = self.von_mangoldt(**params)
            return {'status': 'success', 'result': result}
        elif action == 'chebyshev_psi':
            result = self.chebyshev_psi(**params)
            return {'status': 'success', 'result': result}
        elif action == 'explicit_formula':
            result = self.explicit_formula_psi(**params)
            return {'status': 'success', 'result': result}
        else:
            return {'status': 'error', 'message': f'Unknown action: {action}'}

    def get_stats(self) -> Dict[str, int]:
        """
        Get computation statistics.

        Returns:
            Stats dict
        """
        return {
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'formulas_evaluated': self.formulas_evaluated,
            'zero_contributions_computed': self.zero_contributions_computed,
            'von_mangoldt_calls': self.von_mangoldt_calls,
            'chebyshev_calls': self.chebyshev_calls
        }


# Export
__all__ = ['ExplicitFormulaSpecialist']


if __name__ == '__main__':
    """Test Explicit Formula Specialist."""
    print("=" * 80)
    print("EXPLICIT FORMULA SPECIALIST TEST")
    print("=" * 80)

    specialist = ExplicitFormulaSpecialist()

    # Test von Mangoldt
    print("\n--- von Mangoldt Function ---")
    for n in [1, 2, 4, 8, 9, 10, 16, 17]:
        result = specialist.von_mangoldt(n)
        print(f"Lambda({n}) = {result['lambda_n']:.4f} - {result.get('formula', '')}")

    # Test Chebyshev
    print("\n--- Chebyshev Function ---")
    for x in [10, 50, 100]:
        result = specialist.chebyshev_psi(x)
        print(f"psi({x}) = {result['psi_x']:.4f}, ratio to x: {result['ratio_to_x']:.4f}")

    # Test explicit formula
    print("\n--- Explicit Formula ---")
    result = specialist.explicit_formula_psi(100, max_zeros=5)
    print(f"psi(100) via explicit formula = {result['psi_x_explicit']:.4f}")
    print(f"  Main term: {result['main_term']:.4f}")
    print(f"  Zero contribution: {result['zero_contribution']:.4f}")
    print(f"  Zeros used: {result['num_zeros_used']}")

    print(f"\nStatistics: {specialist.get_stats()}")
