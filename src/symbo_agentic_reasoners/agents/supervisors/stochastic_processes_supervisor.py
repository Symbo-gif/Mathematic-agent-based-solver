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
PHASE 1 - STOCHASTIC PROCESSES SUPERVISOR (Tier 2)
===================================================

The Stochastic Processes Supervisor routes stochastic analysis tasks
to appropriate specialists.

ROUTING LOGIC:
-------------
- Brownian motion / Wiener process → Brownian Motion Specialist
- SDE / Ito calculus → SDE Solver Specialist
- Levy processes / jump processes → Levy Process Specialist
- Martingales / stopping times → Martingale Theory Specialist
- Continuous-time Markov → Markov Process Specialist
- Stochastic calculus / Girsanov → Stochastic Calculus Specialist

NO SYMPY - Pure native mathematical reasoning.
"""

from typing import List, Dict, Any, Optional
import logging

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)

logger = logging.getLogger(__name__)


class StochasticProcessesSupervisor(BDIAgent):
    """
    Stochastic Processes Supervisor - Tier 2 Strategic Router

    ROLE:
    ----
    Routes stochastic analysis tasks to appropriate specialists.
    NEVER computes - only analyzes and routes.

    ROUTING STRATEGY:
    ----------------
    - Brownian motion keywords → Brownian Motion Specialist
    - SDE keywords → SDE Solver Specialist
    - Levy process keywords → Levy Process Specialist
    - Martingale keywords → Martingale Theory Specialist
    - Markov process keywords → Markov Process Specialist
    - Stochastic calculus → Stochastic Calculus Specialist
    """

    def __init__(
        self,
        agent_id: str = 'stochastic_processes_supervisor_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Stochastic Processes Supervisor

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

        logger.info(f"[{self.agent_id}] Stochastic Processes Supervisor initialized")
        logger.info(f"  Role: Strategic router for stochastic analysis tasks")
        logger.info(f"  Mode: Analysis and delegation only - NEVER computes")

    def _register_services(self):
        """Register services with Directory Facilitator"""
        registration = create_service_registration(
            service_type='math.stochastic',
            agent_id=self.agent_id,
            algorithm='routing',
            cost='low',
            instance=self,  # Register instance for direct invocation
            type='supervisor',
            domain='stochastic_processes',
            tier='2'
        )
        self.df.register(registration)
        logger.info(f"  [DF] Registered: math.stochastic (supervisor)")

    def process(self, task_entry: Any) -> Any:
        """
        Process stochastic task by routing to appropriate specialist

        Args:
            task_entry: Blackboard entry containing task

        Returns:
            Result from specialist (via Blackboard)
        """
        logger.info(f"\n[{self.agent_id}] Processing stochastic processes task")

        self.tasks_routed += 1

        # Extract metadata
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        raw_input = metadata.get('raw_input', '').lower()

        logger.info(f"  Raw input: {raw_input[:100]}...")

        # Analyze task and determine routing
        routing_decision = self._analyze_task(task_entry)

        logger.info(f"  Routing to: {routing_decision['target']}")
        logger.info(f"  Reason: {routing_decision['reason']}")

        # Find specialist via Directory Facilitator
        specialists = self._find_specialists(routing_decision['service_type'])

        if not specialists:
            error_msg = f"No specialist available for {routing_decision['target']}"
            logger.error(f"  [ERROR] {error_msg}")
            self.tasks_failed += 1
            return self._create_error_result(task_entry, error_msg)

        # Delegate to specialist
        specialist = specialists[0]  # Use first available specialist
        logger.info(f"  Delegating to: {specialist.agent_id}")

        result = self._delegate_to_specialist(task_entry, specialist, routing_decision)
        return result

    def _analyze_task(self, task_entry: Any) -> Dict[str, Any]:
        """
        Analyze task and determine which specialist to route to

        Args:
            task_entry: Task to analyze

        Returns:
            dict with 'target', 'service_type', 'reason'
        """
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        raw_input = metadata.get('raw_input', '').lower()

        # Brownian motion / Wiener process
        brownian_kw = ['brownian', 'wiener', 'gaussian process', 'random walk']
        if any(kw in raw_input for kw in brownian_kw):
            return {
                'target': 'Brownian Motion Specialist',
                'service_type': 'math.stochastic.brownian',
                'reason': 'Detected Brownian motion / Wiener process keywords'
            }

        # SDE / Ito calculus
        sde_kw = ['sde', 'stochastic differential equation', 'ito', 'euler-maruyama', 'milstein']
        if any(kw in raw_input for kw in sde_kw):
            return {
                'target': 'SDE Solver Specialist',
                'service_type': 'math.stochastic.sde',
                'reason': 'Detected SDE / Ito calculus keywords'
            }

        # Levy processes
        levy_kw = ['levy', 'jump process', 'compound poisson', 'levy-khintchine']
        if any(kw in raw_input for kw in levy_kw):
            return {
                'target': 'Levy Process Specialist',
                'service_type': 'math.stochastic.levy',
                'reason': 'Detected Levy process keywords'
            }

        # Martingales
        martingale_kw = ['martingale', 'submartingale', 'supermartingale', 'stopping time', 'optional sampling']
        if any(kw in raw_input for kw in martingale_kw):
            return {
                'target': 'Martingale Theory Specialist',
                'service_type': 'math.stochastic.martingale',
                'reason': 'Detected martingale theory keywords'
            }

        # Markov processes
        markov_kw = ['markov', 'markov chain', 'markov process', 'kolmogorov equation', 'generator']
        if any(kw in raw_input for kw in markov_kw):
            return {
                'target': 'Markov Process Specialist',
                'service_type': 'math.stochastic.markov',
                'reason': 'Detected Markov process keywords'
            }

        # Stochastic calculus
        calc_kw = ['stochastic calculus', 'stratonovich', 'girsanov', 'novikov', 'change of measure']
        if any(kw in raw_input for kw in calc_kw):
            return {
                'target': 'Stochastic Calculus Specialist',
                'service_type': 'math.stochastic.calculus',
                'reason': 'Detected stochastic calculus keywords'
            }

        # Default to Brownian Motion (most fundamental)
        return {
            'target': 'Brownian Motion Specialist',
            'service_type': 'math.stochastic.brownian',
            'reason': 'Default stochastic process routing'
        }

    def _find_specialists(self, service_type: str) -> List[Any]:
        """
        Find specialists via Directory Facilitator

        Args:
            service_type: Service type to search for

        Returns:
            List of matching specialists
        """
        if not self.df:
            return []

        specialists = self.df.search(service_type=service_type)
        return specialists

    def _delegate_to_specialist(self, task_entry: Any, specialist: Any, routing_decision: Dict[str, Any]) -> Any:
        """
        Delegate task to specialist via Blackboard

        Args:
            task_entry: Original task
            specialist: Specialist to delegate to
            routing_decision: Routing decision metadata

        Returns:
            Result from specialist
        """
        if not self.blackboard:
            logger.warning("No blackboard - cannot delegate")
            return None

        # Create delegated task entry
        delegation_id = f"delegation_{task_entry.entry_id}"

        delegated_entry = create_entry(
            entry_type=EntryType.TASK,
            content=task_entry.content,
            author_agent=self.agent_id,
            conversation_id=task_entry.conversation_id,
            tags=['stochastic', routing_decision['target'].lower().replace(' ', '_'), delegation_id],
            status=EntryStatus.PENDING,
            metadata={
                **task_entry.metadata,
                'delegated_by': self.agent_id,
                'delegation_id': delegation_id,
                'assigned_agent': specialist.agent_id,
                'routing_reason': routing_decision['reason'],
                'original_task_id': task_entry.entry_id
            }
        )

        self.blackboard.post(delegated_entry)

        # Process directly if specialist has process method
        if hasattr(specialist, 'process'):
            result = specialist.process(delegated_entry)
            if result:
                self.tasks_completed += 1
            return result

        return delegated_entry

    def _create_error_result(self, task_entry: Any, error_msg: str) -> Any:
        """
        Create error result entry

        Args:
            task_entry: Original task
            error_msg: Error message

        Returns:
            Error entry
        """
        if not self.blackboard:
            return None

        error_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=task_entry.content,
            author_agent=self.agent_id,
            conversation_id=task_entry.conversation_id,
            tags=['error'],
            status=EntryStatus.FAILED,
            metadata={'error': error_msg}
        )

        self.blackboard.post(error_entry)
        return error_entry

    def update_beliefs(self):
        """PERCEIVE: Query Blackboard for stochastic tasks"""
        if not self.blackboard:
            return

        try:
            # Query for stochastic tasks
            tasks = self.blackboard.query_entries(
                tags=['stochastic'],
                status=EntryStatus.PENDING
            )

            for task in tasks:
                belief_key = f'pending_stochastic_{task.entry_id}'
                if not self.has_belief(belief_key):
                    self.add_belief(
                        predicate=belief_key,
                        content=task,
                        confidence=1.0,
                        source='blackboard'
                    )
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create routing intentions"""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_stochastic_'):
                continue

            task = belief.content
            task_id = task.entry_id

            # Skip if already working on this task
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            # Build routing plan
            steps = ['analyze_task', 'find_specialist', 'delegate_task', 'track_result']

            intention = Intention(
                plan_id=f'route_{task_id}',
                steps=steps,
                target_desire='route_stochastic_task',
                metadata={
                    'task_id': task_id,
                    'task_entry': task
                }
            )
            new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Execute one routing step"""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')

        try:
            if action == 'analyze_task':
                routing = self._analyze_task(task)
                intention.metadata['routing_decision'] = routing
                intention.advance()

            elif action == 'find_specialist':
                routing = intention.metadata.get('routing_decision', {})
                specialists = self._find_specialists(routing.get('service_type', ''))
                if specialists:
                    intention.metadata['specialist'] = specialists[0]
                    intention.advance()
                else:
                    self.tasks_failed += 1
                    intention.mark_failed()

            elif action == 'delegate_task':
                specialist = intention.metadata.get('specialist')
                routing = intention.metadata.get('routing_decision', {})
                result = self._delegate_to_specialist(task, specialist, routing)
                intention.metadata['result'] = result
                intention.advance()

            elif action == 'track_result':
                self.tasks_completed += 1
                intention.mark_completed()

        except Exception as e:
            logger.error(f"[{self.agent_id}] Execute step error: {e}")
            self.tasks_failed += 1
            intention.mark_failed()

    def get_statistics(self) -> Dict[str, Any]:
        """Return supervisor statistics"""
        return {
            'agent_id': self.agent_id,
            'tier': 2,
            'role': 'supervisor',
            'domain': 'stochastic_processes',
            'tasks_routed': self.tasks_routed,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'success_rate': (self.tasks_completed / self.tasks_routed * 100)
                           if self.tasks_routed > 0 else 0.0
        }


if __name__ == "__main__":
    # Quick test
    supervisor = StochasticProcessesSupervisor()
    print(f"\nSupervisor initialized: {supervisor.agent_id}")
    print(f"Statistics: {supervisor.get_statistics()}")
