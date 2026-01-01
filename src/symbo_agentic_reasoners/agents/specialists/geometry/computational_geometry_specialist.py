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
COMPUTATIONAL GEOMETRY SPECIALIST (Tier 3)
==========================================

Algorithmic computational geometry operations.

CAPABILITIES:
------------
- Convex hull (Graham scan, Jarvis march)
- Line segment intersection
- Point-in-polygon tests
- Polygon area and centroid
- Closest pair of points
- Triangulation (ear clipping)

NO SYMPY - All mathematical operations use native implementations.
"""

import logging
import math
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard

logger = logging.getLogger('symbo_agentic_reasoners.specialists.computational_geometry')


@dataclass
class Point:
    """2D Point."""
    x: float
    y: float

    def __sub__(self, other: 'Point') -> 'Point':
        return Point(self.x - other.x, self.y - other.y)

    def __add__(self, other: 'Point') -> 'Point':
        return Point(self.x + other.x, self.y + other.y)

    def dot(self, other: 'Point') -> float:
        """Perform dot operation.

        Args:
        other

        Returns:
        Result of the operation

        Example:
        >>> specialist = Point()
        >>> result = specialist.dot(...)
        # Returns result
        """
        return self.x * other.x + self.y * other.y

    def cross(self, other: 'Point') -> float:
        """Perform cross operation.

        Args:
        other

        Returns:
        Result of the operation

        Example:
        >>> specialist = Point()
        >>> result = specialist.cross(...)
        # Returns result
        """
        return self.x * other.y - self.y * other.x

    def magnitude(self) -> float:
        """Perform magnitude operation.

        Args:


        Returns:
        Result of the operation

        Example:
        >>> specialist = Point()
        >>> result = specialist.magnitude(...)
        # Returns result
        """
        return math.sqrt(self.x ** 2 + self.y ** 2)


@dataclass
class LineSegment:
    """Line segment from p1 to p2."""
    p1: Point
    p2: Point


class ComputationalGeometrySpecialist(BDIAgent):
    """
    Computational Geometry Specialist

    DIRECTIVE:
    ---------
    Provide algorithmic geometry operations for computational geometry tasks.

    OPERATIONS:
    ----------
    - convex_hull: Compute convex hull of points
    - point_in_polygon: Test if point is inside polygon
    - line_intersection: Find line segment intersection
    - polygon_area: Compute polygon area
    - closest_pair: Find closest pair of points
    - triangulate: Triangulate simple polygon
    """

    def __init__(
        self,
        agent_id: str = "computational_geometry_specialist",
        directory_facilitator: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
    ):
        super().__init__(agent_id=agent_id)
        self.agent_type = "computational_geometry_specialist"
        self.df = directory_facilitator
        self.blackboard = blackboard
        self._register_services()
        self._stats = {'operations': 0}

    def _register_services(self):
        """Register specialist services."""
        if self.df:
            self.df.register_service(create_service_registration(
                agent_id=self.agent_id,
                service_type="computational_geometry",
                description="Computational geometry algorithms"
            ))

    # ==================== CONVEX HULL ====================

    def convex_hull_graham(self, points: List[Point]) -> List[Point]:
        """Graham scan algorithm for convex hull. O(n log n)."""
        self._stats['operations'] += 1

        if len(points) < 3:
            return points.copy()

        # Find lowest point (and leftmost if tie)
        pivot = min(points, key=lambda p: (p.y, p.x))

        def polar_angle(p: Point) -> float:
            """Perform polar angle operation.

            Args:
            p: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.polar_angle(...)
            """
            return math.atan2(p.y - pivot.y, p.x - pivot.x)

        def distance(p: Point) -> float:
            """Perform distance operation.

            Args:
            p: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.distance(...)
            """
            return (p.x - pivot.x) ** 2 + (p.y - pivot.y) ** 2

        # Sort by polar angle
        sorted_points = sorted(
            [p for p in points if p != pivot],
            key=lambda p: (polar_angle(p), -distance(p))
        )

        # Build hull using stack
        hull = [pivot]

        for p in sorted_points:
            while len(hull) > 1 and self._ccw(hull[-2], hull[-1], p) <= 0:
                hull.pop()
            hull.append(p)

        return hull

    def convex_hull_jarvis(self, points: List[Point]) -> List[Point]:
        """Jarvis march (gift wrapping) algorithm. O(nh)."""
        self._stats['operations'] += 1

        if len(points) < 3:
            return points.copy()

        # Find leftmost point
        start = min(points, key=lambda p: (p.x, p.y))
        hull = []
        current = start

        while True:
            hull.append(current)
            next_point = points[0]

            for p in points:
                if p == current:
                    continue

                cross = self._ccw(current, next_point, p)
                if next_point == current or cross > 0:
                    next_point = p
                elif cross == 0:
                    # Collinear - take farther point
                    if self._dist_sq(current, p) > self._dist_sq(current, next_point):
                        next_point = p

            current = next_point
            if current == start:
                break

        return hull

    def _ccw(self, a: Point, b: Point, c: Point) -> float:
        """Counter-clockwise test. >0: ccw, <0: cw, =0: collinear."""
        return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)

    def _dist_sq(self, a: Point, b: Point) -> float:
        """Squared distance between points."""
        return (a.x - b.x) ** 2 + (a.y - b.y) ** 2

    # ==================== POINT IN POLYGON ====================

    def point_in_polygon(self, point: Point, polygon: List[Point]) -> bool:
        """Ray casting algorithm for point-in-polygon test."""
        self._stats['operations'] += 1

        n = len(polygon)
        inside = False

        j = n - 1
        for i in range(n):
            if ((polygon[i].y > point.y) != (polygon[j].y > point.y) and
                point.x < (polygon[j].x - polygon[i].x) *
                           (point.y - polygon[i].y) /
                           (polygon[j].y - polygon[i].y) + polygon[i].x):
                inside = not inside
            j = i

        return inside

    def point_on_polygon_edge(self, point: Point, polygon: List[Point], eps: float = 1e-10) -> bool:
        """Test if point lies on polygon edge."""
        n = len(polygon)
        for i in range(n):
            j = (i + 1) % n
            if self._point_on_segment(point, polygon[i], polygon[j], eps):
                return True
        return False

    def _point_on_segment(self, p: Point, a: Point, b: Point, eps: float) -> bool:
        """Test if point lies on line segment."""
        cross = abs(self._ccw(a, b, p))
        if cross > eps:
            return False
        return (min(a.x, b.x) - eps <= p.x <= max(a.x, b.x) + eps and
                min(a.y, b.y) - eps <= p.y <= max(a.y, b.y) + eps)

    # ==================== LINE INTERSECTION ====================

    def line_segment_intersection(
        self,
        seg1: LineSegment,
        seg2: LineSegment
    ) -> Optional[Point]:
        """Find intersection point of two line segments."""
        self._stats['operations'] += 1

        p1, p2 = seg1.p1, seg1.p2
        p3, p4 = seg2.p1, seg2.p2

        d1 = p2 - p1
        d2 = p4 - p3
        d3 = p1 - p3

        cross = d1.cross(d2)

        if abs(cross) < 1e-10:
            return None  # Parallel

        t = d3.cross(d2) / (-cross)
        u = d1.cross(d3) / cross

        if 0 <= t <= 1 and 0 <= u <= 1:
            return Point(p1.x + t * d1.x, p1.y + t * d1.y)

        return None

    def segments_intersect(self, seg1: LineSegment, seg2: LineSegment) -> bool:
        """Test if two line segments intersect."""
        d1 = self._ccw(seg1.p1, seg1.p2, seg2.p1)
        d2 = self._ccw(seg1.p1, seg1.p2, seg2.p2)
        d3 = self._ccw(seg2.p1, seg2.p2, seg1.p1)
        d4 = self._ccw(seg2.p1, seg2.p2, seg1.p2)

        if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
           ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
            return True

        # Check collinear cases
        if d1 == 0 and self._on_segment(seg1, seg2.p1):
            return True
        if d2 == 0 and self._on_segment(seg1, seg2.p2):
            return True
        if d3 == 0 and self._on_segment(seg2, seg1.p1):
            return True
        if d4 == 0 and self._on_segment(seg2, seg1.p2):
            return True

        return False

    def _on_segment(self, seg: LineSegment, p: Point) -> bool:
        """Check if point lies on segment (assuming collinear)."""
        return (min(seg.p1.x, seg.p2.x) <= p.x <= max(seg.p1.x, seg.p2.x) and
                min(seg.p1.y, seg.p2.y) <= p.y <= max(seg.p1.y, seg.p2.y))

    # ==================== POLYGON OPERATIONS ====================

    def polygon_area(self, polygon: List[Point]) -> float:
        """Compute polygon area using shoelace formula."""
        self._stats['operations'] += 1

        n = len(polygon)
        area = 0.0

        for i in range(n):
            j = (i + 1) % n
            area += polygon[i].x * polygon[j].y
            area -= polygon[j].x * polygon[i].y

        return abs(area) / 2

    def polygon_centroid(self, polygon: List[Point]) -> Point:
        """Compute polygon centroid."""
        self._stats['operations'] += 1

        n = len(polygon)
        area = self.polygon_area(polygon)

        if area == 0:
            # Degenerate polygon - return average of points
            return Point(
                sum(p.x for p in polygon) / n,
                sum(p.y for p in polygon) / n
            )

        cx, cy = 0.0, 0.0

        for i in range(n):
            j = (i + 1) % n
            cross = polygon[i].x * polygon[j].y - polygon[j].x * polygon[i].y
            cx += (polygon[i].x + polygon[j].x) * cross
            cy += (polygon[i].y + polygon[j].y) * cross

        factor = 1 / (6 * area)
        return Point(cx * factor, cy * factor)

    def polygon_is_convex(self, polygon: List[Point]) -> bool:
        """Test if polygon is convex."""
        n = len(polygon)
        if n < 3:
            return False

        sign = None
        for i in range(n):
            cross = self._ccw(polygon[i], polygon[(i + 1) % n], polygon[(i + 2) % n])
            if cross != 0:
                if sign is None:
                    sign = cross > 0
                elif (cross > 0) != sign:
                    return False

        return True

    # ==================== CLOSEST PAIR ====================

    def closest_pair(self, points: List[Point]) -> Tuple[Point, Point, float]:
        """Find closest pair of points. O(n log n)."""
        self._stats['operations'] += 1

        n = len(points)
        if n < 2:
            raise ValueError("Need at least 2 points")

        if n == 2:
            dist = math.sqrt(self._dist_sq(points[0], points[1]))
            return points[0], points[1], dist

        # Sort by x coordinate
        sorted_x = sorted(points, key=lambda p: p.x)

        return self._closest_pair_recursive(sorted_x)

    def _closest_pair_recursive(
        self,
        points: List[Point]
    ) -> Tuple[Point, Point, float]:
        """Divide and conquer closest pair."""
        n = len(points)

        if n <= 3:
            return self._closest_pair_brute(points)

        mid = n // 2
        mid_point = points[mid]

        left = points[:mid]
        right = points[mid:]

        p1_l, p2_l, d_l = self._closest_pair_recursive(left)
        p1_r, p2_r, d_r = self._closest_pair_recursive(right)

        if d_l < d_r:
            p1, p2, d = p1_l, p2_l, d_l
        else:
            p1, p2, d = p1_r, p2_r, d_r

        # Check strip
        strip = [p for p in points if abs(p.x - mid_point.x) < d]
        strip.sort(key=lambda p: p.y)

        for i in range(len(strip)):
            for j in range(i + 1, min(i + 7, len(strip))):
                dist = math.sqrt(self._dist_sq(strip[i], strip[j]))
                if dist < d:
                    d = dist
                    p1, p2 = strip[i], strip[j]

        return p1, p2, d

    def _closest_pair_brute(
        self,
        points: List[Point]
    ) -> Tuple[Point, Point, float]:
        """Brute force closest pair for small inputs."""
        min_dist = float('inf')
        p1, p2 = points[0], points[1]

        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                dist = math.sqrt(self._dist_sq(points[i], points[j]))
                if dist < min_dist:
                    min_dist = dist
                    p1, p2 = points[i], points[j]

        return p1, p2, min_dist

    # ==================== TRIANGULATION ====================

    def triangulate_ear_clipping(
        self,
        polygon: List[Point]
    ) -> List[Tuple[int, int, int]]:
        """
        Triangulate simple polygon using ear clipping.

        Returns list of triangle indices (i, j, k).
        """
        self._stats['operations'] += 1

        n = len(polygon)
        if n < 3:
            return []

        # Create index list
        indices = list(range(n))
        triangles = []

        while len(indices) > 3:
            ear_found = False

            for i in range(len(indices)):
                prev_idx = (i - 1) % len(indices)
                next_idx = (i + 1) % len(indices)

                prev_vertex = indices[prev_idx]
                curr_vertex = indices[i]
                next_vertex = indices[next_idx]

                if self._is_ear(polygon, indices, prev_idx, i, next_idx):
                    triangles.append((prev_vertex, curr_vertex, next_vertex))
                    indices.pop(i)
                    ear_found = True
                    break

            if not ear_found:
                # Fallback - shouldn't happen for simple polygons
                break

        if len(indices) == 3:
            triangles.append((indices[0], indices[1], indices[2]))

        return triangles

    def _is_ear(
        self,
        polygon: List[Point],
        indices: List[int],
        prev_idx: int,
        curr_idx: int,
        next_idx: int
    ) -> bool:
        """Test if vertex at curr_idx forms an ear."""
        prev_v = polygon[indices[prev_idx]]
        curr_v = polygon[indices[curr_idx]]
        next_v = polygon[indices[next_idx]]

        # Must be convex
        if self._ccw(prev_v, curr_v, next_v) <= 0:
            return False

        # No other vertex inside triangle
        for i, idx in enumerate(indices):
            if i in [prev_idx, curr_idx, next_idx]:
                continue

            if self._point_in_triangle(polygon[idx], prev_v, curr_v, next_v):
                return False

        return True

    def _point_in_triangle(self, p: Point, a: Point, b: Point, c: Point) -> bool:
        """Test if point is inside triangle."""
        d1 = self._ccw(a, b, p)
        d2 = self._ccw(b, c, p)
        d3 = self._ccw(c, a, p)

        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

        return not (has_neg and has_pos)

    # ==================== BDI INTEGRATION ====================

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming BDI message."""
        action = message.get('action', '')
        params = message.get('params', {})

        handlers = {
            'convex_hull': lambda p: self.convex_hull_graham(**p),
            'point_in_polygon': lambda p: self.point_in_polygon(**p),
            'polygon_area': lambda p: self.polygon_area(**p),
            'closest_pair': lambda p: self.closest_pair(**p),
            'triangulate': lambda p: self.triangulate_ear_clipping(**p),
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
        >>> specialist = ComputationalGeometrySpecialist()
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
        >>> specialist = ComputationalGeometrySpecialist()
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
        >>> specialist = ComputationalGeometrySpecialist()
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
        >>> specialist = ComputationalGeometrySpecialist()
        >>> result = specialist.execute_step(...)
        # Returns result
        """
        pass


__all__ = [
    'ComputationalGeometrySpecialist',
    'Point',
    'LineSegment',
]
