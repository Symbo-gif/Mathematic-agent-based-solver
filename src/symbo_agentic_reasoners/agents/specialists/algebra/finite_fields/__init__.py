# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

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
