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
Discovery Module - Autonomous Mathematical Exploration
========================================================

This module provides autonomous mathematical exploration capabilities,
allowing the system to generate and solve problems on its own when idle.

Components:
- CuriosityEngine: Main engine coordinating autonomous exploration
- ProblemGenerator: Generates random but meaningful math problems
- InterestScorer: Evaluates how "interesting" discoveries are
- ExplorationResult: Result of an exploration attempt

Usage:
    from symbo_agentic_reasoners.discovery import CuriosityEngine

    engine = CuriosityEngine(solver)
    discoveries = engine.explore_session(60)  # Explore for 60 seconds
"""

from .curiosity_engine import (
    CuriosityEngine,
    ProblemGenerator,
    InterestScorer,
    ExplorationCategory,
    InterestLevel,
    ExplorationResult,
    ExplorationStats,
    explore_mathematics,
)

__all__ = [
    'CuriosityEngine',
    'ProblemGenerator',
    'InterestScorer',
    'ExplorationCategory',
    'InterestLevel',
    'ExplorationResult',
    'ExplorationStats',
    'explore_mathematics',
]
