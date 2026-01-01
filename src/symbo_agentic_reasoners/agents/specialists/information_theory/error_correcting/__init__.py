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
Error Correcting Codes Specialists Package
==========================================

Contains 6 specialists for error-correcting code theory:
- LinearCodeSpecialist: [n,k,d] code construction, parameter validation
- HammingDistanceSpecialist: Hamming distance, minimum weight, sphere volumes
- GeneratorMatrixSpecialist: Encoding via generator matrix, systematic form
- ParityCheckSpecialist: Syndrome computation, syndrome decoding
- MinimumDistanceSpecialist: d_min computation, weight distribution
- DualCodeSpecialist: Dual code construction, MacWilliams identity

ARCHITECTURE:
------------
All specialists inherit from BDIAgent with:
- update_beliefs(): Monitor blackboard for tasks
- deliberate(): Create intentions from beliefs
- execute_step(): Execute plan actions

Service Types (hierarchical):
- math.information_theory.error_correction.linear
- math.information_theory.error_correction.distance
- math.information_theory.error_correction.generator
- math.information_theory.error_correction.parity
- math.information_theory.error_correction.minimum_distance
- math.information_theory.error_correction.dual

BOUNDS SUPPORTED:
----------------
- Singleton bound: d <= n - k + 1
- Hamming bound (sphere packing)
- Plotkin bound
- Griesmer bound
- Gilbert-Varshamov bound

NO SYMPY - Pure native mathematical reasoning.

REFERENCE:
---------
- MacWilliams & Sloane (1977), Theory of Error-Correcting Codes
- Lin & Costello (2004), Error Control Coding
"""

from symbo_agentic_reasoners.agents.specialists.information_theory.error_correcting.linear_code_specialist import LinearCodeSpecialist
from symbo_agentic_reasoners.agents.specialists.information_theory.error_correcting.hamming_distance_specialist import HammingDistanceSpecialist
from symbo_agentic_reasoners.agents.specialists.information_theory.error_correcting.generator_matrix_specialist import GeneratorMatrixSpecialist
from symbo_agentic_reasoners.agents.specialists.information_theory.error_correcting.parity_check_specialist import ParityCheckSpecialist
from symbo_agentic_reasoners.agents.specialists.information_theory.error_correcting.minimum_distance_specialist import MinimumDistanceSpecialist
from symbo_agentic_reasoners.agents.specialists.information_theory.error_correcting.dual_code_specialist import DualCodeSpecialist

__all__ = [
    'LinearCodeSpecialist',
    'HammingDistanceSpecialist',
    'GeneratorMatrixSpecialist',
    'ParityCheckSpecialist',
    'MinimumDistanceSpecialist',
    'DualCodeSpecialist',
]
