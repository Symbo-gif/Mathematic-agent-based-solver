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
GENERATOR MATRIX SPECIALIST (Tier 3)
=====================================

Handles encoding operations via generator matrix.

CAPABILITIES:
------------
- encode: Compute codeword c = m·G from message m
- systematic_encode: Encode using systematic form [I_k | P]
- generate_all_codewords: Enumerate all 2^k codewords
- construct_generator: Build G from code parameters

FORMULATION:
-----------
Generator Matrix G (k×n):
- Rows form basis for code C
- Codeword c = m·G where m ∈ GF(q)^k
- Systematic form: G = [I_k | P] where P is k×(n-k) parity matrix

Encoding:
- Message m = (m_0, ..., m_{k-1})
- Codeword c = m·G = (c_0, ..., c_{n-1})
- For systematic: c = (m_0, ..., m_{k-1}, p_0, ..., p_{n-k-1})

ALGORITHMIC BACKING:
-------------------
Native GF(q) matrix-vector multiplication

NO SYMPY - Pure native mathematical reasoning.

REFERENCE:
---------
- Lin & Costello (2004), Chapter 3: Encoding with Generator Matrix
- MacWilliams & Sloane (1977), Chapter 1: Linear Codes
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
    gf2_matrix_multiply, gf2_rref
)

logger = logging.getLogger(__name__)


