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
Cryptography Specialists Package
================================

Native Python implementations for cryptographic computations.
EDUCATIONAL USE ONLY - Not for production security.

NO external dependencies beyond numpy.

Specialists:
- ModularArithmeticSpecialist: Modular exponentiation, inverses, CRT, primality
- AsymmetricCryptoSpecialist: RSA, Diffie-Hellman, ElGamal (educational)
- HashSpecialist: Hash functions, Merkle trees, collision analysis
"""

from .modular_arithmetic_specialist import ModularArithmeticSpecialist
from .asymmetric_crypto_specialist import AsymmetricCryptoSpecialist
from .hash_specialist import HashSpecialist

__all__ = [
    'ModularArithmeticSpecialist',
    'AsymmetricCryptoSpecialist',
    'HashSpecialist',
]
