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
META-LEARNING TEAM - Team Orchestration Module
===============================================

This module provides the team-level orchestration for the Meta-Learning Team.
It imports and re-exports the team coordinator and related classes from the
main meta_learning module.

PURPOSE:
-------
Provides a clean import path for tests and other modules that need to access
the Meta-Learning Team functionality.

USAGE:
-----
    from symbo_agentic_reasoners.middleware.meta_learning_team import (
        MetaLearningTeam,
        ComplexityLevel
    )
"""

# Import all necessary classes from the main meta_learning module
from symbo_agentic_reasoners.middleware.meta_learning import (
    MetaLearningTeam,
    ComplexityLevel,
    SolutionTrace,
    RoutingHeuristic,
    PerformanceMonitor,
    AgentSelectorOptimizer,
    AdaptiveDispatcher
)

# Export the main classes that tests and other modules need
__all__ = [
    'MetaLearningTeam',
    'ComplexityLevel',
    'SolutionTrace',
    'RoutingHeuristic',
    'PerformanceMonitor',
    'AgentSelectorOptimizer',
    'AdaptiveDispatcher'
]
