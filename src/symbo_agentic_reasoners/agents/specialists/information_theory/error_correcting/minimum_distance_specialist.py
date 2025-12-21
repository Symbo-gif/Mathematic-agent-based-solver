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
MINIMUM DISTANCE SPECIALIST (Tier 3)
=====================================

Handles minimum distance computation and weight distribution.

CAPABILITIES:
------------
- compute_minimum_distance: Find d_min by enumeration or bounds
- weight_distribution: Compute {w: count} for all codewords
- is_perfect: Check if code is perfect (sphere packing is tight)
- bounds_analysis: Apply all 5 major bounds

FORMULATION:
-----------
Minimum Distance: d_min = min{d(c1, c2) : c1, c2 ∈ C, c1 ≠ c2}
For linear codes: d_min = min{w(c) : c ∈ C, c ≠ 0}

Weight Distribution: A_w = |{c ∈ C : w(c) = w}|
Weight Enumerator: W_C(x,y) = Σ_w A_w x^{n-w} y^w

Perfect Code: q^k · V_q(n,t) = q^n where t = ⌊(d-1)/2⌋
Examples: Hamming codes, Golay codes, trivial codes

ALGORITHMIC BACKING:
-------------------
Brute force for small k, bounds analysis for large k

NO SYMPY - Pure native mathematical reasoning.

