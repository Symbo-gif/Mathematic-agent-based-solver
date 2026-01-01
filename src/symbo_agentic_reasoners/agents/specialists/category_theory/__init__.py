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
Category Theory Specialists Package
===================================

Native Python implementations for category theory.
NO external dependencies beyond standard library.

Specialists:
- MorphismSpecialist: Categories, morphisms, composition, classification
- FunctorSpecialist: Functors, natural transformations
- UniversalPropertiesSpecialist: Products, coproducts, limits, colimits
"""

from .morphism_specialist import MorphismSpecialist, Category, Object, Morphism
from .functor_specialist import FunctorSpecialist, Functor, NaturalTransformation
from .universal_properties_specialist import UniversalPropertiesSpecialist, UniversalConstruction

__all__ = [
    'MorphismSpecialist',
    'FunctorSpecialist',
    'UniversalPropertiesSpecialist',
    'Category',
    'Object',
    'Morphism',
    'Functor',
    'NaturalTransformation',
    'UniversalConstruction',
]
