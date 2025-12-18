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
MULTIOBJECTIVE OPTIMIZATION SPECIALIST (Tier 3)
=============================================

Implements multiobjective optimization algorithms: Pareto optimality,
weighted sum method, epsilon-constraint method, and NSGA-II selection.
Handles trade-offs between conflicting objectives.
"""

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator, create_service_registration
from symbo_agentic_reasoners.core.blackboard import Blackboard
from typing import Dict, Any, List, Optional, Tuple, Callable
import numpy as np
from scipy.optimize import minimize, differential_evolution


class MultiobjectiveOptimizationSpecialist(BDIAgent):
    """
    Specialist for multiobjective optimization and Pareto analysis.

    Capabilities:
    - Compute Pareto optimal sets
    - Weighted sum scalarization
    - Epsilon-constraint method
    - Compute utopia and nadir points
    - Check Pareto dominance
    - NSGA-II selection (non-dominated sorting)
    - Hypervolume indicator
    """

    def __init__(self, agent_id='multiobjective_specialist_001', df: Optional[DirectoryFacilitator]=None,
                 blackboard: Optional[Blackboard]=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = 0
        self.pareto_computations = 0
        self.scalarization_computations = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.optimization.advanced.multiobjective',
                agent_id=self.agent_id,
                algorithm='pareto_nsga_weighted',
                cost='medium',
                instance=self,
                type='specialist',
                tier='3',
                methods='pareto_optimal_weighted_sum_epsilon_constraint_nsga_ii'
            ))

        print(f"[{self.agent_id}] Multiobjective Optimization Specialist initialized")
        print(f"  Methods: Pareto optimality, weighted sum, NSGA-II")

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for multiobjective tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
            tasks = (self.blackboard.query_entries(tags=['multiobjective'], status=EntryStatus.PENDING) +
                    self.blackboard.query_entries(tags=['pareto'], status=EntryStatus.PENDING) +
                    self.blackboard.query_entries(tags=['optimization'], status=EntryStatus.PENDING))

            delegated = self.blackboard.query_entries(entry_type=EntryType.TASK, status=EntryStatus.PENDING)
            for task in delegated:
                if (hasattr(task, 'metadata') and task.metadata and
                    task.metadata.get('assigned_agent') == self.agent_id and task not in tasks):
                    tasks.append(task)

            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if (not self.has_belief(f'claimed_task_{task.entry_id}') and
                    not self.has_belief(belief_key)):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create multiobjective computation plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue

            task = belief.content
            task_id = task.entry_id

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'pareto_optimal')

            steps = ['claim_task', 'parse_parameters', 'compute_optimization', 'verify_result', 'post_result']
            intention = Intention(
                plan_id=f'multiobjective_{operation}_{task_id}',
                steps=steps,
                target_desire='multiobjective_computation',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)

        # Periodic Pareto cache update
        if self.tasks_executed > 0 and self.tasks_executed % 40 == 0:
            intent = Intention(
                plan_id=f'update_pareto_cache_{self.tasks_executed}',
                steps=['update_cache'],
                target_desire='maintain_knowledge',
                metadata={'trigger': 'periodic'}
            )
            new_intentions.append(intent)

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Perform multiobjective optimization computations."""
        from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
        from symbo_agentic_reasoners.core.omdoc_schema import create_variable

        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')

        try:
            if action == 'claim_task':
                if self.blackboard:
                    self.blackboard.update_entry_status(task_id, EntryStatus.IN_PROGRESS)
                self.add_belief(f'claimed_task_{task_id}', True)
                self.remove_belief(f'pending_task_{task_id}')
                intention.advance()

            elif action == 'parse_parameters':
                metadata = task.metadata if hasattr(task, 'metadata') else {}
                operation = metadata.get('operation', 'pareto_optimal')

                params = {}
                if operation == 'pareto_optimal':
                    params['objectives'] = metadata.get('objectives', [])
                    params['constraints'] = metadata.get('constraints', [])
                elif operation == 'weighted_sum':
                    params['objectives'] = metadata.get('objectives', [])
                    params['weights'] = metadata.get('weights', [0.5, 0.5])
                    params['constraints'] = metadata.get('constraints', [])

                intention.metadata['params'] = params
                intention.advance()

            elif action == 'compute_optimization':
                operation = intention.metadata.get('operation')
                params = intention.metadata.get('params', {})

                result = None
                if operation == 'pareto_optimal':
                    result = self.compute_pareto_optimal_set(
                        params.get('objectives', []),
                        params.get('constraints', [])
                    )
                elif operation == 'weighted_sum':
                    result = self.weighted_sum_method(
                        params.get('objectives', []),
                        params.get('weights', [0.5, 0.5]),
                        params.get('constraints', [])
                    )
                else:
                    result = {'operation': operation, 'status': 'not_implemented'}

                intention.metadata['result'] = result
                intention.advance()

            elif action == 'verify_result':
                result = intention.metadata.get('result')
                verified = result is not None and 'error' not in result
                intention.metadata['verified'] = verified
                intention.advance()

            elif action == 'post_result':
                result = intention.metadata.get('result')
                if self.blackboard:
                    entry = create_entry(
                        EntryType.PARTIAL_RESULT,
                        create_variable(str(result)),
                        self.agent_id,
                        task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                        ['multiobjective', 'result', task_id],
                        EntryStatus.COMPLETED,
                        {'result': result, 'result_str': str(result)}
                    )
                    self.blackboard.post(entry)
                    self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)
                self.tasks_executed += 1
                intention.advance()

            elif action == 'update_cache':
                self.add_belief(
                    'pareto_cache_updated',
                    {'timestamp': self.tasks_executed, 'pareto': self.pareto_computations,
                     'scalarization': self.scalarization_computations},
                    confidence=0.9,
                    source='self_monitoring'
                )
                intention.advance()

            else:
                intention.advance()

        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"[{self.agent_id}] Step {action} failed: {e}")
            while not intention.is_complete():
                intention.advance()

    def process(self, task_entry):
        """
        Process a multiobjective optimization task (legacy interface).

        Args:
            task_entry: Task entry with metadata containing operation and parameters

        Returns:
            Dict with computation result
        """
        self.tasks_executed += 1
        metadata = task_entry.get('metadata', {}) if isinstance(task_entry, dict) else {}
        operation = metadata.get('operation', 'pareto_optimal')

        try:
            if operation == 'pareto_optimal':
                objectives = metadata.get('objectives', [])
                constraints = metadata.get('constraints', [])
                return self.compute_pareto_optimal_set(objectives, constraints)
            elif operation == 'weighted_sum':
                objectives = metadata.get('objectives', [])
                weights = metadata.get('weights', [0.5, 0.5])
                constraints = metadata.get('constraints', [])
                return self.weighted_sum_method(objectives, weights, constraints)
            else:
                return {'operation': operation, 'explanation': 'Multiobjective optimization'}
        except Exception as e:
            return {'error': str(e), 'operation': operation}

    # ==================== CORE COMPUTATIONAL METHODS ====================

    def compute_pareto_optimal_set(
        self,
        objectives: List[Callable],
        constraints: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Compute Pareto optimal set for multiobjective problem.

        A solution x* is Pareto optimal if there is no other feasible x such that:
        f_i(x) ≤ f_i(x*) for all i, with strict inequality for at least one i.

        Uses weighted sum method with varying weights to approximate Pareto frontier.

        Args:
            objectives: List of objective functions [f1, f2, ...]
            constraints: Optional constraints (dict with 'type' and 'fun')

        Returns:
            Dict with Pareto optimal solutions

        Example:
            >>> # Minimize f1 = x^2 and f2 = (x-2)^2
            >>> f1 = lambda x: x[0]**2
            >>> f2 = lambda x: (x[0] - 2)**2
            >>> result = agent.compute_pareto_optimal_set([f1, f2])
        """
        self.pareto_computations += 1

        if not objectives:
            return {'error': 'At least one objective required'}

        n_objectives = len(objectives)

        # Generate weight vectors to sample Pareto frontier
        n_samples = 20
        weight_vectors = self._generate_weight_vectors(n_objectives, n_samples)

        pareto_solutions = []
        pareto_objectives = []

        for weights in weight_vectors:
            result = self.weighted_sum_method(objectives, weights, constraints)

            if 'error' not in result and 'solution' in result:
                solution = result['solution']
                obj_values = result['objective_values']

                # Check if solution is non-dominated
                is_dominated = False
                for existing_obj in pareto_objectives:
                    if self._dominates(existing_obj, obj_values):
                        is_dominated = True
                        break

                if not is_dominated:
                    # Remove dominated solutions
                    pareto_objectives = [
                        obj for obj in pareto_objectives
                        if not self._dominates(obj_values, obj)
                    ]
                    pareto_objectives.append(obj_values)
                    pareto_solutions.append(solution)

        return {
            'pareto_solutions': pareto_solutions,
            'pareto_objectives': pareto_objectives,
            'n_solutions': len(pareto_solutions),
            'n_objectives': n_objectives
        }

    def _generate_weight_vectors(self, n_objectives: int, n_samples: int) -> List[List[float]]:
        """Generate uniformly distributed weight vectors on simplex."""
        if n_objectives == 2:
            # For 2 objectives, use linear spacing
            weights = []
            for i in range(n_samples):
                w1 = i / (n_samples - 1)
                w2 = 1 - w1
                weights.append([w1, w2])
            return weights
        else:
            # For more objectives, use random sampling on simplex
            weights = []
            for _ in range(n_samples):
                w = np.random.dirichlet(np.ones(n_objectives))
                weights.append(w.tolist())
            return weights

    def _dominates(self, obj1: List[float], obj2: List[float]) -> bool:
        """Check if obj1 dominates obj2 (minimization)."""
        obj1_arr = np.array(obj1)
        obj2_arr = np.array(obj2)

        # obj1 dominates obj2 if obj1[i] <= obj2[i] for all i
        # and obj1[i] < obj2[i] for at least one i
        return np.all(obj1_arr <= obj2_arr) and np.any(obj1_arr < obj2_arr)

    def weighted_sum_method(
        self,
        objectives: List[Callable],
        weights: List[float],
        constraints: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Solve multiobjective problem using weighted sum scalarization.

        Converts multiobjective problem to single objective:
        min Σ w_i f_i(x)

        Args:
            objectives: List of objective functions [f1, f2, ...]
            weights: Weight vector [w1, w2, ...] (must sum to 1)
            constraints: Optional constraints

        Returns:
            Dict with optimal solution and objective values

        Example:
            >>> f1 = lambda x: x[0]**2
            >>> f2 = lambda x: (x[0] - 2)**2
            >>> result = agent.weighted_sum_method([f1, f2], [0.5, 0.5])
        """
        self.scalarization_computations += 1

        if len(objectives) != len(weights):
            return {'error': 'Number of objectives must match number of weights'}

        weights_arr = np.array(weights)
        if not np.allclose(weights_arr.sum(), 1.0, atol=1e-6):
            return {'error': 'Weights must sum to 1', 'sum': float(weights_arr.sum())}

        # Define weighted sum objective
        def weighted_objective(x):
            """Weighted sum objective: Σ w_i · f_i(x)."""
            return sum(w * f(x) for w, f in zip(weights, objectives))

        # Initial guess (origin or random)
        x0 = np.zeros(2)  # Assume 2D for simplicity

        # Optimize
        scipy_constraints = []
        if constraints:
            for c in constraints:
                scipy_constraints.append({
                    'type': c.get('type', 'ineq'),
                    'fun': c.get('fun')
                })

        result = minimize(
            weighted_objective,
            x0,
            method='SLSQP',
            constraints=scipy_constraints if scipy_constraints else None
        )

        if not result.success:
            return {'error': 'Optimization failed', 'message': result.message}

        solution = result.x.tolist()
        objective_values = [float(f(result.x)) for f in objectives]
        weighted_sum = float(result.fun)

        return {
            'solution': solution,
            'objective_values': objective_values,
            'weighted_sum': weighted_sum,
            'weights': weights,
            'success': True
        }

    def epsilon_constraint_method(
        self,
        objectives: List[Callable],
        epsilon_values: List[float],
        primary_index: int = 0
    ) -> Dict[str, Any]:
        """
        Solve multiobjective problem using epsilon-constraint method.

        Minimizes one objective while constraining others:
        min f_k(x)
        s.t. f_i(x) ≤ ε_i for i ≠ k

        Args:
            objectives: List of objective functions [f1, f2, ...]
            epsilon_values: Constraint values [ε1, ε2, ...]
            primary_index: Index of objective to minimize

        Returns:
            Dict with optimal solution and objective values

        Example:
            >>> f1 = lambda x: x[0]**2
            >>> f2 = lambda x: (x[0] - 2)**2
            >>> result = agent.epsilon_constraint_method([f1, f2], [float('inf'), 1.0], primary_index=0)
        """
        if primary_index >= len(objectives):
            return {'error': f'Primary index {primary_index} out of range'}

        # Primary objective to minimize
        primary_objective = objectives[primary_index]

        # Epsilon constraints for other objectives
        constraints = []
        for i, (obj, eps) in enumerate(zip(objectives, epsilon_values)):
            if i != primary_index and eps < float('inf'):
                # f_i(x) <= eps
                constraints.append({
                    'type': 'ineq',
                    'fun': lambda x, obj=obj, eps=eps: eps - obj(x)
                })

        # Initial guess
        x0 = np.zeros(2)

        result = minimize(
            primary_objective,
            x0,
            method='SLSQP',
            constraints=constraints if constraints else None
        )

        if not result.success:
            return {'error': 'Optimization failed', 'message': result.message}

        solution = result.x.tolist()
        objective_values = [float(f(result.x)) for f in objectives]

        return {
            'solution': solution,
            'objective_values': objective_values,
            'primary_objective': float(result.fun),
            'primary_index': primary_index,
            'epsilon_values': epsilon_values,
            'success': True
        }

    def compute_utopia_point(self, objectives: List[Callable]) -> Dict[str, Any]:
        """
        Compute utopia point (ideal point).

        The utopia point u* = (u₁*, u₂*, ...) where u_i* = min f_i(x).
        This is typically unattainable due to conflicting objectives.

        Args:
            objectives: List of objective functions [f1, f2, ...]

        Returns:
            Dict with utopia point and individual minima

        Example:
            >>> f1 = lambda x: x[0]**2
            >>> f2 = lambda x: (x[0] - 2)**2
            >>> result = agent.compute_utopia_point([f1, f2])
        """
        utopia = []
        individual_solutions = []

        for i, obj in enumerate(objectives):
            # Minimize each objective independently
            x0 = np.zeros(2)
            result = minimize(obj, x0, method='BFGS')

            if result.success:
                utopia.append(float(result.fun))
                individual_solutions.append({
                    'objective_index': i,
                    'solution': result.x.tolist(),
                    'minimum': float(result.fun)
                })
            else:
                utopia.append(float('inf'))
                individual_solutions.append({
                    'objective_index': i,
                    'solution': None,
                    'minimum': float('inf')
                })

        return {
            'utopia_point': utopia,
            'individual_minima': individual_solutions,
            'n_objectives': len(objectives)
        }

    def compute_nadir_point(
        self,
        objectives: List[Callable],
        pareto_set: Optional[List[List[float]]] = None
    ) -> Dict[str, Any]:
        """
        Compute nadir point (worst values on Pareto frontier).

        The nadir point z_nad = (z₁_nad, z₂_nad, ...) where z_i_nad is the
        maximum value of objective i over the Pareto frontier.

        Args:
            objectives: List of objective functions [f1, f2, ...]
            pareto_set: Optional pre-computed Pareto set

        Returns:
            Dict with nadir point

        Example:
            >>> f1 = lambda x: x[0]**2
            >>> f2 = lambda x: (x[0] - 2)**2
            >>> result = agent.compute_nadir_point([f1, f2])
        """
        if pareto_set is None:
            # Compute Pareto set if not provided
            pareto_result = self.compute_pareto_optimal_set(objectives)
            if 'error' in pareto_result:
                return pareto_result

            pareto_objectives = pareto_result.get('pareto_objectives', [])
        else:
            # Evaluate objectives at given Pareto set
            pareto_objectives = []
            for x in pareto_set:
                obj_values = [float(f(x)) for f in objectives]
                pareto_objectives.append(obj_values)

        if not pareto_objectives:
            return {'error': 'Empty Pareto set'}

        # Nadir point: maximum of each objective over Pareto frontier
        pareto_arr = np.array(pareto_objectives)
        nadir = np.max(pareto_arr, axis=0).tolist()

        return {
            'nadir_point': nadir,
            'n_pareto_solutions': len(pareto_objectives),
            'n_objectives': len(objectives)
        }

    def check_pareto_dominance(
        self,
        solution1: List[float],
        solution2: List[float]
    ) -> Dict[str, Any]:
        """
        Check if solution1 dominates solution2.

        Solution x dominates y if:
        - f_i(x) ≤ f_i(y) for all objectives i
        - f_i(x) < f_i(y) for at least one objective i

        Args:
            solution1: Objective values for solution 1
            solution2: Objective values for solution 2

        Returns:
            Dict with dominance status

        Example:
            >>> result = agent.check_pareto_dominance([1.0, 2.0], [1.5, 2.5])
            >>> # Returns: {'solution1_dominates': True}
        """
        s1 = np.array(solution1)
        s2 = np.array(solution2)

        if len(s1) != len(s2):
            return {'error': 'Solutions must have same number of objectives'}

        s1_dominates = np.all(s1 <= s2) and np.any(s1 < s2)
        s2_dominates = np.all(s2 <= s1) and np.any(s2 < s1)

        if s1_dominates:
            relation = 'solution1_dominates'
        elif s2_dominates:
            relation = 'solution2_dominates'
        elif np.allclose(s1, s2):
            relation = 'equal'
        else:
            relation = 'non_dominated'

        return {
            'solution1_dominates': s1_dominates,
            'solution2_dominates': s2_dominates,
            'relation': relation,
            'solution1': solution1,
            'solution2': solution2
        }

    def nsga_ii_selection(
        self,
        population: List[List[float]],
        objectives: List[Callable]
    ) -> Dict[str, Any]:
        """
        Apply NSGA-II non-dominated sorting and selection.

        NSGA-II key components:
        1. Non-dominated sorting: Assign rank based on dominance
        2. Crowding distance: Maintain diversity on Pareto front

        Args:
            population: List of candidate solutions
            objectives: List of objective functions

        Returns:
            Dict with fronts, ranks, and crowding distances

        Example:
            >>> pop = [[0.0], [0.5], [1.0], [1.5], [2.0]]
            >>> f1 = lambda x: x[0]**2
            >>> f2 = lambda x: (x[0] - 2)**2
            >>> result = agent.nsga_ii_selection(pop, [f1, f2])
        """
        if not population:
            return {'error': 'Empty population'}

        # Evaluate objectives for all solutions
        objective_values = []
        for x in population:
            obj = [float(f(x)) for f in objectives]
            objective_values.append(obj)

        # Non-dominated sorting
        fronts = self._non_dominated_sort(objective_values)

        # Compute crowding distance for each front
        crowding_distances = []
        for front in fronts:
            if len(front) <= 2:
                distances = [float('inf')] * len(front)
            else:
                distances = self._crowding_distance(
                    [objective_values[i] for i in front]
                )
            crowding_distances.append(distances)

        # Assign ranks
        ranks = [0] * len(population)
        for rank, front in enumerate(fronts):
            for idx in front:
                ranks[idx] = rank

        return {
            'fronts': fronts,
            'ranks': ranks,
            'crowding_distances': crowding_distances,
            'n_fronts': len(fronts),
            'pareto_front': fronts[0] if fronts else []
        }

    def _non_dominated_sort(self, objectives: List[List[float]]) -> List[List[int]]:
        """
        Perform non-dominated sorting.

        Returns list of fronts, where each front is a list of solution indices.
        """
        n = len(objectives)
        domination_count = [0] * n  # Number of solutions dominating i
        dominated_solutions = [[] for _ in range(n)]  # Solutions dominated by i

        # Count dominations
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue

                if self._dominates(objectives[i], objectives[j]):
                    dominated_solutions[i].append(j)
                elif self._dominates(objectives[j], objectives[i]):
                    domination_count[i] += 1

        # First front: solutions with domination_count = 0
        fronts = []
        current_front = [i for i in range(n) if domination_count[i] == 0]
        fronts.append(current_front)

        # Build subsequent fronts
        while current_front:
            next_front = []
            for i in current_front:
                for j in dominated_solutions[i]:
                    domination_count[j] -= 1
                    if domination_count[j] == 0:
                        next_front.append(j)

            if next_front:
                fronts.append(next_front)
            current_front = next_front

        return fronts

    def _crowding_distance(self, objectives: List[List[float]]) -> List[float]:
        """
        Compute crowding distance for a front.

        Crowding distance measures density of solutions around a point.
        Boundary solutions get infinite distance.
        """
        n = len(objectives)
        m = len(objectives[0])  # Number of objectives

        distances = [0.0] * n

        # For each objective
        for obj_idx in range(m):
            # Sort by objective value
            sorted_indices = sorted(range(n), key=lambda i: objectives[i][obj_idx])

            # Boundary solutions get infinite distance
            distances[sorted_indices[0]] = float('inf')
            distances[sorted_indices[-1]] = float('inf')

            # Compute range
            obj_min = objectives[sorted_indices[0]][obj_idx]
            obj_max = objectives[sorted_indices[-1]][obj_idx]
            obj_range = obj_max - obj_min

            if obj_range == 0:
                continue

            # Assign crowding distance
            for i in range(1, n - 1):
                idx = sorted_indices[i]
                prev_idx = sorted_indices[i - 1]
                next_idx = sorted_indices[i + 1]

                distances[idx] += (
                    (objectives[next_idx][obj_idx] - objectives[prev_idx][obj_idx])
                    / obj_range
                )

        return distances

    def compute_hypervolume_indicator(
        self,
        pareto_set: List[List[float]],
        reference_point: List[float]
    ) -> Dict[str, Any]:
        """
        Compute hypervolume indicator for Pareto set.

        Hypervolume: Volume of objective space dominated by Pareto set
        and bounded by reference point. Larger is better.

        For 2D, this is the area under the Pareto front.

        Args:
            pareto_set: List of objective vectors on Pareto front
            reference_point: Reference point (typically nadir or worse)

        Returns:
            Dict with hypervolume value

        Example:
            >>> pareto = [[1.0, 4.0], [2.0, 2.0], [4.0, 1.0]]
            >>> ref = [5.0, 5.0]
            >>> result = agent.compute_hypervolume_indicator(pareto, ref)
        """
        if not pareto_set:
            return {'error': 'Empty Pareto set'}

        pareto_arr = np.array(pareto_set)
        ref = np.array(reference_point)

        # Check if all solutions dominate reference
        if not np.all(pareto_arr <= ref):
            return {'error': 'Reference point must be dominated by all solutions'}

        n_objectives = pareto_arr.shape[1]

        if n_objectives == 2:
            # For 2D, compute exact hypervolume
            # Sort by first objective
            sorted_indices = np.argsort(pareto_arr[:, 0])
            sorted_pareto = pareto_arr[sorted_indices]

            hypervolume = 0.0
            prev_x = ref[0]

            for i in range(len(sorted_pareto) - 1, -1, -1):
                x, y = sorted_pareto[i]
                width = prev_x - x
                height = ref[1] - y
                hypervolume += width * height
                prev_x = x

            return {
                'hypervolume': float(hypervolume),
                'n_solutions': len(pareto_set),
                'n_objectives': n_objectives,
                'reference_point': reference_point
            }
        else:
            # For higher dimensions, use Monte Carlo approximation
            n_samples = 10000
            samples = np.random.uniform(
                low=np.min(pareto_arr, axis=0),
                high=ref,
                size=(n_samples, n_objectives)
            )

            # Count samples dominated by at least one Pareto solution
            dominated_count = 0
            for sample in samples:
                for pareto_sol in pareto_arr:
                    if np.all(pareto_sol <= sample):
                        dominated_count += 1
                        break

            # Estimate hypervolume
            box_volume = np.prod(ref - np.min(pareto_arr, axis=0))
            hypervolume_estimate = (dominated_count / n_samples) * box_volume

            return {
                'hypervolume': float(hypervolume_estimate),
                'n_solutions': len(pareto_set),
                'n_objectives': n_objectives,
                'reference_point': reference_point,
                'method': 'monte_carlo',
                'n_samples': n_samples
            }

    def get_statistics(self) -> Dict[str, Any]:
        """Retrieve agent statistics."""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'pareto_computations': self.pareto_computations,
            'scalarization_computations': self.scalarization_computations
        })
        return stats
