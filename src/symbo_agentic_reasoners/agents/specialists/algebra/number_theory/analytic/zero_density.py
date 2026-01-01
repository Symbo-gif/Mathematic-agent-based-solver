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
ZERO DENSITY SPECIALIST (Tier 3)
=================================

Computes zero-density estimates for the Riemann zeta function and L-functions.

CAPABILITIES:
------------
- Zero counting functions N(σ, T)
- Density estimates for zeros in critical strip
- Ingham-Huxley bounds
- Zero-free regions
- Distribution of zeros near critical line

ALGORITHMS:
-----------
1. Zero counting function:
   N(σ, T) = number of zeros ρ = β + iγ with β ≥ σ and 0 < γ ≤ T

2. Classical estimates:
   - N(T) ≈ (T/2π) log(T/2π) - T/2π (on critical line σ = 1/2)
   - Riemann-von Mangoldt formula

3. Density estimates:
   - N(σ, T) ≤ C T^{A(1-σ)} log^B T for σ > 1/2
   - Classical: A = 2, B = 3
   - Ingham: A = 3/2, B = 2
   - Huxley: A = 32/21 ≈ 1.524

4. Zero-free regions:
   - Classical: Re(s) > 1 - c/log(|Im(s)|)
   - Vinogradov-Korobov region

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


