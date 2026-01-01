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
SOLID GEOMETRY SPECIALIST (Tier 3)
==================================

3D geometry operations for solid objects.

CAPABILITIES:
------------
- 3D point and vector operations
- Plane operations
- 3D line operations
- Solid volume and surface area
- Ray-plane/ray-sphere intersection
- 3D transformations

NO SYMPY - All mathematical operations use native implementations.
"""

import logging
import math
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard

logger = logging.getLogger('symbo_agentic_reasoners.specialists.solid_geometry')


@dataclass
class Point3D:
    """3D Point."""
    x: float
    y: float
    z: float

    def __sub__(self, other: 'Point3D') -> 'Vector3D':
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __add__(self, other: 'Vector3D') -> 'Point3D':
        return Point3D(self.x + other.x, self.y + other.y, self.z + other.z)


@dataclass
class Vector3D:
    """3D Vector."""
    x: float
    y: float
    z: float

    def dot(self, other: 'Vector3D') -> float:
        """Perform dot operation.

        Args:
        other

        Returns:
        Result of the operation

        Example:
        >>> specialist = Vector3D()
        >>> result = specialist.dot(...)
        # Returns result
        """
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: 'Vector3D') -> 'Vector3D':
        """Perform cross operation.

        Args:
        other

        Returns:
        Result of the operation

        Example:
        >>> specialist = Vector3D()
        >>> result = specialist.cross(...)
        # Returns result
        """
        return Vector3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def magnitude(self) -> float:
        """Perform magnitude operation.

        Args:


        Returns:
        Result of the operation

        Example:
        >>> specialist = Vector3D()
        >>> result = specialist.magnitude(...)
        # Returns result
        """
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def normalize(self) -> 'Vector3D':
        """Perform normalize operation.

        Args:


        Returns:
        Result of the operation

        Example:
        >>> specialist = Vector3D()
        >>> result = specialist.normalize(...)
        # Returns result
        """
        mag = self.magnitude()
        if mag == 0:
            return Vector3D(0, 0, 0)
        return Vector3D(self.x / mag, self.y / mag, self.z / mag)

    def scale(self, s: float) -> 'Vector3D':
        """Perform scale operation.

        Args:
        s

        Returns:
        Result of the operation

        Example:
        >>> specialist = Vector3D()
        >>> result = specialist.scale(...)
        # Returns result
        """
        return Vector3D(self.x * s, self.y * s, self.z * s)


@dataclass
class Plane:
    """Plane defined by ax + by + cz + d = 0."""
    a: float
    b: float
    c: float
    d: float

    def normal(self) -> Vector3D:
        """Perform normal operation.

        Args:


        Returns:
        Result of the operation

        Example:
        >>> specialist = Plane()
        >>> result = specialist.normal(...)
        # Returns result
        """
        return Vector3D(self.a, self.b, self.c).normalize()


@dataclass
class Ray3D:
    """3D Ray with origin and direction."""
    origin: Point3D
    direction: Vector3D


class SolidGeometrySpecialist(BDIAgent):
    """
    Solid Geometry Specialist - 3D Geometry Operations

    DIRECTIVE:
    ---------
    Provide 3D geometry operations for solid objects.

    OPERATIONS:
    ----------
    - distance_point_point: Distance between 3D points
    - distance_point_plane: Distance from point to plane
    - plane_from_points: Create plane from three points
    - ray_plane_intersection: Find ray-plane intersection
    - ray_sphere_intersection: Find ray-sphere intersection
    - volume_tetrahedron: Volume of tetrahedron
    - surface_area_sphere: Surface area of sphere
    """

    def __init__(
        self,
        agent_id: str = "solid_geometry_specialist",
        directory_facilitator: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
    ):
        super().__init__(agent_id=agent_id)
        self.agent_type = "solid_geometry_specialist"
        self.df = directory_facilitator
        self.blackboard = blackboard
        self._register_services()
        self._stats = {'operations': 0}

    def _register_services(self):
        """Perform  register services operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj._register_services(...)
        """
        """Perform  register services operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj._register_services(...)
        """
        if self.df:
            self.df.register_service(create_service_registration(
                agent_id=self.agent_id,
                service_type="solid_geometry",
                description="3D solid geometry operations"
            ))

    # ==================== DISTANCE OPERATIONS ====================

    def distance_point_point(self, p1: Point3D, p2: Point3D) -> float:
        """Distance between two 3D points."""
        self._stats['operations'] += 1
        return (p2 - p1).magnitude()

    def distance_point_plane(self, point: Point3D, plane: Plane) -> float:
        """Distance from point to plane."""
        self._stats['operations'] += 1
        num = abs(plane.a * point.x + plane.b * point.y + plane.c * point.z + plane.d)
        denom = math.sqrt(plane.a ** 2 + plane.b ** 2 + plane.c ** 2)
        return num / denom if denom > 0 else 0

    def distance_point_line(
        self,
        point: Point3D,
        line_point: Point3D,
        line_dir: Vector3D
    ) -> float:
        """Distance from point to 3D line."""
        self._stats['operations'] += 1
        v = point - line_point
        cross = Vector3D(v.x, v.y, v.z).cross(line_dir)
        return cross.magnitude() / line_dir.magnitude()

    # ==================== PLANE OPERATIONS ====================

    def plane_from_points(self, p1: Point3D, p2: Point3D, p3: Point3D) -> Plane:
        """Create plane from three non-collinear points."""
        self._stats['operations'] += 1
        v1 = p2 - p1
        v2 = p3 - p1
        normal = v1.cross(v2)

        a, b, c = normal.x, normal.y, normal.z
        d = -(a * p1.x + b * p1.y + c * p1.z)

        return Plane(a, b, c, d)

    def project_point_to_plane(self, point: Point3D, plane: Plane) -> Point3D:
        """Project point onto plane."""
        self._stats['operations'] += 1
        dist = (plane.a * point.x + plane.b * point.y +
                plane.c * point.z + plane.d)
        norm_sq = plane.a ** 2 + plane.b ** 2 + plane.c ** 2

        if norm_sq == 0:
            return point

        t = dist / norm_sq
        return Point3D(
            point.x - plane.a * t,
            point.y - plane.b * t,
            point.z - plane.c * t
        )

    # ==================== RAY INTERSECTION ====================

    def ray_plane_intersection(
        self,
        ray: Ray3D,
        plane: Plane
    ) -> Optional[Point3D]:
        """Find ray-plane intersection."""
        self._stats['operations'] += 1

        normal = Vector3D(plane.a, plane.b, plane.c)
        denom = normal.dot(ray.direction)

        if abs(denom) < 1e-10:
            return None  # Parallel

        t = -(plane.a * ray.origin.x + plane.b * ray.origin.y +
              plane.c * ray.origin.z + plane.d) / denom

        if t < 0:
            return None  # Behind ray

        return ray.origin + ray.direction.scale(t)

    def ray_sphere_intersection(
        self,
        ray: Ray3D,
        center: Point3D,
        radius: float
    ) -> List[Point3D]:
        """Find ray-sphere intersection(s)."""
        self._stats['operations'] += 1

        oc = ray.origin - center
        a = ray.direction.dot(ray.direction)
        b = 2 * Vector3D(oc.x, oc.y, oc.z).dot(ray.direction)
        c = Vector3D(oc.x, oc.y, oc.z).dot(Vector3D(oc.x, oc.y, oc.z)) - radius ** 2

        discriminant = b ** 2 - 4 * a * c

        if discriminant < 0:
            return []

        if abs(discriminant) < 1e-10:
            t = -b / (2 * a)
            if t >= 0:
                return [ray.origin + ray.direction.scale(t)]
            return []

        sqrt_d = math.sqrt(discriminant)
        t1 = (-b - sqrt_d) / (2 * a)
        t2 = (-b + sqrt_d) / (2 * a)

        points = []
        if t1 >= 0:
            points.append(ray.origin + ray.direction.scale(t1))
        if t2 >= 0:
            points.append(ray.origin + ray.direction.scale(t2))

        return points

    # ==================== VOLUME AND SURFACE AREA ====================

    def volume_tetrahedron(
        self,
        p1: Point3D,
        p2: Point3D,
        p3: Point3D,
        p4: Point3D
    ) -> float:
        """Volume of tetrahedron with vertices p1, p2, p3, p4."""
        self._stats['operations'] += 1
        v1 = p2 - p1
        v2 = p3 - p1
        v3 = p4 - p1

        cross = v1.cross(v2)
        scalar_triple = cross.dot(v3)

        return abs(scalar_triple) / 6

    def volume_sphere(self, radius: float) -> float:
        """Volume of sphere."""
        self._stats['operations'] += 1
        return (4 / 3) * math.pi * radius ** 3

    def volume_cylinder(self, radius: float, height: float) -> float:
        """Volume of cylinder."""
        self._stats['operations'] += 1
        return math.pi * radius ** 2 * height

    def volume_cone(self, radius: float, height: float) -> float:
        """Volume of cone."""
        self._stats['operations'] += 1
        return (1 / 3) * math.pi * radius ** 2 * height

    def volume_box(self, length: float, width: float, height: float) -> float:
        """Volume of rectangular box."""
        self._stats['operations'] += 1
        return length * width * height

    def surface_area_sphere(self, radius: float) -> float:
        """Surface area of sphere."""
        self._stats['operations'] += 1
        return 4 * math.pi * radius ** 2

    def surface_area_cylinder(self, radius: float, height: float) -> float:
        """Surface area of cylinder (including caps)."""
        self._stats['operations'] += 1
        lateral = 2 * math.pi * radius * height
        caps = 2 * math.pi * radius ** 2
        return lateral + caps

    def surface_area_cone(self, radius: float, height: float) -> float:
        """Surface area of cone (including base)."""
        self._stats['operations'] += 1
        slant = math.sqrt(radius ** 2 + height ** 2)
        lateral = math.pi * radius * slant
        base = math.pi * radius ** 2
        return lateral + base

    # ==================== 3D TRANSFORMATIONS ====================

    def rotate_point_x(self, point: Point3D, angle: float) -> Point3D:
        """Rotate point around x-axis."""
        self._stats['operations'] += 1
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        return Point3D(
            point.x,
            point.y * cos_a - point.z * sin_a,
            point.y * sin_a + point.z * cos_a
        )

    def rotate_point_y(self, point: Point3D, angle: float) -> Point3D:
        """Rotate point around y-axis."""
        self._stats['operations'] += 1
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        return Point3D(
            point.x * cos_a + point.z * sin_a,
            point.y,
            -point.x * sin_a + point.z * cos_a
        )

    def rotate_point_z(self, point: Point3D, angle: float) -> Point3D:
        """Rotate point around z-axis."""
        self._stats['operations'] += 1
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        return Point3D(
            point.x * cos_a - point.y * sin_a,
            point.x * sin_a + point.y * cos_a,
            point.z
        )

    # ==================== BDI INTEGRATION ====================

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Perform process message operation.

        Args:
        message

        Returns:
        Result of the operation

        Example:
        >>> specialist = SolidGeometrySpecialist()
        >>> result = specialist.process_message(...)
        # Returns result
        """
        action = message.get('action', '')
        params = message.get('params', {})

        handlers = {
            'distance_point_point': lambda p: self.distance_point_point(**p),
            'distance_point_plane': lambda p: self.distance_point_plane(**p),
            'plane_from_points': lambda p: self.plane_from_points(**p),
            'ray_plane_intersection': lambda p: self.ray_plane_intersection(**p),
            'ray_sphere_intersection': lambda p: self.ray_sphere_intersection(**p),
            'volume_tetrahedron': lambda p: self.volume_tetrahedron(**p),
            'volume_sphere': lambda p: self.volume_sphere(**p),
        }

        if action in handlers:
            result = handlers[action](params)
            return {'status': 'success', 'result': result}
        return {'status': 'error', 'message': f'Unknown action: {action}'}

    def get_stats(self) -> Dict[str, int]:
        """Compute get stats using mathematical formula.

        Returns:
        Computed numerical or symbolic result

        Example:
        >>> specialist = SolidGeometrySpecialist()
        >>> result = specialist.get_stats()
        # Returns computed result

        """
        return dict(self._stats)

    def update_beliefs(self):
        """Perform update beliefs operation.

        Args:


        Returns:
        Result of the operation

        Example:
        >>> specialist = SolidGeometrySpecialist()
        >>> result = specialist.update_beliefs(...)
        # Returns result
        """
        pass

    def deliberate(self) -> List:
        """Perform deliberate operation.

        Args:


        Returns:
        Result of the operation

        Example:
        >>> specialist = SolidGeometrySpecialist()
        >>> result = specialist.deliberate(...)
        # Returns result
        """
        return []

    def execute_step(self, intention):
        """Perform execute step operation.

        Args:
        intention

        Returns:
        Result of the operation

        Example:
        >>> specialist = SolidGeometrySpecialist()
        >>> result = specialist.execute_step(...)
        # Returns result
        """
        pass


__all__ = [
    'SolidGeometrySpecialist',
    'Point3D',
    'Vector3D',
    'Plane',
    'Ray3D',
]
