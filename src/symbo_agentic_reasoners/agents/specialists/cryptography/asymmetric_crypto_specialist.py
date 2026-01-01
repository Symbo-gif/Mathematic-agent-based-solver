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
ASYMMETRIC CRYPTOGRAPHY SPECIALIST (Tier 3)
===========================================

Native Python implementation for asymmetric cryptography.
Educational RSA implementation - NOT for production use.

NO SYMPY - Pure native mathematical reasoning.
"""

import logging
import random
from typing import Dict, Any, List, Optional, Tuple

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from .modular_arithmetic_specialist import ModularArithmeticSpecialist

logger = logging.getLogger(__name__)


class AsymmetricCryptoSpecialist(BDIAgent):
    """
    Specialist for asymmetric cryptography operations.

    EDUCATIONAL USE ONLY - Not cryptographically secure!

    Capabilities:
    - RSA key generation (small keys for education)
    - RSA encryption/decryption
    - Diffie-Hellman key exchange
    - ElGamal encryption
    - Digital signatures (RSA-based)
    """

    def __init__(self, agent_id: str = 'asymmetric_crypto_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0
        self.mod_specialist = ModularArithmeticSpecialist()

        if self.df:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
            self.df.register(create_service_registration(
                service_type='math.cryptography.asymmetric',
                agent_id=agent_id,
                algorithm='native_asymmetric_crypto',
                cost='medium',
                instance=self,
                tier='3',
                capabilities='rsa_dh_elgamal_signatures'
            ))

        logger.info(f"[{agent_id}] Asymmetric Crypto Specialist initialized (EDUCATIONAL ONLY)")

    def update_beliefs(self):
        """PERCEIVE: Monitor blackboard for crypto tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryStatus
            tasks = self.blackboard.query_entries(tags=['rsa'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['asymmetric'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['diffie_hellman'], status=EntryStatus.PENDING)

            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(f'claimed_task_{task.entry_id}') and not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create crypto computation plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'rsa_keygen')

            steps = ['claim_task', 'compute_crypto', 'post_result']
            intention = Intention(
                plan_id=f'asymmetric_{operation}_{task_id}',
                steps=steps,
                target_desire='asymmetric_crypto_computation',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)
        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Compute crypto operations."""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')

        if action == 'claim_task':
            self.add_belief(f'claimed_task_{task.entry_id}', True, confidence=1.0)
            intention.advance()
        elif action == 'compute_crypto':
            self._compute_crypto(intention)
        elif action == 'post_result':
            self._post_result(intention)

    def _compute_crypto(self, intention: Intention):
        """Compute the requested crypto operation."""
        task = intention.metadata.get('task_entry')
        metadata = task.metadata if hasattr(task, 'metadata') else {}
        operation = metadata.get('operation', 'rsa_keygen')

        try:
            if operation == 'rsa_keygen':
                bits = metadata.get('bits', 32)
                result = self.rsa_keygen(bits)
            elif operation == 'rsa_encrypt':
                message = metadata.get('message', 0)
                e = metadata.get('e', 65537)
                n = metadata.get('n', 0)
                result = self.rsa_encrypt(message, e, n)
            elif operation == 'rsa_decrypt':
                ciphertext = metadata.get('ciphertext', 0)
                d = metadata.get('d', 0)
                n = metadata.get('n', 0)
                result = self.rsa_decrypt(ciphertext, d, n)
            elif operation == 'rsa_sign':
                message_hash = metadata.get('message_hash', 0)
                d = metadata.get('d', 0)
                n = metadata.get('n', 0)
                result = self.rsa_sign(message_hash, d, n)
            elif operation == 'rsa_verify':
                signature = metadata.get('signature', 0)
                message_hash = metadata.get('message_hash', 0)
                e = metadata.get('e', 0)
                n = metadata.get('n', 0)
                result = self.rsa_verify(signature, message_hash, e, n)
            elif operation == 'dh_keygen':
                p = metadata.get('p', 0)
                g = metadata.get('g', 0)
                result = self.diffie_hellman_keygen(p, g)
            elif operation == 'dh_shared_secret':
                private = metadata.get('private', 0)
                other_public = metadata.get('other_public', 0)
                p = metadata.get('p', 0)
                result = self.diffie_hellman_shared_secret(private, other_public, p)
            elif operation == 'elgamal_keygen':
                p = metadata.get('p', 0)
                g = metadata.get('g', 0)
                result = self.elgamal_keygen(p, g)
            elif operation == 'elgamal_encrypt':
                message = metadata.get('message', 0)
                y = metadata.get('public_key', 0)
                p = metadata.get('p', 0)
                g = metadata.get('g', 0)
                result = self.elgamal_encrypt(message, y, p, g)
            elif operation == 'elgamal_decrypt':
                c1 = metadata.get('c1', 0)
                c2 = metadata.get('c2', 0)
                x = metadata.get('private_key', 0)
                p = metadata.get('p', 0)
                result = self.elgamal_decrypt(c1, c2, x, p)
            else:
                result = {'error': f'Unknown operation: {operation}'}

            intention.metadata['result'] = result
            self.tasks_executed += 1
            intention.advance()

        except Exception as e:
            logger.error(f"[{self.agent_id}] Crypto computation failed: {e}")
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
                tags=['crypto', 'asymmetric', 'result'],
                metadata={'source_task': task.entry_id, 'agent': self.agent_id}
            )
            self.blackboard.post_entry(result_entry)
            self.blackboard.update_entry_status(task.entry_id, EntryStatus.COMPLETED)

        intention.mark_completed()

    # =========================================================================
    # PRIME GENERATION (for educational RSA)
    # =========================================================================

    def _generate_prime(self, bits: int) -> int:
        """Generate a random prime of approximately 'bits' bits."""
        while True:
            # Generate random odd number
            n = random.getrandbits(bits) | (1 << (bits - 1)) | 1

            result = self.mod_specialist.is_prime_miller_rabin(n)
            if result.get('is_prime', False):
                return n

    # =========================================================================
    # RSA
    # =========================================================================

    def rsa_keygen(self, bits: int = 32) -> Dict[str, Any]:
        """
        Generate RSA key pair.

        EDUCATIONAL ONLY - small keys are NOT secure!

        Args:
            bits: Bit size for primes (default 32 gives ~64 bit modulus)

        Returns:
            Dictionary with public key (e, n) and private key (d, n)
        """
        if bits < 8:
            return {'error': 'Bit size must be at least 8'}
        if bits > 64:
            return {'error': 'Bit size capped at 64 for educational use'}

        # Generate two distinct primes
        p = self._generate_prime(bits)
        q = self._generate_prime(bits)
        while q == p:
            q = self._generate_prime(bits)

        n = p * q
        phi_n = (p - 1) * (q - 1)

        # Choose e (commonly 65537)
        e = 65537
        if e >= phi_n:
            e = 3
        while True:
            gcd_result = self.mod_specialist.extended_gcd(e, phi_n)
            if gcd_result['gcd'] == 1:
                break
            e += 2

        # Compute d = e^(-1) mod phi(n)
        inv_result = self.mod_specialist.modular_inverse(e, phi_n)
        if 'error' in inv_result:
            return inv_result
        d = inv_result['inverse']

        return {
            'public_key': {'e': e, 'n': n},
            'private_key': {'d': d, 'n': n},
            'primes': {'p': p, 'q': q},
            'phi_n': phi_n,
            'bit_size': bits * 2,
            'warning': 'EDUCATIONAL ONLY - NOT SECURE',
            'method': 'native_rsa_keygen'
        }

    @staticmethod
    def rsa_encrypt(message: int, e: int, n: int) -> Dict[str, Any]:
        """
        RSA encryption: c = m^e mod n.

        Args:
            message: Message as integer (must be < n)
            e: Public exponent
            n: Modulus

        Returns:
            Dictionary with ciphertext
        """
        if message >= n:
            return {'error': f'Message {message} must be less than modulus {n}'}
        if message < 0:
            return {'error': 'Message must be non-negative'}

        result = ModularArithmeticSpecialist.modular_exponentiation(message, e, n)
        return {
            'ciphertext': result['result'],
            'method': 'native_rsa_encrypt'
        }

    @staticmethod
    def rsa_decrypt(ciphertext: int, d: int, n: int) -> Dict[str, Any]:
        """
        RSA decryption: m = c^d mod n.

        Args:
            ciphertext: Ciphertext as integer
            d: Private exponent
            n: Modulus

        Returns:
            Dictionary with plaintext
        """
        result = ModularArithmeticSpecialist.modular_exponentiation(ciphertext, d, n)
        return {
            'plaintext': result['result'],
            'method': 'native_rsa_decrypt'
        }

    @staticmethod
    def rsa_sign(message_hash: int, d: int, n: int) -> Dict[str, Any]:
        """
        RSA signature: s = H(m)^d mod n.

        Args:
            message_hash: Hash of message as integer
            d: Private exponent
            n: Modulus

        Returns:
            Dictionary with signature
        """
        result = ModularArithmeticSpecialist.modular_exponentiation(message_hash, d, n)
        return {
            'signature': result['result'],
            'method': 'native_rsa_sign'
        }

    @staticmethod
    def rsa_verify(signature: int, message_hash: int, e: int, n: int) -> Dict[str, Any]:
        """
        RSA signature verification.

        Args:
            signature: Signature to verify
            message_hash: Expected hash value
            e: Public exponent
            n: Modulus

        Returns:
            Dictionary with verification result
        """
        result = ModularArithmeticSpecialist.modular_exponentiation(signature, e, n)
        recovered = result['result']

        return {
            'valid': recovered == message_hash,
            'recovered_hash': recovered,
            'expected_hash': message_hash,
            'method': 'native_rsa_verify'
        }

    # =========================================================================
    # DIFFIE-HELLMAN
    # =========================================================================

    def diffie_hellman_keygen(self, p: int, g: int) -> Dict[str, Any]:
        """
        Generate Diffie-Hellman key pair.

        Args:
            p: Prime modulus
            g: Generator

        Returns:
            Dictionary with private and public keys
        """
        if p < 3:
            return {'error': 'Prime must be at least 3'}

        # Private key: random in [2, p-2]
        private = random.randint(2, p - 2)

        # Public key: g^private mod p
        result = self.mod_specialist.modular_exponentiation(g, private, p)
        public = result['result']

        return {
            'private_key': private,
            'public_key': public,
            'p': p,
            'g': g,
            'method': 'native_dh_keygen'
        }

    @staticmethod
    def diffie_hellman_shared_secret(private: int, other_public: int, p: int) -> Dict[str, Any]:
        """
        Compute Diffie-Hellman shared secret.

        Args:
            private: Own private key
            other_public: Other party's public key
            p: Prime modulus

        Returns:
            Dictionary with shared secret
        """
        result = ModularArithmeticSpecialist.modular_exponentiation(other_public, private, p)
        return {
            'shared_secret': result['result'],
            'method': 'native_dh_shared_secret'
        }

    # =========================================================================
    # ELGAMAL
    # =========================================================================

    def elgamal_keygen(self, p: int, g: int) -> Dict[str, Any]:
        """
        Generate ElGamal key pair.

        Args:
            p: Prime modulus
            g: Generator

        Returns:
            Dictionary with keys
        """
        if p < 3:
            return {'error': 'Prime must be at least 3'}

        # Private key x: random in [1, p-2]
        x = random.randint(1, p - 2)

        # Public key y = g^x mod p
        result = self.mod_specialist.modular_exponentiation(g, x, p)
        y = result['result']

        return {
            'private_key': x,
            'public_key': y,
            'p': p,
            'g': g,
            'method': 'native_elgamal_keygen'
        }

    def elgamal_encrypt(self, message: int, y: int, p: int, g: int) -> Dict[str, Any]:
        """
        ElGamal encryption.

        Args:
            message: Message as integer (< p)
            y: Recipient's public key
            p: Prime modulus
            g: Generator

        Returns:
            Dictionary with ciphertext (c1, c2)
        """
        if message >= p:
            return {'error': f'Message must be less than p={p}'}

        # Random ephemeral key k
        k = random.randint(1, p - 2)

        # c1 = g^k mod p
        result1 = self.mod_specialist.modular_exponentiation(g, k, p)
        c1 = result1['result']

        # c2 = m * y^k mod p
        result2 = self.mod_specialist.modular_exponentiation(y, k, p)
        s = result2['result']
        c2 = (message * s) % p

        return {
            'c1': c1,
            'c2': c2,
            'method': 'native_elgamal_encrypt'
        }

    def elgamal_decrypt(self, c1: int, c2: int, x: int, p: int) -> Dict[str, Any]:
        """
        ElGamal decryption.

        Args:
            c1, c2: Ciphertext pair
            x: Private key
            p: Prime modulus

        Returns:
            Dictionary with plaintext
        """
        # s = c1^x mod p
        result = self.mod_specialist.modular_exponentiation(c1, x, p)
        s = result['result']

        # m = c2 * s^(-1) mod p
        inv_result = self.mod_specialist.modular_inverse(s, p)
        if 'error' in inv_result:
            return inv_result

        s_inv = inv_result['inverse']
        plaintext = (c2 * s_inv) % p

        return {
            'plaintext': plaintext,
            'method': 'native_elgamal_decrypt'
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Return agent statistics."""
        return {
            'agent_id': self.agent_id,
            'tasks_executed': self.tasks_executed,
            'capabilities': [
                'rsa_keygen', 'rsa_encrypt', 'rsa_decrypt',
                'rsa_sign', 'rsa_verify',
                'dh_keygen', 'dh_shared_secret',
                'elgamal_keygen', 'elgamal_encrypt', 'elgamal_decrypt'
            ],
            'warning': 'EDUCATIONAL IMPLEMENTATIONS ONLY'
        }
