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
PARITY CHECK SPECIALIST (Tier 3)
=================================

Handles syndrome computation and syndrome decoding.

CAPABILITIES:
------------
- construct_from_generator: Build H from G = [I_k | P] → H = [P^T | I_{n-k}]
- compute_syndrome: s = r·H^T
- syndrome_decode: Map syndrome to error pattern
- build_standard_array: Construct coset leaders for decoding
- is_codeword: Check if vector is valid codeword

FORMULATION:
-----------
Parity Check Matrix H ((n-k)×n):
- c is codeword iff c·H^T = 0
- For systematic G = [I_k | P], H = [P^T | I_{n-k}]
- G·H^T = 0 (orthogonality)

Syndrome Decoding:
- Syndrome s = r·H^T where r = c + e (received = codeword + error)
- s = e·H^T (syndrome depends only on error pattern)
- Decode by finding coset leader with syndrome s

Standard Array:
- Row i: coset of codeword c_i
- Coset leaders minimize weight
- Syndrome uniquely identifies coset

ALGORITHMIC BACKING:
-------------------
Native GF(2) matrix operations

NO SYMPY - Pure native mathematical reasoning.

REFERENCE:
---------
- Lin & Costello (2004), Chapter 3: Syndrome Decoding
- MacWilliams & Sloane (1977), Chapter 1: Parity Check Matrices
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
    hamming_weight
)

logger = logging.getLogger(__name__)