class GeneratorMatrixSpecialist(BDIAgent):
    """
    Generator Matrix Specialist - Encoding Operations

    DIRECTIVE:
    ---------
    Handle encoding of messages using generator matrices.

    OPERATIONS:
    ----------
    - encode: General encoding c = m·G
    - systematic_encode: Systematic form encoding
    - generate_all: Enumerate all codewords
    - construct: Build generator from parameters

    FORMULATION:
    -----------
    Linear code C = {m·G : m ∈ GF(q)^k}.
    Encoding is linear map GF(q)^k → GF(q)^n.

    REFERENCE:
    ---------
    - Lin & Costello (2004), Error Control Coding
    """

    def __init__(
        self,
        agent_id: str = 'generator_matrix_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Generator Matrix Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.encodings_performed = 0
        self.systematic_encodings = 0
        self.codewords_generated = 0
        self.generators_constructed = 0

        if self.df:
            self._register_services()

    def _register_services(self):
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            service_type='math.information_theory.error_correction.generator',
            agent_id=self.agent_id,
            algorithm='generator_encoding',
            cost='low',
            instance=self,
            type='specialist',
            tier='3',
            operations='encode_systematic_generate_construct'
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered as generator matrix specialist")

    # ========================================
    # Core Operations
    # ========================================

    def encode(
        self,
        message: List[int],
        G: List[List[int]],
        q: int = 2
    ) -> Dict[str, Any]:
        """
        Encode message using generator matrix: c = m·G.

        Args:
            message: Message vector m of length k
            G: Generator matrix (k×n)
            q: Field size

        Returns:
            Codeword c
        """
        if not G or not G[0]:
            return {'success': False, 'error': 'Generator matrix cannot be empty'}

        k = len(G)
        n = len(G[0])

        if len(message) != k:
            return {
                'success': False,
                'error': f'Message length {len(message)} must equal k={k}'
            }

        try:
            # Compute c = m·G
            if q == 2:
                # Binary: c[j] = XOR of m[i]*G[i][j]
                codeword = [0] * n
                for j in range(n):
                    for i in range(k):
                        codeword[j] ^= message[i] * G[i][j]
            else:
                # General GF(q)
                codeword = [0] * n
                for j in range(n):
                    for i in range(k):
                        codeword[j] = (codeword[j] + message[i] * G[i][j]) % q

            self.encodings_performed += 1

            return {
                'success': True,
                'message': message,
                'codeword': codeword,
                'k': k,
                'n': n,
                'method': 'matrix_vector_multiplication'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def systematic_encode(
        self,
        message: List[int],
        P: List[List[int]],
        q: int = 2
    ) -> Dict[str, Any]:
        """
        Encode using systematic form c = (m | m·P).

        For systematic G = [I_k | P], codeword is message concatenated with parity.

        Args:
            message: Message vector m
            P: Parity matrix (k × (n-k))
            q: Field size

        Returns:
            Systematic codeword (m, parity)
        """
        if not P or not P[0]:
            return {'success': False, 'error': 'Parity matrix cannot be empty'}

        k = len(P)
        r = len(P[0])  # n - k redundancy bits

        if len(message) != k:
            return {
                'success': False,
                'error': f'Message length {len(message)} must equal k={k}'
            }

        try:
            # Compute parity: p = m·P
            if q == 2:
                parity = [0] * r
                for j in range(r):
                    for i in range(k):
                        parity[j] ^= message[i] * P[i][j]
            else:
                parity = [0] * r
                for j in range(r):
                    for i in range(k):
                        parity[j] = (parity[j] + message[i] * P[i][j]) % q

            # Codeword = message concatenated with parity
            codeword = list(message) + parity

            self.systematic_encodings += 1

            return {
                'success': True,
                'message': message,
                'parity': parity,
                'codeword': codeword,
                'k': k,
                'n': k + r,
                'is_systematic': True,
                'method': 'systematic_encoding'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def generate_all_codewords(
        self,
        G: List[List[int]],
        q: int = 2,
        max_codewords: int = 65536
    ) -> Dict[str, Any]:
        """
        Generate all 2^k codewords by encoding all possible messages.

        Args:
            G: Generator matrix (k×n)
            q: Field size
            max_codewords: Maximum codewords to generate (security limit)

        Returns:
            List of all codewords
        """
        if not G or not G[0]:
            return {'success': False, 'error': 'Generator matrix cannot be empty'}

        k = len(G)
        n = len(G[0])
        num_codewords = q ** k

        if num_codewords > max_codewords:
            return {
                'success': False,
                'error': f'Too many codewords ({num_codewords} > {max_codewords})'
            }

        try:
            codewords = []

            # Generate all q^k messages
            for msg_int in range(num_codewords):
                # Convert integer to q-ary message
                message = []
                temp = msg_int
                for _ in range(k):
                    message.append(temp % q)
                    temp //= q

                # Encode
                result = self.encode(message, G, q)
                if result['success']:
                    codewords.append({
                        'message': message,
                        'codeword': result['codeword']
                    })

            self.codewords_generated += num_codewords

            return {
                'success': True,
                'codewords': codewords,
                'count': len(codewords),
                'k': k,
                'n': n,
                'q': q,
                'method': 'exhaustive_enumeration'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def construct_hamming_generator(self, r: int) -> Dict[str, Any]:
        """
        Construct generator matrix for Hamming code Ham(r, 2).

        Parameters: n = 2^r - 1, k = 2^r - r - 1, d = 3

        Args:
            r: Parity check bits (r >= 2)

        Returns:
            Generator matrix for Ham(r, 2)
        """
        if r < 2:
            return {'success': False, 'error': 'r must be >= 2 for Hamming code'}

        if r > 10:
            return {'success': False, 'error': 'r too large (max 10)'}

        try:
            n = (1 << r) - 1  # 2^r - 1
            k = n - r

            # Build parity check matrix H first (r × n)
            # Columns are all non-zero r-bit vectors
            H = []
            for row in range(r):
                H.append([0] * n)

            col = 0
            for j in range(1, n + 1):
                for i in range(r):
                    H[i][col] = (j >> i) & 1
                col += 1

            # Rearrange to systematic form [P^T | I_r]
            # Then G = [I_k | P]
            H_sys, _ = gf2_rref(H)

            # Extract P from H = [P^T | I_r]
            P = [[H_sys[j][i] for j in range(r)] for i in range(k)]

            # Build G = [I_k | P]
            G = []
            for i in range(k):
                row = [0] * n
                row[i] = 1  # Identity part
                for j in range(r):
                    row[k + j] = P[i][j]  # Parity part
                G.append(row)

            self.generators_constructed += 1

            return {
                'success': True,
                'generator': G,
                'parity_matrix': P,
                'n': n,
                'k': k,
                'd': 3,
                'r': r,
                'code': f'Ham({r}, 2)',
                'method': 'hamming_construction'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def extract_parity_matrix(
        self,
        G: List[List[int]],
        q: int = 2
    ) -> Dict[str, Any]:
        """
        Extract parity matrix P from systematic generator [I_k | P].

        Args:
            G: Generator matrix (must be systematic)
            q: Field size

        Returns:
            Parity matrix P
        """
        if not G or not G[0]:
            return {'success': False, 'error': 'Generator matrix cannot be empty'}

        try:
            k = len(G)
            n = len(G[0])

            # Verify systematic form
            for i in range(k):
                for j in range(k):
                    expected = 1 if i == j else 0
                    if G[i][j] != expected:
                        return {
                            'success': False,
                            'error': 'Generator matrix is not in systematic form'
                        }

            # Extract P (columns k to n-1)
            P = [row[k:] for row in G]

            return {
                'success': True,
                'parity_matrix': P,
                'k': k,
                'n': n,
                'redundancy': n - k,
                'method': 'column_extraction'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ========================================
    # Task Processing
    # ========================================

    def process(self, task_entry: Any) -> Any:
        """Process generator matrix task."""
        self.tasks_executed += 1

        try:
            if hasattr(task_entry, 'metadata'):
                metadata = task_entry.metadata or {}
            elif isinstance(task_entry, dict):
                metadata = task_entry
            else:
                metadata = {'operation': str(task_entry)}

            operation = metadata.get('operation', 'encode')
            message = metadata.get('message') or metadata.get('m')
            G = metadata.get('generator') or metadata.get('G')
            P = metadata.get('parity') or metadata.get('P')
            r = metadata.get('r')
            q = metadata.get('q', 2)

            if operation in ['encode', 'encoding']:
                result = self.encode(message, G, q)
            elif operation in ['systematic', 'systematic_encode']:
                result = self.systematic_encode(message, P, q)
            elif operation in ['generate_all', 'all_codewords', 'enumerate']:
                result = self.generate_all_codewords(G, q)
            elif operation in ['hamming', 'construct_hamming']:
                result = self.construct_hamming_generator(r)
            elif operation in ['extract_parity', 'get_parity']:
                result = self.extract_parity_matrix(G, q)
            else:
                if message is not None and G is not None:
                    result = self.encode(message, G, q)
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
                    ['error_correction', 'generator_matrix', 'encoding'],
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
        """PERCEIVE: Monitor blackboard for encoding tasks."""
        if not self.blackboard:
            return

        entries = self.blackboard.query_entries(
            tags=['generator_matrix', 'encoding', 'generator'],
            status=EntryStatus.PENDING
        )

        for entry in entries:
            belief_key = f'pending_gen_{entry.entry_id}'
            if not self.has_belief(belief_key):
                self.add_belief(belief_key, entry, confidence=1.0, source='blackboard')

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create plans from beliefs."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_gen_'):
                continue

            task = belief.content
            task_id = task.entry_id if hasattr(task, 'entry_id') else str(task)

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            intention = Intention(
                goal=f'solve_gen_{task_id}',
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
            'encodings_performed': self.encodings_performed,
            'systematic_encodings': self.systematic_encodings,
            'codewords_generated': self.codewords_generated,
            'generators_constructed': self.generators_constructed,
        }
