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
Benchmark Testing Infrastructure

This package provides comprehensive benchmark testing for the Symbo Agentic Reasoners system
across multiple mathematical datasets including GSM8K, MATH, AIME, ODE suites, and
university-level problems.

Modules:
    base_benchmark: Abstract base class for all benchmarks
    answer_extractors: Answer parsing utilities
    answer_comparators: Answer equivalence checking
    benchmark_registry: Central registry for benchmark management
    gsm8k_benchmark: GSM8K dataset runner
    math_benchmark: MATH dataset runner
    aime_benchmark: AIME problems runner
    ode_benchmark: ODE test suite runner
    university_benchmark: University-level problems runner
"""

from .base_benchmark import BaseBenchmark, BenchmarkResult
from .answer_extractors import (
    extract_numeric_answer,
    extract_gsm8k_answer,
    extract_math_boxed_answer,
    extract_aime_answer
)
from .answer_comparators import (
    compare_numeric_answers,
    compare_symbolic_expressions,
    compare_latex_expressions,
    compare_ode_solutions
)

__all__ = [
    'BaseBenchmark',
    'BenchmarkResult',
    'extract_numeric_answer',
    'extract_gsm8k_answer',
    'extract_math_boxed_answer',
    'extract_aime_answer',
    'compare_numeric_answers',
    'compare_symbolic_expressions',
    'compare_latex_expressions',
    'compare_ode_solutions',
]
