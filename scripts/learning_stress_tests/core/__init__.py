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
Core infrastructure for learning systems stress testing.
"""

from .learning_test_base import (
    LearningPhase,
    AdaptationMetric,
    LearningTestCase
)
from .resource_monitor import (
    ResourceSnapshot,
    ResourceMonitor
)
from .learning_metrics import (
    LearningMetrics,
    RoutingTableEvolution,
    SimilarityMatrixEvolution,
    NoveltyDetectionQuality
)
from .report_generator import (
    StreamingProgressLog,
    HTMLReportGenerator,
    JSONMetricsExporter
)

__all__ = [
    'LearningPhase',
    'AdaptationMetric',
    'LearningTestCase',
    'ResourceSnapshot',
    'ResourceMonitor',
    'LearningMetrics',
    'RoutingTableEvolution',
    'SimilarityMatrixEvolution',
    'NoveltyDetectionQuality',
    'StreamingProgressLog',
    'HTMLReportGenerator',
    'JSONMetricsExporter',
]
