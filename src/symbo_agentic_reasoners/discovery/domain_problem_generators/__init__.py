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
Domain Problem Generators
==========================

Generates research-level problems for autonomous exploration
across mathematical domains.

Enables curiosity engine to explore:
- Differential Equations
- Number Theory
- Abstract Algebra
- Category Theory
- Real Analysis
- Complex Analysis
- Logic

Each generator creates problems scaled by difficulty and novelty.
"""

__all__ = [
    'ode_problem_generator',
    'number_theory_problem_generator',
    'algebra_problem_generator',
    'category_theory_problem_generator',
    'real_analysis_problem_generator',
    'complex_analysis_problem_generator',
    'logic_problem_generator',
]
