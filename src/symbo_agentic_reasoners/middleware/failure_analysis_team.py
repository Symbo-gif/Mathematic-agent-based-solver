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
FAILURE ANALYSIS TEAM - Team Orchestration Module
==================================================

This module provides the team-level orchestration for the Failure Analysis Team.
It imports and re-exports the team coordinator and related classes from the
main failure_analysis module.

PURPOSE:
-------
Provides a clean import path for tests and other modules that need to access
the Failure Analysis Team functionality.

USAGE:
-----
    from symbo_agentic_reasoners.middleware.failure_analysis_team import (
        FailureAnalysisTeam,
        ErrorType,
        RemedyAction
    )
"""

# Import all necessary classes from the main failure_analysis module
from symbo_agentic_reasoners.middleware.failure_analysis import (
    FailureAnalysisTeam,
    ErrorType,
    RemedyAction,
    FailureStatus,
    FailureReport,
    ExecutionStep,
    ErrorClassifier,
    RootCauseAnalyzer,
    AlternativePathGenerator
)

# Export the main classes that tests and other modules need
__all__ = [
    'FailureAnalysisTeam',
    'ErrorType',
    'RemedyAction',
    'FailureStatus',
    'FailureReport',
    'ExecutionStep',
    'ErrorClassifier',
    'RootCauseAnalyzer',
    'AlternativePathGenerator'
]
