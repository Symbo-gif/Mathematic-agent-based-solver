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
Inequalities and Convexity Specialists
======================================

Tier 3 computational specialists for inequalities and convex analysis.

Classical Inequalities:
- CauchySchwarzSpecialist
- HolderInequalitySpecialist
- JensenInequalitySpecialist
- ChebyshevInequalitySpecialist
- RearrangementInequalitySpecialist

Convex Analysis:
- ConvexSetSpecialist
- ConvexFunctionSpecialist
- SubgradientSpecialist
- SeparationTheoremSpecialist
- ProximalOperatorSpecialist
"""

from symbo_agentic_reasoners.agents.specialists.inequalities.cauchy_schwarz_specialist import CauchySchwarzSpecialist
from symbo_agentic_reasoners.agents.specialists.inequalities.holder_inequality_specialist import HolderInequalitySpecialist
from symbo_agentic_reasoners.agents.specialists.inequalities.jensen_inequality_specialist import JensenInequalitySpecialist
from symbo_agentic_reasoners.agents.specialists.inequalities.chebyshev_inequality_specialist import ChebyshevInequalitySpecialist
from symbo_agentic_reasoners.agents.specialists.inequalities.rearrangement_inequality_specialist import RearrangementInequalitySpecialist
from symbo_agentic_reasoners.agents.specialists.inequalities.convex_set_specialist import ConvexSetSpecialist
from symbo_agentic_reasoners.agents.specialists.inequalities.convex_function_specialist import ConvexFunctionSpecialist
from symbo_agentic_reasoners.agents.specialists.inequalities.subgradient_specialist import SubgradientSpecialist
from symbo_agentic_reasoners.agents.specialists.inequalities.separation_theorem_specialist import SeparationTheoremSpecialist
from symbo_agentic_reasoners.agents.specialists.inequalities.proximal_operator_specialist import ProximalOperatorSpecialist

__all__ = [
    'CauchySchwarzSpecialist',
    'HolderInequalitySpecialist',
    'JensenInequalitySpecialist',
    'ChebyshevInequalitySpecialist',
    'RearrangementInequalitySpecialist',
    'ConvexSetSpecialist',
    'ConvexFunctionSpecialist',
    'SubgradientSpecialist',
    'SeparationTheoremSpecialist',
    'ProximalOperatorSpecialist'
]
