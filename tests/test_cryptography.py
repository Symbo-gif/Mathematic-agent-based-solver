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
Tests for Cryptography Domain
=============================

Comprehensive tests for modular arithmetic, asymmetric crypto, and hash specialists.
"""

import pytest
import math


# =============================================================================
# MODULAR ARITHMETIC SPECIALIST TESTS
# =============================================================================

class TestModularArithmeticSpecialist:
    """Tests for ModularArithmeticSpecialist."""

    def test_mod_exp_basic(self):
        """Basic modular exponentiation."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import ModularArithmeticSpecialist
        specialist = ModularArithmeticSpecialist()

        # 2^10 mod 1000 = 1024 mod 1000 = 24
        result = specialist.modular_exponentiation(2, 10, 1000)
        assert result['result'] == 24

    def test_mod_exp_large(self):
        """Large modular exponentiation."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import ModularArithmeticSpecialist
        specialist = ModularArithmeticSpecialist()

        # 3^1000 mod 7
        result = specialist.modular_exponentiation(3, 1000, 7)
        # By Fermat: 3^6 ≡ 1 (mod 7), 1000 = 166*6 + 4, so 3^1000 ≡ 3^4 = 81 ≡ 4 (mod 7)
        assert result['result'] == 4

    def test_mod_exp_zero_exp(self):
        """x^0 mod n = 1."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import ModularArithmeticSpecialist
        specialist = ModularArithmeticSpecialist()

        result = specialist.modular_exponentiation(5, 0, 13)
        assert result['result'] == 1

    def test_extended_gcd(self):
        """Extended Euclidean algorithm."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import ModularArithmeticSpecialist
        specialist = ModularArithmeticSpecialist()

        result = specialist.extended_gcd(35, 15)
        assert result['gcd'] == 5
        # Verify Bezout: 35*x + 15*y = 5
        assert 35 * result['x'] + 15 * result['y'] == 5

    def test_extended_gcd_coprime(self):
        """Extended GCD of coprime numbers."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import ModularArithmeticSpecialist
        specialist = ModularArithmeticSpecialist()

        result = specialist.extended_gcd(17, 13)
        assert result['gcd'] == 1

    def test_mod_inverse(self):
        """Modular inverse."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import ModularArithmeticSpecialist
        specialist = ModularArithmeticSpecialist()

        # 3^(-1) mod 11 = 4 (since 3*4 = 12 ≡ 1 mod 11)
        result = specialist.modular_inverse(3, 11)
        assert result['inverse'] == 4
        assert result['verification'] == 1

    def test_mod_inverse_no_inverse(self):
        """No modular inverse when gcd != 1."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import ModularArithmeticSpecialist
        specialist = ModularArithmeticSpecialist()

        result = specialist.modular_inverse(6, 9)
        assert 'error' in result

    def test_crt_basic(self):
        """Chinese Remainder Theorem."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import ModularArithmeticSpecialist
        specialist = ModularArithmeticSpecialist()

        # x ≡ 2 (mod 3), x ≡ 3 (mod 5), x ≡ 2 (mod 7)
        result = specialist.chinese_remainder_theorem([2, 3, 2], [3, 5, 7])

        assert 'solution' in result
        x = result['solution']
        assert x % 3 == 2
        assert x % 5 == 3
        assert x % 7 == 2

    def test_crt_not_coprime(self):
        """CRT with non-coprime moduli should error."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import ModularArithmeticSpecialist
        specialist = ModularArithmeticSpecialist()

        result = specialist.chinese_remainder_theorem([1, 2], [4, 6])
        assert 'error' in result

    def test_euler_totient_prime(self):
        """Euler's totient of prime p is p-1."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import ModularArithmeticSpecialist
        specialist = ModularArithmeticSpecialist()

        result = specialist.euler_totient(17)
        assert result['phi'] == 16

    def test_euler_totient_composite(self):
        """Euler's totient of composite number."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import ModularArithmeticSpecialist
        specialist = ModularArithmeticSpecialist()

        # phi(12) = phi(4)*phi(3) = 2*2 = 4
        result = specialist.euler_totient(12)
        assert result['phi'] == 4

    def test_primitive_root(self):
        """Find primitive root."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import ModularArithmeticSpecialist
        specialist = ModularArithmeticSpecialist()

        result = specialist.find_primitive_root(7)
        assert 'primitive_root' in result
        g = result['primitive_root']
        # Check it generates all of Z_7^*
        generated = set()
        power = 1
        for _ in range(6):
            generated.add(power)
            power = (power * g) % 7
        assert generated == {1, 2, 3, 4, 5, 6}

    def test_discrete_log(self):
        """Discrete logarithm."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import ModularArithmeticSpecialist
        specialist = ModularArithmeticSpecialist()

        # 3^x ≡ 5 (mod 7), x = 5 since 3^5 = 243 ≡ 5 (mod 7)
        result = specialist.discrete_logarithm_bsgs(3, 5, 7)
        assert 'discrete_log' in result
        x = result['discrete_log']
        # Verify
        assert pow(3, x, 7) == 5

    def test_miller_rabin_prime(self):
        """Miller-Rabin identifies primes."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import ModularArithmeticSpecialist
        specialist = ModularArithmeticSpecialist()

        for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 97, 101, 1009]:
            result = specialist.is_prime_miller_rabin(p)
            assert result['is_prime'] == True, f"{p} should be prime"

    def test_miller_rabin_composite(self):
        """Miller-Rabin identifies composites."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import ModularArithmeticSpecialist
        specialist = ModularArithmeticSpecialist()

        for n in [4, 6, 8, 9, 10, 15, 21, 100, 1001]:
            result = specialist.is_prime_miller_rabin(n)
            assert result['is_prime'] == False, f"{n} should be composite"


