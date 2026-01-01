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
SYMBO Training Module
=====================

This module provides the continuous learning infrastructure for the SYMBO system,
implementing the Phase 5 "Evolutionary Flywheel" architecture.

Components:
-----------
- SymboTeachingLoop: Wires solver output to distillation pipeline
- solve_and_learn: Convenience function for solving with automatic learning
- get_teaching_loop: Get the global teaching loop instance

Usage:
------
    from symbo_agentic_reasoners.training import solve_and_learn, get_teaching_loop

    # Solve a problem and capture learning trace
    result, captured = solve_and_learn("diff(x**2, x)")

    # Get statistics
    loop = get_teaching_loop()
    stats = loop.get_statistics()

    # Manually trigger distillation
    loop.run_distillation()
"""

from .symbo_teaching_loop import (
    SymboTeachingLoop,
    get_teaching_loop,
    solve_and_learn,
    LearningStatistics,
)

__all__ = [
    'SymboTeachingLoop',
    'get_teaching_loop',
    'solve_and_learn',
    'LearningStatistics',
]
