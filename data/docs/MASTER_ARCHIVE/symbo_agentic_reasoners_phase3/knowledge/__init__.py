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
KNOWLEDGE MANAGEMENT TEAM
=========================

The "Librarians" - Shared memory and RAG integration.

Addresses the Memory Gap (Gap 2) by transforming the system from
stateless isolation to collective consciousness.

AGENTS:
------
1. Context Extractor - Information filter
2. Memory Indexer - Vector DB archivist
3. Retrieval Specialist - RAG integration

REFERENCE:
---------
Phase_3_Build_Order_Breakdown.md: Step 2
"""

from .knowledge_management import (
    KnowledgeManagementTeam,
    ContextExtractorAgent,
    MemoryIndexerAgent,
    RetrievalSpecialistAgent,
    RetrievalConfidence,
    RetrievalResult,
    ContextPacket,
    MemoryEntry
)

__all__ = [
    'KnowledgeManagementTeam',
    'ContextExtractorAgent',
    'MemoryIndexerAgent',
    'RetrievalSpecialistAgent',
    'RetrievalConfidence',
    'RetrievalResult',
    'ContextPacket',
    'MemoryEntry'
]