# =============================================================================
# ASYMMETRIC CRYPTO SPECIALIST TESTS
# =============================================================================

class TestAsymmetricCryptoSpecialist:
    """Tests for AsymmetricCryptoSpecialist."""

    def test_rsa_keygen(self):
        """RSA key generation."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import AsymmetricCryptoSpecialist
        specialist = AsymmetricCryptoSpecialist()

        result = specialist.rsa_keygen(16)

        assert 'public_key' in result
        assert 'private_key' in result
        assert result['public_key']['n'] == result['private_key']['n']

    def test_rsa_encrypt_decrypt(self):
        """RSA encryption and decryption."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import AsymmetricCryptoSpecialist
        specialist = AsymmetricCryptoSpecialist()

        keys = specialist.rsa_keygen(16)
        e = keys['public_key']['e']
        d = keys['private_key']['d']
        n = keys['public_key']['n']

        message = 42

        # Encrypt
        enc_result = specialist.rsa_encrypt(message, e, n)
        ciphertext = enc_result['ciphertext']

        # Decrypt
        dec_result = specialist.rsa_decrypt(ciphertext, d, n)
        plaintext = dec_result['plaintext']

        assert plaintext == message

    def test_rsa_sign_verify(self):
        """RSA signature and verification."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import AsymmetricCryptoSpecialist
        specialist = AsymmetricCryptoSpecialist()

        keys = specialist.rsa_keygen(16)
        e = keys['public_key']['e']
        d = keys['private_key']['d']
        n = keys['public_key']['n']

        message_hash = 123

        # Sign
        sign_result = specialist.rsa_sign(message_hash, d, n)
        signature = sign_result['signature']

        # Verify
        verify_result = specialist.rsa_verify(signature, message_hash, e, n)
        assert verify_result['valid'] == True

    def test_rsa_invalid_signature(self):
        """RSA invalid signature detection."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import AsymmetricCryptoSpecialist
        specialist = AsymmetricCryptoSpecialist()

        keys = specialist.rsa_keygen(16)
        e = keys['public_key']['e']
        n = keys['public_key']['n']

        # Tampered signature
        verify_result = specialist.rsa_verify(12345, 67890, e, n)
        assert verify_result['valid'] == False

    def test_diffie_hellman_key_exchange(self):
        """Diffie-Hellman key exchange."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import AsymmetricCryptoSpecialist
        specialist = AsymmetricCryptoSpecialist()

        # Use small prime for testing
        p = 23
        g = 5

        # Alice generates keys
        alice = specialist.diffie_hellman_keygen(p, g)

        # Bob generates keys
        bob = specialist.diffie_hellman_keygen(p, g)

        # Compute shared secrets
        alice_secret = specialist.diffie_hellman_shared_secret(
            alice['private_key'], bob['public_key'], p
        )
        bob_secret = specialist.diffie_hellman_shared_secret(
            bob['private_key'], alice['public_key'], p
        )

        # Shared secrets should match
        assert alice_secret['shared_secret'] == bob_secret['shared_secret']

    def test_elgamal_encrypt_decrypt(self):
        """ElGamal encryption and decryption."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import AsymmetricCryptoSpecialist
        specialist = AsymmetricCryptoSpecialist()

        p = 23
        g = 5

        # Generate keys
        keys = specialist.elgamal_keygen(p, g)
        x = keys['private_key']
        y = keys['public_key']

        message = 7

        # Encrypt
        enc_result = specialist.elgamal_encrypt(message, y, p, g)

        # Decrypt
        dec_result = specialist.elgamal_decrypt(
            enc_result['c1'], enc_result['c2'], x, p
        )

        assert dec_result['plaintext'] == message


