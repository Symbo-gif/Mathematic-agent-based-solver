# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""NUMBER FIELDS SPECIALIST - Ring of integers, discriminant, ramification"""

import numpy as np
from typing import Dict, Any, List
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
from symbo_agentic_reasoners.core.omdoc_schema import create_variable

class NumberFieldsSpecialist(BDIAgent):
    """Number Fields Specialist - Quadratic fields, discriminant, algebraic integers"""

    def __init__(self, agent_id='number_fields_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = self.tasks_succeeded = self.tasks_failed = 0
        if self.df:
            self.df.register(create_service_registration(
                service_type='math.algebra.numbertheory.algebraic.fields', agent_id=self.agent_id,
                algorithm='quadratic_fields', cost='medium', instance=self, type='specialist', tier='3'))

    def process(self, task_entry):
        self.tasks_executed += 1
        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            d = metadata.get('d', -1)  # Q(sqrt(d))
            result = {'operation': 'quadratic_field', 'd': d, 'field': f'Q(sqrt({d}))',
                     'discriminant': d if d % 4 == 1 else 4*d,
                     'ring_of_integers': f'Z[sqrt({d})]' if d % 4 == 1 else f'Z[(1+sqrt({d}))/2]'}
            self.tasks_succeeded += 1
            return self._create_result_entry(task_entry, result, 'number_field')
        except Exception as e:
            self.tasks_failed += 1
            return {'error': str(e)}

    def _create_result_entry(self, task_entry, result, operation):
        if not self.blackboard: return result
        entry = create_entry(EntryType.PARTIAL_RESULT, create_variable(str(result)),
                           self.agent_id, task_entry.conversation_id, ['number_fields'],
                           EntryStatus.COMPLETED, {'result': result})
        self.blackboard.post(entry)
        return entry

    def update_beliefs(self): pass
    def deliberate(self) -> List[Intention]: return []
    def execute_step(self, intention: Intention): pass
    def get_statistics(self): return {**super().get_statistics(), 'tasks_executed': self.tasks_executed}
