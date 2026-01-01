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

# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
"""
Prover Team Agents - Phase 6
============================

This package contains agents for formal proof construction and verification:

- PRV-1: LogicalProver - Resolution and natural deduction proofs
- PRV-2: ModelChecker - State space exploration and model checking
"""

from .logical_prover import LogicalProver
from .model_checker import ModelChecker

__all__ = [
    'LogicalProver',
    'ModelChecker'
]
