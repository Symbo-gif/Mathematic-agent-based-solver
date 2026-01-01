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

"""Conjecture Generation module"""
from .synthetic_data_generator import SyntheticDataGenerator
from .pattern_recognizer import PatternRecognizer, CandidateConjecture, ConjectureStatus
from .conjecture_formalizer import ConjectureFormalizer
from .boundary_explorer import BoundaryExplorer

__all__ = [
    "SyntheticDataGenerator", 
    "PatternRecognizer", 
    "ConjectureFormalizer", 
    "BoundaryExplorer", 
    "CandidateConjecture", 
    "ConjectureStatus"
]
