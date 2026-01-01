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
Security Hardening Package
==========================

This package provides security hardening features for the system:

Modules:
- security_monitor: Access control and security monitoring
- resilience_tester: System resilience testing
- process_isolation: Sandboxed execution for untrusted inputs

Key Security Features:
1. Regex injection protection
2. Parser-level timeouts
3. Process-level isolation
4. Access control policies
5. Rate limiting
6. Anomaly detection
"""

from .process_isolation import (
    IsolatedExecutor,
    IsolationResult,
    IsolationError,
    IsolationTimeoutError,
    IsolationMemoryError,
    execute_isolated,
    execute_smart,
    is_safe_for_direct_execution,
)

__all__ = [
    # Process isolation
    'IsolatedExecutor',
    'IsolationResult',
    'IsolationError',
    'IsolationTimeoutError',
    'IsolationMemoryError',
    'execute_isolated',
    'execute_smart',
    'is_safe_for_direct_execution',
]
