# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
COMPUTABILITY SUPERVISOR (Tier 2) - Phase 2
Routes to Turing machines, recursive functions, complexity theory specialists
"""

from typing import List, Dict, Any, Optional
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator, create_service_registration
from symbo_agentic_reasoners.core.blackboard import Blackboard

class ComputabilitySupervisor(BDIAgent):
    """Computability Theory Supervisor - Routes computability and complexity tasks"""

    def __init__(self, agent_id='computability_supervisor_001', df: Optional[DirectoryFacilitator]=None,
                 blackboard: Optional[Blackboard]=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_routed = 0
        if self.df:
            self.df.register(create_service_registration(
                service_type='math.computability', agent_id=self.agent_id, algorithm='routing',
                cost='low', instance=self, type='supervisor', domain='computability', tier='2'))

    def process(self, task_entry):
        self.tasks_routed += 1
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        raw_input = metadata.get('raw_input', '').lower()

        if 'turing machine' in raw_input or 'halting' in raw_input:
            service_type = 'math.computability.turing'
        elif 'recursive' in raw_input or 'primitive recursive' in raw_input:
            service_type = 'math.computability.recursion'
        elif 'turing degree' in raw_input or 'reducibility' in raw_input:
            service_type = 'math.computability.degrees'
        elif 'complexity' in raw_input or 'p vs np' in raw_input:
            service_type = 'math.computability.complexity'
        elif 'kolmogorov' in raw_input:
            service_type = 'math.computability.kolmogorov'
        else:
            service_type = 'math.computability.turing'

        specialists = self.df.search(service_type=service_type) if self.df else []
        if specialists and hasattr(specialists[0], 'process'):
            return specialists[0].process(task_entry)
        return {'error': 'No specialist found'}

    def update_beliefs(self): pass
    def deliberate(self) -> List[Intention]: return []
    def execute_step(self, intention: Intention): pass
    def get_statistics(self): return {**super().get_statistics(), 'tasks_routed': self.tasks_routed}