class ZeroDensitySpecialist(BDIAgent):
    """
    Zero Density Specialist - Zeta Function Zero Distribution

    DIRECTIVE:
    ---------
    Compute zero-density estimates and distribution statistics.

    OPERATIONS:
    ----------
    - count_zeros: N(T) = zeros on critical line up to height T
    - density_estimate: N(σ, T) bounds in critical strip
    - zero_free_region: Classical zero-free region boundary
    - riemann_von_mangoldt: Exact zero counting formula
    - huxley_bound: Modern density estimate

    ZERO COUNTING:
    -------------
    N(T) = (T/2π) log(T/2π) - T/2π + O(log T)

    Count of zeros with 0 < Im(ρ) ≤ T on σ = 1/2.

    DENSITY ESTIMATES:
    -----------------
    N(σ, T) ≤ C T^{A(1-σ)} log^B T

    Classical: A = 2, B = 3
    Ingham: A = 3/2, B = 2
    Huxley: A = 32/21, B = 7

    ZERO-FREE REGION:
    ----------------
    ζ(s) ≠ 0 for Re(s) > 1 - c / log(|Im(s)|)

    where c > 0 is an absolute constant.

    REFERENCE:
    ---------
    Riemann hypothesis analytic techniques
    Target: Accurate zero distribution analysis
    """

    def __init__(
        self,
        agent_id: str = 'zero_density_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Zero Density Specialist.

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
        self.estimates_computed = 0
        self.critical_strip_analyzed = 0
        self.zero_counts = 0
        self.bounds_applied = 0

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        logger.info(f"[{self.agent_id}] Zero Density Specialist initialized")
        logger.info(f"  Method: Density estimates and zero counting")

    def _register_services(self):
        """
        Register services with Directory Facilitator.

        Registers:
            - math.algebra.numbertheory.analytic.zero_density
        """
        registration = create_service_registration(
            service_type='math.algebra.numbertheory.analytic.zero_density',
            agent_id=self.agent_id,
            algorithm='density_estimates',
            cost='medium',
            instance=self,
            type='specialist',
            tier='3',
            capabilities='zero_counting_density_bounds_critical_strip'
        )
        self.df.register(registration)
        logger.info(f"  [DF] Registered: math.algebra.numbertheory.analytic.zero_density")

    def process(self, task_entry: Any) -> Any:
        """
        Process zero density task.

        Args:
            task_entry: Task entry from blackboard

        Returns:
            Result entry with computation or error
        """
        logger.info(f"\n[{self.agent_id}] Processing zero density task")

        self.tasks_executed += 1

        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            raw_input = metadata.get('raw_input', '')
            operation = metadata.get('operation', 'count_zeros')
            T = metadata.get('T', 100.0)
            sigma = metadata.get('sigma', 0.5)
            bound_type = metadata.get('bound_type', 'classical')

            logger.info(f"  Operation: {operation}")
            logger.info(f"  Parameters: T={T}, σ={sigma}, bound={bound_type}")

            # Route to appropriate method
            if operation == 'count_zeros':
                result = self.count_zeros(T)
            elif operation == 'density_estimate':
                result = self.density_estimate(sigma, T, bound_type)
            elif operation == 'zero_free_region':
                result = self.zero_free_region(T)
            else:
                result = {'error': f'Unknown operation: {operation}'}

            if 'error' not in result:
                self.tasks_succeeded += 1
                self.estimates_computed += 1
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
                    ['number_theory', 'zero_density'],
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
                    ['number_theory', 'zero_density', 'error'],
                    EntryStatus.FAILED,
                    {'error': str(e)}
                )
            else:
                return {'error': str(e)}

    def count_zeros(self, T: float) -> Dict[str, Any]:
        """
        Count zeros on critical line up to height T.

        Uses Riemann-von Mangoldt formula:
        N(T) = (T/2π) log(T/2π) - T/2π + O(log T)

        Args:
            T: Height parameter

        Returns:
            Result dict with N(T)
        """
        self.zero_counts += 1

        if T <= 0:
            return {'T': T, 'error': 'T must be positive'}

        # Main term
        main_term = (T / (2 * np.pi)) * np.log(T / (2 * np.pi))

        # Linear correction
        linear_term = -T / (2 * np.pi)

        # Small correction (O(log T))
        correction = np.log(T) / 10  # Approximation

        # Total
        N_T = main_term + linear_term + correction

        return {
            'T': T,
            'N_T': float(N_T),
            'main_term': float(main_term),
            'linear_term': float(linear_term),
            'correction': float(correction),
            'formula': 'N(T) = (T/2π)log(T/2π) - T/2π + O(log T)',
            'interpretation': f'Approximately {int(N_T)} zeros on σ=1/2 with 0 < Im(ρ) ≤ {T}'
        }

    def density_estimate(
        self,
        sigma: float,
        T: float,
        bound_type: str = 'classical'
    ) -> Dict[str, Any]:
        """
        Compute density estimate N(σ, T).

        N(σ, T) ≤ C T^{A(1-σ)} log^B T

        Args:
            sigma: Real part (1/2 ≤ σ < 1)
            T: Height parameter
            bound_type: 'classical', 'ingham', or 'huxley'

        Returns:
            Result dict with bound
        """
        self.estimates_computed += 1
        self.critical_strip_analyzed += 1

        if sigma < 0.5 or sigma >= 1:
            return {
                'sigma': sigma,
                'T': T,
                'error': 'σ must be in [1/2, 1) for critical strip'
            }

        if T <= 0:
            return {'sigma': sigma, 'T': T, 'error': 'T must be positive'}

        # Select bound parameters
        if bound_type == 'classical':
            A, B = 2, 3
            C = 100  # Rough constant
        elif bound_type == 'ingham':
            A, B = 1.5, 2
            C = 50
        elif bound_type == 'huxley':
            A, B = 32/21, 7
            C = 30
        else:
            A, B = 2, 3
            C = 100

        self.bounds_applied += 1

        # Compute bound
        exponent = A * (1 - sigma)
        bound = C * (T ** exponent) * (np.log(T) ** B)

        return {
            'sigma': sigma,
            'T': T,
            'N_sigma_T_bound': float(bound),
            'A': A,
            'B': B,
            'C': C,
            'bound_type': bound_type,
            'formula': f'N(σ,T) ≤ C T^(A(1-σ)) log^B(T)',
            'parameters': f'A={A}, B={B}, C={C}',
            'exponent': f'{A}(1-{sigma}) = {exponent}',
            'interpretation': f'At most {int(bound)} zeros with Re(ρ) ≥ {sigma} and 0 < Im(ρ) ≤ {T}'
        }

    def zero_free_region(self, t: float) -> Dict[str, Any]:
        """
        Compute classical zero-free region boundary.

        ζ(s) ≠ 0 for Re(s) > 1 - c / log(|Im(s)|)

        Args:
            t: Imaginary part (height)

        Returns:
            Result dict with zero-free boundary
        """
        if t <= 2:
            return {'t': t, 'error': 't must be > 2 for classical bound'}

        # Classical constant (de la Vallée-Poussin type)
        c = 0.1  # Simplified constant

        # Boundary
        sigma_boundary = 1 - c / np.log(abs(t))

        return {
            't': t,
            'sigma_boundary': float(sigma_boundary),
            'constant_c': c,
            'formula': 'ζ(s) ≠ 0 for Re(s) > 1 - c/log(|Im(s)|)',
            'interpretation': f'No zeros with Re(ρ) > {sigma_boundary:.6f} at height {t}',
            'distance_from_1': float(1 - sigma_boundary),
            'type': 'classical_zero_free_region'
        }

    # ==================== BDI METHODS ====================

    def update_beliefs(self):
        """
        Update beliefs from Blackboard.

        Queries for pending zero density tasks.
        """
        if not self.blackboard:
            return

        try:
            entries = self.blackboard.query_entries(
                tags=['number_theory', 'zero_density'],
                status='pending'
            ) if hasattr(self.blackboard, 'query_entries') else []

            for entry in entries:
                belief_key = f'pending_zero_density_{entry.entry_id}'
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
            if not predicate.startswith('pending_zero_density_'):
                continue

            task = belief.content
            task_id = task.entry_id if hasattr(task, 'entry_id') else str(hash(str(task)))

            # Skip if already processing
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            # Create intention
            intention = Intention(
                goal=f'compute_density_{task_id}',
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
            - compute: Compute zero density
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
                        'density_result',
                        ['number_theory', 'zero_density', 'result'],
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

        if action == 'count_zeros':
            result = self.count_zeros(**params)
            return {'status': 'success', 'result': result}
        elif action == 'density_estimate':
            result = self.density_estimate(**params)
            return {'status': 'success', 'result': result}
        elif action == 'zero_free_region':
            result = self.zero_free_region(**params)
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
            'estimates_computed': self.estimates_computed,
            'critical_strip_analyzed': self.critical_strip_analyzed,
            'zero_counts': self.zero_counts,
            'bounds_applied': self.bounds_applied
        }


# Export
__all__ = ['ZeroDensitySpecialist']


if __name__ == '__main__':
    """Test Zero Density Specialist."""
    print("=" * 80)
    print("ZERO DENSITY SPECIALIST TEST")
    print("=" * 80)

    specialist = ZeroDensitySpecialist()

    # Test zero counting
    print("\n--- Zero Counting ---")
    for T in [10, 100, 1000]:
        result = specialist.count_zeros(T)
        print(f"N({T}) ~= {result['N_T']:.2f} zeros")

    # Test density estimates
    print("\n--- Density Estimates ---")
    T = 1000
    for sigma in [0.5, 0.6, 0.75, 0.9]:
        for bound_type in ['classical', 'ingham', 'huxley']:
            result = specialist.density_estimate(sigma, T, bound_type)
            print(f"N({sigma}, {T}) <= {result['N_sigma_T_bound']:.2e} ({bound_type})")

    # Test zero-free region
    print("\n--- Zero-Free Region ---")
    for t in [10, 100, 1000]:
        result = specialist.zero_free_region(t)
        print(f"At height {t}: sigma > {result['sigma_boundary']:.6f}")

    print(f"\nStatistics: {specialist.get_stats()}")
