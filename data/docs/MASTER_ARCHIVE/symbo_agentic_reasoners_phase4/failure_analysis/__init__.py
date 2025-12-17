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
FAILURE ANALYSIS TEAM - "The Trauma Surgeons"
==============================================

Phase 4 Governance: Graceful Incompleteness Handling System

PURPOSE:
-------
Intercepts all failure signals, diagnoses the root cause, and autonomously
reroutes the system to alternative solution strategies. Ensures the system
never "gives up" with a generic error.

WHY THIS MATTERS:
----------------
Standard mathematical systems return generic ERROR messages when solvers fail,
aborting entire sessions. This team implements "Graceful Incompleteness Handling"
by diagnosing the specific failure type and routing to appropriate treatment.

AGENTS:
------
1. Error Classifier - Diagnostic interceptor (Computational/Logical/Domain)
2. Root Cause Analyzer - Failure attribution system
3. Alternative Path Generator - Plan B engine

REFERENCE:
---------
Phase_4_Build_Order_Breakdown.md: Step 2 (The Failure Analysis Team)
"""

from .failure_analysis_team import (
    FailureAnalysisTeam,
    ErrorClassifier,
    RootCauseAnalyzer,
    AlternativePathGenerator,
    ErrorType,
    RemedyAction,
    FailureReport
)

__all__ = [
    'FailureAnalysisTeam',
    'ErrorClassifier',
    'RootCauseAnalyzer',
    'AlternativePathGenerator',
    'ErrorType',
    'RemedyAction',
    'FailureReport'
]
