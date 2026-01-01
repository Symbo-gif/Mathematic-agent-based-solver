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
Finite Fields Specialists Package
=================================

Contains 7 specialists for finite field theory:
- PrimeFieldSpecialist: GF(p) operations, primitive elements, quadratic residues
- ExtensionFieldSpecialist: GF(p^n) construction, subfield detection
- IrreduciblePolynomialSpecialist: Rabin test, polynomial finding, factorization
- FieldArithmeticSpecialist: Field operations (+, ×, inverse, exp, discrete log)
- MinimalPolynomialSpecialist: Frobenius map, conjugates, trace, norm
- FieldIsomorphismSpecialist: Automorphism groups, fixed fields, orbits
- GaloisTheorySpecialist: Splitting fields, Galois correspondence, towers

ARCHITECTURE:
------------
All specialists inherit from BDIAgent with:
- update_beliefs(): Monitor blackboard for tasks
- deliberate(): Create intentions from beliefs
- execute_step(): Execute plan actions

Service Types (hierarchical):
- math.algebra.finite_fields.prime_field
- math.algebra.finite_fields.extension
- math.algebra.finite_fields.irreducible
- math.algebra.finite_fields.arithmetic
- math.algebra.finite_fields.minimal_poly
- math.algebra.finite_fields.isomorphism
- math.algebra.finite_fields.galois

NO SYMPY - Pure native mathematical reasoning.

REFERENCE:
---------
- Lidl & Niederreiter (1997), Finite Fields
- Shoup (2005), Computational Number Theory
"""

from symbo_agentic_reasoners.agents.specialists.algebra.finite_fields.prime_field_specialist import PrimeFieldSpecialist
from symbo_agentic_reasoners.agents.specialists.algebra.finite_fields.extension_field_specialist import ExtensionFieldSpecialist
from symbo_agentic_reasoners.agents.specialists.algebra.finite_fields.irreducible_polynomial_specialist import IrreduciblePolynomialSpecialist
from symbo_agentic_reasoners.agents.specialists.algebra.finite_fields.field_arithmetic_specialist import FieldArithmeticSpecialist
from symbo_agentic_reasoners.agents.specialists.algebra.finite_fields.minimal_polynomial_specialist import MinimalPolynomialSpecialist
from symbo_agentic_reasoners.agents.specialists.algebra.finite_fields.field_isomorphism_specialist import FieldIsomorphismSpecialist
from symbo_agentic_reasoners.agents.specialists.algebra.finite_fields.galois_theory_specialist import GaloisTheorySpecialist

__all__ = [
    'PrimeFieldSpecialist',
    'ExtensionFieldSpecialist',
    'IrreduciblePolynomialSpecialist',
    'FieldArithmeticSpecialist',
    'MinimalPolynomialSpecialist',
    'FieldIsomorphismSpecialist',
    'GaloisTheorySpecialist',
]
