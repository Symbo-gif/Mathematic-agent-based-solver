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
Formal Knowledge Integration Team - "The Archivist"
=====================================================

Phase 6, Step 5: Closing the Evolutionary Loop

New theorems proven by the Explorer or algorithms discovered by the
FunSearch unit must be permanently integrated into the system's
capability set. This creates a compounding intelligence effect:

If the system discovers a new identity for Prime Numbers today,
the Algebra Supervisor (Phase 2) can utilize that identity as a
primitive tool tomorrow.

Agents:
1. AutoFormalizationPipeline - Converts discoveries to OMDoc/OpenMath
2. VectorDatabaseUpdater - Updates RAG memory with new discoveries

Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx, Section 5
Reference: Phase_6_Build_Order_Breakdown.md, Step 5
"""

from .auto_formalization_pipeline import AutoFormalizationPipeline, FormalizedDiscovery, DiscoveryType
from .vector_database_updater import VectorDatabaseUpdater, DiscoveryIndex

__all__ = [
    'AutoFormalizationPipeline',
    'FormalizedDiscovery',
    'DiscoveryType',
    'VectorDatabaseUpdater',
    'DiscoveryIndex'
]
