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
Complex Analysis Specialists Package
======================================

Provides comprehensive complex analysis capabilities:
- AnalyticFunctionsSpecialist: Cauchy-Riemann, analyticity, singularities, Laurent series
- ResidueCalculusSpecialist: Residue theorem, contour integration via residues
- ConformalMappingSpecialist: Möbius transforms, Schwarz-Christoffel, domain mappings
- ContourIntegrationSpecialist: Complex line integrals, Cauchy integral formula

NO SYMPY - Pure Python/NumPy implementation.
"""

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == 'AnalyticFunctionsSpecialist':
        from .analytic_functions_specialist import AnalyticFunctionsSpecialist
        return AnalyticFunctionsSpecialist
    elif name == 'AnalyticResult':
        from .analytic_functions_specialist import AnalyticResult
        return AnalyticResult
    elif name == 'CauchyRiemannResult':
        from .analytic_functions_specialist import CauchyRiemannResult
        return CauchyRiemannResult
    elif name == 'LaurentSeries':
        from .analytic_functions_specialist import LaurentSeries
        return LaurentSeries
    elif name == 'SingularityType':
        from .analytic_functions_specialist import SingularityType
        return SingularityType
    elif name == 'ResidueCalculusSpecialist':
        from .residue_calculus_specialist import ResidueCalculusSpecialist
        return ResidueCalculusSpecialist
    elif name == 'Residue':
        from .residue_calculus_specialist import Residue
        return Residue
    elif name == 'ContourType':
        from .residue_calculus_specialist import ContourType
        return ContourType
    elif name == 'RealIntegralResult':
        from .residue_calculus_specialist import RealIntegralResult
        return RealIntegralResult
    elif name == 'ConformalMappingSpecialist':
        from .conformal_mapping_specialist import ConformalMappingSpecialist
        return ConformalMappingSpecialist
    elif name == 'MobiusTransform':
        from .conformal_mapping_specialist import MobiusTransform
        return MobiusTransform
    elif name == 'ConformalMapResult':
        from .conformal_mapping_specialist import ConformalMapResult
        return ConformalMapResult
    elif name == 'DomainType':
        from .conformal_mapping_specialist import DomainType
        return DomainType
    elif name == 'ContourIntegrationSpecialist':
        from .contour_integration_specialist import ContourIntegrationSpecialist
        return ContourIntegrationSpecialist
    elif name == 'Contour':
        from .contour_integration_specialist import Contour
        return Contour
    elif name == 'ContourIntegralResult':
        from .contour_integration_specialist import ContourIntegralResult
        return ContourIntegralResult
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Analytic functions
    "AnalyticFunctionsSpecialist",
    "AnalyticResult",
    "CauchyRiemannResult",
    "LaurentSeries",
    "SingularityType",
    # Residue calculus
    "ResidueCalculusSpecialist",
    "Residue",
    "ContourType",
    "RealIntegralResult",
    # Conformal mapping
    "ConformalMappingSpecialist",
    "MobiusTransform",
    "ConformalMapResult",
    "DomainType",
    # Contour integration
    "ContourIntegrationSpecialist",
    "Contour",
    "ContourIntegralResult",
]
