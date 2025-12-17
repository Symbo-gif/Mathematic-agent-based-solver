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
HYPOTHESIS GENERATION TEAM
==========================

The "Scouts" - Tree-of-Thoughts strategic planning.

Addresses the Search Gap (Gap 1) by implementing Tree-of-Thoughts
reasoning that explores the solution space before committing.

AGENTS:
------
1. Hypothesis Generator - Creative strategist
2. Path Evaluator - Heuristic judge
3. Backtracking Manager - State time travel

REFERENCE:
---------
Phase_3_Build_Order_Breakdown.md: Step 3
"""

from .hypothesis_generation import (
    HypothesisGenerationTeam,
    HypothesisGeneratorAgent,
    PathEvaluatorAgent,
    BacktrackingManagerAgent,
    StrategyType,
    SolutionPlan,
    PlanStatus,
    BlackboardSnapshot,
    TreeNode
)

__all__ = [
    'HypothesisGenerationTeam',
    'HypothesisGeneratorAgent',
    'PathEvaluatorAgent',
    'BacktrackingManagerAgent',
    'StrategyType',
    'SolutionPlan',
    'PlanStatus',
    'BlackboardSnapshot',
    'TreeNode'
]
