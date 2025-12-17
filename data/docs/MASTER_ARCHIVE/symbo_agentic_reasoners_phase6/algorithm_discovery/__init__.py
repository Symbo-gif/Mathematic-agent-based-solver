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
Algorithm Discovery Unit - "FunSearch Pattern"
================================================

Phase 6, Step 3: Finding Algorithms, Not Just Answers

Standard mathematical systems find *answers* (numbers, proofs). The Algorithm
Discovery Unit shifts focus to finding *algorithms* (functions). Based on the
FunSearch paradigm, the output is executable code that solves a *class* of
problems more efficiently.

This allows the system to solve open problems in Combinatorics (a known weakness
of standard solvers) by discovering new, verifiable algorithmic approaches.

Agents:
1. CodeEvolutionaryProposer - LLM-based code evolution with mutations
2. SandboxEvaluator - Secure execution environment for testing
3. HeuristicDistiller - Extracts mathematical principles from successful code

Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx, Section 3
Reference: Phase_6_Build_Order_Breakdown.md, Step 3
"""

from .code_evolutionary_proposer import CodeEvolutionaryProposer, CodeCandidate
from .sandbox_evaluator import SandboxEvaluator, EvaluationResult
from .heuristic_distiller import HeuristicDistiller, DistilledHeuristic
from .problem_specification import ProblemSpecification

__all__ = [
    'CodeEvolutionaryProposer',
    'CodeCandidate',
    'SandboxEvaluator',
    'EvaluationResult',
    'HeuristicDistiller',
    'DistilledHeuristic',
    'ProblemSpecification'
]
