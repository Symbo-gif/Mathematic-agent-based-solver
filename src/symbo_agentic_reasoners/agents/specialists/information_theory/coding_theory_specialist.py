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
CODING THEORY SPECIALIST (Tier 3)
=================================

Native Python implementation for coding theory computations.
Handles Huffman coding, error-correcting codes (Hamming, Reed-Solomon basics).

NO SYMPY - Pure native mathematical reasoning.
"""

import heapq
import logging
from typing import Dict, Any, List, Optional, Tuple
from collections import Counter
import numpy as np

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention

logger = logging.getLogger(__name__)


class HuffmanNode:
    """Node in a Huffman tree."""

    def __init__(self, symbol: Optional[str] = None, freq: float = 0.0):
        self.symbol = symbol
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

    def is_leaf(self) -> bool:
        """Verify is leaf holds for mathematical object.

        Returns:
        True if property holds, False otherwise

        Example:
        >>> specialist = HuffmanNode()
        >>> result = specialist.is_leaf()
        # Returns computed result

        """
        return self.symbol is not None


class CodingTheorySpecialist(BDIAgent):
    """
    Specialist for coding theory computations.

    Capabilities:
    - Huffman coding (encode/decode)
    - Average code length computation
    - Code efficiency analysis
    - Hamming codes (7,4) - single error correction
    - Parity check matrices
    - Syndrome decoding
    """

    def __init__(self, agent_id: str = 'coding_theory_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        if self.df:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
            self.df.register(create_service_registration(
                service_type='math.information_theory.coding',
                agent_id=agent_id,
                algorithm='native_coding_theory',
                cost='low',
                instance=self,
                tier='3',
                capabilities='huffman_hamming_parity_syndrome'
            ))

        logger.info(f"[{agent_id}] Coding Theory Specialist initialized")

    def update_beliefs(self):
        """PERCEIVE: Monitor blackboard for coding tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryStatus
            tasks = self.blackboard.query_entries(tags=['coding'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['huffman'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['hamming'], status=EntryStatus.PENDING)

            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(f'claimed_task_{task.entry_id}') and not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create coding computation plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'huffman_encode')

            steps = ['claim_task', 'compute_coding', 'post_result']
            intention = Intention(
                plan_id=f'coding_{operation}_{task_id}',
                steps=steps,
                target_desire='coding_computation',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)
        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Compute coding operations."""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')

        if action == 'claim_task':
            self.add_belief(f'claimed_task_{task.entry_id}', True, confidence=1.0)
            intention.advance()
        elif action == 'compute_coding':
            self._compute_coding(intention)
        elif action == 'post_result':
            self._post_result(intention)

    def _compute_coding(self, intention: Intention):
        """Compute the requested coding operation."""
        task = intention.metadata.get('task_entry')
        metadata = task.metadata if hasattr(task, 'metadata') else {}
        operation = metadata.get('operation', 'huffman_encode')

        try:
            if operation == 'huffman_build':
                symbols = metadata.get('symbols', [])
                frequencies = metadata.get('frequencies', [])
                result = self.build_huffman_code(symbols, frequencies)
            elif operation == 'huffman_encode':
                message = metadata.get('message', '')
                code_table = metadata.get('code_table', None)
                result = self.huffman_encode(message, code_table)
            elif operation == 'huffman_decode':
                encoded = metadata.get('encoded', '')
                code_table = metadata.get('code_table', {})
                result = self.huffman_decode(encoded, code_table)
            elif operation == 'average_code_length':
                code_table = metadata.get('code_table', {})
                frequencies = metadata.get('frequencies', {})
                result = self.average_code_length(code_table, frequencies)
            elif operation == 'hamming_encode':
                data_bits = metadata.get('data_bits', [])
                result = self.hamming_encode_74(data_bits)
            elif operation == 'hamming_decode':
                received = metadata.get('received', [])
                result = self.hamming_decode_74(received)
            elif operation == 'parity_matrix':
                n = metadata.get('n', 7)
                k = metadata.get('k', 4)
                result = self.generate_parity_check_matrix(n, k)
            else:
                result = {'error': f'Unknown operation: {operation}'}

            intention.metadata['result'] = result
            self.tasks_executed += 1
            intention.advance()

        except Exception as e:
            logger.error(f"[{self.agent_id}] Coding computation failed: {e}")
            intention.metadata['result'] = {'error': str(e)}
            intention.advance()

    def _post_result(self, intention: Intention):
        """Post result to blackboard."""
        if self.blackboard:
            from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
            task = intention.metadata.get('task_entry')
            result = intention.metadata.get('result', {})

            result_entry = create_entry(
                content=result,
                entry_type=EntryType.RESULT,
                tags=['coding', 'result'],
                metadata={'source_task': task.entry_id, 'agent': self.agent_id}
            )
            self.blackboard.post_entry(result_entry)
            self.blackboard.update_entry_status(task.entry_id, EntryStatus.COMPLETED)

        intention.mark_completed()

    # =========================================================================
    # HUFFMAN CODING
    # =========================================================================

    @staticmethod
    def build_huffman_code(symbols: List[str], frequencies: List[float]) -> Dict[str, Any]:
        """
        Build a Huffman code from symbols and their frequencies.

        Args:
            symbols: List of symbols
            frequencies: Corresponding frequencies/probabilities

        Returns:
            Dictionary with code table and tree structure
        """
        if len(symbols) != len(frequencies):
            return {'error': 'Symbols and frequencies must have same length'}

        if len(symbols) == 0:
            return {'error': 'Empty symbol list'}

        if len(symbols) == 1:
            return {
                'code_table': {symbols[0]: '0'},
                'method': 'native_huffman'
            }

        # Build heap of leaf nodes
        heap = [HuffmanNode(s, f) for s, f in zip(symbols, frequencies)]
        heapq.heapify(heap)

        # Build tree
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)

            internal = HuffmanNode(freq=left.freq + right.freq)
            internal.left = left
            internal.right = right

            heapq.heappush(heap, internal)

        root = heap[0]

        # Generate codes
        code_table = {}

        def generate_codes(node: HuffmanNode, prefix: str = ''):
            """Perform generate codes operation.

            Args:
            node: Description needed
            prefix: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.generate_codes(...)
            """
            if node.is_leaf():
                code_table[node.symbol] = prefix if prefix else '0'
            else:
                if node.left:
                    generate_codes(node.left, prefix + '0')
                if node.right:
                    generate_codes(node.right, prefix + '1')

        generate_codes(root)

        # Compute average code length
        total_freq = sum(frequencies)
        avg_length = sum(
            (f / total_freq) * len(code_table[s])
            for s, f in zip(symbols, frequencies)
        )

        return {
            'code_table': code_table,
            'average_length': avg_length,
            'num_symbols': len(symbols),
            'method': 'native_huffman'
        }

    @staticmethod
    def huffman_encode(message: str, code_table: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Encode a message using Huffman coding.

        Args:
            message: String to encode
            code_table: Pre-built code table (if None, builds from message)

        Returns:
            Dictionary with encoded string and statistics
        """
        if code_table is None:
            # Build code from message frequencies
            freq = Counter(message)
            symbols = list(freq.keys())
            frequencies = list(freq.values())
            result = CodingTheorySpecialist.build_huffman_code(symbols, frequencies)
            if 'error' in result:
                return result
            code_table = result['code_table']

        try:
            encoded = ''.join(code_table[char] for char in message)
            compression_ratio = len(encoded) / (len(message) * 8) if message else 0

            return {
                'encoded': encoded,
                'original_length': len(message) * 8,
                'encoded_length': len(encoded),
                'compression_ratio': compression_ratio,
                'code_table': code_table,
                'method': 'native_huffman_encode'
            }
        except KeyError as e:
            return {'error': f'Symbol not in code table: {e}'}

    @staticmethod
    def huffman_decode(encoded: str, code_table: Dict[str, str]) -> Dict[str, Any]:
        """
        Decode a Huffman-encoded string.

        Args:
            encoded: Binary string to decode
            code_table: Code table (symbol -> code)

        Returns:
            Dictionary with decoded message
        """
        # Reverse code table
        reverse_table = {code: symbol for symbol, code in code_table.items()}

        decoded = []
        current_code = ''

        for bit in encoded:
            current_code += bit
            if current_code in reverse_table:
                decoded.append(reverse_table[current_code])
                current_code = ''

        if current_code:
            return {'error': f'Invalid encoded string, leftover bits: {current_code}'}

        return {
            'decoded': ''.join(decoded),
            'method': 'native_huffman_decode'
        }

    @staticmethod
    def average_code_length(code_table: Dict[str, str], frequencies: Dict[str, float]) -> Dict[str, Any]:
        """
        Compute average code length for a given code.

        Args:
            code_table: Symbol to code mapping
            frequencies: Symbol to frequency/probability mapping

        Returns:
            Dictionary with average length and efficiency metrics
        """
        total_freq = sum(frequencies.values())

        avg_length = sum(
            (frequencies.get(s, 0) / total_freq) * len(code)
            for s, code in code_table.items()
        )

        # Compute entropy for efficiency calculation
        probs = [f / total_freq for f in frequencies.values() if f > 0]
        entropy = -sum(p * np.log2(p) for p in probs)

        efficiency = entropy / avg_length if avg_length > 0 else 0

        return {
            'average_length': avg_length,
            'entropy': entropy,
            'efficiency': efficiency,
            'redundancy': avg_length - entropy,
            'method': 'native_code_length'
        }

    # =========================================================================
    # HAMMING CODES
    # =========================================================================

    @staticmethod
    def hamming_encode_74(data_bits: List[int]) -> Dict[str, Any]:
        """
        Encode 4 data bits using Hamming(7,4) code.

        Hamming(7,4) can detect and correct single-bit errors.

        Args:
            data_bits: 4 data bits [d1, d2, d3, d4]

        Returns:
            Dictionary with 7-bit codeword
        """
        if len(data_bits) != 4:
            return {'error': 'Hamming(7,4) requires exactly 4 data bits'}

        d = [int(b) % 2 for b in data_bits]

        # Generator matrix for Hamming(7,4)
        # Data positions: 3, 5, 6, 7 (1-indexed)
        # Parity positions: 1, 2, 4

        # Parity bits
        p1 = d[0] ^ d[1] ^ d[3]  # covers positions 1, 3, 5, 7
        p2 = d[0] ^ d[2] ^ d[3]  # covers positions 2, 3, 6, 7
        p4 = d[1] ^ d[2] ^ d[3]  # covers positions 4, 5, 6, 7

        # Codeword: [p1, p2, d1, p4, d2, d3, d4]
        codeword = [p1, p2, d[0], p4, d[1], d[2], d[3]]

        return {
            'codeword': codeword,
            'data_bits': d,
            'parity_bits': [p1, p2, p4],
            'code_rate': 4/7,
            'method': 'native_hamming_74'
        }

    @staticmethod
    def hamming_decode_74(received: List[int]) -> Dict[str, Any]:
        """
        Decode and correct errors in Hamming(7,4) codeword.

        Args:
            received: 7-bit received codeword (may contain errors)

        Returns:
            Dictionary with corrected data and error info
        """
        if len(received) != 7:
            return {'error': 'Hamming(7,4) requires exactly 7 bits'}

        r = [int(b) % 2 for b in received]

        # Compute syndrome
        s1 = r[0] ^ r[2] ^ r[4] ^ r[6]  # positions 1, 3, 5, 7
        s2 = r[1] ^ r[2] ^ r[5] ^ r[6]  # positions 2, 3, 6, 7
        s4 = r[3] ^ r[4] ^ r[5] ^ r[6]  # positions 4, 5, 6, 7

        syndrome = s1 + 2 * s2 + 4 * s4
        error_position = syndrome  # 1-indexed (0 means no error)

        corrected = r.copy()
        error_detected = syndrome != 0

        if error_detected:
            # Flip the error bit (convert to 0-indexed)
            corrected[error_position - 1] ^= 1

        # Extract data bits (positions 3, 5, 6, 7 -> indices 2, 4, 5, 6)
        data_bits = [corrected[2], corrected[4], corrected[5], corrected[6]]

        return {
            'data_bits': data_bits,
            'corrected_codeword': corrected,
            'received': r,
            'syndrome': syndrome,
            'error_detected': error_detected,
            'error_position': error_position if error_detected else None,
            'method': 'native_hamming_74_decode'
        }

    @staticmethod
    def generate_parity_check_matrix(n: int = 7, k: int = 4) -> Dict[str, Any]:
        """
        Generate parity check matrix H for Hamming code.

        Args:
            n: Code length (default 7)
            k: Data bits (default 4)

        Returns:
            Dictionary with parity check matrix
        """
        if n != 7 or k != 4:
            return {'error': 'Currently only Hamming(7,4) is supported'}

        # Parity check matrix for Hamming(7,4)
        # Columns are binary representations of 1 to 7
        H = np.array([
            [1, 0, 1, 0, 1, 0, 1],  # s1
            [0, 1, 1, 0, 0, 1, 1],  # s2
            [0, 0, 0, 1, 1, 1, 1],  # s4
        ], dtype=int)

        return {
            'parity_check_matrix': H.tolist(),
            'n': n,
            'k': k,
            'r': n - k,  # redundancy
            'method': 'native_parity_matrix'
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Return agent statistics."""
        return {
            'agent_id': self.agent_id,
            'tasks_executed': self.tasks_executed,
            'capabilities': [
                'huffman_build', 'huffman_encode', 'huffman_decode',
                'hamming_encode_74', 'hamming_decode_74', 'parity_matrix'
            ]
        }
