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
DOMAIN-SPECIFIC EXPLORATION AGENTS
===================================

Specialized exploration agents for each mathematical domain.

These agents maintain domain-specific strategy libraries and provide
expert recommendations for strategy selection within their domains.

IMPLEMENTED EXPLORERS:
---------------------
- CalculusExplorer: Integration, differentiation, limits, series
- AlgebraExplorer: Equations, polynomials, factorization

PLANNED EXPLORERS:
-----------------
- LinearAlgebraExplorer: Matrices, vectors, decompositions
- GeometryExplorer: Euclidean, analytic, trigonometry
- LogicExplorer: Propositional, predicate, proofs
- NumberTheoryExplorer: Primes, divisibility, modular arithmetic
- StatisticsExplorer: Distributions, inference, Bayesian methods
- DiscreteMathExplorer: Combinatorics, graphs
- PhysicsExplorer: Mechanics, EM, thermodynamics, quantum

USAGE:
------
```python
from symbo_agentic_reasoners.exploration.domain_explorers import CalculusExplorer

explorer = CalculusExplorer(
    directory_facilitator=df,
    knowledge_team=km_team
)

strategies = explorer.suggest_strategies(problem, features)
```
"""

# Import implemented explorers
from symbo_agentic_reasoners.exploration.domain_explorers.calculus_explorer import CalculusExplorer
from symbo_agentic_reasoners.exploration.domain_explorers.algebra_explorer import AlgebraExplorer

# Export implemented explorers
__all__ = [
    'CalculusExplorer',
    'AlgebraExplorer',
]
