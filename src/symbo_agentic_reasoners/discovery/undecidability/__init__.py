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

"""Undecidability Navigator stubs"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Callable, List

class DecidabilityClass(Enum):
    DECIDABLE = 'decidable'
    UNDECIDABLE = 'undecidable'
    UNKNOWN = 'unknown'

@dataclass
class DecidabilityAssessment:
    decidability_class: DecidabilityClass
    resource_bounds: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProofStateSummary:
    problem_id: str = ""
    current_state: str = ""

class DecidabilityChecker:
    def __init__(self): pass
    def assess(self, candidate): return DecidabilityAssessment(DecidabilityClass.DECIDABLE)
    def health_check(self): return True
    def reset(self): pass

class InteractiveGuidanceLiaison:
    def __init__(self, notification_callback: Callable = None): pass
    def request_guidance(self, problem, search_state): return type("Request", (), {"summary": ProofStateSummary()})()
    def receive_guidance(self, request_id, guidance): return True
    def get_pending_requests(self): return []
    def health_check(self): return True
    def reset(self): pass
    def get_statistics(self): return {}

__all__ = ["DecidabilityClass", "DecidabilityChecker", "InteractiveGuidanceLiaison", "ProofStateSummary", "DecidabilityAssessment"]
