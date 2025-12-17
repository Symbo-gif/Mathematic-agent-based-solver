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
Calculus Specialists Package
=============================

Provides calculus-related specialist agents:
- differentiation_specialist: Symbolic differentiation
- integration_specialist: Symbolic integration
- ode_solver: Basic ODE solving
- ode_specialist: Advanced ODE solution (separable, linear, constant coefficient)
- fourier_specialist: Fourier analysis (series, DFT, FFT, convolution)
- series_specialist: Taylor/power series expansion

Key Capabilities:
- Symbolic differentiation and integration
- ODE solving (first and second order)
- Fourier series and transforms
- Discrete Fourier Transform (DFT/FFT)
- Signal convolution and filtering
"""

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == 'DifferentiationSpecialist':
        from .differentiation_specialist import DifferentiationSpecialist
        return DifferentiationSpecialist
    elif name == 'IntegrationSpecialist':
        from .integration_specialist import IntegrationSpecialist
        return IntegrationSpecialist
    elif name == 'LimitEvaluator':
        from .limit_evaluator import LimitEvaluator
        return LimitEvaluator
    elif name == 'SeriesSpecialist':
        from .series_specialist import SeriesSpecialist
        return SeriesSpecialist
    elif name == 'ODESolutionSpecialist':
        from .ode_specialist import ODESolutionSpecialist
        return ODESolutionSpecialist
    elif name == 'FourierAnalysisSpecialist':
        from .fourier_specialist import FourierAnalysisSpecialist
        return FourierAnalysisSpecialist
    elif name == 'FourierSeriesResult':
        from .fourier_specialist import FourierSeriesResult
        return FourierSeriesResult
    elif name == 'DFTResult':
        from .fourier_specialist import DFTResult
        return DFTResult
    elif name == 'SpecialFunctionsSpecialist':
        from .special_functions_specialist import SpecialFunctionsSpecialist
        return SpecialFunctionsSpecialist
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Class exports (lazy loaded)
    "DifferentiationSpecialist",
    "IntegrationSpecialist",
    "LimitEvaluator",
    "SeriesSpecialist",
    "ODESolutionSpecialist",
    "FourierAnalysisSpecialist",
    "SpecialFunctionsSpecialist",
    # Supporting types
    "FourierSeriesResult",
    "DFTResult",
    # Module aliases
    "differentiation_specialist",
    "integration_specialist",
    "limit_evaluator",
    "ode_solver",
    "series_specialist",
    "ode_specialist",
    "fourier_specialist",
    "special_functions_specialist",
]