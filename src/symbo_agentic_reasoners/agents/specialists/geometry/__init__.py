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
GEOMETRY SPECIALISTS
====================

Specialist agents for geometric computations including Euclidean geometry,
analytic geometry, transformations, trigonometry, computational geometry,
and 3D solid geometry.
"""

from symbo_agentic_reasoners.agents.specialists.geometry.euclidean_specialist import EuclideanGeometrySpecialist
from symbo_agentic_reasoners.agents.specialists.geometry.analytic_specialist import AnalyticGeometrySpecialist
from symbo_agentic_reasoners.agents.specialists.geometry.transformation_specialist import TransformationSpecialist
from symbo_agentic_reasoners.agents.specialists.geometry.trigonometry_specialist import TrigonometrySpecialist
from symbo_agentic_reasoners.agents.specialists.geometry.computational_geometry_specialist import (
    ComputationalGeometrySpecialist, Point, LineSegment
)
from symbo_agentic_reasoners.agents.specialists.geometry.solid_geometry_specialist import (
    SolidGeometrySpecialist, Point3D, Vector3D, Plane, Ray3D
)

__all__ = [
    # 2D Geometry
    'EuclideanGeometrySpecialist',
    'AnalyticGeometrySpecialist',
    'TransformationSpecialist',
    'TrigonometrySpecialist',
    # Computational Geometry
    'ComputationalGeometrySpecialist',
    'Point',
    'LineSegment',
    # 3D Solid Geometry
    'SolidGeometrySpecialist',
    'Point3D',
    'Vector3D',
    'Plane',
    'Ray3D',
]
