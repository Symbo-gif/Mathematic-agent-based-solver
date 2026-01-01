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
Real Analysis Specialists Package
===================================

Provides comprehensive real analysis capabilities:
- MeasureTheorySpecialist: Lebesgue measure and integration, convergence theorems
- MetricSpaceSpecialist: Completeness, compactness, continuity, fixed points
- SequencesSeriesSpecialist: Convergence tests, uniform convergence, power series

NO SYMPY - Pure Python/NumPy implementation.
"""

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == 'MeasureTheorySpecialist':
        from .measure_theory_specialist import MeasureTheorySpecialist
        return MeasureTheorySpecialist
    elif name == 'MeasureResult':
        from .measure_theory_specialist import MeasureResult
        return MeasureResult
    elif name == 'IntegralResult':
        from .measure_theory_specialist import IntegralResult
        return IntegralResult
    elif name == 'LpNormResult':
        from .measure_theory_specialist import LpNormResult
        return LpNormResult
    elif name == 'MeasureType':
        from .measure_theory_specialist import MeasureType
        return MeasureType
    elif name == 'MetricSpaceSpecialist':
        from .metric_space_specialist import MetricSpaceSpecialist
        return MetricSpaceSpecialist
    elif name == 'MetricResult':
        from .metric_space_specialist import MetricResult
        return MetricResult
    elif name == 'FixedPointResult':
        from .metric_space_specialist import FixedPointResult
        return FixedPointResult
    elif name == 'ContinuityResult':
        from .metric_space_specialist import ContinuityResult
        return ContinuityResult
    elif name == 'SequencesSeriesSpecialist':
        from .sequences_series_specialist import SequencesSeriesSpecialist
        return SequencesSeriesSpecialist
    elif name == 'SequenceAnalysis':
        from .sequences_series_specialist import SequenceAnalysis
        return SequenceAnalysis
    elif name == 'SeriesAnalysis':
        from .sequences_series_specialist import SeriesAnalysis
        return SeriesAnalysis
    elif name == 'UniformConvergenceResult':
        from .sequences_series_specialist import UniformConvergenceResult
        return UniformConvergenceResult
    elif name == 'ConvergenceResult':
        from .sequences_series_specialist import ConvergenceResult
        return ConvergenceResult
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Measure theory
    "MeasureTheorySpecialist",
    "MeasureResult",
    "IntegralResult",
    "LpNormResult",
    "MeasureType",
    # Metric spaces
    "MetricSpaceSpecialist",
    "MetricResult",
    "FixedPointResult",
    "ContinuityResult",
    # Sequences and series
    "SequencesSeriesSpecialist",
    "SequenceAnalysis",
    "SeriesAnalysis",
    "UniformConvergenceResult",
    "ConvergenceResult",
]
