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
