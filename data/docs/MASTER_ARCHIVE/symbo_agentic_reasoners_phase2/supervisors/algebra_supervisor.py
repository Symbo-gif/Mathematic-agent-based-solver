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
PHASE 2 - STEP 1: ALGEBRA SUPERVISOR (Tier 2)
==============================================

The Algebra Supervisor acts as the "Foreman" for all algebraic tasks.
Its primary logic is simplification strategy, not direct computation.

DIRECTIVE:
---------
Route high-level algebra tasks to appropriate specialists based on:
- Task complexity analysis
- Prerequisite identification (e.g., factoring before root-finding)
- Specialist capability matching

ROUTING LOGIC:
-------------
- Arbitrary-precision arithmetic → Arithmetic Specialist
- Polynomial operations → Polynomial Manipulation Specialist
- Prime/integer tasks → Number Theory Specialist

REFERENCE:
---------
- Phase_2_Build_Order_Breakdown.md: Lines 50-53 (Agent 1.1)
- Phase 2 Coding Strategy: Section 3.1 "The Foundation Layer"
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


class AlgebraSupervisor(BDIAgent):
    """
    Algebra Supervisor - Tier 2 Strategic Router

    ROLE:
    ----
    Acts as foreman for all algebraic tasks. Routes tasks to appropriate
    specialists based on task analysis and prerequisite understanding.

    CRITICAL:
    --------
    Like all supervisors, this agent NEVER computes. It only:
    1. Analyzes task requirements
    2. Determines prerequisites
    3. Routes to appropriate specialist
    4. Aggregates results

    ROUTING STRATEGY:
    ----------------
    - Contains integers/fractions with high precision needs → Arithmetic
    - Polynomial expressions/equations → Polynomial Manipulation
    - Prime numbers/factorization/modular arithmetic → Number Theory

    REFERENCE:
    ---------
    Phase_2_Build_Order_Breakdown.md: Lines 50-53
    """

    def __init__(
        self,
        agent_id: str = 'algebra_supervisor_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Algebra Supervisor

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

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        print(f"[{self.agent_id}] Algebra Supervisor initialized")
        print(f"  Role: Strategic router for algebraic tasks")
        print(f"  Mode: Analysis and delegation only - NEVER computes")

    def _register_services(self):
        """
        Register services with Directory Facilitator

        REFERENCE:
        ---------
        Phase_2_Build_Order_Breakdown.md: Lines 53
        "DF REGISTRATION: service: math.algebra"
        """
        registration = create_service_registration(
            service_type='math.algebra',
            agent_id=self.agent_id,
            algorithm='routing',
            cost='low',
            type='supervisor',
            domain='algebra',
            tier='2'
        )
        self.df.register(registration)
        print(f"  [DF] Registered: math.algebra (supervisor)")

    def process(self, task_entry: Any) -> Any:
        """
        Process algebra task by routing to appropriate specialist

        Args:
            task_entry: Blackboard entry containing task

        Returns:
            Result from specialist (via Blackboard)
        """
        print(f"\n[{self.agent_id}] Processing algebra task")

        # Extract task metadata
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        raw_input = metadata.get('raw_input', '')

        print(f"  Task: {raw_input}")

        # Analyze task to determine routing
        routing_decision = self._analyze_task(task_entry)

        print(f"  Routing decision: {routing_decision['target']}")
        print(f"  Reasoning: {routing_decision['reason']}")

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

        This implements the supervisor's strategic logic for understanding
        task requirements and prerequisites.

        Args:
            task_entry: Task to analyze

        Returns:
            Routing decision with target service type and reasoning
        """
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        raw_input = metadata.get('raw_input', '').lower()
        operation = metadata.get('operation', 'compute')

        # Keyword-based analysis (simplified for Phase 2)
        # Phase 3 will implement more sophisticated NLU

        # Number Theory keywords
        if any(kw in raw_input for kw in ['prime', 'factor', 'gcd', 'lcm', 'modulo', 'mod', 'divisible']):
            return {
                'target': 'Number Theory Specialist',
                'service_type': 'math.algebra.numbertheory',
                'reason': 'Detected number theory keywords (prime/factor/gcd/etc)'
            }

        # Polynomial keywords
        if any(kw in raw_input for kw in ['polynomial', 'factor', 'roots', 'solve', 'equation', 'x**', '^']):
            return {
                'target': 'Polynomial Manipulation Specialist',
                'service_type': 'math.algebra.polynomial',
                'reason': 'Detected polynomial keywords (solve/factor/roots/etc)'
            }

        # Arithmetic (default for numeric operations)
        if any(kw in raw_input for kw in ['calculate', 'compute', 'add', 'subtract', 'multiply', 'divide', 'power']):
            return {
                'target': 'Arithmetic Specialist',
                'service_type': 'math.algebra.arithmetic',
                'reason': 'Detected arithmetic keywords (calculate/compute/etc)'
            }

        # Default to Arithmetic Specialist
        return {
            'target': 'Arithmetic Specialist',
            'service_type': 'math.algebra.arithmetic',
            'reason': 'Default routing for general algebraic computation'
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
            'routing_reason': routing_decision['reason']
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
        """Update beliefs - monitors Blackboard for algebra tasks"""
        # Phase 2: Direct method invocation
        # Phase 3: Full BDI loop with proactive task monitoring
        pass

    def deliberate(self) -> List[Intention]:
        """Generate intentions - plans for task routing"""
        # Phase 2: Reactive routing via process()
        # Phase 3: Proactive task decomposition
        return []

    def execute_step(self, intention: Intention):
        """Execute intention step"""
        # Phase 2: Simplified execution
        pass

    def get_statistics(self) -> Dict[str, Any]:
        """Get supervisor statistics"""
        stats = super().get_statistics()
        stats.update({
            'tasks_routed': self.tasks_routed,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed
        })
        return stats


if __name__ == "__main__":
    """Test Algebra Supervisor"""
    print("=" * 80)
    print("PHASE 2 - ALGEBRA SUPERVISOR TEST")
    print("=" * 80)
    print()

    from symbo_agentic_reasoners_phase0.phase0_system import Phase0System

    # Initialize Phase 0
    print("Initializing Phase 0 infrastructure...")
    phase0 = Phase0System()
    phase0.start()
    print()

    # Initialize Algebra Supervisor
    supervisor = AlgebraSupervisor(
        df=phase0.df,
        blackboard=phase0.blackboard
    )
    print()

    print("=" * 80)
    print("ALGEBRA SUPERVISOR INITIALIZED")
    print("=" * 80)
    print()

    # Check DF registration
    services = phase0.df.search(service_type='math.algebra')
    print(f"Registered services: {len(services)}")
    for service in services:
        print(f"  - {service.service_type}: {service.agent_id}")

    print()
    print("Statistics:")
    import json
    print(json.dumps(supervisor.get_statistics(), indent=2))

    # Shutdown
    phase0.shutdown()
