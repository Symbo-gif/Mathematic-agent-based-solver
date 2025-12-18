# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
STOCHASTIC CALCULUS SPECIALIST (Tier 3)
Handles Ito's lemma, Girsanov theorem, change of measure.
"""

import numpy as np
from typing import Dict, Any, List
import logging

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
from symbo_agentic_reasoners.core.omdoc_schema import create_variable

logger = logging.getLogger(__name__)


class StochasticCalculusSpecialist(BDIAgent):
    """Stochastic Calculus Specialist - Ito's lemma, Girsanov, change of measure"""

    def __init__(self, agent_id='stochastic_calculus_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = self.tasks_succeeded = self.tasks_failed = 0
        self.ito_applications = 0
        self.girsanov_transforms = 0
        if self.df:
            self._register_services()
        logger.info(f"[{self.agent_id}] Stochastic Calculus Specialist initialized")

    def _register_services(self):
        self.df.register(create_service_registration(
            service_type='math.stochastic.calculus', agent_id=self.agent_id,
            algorithm='ito_girsanov', cost='medium', instance=self,
            type='specialist', tier='3', capabilities='ito_lemma_girsanov_theorem'
        ))

    def process(self, task_entry):
        self.tasks_executed += 1
        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            raw_input = metadata.get('raw_input', '')

            if 'ito' in raw_input.lower() or 'ito lemma' in raw_input.lower():
                result = self._apply_ito_lemma(
                    function_type=metadata.get('function_type', 'quadratic'),
                    mu=metadata.get('mu', 0.0),
                    sigma=metadata.get('sigma', 1.0)
                )
            elif 'girsanov' in raw_input.lower():
                result = self._apply_girsanov_theorem(
                    drift_change=metadata.get('drift_change', 0.1),
                    T=metadata.get('T', 1.0)
                )
            else:
                result = self._compute_quadratic_variation(
                    T=metadata.get('T', 1.0),
                    n_steps=metadata.get('n_steps', 1000)
                )

            self.tasks_succeeded += 1
            return self._create_result_entry(task_entry, result, 'stochastic_calculus')
        except Exception as e:
            logger.error(f"[{self.agent_id}] Error: {e}")
            self.tasks_failed += 1
            return self._create_error_entry(task_entry, str(e))

    def _apply_ito_lemma(self, function_type, mu, sigma):
        """Apply Ito's lemma to derive SDE for f(X_t)"""
        self.ito_applications += 1

        if function_type == 'quadratic':
            # For f(x) = x^2, df/dx = 2x, d^2f/dx^2 = 2
            # d(X^2) = 2X dX + (1/2)*2*sigma^2 dt = 2X(mu dt + sigma dW) + sigma^2 dt
            drift_term = f'2X*{mu} + {sigma**2}'
            diffusion_term = f'2X*{sigma}'
            result_sde = f'd(X^2) = ({drift_term}) dt + ({diffusion_term}) dW'
        elif function_type == 'exp':
            # For f(x) = exp(x), df/dx = exp(x), d^2f/dx^2 = exp(x)
            # d(exp(X)) = exp(X)(mu + sigma^2/2) dt + exp(X)*sigma dW
            drift_term = f'exp(X)*({mu} + {sigma**2/2})'
            diffusion_term = f'exp(X)*{sigma}'
            result_sde = f'd(exp(X)) = ({drift_term}) dt + ({diffusion_term}) dW'
        else:
            result_sde = 'Unknown function type'

        return {
            'operation': 'ito_lemma',
            'function_type': function_type,
            'original_sde': f'dX = {mu} dt + {sigma} dW',
            'transformed_sde': result_sde,
            'drift_coefficient': drift_term,
            'diffusion_coefficient': diffusion_term,
            'explanation': f'Applied Ito lemma to f(x) = {function_type}(x)'
        }

    def _apply_girsanov_theorem(self, drift_change, T):
        """Apply Girsanov theorem for change of measure"""
        self.girsanov_transforms += 1

        # Girsanov: dW_tilde = dW + theta*dt
        # Radon-Nikodym derivative: dQ/dP = exp(-theta*W_T - 0.5*theta^2*T)

        return {
            'operation': 'girsanov_theorem',
            'drift_change': drift_change,
            'T': T,
            'new_measure': f'Q with dQ/dP = exp(-{drift_change}*W_T - {0.5*drift_change**2*T})',
            'transformed_process': f'dW_tilde = dW + {drift_change}*dt',
            'novikov_condition': f'E[exp(0.5*{drift_change**2}*{T})] < infinity (satisfied for bounded theta)',
            'explanation': f'Changed measure: W becomes W_tilde with drift {drift_change}'
        }

    def _compute_quadratic_variation(self, T, n_steps):
        """Compute quadratic variation [W,W]_T = T"""
        dt = T / n_steps
        dW = np.random.normal(0, np.sqrt(dt), n_steps)
        quadratic_var = np.sum(dW**2)

        return {
            'operation': 'quadratic_variation',
            'T': T,
            'n_steps': n_steps,
            'computed_QV': float(quadratic_var),
            'theoretical_QV': T,
            'error': abs(quadratic_var - T),
            'explanation': f'[W,W]_T = {quadratic_var:.4f} (theoretical: {T})'
        }

    def _create_result_entry(self, task_entry, result, operation):
        if not self.blackboard:
            return result
        entry = create_entry(EntryType.PARTIAL_RESULT, create_variable(str(result)),
                           self.agent_id, task_entry.conversation_id,
                           ['stochastic_calculus', 'result'], EntryStatus.COMPLETED,
                           {'result': result, 'operation': operation})
        self.blackboard.post(entry)
        return entry

    def _create_error_entry(self, task_entry, error_msg):
        if not self.blackboard:
            return {'error': error_msg}
        entry = create_entry(EntryType.PARTIAL_RESULT, create_variable(f"ERROR: {error_msg}"),
                           self.agent_id, task_entry.conversation_id,
                           ['error'], EntryStatus.FAILED, {'error': error_msg})
        self.blackboard.post(entry)
        return entry

    def update_beliefs(self):
        if not self.blackboard:
            return
        try:
            tasks = self.blackboard.query_entries(tags=['stochastic_calculus'], status=EntryStatus.PENDING)
            for task in tasks:
                belief_key = f'pending_calculus_{task.entry_id}'
                if not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, 1.0, 'blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_calculus_'):
                continue
            task = belief.content
            if any(i.metadata.get('task_id') == task.entry_id for i in self.intentions):
                continue
            new_intentions.append(Intention(
                f'compute_{task.entry_id}', ['claim', 'compute', 'post'],
                'compute_stochastic', {'task_id': task.entry_id, 'task_entry': task}
            ))
        return new_intentions

    def execute_step(self, intention: Intention):
        action = intention.get_current_action()
        if action == 'claim':
            intention.advance()
        elif action == 'compute':
            result = self.process(intention.metadata.get('task_entry'))
            intention.metadata['result'] = result
            intention.advance()
        elif action == 'post':
            intention.mark_completed()

    def get_statistics(self) -> Dict[str, Any]:
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'ito_applications': self.ito_applications,
            'girsanov_transforms': self.girsanov_transforms
        })
        return stats
