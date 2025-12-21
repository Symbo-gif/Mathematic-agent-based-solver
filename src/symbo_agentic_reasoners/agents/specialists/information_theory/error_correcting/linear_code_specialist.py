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
LINEAR CODE SPECIALIST (Tier 3)
================================

Handles construction and validation of linear error-correcting codes.

CAPABILITIES:
------------
- construct_from_generator: Build [n,k,d] code from generator matrix G
- validate_parameters: Check Singleton/Hamming/Plotkin bounds
- is_systematic: Check if G = [I_k | P]
- make_systematic: Convert to systematic form via row reduction
- code_rate: Compute R = k/n

FORMULATION:
-----------
Linear [n,k,d] code C over GF(q):
- n = code length (block size)
- k = dimension (message bits)
- d = minimum distance (error detection/correction)
- R = k/n = code rate

Bounds on parameters:
- Singleton: d <= n - k + 1 (equality for MDS codes)
- Hamming: Sum_{i=0}^{t} C(n,i)(q-1)^i <= q^{n-k}
- Plotkin: For d > n(q-1)/q

ALGORITHMIC BACKING:
-------------------
Native GF(2) matrix operations from core/coding_theory_native.py

NO SYMPY - Pure native mathematical reasoning.

REFERENCE:
---------
- MacWilliams & Sloane (1977), Chapter 1: Linear Codes
- Lin & Costello (2004), Chapter 3: Linear Block Codes
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
    gf2_rref, gf2_rank, singleton_bound, hamming_bound,
    plotkin_bound, griesmer_bound
)

logger = logging.getLogger(__name__)


