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
TIME SERIES ANALYSIS SUPERVISOR (Tier 2)
========================================

Routes time series analysis problems to appropriate specialists.
Never computes directly - only delegates to Tier 3 specialists.

NO SYMPY - Pure native mathematical reasoning.
"""

import logging
from typing import Dict, Any, List

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention

logger = logging.getLogger(__name__)


class TimeSeriesAnalysisSupervisor(BDIAgent):
    """
    Supervisor for time series analysis domain.

    Routes to:
    - ARIMASpecialist: ARIMA models, Box-Jenkins methodology, forecasting
    - KalmanFilterSpecialist: State-space models, Kalman filtering, tracking
    - SpectralAnalysisSpecialist: Fourier analysis, periodogram, spectral density
    - NonlinearTimeSeriesSpecialist: ARCH/GARCH, threshold models, regime switching

    This supervisor NEVER computes - only routes.
    """

    # Keywords for routing
    ARIMA_KEYWORDS = ['arima', 'autoregressive', 'moving average', 'box-jenkins',
                     'acf', 'pacf', 'forecast', 'ar', 'ma', 'differencing']
    KALMAN_KEYWORDS = ['kalman', 'state space', 'observation model', 'prediction', 'update',
                      'filtering', 'tracking', 'covariance', 'gain']
    SPECTRAL_KEYWORDS = ['spectral', 'periodogram', 'fourier', 'frequency', 'spectrum',
                        'power spectral density', 'fft', 'harmonic']
    NONLINEAR_KEYWORDS = ['arch', 'garch', 'nonlinear', 'threshold', 'regime switching',
                         'volatility', 'conditional heteroscedasticity', 'tar']

    def __init__(self, agent_id: str = 'timeseries_supervisor_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard

        # Lazy-loaded specialists
        self._arima_specialist = None
        self._kalman_specialist = None
        self._spectral_specialist = None
        self._nonlinear_specialist = None

        if self.df:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
            self.df.register(create_service_registration(
                service_type='math.statistics.timeseries',
                agent_id=agent_id,
                algorithm='router',
                cost='minimal',
                instance=self,
                tier='2',
                capabilities='arima_kalman_spectral_nonlinear_routing'
            ))

        logger.info(f"[{agent_id}] Time Series Analysis Supervisor initialized")

    @property
    def arima_specialist(self):
        """Lazy load ARIMA specialist."""
        if self._arima_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.statistics.timeseries.arima import ARIMASpecialist
            self._arima_specialist = ARIMASpecialist(
                agent_id='arima_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._arima_specialist

    @property
    def kalman_specialist(self):
        """Lazy load Kalman filter specialist."""
        if self._kalman_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.statistics.timeseries.kalman_filter import KalmanFilterSpecialist
            self._kalman_specialist = KalmanFilterSpecialist(
                agent_id='kalman_filter_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._kalman_specialist

    @property
    def spectral_specialist(self):
        """Lazy load spectral analysis specialist."""
        if self._spectral_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.statistics.timeseries.spectral_analysis import SpectralAnalysisSpecialist
            self._spectral_specialist = SpectralAnalysisSpecialist(
                agent_id='spectral_analysis_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._spectral_specialist

    @property
    def nonlinear_specialist(self):
        """Lazy load nonlinear time series specialist."""
        if self._nonlinear_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.statistics.timeseries.nonlinear_timeseries import NonlinearTimeSeriesSpecialist
            self._nonlinear_specialist = NonlinearTimeSeriesSpecialist(
                agent_id='nonlinear_timeseries_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._nonlinear_specialist

    def update_beliefs(self):
        """PERCEIVE: Monitor for time series analysis tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryStatus
            tasks = self.blackboard.query_entries(tags=['timeseries'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['arima'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['kalman'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['spectral_analysis'], status=EntryStatus.PENDING)

            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(f'routed_task_{task.entry_id}') and not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create routing plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            target_specialist = self._determine_specialist(task)

            steps = ['route_task']
            intention = Intention(
                plan_id=f'route_timeseries_{task_id}',
                steps=steps,
                target_desire='timeseries_routing',
                metadata={'task_id': task_id, 'task_entry': task, 'target': target_specialist}
            )
            new_intentions.append(intention)
        return new_intentions

    def _determine_specialist(self, task) -> str:
        """Determine which specialist should handle this task."""
        metadata = task.metadata if hasattr(task, 'metadata') else {}
        content = str(task.content).lower() if hasattr(task, 'content') else ''
        operation = metadata.get('operation', '').lower()

        combined_text = f"{content} {operation}"

        # Check explicit operations
        arima_ops = ['arima', 'box_jenkins', 'forecast', 'acf', 'pacf', 'ar', 'ma']
        kalman_ops = ['kalman', 'state_space', 'filter', 'predict', 'update']
        spectral_ops = ['periodogram', 'spectrum', 'fft', 'spectral_density']
        nonlinear_ops = ['arch', 'garch', 'threshold', 'regime_switching', 'tar']

        if operation in arima_ops:
            return 'arima'
        if operation in kalman_ops:
            return 'kalman'
        if operation in spectral_ops:
            return 'spectral'
        if operation in nonlinear_ops:
            return 'nonlinear'

        # Check keywords
        arima_score = sum(1 for kw in self.ARIMA_KEYWORDS if kw in combined_text)
        kalman_score = sum(1 for kw in self.KALMAN_KEYWORDS if kw in combined_text)
        spectral_score = sum(1 for kw in self.SPECTRAL_KEYWORDS if kw in combined_text)
        nonlinear_score = sum(1 for kw in self.NONLINEAR_KEYWORDS if kw in combined_text)

        scores = {
            'arima': arima_score,
            'kalman': kalman_score,
            'spectral': spectral_score,
            'nonlinear': nonlinear_score
        }

        return max(scores, key=scores.get) if max(scores.values()) > 0 else 'arima'

    def execute_step(self, intention: Intention):
        """EXECUTE: Route to appropriate specialist."""
        action = intention.get_current_action()

        if action == 'route_task':
            task = intention.metadata.get('task_entry')
            target = intention.metadata.get('target', 'arima')

            self.add_belief(f'routed_task_{task.entry_id}', True, confidence=1.0)

            if target == 'arima':
                specialist = self.arima_specialist
            elif target == 'kalman':
                specialist = self.kalman_specialist
            elif target == 'spectral':
                specialist = self.spectral_specialist
            else:
                specialist = self.nonlinear_specialist

            logger.info(f"[{self.agent_id}] Routing task {task.entry_id} to {target} specialist")

            specialist.update_beliefs()
            new_intentions = specialist.deliberate()
            for new_intention in new_intentions:
                specialist.intentions.append(new_intention)

            intention.mark_completed()

    def solve(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """
        Direct solve interface for time series analysis problems.

        Args:
            problem: Dictionary with 'type' and relevant parameters

        Returns:
            Solution dictionary
        """
        problem_type = problem.get('type', '').lower()

        # Route to appropriate specialist based on problem type
        if any(kw in problem_type for kw in ['arima', 'autoregressive', 'forecast', 'box-jenkins']):
            return self.arima_specialist.solve(problem)
        elif any(kw in problem_type for kw in ['kalman', 'state_space', 'filter']):
            return self.kalman_specialist.solve(problem)
        elif any(kw in problem_type for kw in ['spectral', 'periodogram', 'fourier', 'frequency']):
            return self.spectral_specialist.solve(problem)
        elif any(kw in problem_type for kw in ['arch', 'garch', 'nonlinear', 'threshold']):
            return self.nonlinear_specialist.solve(problem)

        return {'error': f'Unknown problem type: {problem_type}'}

    def get_statistics(self) -> Dict[str, Any]:
        """Return supervisor statistics."""
        stats = {
            'agent_id': self.agent_id,
            'tier': 2,
            'role': 'supervisor',
            'specialists': ['arima', 'kalman', 'spectral', 'nonlinear']
        }

        if self._arima_specialist:
            stats['arima_tasks'] = getattr(self._arima_specialist, 'tasks_executed', 0)
        if self._kalman_specialist:
            stats['kalman_tasks'] = getattr(self._kalman_specialist, 'tasks_executed', 0)
        if self._spectral_specialist:
            stats['spectral_tasks'] = getattr(self._spectral_specialist, 'tasks_executed', 0)
        if self._nonlinear_specialist:
            stats['nonlinear_tasks'] = getattr(self._nonlinear_specialist, 'tasks_executed', 0)

        return stats
