# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

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
