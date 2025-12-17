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
Optimization Specialists Package
================================

Native Python implementations for optimization problems.
NO external dependencies beyond numpy.

Specialists:
- LinearProgrammingSpecialist: Simplex method, sensitivity analysis
- ConvexOptimizationSpecialist: Gradient descent, Newton's method, QP
- CombinatorialOptimizationSpecialist: Knapsack, TSP, assignment, set cover
"""

from .linear_programming_specialist import LinearProgrammingSpecialist
from .convex_optimization_specialist import ConvexOptimizationSpecialist
from .combinatorial_specialist import CombinatorialOptimizationSpecialist

__all__ = [
    'LinearProgrammingSpecialist',
    'ConvexOptimizationSpecialist',
    'CombinatorialOptimizationSpecialist',
]
