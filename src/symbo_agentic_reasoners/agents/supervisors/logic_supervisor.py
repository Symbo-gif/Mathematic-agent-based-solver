# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
LOGIC SUPERVISOR (Tier 2)
=========================

Routes logic problems to appropriate Tier 3 specialists:
- Propositional Logic (truth tables, SAT, equivalence)
- Predicate Logic (quantifiers, predicates, unification)
- Proofs (induction, contradiction, direct proof)

Handles: Boolean algebra, formal reasoning, proof verification.
"""

from typing import Any, Dict, List, Optional
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard


class LogicSupervisor(BDIAgent):
    """Supervisor for logic problems."""

    # Keywords for routing
    PROPOSITIONAL_KEYWORDS = [
        'truth table', 'tautology', 'contradiction', 'satisfiable',
        'boolean', 'cnf', 'dnf', 'logical equivalent', 'and', 'or',
        'not', 'implies', 'iff', 'xor', 'nand', 'nor'
    ]
    PREDICATE_KEYWORDS = [
        'forall', 'exists', 'quantifier', 'predicate', 'domain',
        'universal', 'existential', 'substitution', 'unify', 'first order'
    ]
    PROOF_KEYWORDS = [
        'proof', 'prove', 'induction', 'contradiction', 'contrapositive',
        'direct proof', 'case', 'qed', 'therefore', 'hence', 'lemma',
        'theorem', 'corollary'
    ]

    def __init__(
        self,
        agent_id: str = 'logic_supervisor_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Logic Supervisor.

        Sets up routing infrastructure for logic tasks. Routes to
        Propositional, Predicate, and Proof specialists.

        Args:
            agent_id: Unique identifier (default: 'logic_supervisor_001')
            df: Directory Facilitator for service registration
            blackboard: Shared memory for agent communication

        Example:
            >>> supervisor = LogicSupervisor()
            >>> result = supervisor.process({"problem": "Prove using resolution"})

        Notes:
            - Tracks routing statistics
            - Auto-registers with Directory Facilitator if provided
            - Tier 2 strategic router (no computation)
        """
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_routed = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.logic',
                agent_id=agent_id,
                algorithm='supervisor_routing',
                cost='low',
                instance=self,
                tier='2',
                capabilities='propositional_predicate_proof_routing'
            ))

        print(f"[{agent_id}] Logic Supervisor initialized")
        print(f"  Specialists: Propositional, Predicate, Proof")

    def route_task(self, task: Dict[str, Any]) -> str:
        """Determine which specialist should handle the task."""
        problem = str(task.get('problem', '')).lower()
        operation = str(task.get('operation', '')).lower()

        # Check proof keywords first (most specific)
        for keyword in self.PROOF_KEYWORDS:
            if keyword in problem or keyword in operation:
                return 'math.logic.proof'

        # Check predicate logic
        for keyword in self.PREDICATE_KEYWORDS:
            if keyword in problem or keyword in operation:
                return 'math.logic.predicate'

        # Check propositional
        for keyword in self.PROPOSITIONAL_KEYWORDS:
            if keyword in problem or keyword in operation:
                return 'math.logic.propositional'

        # Default to propositional
        return 'math.logic.propositional'

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route task to appropriate specialist."""
        self.tasks_routed += 1

        specialist_type = self.route_task(task)

        if self.df:
            specialists = self.df.search(service_type=specialist_type)
            if specialists:
                return {
                    'status': 'routed',
                    'specialist_type': specialist_type,
                    'specialist_id': specialists[0]['agent_id'],
                    'task': task
                }

        return {
            'status': 'no_specialist',
            'specialist_type': specialist_type,
            'task': task
        }

    # ==========================================================================
    # REAL BDI IMPLEMENTATION
    # ==========================================================================

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for logic tasks."""
        if not self.blackboard:
            return

        try:
            pending_tasks = self.blackboard.query_entries(tags=['logic'], status='pending')
            task_entries = self.blackboard.query_entries(entry_type='task', status='pending')

            for task in task_entries:
                domain = ''
                if hasattr(task, 'metadata') and task.metadata:
                    domain = task.metadata.get('domain', '').lower()
                if domain in ['logic', ''] and task not in pending_tasks:
                    pending_tasks.append(task)

            for task in pending_tasks:
                belief_key = f'pending_logic_{task.entry_id}'
                if not self.has_belief(f'routed_{task.entry_id}') and not self.has_belief(f'delegated_{task.entry_id}'):
                    if not self.has_belief(belief_key):
                        self.add_belief(predicate=belief_key, content=task, confidence=1.0, source='blackboard')

            for predicate in list(self.beliefs.keys()):
                if predicate.startswith('delegated_'):
                    delegation_info = self.get_belief(predicate).content
                    delegation_id = delegation_info.get('delegation_id')
                    results = self.blackboard.query_entries(tags=[delegation_id, 'result'], status='completed')
                    if results:
                        self.add_belief(f'result_{delegation_id}', results[0], source='specialist')
                        self.remove_belief(predicate)
                    failures = self.blackboard.query_entries(tags=[delegation_id], status='failed')
                    if failures:
                        self.add_belief(f'failed_{delegation_id}', failures[0], source='specialist')
                        self.remove_belief(predicate)
        except Exception as e:
            print(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create routing plans for logic tasks."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_logic_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            # Analyze task for routing
            metadata = task.metadata if hasattr(task, 'metadata') else {}
            raw_input = metadata.get('raw_input', '').lower()
            routing = {'service_type': self.route_task({'problem': raw_input, 'operation': ''}), 'reason': 'Logic routing'}

            intention = Intention(
                plan_id=f'route_{task_id}',
                steps=['analyze_task', 'find_specialist', 'delegate_task', 'track_result'],
                target_desire='route_logic_task',
                metadata={'task_id': task_id, 'task_entry': task, 'routing_decision': routing}
            )
            new_intentions.append(intention)
        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Execute routing steps."""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')
        routing = intention.metadata.get('routing_decision', {})

        try:
            if action == 'analyze_task':
                intention.advance()
            elif action == 'find_specialist':
                specialists = self._find_specialists(routing.get('service_type', 'math.logic.propositional'))
                if specialists:
                    intention.metadata['specialist'] = specialists[0]
                    intention.advance()
                else:
                    raise ValueError(f"No specialist for {routing.get('service_type')}")
            elif action == 'delegate_task':
                specialist = intention.metadata.get('specialist')
                if not specialist or not self.blackboard:
                    raise ValueError("No specialist or blackboard")

                import uuid
                from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus

                delegation_id = f'delegation_{uuid.uuid4().hex[:8]}'
                delegated_metadata = dict(task.metadata) if hasattr(task, 'metadata') else {}
                delegated_metadata.update({
                    'delegated_by': self.agent_id, 'delegation_id': delegation_id,
                    'assigned_agent': specialist.agent_id, 'routing_reason': routing.get('reason', ''),
                    'original_task_id': task_id
                })

                specialist_tag = routing.get('service_type', 'propositional').split('.')[-1]
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
                self.remove_belief(f'pending_logic_{task_id}')
                self.tasks_routed += 1
                intention.advance()
            elif action == 'track_result':
                intention.advance()
            else:
                intention.advance()
        except Exception as e:
            print(f"[{self.agent_id}] Step {action} failed: {e}")
            if task_id:
                self.remove_belief(f'pending_logic_{task_id}')
            while not intention.is_complete():
                intention.advance()

    def _find_specialists(self, service_type: str) -> List[Any]:
        """Query DF for specialists"""
        if not self.df:
            return []
        return self.df.search(service_type=service_type)

    def get_statistics(self) -> Dict[str, Any]:
        stats = super().get_statistics()
        stats['tasks_routed'] = self.tasks_routed
        return stats