class LinearCodeSpecialist(BDIAgent):
    """
    Linear Code Specialist - [n,k,d] Code Construction

    DIRECTIVE:
    ---------
    Handle construction and validation of linear error-correcting codes.

    OPERATIONS:
    ----------
    - construct: Build code from generator matrix
    - validate: Check parameters against bounds
    - systematic: Convert to systematic form
    - rate: Compute code rate

    FORMULATION:
    -----------
    Linear code C is k-dimensional subspace of GF(q)^n.
    Generator matrix G is k×n with C = {mG : m ∈ GF(q)^k}.

    REFERENCE:
    ---------
    - MacWilliams & Sloane (1977), Theory of Error-Correcting Codes
    """

    def __init__(
        self,
        agent_id: str = 'linear_code_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Linear Code Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.codes_constructed = 0
        self.parameters_validated = 0
        self.systematic_conversions = 0
        self.equivalence_checks = 0

        if self.df:
            self._register_services()

    def _register_services(self):
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            service_type='math.information_theory.error_correction.linear',
            agent_id=self.agent_id,
            algorithm='linear_code_construction',
            cost='medium',
            instance=self,
            type='specialist',
            tier='3',
            operations='construct_validate_systematic_rate'
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered as linear code specialist")

    # ========================================
    # Core Operations
    # ========================================

    def construct_from_generator(
        self,
        G: List[List[int]],
        q: int = 2
    ) -> Dict[str, Any]:
        """
        Construct linear code from generator matrix.

        Args:
            G: Generator matrix (k×n over GF(q))
            q: Field size (default 2 for binary)

        Returns:
            Code structure with parameters
        """
        if not G or not G[0]:
            return {'success': False, 'error': 'Generator matrix cannot be empty'}

        try:
            k = len(G)
            n = len(G[0])

            # Validate dimensions
            for row in G:
                if len(row) != n:
                    return {'success': False, 'error': 'Generator matrix rows must have same length'}

            # Check rank equals k (full row rank)
            rank = gf2_rank(G) if q == 2 else self._matrix_rank_gfq(G, q)

            if rank != k:
                return {
                    'success': False,
                    'error': f'Generator matrix has rank {rank}, expected {k} (full row rank)'
                }

            # Compute code rate
            rate = k / n

            self.codes_constructed += 1

            return {
                'success': True,
                'code': {
                    'n': n,
                    'k': k,
                    'generator': G,
                    'field_size': q,
                    'rate': rate,
                    'dimension': k,
                    'length': n,
                    'num_codewords': q ** k
                },
                'method': 'generator_construction'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def validate_parameters(
        self,
        n: int,
        k: int,
        d: int,
        q: int = 2
    ) -> Dict[str, Any]:
        """
        Validate code parameters against known bounds.

        Args:
            n: Code length
            k: Dimension
            d: Minimum distance
            q: Field size

        Returns:
            Validation result with applicable bounds
        """
        if n < 1 or k < 1 or d < 1:
            return {'success': False, 'error': 'Parameters must be positive'}

        if k > n:
            return {'success': False, 'error': f'k={k} cannot exceed n={n}'}

        if d > n:
            return {'success': False, 'error': f'd={d} cannot exceed n={n}'}

        try:
            bounds_analysis = {}

            # Singleton bound: d <= n - k + 1
            singleton_max = singleton_bound(n, k, q)
            bounds_analysis['singleton'] = {
                'bound': singleton_max,
                'satisfied': d <= singleton_max,
                'is_mds': d == singleton_max
            }

            # Hamming bound (sphere-packing)
            t = (d - 1) // 2  # Error correction capability
            hamming_ok = hamming_bound(n, k, t, q)
            bounds_analysis['hamming'] = {
                'correction_capability': t,
                'satisfied': hamming_ok,
                'is_perfect': hamming_ok  # If bound is tight
            }

            # Plotkin bound
            try:
                plotkin_max = plotkin_bound(n, d, q)
                bounds_analysis['plotkin'] = {
                    'max_codewords': plotkin_max,
                    'satisfied': q ** k <= plotkin_max if plotkin_max > 0 else True
                }
            except Exception:
                bounds_analysis['plotkin'] = {'applicable': False}

            # Griesmer bound
            try:
                griesmer_min = griesmer_bound(k, d, q)
                bounds_analysis['griesmer'] = {
                    'min_length': griesmer_min,
                    'satisfied': n >= griesmer_min
                }
            except Exception:
                bounds_analysis['griesmer'] = {'applicable': False}

            all_satisfied = all(
                b.get('satisfied', True)
                for b in bounds_analysis.values()
                if isinstance(b, dict)
            )

            self.parameters_validated += 1

            return {
                'success': True,
                'valid': all_satisfied,
                'parameters': {'n': n, 'k': k, 'd': d, 'q': q},
                'bounds': bounds_analysis,
                'rate': k / n,
                'method': 'bounds_verification'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def is_systematic(self, G: List[List[int]]) -> Dict[str, Any]:
        """
        Check if generator matrix is in systematic form [I_k | P].

        Args:
            G: Generator matrix

        Returns:
            True if systematic
        """
        if not G or not G[0]:
            return {'success': False, 'error': 'Matrix cannot be empty'}

        try:
            k = len(G)
            n = len(G[0])

            if k > n:
                return {
                    'success': True,
                    'is_systematic': False,
                    'reason': 'k > n'
                }

            # Check if first k columns form identity matrix
            is_sys = True
            for i in range(k):
                for j in range(k):
                    expected = 1 if i == j else 0
                    if G[i][j] != expected:
                        is_sys = False
                        break
                if not is_sys:
                    break

            return {
                'success': True,
                'is_systematic': is_sys,
                'k': k,
                'n': n,
                'method': 'identity_check'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def make_systematic(
        self,
        G: List[List[int]],
        q: int = 2
    ) -> Dict[str, Any]:
        """
        Convert generator matrix to systematic form [I_k | P].

        Args:
            G: Generator matrix
            q: Field size

        Returns:
            Systematic form and parity matrix P
        """
        if not G or not G[0]:
            return {'success': False, 'error': 'Matrix cannot be empty'}

        try:
            k = len(G)
            n = len(G[0])

            if q == 2:
                # Use GF(2) row reduction
                systematic, rank = gf2_rref(G)
            else:
                systematic = self._rref_gfq(G, q)
                rank = len([r for r in systematic if any(c != 0 for c in r)])

            if rank != k:
                return {
                    'success': False,
                    'error': f'Matrix is not full rank ({rank} < {k})'
                }

            # Extract parity matrix P (columns k to n-1)
            parity_matrix = [row[k:] for row in systematic[:k]]

            self.systematic_conversions += 1

            return {
                'success': True,
                'systematic_generator': systematic[:k],
                'parity_matrix': parity_matrix,
                'original_k': k,
                'original_n': n,
                'method': 'row_reduction'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def code_rate(self, n: int, k: int) -> Dict[str, Any]:
        """
        Compute code rate R = k/n.

        Args:
            n: Code length
            k: Dimension

        Returns:
            Code rate and interpretation
        """
        if n < 1 or k < 1:
            return {'success': False, 'error': 'Parameters must be positive'}

        if k > n:
            return {'success': False, 'error': f'k={k} cannot exceed n={n}'}

        rate = k / n
        redundancy = 1 - rate

        return {
            'success': True,
            'rate': rate,
            'redundancy': redundancy,
            'overhead': (n - k) / k if k > 0 else float('inf'),
            'interpretation': self._rate_interpretation(rate),
            'method': 'direct_computation'
        }

    def _rate_interpretation(self, rate: float) -> str:
        """Interpret code rate."""
        if rate >= 0.9:
            return 'Very high rate (minimal redundancy)'
        elif rate >= 0.7:
            return 'High rate'
        elif rate >= 0.5:
            return 'Medium rate'
        elif rate >= 0.3:
            return 'Low rate'
        else:
            return 'Very low rate (high redundancy)'

    def _matrix_rank_gfq(self, M: List[List[int]], q: int) -> int:
        """Compute matrix rank over GF(q)."""
        if not M or not M[0]:
            return 0

        # Copy matrix
        A = [[c % q for c in row] for row in M]
        rows = len(A)
        cols = len(A[0])

        rank = 0
        for col in range(cols):
            # Find pivot
            pivot = None
            for row in range(rank, rows):
                if A[row][col] != 0:
                    pivot = row
                    break

            if pivot is None:
                continue

            # Swap
            A[rank], A[pivot] = A[pivot], A[rank]

            # Eliminate
            pivot_inv = pow(A[rank][col], q - 2, q)
            for row in range(rows):
                if row != rank and A[row][col] != 0:
                    factor = (A[row][col] * pivot_inv) % q
                    for j in range(cols):
                        A[row][j] = (A[row][j] - factor * A[rank][j]) % q

            rank += 1

        return rank

    def _rref_gfq(self, M: List[List[int]], q: int) -> List[List[int]]:
        """Row reduce matrix over GF(q)."""
        if not M:
            return []

        A = [[c % q for c in row] for row in M]
        rows = len(A)
        cols = len(A[0])

        pivot_row = 0
        for col in range(cols):
            if pivot_row >= rows:
                break

            # Find pivot
            pivot = None
            for row in range(pivot_row, rows):
                if A[row][col] != 0:
                    pivot = row
                    break

            if pivot is None:
                continue

            # Swap
            A[pivot_row], A[pivot] = A[pivot], A[pivot_row]

            # Scale pivot row
            pivot_val = A[pivot_row][col]
            pivot_inv = pow(pivot_val, q - 2, q)
            A[pivot_row] = [(c * pivot_inv) % q for c in A[pivot_row]]

            # Eliminate
            for row in range(rows):
                if row != pivot_row and A[row][col] != 0:
                    factor = A[row][col]
                    for j in range(cols):
                        A[row][j] = (A[row][j] - factor * A[pivot_row][j]) % q

            pivot_row += 1

        return A

    # ========================================
    # Task Processing
    # ========================================

    def process(self, task_entry: Any) -> Any:
        """Process linear code task."""
        self.tasks_executed += 1

        try:
            if hasattr(task_entry, 'metadata'):
                metadata = task_entry.metadata or {}
            elif isinstance(task_entry, dict):
                metadata = task_entry
            else:
                metadata = {'operation': str(task_entry)}

            operation = metadata.get('operation', 'construct')
            G = metadata.get('generator') or metadata.get('G')
            n = metadata.get('n')
            k = metadata.get('k')
            d = metadata.get('d')
            q = metadata.get('q', 2)

            if operation in ['construct', 'construct_from_generator', 'build']:
                result = self.construct_from_generator(G, q)
            elif operation in ['validate', 'validate_parameters', 'check']:
                result = self.validate_parameters(n, k, d, q)
            elif operation in ['systematic', 'is_systematic']:
                result = self.is_systematic(G)
            elif operation in ['make_systematic', 'convert']:
                result = self.make_systematic(G, q)
            elif operation in ['rate', 'code_rate']:
                result = self.code_rate(n, k)
            else:
                if G is not None:
                    result = self.construct_from_generator(G, q)
                elif n is not None and k is not None and d is not None:
                    result = self.validate_parameters(n, k, d, q)
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
                    ['error_correction', 'linear_code'],
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
        """PERCEIVE: Monitor blackboard for linear code tasks."""
        if not self.blackboard:
            return

        entries = self.blackboard.query_entries(
            tags=['linear_code', 'error_correction', 'generator_matrix'],
            status=EntryStatus.PENDING
        )

        for entry in entries:
            belief_key = f'pending_lincode_{entry.entry_id}'
            if not self.has_belief(belief_key):
                self.add_belief(belief_key, entry, confidence=1.0, source='blackboard')

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create plans from beliefs."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_lincode_'):
                continue

            task = belief.content
            task_id = task.entry_id if hasattr(task, 'entry_id') else str(task)

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            intention = Intention(
                goal=f'solve_lincode_{task_id}',
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
            'codes_constructed': self.codes_constructed,
            'parameters_validated': self.parameters_validated,
            'systematic_conversions': self.systematic_conversions,
            'equivalence_checks': self.equivalence_checks,
        }