class ParityCheckSpecialist(BDIAgent):
    """
    Parity Check Specialist - Syndrome Decoding

    DIRECTIVE:
    ---------
    Handle parity check operations and syndrome decoding.

    OPERATIONS:
    ----------
    - construct: Build H from generator G
    - syndrome: Compute syndrome s = r·H^T
    - decode: Syndrome table lookup
    - standard_array: Build coset leaders
    - validate: Check if vector is codeword

    FORMULATION:
    -----------
    Parity check defines code as null space: C = {c : c·H^T = 0}.
    Syndrome s = e·H^T determines error coset.

    REFERENCE:
    ---------
    - Lin & Costello (2004), Error Control Coding
    """

    def __init__(
        self,
        agent_id: str = 'parity_check_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Parity Check Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.parity_matrices_constructed = 0
        self.syndromes_computed = 0
        self.syndrome_decodings = 0
        self.standard_arrays_built = 0
        self.codeword_validations = 0

        if self.df:
            self._register_services()

    def _register_services(self):
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            service_type='math.information_theory.error_correction.parity',
            agent_id=self.agent_id,
            algorithm='syndrome_decoding',
            cost='medium',
            instance=self,
            type='specialist',
            tier='3',
            operations='construct_syndrome_decode_array'
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered as parity check specialist")

    # ========================================
    # Core Operations
    # ========================================

    def construct_from_generator(
        self,
        G: List[List[int]],
        q: int = 2
    ) -> Dict[str, Any]:
        """
        Construct parity check matrix from systematic generator.

        For G = [I_k | P], H = [P^T | I_{n-k}]

        Args:
            G: Generator matrix (must be systematic [I_k | P])
            q: Field size

        Returns:
            Parity check matrix H
        """
        if not G or not G[0]:
            return {'success': False, 'error': 'Generator matrix cannot be empty'}

        try:
            k = len(G)
            n = len(G[0])
            r = n - k  # Redundancy

            # Verify systematic form
            for i in range(k):
                for j in range(k):
                    expected = 1 if i == j else 0
                    if G[i][j] % q != expected:
                        return {
                            'success': False,
                            'error': 'Generator must be in systematic form [I_k | P]'
                        }

            # Extract P (k×r parity matrix)
            P = [row[k:] for row in G]

            # Build H = [P^T | I_r]
            H = []
            for i in range(r):
                row = []
                # P^T part
                for j in range(k):
                    row.append(P[j][i] % q)
                # I_r part
                for j in range(r):
                    row.append(1 if i == j else 0)
                H.append(row)

            self.parity_matrices_constructed += 1

            return {
                'success': True,
                'parity_check': H,
                'n': n,
                'k': k,
                'redundancy': r,
                'method': 'systematic_construction'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def compute_syndrome(
        self,
        received: List[int],
        H: List[List[int]],
        q: int = 2
    ) -> Dict[str, Any]:
        """
        Compute syndrome s = r·H^T.

        Args:
            received: Received vector r (length n)
            H: Parity check matrix (r × n)
            q: Field size

        Returns:
            Syndrome vector
        """
        if not H or not H[0]:
            return {'success': False, 'error': 'Parity check matrix cannot be empty'}

        r_parity = len(H)
        n = len(H[0])

        if len(received) != n:
            return {
                'success': False,
                'error': f'Received vector length {len(received)} must equal n={n}'
            }

        try:
            # s = r·H^T (H^T is n×r, so s is length r)
            syndrome = [0] * r_parity

            for i in range(r_parity):
                for j in range(n):
                    if q == 2:
                        syndrome[i] ^= received[j] * H[i][j]
                    else:
                        syndrome[i] = (syndrome[i] + received[j] * H[i][j]) % q

            self.syndromes_computed += 1

            is_codeword = all(s == 0 for s in syndrome)

            return {
                'success': True,
                'syndrome': syndrome,
                'is_codeword': is_codeword,
                'syndrome_weight': sum(1 for s in syndrome if s != 0),
                'method': 'matrix_multiplication'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def syndrome_decode(
        self,
        received: List[int],
        H: List[List[int]],
        syndrome_table: Dict[tuple, List[int]],
        q: int = 2
    ) -> Dict[str, Any]:
        """
        Decode using syndrome table lookup.

        Args:
            received: Received vector
            H: Parity check matrix
            syndrome_table: Map from syndrome tuple to error pattern
            q: Field size

        Returns:
            Decoded codeword
        """
        try:
            # Compute syndrome
            syn_result = self.compute_syndrome(received, H, q)
            if not syn_result['success']:
                return syn_result

            syndrome = syn_result['syndrome']
            syn_key = tuple(syndrome)

            if syn_key not in syndrome_table:
                return {
                    'success': False,
                    'error': 'Syndrome not in decoding table (uncorrectable error)'
                }

            error = syndrome_table[syn_key]

            # Correct: codeword = received - error
            if q == 2:
                codeword = [received[i] ^ error[i] for i in range(len(received))]
            else:
                codeword = [(received[i] - error[i]) % q for i in range(len(received))]

            self.syndrome_decodings += 1

            return {
                'success': True,
                'received': received,
                'syndrome': syndrome,
                'error_pattern': error,
                'codeword': codeword,
                'errors_corrected': hamming_weight(error),
                'method': 'syndrome_table_lookup'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def build_standard_array(
        self,
        G: List[List[int]],
        q: int = 2,
        max_size: int = 65536
    ) -> Dict[str, Any]:
        """
        Build standard array for syndrome decoding.

        Args:
            G: Generator matrix
            q: Field size
            max_size: Maximum array size

        Returns:
            Syndrome table mapping syndrome → coset leader
        """
        if not G or not G[0]:
            return {'success': False, 'error': 'Generator matrix cannot be empty'}

        k = len(G)
        n = len(G[0])
        num_codewords = q ** k
        num_cosets = q ** (n - k)

        if num_codewords > max_size or num_cosets > max_size:
            return {
                'success': False,
                'error': f'Code too large for standard array ({num_codewords}×{num_cosets})'
            }

        try:
            # Generate all codewords
            codewords = []
            for i in range(num_codewords):
                message = []
                temp = i
                for _ in range(k):
                    message.append(temp % q)
                    temp //= q

                # Encode
                cw = [0] * n
                for j in range(n):
                    for m_idx in range(k):
                        if q == 2:
                            cw[j] ^= message[m_idx] * G[m_idx][j]
                        else:
                            cw[j] = (cw[j] + message[m_idx] * G[m_idx][j]) % q
                codewords.append(cw)

            # Build parity check matrix
            H_result = self.construct_from_generator(G, q)
            if not H_result['success']:
                return H_result

            H = H_result['parity_check']

            # Build syndrome table
            # Start with all-zeros syndrome → zero error
            syndrome_table = {}
            used_vectors = set()

            for cw in codewords:
                used_vectors.add(tuple(cw))

            # Find coset leaders (minimum weight representatives)
            for w in range(n + 1):  # Weight 0, 1, 2, ...
                for error_int in range(q ** n):
                    # Convert to vector
                    error = []
                    temp = error_int
                    for _ in range(n):
                        error.append(temp % q)
                        temp //= q

                    if hamming_weight(error) != w:
                        continue

                    # Compute syndrome
                    syn_result = self.compute_syndrome(error, H, q)
                    syn_key = tuple(syn_result['syndrome'])

                    if syn_key not in syndrome_table:
                        syndrome_table[syn_key] = error

                if len(syndrome_table) == num_cosets:
                    break

            self.standard_arrays_built += 1

            return {
                'success': True,
                'syndrome_table': syndrome_table,
                'num_codewords': num_codewords,
                'num_cosets': num_cosets,
                'parity_check': H,
                'method': 'coset_enumeration'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def is_codeword(
        self,
        vector: List[int],
        H: List[List[int]],
        q: int = 2
    ) -> Dict[str, Any]:
        """
        Check if vector is a valid codeword.

        Args:
            vector: Vector to check
            H: Parity check matrix
            q: Field size

        Returns:
            True if vector is codeword (syndrome = 0)
        """
        try:
            syn_result = self.compute_syndrome(vector, H, q)
            if not syn_result['success']:
                return syn_result

            self.codeword_validations += 1

            return {
                'success': True,
                'is_codeword': syn_result['is_codeword'],
                'syndrome': syn_result['syndrome'],
                'method': 'syndrome_check'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def verify_orthogonality(
        self,
        G: List[List[int]],
        H: List[List[int]],
        q: int = 2
    ) -> Dict[str, Any]:
        """
        Verify G·H^T = 0 (orthogonality condition).

        Args:
            G: Generator matrix (k×n)
            H: Parity check matrix ((n-k)×n)
            q: Field size

        Returns:
            True if orthogonal
        """
        if not G or not H or not G[0] or not H[0]:
            return {'success': False, 'error': 'Matrices cannot be empty'}

        try:
            k = len(G)
            n = len(G[0])
            r = len(H)

            if len(H[0]) != n:
                return {'success': False, 'error': 'G and H must have same number of columns'}

            # Compute G·H^T (k×r matrix)
            product = [[0] * r for _ in range(k)]

            for i in range(k):
                for j in range(r):
                    for l in range(n):
                        if q == 2:
                            product[i][j] ^= G[i][l] * H[j][l]
                        else:
                            product[i][j] = (product[i][j] + G[i][l] * H[j][l]) % q

            is_orthogonal = all(all(c == 0 for c in row) for row in product)

            return {
                'success': True,
                'is_orthogonal': is_orthogonal,
                'product': product,
                'method': 'matrix_multiplication'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ========================================
    # Task Processing
    # ========================================

    def process(self, task_entry: Any) -> Any:
        """Process parity check task."""
        self.tasks_executed += 1

        try:
            if hasattr(task_entry, 'metadata'):
                metadata = task_entry.metadata or {}
            elif isinstance(task_entry, dict):
                metadata = task_entry
            else:
                metadata = {'operation': str(task_entry)}

            operation = metadata.get('operation', 'syndrome')
            G = metadata.get('generator') or metadata.get('G')
            H = metadata.get('parity_check') or metadata.get('H')
            received = metadata.get('received') or metadata.get('r')
            vector = metadata.get('vector') or metadata.get('v')
            syndrome_table = metadata.get('syndrome_table')
            q = metadata.get('q', 2)

            if operation in ['construct', 'construct_from_generator']:
                result = self.construct_from_generator(G, q)
            elif operation in ['syndrome', 'compute_syndrome']:
                result = self.compute_syndrome(received, H, q)
            elif operation in ['decode', 'syndrome_decode']:
                result = self.syndrome_decode(received, H, syndrome_table, q)
            elif operation in ['standard_array', 'build_array']:
                result = self.build_standard_array(G, q)
            elif operation in ['is_codeword', 'validate']:
                result = self.is_codeword(vector or received, H, q)
            elif operation in ['orthogonality', 'verify_orthogonality']:
                result = self.verify_orthogonality(G, H, q)
            else:
                if received is not None and H is not None:
                    result = self.compute_syndrome(received, H, q)
                elif G is not None:
                    result = self.construct_from_generator(G, q)
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
                    ['error_correction', 'parity_check', 'syndrome'],
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
        """PERCEIVE: Monitor blackboard for parity check tasks."""
        if not self.blackboard:
            return

        entries = self.blackboard.query_entries(
            tags=['parity_check', 'syndrome', 'decoding'],
            status=EntryStatus.PENDING
        )

        for entry in entries:
            belief_key = f'pending_parity_{entry.entry_id}'
            if not self.has_belief(belief_key):
                self.add_belief(belief_key, entry, confidence=1.0, source='blackboard')

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create plans from beliefs."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_parity_'):
                continue

            task = belief.content
            task_id = task.entry_id if hasattr(task, 'entry_id') else str(task)

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            intention = Intention(
                goal=f'solve_parity_{task_id}',
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
            'parity_matrices_constructed': self.parity_matrices_constructed,
            'syndromes_computed': self.syndromes_computed,
            'syndrome_decodings': self.syndrome_decodings,
            'standard_arrays_built': self.standard_arrays_built,
            'codeword_validations': self.codeword_validations,
        }
