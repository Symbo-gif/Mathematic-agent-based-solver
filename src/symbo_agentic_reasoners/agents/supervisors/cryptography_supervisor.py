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
CRYPTOGRAPHY SUPERVISOR (Tier 2)
================================

Routes cryptography problems to appropriate specialists.
Never computes directly - only delegates to Tier 3 specialists.

EDUCATIONAL USE ONLY - Not for production security.
NO SYMPY - Pure native mathematical reasoning.
"""

import logging
from typing import Dict, Any, List, Optional

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention

logger = logging.getLogger(__name__)


class CryptographySupervisor(BDIAgent):
    """
    Supervisor for cryptography domain.

    Routes to:
    - ModularArithmeticSpecialist: Modular operations, primality
    - AsymmetricCryptoSpecialist: RSA, DH, ElGamal
    - HashSpecialist: Hash functions, Merkle trees

    This supervisor NEVER computes - only routes.
    """

    # Keywords for routing decisions
    MODULAR_KEYWORDS = [
        'modular', 'mod', 'inverse', 'gcd', 'crt', 'chinese remainder',
        'totient', 'euler', 'primitive root', 'discrete log', 'primality'
    ]

    ASYMMETRIC_KEYWORDS = [
        'rsa', 'diffie', 'hellman', 'elgamal', 'encrypt', 'decrypt',
        'sign', 'verify', 'key', 'public', 'private', 'asymmetric'
    ]

    HASH_KEYWORDS = [
        'hash', 'merkle', 'tree', 'chain', 'collision', 'birthday',
        'djb2', 'fnv', 'digest'
    ]

    def __init__(self, agent_id: str = 'cryptography_supervisor_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard

        # Lazy-loaded specialists
        self._modular_specialist = None
        self._asymmetric_specialist = None
        self._hash_specialist = None

        if self.df:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
            self.df.register(create_service_registration(
                service_type='math.cryptography',
                agent_id=agent_id,
                algorithm='router',
                cost='minimal',
                instance=self,
                tier='2',
                capabilities='modular_asymmetric_hash_routing'
            ))

        logger.info(f"[{agent_id}] Cryptography Supervisor initialized")

    @property
    def modular_specialist(self):
        """Lazy load modular arithmetic specialist."""
        if self._modular_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.cryptography import ModularArithmeticSpecialist
            self._modular_specialist = ModularArithmeticSpecialist(
                agent_id='modular_arithmetic_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._modular_specialist

    @property
    def asymmetric_specialist(self):
        """Lazy load asymmetric crypto specialist."""
        if self._asymmetric_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.cryptography import AsymmetricCryptoSpecialist
            self._asymmetric_specialist = AsymmetricCryptoSpecialist(
                agent_id='asymmetric_crypto_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._asymmetric_specialist

    @property
    def hash_specialist(self):
        """Lazy load hash specialist."""
        if self._hash_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.cryptography import HashSpecialist
            self._hash_specialist = HashSpecialist(
                agent_id='hash_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._hash_specialist

    def update_beliefs(self):
        """PERCEIVE: Monitor for cryptography tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryStatus
            tasks = self.blackboard.query_entries(tags=['cryptography'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['crypto'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['rsa'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['hash'], status=EntryStatus.PENDING)

            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(f'routed_task_{task.entry_id}') and not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create routing plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            target_specialist = self._determine_specialist(task)

            steps = ['route_task']
            intention = Intention(
                plan_id=f'route_crypto_{task_id}',
                steps=steps,
                target_desire='cryptography_routing',
                metadata={'task_id': task_id, 'task_entry': task, 'target': target_specialist}
            )
            new_intentions.append(intention)
        return new_intentions

    def _determine_specialist(self, task) -> str:
        """Determine which specialist should handle this task."""
        metadata = task.metadata if hasattr(task, 'metadata') else {}
        content = str(task.content).lower() if hasattr(task, 'content') else ''
        operation = metadata.get('operation', '').lower()

        combined_text = f"{content} {operation}"

        # Check explicit operation mappings
        modular_ops = ['mod_exp', 'mod_inverse', 'extended_gcd', 'crt', 'primitive_root',
                       'discrete_log', 'is_prime', 'euler_totient']
        asymmetric_ops = ['rsa_keygen', 'rsa_encrypt', 'rsa_decrypt', 'rsa_sign', 'rsa_verify',
                         'dh_keygen', 'dh_shared_secret', 'elgamal_keygen', 'elgamal_encrypt',
                         'elgamal_decrypt']
        hash_ops = ['simple_hash', 'djb2_hash', 'fnv1a_hash', 'merkle_root', 'merkle_proof',
                    'verify_merkle_proof', 'hash_chain', 'birthday_probability']

        if operation in modular_ops:
            return 'modular'
        if operation in asymmetric_ops:
            return 'asymmetric'
        if operation in hash_ops:
            return 'hash'

        # Check keywords
        modular_score = sum(1 for kw in self.MODULAR_KEYWORDS if kw in combined_text)
        asymmetric_score = sum(1 for kw in self.ASYMMETRIC_KEYWORDS if kw in combined_text)
        hash_score = sum(1 for kw in self.HASH_KEYWORDS if kw in combined_text)

        scores = {
            'modular': modular_score,
            'asymmetric': asymmetric_score,
            'hash': hash_score
        }

        return max(scores, key=scores.get) if max(scores.values()) > 0 else 'modular'

    def execute_step(self, intention: Intention):
        """EXECUTE: Route to appropriate specialist."""
        action = intention.get_current_action()

        if action == 'route_task':
            task = intention.metadata.get('task_entry')
            target = intention.metadata.get('target', 'modular')

            self.add_belief(f'routed_task_{task.entry_id}', True, confidence=1.0)

            if target == 'modular':
                specialist = self.modular_specialist
            elif target == 'asymmetric':
                specialist = self.asymmetric_specialist
            else:
                specialist = self.hash_specialist

            logger.info(f"[{self.agent_id}] Routing task {task.entry_id} to {target} specialist")

            specialist.update_beliefs()
            new_intentions = specialist.deliberate()
            for new_intention in new_intentions:
                specialist.intentions.append(new_intention)

            intention.mark_completed()

    def solve(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """
        Direct solve interface for cryptography problems.

        Args:
            problem: Dictionary with 'type' and relevant parameters

        Returns:
            Solution dictionary
        """
        problem_type = problem.get('type', '').lower()

        # Modular arithmetic operations
        if problem_type == 'mod_exp':
            return self.modular_specialist.modular_exponentiation(
                problem.get('base', 2),
                problem.get('exponent', 10),
                problem.get('modulus', 1000)
            )
        if problem_type == 'mod_inverse':
            return self.modular_specialist.modular_inverse(
                problem.get('a', 3),
                problem.get('modulus', 11)
            )
        if problem_type == 'extended_gcd':
            return self.modular_specialist.extended_gcd(
                problem.get('a', 0),
                problem.get('b', 0)
            )
        if problem_type == 'crt':
            return self.modular_specialist.chinese_remainder_theorem(
                problem.get('remainders', []),
                problem.get('moduli', [])
            )
        if problem_type == 'is_prime':
            return self.modular_specialist.is_prime_miller_rabin(
                problem.get('n', 17)
            )
        if problem_type == 'euler_totient':
            return self.modular_specialist.euler_totient(
                problem.get('n', 12)
            )
        if problem_type == 'primitive_root':
            return self.modular_specialist.find_primitive_root(
                problem.get('prime', 7)
            )
        if problem_type == 'discrete_log':
            return self.modular_specialist.discrete_logarithm_bsgs(
                problem.get('base', 2),
                problem.get('value', 8),
                problem.get('modulus', 11)
            )

        # RSA operations
        if problem_type == 'rsa_keygen':
            return self.asymmetric_specialist.rsa_keygen(
                problem.get('bits', 32)
            )
        if problem_type == 'rsa_encrypt':
            return self.asymmetric_specialist.rsa_encrypt(
                problem.get('message', 0),
                problem.get('e', 65537),
                problem.get('n', 0)
            )
        if problem_type == 'rsa_decrypt':
            return self.asymmetric_specialist.rsa_decrypt(
                problem.get('ciphertext', 0),
                problem.get('d', 0),
                problem.get('n', 0)
            )

        # DH operations
        if problem_type == 'dh_keygen':
            return self.asymmetric_specialist.diffie_hellman_keygen(
                problem.get('p', 0),
                problem.get('g', 0)
            )
        if problem_type == 'dh_shared_secret':
            return self.asymmetric_specialist.diffie_hellman_shared_secret(
                problem.get('private', 0),
                problem.get('other_public', 0),
                problem.get('p', 0)
            )

        # Hash operations
        if problem_type == 'hash' or problem_type == 'simple_hash':
            return self.hash_specialist.simple_hash(
                problem.get('data', ''),
                problem.get('bits', 32)
            )
        if problem_type == 'djb2':
            return self.hash_specialist.djb2_hash(
                problem.get('data', '')
            )
        if problem_type == 'merkle_root':
            return self.hash_specialist.merkle_root(
                problem.get('leaves', [])
            )
        if problem_type == 'birthday_probability':
            return self.hash_specialist.birthday_collision_probability(
                problem.get('hash_bits', 32),
                problem.get('samples', 1000)
            )

        return {'error': f'Unknown problem type: {problem_type}'}

    def get_statistics(self) -> Dict[str, Any]:
        """Return supervisor statistics."""
        stats = {
            'agent_id': self.agent_id,
            'tier': 2,
            'role': 'supervisor',
            'specialists': ['modular', 'asymmetric', 'hash'],
            'warning': 'EDUCATIONAL IMPLEMENTATIONS ONLY'
        }

        if self._modular_specialist:
            stats['modular_tasks'] = self._modular_specialist.tasks_executed
        if self._asymmetric_specialist:
            stats['asymmetric_tasks'] = self._asymmetric_specialist.tasks_executed
        if self._hash_specialist:
            stats['hash_tasks'] = self._hash_specialist.tasks_executed

        return stats
