# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
GEOMETRY SUPERVISOR (Tier 2)
============================

Strategic router for geometry tasks including Euclidean geometry,
analytic geometry, transformations, and trigonometry.

ROUTING LOGIC:
- Triangles, circles, polygons, angles -> Euclidean Specialist
- Lines, conics, coordinates, intersections -> Analytic Specialist
- Rotations, reflections, translations -> Transformation Specialist
- Trig functions, identities, law of sines/cosines -> Trigonometry Specialist
"""

from typing import Any, Dict, List, Optional
import uuid

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)


class GeometrySupervisor(BDIAgent):
    """Geometry Supervisor - Routes to appropriate geometry specialists."""

    def __init__(
        self,
        agent_id: str = 'geometry_supervisor_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_routed = 0
        self.euclidean_routes = 0
        self.analytic_routes = 0
        self.transformation_routes = 0
        self.trigonometry_routes = 0

        if self.df:
            self._register_services()

        self._log_info("Geometry Supervisor initialized")
        self._log_debug("Role: Strategic router for geometry tasks | Mode: Analysis and delegation only")

    def _register_services(self):
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            service_type='math.geometry',
            agent_id=self.agent_id,
            algorithm='routing',
            cost='low',
            instance=self,
            type='supervisor',
            domain='geometry',
            tier='2'
        )
        self.df.register(registration)
        self._log_debug("Registered with DF: math.geometry (supervisor)")

    def process(self, task_entry: Any) -> Any:
        """Process geometry task by routing to appropriate specialist."""
        self._log_info("Processing geometry task")

        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        raw_input = metadata.get('raw_input', '').lower()

        self._log_debug(f"Task: {raw_input}")

        routing_decision = self._analyze_task(task_entry)

        self._log_info(f"Routing decision: {routing_decision['target']}", reason=routing_decision['reason'])

        # Update counters
        if 'euclidean' in routing_decision['service_type']:
            self.euclidean_routes += 1
        elif 'analytic' in routing_decision['service_type']:
            self.analytic_routes += 1
        elif 'transformation' in routing_decision['service_type']:
            self.transformation_routes += 1
        else:
            self.trigonometry_routes += 1

        specialists = self._find_specialists(routing_decision['service_type'])

        if not specialists:
            error_msg = f"No specialist available for: {routing_decision['service_type']}"
            self._log_error(error_msg)
            return self._create_error_result(task_entry, error_msg)

        self._log_debug(f"Found specialist: {specialists[0].agent_id}")

        result = self._delegate_to_specialist(task_entry, specialists[0], routing_decision)
        self.tasks_routed += 1

        return result

    def _analyze_task(self, task_entry: Any) -> Dict[str, Any]:
        """Analyze task to determine routing strategy."""
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        raw_input = metadata.get('raw_input', '').lower()

        # Trigonometry keywords (check first - most specific)
        trig_keywords = [
            'sin', 'cos', 'tan', 'cot', 'sec', 'csc',
            'arcsin', 'arccos', 'arctan', 'asin', 'acos', 'atan',
            'law of sines', 'law of cosines', 'polar',
            'radian', 'degree', 'trigonometric', 'trig identity',
            'unit circle', 'periodic'
        ]
        if any(kw in raw_input for kw in trig_keywords):
            return {
                'target': 'Trigonometry Specialist',
                'service_type': 'math.geometry.trigonometry',
                'reason': 'Detected trigonometry keywords'
            }

        # Transformation keywords
        transform_keywords = [
            'rotate', 'rotation', 'reflect', 'reflection',
            'translate', 'translation', 'dilate', 'dilation',
            'scale', 'transform', 'matrix', 'affine',
            'shear', 'composition'
        ]
        if any(kw in raw_input for kw in transform_keywords):
            return {
                'target': 'Transformation Specialist',
                'service_type': 'math.geometry.transformations',
                'reason': 'Detected transformation keywords'
            }

        # Analytic geometry keywords
        analytic_keywords = [
            'coordinate', 'slope', 'intercept', 'equation of line',
            'conic', 'parabola', 'ellipse', 'hyperbola',
            'midpoint', 'parametric', 'intersection',
            'perpendicular', 'parallel lines', 'distance formula'
        ]
        if any(kw in raw_input for kw in analytic_keywords):
            return {
                'target': 'Analytic Geometry Specialist',
                'service_type': 'math.geometry.analytic',
                'reason': 'Detected analytic geometry keywords'
            }

        # Default to Euclidean geometry
        return {
            'target': 'Euclidean Geometry Specialist',
            'service_type': 'math.geometry.euclidean',
            'reason': 'Default routing for geometric shapes and measurements'
        }

    def _find_specialists(self, service_type: str) -> List[Any]:
        """Query Directory Facilitator for specialists."""
        if not self.df:
            return []
        return self.df.search(service_type=service_type)

    def _delegate_to_specialist(
        self,
        task_entry: Any,
        specialist: Any,
        routing_decision: Dict[str, Any]
    ) -> Any:
        """Delegate task to specialist via Blackboard."""
        if not self.blackboard:
            return self._create_error_result(task_entry, "No Blackboard available")

        delegation_id = f'delegation_{uuid.uuid4().hex[:8]}'

        delegated_metadata = dict(task_entry.metadata) if hasattr(task_entry, 'metadata') else {}
        delegated_metadata.update({
            'delegated_by': self.agent_id,
            'delegation_id': delegation_id,
            'assigned_agent': specialist.agent_id,
            'routing_reason': routing_decision['reason']
        })

        delegated_entry = create_entry(
            entry_type=EntryType.TASK,
            content=task_entry.content,
            author_agent=self.agent_id,
            conversation_id=delegation_id,
            tags=[routing_decision['service_type'].split('.')[-1], 'delegated', delegation_id],
            metadata=delegated_metadata
        )

        self.blackboard.post(delegated_entry)
        self._log_info(f"Delegated to {specialist.agent_id}")

        return delegated_entry

    def _create_error_result(self, task_entry: Any, error_msg: str) -> Any:
        """Create error result entry."""
        if not self.blackboard:
            return None

        error_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=task_entry.content if hasattr(task_entry, 'content') else None,
            author_agent=self.agent_id,
            conversation_id=task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'error',
            tags=['error'],
            status=EntryStatus.FAILED,
            metadata={'error': error_msg}
        )

        self.blackboard.post(error_entry)
        return error_entry

    # ==========================================================================
    # REAL BDI IMPLEMENTATION
    # ==========================================================================

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for geometry tasks that need routing."""
        if not self.blackboard:
            return

        try:
            pending_tasks = self.blackboard.query_entries(
                tags=['geometry'],
                status=EntryStatus.PENDING
            )

            task_entries = self.blackboard.query_entries(
                entry_type=EntryType.TASK,
                status=EntryStatus.PENDING
            )

            for task in task_entries:
                domain = ''
                if hasattr(task, 'metadata') and task.metadata:
                    domain = task.metadata.get('domain', '').lower()

                if domain in ['geometry', ''] and task not in pending_tasks:
                    pending_tasks.append(task)

            for task in pending_tasks:
                belief_key = f'pending_geometry_{task.entry_id}'

                if self.has_belief(f'routed_{task.entry_id}') or self.has_belief(f'delegated_{task.entry_id}'):
                    continue

                if not self.has_belief(belief_key):
                    self.add_belief(predicate=belief_key, content=task, confidence=1.0, source='blackboard')

            for predicate in list(self.beliefs.keys()):
                if predicate.startswith('delegated_'):
                    delegation_info = self.get_belief(predicate).content
                    delegation_id = delegation_info.get('delegation_id')

                    results = self.blackboard.query_entries(tags=[delegation_id, 'result'], status=EntryStatus.COMPLETED)
                    if results:
                        self.add_belief(f'result_{delegation_id}', results[0], source='specialist')
                        self.remove_belief(predicate)

                    failures = self.blackboard.query_entries(tags=[delegation_id], status=EntryStatus.FAILED)
                    if failures:
                        self.add_belief(f'failed_{delegation_id}', failures[0], source='specialist')
                        self.remove_belief(predicate)

        except Exception as e:
            self._log_error(f"update_beliefs error: {e}", exc=e)

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create routing plans for pending geometry tasks."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_geometry_'):
                continue

            task = belief.content
            task_id = task.entry_id

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            routing_decision = self._analyze_task(task)

            intention = Intention(
                plan_id=f'route_{task_id}',
                steps=['analyze_task', 'find_specialist', 'delegate_task', 'track_result'],
                target_desire='route_geometry_task',
                metadata={'task_id': task_id, 'task_entry': task, 'routing_decision': routing_decision}
            )

            new_intentions.append(intention)
            self._log_debug(f"Created routing plan for {task_id} -> {routing_decision['target']}")

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Execute one step of the routing plan."""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')
        routing = intention.metadata.get('routing_decision', {})

        try:
            if action == 'analyze_task':
                intention.advance()
            elif action == 'find_specialist':
                service_type = routing.get('service_type', 'math.geometry.euclidean')
                specialists = self._find_specialists(service_type)
                if specialists:
                    intention.metadata['specialist'] = specialists[0]
                    intention.advance()
                else:
                    raise ValueError(f"No specialist available for {service_type}")
            elif action == 'delegate_task':
                specialist = intention.metadata.get('specialist')
                if not specialist or not self.blackboard:
                    raise ValueError("No specialist or blackboard")

                delegation_id = f'delegation_{uuid.uuid4().hex[:8]}'
                delegated_metadata = dict(task.metadata) if hasattr(task, 'metadata') else {}
                delegated_metadata.update({
                    'delegated_by': self.agent_id,
                    'delegation_id': delegation_id,
                    'assigned_agent': specialist.agent_id,
                    'routing_reason': routing.get('reason', ''),
                    'original_task_id': task_id
                })

                specialist_tag = routing.get('service_type', 'euclidean').split('.')[-1]
                delegated_entry = create_entry(
                    entry_type=EntryType.TASK, content=task.content, author_agent=self.agent_id,
                    conversation_id=delegation_id, tags=[specialist_tag, 'delegated', delegation_id, 'task'],
                    status=EntryStatus.PENDING, metadata=delegated_metadata
                )

                self.blackboard.post(delegated_entry)
                self.add_belief(f'routed_{task_id}', True)
                self.add_belief(f'delegated_{task_id}', {
                    'delegation_id': delegation_id, 'specialist': specialist.agent_id,
                    'delegated_entry_id': delegated_entry.entry_id
                })
                self.blackboard.update_entry_status(task_id, EntryStatus.IN_PROGRESS)
                self.remove_belief(f'pending_geometry_{task_id}')
                self.tasks_routed += 1
                intention.advance()
            elif action == 'track_result':
                intention.advance()
            else:
                intention.advance()

        except Exception as e:
            self._log_error(f"Step {action} failed: {e}", exc=e)
            if self.blackboard and task_id:
                error_entry = create_entry(
                    entry_type=EntryType.PARTIAL_RESULT, content=task.content if hasattr(task, 'content') else None,
                    author_agent=self.agent_id, conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                    tags=['error', 'routing_failed', task_id], status=EntryStatus.FAILED,
                    metadata={'error': str(e), 'task_id': task_id}
                )
                self.blackboard.post(error_entry)
            if task_id:
                self.remove_belief(f'pending_geometry_{task_id}')
            while not intention.is_complete():
                intention.advance()

    def get_statistics(self) -> Dict[str, Any]:
        stats = super().get_statistics()
        stats.update({
            'tasks_routed': self.tasks_routed,
            'euclidean_routes': self.euclidean_routes,
            'analytic_routes': self.analytic_routes,
            'transformation_routes': self.transformation_routes,
            'trigonometry_routes': self.trigonometry_routes
        })
        return stats
