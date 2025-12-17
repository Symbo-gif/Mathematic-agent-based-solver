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
Conjecture Generation Team - "The Theorist"
============================================

Phase 6, Step 1: Addresses Proactive Knowledge Synthesis

This team evolves the system from reactive problem solving (answering queries)
to proactive knowledge synthesis (asking "What else is true?").

Agents:
1. SyntheticDataGenerator ("The Dreamer") - AlphaGeometry-style synthetic theorem generation
2. PatternRecognizer ("The Filter") - Filters trivial theorems, identifies novel patterns
3. ConjectureFormalizer - Converts patterns to Lean4/Isabelle statements

Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx, Section 1
"""

from .synthetic_data_generator import SyntheticDataGenerator, SyntheticTheorem
from .pattern_recognizer import PatternRecognizer, CandidateConjecture
from .conjecture_formalizer import ConjectureFormalizer, ConjectureStatus

__all__ = [
    'SyntheticDataGenerator',
    'SyntheticTheorem',
    'PatternRecognizer',
    'CandidateConjecture',
    'ConjectureFormalizer',
    'ConjectureStatus'
]
