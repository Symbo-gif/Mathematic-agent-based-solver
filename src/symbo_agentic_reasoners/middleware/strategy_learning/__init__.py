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
Strategy Learning Package
==========================

Meta-cognitive strategy learning for mathematical problem solving.

COMPONENTS:
-----------
- strategy_patterns: Core data structures for strategies
- structural_strategy_learner: Agent 3.4 - Learns Pólya cycle, re-encoding, local-global
- heuristic_pattern_learner: Agent 3.5 - Learns invariants, extremal, symmetrization, functional
- nonstandard_move_learner: Agent 3.6 - Learns descent, graphical, fixed-point
- meta_strategy_learner: Agent 3.7 - Learns template mining, multi-solution
- strategy_coordinator: Agent 3.8 - Orchestrates learning, manages KnowledgeGraph
- strategy_detectors: Individual detector implementations

PURPOSE:
--------
Automatically learn high-level problem-solving strategies from every solution,
storing patterns in KnowledgeGraph for future recommendation and cross-domain transfer.

EXTENDS:
--------
MetaLearningTeam (AutoMaAS) with 5 new agents (3.4-3.8)
"""

from symbo_agentic_reasoners.middleware.strategy_learning.strategy_patterns import (
    StrategyPattern,
    StrategyDetection,
    StrategyDetectionResult,
    TemplatePattern,
    StrategyApplication,
    StrategyCategory,
    DetectionConfidence,
)

from symbo_agentic_reasoners.middleware.strategy_learning.structural_strategy_learner import (
    StructuralStrategyLearner
)
from symbo_agentic_reasoners.middleware.strategy_learning.heuristic_pattern_learner import (
    HeuristicPatternLearner
)
from symbo_agentic_reasoners.middleware.strategy_learning.nonstandard_move_learner import (
    NonStandardMoveLearner
)
from symbo_agentic_reasoners.middleware.strategy_learning.meta_strategy_learner import (
    MetaStrategyLearner
)
from symbo_agentic_reasoners.middleware.strategy_learning.strategy_coordinator import (
    StrategyCoordinator, AggregatedDetection
)
from symbo_agentic_reasoners.middleware.strategy_learning.strategy_transfer_engine import (
    StrategyTransferEngine, TransferCandidate, TransferResult, DomainMapping
)

__all__ = [
    'StrategyPattern',
    'StrategyDetection',
    'StrategyDetectionResult',
    'TemplatePattern',
    'StrategyApplication',
    'StrategyCategory',
    'DetectionConfidence',
    'StructuralStrategyLearner',
    'HeuristicPatternLearner',
    'NonStandardMoveLearner',
    'MetaStrategyLearner',
    'StrategyCoordinator',
    'AggregatedDetection',
    'StrategyTransferEngine',
    'TransferCandidate',
    'TransferResult',
    'DomainMapping',
]

__version__ = '1.0.0'
