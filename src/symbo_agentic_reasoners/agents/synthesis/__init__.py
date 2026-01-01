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

# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
"""
Synthesis Team Agents - Phase 6
================================

This package contains agents for mathematical synthesis and construction:

- SYN-1: StructuralSynthesizer - Builds mathematical structures from specs
- SYN-2: ProofTermConstructor - Constructs and validates proof terms
- SYN-3: ConjectureGenerator - Generates conjectures from patterns
- SYN-4: FormalLanguageTranslator - Translates between notations
"""

from .structural_synthesizer import StructuralSynthesizer
from .proof_term_constructor import ProofTermConstructor
from .conjecture_generator import ConjectureGenerator
from .formal_translator import FormalLanguageTranslator

__all__ = [
    'StructuralSynthesizer',
    'ProofTermConstructor',
    'ConjectureGenerator',
    'FormalLanguageTranslator'
]
