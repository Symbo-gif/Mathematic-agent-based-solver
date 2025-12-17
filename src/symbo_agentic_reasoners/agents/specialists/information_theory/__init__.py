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
Information Theory Specialists Package
======================================

Native Python implementations for information-theoretic computations.
NO external dependencies beyond numpy.

Specialists:
- EntropySpecialist: Shannon entropy, relative entropy, joint/conditional entropy
- CodingTheorySpecialist: Huffman coding, error-correcting codes
- ChannelCapacitySpecialist: Channel capacity, mutual information
"""

from .entropy_specialist import EntropySpecialist
from .coding_theory_specialist import CodingTheorySpecialist
from .channel_capacity_specialist import ChannelCapacitySpecialist

__all__ = [
    'EntropySpecialist',
    'CodingTheorySpecialist',
    'ChannelCapacitySpecialist',
]
