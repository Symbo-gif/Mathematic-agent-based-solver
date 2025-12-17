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
SYSTEM AGENTS - Codebase Management Agents
==========================================

System agents for auditing, testing, and improving the codebase.
These agents operate on the codebase itself rather than mathematical problems.

INVENTORY (12 Agents):
---------------------
1. AuditAgent - System integrity checking
2. CleanupAgent - Temporary file management
3. CodeChunkingAgent - Code splitting for analysis
4. CrackfinderTestingAgent - Vulnerability scanning
5. DocumentationAgent - Documentation generation
6. MathematicalCrackfinder - Adversarial test cases
7. SecurityStressTester - Security testing
8. ScriptDecomposer - Script decomposition
9. StructureCataloger - Codebase cataloging
10. AlgorithmBuildingExpert - Algorithm construction and improvement
11. AlgorithmBreakingAgent - Adversarial algorithm testing
"""

from .audit_agent import AuditAgent
from .cleanup_agent import CleanupAgent
from .code_chunking_agent import CodeChunkingAgent
from .crackfinder_agent import CrackFinderAgent
from .documentation_agent import DocumentationAgent
from .mathematical_cracker import MathematicalCrackfinder
from .security_stress_tester import SecurityStressTester
from .script_decomposer import ScriptDecomposer
from .structure_cataloger import StructureCataloger
from .algorithm_building_expert import (
    AlgorithmBuildingExpert,
    AlgorithmSpec,
    AlgorithmAnalysis,
    AlgorithmImprovement,
    AlgorithmType,
)
from .algorithm_breaking_agent import (
    AlgorithmBreakingAgent,
    Vulnerability,
    AttackResult,
    FuzzingCampaign,
    VulnerabilityType,
    AttackStrategy,
)

__all__ = [
    # System Agents
    'AuditAgent',
    'CleanupAgent',
    'CodeChunkingAgent',
    'CrackFinderAgent',
    'DocumentationAgent',
    'MathematicalCrackfinder',
    'SecurityStressTester',
    'ScriptDecomposer',
    'StructureCataloger',
    'AlgorithmBuildingExpert',
    'AlgorithmBreakingAgent',

    # Algorithm Building Expert types
    'AlgorithmSpec',
    'AlgorithmAnalysis',
    'AlgorithmImprovement',
    'AlgorithmType',

    # Algorithm Breaking Agent types
    'Vulnerability',
    'AttackResult',
    'FuzzingCampaign',
    'VulnerabilityType',
    'AttackStrategy',
]
