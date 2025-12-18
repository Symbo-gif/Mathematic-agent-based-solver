# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
PRIME DISTRIBUTION SPECIALIST (Tier 3)
Handles prime number theorem, prime counting, sieve methods.
"""

import numpy as np
from typing import Dict, Any, List
import logging

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
from symbo_agentic_reasoners.core.omdoc_schema import create_variable

logger = logging.getLogger(__name__)


class PrimeDistributionSpecialist(BDIAgent):
    """Prime Distribution Specialist - Prime number theorem, prime counting"""

    def __init__(self, agent_id='prime_distribution_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = self.tasks_succeeded = self.tasks_failed = 0
        self.prime_counts = 0
        if self.df:
            self._register_services()

    def _register_services(self):
        self.df.register(create_service_registration(
            service_type='math.algebra.numbertheory.analytic.primes', agent_id=self.agent_id,
            algorithm='prime_counting', cost='medium', instance=self, type='specialist', tier='3',
            capabilities='prime_number_theorem_pi_function_chebyshev_functions'
        ))

    def process(self, task_entry):
        self.tasks_executed += 1
        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            x = metadata.get('x', 100)
            result = self._count_primes(x)
            self.tasks_succeeded += 1
            return self._create_result_entry(task_entry, result, 'prime_counting')
        except Exception as e:
            self.tasks_failed += 1
            return self._create_error_entry(task_entry, str(e))

    def _count_primes(self, x: int) -> Dict[str, Any]:
        """Prime counting function π(x) and comparison with x/ln(x)"""
        self.prime_counts += 1

        # Sieve of Eratosthenes
        if x < 2:
            pi_x = 0
            primes = []
        else:
            sieve = [True] * (x + 1)
            sieve[0] = sieve[1] = False
            for i in range(2, int(np.sqrt(x)) + 1):
                if sieve[i]:
                    for j in range(i*i, x + 1, i):
                        sieve[j] = False
            primes = [i for i in range(x + 1) if sieve[i]]
            pi_x = len(primes)

        # Prime number theorem approximation
        pnt_approx = x / np.log(x) if x > 1 else 0
        error = abs(pi_x - pnt_approx) if x > 1 else 0
        relative_error = error / pi_x if pi_x > 0 else 0

        return {
            'operation': 'prime_counting',
            'x': x,
            'pi(x)': pi_x,
            'pnt_approximation': pnt_approx,
            'error': error,
            'relative_error': relative_error,
            'primes': primes if len(primes) <= 100 else f'{len(primes)} primes (too many to display)',
            'explanation': f'π({x}) = {pi_x}, x/ln(x) ≈ {pnt_approx:.2f}, error = {relative_error:.2%}'
        }

    def _create_result_entry(self, task_entry, result, operation):
        if not self.blackboard:
            return result
        entry = create_entry(EntryType.PARTIAL_RESULT, create_variable(str(result)),
                           self.agent_id, task_entry.conversation_id, ['primes', 'result'],
                           EntryStatus.COMPLETED, {'result': result, 'operation': operation})
        self.blackboard.post(entry)
        return entry

    def _create_error_entry(self, task_entry, error_msg):
        if not self.blackboard:
            return {'error': error_msg}
        entry = create_entry(EntryType.PARTIAL_RESULT, create_variable(f"ERROR: {error_msg}"),
                           self.agent_id, task_entry.conversation_id, ['error'],
                           EntryStatus.FAILED, {'error': error_msg})
        self.blackboard.post(entry)
        return entry

    def update_beliefs(self):
        if not self.blackboard:
            return
        try:
            tasks = self.blackboard.query_entries(tags=['prime_distribution'], status=EntryStatus.PENDING)
            for task in tasks:
                if not self.has_belief(f'pending_prime_{task.entry_id}'):
                    self.add_belief(f'pending_prime_{task.entry_id}', task, 1.0, 'blackboard')
        except: pass

    def deliberate(self) -> List[Intention]:
        return [Intention(f'count_{t.content.entry_id}', ['claim', 'count', 'post'],
                         'count_primes', {'task_entry': t.content})
                for p, t in self.beliefs.items() if p.startswith('pending_prime_')]

    def execute_step(self, intention: Intention):
        action = intention.get_current_action()
        if action in ['claim', 'count']:
            intention.advance()
        elif action == 'post':
            intention.mark_completed()

    def get_statistics(self) -> Dict[str, Any]:
        return {**super().get_statistics(), 'tasks_executed': self.tasks_executed,
                'tasks_succeeded': self.tasks_succeeded, 'prime_counts': self.prime_counts}
