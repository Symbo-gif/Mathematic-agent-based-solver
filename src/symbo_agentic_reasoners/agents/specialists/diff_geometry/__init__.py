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
Differential Geometry & Topology Specialists Package
======================================================

Provides comprehensive differential geometry and topology capabilities:
- DifferentialGeometrySpecialist: Metrics, curvature, geodesics, Christoffel symbols
- TopologySpecialist: Simplicial complexes, homology, Euler characteristic

NO SYMPY - Pure Python/NumPy implementation.
"""

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == 'DifferentialGeometrySpecialist':
        from .differential_geometry_specialist import DifferentialGeometrySpecialist
        return DifferentialGeometrySpecialist
    elif name == 'MetricTensor':
        from .differential_geometry_specialist import MetricTensor
        return MetricTensor
    elif name == 'ChristoffelSymbols':
        from .differential_geometry_specialist import ChristoffelSymbols
        return ChristoffelSymbols
    elif name == 'CurvatureResult':
        from .differential_geometry_specialist import CurvatureResult
        return CurvatureResult
    elif name == 'GeodesicResult':
        from .differential_geometry_specialist import GeodesicResult
        return GeodesicResult
    elif name == 'TopologySpecialist':
        from .topology_specialist import TopologySpecialist
        return TopologySpecialist
    elif name == 'SimplicialComplex':
        from .topology_specialist import SimplicialComplex
        return SimplicialComplex
    elif name == 'HomologyResult':
        from .topology_specialist import HomologyResult
        return HomologyResult
    elif name == 'TopologyResult':
        from .topology_specialist import TopologyResult
        return TopologyResult
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Differential geometry
    "DifferentialGeometrySpecialist",
    "MetricTensor",
    "ChristoffelSymbols",
    "CurvatureResult",
    "GeodesicResult",
    # Topology
    "TopologySpecialist",
    "SimplicialComplex",
    "HomologyResult",
    "TopologyResult",
]
