# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
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
PHASE 2 - STEP 2.1: CALCULUS SUPERVISOR (Tier 2)
================================================

The Calculus Supervisor acts as the primary gatekeeper for calculus tasks,
possessing the crucial decision logic to route problems to the correct engine.

CRITICAL FUNCTION:
-----------------
Must distinguish between requests for exact solutions (symbolic) and
approximate solutions (numerical) to prevent wasted computation on
non-integrable functions.

ROUTING LOGIC:
-------------
- "Find the exact integral" → Integration Specialist (Symbolic Engine)
- "Approximate the area" → Integration Specialist (Numerical Engine)
- "Derivative" / "gradient" → Differentiation Specialist
- "Differential equation" / "ODE" / "PDE" → Differential Equation Solver
- "Series" / "Taylor" / "Fourier" → Series Specialist

WHY THIS MATTERS:
----------------
This is the most complex domain in Phase 2. Many functions are NOT
analytically integrable (no closed-form antiderivative exists). Sending
these to symbolic engines wastes resources. The supervisor's intelligence
prevents this failure mode.

REFERENCE:
---------
- Phase_2_Build_Order_Breakdown.md: Lines 96-99 (Agent 2.1)
- Phase 2 Coding Strategy: Section 3.2 "The Analysis Layer"
"""

import sys
import os
from typing import List, Dict, Any, Optional
import uuid

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from symbo_agentic_reasoners_phase0.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners_phase0.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners_phase0.memory.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)


class CalculusSupervisor(BDIAgent):
    """
    Calculus Supervisor - Tier 2 Strategic Router with Critical Decision Logic

    ROLE:
    ----
    Acts as gatekeeper for calculus tasks with emphasis on the critical
    distinction between symbolic (exact) and numerical (approximate) methods.

    CRITICAL DECISION:
    -----------------
    The most important routing decision is determining whether to use:
    - Symbolic Engine (Risch algorithm) for exact closed-form results
    - Numerical Engine (Quadrature) for approximate numerical results

    This decision prevents wasted resources on non-integrable functions.

    ROUTING STRATEGY:
    ----------------
    Keyword-based routing (Phase 2 simplified):
    - "exact", "closed form", "antiderivative" → Symbolic
    - "approximate", "numerical", "area", "estimate" → Numerical
    - "derivative", "gradient" → Differentiation
    - "ODE", "PDE", "differential equation" → Differential Equation Solver
    - "series", "Taylor", "Fourier" → Series Specialist

    REFERENCE:
    ---------
    Phase_2_Build_Order_Breakdown.md: Lines 96-99
    """

    def __init__(
        self,
        agent_id: str = 'calculus_supervisor_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Calculus Supervisor

        Args:
            agent_id: Unique supervisor identifier
            df: Directory Facilitator instance
            blackboard: Blackboard instance
        """
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_routed = 0
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.symbolic_routes = 0
        self.numerical_routes = 0

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        print(f"[{self.agent_id}] Calculus Supervisor initialized")
        print(f"  Role: Strategic router with symbolic/numerical decision logic")
        print(f"  Critical Function: Prevent resource waste on non-integrable functions")
        print(f"  Mode: Analysis and delegation only - NEVER computes")

    def _register_services(self):
        """
        Register services with Directory Facilitator

        REFERENCE:
        ---------
        Phase_2_Build_Order_Breakdown.md: Line 99
        "DF REGISTRATION: service: math.calculus"
        """
        registration = create_service_registration(
            service_type='math.calculus',
            agent_id=self.agent_id,
            algorithm='routing',
            cost='low',
            type='supervisor',
            domain='calculus',
            tier='2',
            decision_logic='symbolic_vs_numerical'
        )
        self.df.register(registration)
        print(f"  [DF] Registered: math.calculus (supervisor with decision logic)")

    def process(self, task_entry: Any) -> Any:
        """
        Process calculus task by routing to appropriate specialist

        Args:
            task_entry: Blackboard entry containing task

        Returns:
            Result from specialist (via Blackboard)
        """
        print(f"\n[{self.agent_id}] Processing calculus task")

        # Extract task metadata
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        raw_input = metadata.get('raw_input', '').lower()

        print(f"  Task: {raw_input}")

        # Analyze task to determine routing
        routing_decision = self._analyze_task(task_entry)

        print(f"  Routing decision: {routing_decision['target']}")
        print(f"  Engine: {routing_decision.get('engine', 'N/A')}")
        print(f"  Reasoning: {routing_decision['reason']}")

        # Track routing statistics
        if routing_decision.get('engine') == 'symbolic':
            self.symbolic_routes += 1
        elif routing_decision.get('engine') == 'numerical':
            self.numerical_routes += 1

        # Query DF for appropriate specialist
        specialist_service = routing_decision['service_type']
        specialists = self._find_specialists(specialist_service)

        if not specialists:
            error_msg = f"No specialist available for: {specialist_service}"
            print(f"  [ERROR] {error_msg}")
            return self._create_error_result(task_entry, error_msg)

        print(f"  Found specialist: {specialists[0].agent_id}")

        # Delegate to specialist via Blackboard
        result = self._delegate_to_specialist(task_entry, specialists[0], routing_decision)

        self.tasks_routed += 1

        return result

    def _analyze_task(self, task_entry: Any) -> Dict[str, Any]:
        """
        Analyze task to determine routing strategy

        This implements the critical decision logic for symbolic vs numerical
        methods. This is the MOST IMPORTANT function of this supervisor.

        Args:
            task_entry: Task to analyze

        Returns:
            Routing decision with target service type and reasoning
        """
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        raw_input = metadata.get('raw_input', '').lower()
        operation = metadata.get('operation', 'compute')

        # Priority 1: Differential Equations
        if any(kw in raw_input for kw in ['ode', 'pde', 'differential equation', 'dy/dx', "d'", 'boundary']):
            return {
                'target': 'Differential Equation Solver',
                'service_type': 'math.calculus.ode',
                'reason': 'Detected differential equation keywords'
            }

        # Priority 2: Series Expansion
        if any(kw in raw_input for kw in ['series', 'taylor', 'fourier', 'expansion', 'convergence']):
            return {
                'target': 'Series Specialist',
                'service_type': 'math.calculus.series',
                'reason': 'Detected series expansion keywords'
            }

        # Priority 3: Differentiation
        if any(kw in raw_input for kw in ['derivative', 'differentiate', 'gradient', 'jacobian', 'hessian', "d/dx"]):
            return {
                'target': 'Differentiation Specialist',
                'service_type': 'math.calculus.diff',
                'reason': 'Detected differentiation keywords'
            }

        # Priority 4: Integration - THE CRITICAL SPLIT
        if any(kw in raw_input for kw in ['integrate', 'integral', 'antiderivative', 'area', 'accumulation']):
            # CRITICAL DECISION: Symbolic or Numerical?

            # Symbolic indicators
            if any(kw in raw_input for kw in ['exact', 'closed form', 'antiderivative', 'find the integral']):
                return {
                    'target': 'Integration Specialist',
                    'service_type': 'math.calculus.integration',
                    'engine': 'symbolic',
                    'reason': 'Exact/symbolic integration requested'
                }

            # Numerical indicators
            if any(kw in raw_input for kw in ['approximate', 'numerical', 'area', 'estimate', 'compute']):
                return {
                    'target': 'Integration Specialist',
                    'service_type': 'math.calculus.integration',
                    'engine': 'numerical',
                    'reason': 'Approximate/numerical integration requested'
                }

            # Default for integration: Try symbolic first
            return {
                'target': 'Integration Specialist',
                'service_type': 'math.calculus.integration',
                'engine': 'symbolic',
                'reason': 'Default to symbolic integration (will fallback to numerical if needed)'
            }

        # Default: Route to differentiation (most common calculus operation)
        return {
            'target': 'Differentiation Specialist',
            'service_type': 'math.calculus.diff',
            'reason': 'Default routing for general calculus computation'
        }

    def _find_specialists(self, service_type: str) -> List[Any]:
        """Query Directory Facilitator for specialists"""
        if not self.df:
            return []
        return self.df.search(service_type=service_type)

    def _delegate_to_specialist(
        self,
        task_entry: Any,
        specialist: Any,
        routing_decision: Dict[str, Any]
    ) -> Any:
        """
        Delegate task to specialist via Blackboard

        Args:
            task_entry: Original task
            specialist: Specialist service registration
            routing_decision: Routing analysis

        Returns:
            Delegation result
        """
        if not self.blackboard:
            return self._create_error_result(task_entry, "No Blackboard available")

        # Create delegated task entry
        delegation_id = f'delegation_{uuid.uuid4().hex[:8]}'

        # Update task metadata to include routing info
        delegated_metadata = dict(task_entry.metadata) if hasattr(task_entry, 'metadata') else {}
        delegated_metadata.update({
            'delegated_by': self.agent_id,
            'delegation_id': delegation_id,
            'assigned_agent': specialist.agent_id,
            'routing_reason': routing_decision['reason'],
            'engine': routing_decision.get('engine', 'default')
        })

        # Post delegated task
        delegated_entry = create_entry(
            entry_type=EntryType.TASK,
            content=task_entry.content,
            author_agent=self.agent_id,
            conversation_id=delegation_id,
            tags=[routing_decision['service_type'].split('.')[-1], 'delegated', delegation_id],
            metadata=delegated_metadata
        )

        self.blackboard.post(delegated_entry)

        print(f"  [OK] Delegated to {specialist.agent_id}")

        return delegated_entry

    def _create_error_result(self, task_entry: Any, error_msg: str) -> Any:
        """Create error result entry"""
        self.tasks_failed += 1

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

    # BDI Implementation (simplified for Phase 2)
    def update_beliefs(self):
        """Update beliefs - monitors Blackboard for calculus tasks"""
        pass

    def deliberate(self) -> List[Intention]:
        """Generate intentions - plans for task routing"""
        return []

    def execute_step(self, intention: Intention):
        """Execute intention step"""
        pass

    def get_statistics(self) -> Dict[str, Any]:
        """Get supervisor statistics"""
        stats = super().get_statistics()
        stats.update({
            'tasks_routed': self.tasks_routed,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'symbolic_routes': self.symbolic_routes,
            'numerical_routes': self.numerical_routes
        })
        return stats


if __name__ == "__main__":
    """Test Calculus Supervisor"""
    print("=" * 80)
    print("PHASE 2 - CALCULUS SUPERVISOR TEST")
    print("=" * 80)
    print()

    from symbo_agentic_reasoners_phase0.phase0_system import Phase0System

    # Initialize Phase 0
    print("Initializing Phase 0 infrastructure...")
    phase0 = Phase0System()
    phase0.start()
    print()

    # Initialize Calculus Supervisor
    supervisor = CalculusSupervisor(
        df=phase0.df,
        blackboard=phase0.blackboard
    )
    print()

    print("=" * 80)
    print("CALCULUS SUPERVISOR INITIALIZED")
    print("=" * 80)
    print()

    # Check DF registration
    services = phase0.df.search(service_type='math.calculus')
    print(f"Registered services: {len(services)}")
    for service in services:
        print(f"  - {service.service_type}: {service.agent_id}")
        print(f"    Decision Logic: {service.properties.get('decision_logic')}")

    print()
    print("Statistics:")
    import json
    print(json.dumps(supervisor.get_statistics(), indent=2))

    # Shutdown
    phase0.shutdown()
