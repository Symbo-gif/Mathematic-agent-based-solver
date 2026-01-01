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
ANALYTIC GEOMETRY SPECIALIST (Tier 3)
=====================================

Handles coordinate geometry: lines, conic sections, distance formulas,
midpoints, slopes, and parametric equations.

CAPABILITIES:
- Line equations (slope-intercept, point-slope, general form)
- Conic sections (parabola, ellipse, hyperbola)
- Distance and midpoint formulas
- Intersection of lines and curves
- Parametric curve analysis
"""

from typing import Any, Dict, List, Optional, Tuple
import math
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard


# ============================================================================
# NATIVE GEOMETRY CLASSES (NO SYMPY)
# ============================================================================

class NativePoint:
    """Native 2D/3D point without SymPy."""

    def __init__(self, *coords):
        if len(coords) == 1 and isinstance(coords[0], (tuple, list)):
            coords = coords[0]
        self.coords = tuple(float(c) for c in coords)
        self.x = self.coords[0]
        self.y = self.coords[1] if len(self.coords) > 1 else 0
        self.z = self.coords[2] if len(self.coords) > 2 else 0

    def distance(self, other: 'NativePoint') -> float:
        """Calculate Euclidean distance to another point."""
        return math.sqrt(sum((a - b)**2 for a, b in zip(self.coords, other.coords)))

    def midpoint(self, other: 'NativePoint') -> 'NativePoint':
        """Calculate midpoint between this point and another."""
        return NativePoint(*[(a + b) / 2 for a, b in zip(self.coords, other.coords)])

    def __repr__(self):
        return f"Point({', '.join(str(c) for c in self.coords)})"


class NativeLine:
    """Native 2D line without SymPy."""

    def __init__(self, p1: NativePoint, p2: NativePoint):
        if isinstance(p1, (tuple, list)):
            p1 = NativePoint(p1)
        if isinstance(p2, (tuple, list)):
            p2 = NativePoint(p2)
        self.p1 = p1
        self.p2 = p2

        # Calculate line coefficients ax + by + c = 0
        dx = p2.x - p1.x
        dy = p2.y - p1.y

        # a = dy, b = -dx, c = dx*p1.y - dy*p1.x
        self.a = dy
        self.b = -dx
        self.c = dx * p1.y - dy * p1.x

        # Calculate slope (undefined for vertical lines)
        if dx != 0:
            self._slope = dy / dx
        else:
            self._slope = float('inf')

    @property
    def slope(self):
        """Perform slope operation.

        Args:


        Returns:
        Result of the operation

        Example:
        >>> specialist = NativeLine()
        >>> result = specialist.slope(...)
        # Returns result
        """
        return self._slope

    @property
    def coefficients(self):
        """Return (a, b, c) for ax + by + c = 0."""
        return (self.a, self.b, self.c)

    def intersection(self, other: 'NativeLine') -> List[NativePoint]:
        """Find intersection with another line."""
        # Solve system: a1*x + b1*y + c1 = 0 and a2*x + b2*y + c2 = 0
        det = self.a * other.b - self.b * other.a
        if abs(det) < 1e-14:
            return []  # Lines are parallel

        x = (self.b * other.c - other.b * self.c) / det
        y = (other.a * self.c - self.a * other.c) / det
        return [NativePoint(x, y)]

    def angle_between(self, other: 'NativeLine') -> float:
        """Calculate angle between two lines."""
        if self._slope == float('inf') or other._slope == float('inf'):
            if self._slope == float('inf') and other._slope == float('inf'):
                return 0
            elif self._slope == float('inf'):
                return math.atan(abs(1 / other._slope)) if other._slope != 0 else math.pi / 2
            else:
                return math.atan(abs(1 / self._slope)) if self._slope != 0 else math.pi / 2

        # tan(theta) = |m1 - m2| / (1 + m1*m2)
        denom = 1 + self._slope * other._slope
        if abs(denom) < 1e-14:
            return math.pi / 2  # Perpendicular lines
        return abs(math.atan((self._slope - other._slope) / denom))

    def __repr__(self):
        return f"Line({self.a}*x + {self.b}*y + {self.c} = 0)"


class NativeCircle:
    """Native circle without SymPy."""

    def __init__(self, center: NativePoint, radius: float):
        if isinstance(center, (tuple, list)):
            center = NativePoint(center)
        self.center = center
        self.radius = float(radius)

    @property
    def area(self) -> float:
        """Perform area operation.

        Args:


        Returns:
        Result of the operation

        Example:
        >>> specialist = NativeCircle()
        >>> result = specialist.area(...)
        # Returns result
        """
        return math.pi * self.radius ** 2

    @property
    def circumference(self) -> float:
        """Perform circumference operation.

        Args:


        Returns:
        Result of the operation

        Example:
        >>> specialist = NativeCircle()
        >>> result = specialist.circumference(...)
        # Returns result
        """
        return 2 * math.pi * self.radius

    def __repr__(self):
        return f"Circle(center={self.center}, r={self.radius})"


class NativeEllipse:
    """Native ellipse without SymPy."""

    def __init__(self, center: NativePoint, semi_major: float, semi_minor: float):
        if isinstance(center, (tuple, list)):
            center = NativePoint(center)
        self.center = center
        self.a = max(semi_major, semi_minor)  # semi-major axis
        self.b = min(semi_major, semi_minor)  # semi-minor axis

    @property
    def area(self) -> float:
        """Perform area operation.

        Args:


        Returns:
        Result of the operation

        Example:
        >>> specialist = NativeEllipse()
        >>> result = specialist.area(...)
        # Returns result
        """
        return math.pi * self.a * self.b

    @property
    def eccentricity(self) -> float:
        """Perform eccentricity operation.

        Args:


        Returns:
        Result of the operation

        Example:
        >>> specialist = NativeEllipse()
        >>> result = specialist.eccentricity(...)
        # Returns result
        """
        return math.sqrt(1 - (self.b / self.a) ** 2)

    @property
    def focal_distance(self) -> float:
        """Perform focal distance operation.

        Args:


        Returns:
        Result of the operation

        Example:
        >>> specialist = NativeEllipse()
        >>> result = specialist.focal_distance(...)
        # Returns result
        """
        return math.sqrt(self.a ** 2 - self.b ** 2)

    def __repr__(self):
        return f"Ellipse(center={self.center}, a={self.a}, b={self.b})"


class AnalyticGeometrySpecialist(BDIAgent):
    """Specialist for analytic/coordinate geometry."""

    def __init__(
        self,
        agent_id: str = 'analytic_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.geometry.analytic',
                agent_id=agent_id,
                algorithm='native_geometry',
                cost='low',
                instance=self,  # Enable direct invocation by supervisors
                tier='3',
                capabilities='lines_conics_intersections_parametric'
            ))

        print(f"[{agent_id}] Analytic Geometry Specialist initialized (NO SYMPY)")
        print(f"  Capabilities: Lines, conics, intersections, parametric curves")

    def line_from_points(self, p1: Tuple, p2: Tuple) -> Dict[str, Any]:
        """Get line equation from two points using native geometry."""
        try:
            line = NativeLine(NativePoint(p1), NativePoint(p2))
            a, b, c = line.coefficients
            slope = line.slope if line.slope != float('inf') else 'undefined'
            return {
                'slope': float(slope) if slope != 'undefined' else slope,
                'coefficients': (float(a), float(b), float(c)),
                'equation': f"{a}*x + {b}*y + {c} = 0"
            }
        except Exception as e:
            return {'error': str(e)}

    def line_intersection(self, line1_points: Tuple, line2_points: Tuple) -> Dict[str, Any]:
        """Find intersection of two lines using native geometry."""
        try:
            l1 = NativeLine(NativePoint(line1_points[0]), NativePoint(line1_points[1]))
            l2 = NativeLine(NativePoint(line2_points[0]), NativePoint(line2_points[1]))
            intersection = l1.intersection(l2)
            if intersection:
                pt = intersection[0]
                return {'intersection': (float(pt.x), float(pt.y))}
            return {'intersection': None, 'note': 'Lines are parallel'}
        except Exception as e:
            return {'error': str(e)}

    def midpoint(self, p1: Tuple, p2: Tuple) -> Tuple[float, float]:
        """Calculate midpoint between two points."""
        return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

    def distance(self, p1: Tuple, p2: Tuple) -> float:
        """Calculate distance between two points using native math."""
        return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

    def circle_equation(self, center: Tuple, radius: float) -> str:
        """Get circle equation in standard form."""
        h, k = center
        return f"(x - {h})^2 + (y - {k})^2 = {radius**2}"

    def ellipse_properties(self, center: Tuple, a: float, b: float) -> Dict[str, Any]:
        """Compute ellipse properties (a = semi-major, b = semi-minor) using native math."""
        try:
            ellipse = NativeEllipse(center, a, b)
            return {
                'center': center,
                'semi_major': ellipse.a,
                'semi_minor': ellipse.b,
                'eccentricity': ellipse.eccentricity,
                'foci_distance': ellipse.focal_distance,
                'area': ellipse.area
            }
        except Exception as e:
            return {'error': str(e)}

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process an analytic geometry task."""
        self.tasks_executed += 1
        operation = task.get('operation', 'line')

        if operation in ('line', 'line_from_points'):
            result = self.line_from_points(task['p1'], task['p2'])
            # Add y_intercept for convenience
            if 'slope' in result and result['slope'] != 'undefined':
                slope = result['slope']
                # y - y1 = m(x - x1), at x=0: y_intercept = y1 - m*x1
                p1 = task['p1']
                y_intercept = p1[1] - slope * p1[0]
                result['y_intercept'] = float(y_intercept)
            return result
        elif operation == 'line_intersection':
            return self.line_intersection(task['line1'], task['line2'])
        elif operation == 'midpoint':
            return {'midpoint': self.midpoint(task['p1'], task['p2'])}
        elif operation == 'distance':
            return {'distance': self.distance(task['p1'], task['p2'])}
        elif operation == 'ellipse':
            return self.ellipse_properties(task['center'], task['a'], task['b'])
        else:
            return {'error': f'Unknown operation: {operation}'}

    def update_beliefs(self):
        """Query blackboard for pending analytic geometry tasks."""
        if not self.blackboard:
            return
        from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
        entries = self.blackboard.query_entries(
            entry_type=EntryType.TASK,
            status=EntryStatus.PENDING,
            tags=['math.geometry.analytic']
        )
        for entry in entries:
            self.beliefs[f'task_{entry.entry_id}'] = entry

    def deliberate(self) -> List[Intention]:
        """Create intentions for analytic geometry tasks."""
        intentions = []
        for key, entry in list(self.beliefs.items()):
            if key.startswith('task_'):
                intention = Intention(
                    goal=f"solve_analytic_{entry.entry_id}",
                    plan=['accept_task', 'solve', 'post_result'],
                    priority=1.0
                )
                intention.metadata = {'entry': entry, 'entry_id': entry.entry_id}
                intentions.append(intention)
        return intentions

    def execute_step(self, intention: Intention):
        """Execute analytic geometry computation via process()."""
        if not intention or not hasattr(intention, 'metadata'):
            return
        entry = intention.metadata.get('entry')
        if not entry:
            return
        action = intention.get_current_action()
        if action == 'accept_task':
            if self.blackboard:
                from symbo_agentic_reasoners.core.blackboard import EntryStatus
                self.blackboard.update_entry_status(entry.entry_id, EntryStatus.IN_PROGRESS)
            intention.advance()
        elif action == 'solve':
            task = entry.metadata if hasattr(entry, 'metadata') and entry.metadata else {}
            result = self.process(task)
            intention.metadata['result'] = result
            intention.advance()
        elif action == 'post_result':
            result = intention.metadata.get('result', {})
            if self.blackboard:
                from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
                from symbo_agentic_reasoners.core.omdoc_schema import create_variable
                result_entry = create_entry(
                    entry_type=EntryType.RESULT,
                    content=create_variable(str(result)),
                    author_agent=self.agent_id,
                    status=EntryStatus.COMPLETED,
                    metadata={'result': result, 'result_str': str(result)}
                )
                self.blackboard.post(result_entry)
                self.blackboard.update_entry_status(entry.entry_id, EntryStatus.COMPLETED)
            del self.beliefs[f'task_{entry.entry_id}']
            intention.advance()

    def get_statistics(self) -> Dict[str, Any]:
        """Compute get statistics using mathematical formula.

        Returns:
        Computed numerical or symbolic result

        Example:
        >>> specialist = AnalyticGeometrySpecialist()
        >>> result = specialist.get_statistics()
        # Returns computed result

        """
        stats = super().get_statistics()
        stats['tasks_executed'] = self.tasks_executed
        return stats
