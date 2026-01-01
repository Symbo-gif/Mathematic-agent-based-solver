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
HAMMING DISTANCE SPECIALIST (Tier 3)
=====================================

Handles Hamming distance computation and related operations.

CAPABILITIES:
------------
- hamming_distance: Count differing positions between two vectors
- hamming_weight: Count non-zero positions in vector
- minimum_weight: Find minimum weight among codewords
- sphere_volume: Compute V_q(n,t) = Σ C(n,i)(q-1)^i
- error_capability: Compute detection/correction capability from d

FORMULATION:
-----------
Hamming Distance: d(x,y) = |{i : x_i ≠ y_i}|
Hamming Weight: w(x) = |{i : x_i ≠ 0}|
For linear codes: d_min = min{w(c) : c ∈ C, c ≠ 0}
Sphere Volume: V_q(n,t) = Σ_{i=0}^{t} C(n,i)(q-1)^i

Error Capability:
- Detection: t_detect = d - 1 errors
- Correction: t_correct = ⌊(d-1)/2⌋ errors

ALGORITHMIC BACKING:
-------------------
Native implementations from core/coding_theory_native.py

NO SYMPY - Pure native mathematical reasoning.

REFERENCE:
---------
- MacWilliams & Sloane (1977), Chapter 1: Distance Properties
- Huffman & Pless (2003), Fundamentals of Error-Correcting Codes
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
    hamming_distance as native_hamming_distance,
    hamming_weight as native_hamming_weight,
    sphere_volume as native_sphere_volume,
    binomial
)

logger = logging.getLogger(__name__)


