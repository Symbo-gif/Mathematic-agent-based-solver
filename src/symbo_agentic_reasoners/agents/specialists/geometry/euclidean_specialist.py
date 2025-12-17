# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
EUCLIDEAN GEOMETRY SPECIALIST (Tier 3)
======================================

Handles classical Euclidean geometry: triangles, circles, polygons,
angles, congruence, similarity, and geometric proofs.

CAPABILITIES:
- Triangle computations (area, perimeter, angles, centers)
- Circle computations (area, circumference, tangents, chords)
- Polygon analysis (regular/irregular, convexity)
- Angle relationships (complementary, supplementary, vertical)
- Congruence and similarity checks
- Pythagorean theorem applications

LIBRARY: SymPy geometry module
"""

from typing import Any, Dict, List, Optional, Tuple
import math
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard


# ============================================================================
# NATIVE EUCLIDEAN GEOMETRY CLASSES (NO SYMPY)
# ============================================================================

class NativePoint:
    """Native 2D point without SymPy."""

    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], (tuple, list)):
            args = args[0]
        self.x = float(args[0])
        self.y = float(args[1]) if len(args) > 1 else 0.0

    def distance(self, other: 'NativePoint') -> float:
        """Calculate Euclidean distance to another point."""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def __repr__(self):
        return f"Point({self.x}, {self.y})"


class NativeLine:
    """Native 2D line without SymPy."""

    def __init__(self, p1: NativePoint, p2: NativePoint):
        if isinstance(p1, (tuple, list)):
            p1 = NativePoint(p1)
        if isinstance(p2, (tuple, list)):
            p2 = NativePoint(p2)
        self.p1 = p1
        self.p2 = p2
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        self._slope = dy / dx if dx != 0 else float('inf')

    def angle_between(self, other: 'NativeLine') -> float:
        """Calculate angle between two lines."""
        if self._slope == float('inf') or other._slope == float('inf'):
            if self._slope == float('inf') and other._slope == float('inf'):
                return 0
            return math.pi / 2
        denom = 1 + self._slope * other._slope
        if abs(denom) < 1e-14:
            return math.pi / 2
        return abs(math.atan((self._slope - other._slope) / denom))


class NativeCircle:
    """Native circle without SymPy."""

    def __init__(self, center: NativePoint, radius: float):
        if isinstance(center, (tuple, list)):
            center = NativePoint(center)
        self.center = center
        self.radius = float(radius)

    @property
    def area(self) -> float:
        return math.pi * self.radius ** 2

    @property
    def circumference(self) -> float:
        return 2 * math.pi * self.radius


class NativeTriangle:
    """Native triangle without SymPy."""

    def __init__(self, p1: NativePoint, p2: NativePoint, p3: NativePoint):
        if isinstance(p1, (tuple, list)):
            p1 = NativePoint(p1)
        if isinstance(p2, (tuple, list)):
            p2 = NativePoint(p2)
        if isinstance(p3, (tuple, list)):
            p3 = NativePoint(p3)
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

        # Side lengths
        self.a = p2.distance(p3)  # opposite to p1
        self.b = p1.distance(p3)  # opposite to p2
        self.c = p1.distance(p2)  # opposite to p3

    @property
    def area(self) -> float:
        """Calculate area using the shoelace formula."""
        return abs(
            (self.p1.x * (self.p2.y - self.p3.y) +
             self.p2.x * (self.p3.y - self.p1.y) +
             self.p3.x * (self.p1.y - self.p2.y)) / 2
        )

    @property
    def perimeter(self) -> float:
        """Calculate perimeter."""
        return self.a + self.b + self.c

    @property
    def centroid(self) -> NativePoint:
        """Calculate centroid (center of mass)."""
        return NativePoint(
            (self.p1.x + self.p2.x + self.p3.x) / 3,
            (self.p1.y + self.p2.y + self.p3.y) / 3
        )

    @property
    def circumcenter(self) -> NativePoint:
        """Calculate circumcenter (center of circumscribed circle)."""
        ax, ay = self.p1.x, self.p1.y
        bx, by = self.p2.x, self.p2.y
        cx, cy = self.p3.x, self.p3.y

        d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
        if abs(d) < 1e-14:
            return self.centroid  # Degenerate case

        ux = ((ax**2 + ay**2) * (by - cy) + (bx**2 + by**2) * (cy - ay) + (cx**2 + cy**2) * (ay - by)) / d
        uy = ((ax**2 + ay**2) * (cx - bx) + (bx**2 + by**2) * (ax - cx) + (cx**2 + cy**2) * (bx - ax)) / d
        return NativePoint(ux, uy)

    @property
    def incenter(self) -> NativePoint:
        """Calculate incenter (center of inscribed circle)."""
        p = self.perimeter
        if p == 0:
            return self.centroid
        return NativePoint(
            (self.a * self.p1.x + self.b * self.p2.x + self.c * self.p3.x) / p,
            (self.a * self.p1.y + self.b * self.p2.y + self.c * self.p3.y) / p
        )

    def is_right(self) -> bool:
        """Check if triangle is a right triangle."""
        sides = sorted([self.a, self.b, self.c])
        return abs(sides[0]**2 + sides[1]**2 - sides[2]**2) < 1e-10

    def is_equilateral(self) -> bool:
        """Check if triangle is equilateral."""
        return abs(self.a - self.b) < 1e-10 and abs(self.b - self.c) < 1e-10

    def is_isosceles(self) -> bool:
        """Check if triangle is isosceles."""
        return (abs(self.a - self.b) < 1e-10 or
                abs(self.b - self.c) < 1e-10 or
                abs(self.a - self.c) < 1e-10)


class EuclideanGeometrySpecialist(BDIAgent):
    """Specialist for Euclidean geometry computations."""

    def __init__(
        self,
        agent_id: str = 'euclidean_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.geometry.euclidean',
                agent_id=agent_id,
                algorithm='native_geometry',
                cost='low',
                instance=self,  # Enable direct invocation by supervisors
                tier='3',
                capabilities='triangles_circles_polygons_angles'
            ))

        print(f"[{agent_id}] Euclidean Geometry Specialist initialized (NO SYMPY)")
        print(f"  Library: Native Python geometry")
        print(f"  Capabilities: Triangles, circles, polygons, angles")

    def compute_triangle(self, p1: tuple, p2: tuple, p3: tuple) -> Dict[str, Any]:
        """Compute triangle properties from three points using native geometry."""
        try:
            t = NativeTriangle(p1, p2, p3)
            return {
                'area': t.area,
                'perimeter': t.perimeter,
                'centroid': (t.centroid.x, t.centroid.y),
                'circumcenter': (t.circumcenter.x, t.circumcenter.y),
                'incenter': (t.incenter.x, t.incenter.y),
                'is_right': t.is_right(),
                'is_equilateral': t.is_equilateral(),
                'is_isosceles': t.is_isosceles(),
            }
        except Exception as e:
            return {'error': str(e)}

    def compute_circle(self, center: tuple, radius: float) -> Dict[str, Any]:
        """Compute circle properties using native geometry."""
        try:
            c = NativeCircle(center, radius)
            return {
                'area': c.area,
                'circumference': c.circumference,
                'center': center,
                'radius': radius,
                'diameter': 2 * radius,
            }
        except Exception as e:
            return {'error': str(e)}

    def distance(self, p1: tuple, p2: tuple) -> float:
        """Compute distance between two points using native geometry."""
        return NativePoint(p1).distance(NativePoint(p2))

    def angle_between_lines(self, line1: tuple, line2: tuple) -> float:
        """Compute angle between two lines (each defined by two points) using native geometry."""
        l1 = NativeLine(line1[0], line1[1])
        l2 = NativeLine(line2[0], line2[1])
        return l1.angle_between(l2)

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a geometry task."""
        self.tasks_executed += 1
        operation = task.get('operation', 'triangle')

        if operation == 'triangle':
            return self.compute_triangle(
                task.get('p1', (0, 0)),
                task.get('p2', (1, 0)),
                task.get('p3', (0, 1))
            )
        elif operation == 'triangle_area':
            # Simple base*height/2 formula
            base = task.get('base')
            height = task.get('height')
            if base is not None and height is not None:
                return {'area': 0.5 * base * height, 'base': base, 'height': height}
            # Try 3 points
            if 'p1' in task:
                result = self.compute_triangle(task['p1'], task['p2'], task['p3'])
                return {'area': result.get('area')}
            return {'error': 'Need (base, height) or (p1, p2, p3)'}
        elif operation == 'circle':
            return self.compute_circle(
                task.get('center', (0, 0)),
                task.get('radius', 1)
            )
        elif operation == 'distance':
            return {'distance': self.distance(task.get('p1'), task.get('p2'))}
        else:
            return {'error': f'Unknown operation: {operation}'}

    # ==========================================================================
    # REAL BDI IMPLEMENTATION
    # ==========================================================================

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for geometry tasks."""
        if not self.blackboard:
            return

        try:
            from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus

            tasks = self.blackboard.query_entries(tags=['euclidean'], status=EntryStatus.PENDING)

            delegated = self.blackboard.query_entries(entry_type=EntryType.TASK, status=EntryStatus.PENDING)
            for task in delegated:
                if hasattr(task, 'metadata') and task.metadata:
                    if task.metadata.get('assigned_agent') == self.agent_id and task not in tasks:
                        tasks.append(task)

            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if self.has_belief(f'claimed_task_{task.entry_id}'):
                    continue
                if not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')

        except Exception as e:
            print(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create computation plans for geometry tasks."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue

            task = belief.content
            task_id = task.entry_id

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            raw_input = metadata.get('raw_input', '').lower()
            operation = metadata.get('operation', 'triangle')

            # Detect operation from input
            if 'circle' in raw_input:
                operation = 'circle'
            elif 'distance' in raw_input:
                operation = 'distance'
            elif 'angle' in raw_input:
                operation = 'angle'
            elif 'triangle' in raw_input or 'area' in raw_input:
                operation = 'triangle'

            steps = ['claim_task', 'parse_geometry', f'compute_{operation}', 'verify_result', 'post_result']

            intention = Intention(
                plan_id=f'geom_{operation}_{task_id}',
                steps=steps,
                target_desire='solve_geometry',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation, 'raw_input': raw_input}
            )
            new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Execute geometry computation (DELEGATE to SymPy geometry)."""
        from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
        from symbo_agentic_reasoners.core.omdoc_schema import create_variable
        import re

        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')

        try:
            if action == 'claim_task':
                if self.blackboard:
                    self.blackboard.update_entry_status(task_id, EntryStatus.IN_PROGRESS)
                self.add_belief(f'claimed_task_{task_id}', True)
                self.remove_belief(f'pending_task_{task_id}')
                intention.advance()

            elif action == 'parse_geometry':
                raw = intention.metadata.get('raw_input', '')
                numbers = [float(n) for n in re.findall(r'-?\d+\.?\d*', raw)]
                intention.metadata['numbers'] = numbers
                intention.advance()

            elif action == 'compute_triangle':
                numbers = intention.metadata.get('numbers', [])
                if len(numbers) >= 2:
                    # Assume base and height
                    result = {'area': 0.5 * numbers[0] * numbers[1]}
                elif len(numbers) >= 6:
                    # Three points
                    p1 = (numbers[0], numbers[1])
                    p2 = (numbers[2], numbers[3])
                    p3 = (numbers[4], numbers[5])
                    result = self.compute_triangle(p1, p2, p3)
                else:
                    result = {'error': 'Need base+height or 3 points'}
                intention.metadata['result'] = result
                self.add_belief('computed_result', result)
                intention.advance()

            elif action == 'compute_circle':
                numbers = intention.metadata.get('numbers', [])
                radius = numbers[0] if numbers else 1
                result = self.compute_circle((0, 0), radius)
                intention.metadata['result'] = result
                self.add_belief('computed_result', result)
                intention.advance()

            elif action == 'compute_distance':
                numbers = intention.metadata.get('numbers', [])
                if len(numbers) >= 4:
                    dist = self.distance((numbers[0], numbers[1]), (numbers[2], numbers[3]))
                    result = {'distance': dist}
                else:
                    result = {'error': 'Need 4 coordinates'}
                intention.metadata['result'] = result
                self.add_belief('computed_result', result)
                intention.advance()

            elif action == 'compute_angle':
                # Simplified angle computation
                result = {'angle': 'Angle computation requires line definitions'}
                intention.metadata['result'] = result
                intention.advance()

            elif action == 'verify_result':
                intention.metadata['verified'] = 'error' not in str(intention.metadata.get('result', {}))
                intention.advance()

            elif action == 'post_result':
                result = intention.metadata.get('result')
                if self.blackboard:
                    entry = create_entry(
                        entry_type=EntryType.PARTIAL_RESULT,
                        content=create_variable(str(result)),
                        author_agent=self.agent_id,
                        conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                        tags=['geometry', 'result', task_id],
                        status=EntryStatus.COMPLETED,
                        metadata={'result': str(result), 'result_str': str(result)}
                    )
                    self.blackboard.post(entry)
                    self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)
                self.tasks_executed += 1
                intention.advance()

            else:
                intention.advance()

        except Exception as e:
            print(f"[{self.agent_id}] Step {action} failed: {e}")
            while not intention.is_complete():
                intention.advance()

    def get_statistics(self) -> Dict[str, Any]:
        stats = super().get_statistics()
        stats['tasks_executed'] = self.tasks_executed
        return stats
