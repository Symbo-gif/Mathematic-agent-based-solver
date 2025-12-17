# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
TRANSFORMATION SPECIALIST (Tier 3)
==================================

Handles geometric transformations: rotations, reflections, translations,
dilations, and composition of transformations.

CAPABILITIES:
- 2D/3D rotations
- Reflections across lines/planes
- Translations
- Dilations/scaling
- Transformation matrices
- Composition of transformations
"""

from typing import Any, Dict, List, Optional, Tuple
import math
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard


# ============================================================================
# NATIVE MATRIX CLASS (NO SYMPY)
# ============================================================================

class NativeMatrix:
    """Native matrix implementation without SymPy."""

    def __init__(self, data: List[List[float]]):
        self.data = [[float(x) for x in row] for row in data]
        self.rows = len(data)
        self.cols = len(data[0]) if data else 0

    def __mul__(self, other: 'NativeMatrix') -> 'NativeMatrix':
        """Matrix multiplication."""
        if self.cols != other.rows:
            raise ValueError(f"Cannot multiply {self.rows}x{self.cols} by {other.rows}x{other.cols}")

        result = [[0.0] * other.cols for _ in range(self.rows)]
        for i in range(self.rows):
            for j in range(other.cols):
                for k in range(self.cols):
                    result[i][j] += self.data[i][k] * other.data[k][j]
        return NativeMatrix(result)

    def tolist(self) -> List[List[float]]:
        """Convert to list of lists."""
        return self.data

    def __repr__(self):
        return f"Matrix({self.data})"


def native_simplify(matrix: NativeMatrix) -> NativeMatrix:
    """Simplify matrix by rounding very small values to zero."""
    result = []
    for row in matrix.data:
        new_row = []
        for val in row:
            if abs(val) < 1e-14:
                new_row.append(0.0)
            elif abs(val - round(val)) < 1e-14:
                new_row.append(float(round(val)))
            else:
                new_row.append(val)
        result.append(new_row)
    return NativeMatrix(result)


class TransformationSpecialist(BDIAgent):
    """Specialist for geometric transformations."""

    def __init__(
        self,
        agent_id: str = 'transformation_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.geometry.transformations',
                agent_id=agent_id,
                algorithm='native_matrix_transformations',
                cost='low',
                instance=self,  # Enable direct invocation by supervisors
                tier='3',
                capabilities='rotation_reflection_translation_dilation'
            ))

        print(f"[{agent_id}] Transformation Specialist initialized (NO SYMPY)")
        print(f"  Capabilities: Rotation, reflection, translation, dilation")

    def rotation_matrix_2d(self, angle: float) -> NativeMatrix:
        """Get 2D rotation matrix for given angle (radians) using native math."""
        c, s = math.cos(angle), math.sin(angle)
        return NativeMatrix([
            [c, -s],
            [s, c]
        ])

    def rotation_matrix_3d(self, axis: str, angle: float) -> NativeMatrix:
        """Get 3D rotation matrix around x, y, or z axis using native math."""
        c, s = math.cos(angle), math.sin(angle)
        if axis == 'x':
            return NativeMatrix([[1, 0, 0], [0, c, -s], [0, s, c]])
        elif axis == 'y':
            return NativeMatrix([[c, 0, s], [0, 1, 0], [-s, 0, c]])
        elif axis == 'z':
            return NativeMatrix([[c, -s, 0], [s, c, 0], [0, 0, 1]])
        raise ValueError(f"Invalid axis: {axis}")

    def rotate_point_2d(self, point: Tuple, angle: float, center: Tuple = (0, 0)) -> Tuple:
        """Rotate a 2D point around a center."""
        # Translate to origin
        px, py = point[0] - center[0], point[1] - center[1]
        # Rotate
        c, s = math.cos(angle), math.sin(angle)
        rx = px * c - py * s
        ry = px * s + py * c
        # Translate back
        return (rx + center[0], ry + center[1])

    def reflect_point_2d(self, point: Tuple, line_angle: float = 0) -> Tuple:
        """Reflect point across a line through origin at given angle."""
        px, py = point
        c, s = math.cos(2 * line_angle), math.sin(2 * line_angle)
        return (px * c + py * s, px * s - py * c)

    def translate_point(self, point: Tuple, vector: Tuple) -> Tuple:
        """Translate point by vector."""
        return tuple(p + v for p, v in zip(point, vector))

    def scale_point(self, point: Tuple, factor: float, center: Tuple = None) -> Tuple:
        """Scale point by factor around center."""
        if center is None:
            center = (0,) * len(point)
        return tuple(center[i] + factor * (point[i] - center[i]) for i in range(len(point)))

    def compose_matrices(self, *matrices: NativeMatrix) -> NativeMatrix:
        """Compose transformation matrices (right to left application) using native math."""
        result = matrices[0]
        for m in matrices[1:]:
            result = result * m
        return native_simplify(result)

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a transformation task."""
        self.tasks_executed += 1
        operation = task.get('operation', 'rotate')

        try:
            if operation in ('rotate', 'rotate_2d'):
                result = self.rotate_point_2d(
                    task['point'], task['angle'],
                    task.get('center', (0, 0))
                )
                return {'x': result[0], 'y': result[1], 'result': result}
            elif operation == 'rotation_matrix_2d':
                m = self.rotation_matrix_2d(task['angle'])
                return {'matrix': m.tolist()}
            elif operation == 'rotation_matrix_3d':
                m = self.rotation_matrix_3d(task['axis'], task['angle'])
                return {'matrix': m.tolist()}
            elif operation == 'reflect':
                result = self.reflect_point_2d(task['point'], task.get('line_angle', 0))
                return {'result': result}
            elif operation == 'translate':
                result = self.translate_point(task['point'], task['vector'])
                return {'result': result}
            elif operation == 'scale':
                result = self.scale_point(
                    task['point'], task['factor'],
                    task.get('center')
                )
                return {'result': result}
            else:
                return {'error': f'Unknown operation: {operation}'}
        except Exception as e:
            return {'error': str(e)}

    def update_beliefs(self):
        """Query blackboard for pending transformation tasks."""
        if not self.blackboard:
            return
        from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
        entries = self.blackboard.query_entries(
            entry_type=EntryType.TASK,
            status=EntryStatus.PENDING,
            tags=['math.geometry.transformations']
        )
        for entry in entries:
            self.beliefs[f'task_{entry.entry_id}'] = entry

    def deliberate(self) -> List[Intention]:
        """Create intentions for transformation tasks."""
        intentions = []
        for key, entry in list(self.beliefs.items()):
            if key.startswith('task_'):
                intention = Intention(
                    goal=f"solve_transform_{entry.entry_id}",
                    plan=['accept_task', 'solve', 'post_result'],
                    priority=1.0
                )
                intention.metadata = {'entry': entry, 'entry_id': entry.entry_id}
                intentions.append(intention)
        return intentions

    def execute_step(self, intention: Intention):
        """Execute transformation computation via process()."""
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
        stats = super().get_statistics()
        stats['tasks_executed'] = self.tasks_executed
        return stats
