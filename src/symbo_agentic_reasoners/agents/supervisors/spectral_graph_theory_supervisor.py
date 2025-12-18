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
SPECTRAL GRAPH THEORY SUPERVISOR (Tier 2)
=========================================

Routes spectral graph theory problems to appropriate specialists.
Never computes directly - only delegates to Tier 3 specialists.

NO SYMPY - Pure native mathematical reasoning.
"""

import logging
from typing import Dict, Any, List

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention

logger = logging.getLogger(__name__)


class SpectralGraphTheorySupervisor(BDIAgent):
    """
    Supervisor for spectral graph theory domain.

    Routes to:
    - LaplacianSpectrumSpecialist: Graph Laplacian, eigenvalues, Fiedler value
    - AdjacencySpectrumSpecialist: Adjacency matrix eigenvalues, spectral radius
    - CheegerInequalitySpecialist: Cheeger inequality, graph conductance
    - RandomWalkSpecialist: Stationary distribution, mixing time
    - SpectralClusteringSpecialist: Normalized cuts, k-way partitioning

    This supervisor NEVER computes - only routes.
    """

    # Keywords for routing
    LAPLACIAN_KEYWORDS = ['laplacian', 'fiedler', 'algebraic connectivity', 'graph laplacian',
                         'degree matrix', 'normalized laplacian']
    ADJACENCY_KEYWORDS = ['adjacency', 'adjacency matrix', 'spectral radius', 'eigenvalue',
                         'characteristic polynomial', 'spectrum']
    CHEEGER_KEYWORDS = ['cheeger', 'conductance', 'expansion', 'isoperimetric', 'edge expansion',
                       'cheeger constant']
    RANDOM_WALK_KEYWORDS = ['random walk', 'markov chain', 'stationary', 'mixing time',
                           'hitting time', 'transition matrix']
    CLUSTERING_KEYWORDS = ['clustering', 'spectral clustering', 'normalized cut', 'partition',
                          'k-way', 'graph cut', 'embedding']

    def __init__(self, agent_id: str = 'spectral_graph_theory_supervisor_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard

        # Lazy-loaded specialists
        self._laplacian_specialist = None
        self._adjacency_specialist = None
        self._cheeger_specialist = None
        self._random_walk_specialist = None
        self._clustering_specialist = None

        if self.df:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
            self.df.register(create_service_registration(
                service_type='math.discrete.graphs.spectral',
                agent_id=agent_id,
                algorithm='router',
                cost='minimal',
                instance=self,
                tier='2',
                capabilities='laplacian_adjacency_cheeger_random_walk_clustering_routing'
            ))

        logger.info(f"[{agent_id}] Spectral Graph Theory Supervisor initialized")

    @property
    def laplacian_specialist(self):
        """Lazy load Laplacian spectrum specialist."""
        if self._laplacian_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.discrete_math.spectral_graphs.laplacian_spectrum import LaplacianSpectrumSpecialist
            self._laplacian_specialist = LaplacianSpectrumSpecialist(
                agent_id='laplacian_spectrum_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._laplacian_specialist

    @property
    def adjacency_specialist(self):
        """Lazy load adjacency spectrum specialist."""
        if self._adjacency_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.discrete_math.spectral_graphs.adjacency_spectrum import AdjacencySpectrumSpecialist
            self._adjacency_specialist = AdjacencySpectrumSpecialist(
                agent_id='adjacency_spectrum_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._adjacency_specialist

    @property
    def cheeger_specialist(self):
        """Lazy load Cheeger inequality specialist."""
        if self._cheeger_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.discrete_math.spectral_graphs.cheeger_inequality import CheegerInequalitySpecialist
            self._cheeger_specialist = CheegerInequalitySpecialist(
                agent_id='cheeger_inequality_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._cheeger_specialist

    @property
    def random_walk_specialist(self):
        """Lazy load random walk specialist."""
        if self._random_walk_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.discrete_math.spectral_graphs.random_walks import RandomWalkSpecialist
            self._random_walk_specialist = RandomWalkSpecialist(
                agent_id='random_walk_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._random_walk_specialist

    @property
    def clustering_specialist(self):
        """Lazy load spectral clustering specialist."""
        if self._clustering_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.discrete_math.spectral_graphs.spectral_clustering import SpectralClusteringSpecialist
            self._clustering_specialist = SpectralClusteringSpecialist(
                agent_id='spectral_clustering_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._clustering_specialist

    def update_beliefs(self):
        """PERCEIVE: Monitor for spectral graph theory tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryStatus
            tasks = self.blackboard.query_entries(tags=['spectral_graph'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['graph_spectrum'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['laplacian'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['spectral_clustering'], status=EntryStatus.PENDING)

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
                plan_id=f'route_spectral_graph_{task_id}',
                steps=steps,
                target_desire='spectral_graph_routing',
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
        laplacian_ops = ['laplacian', 'fiedler', 'algebraic_connectivity']
        adjacency_ops = ['adjacency', 'spectral_radius', 'characteristic_polynomial']
        cheeger_ops = ['cheeger', 'conductance', 'expansion', 'isoperimetric']
        random_walk_ops = ['random_walk', 'stationary', 'mixing_time', 'hitting_time']
        clustering_ops = ['cluster', 'partition', 'normalized_cut', 'spectral_clustering']

        if operation in laplacian_ops:
            return 'laplacian'
        if operation in adjacency_ops:
            return 'adjacency'
        if operation in cheeger_ops:
            return 'cheeger'
        if operation in random_walk_ops:
            return 'random_walk'
        if operation in clustering_ops:
            return 'clustering'

        # Check keywords
        laplacian_score = sum(1 for kw in self.LAPLACIAN_KEYWORDS if kw in combined_text)
        adjacency_score = sum(1 for kw in self.ADJACENCY_KEYWORDS if kw in combined_text)
        cheeger_score = sum(1 for kw in self.CHEEGER_KEYWORDS if kw in combined_text)
        random_walk_score = sum(1 for kw in self.RANDOM_WALK_KEYWORDS if kw in combined_text)
        clustering_score = sum(1 for kw in self.CLUSTERING_KEYWORDS if kw in combined_text)

        scores = {
            'laplacian': laplacian_score,
            'adjacency': adjacency_score,
            'cheeger': cheeger_score,
            'random_walk': random_walk_score,
            'clustering': clustering_score
        }

        return max(scores, key=scores.get) if max(scores.values()) > 0 else 'laplacian'

    def execute_step(self, intention: Intention):
        """EXECUTE: Route to appropriate specialist."""
        action = intention.get_current_action()

        if action == 'route_task':
            task = intention.metadata.get('task_entry')
            target = intention.metadata.get('target', 'laplacian')

            self.add_belief(f'routed_task_{task.entry_id}', True, confidence=1.0)

            if target == 'laplacian':
                specialist = self.laplacian_specialist
            elif target == 'adjacency':
                specialist = self.adjacency_specialist
            elif target == 'cheeger':
                specialist = self.cheeger_specialist
            elif target == 'random_walk':
                specialist = self.random_walk_specialist
            else:
                specialist = self.clustering_specialist

            logger.info(f"[{self.agent_id}] Routing task {task.entry_id} to {target} specialist")

            specialist.update_beliefs()
            new_intentions = specialist.deliberate()
            for new_intention in new_intentions:
                specialist.intentions.append(new_intention)

            intention.mark_completed()

    def solve(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """
        Direct solve interface for spectral graph theory problems.

        Args:
            problem: Dictionary with 'type' and relevant parameters

        Returns:
            Solution dictionary
        """
        problem_type = problem.get('type', '').lower()

        # Route to appropriate specialist based on problem type
        if any(kw in problem_type for kw in ['laplacian', 'fiedler', 'algebraic_connectivity']):
            return self.laplacian_specialist.solve(problem)
        elif any(kw in problem_type for kw in ['adjacency', 'spectral_radius']):
            return self.adjacency_specialist.solve(problem)
        elif any(kw in problem_type for kw in ['cheeger', 'conductance', 'expansion']):
            return self.cheeger_specialist.solve(problem)
        elif any(kw in problem_type for kw in ['random_walk', 'stationary', 'mixing']):
            return self.random_walk_specialist.solve(problem)
        elif any(kw in problem_type for kw in ['cluster', 'partition', 'cut']):
            return self.clustering_specialist.solve(problem)

        return {'error': f'Unknown problem type: {problem_type}'}

    def get_statistics(self) -> Dict[str, Any]:
        """Return supervisor statistics."""
        stats = {
            'agent_id': self.agent_id,
            'tier': 2,
            'role': 'supervisor',
            'specialists': ['laplacian', 'adjacency', 'cheeger', 'random_walk', 'clustering']
        }

        if self._laplacian_specialist:
            stats['laplacian_tasks'] = getattr(self._laplacian_specialist, 'tasks_executed', 0)
        if self._adjacency_specialist:
            stats['adjacency_tasks'] = getattr(self._adjacency_specialist, 'tasks_executed', 0)
        if self._cheeger_specialist:
            stats['cheeger_tasks'] = getattr(self._cheeger_specialist, 'tasks_executed', 0)
        if self._random_walk_specialist:
            stats['random_walk_tasks'] = getattr(self._random_walk_specialist, 'tasks_executed', 0)
        if self._clustering_specialist:
            stats['clustering_tasks'] = getattr(self._clustering_specialist, 'tasks_executed', 0)

        return stats