class HammingDistanceSpecialist(BDIAgent):
    """
    Hamming Distance Specialist - Distance Metric Operations

    DIRECTIVE:
    ---------
    Handle Hamming distance and weight computations.

    OPERATIONS:
    ----------
    - distance: Compute Hamming distance between vectors
    - weight: Compute Hamming weight of vector
    - minimum_weight: Find minimum nonzero weight in code
    - sphere_volume: Hamming sphere volume
    - error_capability: Error detection/correction capability

    FORMULATION:
    -----------
    Hamming distance is the fundamental metric for error-correcting codes.
    Minimum distance determines the code's error-correcting capability.

    REFERENCE:
    ---------
    - MacWilliams & Sloane (1977), Theory of Error-Correcting Codes
    """

    def __init__(
        self,
        agent_id: str = 'hamming_distance_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Hamming Distance Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.distances_computed = 0
        self.weights_computed = 0
        self.minimum_weights_found = 0
        self.sphere_volumes_computed = 0

        if self.df:
            self._register_services()

    def _register_services(self):
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            service_type='math.information_theory.error_correction.distance',
            agent_id=self.agent_id,
            algorithm='hamming_distance',
            cost='low',
            instance=self,
            type='specialist',
            tier='3',
            operations='distance_weight_minimum_sphere'
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered as hamming distance specialist")

    # ========================================
    # Core Operations
    # ========================================

    def compute_distance(
        self,
        x: List[int],
        y: List[int]
    ) -> Dict[str, Any]:
        """
        Compute Hamming distance between two vectors.

        Args:
            x: First vector
            y: Second vector (same length as x)

        Returns:
            Hamming distance d(x, y)
        """
        if len(x) != len(y):
            return {
                'success': False,
                'error': f'Vectors must have same length: {len(x)} vs {len(y)}'
            }

        try:
            distance = native_hamming_distance(x, y)
            self.distances_computed += 1

            return {
                'success': True,
                'distance': distance,
                'vector_length': len(x),
                'agreement_positions': len(x) - distance,
                'method': 'position_comparison'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def compute_weight(self, x: List[int]) -> Dict[str, Any]:
        """
        Compute Hamming weight of vector.

        Args:
            x: Vector to weigh

        Returns:
            Hamming weight w(x)
        """
        try:
            weight = native_hamming_weight(x)
            self.weights_computed += 1

            return {
                'success': True,
                'weight': weight,
                'vector_length': len(x),
                'density': weight / len(x) if len(x) > 0 else 0,
                'method': 'nonzero_count'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def minimum_weight(
        self,
        codewords: List[List[int]],
        exclude_zero: bool = True
    ) -> Dict[str, Any]:
        """
        Find minimum Hamming weight among codewords.

        For linear codes, d_min = min{w(c) : c ≠ 0}.

        Args:
            codewords: List of codewords
            exclude_zero: Whether to exclude zero codeword

        Returns:
            Minimum weight and achieving codeword
        """
        if not codewords:
            return {'success': False, 'error': 'Codeword list cannot be empty'}

        try:
            min_weight = float('inf')
            min_codeword = None

            for cw in codewords:
                weight = native_hamming_weight(cw)

                if exclude_zero and weight == 0:
                    continue

                if weight < min_weight:
                    min_weight = weight
                    min_codeword = cw

            if min_codeword is None:
                return {
                    'success': True,
                    'minimum_weight': 0,
                    'note': 'Only zero codeword found',
                    'method': 'enumeration'
                }

            self.minimum_weights_found += 1

            return {
                'success': True,
                'minimum_weight': min_weight,
                'achieving_codeword': min_codeword,
                'codewords_checked': len(codewords),
                'method': 'enumeration'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def sphere_volume(
        self,
        n: int,
        t: int,
        q: int = 2
    ) -> Dict[str, Any]:
        """
        Compute Hamming sphere volume V_q(n,t).

        V_q(n,t) = Σ_{i=0}^{t} C(n,i)(q-1)^i

        This is the number of vectors at distance ≤ t from any given vector.

        Args:
            n: Vector length
            t: Sphere radius
            q: Alphabet size

        Returns:
            Sphere volume
        """
        if n < 0 or t < 0:
            return {'success': False, 'error': 'n and t must be non-negative'}

        if t > n:
            return {'success': False, 'error': f't={t} cannot exceed n={n}'}

        try:
            volume = native_sphere_volume(n, t, q)
            self.sphere_volumes_computed += 1

            # Compute individual shell sizes
            shells = []
            for i in range(t + 1):
                shell_size = binomial(n, i) * ((q - 1) ** i)
                shells.append({'radius': i, 'size': shell_size})

            return {
                'success': True,
                'volume': volume,
                'n': n,
                't': t,
                'q': q,
                'shells': shells,
                'total_space': q ** n,
                'coverage_ratio': volume / (q ** n) if q ** n > 0 else 0,
                'method': 'binomial_sum'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def error_capability(self, d: int) -> Dict[str, Any]:
        """
        Compute error detection and correction capability from minimum distance.

        Args:
            d: Minimum distance

        Returns:
            Detection and correction capabilities
        """
        if d < 1:
            return {'success': False, 'error': 'd must be positive'}

        t_detect = d - 1
        t_correct = (d - 1) // 2

        return {
            'success': True,
            'minimum_distance': d,
            'detection_capability': t_detect,
            'correction_capability': t_correct,
            'can_detect': f'up to {t_detect} errors',
            'can_correct': f'up to {t_correct} errors',
            'method': 'distance_bounds'
        }

    def distance_distribution(
        self,
        codewords: List[List[int]]
    ) -> Dict[str, Any]:
        """
        Compute distance distribution between all pairs of codewords.

        Args:
            codewords: List of codewords

        Returns:
            Distribution of pairwise distances
        """
        if not codewords:
            return {'success': False, 'error': 'Codeword list cannot be empty'}

        if len(codewords) > 256:
            return {
                'success': False,
                'error': 'Too many codewords for full distance distribution (max 256)'
            }

        try:
            distribution = {}
            min_dist = float('inf')
            max_dist = 0

            for i in range(len(codewords)):
                for j in range(i + 1, len(codewords)):
                    d = native_hamming_distance(codewords[i], codewords[j])
                    distribution[d] = distribution.get(d, 0) + 1
                    min_dist = min(min_dist, d)
                    max_dist = max(max_dist, d)

            return {
                'success': True,
                'distribution': distribution,
                'minimum_distance': min_dist if min_dist != float('inf') else 0,
                'maximum_distance': max_dist,
                'num_pairs': len(codewords) * (len(codewords) - 1) // 2,
                'method': 'pairwise_enumeration'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ========================================
    # Task Processing
    # ========================================

    def process(self, task_entry: Any) -> Any:
        """Process Hamming distance task."""
        self.tasks_executed += 1

        try:
            if hasattr(task_entry, 'metadata'):
                metadata = task_entry.metadata or {}
            elif isinstance(task_entry, dict):
                metadata = task_entry
            else:
                metadata = {'operation': str(task_entry)}

            operation = metadata.get('operation', 'distance')
            x = metadata.get('x') or metadata.get('vector1')
            y = metadata.get('y') or metadata.get('vector2')
            codewords = metadata.get('codewords')
            n = metadata.get('n')
            t = metadata.get('t')
            d = metadata.get('d')
            q = metadata.get('q', 2)

            if operation in ['distance', 'hamming_distance']:
                result = self.compute_distance(x, y)
            elif operation in ['weight', 'hamming_weight']:
                result = self.compute_weight(x)
            elif operation in ['minimum', 'minimum_weight', 'min_weight']:
                result = self.minimum_weight(codewords)
            elif operation in ['sphere', 'sphere_volume', 'volume']:
                result = self.sphere_volume(n, t, q)
            elif operation in ['capability', 'error_capability']:
                result = self.error_capability(d)
            elif operation in ['distribution', 'distance_distribution']:
                result = self.distance_distribution(codewords)
            else:
                if x is not None and y is not None:
                    result = self.compute_distance(x, y)
                elif x is not None:
                    result = self.compute_weight(x)
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
                    ['error_correction', 'hamming_distance'],
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
        """PERCEIVE: Monitor blackboard for distance tasks."""
        if not self.blackboard:
            return

        entries = self.blackboard.query_entries(
            tags=['hamming_distance', 'distance', 'weight'],
            status=EntryStatus.PENDING
        )

        for entry in entries:
            belief_key = f'pending_dist_{entry.entry_id}'
            if not self.has_belief(belief_key):
                self.add_belief(belief_key, entry, confidence=1.0, source='blackboard')

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create plans from beliefs."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_dist_'):
                continue

            task = belief.content
            task_id = task.entry_id if hasattr(task, 'entry_id') else str(task)

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            intention = Intention(
                goal=f'solve_dist_{task_id}',
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
            'distances_computed': self.distances_computed,
            'weights_computed': self.weights_computed,
            'minimum_weights_found': self.minimum_weights_found,
            'sphere_volumes_computed': self.sphere_volumes_computed,
        }
