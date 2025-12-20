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
Generating Functions Specialists Package
=========================================

7 specialists for generating function operations:
- OrdinaryGFSpecialist: OGF construction and manipulation
- ExponentialGFSpecialist: EGF and labeled structures
- RationalGFSpecialist: Partial fractions, poles
- RecurrenceGFSpecialist: Solve recurrences via GF
- BivariateGFSpecialist: Two-variable GFs
- GFCompositionSpecialist: GF operations (add, multiply, compose, hadamard)
- AsymptoticExtractionSpecialist: Singularity analysis

All specialists use core/generating_functions.py (100% native Python).

NO SYMPY - Pure native mathematical reasoning.
"""

from .ordinary_gf_specialist import OrdinaryGFSpecialist
from .exponential_gf_specialist import ExponentialGFSpecialist
from .rational_gf_specialist import RationalGFSpecialist
from .recurrence_gf_specialist import RecurrenceGFSpecialist
from .bivariate_gf_specialist import BivariateGFSpecialist
from .gf_composition_specialist import GFCompositionSpecialist
from .asymptotic_extraction_specialist import AsymptoticExtractionSpecialist

__all__ = [
    'OrdinaryGFSpecialist',
    'ExponentialGFSpecialist',
    'RationalGFSpecialist',
    'RecurrenceGFSpecialist',
    'BivariateGFSpecialist',
    'GFCompositionSpecialist',
    'AsymptoticExtractionSpecialist'
]
