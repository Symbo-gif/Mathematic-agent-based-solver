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
EXPLORATION LAYER (TIER 1.5)
============================

Strategic exploration agents for systematic solution space search and learning.

This package implements the exploration layer that sits between the MainOrchestrator
(Tier 1) and domain Supervisors (Tier 2). It provides intelligent strategy selection,
ranking, and learning from past exploration attempts.

COMPONENTS:
----------
- data_structures: Core types (Strategy, ExplorationResult, StrategyRanking)
- strategy_library: Initial library of 50+ strategies across all domains
- base_explorer: BaseExplorationAgent abstract class
- universal_explorer: UniversalStrategyExplorer (meta-level orchestration)
- domain_explorers: Domain-specific exploration agents (9 domains)

USAGE:
-----
```python
from symbo_agentic_reasoners.exploration import UniversalStrategyExplorer

explorer = UniversalStrategyExplorer(
    directory_facilitator=df,
    knowledge_team=km_team
)

ranking = explorer.explore_strategies(problem)
```
"""

from symbo_agentic_reasoners.exploration.data_structures import (
    Strategy,
    ExplorationResult,
    StrategyRanking,
    ExplorationOutcome,
    hash_problem,
    estimate_complexity
)

from symbo_agentic_reasoners.exploration.base_explorer import BaseExplorationAgent
from symbo_agentic_reasoners.exploration.universal_explorer import UniversalStrategyExplorer

__all__ = [
    'Strategy',
    'ExplorationResult',
    'StrategyRanking',
    'ExplorationOutcome',
    'hash_problem',
    'estimate_complexity',
    'BaseExplorationAgent',
    'UniversalStrategyExplorer',
]
