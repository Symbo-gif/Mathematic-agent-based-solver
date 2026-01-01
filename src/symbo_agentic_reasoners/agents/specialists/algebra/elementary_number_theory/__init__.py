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
Elementary Number Theory Specialists Package
============================================

7 specialists for elementary number theory operations:
- CongruenceSpecialist: Linear/quadratic congruences, CRT
- ContinuedFractionsSpecialist: CF expansion, convergents
- PellEquationSpecialist: Fundamental solutions, negative Pell
- TonelliShanksSpecialist: Modular square roots
- LiftingTheExponentSpecialist: LTE lemma, p-adic valuations
- DiophantineBasicSpecialist: Linear Diophantine, Pythagorean triples
- QuadraticResidueSpecialist: Legendre symbol, quadratic reciprocity

All specialists use core/elementary_number_theory.py (100% native Python).

NO SYMPY - Pure native mathematical reasoning.
"""

from .congruence_specialist import CongruenceSpecialist
from .continued_fractions_specialist import ContinuedFractionsSpecialist
from .pell_equation_specialist import PellEquationSpecialist
from .tonelli_shanks_specialist import TonelliShanksSpecialist
from .lifting_the_exponent_specialist import LiftingTheExponentSpecialist
from .diophantine_basic_specialist import DiophantineBasicSpecialist
from .quadratic_residue_specialist import QuadraticResidueSpecialist

__all__ = [
    'CongruenceSpecialist',
    'ContinuedFractionsSpecialist',
    'PellEquationSpecialist',
    'TonelliShanksSpecialist',
    'LiftingTheExponentSpecialist',
    'DiophantineBasicSpecialist',
    'QuadraticResidueSpecialist'
]