# =============================================================================
# HASH SPECIALIST TESTS
# =============================================================================

class TestHashSpecialist:
    """Tests for HashSpecialist."""

    def test_simple_hash_deterministic(self):
        """Simple hash is deterministic."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import HashSpecialist
        specialist = HashSpecialist()

        h1 = specialist.simple_hash("test")
        h2 = specialist.simple_hash("test")

        assert h1['hash'] == h2['hash']

    def test_simple_hash_different_inputs(self):
        """Different inputs give different hashes."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import HashSpecialist
        specialist = HashSpecialist()

        h1 = specialist.simple_hash("hello")
        h2 = specialist.simple_hash("world")

        assert h1['hash'] != h2['hash']

    def test_djb2_hash(self):
        """DJB2 hash function."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import HashSpecialist
        specialist = HashSpecialist()

        result = specialist.djb2_hash("hello")
        assert 'hash' in result
        assert result['method'] == 'djb2'

    def test_fnv1a_hash(self):
        """FNV-1a hash function."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import HashSpecialist
        specialist = HashSpecialist()

        result = specialist.fnv1a_hash("hello")
        assert 'hash' in result
        assert result['method'] == 'fnv1a_32'

    def test_merkle_root(self):
        """Merkle tree root computation."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import HashSpecialist
        specialist = HashSpecialist()

        leaves = ["a", "b", "c", "d"]
        result = specialist.merkle_root(leaves)

        assert 'root' in result
        assert result['num_leaves'] == 4

    def test_merkle_root_single_leaf(self):
        """Merkle tree with single leaf."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import HashSpecialist
        specialist = HashSpecialist()

        result = specialist.merkle_root(["single"])
        assert 'root' in result

    def test_merkle_proof_verify(self):
        """Merkle proof generation and verification."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import HashSpecialist
        specialist = HashSpecialist()

        leaves = ["a", "b", "c", "d"]

        # Get proof for leaf at index 1
        proof_result = specialist.merkle_proof(leaves, 1)

        assert 'proof' in proof_result
        assert proof_result['leaf'] == "b"

        # Verify the proof
        verify_result = specialist.verify_merkle_proof(
            "b",
            proof_result['proof'],
            proof_result['root'],
            1
        )

        assert verify_result['valid'] == True

    def test_merkle_proof_tampered(self):
        """Tampered Merkle proof should fail."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import HashSpecialist
        specialist = HashSpecialist()

        leaves = ["a", "b", "c", "d"]
        proof_result = specialist.merkle_proof(leaves, 1)

        # Try to verify with wrong leaf
        verify_result = specialist.verify_merkle_proof(
            "x",  # Wrong leaf
            proof_result['proof'],
            proof_result['root'],
            1
        )

        assert verify_result['valid'] == False

    def test_hash_chain(self):
        """Hash chain generation."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import HashSpecialist
        specialist = HashSpecialist()

        result = specialist.hash_chain("seed", 5)

        assert 'chain' in result
        assert len(result['chain']) == 5
        assert result['chain'][0]['index'] == 0

    def test_birthday_probability(self):
        """Birthday collision probability."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import HashSpecialist
        specialist = HashSpecialist()

        result = specialist.birthday_collision_probability(32, 1000)

        assert 'collision_probability' in result
        assert 0 <= result['collision_probability'] <= 1
        assert 'birthday_bound' in result

    def test_birthday_probability_high_samples(self):
        """High sample count approaches probability 1."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import HashSpecialist
        specialist = HashSpecialist()

        # With 16-bit hash and 1000 samples, collision is almost certain
        result = specialist.birthday_collision_probability(16, 1000)
        assert result['collision_probability'] > 0.99


# =============================================================================
# CRYPTOGRAPHY SUPERVISOR TESTS
# =============================================================================

class TestCryptographySupervisor:
    """Tests for CryptographySupervisor."""

    def test_supervisor_initialization(self):
        """Supervisor initializes correctly."""
        from symbo_agentic_reasoners.agents.supervisors.cryptography_supervisor import CryptographySupervisor
        supervisor = CryptographySupervisor()

        assert supervisor.agent_id == 'cryptography_supervisor_001'

    def test_supervisor_solve_mod_exp(self):
        """Supervisor routes modular exponentiation."""
        from symbo_agentic_reasoners.agents.supervisors.cryptography_supervisor import CryptographySupervisor
        supervisor = CryptographySupervisor()

        result = supervisor.solve({
            'type': 'mod_exp',
            'base': 2,
            'exponent': 10,
            'modulus': 1000
        })

        assert result['result'] == 24

    def test_supervisor_solve_rsa_keygen(self):
        """Supervisor routes RSA key generation."""
        from symbo_agentic_reasoners.agents.supervisors.cryptography_supervisor import CryptographySupervisor
        supervisor = CryptographySupervisor()

        result = supervisor.solve({
            'type': 'rsa_keygen',
            'bits': 16
        })

        assert 'public_key' in result

    def test_supervisor_solve_hash(self):
        """Supervisor routes hash computation."""
        from symbo_agentic_reasoners.agents.supervisors.cryptography_supervisor import CryptographySupervisor
        supervisor = CryptographySupervisor()

        result = supervisor.solve({
            'type': 'hash',
            'data': 'test'
        })

        assert 'hash' in result

    def test_supervisor_unknown_type(self):
        """Supervisor handles unknown problem type."""
        from symbo_agentic_reasoners.agents.supervisors.cryptography_supervisor import CryptographySupervisor
        supervisor = CryptographySupervisor()

        result = supervisor.solve({
            'type': 'unknown_operation'
        })

        assert 'error' in result


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestCryptographyIntegration:
    """Integration tests for cryptography domain."""

    def test_rsa_full_workflow(self):
        """Full RSA workflow: keygen, encrypt, decrypt."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import (
            ModularArithmeticSpecialist, AsymmetricCryptoSpecialist
        )

        crypto = AsymmetricCryptoSpecialist()

        # Generate keys
        keys = crypto.rsa_keygen(16)

        # Test multiple messages
        for msg in [1, 10, 42, 100]:
            enc = crypto.rsa_encrypt(msg, keys['public_key']['e'], keys['public_key']['n'])
            dec = crypto.rsa_decrypt(enc['ciphertext'], keys['private_key']['d'], keys['private_key']['n'])
            assert dec['plaintext'] == msg

    def test_crt_rsa_decryption(self):
        """CRT can speed up RSA decryption."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import (
            ModularArithmeticSpecialist, AsymmetricCryptoSpecialist
        )

        mod = ModularArithmeticSpecialist()
        crypto = AsymmetricCryptoSpecialist()

        keys = crypto.rsa_keygen(16)
        p, q = keys['primes']['p'], keys['primes']['q']
        d = keys['private_key']['d']
        n = keys['public_key']['n']

        # Encrypt message
        message = 42
        enc = crypto.rsa_encrypt(message, keys['public_key']['e'], n)
        c = enc['ciphertext']

        # Standard decryption
        standard = mod.modular_exponentiation(c, d, n)

        # CRT-based decryption
        dp = d % (p - 1)
        dq = d % (q - 1)
        mp = mod.modular_exponentiation(c % p, dp, p)['result']
        mq = mod.modular_exponentiation(c % q, dq, q)['result']

        # Combine using CRT
        crt_result = mod.chinese_remainder_theorem([mp, mq], [p, q])

        assert crt_result['solution'] == standard['result']
        assert crt_result['solution'] == message

    def test_merkle_all_leaves(self):
        """Merkle proofs work for all leaves."""
        from symbo_agentic_reasoners.agents.specialists.cryptography import HashSpecialist

        specialist = HashSpecialist()
        leaves = ["a", "b", "c", "d", "e", "f", "g", "h"]

        root_result = specialist.merkle_root(leaves)
        root = root_result['root']

        for i, leaf in enumerate(leaves):
            proof = specialist.merkle_proof(leaves, i)
            verify = specialist.verify_merkle_proof(leaf, proof['proof'], root, i)
            assert verify['valid'], f"Proof failed for leaf {i}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
