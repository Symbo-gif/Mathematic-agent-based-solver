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
Functional Analysis Specialists Package
=========================================

Provides comprehensive functional analysis capabilities:
- BanachSpaceSpecialist: Norms, bounded operators, dual spaces, Banach theorems
- HilbertSpaceSpecialist: Inner products, orthogonality, projections, Fourier
- OperatorTheorySpecialist: Spectrum, resolvent, operator classification

NO SYMPY - Pure Python/NumPy implementation.
"""

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == 'BanachSpaceSpecialist':
        from .banach_space_specialist import BanachSpaceSpecialist
        return BanachSpaceSpecialist
    elif name == 'NormResult':
        from .banach_space_specialist import NormResult
        return NormResult
    elif name == 'OperatorNormResult':
        from .banach_space_specialist import OperatorNormResult
        return OperatorNormResult
    elif name == 'DualSpaceResult':
        from .banach_space_specialist import DualSpaceResult
        return DualSpaceResult
    elif name == 'HilbertSpaceSpecialist':
        from .hilbert_space_specialist import HilbertSpaceSpecialist
        return HilbertSpaceSpecialist
    elif name == 'InnerProductResult':
        from .hilbert_space_specialist import InnerProductResult
        return InnerProductResult
    elif name == 'ProjectionResult':
        from .hilbert_space_specialist import ProjectionResult
        return ProjectionResult
    elif name == 'FourierResult':
        from .hilbert_space_specialist import FourierResult
        return FourierResult
    elif name == 'OperatorTheorySpecialist':
        from .operator_theory_specialist import OperatorTheorySpecialist
        return OperatorTheorySpecialist
    elif name == 'SpectrumResult':
        from .operator_theory_specialist import SpectrumResult
        return SpectrumResult
    elif name == 'ResolventResult':
        from .operator_theory_specialist import ResolventResult
        return ResolventResult
    elif name == 'OperatorClassification':
        from .operator_theory_specialist import OperatorClassification
        return OperatorClassification
    elif name == 'OperatorType':
        from .operator_theory_specialist import OperatorType
        return OperatorType
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Banach space
    "BanachSpaceSpecialist",
    "NormResult",
    "OperatorNormResult",
    "DualSpaceResult",
    # Hilbert space
    "HilbertSpaceSpecialist",
    "InnerProductResult",
    "ProjectionResult",
    "FourierResult",
    # Operator theory
    "OperatorTheorySpecialist",
    "SpectrumResult",
    "ResolventResult",
    "OperatorClassification",
    "OperatorType",
]
