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
PRECONDITION VALIDATION TEAM
============================

The "Anesthesiologist" - Pre-flight checklist for mathematical validity.

Addresses the Assumption Gap (Gap 3) by ensuring every problem is
mathematically sound and well-defined before any solver touches it.

AGENTS:
------
1. Domain Checker - Solvability gatekeeper
2. Assumption Validator - Constraint compliance checker
3. Edge Case Detector - Red Team saboteur
4. Constraint Propagator - Hierarchical constraint injection

REFERENCE:
---------
Phase_3_Build_Order_Breakdown.md: Step 1
"""

from .precondition_validation import (
    PreconditionValidationTeam,
    DomainCheckerAgent,
    AssumptionValidatorAgent,
    EdgeCaseDetectorAgent,
    ConstraintPropagatorAgent,
    ValidationStatus,
    ValidationResult,
    MathematicalDomain,
    MathematicalConstraint
)

__all__ = [
    'PreconditionValidationTeam',
    'DomainCheckerAgent',
    'AssumptionValidatorAgent',
    'EdgeCaseDetectorAgent',
    'ConstraintPropagatorAgent',
    'ValidationStatus',
    'ValidationResult',
    'MathematicalDomain',
    'MathematicalConstraint'
]
