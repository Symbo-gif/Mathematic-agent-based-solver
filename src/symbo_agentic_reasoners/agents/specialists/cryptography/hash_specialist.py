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
HASH SPECIALIST (Tier 3)
========================

Native Python implementation for hash function computations.
Educational implementations showing hash function principles.

NO SYMPY - Pure native mathematical reasoning.
"""

import logging
import struct
from typing import Dict, Any, List, Optional

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention

logger = logging.getLogger(__name__)


class HashSpecialist(BDIAgent):
    """
    Specialist for hash function computations.

    EDUCATIONAL USE - demonstrates hash principles.

    Capabilities:
    - Simple hash functions (for demonstration)
    - Merkle tree construction
    - Hash chain verification
    - Birthday attack analysis
    - Hash collision analysis
    """

    def __init__(self, agent_id: str = 'hash_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        if self.df:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
            self.df.register(create_service_registration(
                service_type='math.cryptography.hash',
                agent_id=agent_id,
                algorithm='native_hash',
                cost='low',
                instance=self,
                tier='3',
                capabilities='hash_merkle_chain_analysis'
            ))

        logger.info(f"[{agent_id}] Hash Specialist initialized")

    def update_beliefs(self):
        """PERCEIVE: Monitor blackboard for hash tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryStatus
            tasks = self.blackboard.query_entries(tags=['hash'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['merkle'], status=EntryStatus.PENDING)

            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(f'claimed_task_{task.entry_id}') and not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create hash computation plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'simple_hash')

            steps = ['claim_task', 'compute_hash', 'post_result']
            intention = Intention(
                plan_id=f'hash_{operation}_{task_id}',
                steps=steps,
                target_desire='hash_computation',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)
        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Compute hash operations."""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')

        if action == 'claim_task':
            self.add_belief(f'claimed_task_{task.entry_id}', True, confidence=1.0)
            intention.advance()
        elif action == 'compute_hash':
            self._compute_hash(intention)
        elif action == 'post_result':
            self._post_result(intention)

    def _compute_hash(self, intention: Intention):
        """Compute the requested hash operation."""
        task = intention.metadata.get('task_entry')
        metadata = task.metadata if hasattr(task, 'metadata') else {}
        operation = metadata.get('operation', 'simple_hash')

        try:
            if operation == 'simple_hash':
                data = metadata.get('data', '')
                bits = metadata.get('bits', 32)
                result = self.simple_hash(data, bits)
            elif operation == 'djb2_hash':
                data = metadata.get('data', '')
                result = self.djb2_hash(data)
            elif operation == 'fnv1a_hash':
                data = metadata.get('data', '')
                result = self.fnv1a_hash(data)
            elif operation == 'merkle_root':
                leaves = metadata.get('leaves', [])
                result = self.merkle_root(leaves)
            elif operation == 'merkle_proof':
                leaves = metadata.get('leaves', [])
                index = metadata.get('index', 0)
                result = self.merkle_proof(leaves, index)
            elif operation == 'verify_merkle_proof':
                leaf = metadata.get('leaf', '')
                proof = metadata.get('proof', [])
                root = metadata.get('root', 0)
                index = metadata.get('index', 0)
                result = self.verify_merkle_proof(leaf, proof, root, index)
            elif operation == 'hash_chain':
                seed = metadata.get('seed', '')
                length = metadata.get('length', 10)
                result = self.hash_chain(seed, length)
            elif operation == 'birthday_probability':
                hash_bits = metadata.get('hash_bits', 32)
                samples = metadata.get('samples', 1000)
                result = self.birthday_collision_probability(hash_bits, samples)
            else:
                result = {'error': f'Unknown operation: {operation}'}

            intention.metadata['result'] = result
            self.tasks_executed += 1
            intention.advance()

        except Exception as e:
            logger.error(f"[{self.agent_id}] Hash computation failed: {e}")
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
                tags=['hash', 'result'],
                metadata={'source_task': task.entry_id, 'agent': self.agent_id}
            )
            self.blackboard.post_entry(result_entry)
            self.blackboard.update_entry_status(task.entry_id, EntryStatus.COMPLETED)

        intention.mark_completed()

    # =========================================================================
    # SIMPLE HASH FUNCTIONS
    # =========================================================================

    @staticmethod
    def simple_hash(data: str, bits: int = 32) -> Dict[str, Any]:
        """
        Simple polynomial rolling hash.

        Args:
            data: String to hash
            bits: Output bit size

        Returns:
            Dictionary with hash value
        """
        if bits < 1 or bits > 64:
            return {'error': 'Bits must be between 1 and 64'}

        prime = 31
        mod = (1 << bits)

        h = 0
        for char in data:
            h = (h * prime + ord(char)) % mod

        return {
            'hash': h,
            'hex': hex(h),
            'bits': bits,
            'method': 'simple_polynomial_hash'
        }

    @staticmethod
    def djb2_hash(data: str) -> Dict[str, Any]:
        """
        DJB2 hash function (Dan Bernstein).

        Args:
            data: String to hash

        Returns:
            Dictionary with hash value
        """
        h = 5381
        for char in data:
            h = ((h << 5) + h) + ord(char)  # h * 33 + c
            h = h & 0xFFFFFFFF  # 32-bit

        return {
            'hash': h,
            'hex': hex(h),
            'method': 'djb2'
        }

    @staticmethod
    def fnv1a_hash(data: str) -> Dict[str, Any]:
        """
        FNV-1a hash function (Fowler-Noll-Vo).

        Args:
            data: String to hash

        Returns:
            Dictionary with hash value
        """
        # FNV-1a 32-bit parameters
        FNV_PRIME = 0x01000193
        FNV_OFFSET = 0x811c9dc5

        h = FNV_OFFSET
        for char in data:
            h ^= ord(char)
            h = (h * FNV_PRIME) & 0xFFFFFFFF

        return {
            'hash': h,
            'hex': hex(h),
            'method': 'fnv1a_32'
        }

    # =========================================================================
    # MERKLE TREE
    # =========================================================================

    def merkle_root(self, leaves: List[str]) -> Dict[str, Any]:
        """
        Compute Merkle tree root.

        Args:
            leaves: List of leaf values (strings)

        Returns:
            Dictionary with root hash
        """
        if not leaves:
            return {'error': 'Empty leaf list'}

        # Hash all leaves
        current_level = []
        for leaf in leaves:
            result = self.djb2_hash(leaf)
            current_level.append(result['hash'])

        # Build tree upward
        levels = [current_level.copy()]

        while len(current_level) > 1:
            next_level = []

            # Pad if odd number
            if len(current_level) % 2 == 1:
                current_level.append(current_level[-1])

            for i in range(0, len(current_level), 2):
                # Combine two hashes
                combined = str(current_level[i]) + str(current_level[i + 1])
                result = self.djb2_hash(combined)
                next_level.append(result['hash'])

            current_level = next_level
            levels.append(current_level.copy())

        return {
            'root': current_level[0],
            'root_hex': hex(current_level[0]),
            'num_leaves': len(leaves),
            'tree_height': len(levels),
            'method': 'native_merkle_tree'
        }

    def merkle_proof(self, leaves: List[str], index: int) -> Dict[str, Any]:
        """
        Generate Merkle proof for a leaf.

        Args:
            leaves: List of leaf values
            index: Index of leaf to prove

        Returns:
            Dictionary with proof path
        """
        if not leaves:
            return {'error': 'Empty leaf list'}
        if index < 0 or index >= len(leaves):
            return {'error': f'Index {index} out of range'}

        # Hash all leaves
        current_level = []
        for leaf in leaves:
            result = self.djb2_hash(leaf)
            current_level.append(result['hash'])

        proof = []
        current_index = index

        while len(current_level) > 1:
            # Pad if odd
            if len(current_level) % 2 == 1:
                current_level.append(current_level[-1])

            # Get sibling
            if current_index % 2 == 0:
                sibling_index = current_index + 1
                direction = 'right'
            else:
                sibling_index = current_index - 1
                direction = 'left'

            proof.append({
                'hash': current_level[sibling_index],
                'direction': direction
            })

            # Build next level
            next_level = []
            for i in range(0, len(current_level), 2):
                combined = str(current_level[i]) + str(current_level[i + 1])
                result = self.djb2_hash(combined)
                next_level.append(result['hash'])

            current_level = next_level
            current_index //= 2

        return {
            'leaf': leaves[index],
            'index': index,
            'proof': proof,
            'root': current_level[0],
            'method': 'native_merkle_proof'
        }

    def verify_merkle_proof(self, leaf: str, proof: List[Dict], root: int, index: int) -> Dict[str, Any]:
        """
        Verify a Merkle proof.

        Args:
            leaf: Leaf value
            proof: Proof path
            root: Expected root hash
            index: Leaf index

        Returns:
            Dictionary with verification result
        """
        result = self.djb2_hash(leaf)
        current = result['hash']

        for step in proof:
            sibling = step['hash']
            direction = step['direction']

            if direction == 'right':
                combined = str(current) + str(sibling)
            else:
                combined = str(sibling) + str(current)

            result = self.djb2_hash(combined)
            current = result['hash']

        return {
            'valid': current == root,
            'computed_root': current,
            'expected_root': root,
            'method': 'native_merkle_verify'
        }

    # =========================================================================
    # HASH CHAIN
    # =========================================================================

    def hash_chain(self, seed: str, length: int) -> Dict[str, Any]:
        """
        Generate hash chain.

        Args:
            seed: Initial value
            length: Chain length

        Returns:
            Dictionary with chain
        """
        if length < 1:
            return {'error': 'Length must be at least 1'}
        if length > 1000:
            return {'error': 'Length capped at 1000'}

        chain = []
        current = seed

        for i in range(length):
            result = self.djb2_hash(current)
            chain.append({
                'index': i,
                'value': result['hash'],
                'hex': result['hex']
            })
            current = str(result['hash'])

        return {
            'chain': chain,
            'seed': seed,
            'length': length,
            'final': chain[-1],
            'method': 'native_hash_chain'
        }

    # =========================================================================
    # COLLISION ANALYSIS
    # =========================================================================

    @staticmethod
    def birthday_collision_probability(hash_bits: int, samples: int) -> Dict[str, Any]:
        """
        Compute birthday attack collision probability.

        P(collision) ≈ 1 - exp(-n^2 / (2 * 2^bits))

        Args:
            hash_bits: Number of bits in hash output
            samples: Number of hash samples

        Returns:
            Dictionary with probability analysis
        """
        import math

        if hash_bits < 1 or hash_bits > 256:
            return {'error': 'Hash bits must be between 1 and 256'}

        hash_space = 2 ** hash_bits

        # Exact formula for small values
        if samples <= 1:
            exact_prob = 0.0
        elif samples > hash_space:
            exact_prob = 1.0
        else:
            # Use approximation: 1 - exp(-n^2 / (2H))
            approx_prob = 1 - math.exp(-samples * samples / (2 * hash_space))
            exact_prob = approx_prob

        # 50% collision threshold (birthday bound)
        birthday_bound = math.sqrt(2 * hash_space * math.log(2))

        return {
            'collision_probability': exact_prob,
            'hash_bits': hash_bits,
            'hash_space': hash_space,
            'samples': samples,
            'birthday_bound': int(birthday_bound),
            'note': f'~{int(birthday_bound)} samples for 50% collision chance',
            'method': 'birthday_attack_analysis'
        }

    @staticmethod
    def hash_distribution_analysis(hashes: List[int], bits: int = 32) -> Dict[str, Any]:
        """
        Analyze hash distribution for uniformity.

        Args:
            hashes: List of hash values
            bits: Expected bit size

        Returns:
            Dictionary with distribution metrics
        """
        if not hashes:
            return {'error': 'Empty hash list'}

        import math

        n = len(hashes)
        max_val = 2 ** bits

        # Check for collisions
        unique = len(set(hashes))
        collision_rate = 1 - (unique / n)

        # Check bit distribution
        bit_counts = [0] * bits
        for h in hashes:
            for b in range(bits):
                if h & (1 << b):
                    bit_counts[b] += 1

        # Chi-squared for uniformity (simplified)
        expected_per_bit = n / 2
        chi_squared = sum((c - expected_per_bit) ** 2 / expected_per_bit for c in bit_counts)

        return {
            'total_hashes': n,
            'unique_hashes': unique,
            'collision_rate': collision_rate,
            'bit_distribution': bit_counts,
            'chi_squared': chi_squared,
            'uniformity': 'good' if chi_squared < 2 * bits else 'poor',
            'method': 'hash_distribution_analysis'
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Return agent statistics."""
        return {
            'agent_id': self.agent_id,
            'tasks_executed': self.tasks_executed,
            'capabilities': [
                'simple_hash', 'djb2_hash', 'fnv1a_hash',
                'merkle_root', 'merkle_proof', 'verify_merkle_proof',
                'hash_chain', 'birthday_probability'
            ]
        }
