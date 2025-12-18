# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""PROOF THEORY SUPERVISOR - Routes to cut elimination, ordinals, type theory specialists"""

from typing import List, Dict, Any, Optional
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator, create_service_registration
from symbo_agentic_reasoners.core.blackboard import Blackboard, create_entry, EntryType, EntryStatus

class ProofTheorySupervisor(BDIAgent):
    """Proof Theory Supervisor - Routes proof-theoretic tasks"""

    def __init__(self, agent_id='proof_theory_supervisor_001', df: Optional[DirectoryFacilitator]=None,
                 blackboard: Optional[Blackboard]=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_routed = self.tasks_completed = self.tasks_failed = 0
        if self.df:
            self.df.register(create_service_registration(
                service_type='math.prooftheory', agent_id=self.agent_id, algorithm='routing',
                cost='low', instance=self, type='supervisor', domain='proof_theory', tier='2'))

    def process(self, task_entry):
        self.tasks_routed += 1
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        raw_input = metadata.get('raw_input', '').lower()

        # Route based on keywords
        if 'cut elimination' in raw_input or 'hauptsatz' in raw_input:
            service_type = 'math.prooftheory.cutelimination'
        elif 'ordinal' in raw_input or 'proof-theoretic ordinal' in raw_input:
            service_type = 'math.prooftheory.ordinals'
        elif 'type theory' in raw_input or 'dependent type' in raw_input or 'polymorphism' in raw_input:
            service_type = 'math.prooftheory.types'
        elif 'curry-howard' in raw_input or 'propositions as types' in raw_input:
            service_type = 'math.prooftheory.curryhoward'
        elif 'constructive' in raw_input or 'intuitionistic' in raw_input:
            service_type = 'math.prooftheory.constructive'
        else:
            service_type = 'math.prooftheory.cutelimination'  # Default

        specialists = self.df.search(service_type=service_type) if self.df else []
        if specialists and hasattr(specialists[0], 'process'):
            return specialists[0].process(task_entry)
        return {'error': 'No specialist found'}

    def update_beliefs(self): pass
    def deliberate(self) -> List[Intention]: return []
    def execute_step(self, intention: Intention): pass
    def get_statistics(self): return {**super().get_statistics(), 'tasks_routed': self.tasks_routed}