REFERENCE:
---------
- MacWilliams & Sloane (1977), Chapter 5: Weight Distributions
- Lin & Costello (2004), Chapter 3: Minimum Distance
"""

import logging
from typing import Any, Dict, List, Optional

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.coding_theory_native import (
    hamming_weight, singleton_bound, hamming_bound,
    plotkin_bound, griesmer_bound, sphere_volume,
    is_perfect_code
)

logger = logging.getLogger(__name__)


class MinimumDistanceSpecialist(BDIAgent):
    """
    Minimum Distance Specialist - Distance and Weight Analysis

    DIRECTIVE:
    ---------
    Handle minimum distance computation and weight distribution.

    OPERATIONS:
    ----------
    - minimum_distance: Compute d_min
    - weight_distribution: Count codewords by weight
    - is_perfect: Check perfect code property
    - bounds_analysis: Apply theoretical bounds

    FORMULATION:
    -----------
    For linear code, d_min equals minimum nonzero weight.
    Weight distribution determines code quality.

    REFERENCE:
    ---------
    - MacWilliams & Sloane (1977), Theory of Error-Correcting Codes
    """

    def __init__(
        self,
        agent_id: str = 'minimum_distance_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Minimum Distance Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.minimum_distances_computed = 0
        self.weight_distributions_computed = 0
        self.perfect_code_checks = 0
        self.bounds_computed = 0

        if self.df:
            self._register_services()

    def _register_services(self):
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            service_type='math.information_theory.error_correction.minimum_distance',
            agent_id=self.agent_id,
            algorithm='minimum_distance_computation',
            cost='high',
            instance=self,
            type='specialist',
            tier='3',
            operations='distance_weight_perfect_bounds'
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered as minimum distance specialist")

    # ========================================
    # Core Operations
    # ========================================

    def compute_minimum_distance(
        self,
        G: List[List[int]],
        q: int = 2,
        max_k: int = 16
    ) -> Dict[str, Any]:
        """
        Compute minimum distance of linear code.

        For k ≤ max_k, uses brute force enumeration.
        For k > max_k, returns bounds estimate.

        Args:
            G: Generator matrix (k×n)
            q: Field size
            max_k: Maximum k for brute force

        Returns:
            Minimum distance
        """
        if not G or not G[0]:
            return {'success': False, 'error': 'Generator matrix cannot be empty'}

        k = len(G)
        n = len(G[0])

        if k > max_k:
            return self._estimate_distance_bounds(n, k, q)

        try:
            min_weight = float('inf')
            min_codeword = None

            # Enumerate all 2^k - 1 nonzero codewords
            for msg_int in range(1, q ** k):
                # Convert to message
                message = []
                temp = msg_int
                for _ in range(k):
                    message.append(temp % q)
                    temp //= q

                # Encode
                codeword = [0] * n
                for j in range(n):
                    for i in range(k):
                        if q == 2:
                            codeword[j] ^= message[i] * G[i][j]
                        else:
                            codeword[j] = (codeword[j] + message[i] * G[i][j]) % q

                weight = hamming_weight(codeword)
                if weight < min_weight:
                    min_weight = weight
                    min_codeword = codeword

            self.minimum_distances_computed += 1

            # Error capability
            t_correct = (min_weight - 1) // 2 if min_weight > 0 else 0

            return {
                'success': True,
                'minimum_distance': min_weight,
                'minimum_weight_codeword': min_codeword,
                'n': n,
                'k': k,
                'correction_capability': t_correct,
                'detection_capability': min_weight - 1 if min_weight > 0 else 0,
                'method': 'brute_force_enumeration'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _estimate_distance_bounds(
        self,
        n: int,
        k: int,
        q: int
    ) -> Dict[str, Any]:
        """Estimate minimum distance using bounds when exact computation is infeasible."""
        try:
            bounds = {}

            # Singleton bound: d ≤ n - k + 1
            singleton = singleton_bound(n, k, q)
            bounds['singleton_upper'] = singleton

            # Griesmer lower bound (for given n, k)
            # Find largest d such that Griesmer(k, d) ≤ n
            d_griesmer = 1
            for d in range(1, n + 1):
                if griesmer_bound(k, d, q) <= n:
                    d_griesmer = d
                else:
                    break
            bounds['griesmer_lower'] = d_griesmer

            return {
                'success': True,
                'minimum_distance_estimate': f'{d_griesmer} ≤ d ≤ {singleton}',
                'lower_bound': d_griesmer,
                'upper_bound': singleton,
                'bounds': bounds,
                'n': n,
                'k': k,
                'note': f'k={k} too large for exact computation (max 16)',
                'method': 'bounds_analysis'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def weight_distribution(
        self,
        G: List[List[int]],
        q: int = 2,
        max_k: int = 16
    ) -> Dict[str, Any]:
        """
        Compute weight distribution of code.

        Args:
            G: Generator matrix
            q: Field size
            max_k: Maximum k for enumeration

        Returns:
            Weight distribution {w: A_w}
        """
        if not G or not G[0]:
            return {'success': False, 'error': 'Generator matrix cannot be empty'}

        k = len(G)
        n = len(G[0])

        if k > max_k:
            return {
                'success': False,
                'error': f'k={k} too large for weight distribution (max {max_k})'
            }

        try:
            distribution = {i: 0 for i in range(n + 1)}

            # Enumerate all q^k codewords
            for msg_int in range(q ** k):
                message = []
                temp = msg_int
                for _ in range(k):
                    message.append(temp % q)
                    temp //= q

                # Encode
                codeword = [0] * n
                for j in range(n):
                    for i in range(k):
                        if q == 2:
                            codeword[j] ^= message[i] * G[i][j]
                        else:
                            codeword[j] = (codeword[j] + message[i] * G[i][j]) % q

                weight = hamming_weight(codeword)
                distribution[weight] += 1

            # Remove zero counts
            distribution = {w: count for w, count in distribution.items() if count > 0}

            self.weight_distributions_computed += 1

            return {
                'success': True,
                'weight_distribution': distribution,
                'n': n,
                'k': k,
                'total_codewords': q ** k,
                'minimum_distance': min(w for w in distribution.keys() if w > 0) if 1 in distribution or any(w > 0 for w in distribution) else 0,
                'method': 'exhaustive_enumeration'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def check_perfect(
        self,
        n: int,
        k: int,
        d: int,
        q: int = 2
    ) -> Dict[str, Any]:
        """
        Check if code is perfect.

        Perfect code: sphere packing bound is tight.

        Args:
            n: Code length
            k: Dimension
            d: Minimum distance
            q: Field size

        Returns:
            True if code is perfect
        """
        try:
            t = (d - 1) // 2  # Correction capability
            vol = sphere_volume(n, t, q)
            total_space = q ** n
            codewords = q ** k

            # Perfect if codewords × sphere_volume = total_space
            is_perf = is_perfect_code(n, k, d, q)

            self.perfect_code_checks += 1

            return {
                'success': True,
                'is_perfect': is_perf,
                'n': n,
                'k': k,
                'd': d,
                'correction_capability': t,
                'sphere_volume': vol,
                'total_space': total_space,
                'codewords': codewords,
                'packing_ratio': (codewords * vol) / total_space,
                'method': 'sphere_packing_check'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def bounds_analysis(
        self,
        n: int,
        k: int,
        q: int = 2
    ) -> Dict[str, Any]:
        """
        Apply all major bounds to code parameters.

        Args:
            n: Code length
            k: Dimension
            q: Field size

        Returns:
            All applicable bounds
        """
        try:
            bounds = {}

            # Singleton bound: d ≤ n - k + 1
            bounds['singleton'] = {
                'description': 'd ≤ n - k + 1',
                'max_d': singleton_bound(n, k, q),
                'is_mds_at_bound': True
            }

            # Hamming (sphere packing) bound
            # Find max t such that Hamming bound is satisfied
            for t in range(n + 1):
                if not hamming_bound(n, k, t, q):
                    bounds['hamming'] = {
                        'description': 'Sphere packing bound',
                        'max_correction': t - 1 if t > 0 else 0,
                        'max_d': 2 * (t - 1) + 1 if t > 0 else 1
                    }
                    break
            else:
                bounds['hamming'] = {
                    'description': 'Sphere packing bound',
                    'max_correction': n,
                    'max_d': 2 * n + 1
                }

            # Griesmer bound (lower bound on n for given k, d)
            # Find max d such that Griesmer(k, d) ≤ n
            for d in range(n, 0, -1):
                if griesmer_bound(k, d, q) <= n:
                    bounds['griesmer'] = {
                        'description': 'Lower bound on n',
                        'achievable_d': d
                    }
                    break

            self.bounds_computed += 1

            return {
                'success': True,
                'n': n,
                'k': k,
                'q': q,
                'rate': k / n,
                'bounds': bounds,
                'method': 'bounds_analysis'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ========================================
    # Task Processing
    # ========================================

    def process(self, task_entry: Any) -> Any:
        """Process minimum distance task."""
        self.tasks_executed += 1

        try:
            if hasattr(task_entry, 'metadata'):
                metadata = task_entry.metadata or {}
            elif isinstance(task_entry, dict):
                metadata = task_entry
            else:
                metadata = {'operation': str(task_entry)}

            operation = metadata.get('operation', 'minimum_distance')
            G = metadata.get('generator') or metadata.get('G')
            n = metadata.get('n')
            k = metadata.get('k')
            d = metadata.get('d')
            q = metadata.get('q', 2)

            if operation in ['minimum_distance', 'min_dist', 'dmin']:
                result = self.compute_minimum_distance(G, q)
            elif operation in ['weight_distribution', 'weight', 'distribution']:
                result = self.weight_distribution(G, q)
            elif operation in ['perfect', 'is_perfect', 'check_perfect']:
                result = self.check_perfect(n, k, d, q)
            elif operation in ['bounds', 'bounds_analysis']:
                result = self.bounds_analysis(n, k, q)
            else:
                if G is not None:
                    result = self.compute_minimum_distance(G, q)
                elif n is not None and k is not None:
                    result = self.bounds_analysis(n, k, q)
                else:
                    result = {'success': False, 'error': f'Unknown operation: {operation}'}

            if result.get('success', False):
                self.tasks_succeeded += 1
            else:
                self.tasks_failed += 1

            if self.blackboard and hasattr(task_entry, 'conversation_id'):
                return create_entry(
                    EntryType.PARTIAL_RESULT,
                    str(result),
                    self.agent_id,
                    task_entry.conversation_id,
                    ['error_correction', 'minimum_distance', 'weight'],
                    EntryStatus.COMPLETED if result.get('success') else EntryStatus.FAILED,
                    {'result': result}
                )

            return result

        except Exception as e:
            self.tasks_failed += 1
            logger.error(f"[{self.agent_id}] Task processing failed: {e}")
            return {'success': False, 'error': str(e)}

    # ========================================
    # BDI Interface
    # ========================================

    def update_beliefs(self):
        """PERCEIVE: Monitor blackboard for minimum distance tasks."""
        if not self.blackboard:
            return

        entries = self.blackboard.query_entries(
            tags=['minimum_distance', 'weight_distribution', 'perfect_code'],
            status=EntryStatus.PENDING
        )

        for entry in entries:
            belief_key = f'pending_mindist_{entry.entry_id}'
            if not self.has_belief(belief_key):
                self.add_belief(belief_key, entry, confidence=1.0, source='blackboard')

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create plans from beliefs."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_mindist_'):
                continue

            task = belief.content
            task_id = task.entry_id if hasattr(task, 'entry_id') else str(task)

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            intention = Intention(
                goal=f'solve_mindist_{task_id}',
                plan=['claim', 'solve', 'post'],
                priority=5,
                metadata={'task_id': task_id, 'task_entry': task}
            )
            new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Run one action from plan."""
        action = intention.get_current_action()

        if action == 'claim':
            intention.advance()
        elif action == 'solve':
            task_entry = intention.metadata.get('task_entry')
            result = self.process(task_entry)
            intention.metadata['result'] = result
            intention.advance()
        elif action == 'post':
            result = intention.metadata.get('result')
            if self.blackboard and result and hasattr(result, 'entry_type'):
                self.blackboard.post(result)
            intention.complete()

    # ========================================
    # Statistics
    # ========================================

    def get_stats(self) -> Dict[str, int]:
        """Return computation statistics."""
        return {
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'minimum_distances_computed': self.minimum_distances_computed,
            'weight_distributions_computed': self.weight_distributions_computed,
            'perfect_code_checks': self.perfect_code_checks,
            'bounds_computed': self.bounds_computed,
        }
