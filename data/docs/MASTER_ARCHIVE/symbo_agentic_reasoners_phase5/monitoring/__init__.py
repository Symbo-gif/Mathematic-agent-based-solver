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
Phase 5 Production Monitoring
==============================

Provides runtime monitoring for production deployments including:
- PyTorch/CUDA availability tracking
- Dependency health checks
- Performance metrics collection
- Resource utilization monitoring
"""

from .dependency_monitor import (
    DependencyMonitor,
    DependencyStatus,
    get_dependency_report,
    check_pytorch_availability,
    log_dependency_status
)

__all__ = [
    'DependencyMonitor',
    'DependencyStatus',
    'get_dependency_report',
    'check_pytorch_availability',
    'log_dependency_status'
]
